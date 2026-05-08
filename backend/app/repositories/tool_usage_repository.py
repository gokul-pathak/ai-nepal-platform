from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.tool_usage import ToolUsage


class ToolUsageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, usage: ToolUsage) -> ToolUsage:
        self.db.add(usage)
        self.db.commit()
        self.db.refresh(usage)
        return usage

    def count_daily_by_session(self, session_id: str) -> int:
        stmt = select(func.count()).select_from(ToolUsage).where(
            ToolUsage.session_id == session_id,
            func.date(ToolUsage.created_at) == func.current_date(),
        )
        return int(self.db.scalar(stmt) or 0)
