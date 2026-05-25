import uuid
from datetime import datetime

from pydantic import BaseModel


class ConnectionResponse(BaseModel):
    id: uuid.UUID
    provider: str
    status: str
    last_synced_at: datetime | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}


class ConnectionListResponse(BaseModel):
    connections: list[ConnectionResponse]


class InitiateConnectionRequest(BaseModel):
    provider: str


class ConnectionCallbackRequest(BaseModel):
    provider: str
    code: str
    state: str | None = None


class BurgerPrintsConnectRequest(BaseModel):
    api_key: str


class BurgerPrintsConnectionStatus(BaseModel):
    connected: bool
    connection_id: uuid.UUID | None = None
    status: str | None = None
    last_synced_at: datetime | None = None
    error_message: str | None = None
