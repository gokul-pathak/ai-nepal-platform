import hmac

from fastapi import Header, HTTPException, status

from app.core.config import settings
from app.services.rate_limit_service import get_rate_limit_service


def require_admin_api_key(x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key")) -> None:
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API key is not configured",
        )

    if not x_admin_api_key or not hmac.compare_digest(x_admin_api_key, settings.admin_api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin API key")


def check_rate_limit(
    x_session_id: str | None = Header(default=None, alias="X-Session-ID"),
) -> None:
    """
    Rate limit dependency for public tool execution endpoints.
    
    Uses session ID as the rate limiting key. If rate limit is exceeded,
    returns HTTP 429 (Too Many Requests).
    
    Args:
        x_session_id: Session ID from header
    
    Raises:
        HTTPException: If session ID is missing or rate limit is exceeded
    """
    if not settings.rate_limit_enabled:
        return
    
    if not x_session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Session-ID header is required",
        )
    
    rate_limiter = get_rate_limit_service(
        requests_per_window=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )
    
    if not rate_limiter.is_allowed(x_session_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )
