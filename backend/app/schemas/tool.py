import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic import Field


class ToolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    description: str | None
    category: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ToolRunRequest(BaseModel):
    input: str = Field(min_length=1, max_length=4000)
    language: str = Field(default="en", min_length=2, max_length=8)


class ToolRunUsageResponse(BaseModel):
    remaining_daily_requests: int


class ToolRunResponse(BaseModel):
    tool: str
    result: str
    usage: ToolRunUsageResponse
