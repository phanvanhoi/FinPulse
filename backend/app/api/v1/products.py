from fastapi import APIRouter

from app.dependencies import DB
from app.schemas.product import ProductListResponse, ProductResponse
from app.services import catalog_service

router = APIRouter()


@router.get("", response_model=ProductListResponse)
async def list_products(db: DB):
    products = await catalog_service.list_catalog(db)
    return ProductListResponse(products=[ProductResponse.model_validate(p) for p in products])
