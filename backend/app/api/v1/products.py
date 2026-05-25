from fastapi import APIRouter, Query

from app.dependencies import DB
from app.schemas.product import ProductListResponse, ProductResponse
from app.services import catalog_service

router = APIRouter()


@router.get("", response_model=ProductListResponse)
async def list_products(
    db: DB,
    fulfillment_provider: str | None = Query(default=None),
):
    products = await catalog_service.list_catalog(db, fulfillment_provider=fulfillment_provider)
    return ProductListResponse(products=[ProductResponse.model_validate(p) for p in products])
