#!/bin/sh
set -e

echo "==> Initializing database..."
python scripts/init_db.py

echo "==> Starting API server..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers "${UVICORN_WORKERS:-2}"
