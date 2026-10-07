# Krishna.code

Krishna.code is an AI-native software engineering workspace. It turns a natural-language software request into structured requirements, architecture, boilerplate, separate backend and frontend source streams, syntax feedback, and a generated README.

The workspace also provides a project-scoped RAG assistant. After generation, users can ask questions about the project without manually reading long artifacts. The assistant retrieves the project's indexed requirements, architecture, boilerplate, backend, frontend, and README context before answering.

## Features

- Project creation and saved-project browsing.
- Project deletion with confirmation and artifact cleanup.
- Requirements validation that rejects empty, short, or obvious gibberish input.
- LangGraph workflow with these stages:
  1. Requirements analysis
  2. Architecture design
  3. Boilerplate planning
  4. Backend generation
  5. Frontend generation
  6. Python syntax analysis
  7. README generation
- Backend and frontend generated separately and streamed live to the code page.
- Backend output constrained to Python.
- Library-first generation prompts that prefer established frameworks and packages for databases, RAG, APIs, validation, integrations, and other substantial capabilities.
- Copyable generated code panels.
- Artifact page for requirements, architecture, boilerplate, and README.
- Project-scoped RAG indexing with OpenAI embeddings.
- Streaming project chatbot responses through Server-Sent Events.
- Source labels showing which project documents informed an answer.
- SQLite persistence for projects, artifacts, and indexed RAG document chunks.

## Requirements

- Python 3.10 or newer
- Node.js 16 or newer
- npm
- An OpenAI API key

The backend uses OpenAI models for generation, embeddings, and project chat. The API key is read from `OPENAI_API_KEY`.

## Configuration

Set the key in the shell that will run the backend:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

Never commit an API key, `.env` file containing a key, virtual environment, SQLite database, or generated build output.

## Installation

From the repository root:

```bash
chmod +x SETUP.sh run.sh
./SETUP.sh
```

`SETUP.sh` creates `backend/venv` and installs the backend/frontend dependencies. The SQLite database is created automatically when the API starts.

For manual setup:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn pydantic python-dotenv sqlalchemy langchain-openai langchain-core langgraph langchain-ollama

cd ../frontend
npm install
```

## Start The Application

### Recommended: two terminals

Terminal 1, backend:

```bash
cd backend
source venv/bin/activate
export OPENAI_API_KEY="your-openai-api-key"
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2, frontend:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`.

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Health check: `http://localhost:8000/api/health`

The frontend defaults to `http://localhost:8000` for the backend. To use another backend URL:

```bash
VITE_API_URL="http://localhost:9000" npm run dev
```

### Combined launcher

`run.sh` starts Uvicorn and Vite together:

```bash
export OPENAI_API_KEY="your-openai-api-key"
./run.sh
```

For predictable virtual-environment behavior, use the two-terminal instructions above. Stop the combined launcher with `Ctrl+C`.

## User Workflow

1. Create a project from the home screen.
2. Enter meaningful software requirements.
3. Watch the pipeline progress through requirements, architecture, boilerplate, backend, frontend, syntax analysis, and README generation.
4. Inspect backend and frontend code in separate live panels. Each panel has its own copy action.
5. Open **Artifacts** to inspect requirements, architecture, boilerplate, or README.
6. Open **Ask the project** to use the grounded chatbot.
7. Open **Open Project** later to reload saved projects.
8. Hover a saved project and choose **DELETE** to remove it after confirmation.

## RAG Project Chat

When generation completes, the backend indexes these project documents:

- Requirements
- Architecture
- Boilerplate
- Generated backend source
- Generated frontend source
- README

Documents are chunked, embedded with OpenAI embeddings, and stored in the SQLite `project_rag_documents` table. A chat question retrieves only chunks belonging to the selected project. Retrieved context is sent privately to the OpenAI chat model and is not dumped directly into the UI.

The assistant streams its answer token by token. It is instructed to answer briefly, stay grounded in project documents, and say when the project does not specify an answer instead of inventing commands, files, endpoints, or behavior.

## Backend API

### Projects

```http
POST   /api/projects
GET    /api/projects
GET    /api/projects/{project_id}
DELETE /api/projects/{project_id}
```

Create a project:

```json
{
  "project_name": "RAG Knowledge Assistant"
}
```

### Generation

Synchronous generation:

```http
POST /api/generate
Content-Type: application/json
```

```json
{
  "project_id": "project-uuid",
  "requirements": "Build a Python RAG assistant with document upload and project-scoped chat"
}
```

Streaming generation:

```http
GET /api/generate-stream?project_id=project-uuid&requirements=Build%20a%20RAG%20assistant
Accept: text/event-stream
```

Generation SSE messages include status updates, agent lifecycle events, backend/frontend file lifecycle events, code tokens, syntax results, completion data, and errors.

### Project chatbot

```http
POST /api/projects/{project_id}/chat-stream
Content-Type: application/json
Accept: text/event-stream
```

```json
{
  "question": "How do I start the backend?"
}
```

Chat SSE messages include retrieved source labels, answer tokens, completion, and error events.

### Health

```http
GET /api/health
```

## Backend Structure

```text
backend/
├── api.py                       FastAPI routes, SSE endpoints, persistence
├── agents.py                    LLM agent wrappers and sequential file generation
├── mod1_workflow.py             LangGraph workflow and agent events
├── prompts.py                   Requirements, architecture, boilerplate, code, README prompts
├── schemas.py                   Pydantic workflow state and review models
├── rag_service.py               Project document indexing and grounded chat retrieval
├── syntax_analysis.py           Python AST syntax analyzer
├── generated_code_validation.py Backend/frontend separation checks
├── requirements_validation.py   User-input validation
├── events.py                    Thread-safe workflow event queue
├── aapi.py                      Environment-based OpenAI key loading
└── database/
    ├── database.py              SQLAlchemy engine, Base, and sessions
    └── models.py                Projects, artifacts, and RAG document models
```

## Frontend Structure

```text
frontend/src/
├── App.tsx                       Screen-level routing
├── api.ts                        Axios and SSE API clients
├── types.ts                      Shared API and workflow types
├── styles.css                    Application design system and responsive styles
└── components/
    ├── HomePage.tsx              Home and project entry point
    ├── CreateProjectModal.tsx    Project creation dialog
    ├── OpenProject.tsx           Saved project browser and deletion flow
    ├── ProjectWorkflow.tsx       Generation pipeline and code panels
    ├── ArtifactPage.tsx          Artifact inspection and copy actions
    └── ProjectChatPage.tsx       Streaming grounded project chatbot
```

## Tests And Builds

Run backend tests from the repository root:

```bash
PYTHONPATH=backend python -m unittest discover -s backend/tests -p 'test_*.py'
```

Compile backend modules:

```bash
python -m py_compile backend/*.py backend/database/*.py
```

Build the frontend:

```bash
cd frontend
npm run build
```

The frontend build runs TypeScript checking before the Vite production build.

## Troubleshooting

### `OPENAI_API_KEY is not set`

Set the key in the same terminal that starts Uvicorn:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Frontend cannot reach the backend

Check that Uvicorn is running on port `8000`:

```bash
curl http://localhost:8000/api/health
```

For another backend port or host, set `VITE_API_URL` before running Vite.

### The project chatbot has no context

The chatbot can answer after generation completes and its documents are indexed. Regenerate projects created before RAG indexing was enabled.

### SQLite data

The runtime database is `backend/krishna_code_ai.db`. It contains project metadata, saved artifacts, and project-scoped RAG document embeddings. Back it up if project persistence matters; do not commit it to source control.

## Repository Hygiene

Do not upload:

- `backend/venv/`
- `.venv/`
- `frontend/node_modules/`
- `frontend/dist/`
- `__pycache__/`
- `*.pyc`
- `*.db`
- `.env`
- API keys
