from sqlalchemy.orm import Session

from app.models.tool import Tool
from app.repositories.tool_repository import ToolRepository


class ToolService:
    def __init__(self, db: Session) -> None:
        self.repository = ToolRepository(db)

    def list_active_tools(self) -> list[Tool]:
        return self.repository.list_active()
