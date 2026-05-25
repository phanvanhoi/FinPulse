#!/usr/bin/env bash
# Fix backend restart loop on VPS (PYTHONPATH + rebuild)
set -euo pipefail

cd "$(dirname "$0")/.."
COMPOSE="docker compose -f docker-compose.prod.yml --env-file .env"

echo "==> Applying PYTHONPATH fixes..."

if ! grep -q 'ENV PYTHONPATH=/app' backend/Dockerfile.prod; then
  sed -i '/^WORKDIR \/app/a ENV PYTHONPATH=/app' backend/Dockerfile.prod
  echo "  Added ENV PYTHONPATH to Dockerfile.prod"
fi

if ! grep -q 'export PYTHONPATH=/app' backend/entrypoint.sh; then
  sed -i '/^set -e/a export PYTHONPATH=/app' backend/entrypoint.sh
  echo "  Added export PYTHONPATH to entrypoint.sh"
fi

if ! grep -q 'sys.path.insert' backend/scripts/init_db.py; then
  echo "  WARNING: init_db.py missing sys.path fix — run git pull for latest code"
fi

echo "==> Rebuilding backend (no cache)..."
$COMPOSE build --no-cache backend

echo "==> Starting stack..."
$COMPOSE up -d

echo "==> Backend logs (tail 40)..."
sleep 5
$COMPOSE logs backend --tail=40

echo ""
echo "==> Container status:"
$COMPOSE ps -a
