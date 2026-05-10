import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

logger = logging.getLogger(__name__)


def _resolve_cors_origins() -> list[str]:
    raw = settings.backend_cors_origins or settings.allowed_origins
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]

    if settings.environment.lower() == "production" and "*" in origins:
        raise RuntimeError("Wildcard CORS origin is not allowed in production")

    return origins

origins = _resolve_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled API error", extra={"error_type": exc.__class__.__name__})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
