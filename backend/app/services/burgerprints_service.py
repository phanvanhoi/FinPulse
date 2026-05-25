import json
import uuid

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.encryption import decrypt, encrypt
from app.core.exceptions import BadRequestError, NotFoundError
from app.integrations.burgerprints.client import BurgerPrintsClient
from app.integrations.burgerprints.exceptions import BurgerPrintsAPIError, BurgerPrintsAuthError
from app.models.connection import Connection, ConnectionProvider, ConnectionStatus

PROVIDER = ConnectionProvider.BURGER_PRINTS


def _encode_credentials(api_key: str) -> str:
    return encrypt(api_key)


def decode_api_key(credentials_encrypted: str | None) -> str | None:
    if not credentials_encrypted:
        return None
    try:
        return decrypt(credentials_encrypted)
    except Exception:
        try:
            data = json.loads(credentials_encrypted)
            return data.get("api_key")
        except json.JSONDecodeError:
            return credentials_encrypted


async def get_burgerprints_connection(db: AsyncSession, organization_id: uuid.UUID) -> Connection | None:
    result = await db.execute(
        select(Connection).where(
            Connection.organization_id == organization_id,
            Connection.provider == PROVIDER,
        )
    )
    return result.scalar_one_or_none()


async def get_client_for_organization(db: AsyncSession, organization_id: uuid.UUID) -> BurgerPrintsClient:
    connection = await get_burgerprints_connection(db, organization_id)
    api_key = decode_api_key(connection.credentials_encrypted) if connection else None
    if not api_key and settings.APP_ENV == "development":
        api_key = settings.BURGERPRINTS_API_KEY
    if not api_key:
        raise BadRequestError("BurgerPrints is not connected. Add your API key in Settings → Connections.")
    return BurgerPrintsClient(api_key=api_key)


async def connect_burgerprints(
    db: AsyncSession,
    organization_id: uuid.UUID,
    api_key: str,
) -> Connection:
    api_key = api_key.strip()
    if not api_key:
        raise BadRequestError("API key is required")

    client = BurgerPrintsClient(api_key=api_key)
    try:
        await client.verify_api_key()
    except BurgerPrintsAuthError as exc:
        raise BadRequestError(str(exc)) from exc
    except (BurgerPrintsAPIError, httpx.HTTPError) as exc:
        raise BadRequestError(f"Could not verify BurgerPrints API key: {exc}") from exc

    connection = await get_burgerprints_connection(db, organization_id)
    if connection:
        connection.credentials_encrypted = _encode_credentials(api_key)
        connection.status = ConnectionStatus.ACTIVE
        connection.error_message = None
    else:
        connection = Connection(
            organization_id=organization_id,
            provider=PROVIDER,
            credentials_encrypted=_encode_credentials(api_key),
            status=ConnectionStatus.ACTIVE,
        )
        db.add(connection)

    await db.flush()
    return connection


async def disconnect_burgerprints(db: AsyncSession, organization_id: uuid.UUID) -> None:
    connection = await get_burgerprints_connection(db, organization_id)
    if not connection:
        raise NotFoundError("BurgerPrints connection not found")
    await db.delete(connection)
