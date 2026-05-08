import logging

from app.core.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.openai_provider import OpenAIProvider


logger = logging.getLogger(__name__)


def get_provider() -> AIProvider:
    provider = settings.ai_provider.lower().strip()
    logger.info("Selecting AI provider", extra={"provider": provider})
    if provider == "gemini":
        return GeminiProvider()
    if provider == "openai":
        return OpenAIProvider()
    if provider in {"claude", "local"}:
        raise NotImplementedError(f"Provider '{provider}' is not implemented yet")
    raise ValueError(f"Unsupported AI provider '{provider}'")
