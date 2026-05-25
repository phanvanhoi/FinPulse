"""Initialize production database on first deploy.

Fresh VPS databases have no tables. Alembic migrations only cover stores/commerce
add-ons and assume base tables already exist (created via create_all in dev).
This script creates all tables on first run, then stamps Alembic to head.
"""

import asyncio
import sys
import traceback
from pathlib import Path

# `python scripts/init_db.py` puts scripts/ on sys.path — add project root for `app` imports
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.core.database import async_session_factory
from app.core.sync_database import sync_engine
from app.models import Base
from app.services.catalog_service import seed_catalog


def _existing_tables() -> set[str]:
    inspector = inspect(sync_engine)
    return set(inspector.get_table_names())


def _run_migrations() -> None:
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")


def _create_all_and_stamp() -> None:
    print("Fresh database detected — creating schema from models...")
    Base.metadata.create_all(sync_engine)
    cfg = Config("alembic.ini")
    command.stamp(cfg, "head")
    print("Schema created and Alembic stamped to head.")


async def _seed_catalog() -> None:
    async with async_session_factory() as session:
        await seed_catalog(session)
        await session.commit()


def main() -> None:
    try:
        tables = _existing_tables()
        print(f"Found {len(tables)} existing table(s).")

        if "organizations" not in tables:
            _create_all_and_stamp()
        else:
            print("Existing database — applying Alembic migrations...")
            _run_migrations()

        print("Seeding product catalog...")
        asyncio.run(_seed_catalog())
        print("Database ready.")
    except Exception:
        print("FATAL: Database initialization failed:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
