#!/bin/bash
set -e

BACKEND_PORT=4001
FRONTEND_PORT=4000
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Kill processes on ports 4001 and 4000
echo "Bajando procesos en puertos $BACKEND_PORT y $FRONTEND_PORT..."

for PORT in $BACKEND_PORT $FRONTEND_PORT; do
  PID=$(lsof -ti tcp:$PORT 2>/dev/null) || true
  if [ -n "$PID" ]; then
    kill -9 $PID 2>/dev/null && echo "  ✓ Puerto $PORT liberado (PID $PID)"
  else
    echo "  · Puerto $PORT ya libre"
  fi
done

sleep 1

# Backend
echo ""
echo "Levantando backend (puerto $BACKEND_PORT)..."
cd "$ROOT_DIR/backend"

if [ ! -d "venv" ]; then
  echo "  Creando virtualenv con Python 3.11..."
  python3.11 -m venv venv
fi

source venv/bin/activate

pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "  ⚠ Se copió .env.example a .env — editalo si es necesario"
fi

mkdir -p "$ROOT_DIR/logs"
nohup python main.py > "$ROOT_DIR/logs/backend.log" 2>&1 &
echo "  ✓ Backend PID: $!"

# Frontend
echo ""
echo "Levantando frontend (puerto $FRONTEND_PORT)..."
cd "$ROOT_DIR/frontend"

if [ ! -d "node_modules" ]; then
  echo "  Instalando dependencias npm..."
  npm install --silent
fi

nohup npm run dev > "$ROOT_DIR/logs/frontend.log" 2>&1 &
echo "  ✓ Frontend PID: $!"

echo ""
echo "Servidores levantados:"
echo "  Backend  → http://localhost:$BACKEND_PORT"
echo "  Frontend → http://localhost:$FRONTEND_PORT"
echo ""
echo "Logs:"
echo "  tail -f $ROOT_DIR/logs/backend.log"
echo "  tail -f $ROOT_DIR/logs/frontend.log"
