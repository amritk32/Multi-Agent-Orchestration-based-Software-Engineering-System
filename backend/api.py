import json
import threading
import queue
from fastapi.encoders import jsonable_encoder
from aapi import OPEN_AI_API
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from datetime import datetime
from sqlalchemy import inspect, text
from mod2_workflow import Module2Workflow
from schemas import AuditInput, Module3

import traceback

from sqlalchemy.orm import Session
from database.database import Base, engine, SessionLocal
from database.models import ProjectDetails, Artifacts, CyberIntelligenceReport

from agents import Agents
from mod1_workflow import Module1Workflow
from events import set_event_queue
from requirements_validation import validate_requirements
from rag_service import ProjectRAGService

from database.models import ProjectDetails, Artifacts

app = FastAPI(
    title="Krishna Code AI",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateProjectRequest(BaseModel):
    project_name: str


class ProjectResponse(BaseModel):
    project_id: str
    project_name: str
    created_at: datetime


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

    # create_all does not alter existing SQLite tables, so add fields introduced
    # after the first database initialization explicitly.
    with engine.begin() as connection:
        artifact_columns = {
            column["name"] for column in inspect(connection).get_columns("artifacts")
        }
        if "readme" not in artifact_columns:
            connection.execute(text("ALTER TABLE artifacts ADD COLUMN readme TEXT"))


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@app.post("/api/projects", response_model=ProjectResponse)
def create_project(
    request: CreateProjectRequest,
    db: Session = Depends(get_db),
):

    project_name = request.project_name.strip()

    if not project_name:
        raise HTTPException(
            status_code=400,
            detail="Project name cannot be empty.",
        )

    project = ProjectDetails(
        project_name=project_name,
    )

    db.add(project)

    db.commit()

    db.refresh(project)

    return {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "created_at": project.created_at,
    }


class GenerateRequest(BaseModel):
    project_id: str
    requirements: str


api_key = OPEN_AI_API

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set. Export it before starting FastAPI.")


llm1 = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0,
    api_key=api_key,
)
llm2 = ChatOpenAI(
    model="gpt-5-nano",
    temperature=0,
    api_key=api_key,
)

agents = Agents(llm1, llm2)
workflow = Module1Workflow(agents)
module2_workflow = Module2Workflow(agents)
rag_service = ProjectRAGService()


def index_project_documents(db: Session, project_id: str, result: dict) -> None:
    """Index every generated project source used by the project chatbot."""
    rag_service.index_project(
        db,
        project_id,
        {
            "requirements": result.get("requirements", ""),
            "architecture": result.get("architecture", ""),
            "boilerplate": result.get("boilerplate", ""),
            "backend": result.get("backend_code", ""),
            "frontend": result.get("frontend_code", ""),
            "readme": result.get("report", ""),
        },
    )


class ProjectChatRequest(BaseModel):
    question: str


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "Krishna Code AI",
    }


# Process a request(Generate the code) and log into database
@app.post("/api/generate")
def generate(
    request: GenerateRequest,
    db: Session = Depends(get_db),
):
    requirements = request.requirements.strip()

    if not requirements:
        raise HTTPException(
            status_code=400,
            detail="Requirements cannot be empty.",
        )

    validation_error = validate_requirements(requirements)
    if validation_error:
        raise HTTPException(status_code=400, detail=validation_error)

    # Verify project exists
    project = (
        db.query(ProjectDetails)
        .filter(ProjectDetails.project_id == request.project_id)
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    try:
        print(f"\n{'='*60}")
        print(f"Starting workflow for project: {project.project_name}")
        print(f"{'='*60}\n")

        # Invoke workflow with proper state initialization
        result = workflow.graph.invoke(
            {
                "requirements": requirements,
                "architecture": "",
                "boilerplate": "",
                "code": "",
                "syntax_valid": False,
                "syntax_error": None,
                "report": "",
            }
        )

        # Check if artifact already exists
        existing_artifact = (
            db.query(Artifacts)
            .filter(Artifacts.project_id == request.project_id)
            .first()
        )

        if existing_artifact:
            # Update existing artifact
            existing_artifact.requirements = result.get("requirements", "")
            existing_artifact.architecture = result.get("architecture", "")
            existing_artifact.boilerplate = result.get("boilerplate", "")
            existing_artifact.generated_code = result.get("code", "")
            # Added Backend and frontend code logging
            existing_artifact.backend_code = result.get("backend_code", "")
            existing_artifact.frontend_code = result.get("frontend_code", "")
            existing_artifact.readme = result.get("report", "")
        else:
            # Create new artifact
            artifact = Artifacts(
                project_id=request.project_id,
                requirements=result.get("requirements", ""),
                architecture=result.get("architecture", ""),
                boilerplate=result.get("boilerplate", ""),
                generated_code=result.get("code", ""),
                # Added Backend and frontend code logging
                backend_code=result.get("backend_code", ""),
                frontend_code=result.get("frontend_code", ""),
                readme=result.get("report", ""),
            )
            db.add(artifact)

        db.commit()
        index_project_documents(db, request.project_id, result)

        print(f"\n{'='*60}")
        print(f"Workflow completed successfully!")
        print(f"{'='*60}\n")

    except Exception as exc:
        print(f"\n{'='*60}")
        print(f"❌ WORKFLOW ERROR: {str(exc)}")
        print(f"{'='*60}\n")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {exc}",
        ) from exc

    return {
        "requirements": result.get("requirements", ""),
        "architecture": result.get("architecture", ""),
        "boilerplate": result.get("boilerplate", ""),
        "code": result.get("code", ""),
        "backend_code": result.get("backend_code", ""),
        "frontend_code": result.get("frontend_code", ""),
        "syntax_valid": result.get("syntax_valid", False),
        "syntax_error": result.get("syntax_error"),
        "report": result.get("report", ""),
    }


# Added Module 3 endpoint
@app.post("/api/projects/{project_id}/audit")
def audit_project(
    project_id: str,
    db: Session = Depends(get_db),
):
    """Audit a project's generated backend and persist its report."""

    project = (
        db.query(ProjectDetails).filter(ProjectDetails.project_id == project_id).first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    artifact = db.query(Artifacts).filter(Artifacts.project_id == project_id).first()

    if artifact is None or not (artifact.backend_code or "").strip():
        raise HTTPException(
            status_code=400,
            detail="This project has no generated backend code to audit.",
        )

    try:
        initial_state = Module3(
            source_code=artifact.backend_code,
        )

        result = module2_workflow.graph.invoke(initial_state.model_dump())

        report = result.get("final_report")

        if not report:
            raise RuntimeError("Audit workflow returned no final report.")

        # Store the report as JSON in the existing ORM model.
        report_json = json.dumps(
            jsonable_encoder(report),
            ensure_ascii=False,
        )

        saved_report = (
            db.query(CyberIntelligenceReport)
            .filter(CyberIntelligenceReport.project_id == project_id)
            .first()
        )

        if saved_report is None:
            saved_report = CyberIntelligenceReport(
                project_id=project_id,
                status="completed",
                report_json=report_json,
            )
            db.add(saved_report)
        else:
            saved_report.status = "completed"
            saved_report.report_json = report_json
            saved_report.created_at = datetime.now().astimezone()

        db.commit()
        db.refresh(saved_report)

        return {
            "success": True,
            "project_id": project_id,
            "report_id": saved_report.id,
            "status": saved_report.status,
            "created_at": saved_report.created_at,
            "report": json.loads(saved_report.report_json),
        }

    except Exception as exc:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# Get Audited Project Details
@app.get("/api/projects/{project_id}/audit")
def get_project_audit(
    project_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve the latest saved cyber-intelligence report."""

    project = (
        db.query(ProjectDetails).filter(ProjectDetails.project_id == project_id).first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    saved_report = (
        db.query(CyberIntelligenceReport)
        .filter(CyberIntelligenceReport.project_id == project_id)
        .first()
    )

    if saved_report is None:
        raise HTTPException(
            status_code=404,
            detail="No audit report exists for this project.",
        )

    return {
        "project_id": project_id,
        "report_id": saved_report.id,
        "status": saved_report.status,
        "created_at": saved_report.created_at,
        "report": json.loads(saved_report.report_json),
    }


# ------------------


# Token by token streaming
@app.get("/api/generate-stream")
async def generate_stream(
    requirements: str,
    project_id: str,
    db: Session = Depends(get_db),
):
    """
    Stream-based code generation endpoint using Server-Sent Events.
    Emits real-time updates as each agent in the workflow completes.
    """
    requirements = requirements.strip()

    if not requirements:
        raise HTTPException(
            status_code=400,
            detail="Requirements cannot be empty.",
        )

    validation_error = validate_requirements(requirements)
    if validation_error:
        raise HTTPException(status_code=400, detail=validation_error)

    project = (
        db.query(ProjectDetails).filter(ProjectDetails.project_id == project_id).first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    async def event_generator():
        """Generator that yields Server-Sent Events"""
        # Create event queue for this stream
        event_q: queue.Queue = queue.Queue()
        set_event_queue(event_q)

        try:
            # Emit start event
            yield f"data: {json.dumps({'type': 'status', 'message': 'Starting code generation workflow'})}\n\n"

            print(f"\n{'='*60}")
            print(f"Starting streaming workflow...")
            print(f"{'='*60}\n")

            # Run workflow in a thread so we can monitor the queue
            result_holder = {}
            exception_holder = {}

            def run_workflow():
                try:
                    result_holder["result"] = workflow.graph.invoke(
                        {
                            "requirements": requirements,
                            "architecture": "",
                            "boilerplate": "",
                            "code": "",
                            "syntax_valid": False,
                            "syntax_error": None,
                            "report": "",
                        }
                    )
                except Exception as e:
                    exception_holder["error"] = e
                finally:
                    # Signal completion
                    event_q.put({"type": "workflow_done"})

            workflow_thread = threading.Thread(target=run_workflow, daemon=True)
            workflow_thread.start()

            # Monitor queue and emit events
            workflow_complete = False
            while not workflow_complete:
                try:
                    # Get events from queue with timeout to avoid blocking forever
                    event = event_q.get(timeout=0.1)

                    if event["type"] == "workflow_done":
                        workflow_complete = True
                        break
                    elif event["type"] == "agent_start":
                        yield f"data: {json.dumps({'type': 'agent_start', 'agent': event.get('agent')})}\n\n"
                    elif event["type"] == "agent_end":
                        agent_event = {
                            "type": "agent_end",
                            "agent": event.get("agent"),
                        }
                        if event.get("agent") == "syntax_analysis":
                            agent_event.update(
                                {
                                    "syntax_valid": event.get("syntax_valid"),
                                    "syntax_error": event.get("syntax_error"),
                                }
                            )
                        yield f"data: {json.dumps(agent_event)}\n\n"
                    elif event["type"] in {"file_start", "file_end"}:
                        yield f"data: {json.dumps(event)}\n\n"
                    elif event["type"] == "code_token":
                        yield f"data: {json.dumps({'type': 'code_token', 'token': event.get('token', ''), 'file': event.get('file')})}\n\n"
                except queue.Empty:
                    # No events, continue waiting
                    if not workflow_thread.is_alive():
                        # Thread finished but didn't signal completion properly
                        workflow_complete = True
                        break
                    continue

            # Check if there was an error
            if "error" in exception_holder:
                raise exception_holder["error"]

            result = result_holder.get("result", {})

            artifact = (
                db.query(Artifacts).filter(Artifacts.project_id == project_id).first()
            )
            if artifact is None:
                artifact = Artifacts(project_id=project_id)
                db.add(artifact)

            artifact.requirements = result.get("requirements", "")
            artifact.architecture = result.get("architecture", "")
            artifact.boilerplate = result.get("boilerplate", "")
            artifact.generated_code = result.get("code", "")
            # Added Backend and frontend code logging
            artifact.backend_code = result.get("backend_code", "")
            artifact.frontend_code = result.get("frontend_code", "")
            artifact.readme = result.get("report", "")
            db.commit()
            index_project_documents(db, project_id, result)

            print(f"\n{'='*60}")
            print(f"Streaming workflow completed!")
            print(f"{'='*60}\n")

            # Emit complete event with full result
            completion_data = {
                "type": "complete",
                "data": {
                    "requirements": result.get("requirements", ""),
                    "architecture": result.get("architecture", ""),
                    "boilerplate": result.get("boilerplate", ""),
                    "code": result.get("code", ""),
                    "backend_code": result.get("backend_code", ""),
                    "frontend_code": result.get("frontend_code", ""),
                    "syntax_valid": result.get("syntax_valid", False),
                    "syntax_error": result.get("syntax_error"),
                    "report": result.get("report", ""),
                },
            }
            safe_data = jsonable_encoder(completion_data)
            yield f"data: {json.dumps(safe_data)}\n\n"

        except Exception as exc:
            print(f"\n{'='*60}")
            print(f"❌ STREAMING WORKFLOW ERROR: {str(exc)}")
            print(f"{'='*60}\n")
            import traceback

            traceback.print_exc()
            error_message = f"Workflow execution failed: {str(exc)}"
            yield f"data: {json.dumps({'type': 'error', 'error': error_message})}\n\n"
        finally:
            # Clean up
            set_event_queue(None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# Token streaming for Chatbot
@app.post("/api/projects/{project_id}/chat-stream")
async def stream_project_chat(
    project_id: str,
    request: ProjectChatRequest,
    db: Session = Depends(get_db),
):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    project = (
        db.query(ProjectDetails).filter(ProjectDetails.project_id == project_id).first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    try:
        messages, sources = rag_service.build_messages(db, project_id, question)
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"Project chatbot is unavailable: {exc}"
        ) from exc

    async def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
            async for token in rag_service.stream_answer(
                db, project_id, question, messages
            ):
                yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
            yield 'data: {"type": "complete"}\n\n'
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# Show all projects
@app.get("/api/projects")
def list_projects(db: Session = Depends(get_db)):
    """
    Get all projects from the database.
    Returns project_id, project_name, and created_at.
    """
    projects = db.query(ProjectDetails).order_by(ProjectDetails.created_at.desc()).all()

    return [
        {
            "project_id": p.project_id,
            "project_name": p.project_name,
            "created_at": p.created_at,
        }
        for p in projects
    ]


# Fetch the project and its artifacts
@app.get("/api/projects/{project_id}")
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a specific project and its artifacts.
    """
    project = (
        db.query(ProjectDetails).filter(ProjectDetails.project_id == project_id).first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    artifacts = db.query(Artifacts).filter(Artifacts.project_id == project_id).first()

    return {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "created_at": project.created_at,
        "artifacts": (
            {
                "requirements": artifacts.requirements if artifacts else None,
                "architecture": artifacts.architecture if artifacts else None,
                "boilerplate": artifacts.boilerplate if artifacts else None,
                "generated_code": artifacts.generated_code if artifacts else None,
                "backend_code": artifacts.backend_code if artifacts else None,
                "frontend_code": artifacts.frontend_code if artifacts else None,
                "readme": artifacts.readme if artifacts else None,
            }
            if artifacts
            else None
        ),
    }


# Delete the project from database
@app.delete("/api/projects/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
):
    """Delete a project and all artifacts owned by it."""
    project = (
        db.query(ProjectDetails).filter(ProjectDetails.project_id == project_id).first()
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    try:
        db.query(Artifacts).filter(Artifacts.project_id == project_id).delete(
            synchronize_session=False
        )
        db.delete(project)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to delete project.",
        ) from exc

    return {"project_id": project_id, "deleted": True}
