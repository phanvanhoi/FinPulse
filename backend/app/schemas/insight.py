import uuid
from datetime import datetime

from pydantic import BaseModel


class InsightResponse(BaseModel):
    id: uuid.UUID
    insight_type: str
    category: str
    title: str
    body_markdown: str
    severity: str
    data_context: dict | None = None
    is_read: bool
    generated_at: datetime

    model_config = {"from_attributes": True}


class InsightListResponse(BaseModel):
    items: list[InsightResponse]
    total: int
    page: int
    page_size: int


class MarkInsightReadRequest(BaseModel):
    insight_ids: list[uuid.UUID]
