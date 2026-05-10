from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_admin_api_key
from app.core.database import get_db
from app.schemas.metrics import AdminMetricsResponse, PublicMetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/public", response_model=PublicMetricsResponse)
def get_public_metrics(db: Session = Depends(get_db)) -> PublicMetricsResponse:
    service = MetricsService(db)
    return service.get_public_metrics()


@admin_router.get("/metrics", response_model=AdminMetricsResponse, dependencies=[Depends(require_admin_api_key)])
def get_admin_metrics(
    db: Session = Depends(get_db),
) -> AdminMetricsResponse:
    service = MetricsService(db)
    return service.get_admin_metrics()
