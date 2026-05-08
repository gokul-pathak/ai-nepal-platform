import os
import tempfile

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models.tool import Tool


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


def test_tools_endpoint_returns_only_active_tools() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            db.add(Tool(slug="translator", name="Translator", is_active=True))
            db.add(Tool(slug="inactive-tool", name="Inactive Tool", is_active=False))
            db.commit()

        response = client.get("/api/v1/tools")

        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 1
        assert payload[0]["slug"] == "translator"
        assert payload[0]["is_active"] is True
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)
