#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND="$ROOT/frontend"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required."
  exit 1
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY is not set."
  echo 'Run: export OPENAI_API_KEY="your-key"'
  exit 1
fi

if [ ! -d "$ROOT/.venv" ]; then
  if [ ! -x "$ROOT/backend/venv/bin/uvicorn" ]; then
    echo "Python environment not found. Run ./SETUP.sh first."
    exit 1
  fi
fi

cd "$FRONTEND"
if [ ! -d node_modules ]; then
  npm install
fi

cd "$ROOT/backend"
if [ -x "$ROOT/.venv/bin/uvicorn" ]; then
  "$ROOT/.venv/bin/uvicorn" api:app --reload --port 8000 &
else
  "$ROOT/backend/venv/bin/uvicorn" api:app --reload --port 8000 &
fi
BACKEND_PID=$!

cleanup() {
  kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cd "$FRONTEND"
npm run dev
