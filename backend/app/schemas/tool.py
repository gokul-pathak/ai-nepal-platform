import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
