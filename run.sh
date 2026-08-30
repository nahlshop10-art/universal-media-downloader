#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "=========================================================="
echo " Starting Universal Social Media Downloader Full Stack..."
echo "=========================================================="

# 1. Start Backend
echo "-> Starting FastAPI Backend on http://localhost:8000 ..."
cd "$DIR/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 2. Start Frontend
echo "-> Starting Next.js Frontend on http://localhost:3000 ..."
cd "$DIR/frontend"
node ./node_modules/next/dist/bin/next start -p 3000 &
FRONTEND_PID=$!

echo "=========================================================="
echo "  🚀 App running!"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "=========================================================="

cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
}
trap cleanup EXIT INT TERM

wait
