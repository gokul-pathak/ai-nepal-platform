import json
import logging
from datetime import UTC, datetime

from app.observability.request_context import get_request_id


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": get_request_id() or None,
        }

        safe_fields = [
            "route",
            "method",
            "status_code",
            "duration_ms",
            "error_type",
            "provider",
            "event",
        ]
        for field in safe_fields:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        return json.dumps(payload, ensure_ascii=True)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)
