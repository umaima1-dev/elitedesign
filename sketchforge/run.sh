#!/usr/bin/env bash
# Starts the API (port 8000) and the web app (port 3000). Ctrl+C stops both.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d backend/.venv ]; then
  python3 -m venv backend/.venv
  backend/.venv/bin/pip install -q -r backend/requirements.txt
fi
[ -d frontend/node_modules ] || (cd frontend && npm install --no-audit --no-fund)

trap 'kill 0' EXIT
(cd backend && .venv/bin/uvicorn app.main:app --port 8000) &
(cd frontend && npm run dev) &
echo "SketchForge: http://localhost:3000   (API docs: http://localhost:8000/docs)"
wait
