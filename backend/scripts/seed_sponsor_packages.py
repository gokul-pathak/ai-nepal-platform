from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.sponsor_package import SponsorPackage

SEED_PACKAGES = [
    {
        "name": "Bronze",
        "slug": "bronze",
        "monthly_request_limit": 5000,
        "price_label": "Starter sponsorship",
        "description": "Sponsor basic user AI credits for local communities.",
    },
    {
        "name": "Silver",
        "slug": "silver",
        "monthly_request_limit": 25000,
        "price_label": "Institution sponsorship",
        "description": "Sponsor school or district-level access to AI tools.",
    },
    {
        "name": "Gold",
        "slug": "gold",
        "monthly_request_limit": 100000,
        "price_label": "Community sponsorship",
        "description": "Sponsor larger community programs with scaled monthly access.",
    },
]


def main() -> None:
    with SessionLocal() as db:
        for package_data in SEED_PACKAGES:
            existing = db.scalar(select(SponsorPackage).where(SponsorPackage.slug == package_data["slug"]))
            if existing:
                continue

            db.add(
                SponsorPackage(
                    name=package_data["name"],
                    slug=package_data["slug"],
                    monthly_request_limit=package_data["monthly_request_limit"],
                    price_label=package_data["price_label"],
                    description=package_data["description"],
                    is_active=True,
                )
            )

        db.commit()


if __name__ == "__main__":
    main()
