from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tool import Tool


class ToolRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(self) -> list[Tool]:
        stmt = select(Tool).where(Tool.is_active.is_(True)).order_by(Tool.created_at.asc())
        return list(self.db.scalars(stmt).all())
