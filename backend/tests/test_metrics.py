import os
import tempfile
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models.sponsor_lead import SponsorLead
from app.models.tool import Tool
from app.models.tool_usage import ToolUsage


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


def test_public_metrics_response() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            tool = Tool(slug="translator", name="Translator", is_active=True)
            db.add(tool)
            db.commit()
            db.refresh(tool)

            db.add(ToolUsage(id=uuid.uuid4(), tool_id=tool.id, session_id="a", language="en", status="success"))
            db.add(ToolUsage(id=uuid.uuid4(), tool_id=tool.id, session_id="b", language="en", status="success"))
            db.add(SponsorLead(organization_name="Org", contact_name="Lead", email="lead@example.com"))
            db.commit()

        response = client.get("/api/v1/metrics/public")
        assert response.status_code == 200
        payload = response.json()
        assert payload["total_requests"] == 2
        assert payload["total_users_helped"] == 2
        assert payload["total_sponsor_leads"] == 1
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_admin_metrics_response() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            t1 = Tool(slug="translator", name="Translator", is_active=True)
            t2 = Tool(slug="form-helper", name="Form Helper", is_active=True)
            db.add_all([t1, t2])
            db.commit()
            db.refresh(t1)
            db.refresh(t2)

            db.add(ToolUsage(id=uuid.uuid4(), tool_id=t1.id, session_id="u1", language="en", status="success"))
            db.add(ToolUsage(id=uuid.uuid4(), tool_id=t1.id, session_id="u2", language="ne", status="success"))
            db.add(ToolUsage(id=uuid.uuid4(), tool_id=t2.id, session_id="u2", language="en", status="failed"))
            db.add(SponsorLead(organization_name="Org", contact_name="Lead", email="lead@example.com"))
            db.commit()

        test_key = f"test-{uuid.uuid4()}"
        settings.admin_api_key = test_key
        response = client.get("/api/v1/admin/metrics", headers={"X-Admin-API-Key": test_key})
        assert response.status_code == 200
        payload = response.json()
        assert payload["total_tool_usage_count"] == 3
        assert payload["total_users_helped"] == 2
        assert payload["sponsor_lead_count"] == 1
        assert len(payload["usage_count_by_tool"]) >= 2
        assert len(payload["latest_sponsor_leads"]) == 1
        assert len(payload["latest_tool_usage_records"]) == 3
        assert "email" not in payload["latest_sponsor_leads"][0]
        assert "session_id" not in payload["latest_tool_usage_records"][0]
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_admin_metrics_requires_api_key() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        settings.admin_api_key = f"test-{uuid.uuid4()}"
        response = client.get("/api/v1/admin/metrics")
        assert response.status_code == 401
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)
