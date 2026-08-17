from fastapi import APIRouter

from app.api.v1.endpoints import calculations, deals, health, integrations, n8n, parcels

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(deals.router, prefix="/deals", tags=["deals"])
api_router.include_router(calculations.router, prefix="/calculations", tags=["calculations"])
api_router.include_router(parcels.router, prefix="/parcels", tags=["parcels"])
api_router.include_router(n8n.router, prefix="/n8n", tags=["n8n"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
