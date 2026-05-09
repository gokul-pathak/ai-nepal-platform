from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.sponsor import SponsorLeadCreateRequest, SponsorLeadCreateResponse, SponsorPackageResponse
from app.services.sponsor_service import SponsorService

router = APIRouter(prefix="/sponsors", tags=["sponsors"])


@router.get("/packages", response_model=list[SponsorPackageResponse])
def list_sponsor_packages(db: Session = Depends(get_db)) -> list[SponsorPackageResponse]:
    service = SponsorService(db)
    packages = service.get_active_packages()
    return [SponsorPackageResponse.model_validate(item) for item in packages]


@router.post("/leads", response_model=SponsorLeadCreateResponse, status_code=status.HTTP_201_CREATED)
def create_sponsor_lead(payload: SponsorLeadCreateRequest, db: Session = Depends(get_db)) -> SponsorLeadCreateResponse:
    service = SponsorService(db)
    lead = service.create_lead(payload)
    return SponsorLeadCreateResponse(id=lead.id, message="Sponsor interest submitted successfully")
