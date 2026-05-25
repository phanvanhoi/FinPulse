#!/usr/bin/env bash
# Collect backend diagnostics on VPS when container is unhealthy
set -euo pipefail

COMPOSE="docker compose -f docker-compose.prod.yml --env-file .env"

echo "=== Container status ==="
$COMPOSE ps -a

echo ""
echo "=== Backend logs (last 150 lines) ==="
$COMPOSE logs backend --tail=150

echo ""
echo "=== Backend healthcheck ==="
docker inspect finpulse-backend-1 --format='{{json .State.Health}}' 2>/dev/null || \
  docker inspect "$(docker ps -aq -f name=backend | head -1)" --format='{{json .State.Health}}' 2>/dev/null || \
  echo "Could not inspect backend container"

echo ""
echo "=== DATABASE_URL in .env (password masked) ==="
grep -E '^(DATABASE_URL|POSTGRES_)' .env | sed 's/:[^:@]*@/:***@/'

echo ""
echo "=== Manual init_db test (optional) ==="
echo "Run: $COMPOSE run --rm --entrypoint sh backend -c 'python scripts/init_db.py'"
