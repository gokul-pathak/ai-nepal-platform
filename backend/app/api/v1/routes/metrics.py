from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.metrics import AdminMetricsResponse, PublicMetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/public", response_model=PublicMetricsResponse)
def get_public_metrics(db: Session = Depends(get_db)) -> PublicMetricsResponse:
    service = MetricsService(db)
    return service.get_public_metrics()


@admin_router.get("/metrics", response_model=AdminMetricsResponse)
def get_admin_metrics(
    db: Session = Depends(get_db),
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
) -> AdminMetricsResponse:
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin metrics not configured",
        )

    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin API key")

    service = MetricsService(db)
    return service.get_admin_metrics()
