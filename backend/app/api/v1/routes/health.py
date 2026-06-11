from fastapi import APIRouter

from app.core.config import settings
from app.observability.monitoring import check_database_connectivity, check_provider_availability, get_uptime_snapshot

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, object]:
    database = check_database_connectivity()
    provider = check_provider_availability()

    checks = {
        "database": database,
        "ai_provider": provider,
    }
    overall_status = "ok" if all(item.get("status") == "ok" for item in checks.values()) else "degraded"

    return {
        "status": overall_status,
        "service": settings.app_name,
        "environment": {
            "name": settings.environment,
            "api_prefix": settings.api_v1_prefix,
        },
        "checks": checks,
        "uptime": get_uptime_snapshot(),
    }
