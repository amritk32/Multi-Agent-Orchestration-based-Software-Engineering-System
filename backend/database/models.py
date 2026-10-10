import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class ProjectDetails(Base):

    __tablename__ = "project_details"

    project_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    project_name = Column(
        String,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    artifacts = relationship(
        "Artifacts",
        back_populates="project",
        cascade="all, delete-orphan",
        uselist=False,
    )


class Artifacts(Base):

    __tablename__ = "artifacts"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    project_id = Column(
        String(36),
        ForeignKey("project_details.project_id"),
        nullable=False,
        unique=True,
    )

    requirements = Column(
        Text,
        nullable=True,
    )

    architecture = Column(
        Text,
        nullable=True,
    )

    boilerplate = Column(
        Text,
        nullable=True,
    )

    generated_code = Column(
        Text,
        nullable=True,
    )

    # Added seperate attributes for backend and frontend code logging
    backend_code = Column(Text, nullable=True)

    frontend_code = Column(Text, nullable=True)

    readme = Column(
        Text,
        nullable=True,
    )

    project = relationship(
        "ProjectDetails",
        back_populates="artifacts",
    )


class ProjectRAGDocument(Base):

    __tablename__ = "project_rag_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(
        String(36),
        ForeignKey("project_details.project_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_type = Column(String(40), nullable=False)
    chunk_index = Column(Integer, nullable=False, default=0)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)


class ProjectChatHistory(Base):
    __tablename__ = "project_chat_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(
        String(36),
        ForeignKey("project_details.project_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class CyberIntelligenceReport(Base):
    __tablename__ = "cyber_intelligence_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    project_id = Column(
        String(36),
        ForeignKey("project_details.project_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    status = Column(String(30), nullable=False, default="completed")
    report_json = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
