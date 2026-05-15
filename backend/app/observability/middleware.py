import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request, Response

from app.observability.request_context import set_request_id


logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"
SLOW_REQUEST_THRESHOLD_MS = 1000.0


async def observability_middleware(request: Request, call_next) -> Response:
    request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
    set_request_id(request_id)
    request.state.request_id = request_id

    start_time = perf_counter()
    response: Response | None = None
    error_type: str | None = None

    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        error_type = exc.__class__.__name__
        raise
    finally:
        duration_ms = round((perf_counter() - start_time) * 1000, 3)
        status_code = response.status_code if response is not None else 500

        if response is not None:
            response.headers[REQUEST_ID_HEADER] = request_id

        logger.info(
            "API request completed",
            extra={
                "event": "api_request",
                "route": request.url.path,
                "method": request.method,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "error_type": error_type,
            },
        )

        if duration_ms >= SLOW_REQUEST_THRESHOLD_MS:
            logger.warning(
                "Slow API request detected",
                extra={
                    "event": "slow_request",
                    "route": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )
