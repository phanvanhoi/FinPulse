#!/bin/sh
set -e

export PYTHONPATH=/app

echo "==> Waiting for database..."
python - <<'PY'
import sys
import time
from sqlalchemy import create_engine, text
from app.config import settings

url = settings.DATABASE_URL_SYNC
# Log host only (never print password)
host = url.split("@")[-1] if "@" in url else url
print(f"Connecting to: {host}")

for attempt in range(1, 31):
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection OK.")
        sys.exit(0)
    except Exception as exc:
        print(f"Attempt {attempt}/30 failed: {exc}")
        time.sleep(2)

print("ERROR: Could not connect to database after 60s.")
print("Check DATABASE_URL / DATABASE_URL_SYNC in .env — password special chars must be URL-encoded (e.g. ! -> %21)")
sys.exit(1)
PY

echo "==> Initializing database..."
python scripts/init_db.py || {
  echo "ERROR: init_db.py failed — see traceback above"
  exit 1
}

echo "==> Starting API server (workers=${UVICORN_WORKERS:-1})..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers "${UVICORN_WORKERS:-1}"
