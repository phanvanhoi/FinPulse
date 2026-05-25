from fastapi import APIRouter
from sqlalchemy import select

from app.dependencies import DB, CurrentUser
from app.models.connection import Connection
from app.schemas.connection import ConnectionListResponse, ConnectionResponse

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


@router.delete("/{connection_id}")
async def delete_connection(connection_id: str, current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(Connection).where(
            Connection.id == connection_id,
            Connection.organization_id == current_user.organization_id,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Connection not found")

    await db.delete(connection)
    return {"status": "deleted"}
