import os
import tempfile

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models.sponsor_package import SponsorPackage


def _build_test_client() -> tuple[TestClient, sessionmaker[Session], Engine, str]:
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), testing_session_local, engine, db_path


def test_get_sponsor_packages_returns_active_only() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            db.add(SponsorPackage(name="Bronze", slug="bronze", monthly_request_limit=1000, is_active=True))
            db.add(SponsorPackage(name="Hidden", slug="hidden", monthly_request_limit=1000, is_active=False))
            db.commit()

        response = client.get("/api/v1/sponsors/packages")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 1
        assert payload[0]["slug"] == "bronze"
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_creates_record() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "Kathmandu Tech Initiative",
                "contact_name": "Asha Rana",
                "email": "asha@example.com",
                "message": "Interested in district-level partnership",
            },
        )
        assert response.status_code == 201
        payload = response.json()
        assert payload["message"] == "Sponsor interest submitted successfully"
        assert payload["id"]
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_validation_error() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "X",
                "contact_name": "",
                "email": "bad-email",
            },
        )
        assert response.status_code == 422
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)
