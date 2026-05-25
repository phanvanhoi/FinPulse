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
