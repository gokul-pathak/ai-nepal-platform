from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.dependencies import check_rate_limit
from app.schemas.tool import ToolResponse, ToolRunRequest, ToolRunResponse, ToolRunUsageResponse
from app.services.tool_runner import ToolRunnerService
from app.services.tool_service import ToolService

router = APIRouter(tags=["tools"])


@router.get("/tools", response_model=list[ToolResponse])
def list_tools(db: Session = Depends(get_db)) -> list[ToolResponse]:
    service = ToolService(db)
    return [ToolResponse.model_validate(tool) for tool in service.list_active_tools()]


@router.post("/tools/{tool_slug}/run", response_model=ToolRunResponse)
def run_tool(
    tool_slug: str,
    payload: ToolRunRequest,
    x_session_id: str | None = Header(default=None, alias="X-Session-ID"),
    db: Session = Depends(get_db),
    _: None = Depends(check_rate_limit),
) -> ToolRunResponse:
    if not x_session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Session-ID header is required")

    runner = ToolRunnerService(db)
    result, remaining = runner.run(
        tool_slug=tool_slug,
        user_input=payload.input,
        language=payload.language,
        session_id=x_session_id,
    )

    return ToolRunResponse(
        tool=tool_slug,
        result=result,
        usage=ToolRunUsageResponse(remaining_daily_requests=remaining),
    )
