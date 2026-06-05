#!/bin/bash
set -e

BACKEND_PORT=4001
FRONTEND_PORT=4000

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
cd "$(dirname "$0")/backend"

if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
  echo "  Creando virtualenv..."
  python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null

pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "  ⚠ Se copió .env.example a .env — editalo si es necesario"
fi

nohup python main.py > ../logs/backend.log 2>&1 &
echo "  ✓ Backend PID: $!"

# Frontend
echo ""
echo "Levantando frontend (puerto $FRONTEND_PORT)..."
cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
  echo "  Instalando dependencias npm..."
  npm install --silent
fi

mkdir -p "$(dirname "$0")/logs"
nohup npm run dev > ../logs/frontend.log 2>&1 &
echo "  ✓ Frontend PID: $!"

echo ""
echo "Servidores levantados:"
echo "  Backend  → http://localhost:$BACKEND_PORT"
echo "  Frontend → http://localhost:$FRONTEND_PORT"
echo ""
echo "Logs:"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
