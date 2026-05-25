#!/usr/bin/env bash
# Obtain Let's Encrypt certificate and enable HTTPS nginx config.
# Usage: bash scripts/setup-ssl.sh yourdomain.com admin@yourdomain.com

set -euo pipefail

DOMAIN="${1:?Usage: setup-ssl.sh DOMAIN EMAIL}"
EMAIL="${2:?Usage: setup-ssl.sh DOMAIN EMAIL}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE="docker compose -f docker-compose.prod.yml --env-file .env"

echo "==> Requesting certificate for ${DOMAIN}..."
$COMPOSE --profile ssl run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email \
  -d "$DOMAIN"

SSL_CONF="infrastructure/nginx/conf.d/ssl.conf"
SSL_EXAMPLE="infrastructure/nginx/conf.d/ssl.conf.example"

if [ ! -f "$SSL_CONF" ]; then
  echo "==> Creating SSL nginx config..."
  sed "s/YOUR_DOMAIN/${DOMAIN}/g" "$SSL_EXAMPLE" > "$SSL_CONF"
  echo "Created ${SSL_CONF}"
fi

echo "==> Disabling HTTP-only default.conf (using ssl.conf)..."
mv infrastructure/nginx/conf.d/default.conf infrastructure/nginx/conf.d/default.conf.disabled 2>/dev/null || true

echo "==> Reloading nginx..."
$COMPOSE exec nginx nginx -s reload

echo "==> Starting certbot auto-renewal..."
$COMPOSE --profile ssl up -d certbot

echo ""
echo "SSL enabled for https://${DOMAIN}"
echo "Update .env URLs to https://${DOMAIN} and rebuild frontend:"
echo "  NEXT_PUBLIC_API_URL=https://${DOMAIN}"
echo "  FRONTEND_URL=https://${DOMAIN}"
echo "  BACKEND_URL=https://${DOMAIN}"
echo "  docker compose -f docker-compose.prod.yml up -d --build frontend"
