from datetime import UTC, datetime
from time import monotonic

from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.services.ai.provider_factory import get_provider


APP_STARTED_AT = datetime.now(UTC)
APP_STARTED_MONOTONIC = monotonic()


def get_uptime_snapshot() -> dict[str, object]:
    uptime_seconds = max(monotonic() - APP_STARTED_MONOTONIC, 0.0)
    return {
        "started_at": APP_STARTED_AT.isoformat(),
        "uptime_seconds": round(uptime_seconds, 3),
    }


def check_database_connectivity() -> dict[str, object]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - defensive path
        return {"status": "error", "error_type": exc.__class__.__name__}


def check_provider_availability() -> dict[str, object]:
    provider = settings.ai_provider.lower().strip()
    try:
        _ = get_provider()
        return {"status": "ok", "provider": provider}
    except Exception as exc:
        return {
            "status": "error",
            "provider": provider,
            "error_type": exc.__class__.__name__,
        }
