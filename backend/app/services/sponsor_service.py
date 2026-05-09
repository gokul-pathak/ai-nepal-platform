from sqlalchemy.orm import Session

from app.models.sponsor_lead import SponsorLead
from app.models.sponsor_package import SponsorPackage
from app.repositories.sponsor_repository import SponsorRepository
from app.schemas.sponsor import SponsorLeadCreateRequest


class SponsorService:
    def __init__(self, db: Session) -> None:
        self.repository = SponsorRepository(db)

    def get_active_packages(self) -> list[SponsorPackage]:
        return self.repository.list_active_packages()

    def create_lead(self, payload: SponsorLeadCreateRequest) -> SponsorLead:
        lead = SponsorLead(
            organization_name=payload.organization_name.strip(),
            contact_name=payload.contact_name.strip(),
            email=payload.email,
            phone=payload.phone,
            sponsor_type=payload.sponsor_type,
            budget_range=payload.budget_range,
            target_group=payload.target_group,
            message=payload.message,
            status="new",
        )
        return self.repository.create_lead(lead)
