from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.tool import Tool
from app.repositories.tool_repository import ToolRepository
from app.services.ai.provider_factory import get_provider
from app.services.ai.prompts import (
    agriculture_helper,
    form_helper,
    legal_basic_helper,
    letter_writer,
    translator,
)
from app.services.usage_service import DAILY_FREE_REQUEST_LIMIT, UsageService


PROMPT_BUILDERS = {
    "translator": translator.build_prompt,
    "letter-writer": letter_writer.build_prompt,
    "form-helper": form_helper.build_prompt,
    "agriculture-helper": agriculture_helper.build_prompt,
    "legal-basic-helper": legal_basic_helper.build_prompt,
}


class ToolRunnerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.tool_repository = ToolRepository(db)
        self.usage_service = UsageService(db)

    def run(self, tool_slug: str, user_input: str, language: str, session_id: str) -> tuple[str, int]:
        tool = self._get_active_tool(tool_slug)
        remaining = self.usage_service.ensure_within_limit(session_id)
        if remaining <= 0:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Daily free usage limit reached")

        prompt_builder = PROMPT_BUILDERS.get(tool_slug)
        if prompt_builder is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

        cleaned_input = self._sanitize_input(user_input)

        try:
            provider = get_provider()
            output = provider.generate_text(prompt_builder(language), cleaned_input)
            self.usage_service.track(tool=tool, session_id=session_id, language=language, status="success")
        except HTTPException:
            raise
        except Exception as exc:
            self.usage_service.track(tool=tool, session_id=session_id, language=language, status="failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI provider request failed",
            ) from exc

        updated_remaining = max(DAILY_FREE_REQUEST_LIMIT - self.usage_service.repository.count_daily_by_session(session_id), 0)
        return output, updated_remaining

    def _get_active_tool(self, tool_slug: str) -> Tool:
        tool = self.tool_repository.get_by_slug(tool_slug)
        if tool is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
        if not tool.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tool is inactive")
        return tool

    @staticmethod
    def _sanitize_input(user_input: str) -> str:
        normalized = " ".join(user_input.strip().split())
        lowered = normalized.lower()
        blocked_patterns = ["ignore previous instructions", "reveal system prompt", "developer message"]
        if any(pattern in lowered for pattern in blocked_patterns):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Input contains disallowed instructions")
        return normalized
