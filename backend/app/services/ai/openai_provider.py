import logging

from openai import OpenAI

from app.core.config import settings
from app.services.ai.base import AIProvider


logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        if not settings.openai_model.strip():
            raise RuntimeError("OPENAI_MODEL is not configured")
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_text(self, prompt: str, user_input: str = "") -> str:
        try:
            response = self.client.responses.create(
                model=settings.openai_model,
                input=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_input},
                ],
            )
            return response.output_text.strip()
        except Exception as exc:
            logger.error(
                "AI provider request failed",
                extra={"provider": "openai", "error_type": exc.__class__.__name__},
            )
            raise
