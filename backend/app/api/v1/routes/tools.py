from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.tool import ToolResponse
from app.services.tool_service import ToolService

router = APIRouter(tags=["tools"])


@router.get("/tools", response_model=list[ToolResponse])
def list_tools(db: Session = Depends(get_db)) -> list[ToolResponse]:
    service = ToolService(db)
    return service.list_active_tools()
