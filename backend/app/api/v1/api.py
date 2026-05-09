from fastapi import APIRouter

from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.metrics import admin_router as admin_metrics_router
from app.api.v1.routes.metrics import router as metrics_router
from app.api.v1.routes.sponsors import router as sponsors_router
from app.api.v1.routes.tools import router as tools_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(tools_router)
api_router.include_router(sponsors_router)
api_router.include_router(metrics_router)
api_router.include_router(admin_metrics_router)
