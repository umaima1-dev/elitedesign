#!/usr/bin/env bash
# bash run.sh        -> the app on http://localhost:8000 (web page + API from one server)
# bash run.sh next   -> also starts the optional Next.js UI on http://localhost:3000
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d backend/.venv ]; then
  python3 -m venv backend/.venv
  backend/.venv/bin/pip install -q -r backend/requirements.txt
fi

trap 'kill 0' EXIT
(cd backend && .venv/bin/uvicorn app.main:app --port 8000) &
echo "SketchForge: http://localhost:8000   (API docs: http://localhost:8000/docs)"

if [ "${1:-}" = "next" ]; then
  [ -d frontend/node_modules ] || (cd frontend && npm install --no-audit --no-fund)
  (cd frontend && npm run dev) &
  echo "Next.js UI:  http://localhost:3000"
fi
wait
