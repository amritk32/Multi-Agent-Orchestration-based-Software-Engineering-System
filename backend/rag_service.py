import json
import uuid
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from sqlalchemy.orm import Session

from aapi import OPEN_AI_API
from database.models import ProjectRAGDocument, ProjectChatHistory


class ProjectRAGService:
    """Project-scoped retrieval over generated documents using OpenAI embeddings and FAISS."""

    def __init__(self) -> None:
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=OPEN_AI_API,
        )
        self.chat_model = ChatOpenAI(
            model="gpt-5-mini",
            temperature=0,
            api_key=OPEN_AI_API,
        )

    def index_project(
        self, db: Session, project_id: str, documents: dict[str, str]
    ) -> None:
        db.query(ProjectRAGDocument).filter(
            ProjectRAGDocument.project_id == project_id
        ).delete(synchronize_session=False)

        rows: list[ProjectRAGDocument] = []
        for document_type, content in documents.items():
            if not content or not content.strip():
                continue
            for chunk_index, chunk in enumerate(self._chunks(content)):
                embedding = self.embeddings.embed_query(chunk)
                rows.append(
                    ProjectRAGDocument(
                        id=str(uuid.uuid4()),
                        project_id=project_id,
                        document_type=document_type,
                        chunk_index=chunk_index,
                        content=chunk,
                        embedding=json.dumps(embedding),
                        created_at=datetime.now(timezone.utc),
                    )
                )

        db.add_all(rows)
        db.commit()

    def build_messages(self, db: Session, project_id: str, question: str):
        """Retrieve concise context using FAISS and build the private model prompt with Memory."""
        query_embedding = self.embeddings.embed_query(question)
        rows = (
            db.query(ProjectRAGDocument)
            .filter(ProjectRAGDocument.project_id == project_id)
            .all()
        )
        if not rows:
            raise ValueError("This project has no indexed documents yet.")

        # --- FAISS INTEGRATION (Using existing DB embeddings) ---
        text_embeddings = [(row.content, json.loads(row.embedding)) for row in rows]
        metadatas = [{"document_type": row.document_type} for row in rows]

        vectorstore = FAISS.from_embeddings(
            text_embeddings=text_embeddings,
            embedding=self.embeddings,
            metadatas=metadatas,
        )

        # Retrieve top 6 documents
        docs = vectorstore.similarity_search_by_vector(query_embedding, k=6)
        context = "\n\n".join(
            f"[{doc.metadata['document_type']}]\n{doc.page_content}" for doc in docs
        )

        if not context:
            context = "No relevant project context was found."

        # --- MEMORY INTEGRATION (Fetch Chat History) ---
        history = (
            db.query(ProjectChatHistory)
            .filter(ProjectChatHistory.project_id == project_id)
            .order_by(ProjectChatHistory.created_at.asc())
            .all()
        )

        messages = [
            SystemMessage(
                content=(
                    "You are an intelligent, helpful, & friendly project documentation assistant. "
                    "If the user is just greeting you, introducing themselves, or making casual conversation, respond naturally and warmly. "
                    "For any technical or project-related questions, answer directly in 2-5 short paragraphs or bullets, using ONLY the private project context below. "
                    "Do not explain the retrieval process, list all documents, or dump large excerpts. "
                    "If a technical question is unsupported by the context, clearly say that the project documents do not specify it. "
                    "Never invent commands, endpoints, files, or behavior."
                )
            )
        ]

        # Add last 10 messages to maintain context limit
        for msg in history[-5:]:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))

        # Add current question
        messages.append(
            HumanMessage(content=f"Project context:\n{context}\n\nQuestion: {question}")
        )

        return messages, [doc.metadata["document_type"] for doc in docs]

    async def stream_answer(
        self, db: Session, project_id: str, question: str, messages: list
    ):
        # 1. Save User Question to DB
        user_msg = ProjectChatHistory(
            project_id=project_id, role="user", content=question
        )
        db.add(user_msg)
        db.commit()

        full_answer = ""
        # 2. Stream Response
        async for chunk in self.chat_model.astream(messages):
            content = chunk.content
            if isinstance(content, str) and content:
                full_answer += content
                yield content

        # 3. Save Assistant Response to DB after streaming finishes
        ai_msg = ProjectChatHistory(
            project_id=project_id, role="assistant", content=full_answer
        )
        db.add(ai_msg)
        db.commit()

    @staticmethod
    def _chunks(content: str, size: int = 6000) -> list[str]:
        return [content[index : index + size] for index in range(0, len(content), size)]
