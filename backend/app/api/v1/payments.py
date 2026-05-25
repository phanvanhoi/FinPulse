from fastapi import APIRouter

from app.services import checkout_service

router = APIRouter()


@router.get("/config")
async def get_payment_config():
    """Public config: which payment methods are enabled on this server."""
    return checkout_service.get_payment_config()
