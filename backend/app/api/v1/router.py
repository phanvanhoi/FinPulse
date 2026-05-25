from fastapi import APIRouter

from app.api.v1 import auth, campaigns, cart, connections, dashboard, insights, orders, payments, products, store

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(connections.router, prefix="/connections", tags=["Connections"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
api_router.include_router(store.router, prefix="/store", tags=["Store"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(cart.router, prefix="/cart", tags=["Cart"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
