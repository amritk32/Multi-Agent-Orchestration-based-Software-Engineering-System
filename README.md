# Krishna Code AI

Krishna Code AI is an AI-native software engineering workspace that turns a
natural-language software request into structured requirements, architecture,
boilerplate, backend and frontend source code, syntax feedback, and project
documentation.

The workspace also includes a project-scoped assistant. After a generation
completes, users can ask questions about the saved project and receive grounded
answers based on its indexed requirements, architecture, boilerplate, backend,
frontend, and README artifacts.

## Features

- Supabase email/password signup and login.
- Persistent authenticated sessions with automatic token refresh.
- Protected frontend workspace and logout confirmation.
- Bearer-token authentication for protected FastAPI requests.
- User-scoped project listing, creation, retrieval, generation, auditing, chat,
  and deletion.
- Project creation, saved-project browsing, and deletion confirmation.
- Requirements validation for empty, short, or obviously invalid input.
- LangGraph generation workflow:
  1. Requirements analysis
  2. Architecture design
  3. Boilerplate planning
  4. Backend generation
  5. Frontend generation
  6. Python syntax analysis
  7. README generation
- Separate live backend and frontend code streams, delivered through
  project-scoped asynchronous event queues so independent projects can stream
  concurrently.
- Copyable generated code and artifact panels.
- Project-scoped RAG indexing with OpenAI embeddings.
- Streaming project chatbot responses through Server-Sent Events.
- Source labels showing which project documents informed a chatbot answer.
- SQLite persistence for projects, artifacts, and indexed RAG document chunks.
- Cyber Intelligence security assessments for generated backend code.

## Architecture

The frontend uses Supabase Auth as the identity provider. The FastAPI backend
does not implement a second signup or login system.

1. A user signs up or signs in through Supabase from the React frontend.
2. Supabase restores the session after a page refresh and refreshes tokens
   automatically.
3. The centralized frontend API client obtains the current access token.
4. Protected FastAPI requests include:

   ```http
   Authorization: Bearer <supabase-access-token>
   ```

5. FastAPI verifies the JWT using the Supabase JWKS endpoint.
6. Project queries are filtered by the authenticated JWT `sub` claim.
7. An HTTP 401 response clears the frontend session and returns the user to
   login.

Passwords, access tokens, and refresh tokens are not manually stored or
printed by the application.

## Requirements

- Python 3.10 or newer
- Node.js 16 or newer
- npm
- A Supabase project
- An OpenAI API key

The backend uses OpenAI models for generation, embeddings, and project chat.
The key is read from `OPEN_AI_API` in `backend/.env`.

## Supabase setup

Create or use a Supabase project and configure the Email provider under
**Authentication → Providers**.

Email confirmation may be enabled or disabled:

- If disabled, signup creates an active session immediately.
- If enabled, signup displays a confirmation message and the user must confirm
  the email before signing in.

The backend currently verifies tokens for the Supabase project configured in
`backend/auth/security.py`. The frontend `VITE_SUPABASE_URL` must refer to the
same project.

## Environment configuration

### Backend

Add the backend API keys to `backend/.env`:

```bash
OPEN_AI_API="your-openai-api-key"
```

Save these values in `backend/.env`. The backend loads that file automatically.
Never commit API keys, `.env` files containing secrets, virtual environments,
SQLite databases, or generated build output.

### Frontend

Create or update `frontend/.env`:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-supabase-publishable-key
VITE_API_URL=http://localhost:8000
```

`VITE_SUPABASE_PUBLISHABLE_KEY` must be a real Supabase publishable/anonymous
client key. The placeholder value `your_actual_publishable_key` is not valid.
Restart Vite after changing environment variables.

`VITE_API_URL` is optional and defaults to `http://localhost:8000`.
For local development, set it explicitly to `http://localhost:8000`. If it is
set to a deployed URL, `npm run dev` will still load the frontend locally but
all project, generation, and audit requests will go to that remote backend;
the local uvicorn terminal will therefore show no request or agent logs.

## Installation

From the repository root:

```bash
chmod +x SETUP.sh run.sh
./SETUP.sh
```

The setup script creates `backend/venv` and installs backend and frontend
dependencies. The SQLite database is created automatically when the API starts.

For manual setup:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn pydantic python-dotenv sqlalchemy \
  langchain langchain-openai langchain-core langchain-community \
  langgraph langchain-ollama faiss-cpu rank-bm25

cd ../frontend
npm install
```

## Run the application

### Recommended: two terminals

Terminal 1, backend:

```bash
cd backend
source venv/bin/activate
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2, frontend:

```bash
cd frontend
npm run dev
```

Open <http://localhost:5173>.

| Service | URL |
|---|---|
| Frontend | <http://localhost:5173> |
| Backend | <http://localhost:8000> |
| Health check | <http://localhost:8000/api/health> |

### Combined launcher

`run.sh` starts Uvicorn and Vite together:

```bash
./run.sh
```

Run `./SETUP.sh` first so the expected virtual environments and dependencies
exist. Stop the combined launcher with `Ctrl+C`.

## User workflow

1. Open the frontend and create an account or sign in.
2. Confirm the email first if Supabase email confirmation is enabled.
3. Create a project from the home screen.
4. Enter meaningful software requirements.
5. Watch the generation pipeline progress through each workflow stage.
6. Inspect backend and frontend code in separate live panels.
7. Open **Artifacts** to inspect requirements, architecture, boilerplate,
   generated code, and README content.
8. Open **Ask the project** to use the grounded project assistant.
9. Open **Open Project** later to reload projects belonging to the signed-in
   user.
10. Open **Cyber Intelligence** to select a saved project and run a security
    assessment against its generated backend.
11. Use **Sign out**, then confirm the logout action.

Unauthenticated users cannot access the project workspace. The backend remains
the final authorization boundary even if a frontend request is modified.

The frontend uses the shared Krishna Code AI logo across workspace screens.
Cyber Intelligence project panels stack on narrow screens, and generated code
and assessment findings remain within the mobile viewport.

## Backend API

All endpoints below are protected unless explicitly marked public. Protected
requests must include:

```http
Authorization: Bearer <supabase-access-token>
```

### Public endpoints

```http
GET /api/health
```

### Projects

```http
POST   /api/projects
GET    /api/projects
GET    /api/projects/{project_id}
DELETE /api/projects/{project_id}
```

Create a project:

```http
POST /api/projects
Content-Type: application/json
Authorization: Bearer <supabase-access-token>
```

```json
{
  "project_name": "RAG Knowledge Assistant"
}
```

Project list, detail, generation, audit, chat, and deletion operations only
operate on projects owned by the authenticated user.

### Generation

Synchronous generation:

```http
POST /api/generate
Content-Type: application/json
Authorization: Bearer <supabase-access-token>
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
Authorization: Bearer <supabase-access-token>
Accept: text/event-stream
```

Generation SSE messages include status updates, agent lifecycle events,
backend/frontend file events, code tokens, syntax results, completion data, and
errors.

### Security audit

```http
POST /api/projects/{project_id}/audit
Authorization: Bearer <supabase-access-token>
```

### Project chatbot

```http
POST /api/projects/{project_id}/chat-stream
Content-Type: application/json
Authorization: Bearer <supabase-access-token>
Accept: text/event-stream
```

```json
{
  "question": "How do I start the backend?"
}
```

Chat SSE messages include retrieved source labels, answer tokens, completion,
and error events.

## RAG project chat

When generation completes, the backend indexes:

- Requirements
- Architecture
- Boilerplate
- Generated backend source
- Generated frontend source
- README

Documents are chunked, embedded with OpenAI embeddings, and stored in the
SQLite `project_rag_documents` table. Retrieval is restricted to the selected
project. The assistant is instructed to stay grounded in project documents and
to say when the project does not specify an answer.

## Project structure

```text
backend/
├── api.py                       FastAPI routes, SSE endpoints, persistence
├── auth/
│   ├── dependencies.py          Bearer token dependency and current-user lookup
│   ├── security.py              Supabase JWKS/JWT verification
│   └── variables.py             Supabase backend configuration
├── agents.py                    LLM agent wrappers and generation helpers
├── mod1_workflow.py             LangGraph generation workflow
├── mod2_workflow.py             Security audit workflow
├── prompts.py                   Generation and review prompts
├── schemas.py                   Pydantic workflow state and review models
├── rag_service.py               Project document indexing and chat retrieval
├── syntax_analysis.py           Python AST syntax analyzer
├── requirements_validation.py   User-input validation
├── events.py                    Project-scoped asynchronous event queues
├── aapi.py                      Environment-based OpenAI key loading
└── database/
    ├── database.py              SQLAlchemy engine, Base, and sessions
    └── models.py                Projects, artifacts, and RAG document models

frontend/src/
├── auth/
│   ├── supabase.ts              Supabase browser client
│   ├── AuthContext.tsx          Session restoration and auth state
│   ├── AuthForm.tsx             Shared login/signup form
│   ├── LoginPage.tsx            Login experience
│   └── SignupPage.tsx           Signup experience
├── App.tsx                      Auth guard and screen-level routing
├── api.ts                       Authenticated Axios and streaming API client
├── main.tsx                     React entry point and AuthProvider
├── types.ts                     Shared API and workflow types
├── styles.css                   Application design system and responsive styles
└── components/
    ├── HomePage.tsx             Home and project entry point
    ├── CreateProjectModal.tsx   Project creation dialog
    ├── OpenProject.tsx          Saved project browser and deletion flow
    ├── ProjectWorkflow.tsx      Generation pipeline and code panels
    ├── ArtifactPage.tsx         Artifact inspection and copy actions
    ├── ProjectChatPage.tsx      Streaming grounded project chatbot
    └── CyberIntelligencePage.tsx Security assessment interface
```

## Tests and builds

Run backend tests from the repository root:

```bash
PYTHONPATH=backend python -m unittest discover -s backend/tests -p 'test_*.py'
```

Compile backend modules:

```bash
python -m py_compile backend/*.py backend/auth/*.py backend/database/*.py
```

Build the frontend:

```bash
cd frontend
npm run build
```

The frontend build runs TypeScript checking before the Vite production build.

## Troubleshooting

### The frontend is blank or shows a configuration message

Check `frontend/.env` and replace the placeholder Supabase key:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-real-publishable-key
```

Restart Vite after changing the file.

### Signup succeeds but login does not

Email confirmation is probably enabled in Supabase. Confirm the registration
email, then sign in again. Also verify that the frontend URL is included in
Supabase Auth redirect/site URL settings.

### Requests return `401 Unauthorized`

Verify that:

1. The user is signed in.
2. The frontend and backend use the same Supabase project.
3. `VITE_SUPABASE_URL` is correct.
4. The frontend is not still using the placeholder publishable key.
5. FastAPI is running and its Supabase JWKS endpoint is reachable.

The frontend automatically clears the session after a 401 and returns to login.

### Frontend cannot reach the backend

Check the backend:

```bash
curl http://localhost:8000/api/health
```

For another backend host or port:

```bash
VITE_API_URL="http://localhost:9000" npm run dev
```

### `OPEN_AI_API is not set`

Add the key to `backend/.env` and restart the backend:

```env
OPEN_AI_API="your-openai-api-key"
```

### The project chatbot has no context

Chat context becomes available after generation completes and documents are
indexed. Regenerate projects created before RAG indexing was enabled.

### SQLite data

The runtime database is `backend/krishna_code_ai.db`. It contains project
metadata, saved artifacts, and project-scoped RAG document embeddings. Back it
up if project persistence matters; do not commit it to source control.

## Repository hygiene

Do not upload or commit:

- `backend/venv/`
- `.venv/`
- `frontend/node_modules/`
- `frontend/dist/`
- `__pycache__/`
- `*.pyc`
- `*.db`
- `.env`
- API keys or Supabase secrets
