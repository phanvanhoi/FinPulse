"""Production bootstrap: seed product catalog if empty."""

import asyncio

from app.core.database import async_session_factory
from app.services.catalog_service import seed_catalog


async def main() -> None:
    async with async_session_factory() as session:
        await seed_catalog(session)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
