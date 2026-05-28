#!/usr/bin/env python3
"""Create a seller account (organization + user + store). Public signup is disabled.

Usage (from backend directory, or via Docker):

  python scripts/create_seller.py \\
    --email seller@example.com \\
    --password 'YourSecurePass123' \\
    --name "Seller Name" \\
    --org "My Print Shop"

Docker (production):

  docker compose -f docker-compose.prod.yml exec backend \\
    python scripts/create_seller.py \\
    --email seller@example.com \\
    --password 'YourSecurePass123' \\
    --name "Seller Name" \\
    --org "My Print Shop"
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sqlalchemy import select

from app.config import settings
from app.core.database import async_session_factory
from app.core.exceptions import ConflictError
from app.models.store import Store
from app.services.auth_service import create_seller_account


async def _run(args: argparse.Namespace) -> int:
    async with async_session_factory() as session:
        try:
            user, org = await create_seller_account(
                session,
                email=args.email.strip().lower(),
                password=args.password,
                name=args.name.strip(),
                organization_name=args.org.strip(),
                create_store=not args.skip_store,
            )
            await session.commit()
        except ConflictError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        store_slug = None
        if not args.skip_store:
            store = (
                await session.execute(select(Store).where(Store.organization_id == org.id))
            ).scalar_one_or_none()
            store_slug = store.slug if store else None

    base = settings.FRONTEND_URL.rstrip("/")
    print("Seller account created successfully.")
    print(f"  User ID:         {user.id}")
    print(f"  Email:           {user.email}")
    print(f"  Organization:    {org.name} ({org.slug})")
    if store_slug:
        print(f"  Storefront:      {base}/store/{store_slug}")
    print(f"  Login:           {base}/login")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a FinPulse seller account")
    parser.add_argument("--email", required=True, help="Login email")
    parser.add_argument("--password", required=True, help="Login password (min 8 characters)")
    parser.add_argument("--name", required=True, help="Display name")
    parser.add_argument("--org", required=True, help="Organization / store brand name")
    parser.add_argument(
        "--skip-store",
        action="store_true",
        help="Only create user + org, skip storefront record",
    )
    args = parser.parse_args()

    if len(args.password) < 8:
        print("Error: password must be at least 8 characters", file=sys.stderr)
        sys.exit(1)

    sys.exit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
