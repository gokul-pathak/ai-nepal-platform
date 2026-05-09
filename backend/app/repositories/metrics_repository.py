from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.sponsor_lead import SponsorLead
from app.models.tool import Tool
from app.models.tool_usage import ToolUsage


@dataclass
class ToolUsageByToolRow:
    tool_slug: str
    count: int


@dataclass
class LatestSponsorLeadRow:
    organization_name: str
    contact_name: str
    status: str
    created_at: datetime


@dataclass
class LatestToolUsageRow:
    tool_slug: str
    language: str | None
    status: str
    created_at: datetime


class MetricsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def total_tool_usage_count(self) -> int:
        stmt = select(func.count()).select_from(ToolUsage)
        return int(self.db.scalar(stmt) or 0)

    def usage_count_by_tool(self) -> list[ToolUsageByToolRow]:
        stmt = (
            select(Tool.slug, func.count(ToolUsage.id))
            .join(ToolUsage, ToolUsage.tool_id == Tool.id)
            .group_by(Tool.slug)
            .order_by(func.count(ToolUsage.id).desc())
        )
        rows = self.db.execute(stmt).all()
        return [ToolUsageByToolRow(tool_slug=row[0], count=int(row[1])) for row in rows]

    def sponsor_lead_count(self) -> int:
        stmt = select(func.count()).select_from(SponsorLead)
        return int(self.db.scalar(stmt) or 0)

    def latest_sponsor_leads(self, limit: int = 10) -> list[LatestSponsorLeadRow]:
        stmt = (
            select(
                SponsorLead.organization_name,
                SponsorLead.contact_name,
                SponsorLead.status,
                SponsorLead.created_at,
            )
            .order_by(SponsorLead.created_at.desc())
            .limit(limit)
        )
        rows = self.db.execute(stmt).all()
        return [
            LatestSponsorLeadRow(
                organization_name=row[0],
                contact_name=row[1],
                status=row[2],
                created_at=row[3],
            )
            for row in rows
        ]

    def latest_tool_usage(self, limit: int = 10) -> list[LatestToolUsageRow]:
        stmt = (
            select(Tool.slug, ToolUsage.language, ToolUsage.status, ToolUsage.created_at)
            .join(Tool, Tool.id == ToolUsage.tool_id)
            .order_by(ToolUsage.created_at.desc())
            .limit(limit)
        )
        rows = self.db.execute(stmt).all()
        return [
            LatestToolUsageRow(
                tool_slug=row[0],
                language=row[1],
                status=row[2],
                created_at=row[3],
            )
            for row in rows
        ]

    def distinct_users_helped_count(self) -> int:
        stmt = select(func.count(func.distinct(ToolUsage.session_id))).select_from(ToolUsage)
        return int(self.db.scalar(stmt) or 0)
