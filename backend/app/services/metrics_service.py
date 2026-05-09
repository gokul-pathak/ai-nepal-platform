from sqlalchemy.orm import Session

from app.repositories.metrics_repository import MetricsRepository
from app.schemas.metrics import (
    AdminMetricsResponse,
    LatestSponsorLead,
    LatestToolUsage,
    PublicMetricsResponse,
    ToolUsageByTool,
)


class MetricsService:
    def __init__(self, db: Session) -> None:
        self.repository = MetricsRepository(db)

    def get_admin_metrics(self) -> AdminMetricsResponse:
        usage_by_tool = [
            ToolUsageByTool(tool_slug=row.tool_slug, count=row.count)
            for row in self.repository.usage_count_by_tool()
        ]
        latest_leads = [
            LatestSponsorLead(
                organization_name=row.organization_name,
                contact_name=row.contact_name,
                status=row.status,
                created_at=row.created_at,
            )
            for row in self.repository.latest_sponsor_leads()
        ]
        latest_usage = [
            LatestToolUsage(
                tool_slug=row.tool_slug,
                language=row.language,
                status=row.status,
                created_at=row.created_at,
            )
            for row in self.repository.latest_tool_usage()
        ]

        return AdminMetricsResponse(
            total_tool_usage_count=self.repository.total_tool_usage_count(),
            total_users_helped=self.repository.distinct_users_helped_count(),
            usage_count_by_tool=usage_by_tool,
            sponsor_lead_count=self.repository.sponsor_lead_count(),
            latest_sponsor_leads=latest_leads,
            latest_tool_usage_records=latest_usage,
        )

    def get_public_metrics(self) -> PublicMetricsResponse:
        return PublicMetricsResponse(
            total_requests=self.repository.total_tool_usage_count(),
            total_users_helped=self.repository.distinct_users_helped_count(),
            total_sponsor_leads=self.repository.sponsor_lead_count(),
        )
