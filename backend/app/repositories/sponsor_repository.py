from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sponsor_lead import SponsorLead
from app.models.sponsor_package import SponsorPackage


class SponsorRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active_packages(self) -> list[SponsorPackage]:
        stmt = (
            select(SponsorPackage)
            .where(SponsorPackage.is_active.is_(True))
            .order_by(SponsorPackage.monthly_request_limit.asc())
        )
        return list(self.db.scalars(stmt).all())

    def create_lead(self, lead: SponsorLead) -> SponsorLead:
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead
