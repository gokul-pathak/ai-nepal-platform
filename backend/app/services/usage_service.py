import uuid

from sqlalchemy.orm import Session

from app.models.tool import Tool
from app.models.tool_usage import ToolUsage
from app.repositories.tool_usage_repository import ToolUsageRepository

DAILY_FREE_REQUEST_LIMIT = 5


class UsageService:
    def __init__(self, db: Session) -> None:
        self.repository = ToolUsageRepository(db)

    def ensure_within_limit(self, session_id: str) -> int:
        used_today = self.repository.count_daily_by_session(session_id=session_id)
        remaining = DAILY_FREE_REQUEST_LIMIT - used_today
        if remaining <= 0:
            return 0
        return remaining

    def track(self, tool: Tool, session_id: str, language: str, status: str) -> ToolUsage:
        usage = ToolUsage(
            id=uuid.uuid4(),
            tool_id=tool.id,
            session_id=session_id,
            language=language,
            status=status,
        )
        return self.repository.create(usage)
