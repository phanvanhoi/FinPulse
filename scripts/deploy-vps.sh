#!/usr/bin/env bash
# Deploy FinPulse platform on a VPS (Ubuntu/Debian)
# Usage: bash scripts/deploy-vps.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE="docker compose -f docker-compose.prod.yml --env-file .env"

echo "==> Checking .env file..."
if [ ! -f .env ]; then
  echo "ERROR: .env not found. Run: cp .env.production.example .env && nano .env"
  exit 1
fi

if grep -q "CHANGE_ME" .env; then
  echo "WARNING: .env still contains CHANGE_ME placeholders. Update secrets before going live."
fi

echo "==> Building and starting production stack..."
$COMPOSE up -d --build

echo "==> Waiting for backend health..."
sleep 10
$COMPOSE ps

echo ""
echo "Deploy complete!"
echo "  App URL: check FRONTEND_URL in your .env"
echo "  Health:  curl http://YOUR_DOMAIN/health"
echo ""
echo "Useful commands:"
echo "  Logs:     docker compose -f docker-compose.prod.yml logs -f"
echo "  Migrate:  docker compose -f docker-compose.prod.yml exec backend alembic upgrade head"
echo "  SSL:      bash scripts/setup-ssl.sh yourdomain.com admin@yourdomain.com"
