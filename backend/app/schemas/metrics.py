from datetime import datetime

from pydantic import BaseModel


class ToolUsageByTool(BaseModel):
    tool_slug: str
    count: int


class LatestSponsorLead(BaseModel):
    organization_name: str
    contact_name: str
    status: str
    created_at: datetime


class LatestToolUsage(BaseModel):
    tool_slug: str
    language: str | None
    status: str
    created_at: datetime


class AdminMetricsResponse(BaseModel):
    total_tool_usage_count: int
    total_users_helped: int
    usage_count_by_tool: list[ToolUsageByTool]
    sponsor_lead_count: int
    latest_sponsor_leads: list[LatestSponsorLead]
    latest_tool_usage_records: list[LatestToolUsage]


class PublicMetricsResponse(BaseModel):
    total_requests: int
    total_users_helped: int
    total_sponsor_leads: int
