import logging

import google.genai as genai

from app.core.config import settings
from app.services.ai.base import AIProvider


logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        if not settings.gemini_model.strip():
            raise RuntimeError("GEMINI_MODEL is not configured")
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def generate_text(self, prompt: str, user_input: str = "") -> str:
        full_prompt = f"{prompt}\n\nUser input:\n{user_input}" if user_input else prompt
        try:
            response = self.client.models.generate_content(model=settings.gemini_model, contents=full_prompt)
            return (response.text or "").strip()
        except Exception as exc:
            logger.error(
                "AI provider request failed",
                extra={"provider": "gemini", "error_type": exc.__class__.__name__},
            )
            raise
