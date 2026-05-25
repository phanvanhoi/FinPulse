import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.core.exceptions import NotFoundError
from app.dependencies import DB, CurrentUser
from app.models.connection import Connection
from app.schemas.connection import (
    BurgerPrintsConnectRequest,
    BurgerPrintsConnectionStatus,
    ConnectionListResponse,
    ConnectionResponse,
)
from app.services import burgerprints_service

router = APIRouter()


@router.get("", response_model=ConnectionListResponse)
async def list_connections(current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(Connection).where(Connection.organization_id == current_user.organization_id)
    )
    connections = result.scalars().all()
    return ConnectionListResponse(
        connections=[ConnectionResponse.model_validate(c) for c in connections]
    )


@router.get("/burgerprints/status", response_model=BurgerPrintsConnectionStatus)
async def burgerprints_status(current_user: CurrentUser, db: DB):
    connection = await burgerprints_service.get_burgerprints_connection(db, current_user.organization_id)
    if not connection:
        return BurgerPrintsConnectionStatus(connected=False)
    return BurgerPrintsConnectionStatus(
        connected=connection.status.value == "active",
        connection_id=connection.id,
        status=connection.status.value,
        last_synced_at=connection.last_synced_at,
        error_message=connection.error_message,
    )


@router.post("/burgerprints", response_model=ConnectionResponse)
async def connect_burgerprints(
    payload: BurgerPrintsConnectRequest,
    current_user: CurrentUser,
    db: DB,
):
    connection = await burgerprints_service.connect_burgerprints(
        db,
        current_user.organization_id,
        payload.api_key,
    )
    return ConnectionResponse.model_validate(connection)


@router.delete("/burgerprints")
async def disconnect_burgerprints(current_user: CurrentUser, db: DB):
    await burgerprints_service.disconnect_burgerprints(db, current_user.organization_id)
    return {"status": "disconnected"}


@router.delete("/{connection_id}")
async def delete_connection(connection_id: uuid.UUID, current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(Connection).where(
            Connection.id == connection_id,
            Connection.organization_id == current_user.organization_id,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise NotFoundError("Connection not found")

    await db.delete(connection)
    return {"status": "deleted"}
