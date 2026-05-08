from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.tool import Tool

SEED_TOOLS = [
    {"slug": "translator", "name": "Translator", "category": "language"},
    {"slug": "letter-writer", "name": "Letter Writer", "category": "writing"},
    {"slug": "form-helper", "name": "Form Helper", "category": "productivity"},
    {"slug": "agriculture-helper", "name": "Agriculture Helper", "category": "agriculture"},
    {"slug": "legal-basic-helper", "name": "Legal Basic Helper", "category": "legal"},
]


def main() -> None:
    with SessionLocal() as db:
        for tool_data in SEED_TOOLS:
            existing = db.scalar(select(Tool).where(Tool.slug == tool_data["slug"]))
            if existing:
                continue

            db.add(
                Tool(
                    slug=tool_data["slug"],
                    name=tool_data["name"],
                    category=tool_data["category"],
                    description=f"Placeholder description for {tool_data['name']}.",
                    is_active=True,
                )
            )

        db.commit()


if __name__ == "__main__":
    main()
