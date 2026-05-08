import os
import tempfile
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.main import app
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


def test_run_tool_success(monkeypatch) -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    class DummyProvider:
        def generate_text(self, system_prompt: str, user_input: str) -> str:
            return f"AI: {user_input}"

    monkeypatch.setattr("app.services.tool_runner.get_provider", lambda: DummyProvider())

    try:
        with testing_session_local() as db:
            db.add(Tool(slug="translator", name="Translator", is_active=True))
            db.commit()

        response = client.post(
            "/api/v1/tools/translator/run",
            headers={"X-Session-ID": "session-1"},
            json={"input": "Translate this", "language": "en"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["tool"] == "translator"
        assert payload["result"] == "AI: Translate this"
        assert payload["usage"]["remaining_daily_requests"] == 4

        with testing_session_local() as db:
            count = db.query(ToolUsage).count()
            assert count == 1
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_run_tool_invalid_slug() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/tools/unknown-tool/run",
            headers={"X-Session-ID": "session-2"},
            json={"input": "Hello", "language": "en"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Tool not found"
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_run_tool_usage_limit_exceeded() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            tool = Tool(slug="translator", name="Translator", is_active=True)
            db.add(tool)
            db.commit()
            db.refresh(tool)

            for _ in range(5):
                db.add(
                    ToolUsage(
                        id=uuid.uuid4(),
                        tool_id=tool.id,
                        session_id="session-limit",
                        language="en",
                        status="success",
                    )
                )
            db.commit()

        response = client.post(
            "/api/v1/tools/translator/run",
            headers={"X-Session-ID": "session-limit"},
            json={"input": "Hello", "language": "en"},
        )
        assert response.status_code == 429
        assert response.json()["detail"] == "Daily free usage limit reached"
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_run_tool_empty_input() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            db.add(Tool(slug="translator", name="Translator", is_active=True))
            db.commit()

        response = client.post(
            "/api/v1/tools/translator/run",
            headers={"X-Session-ID": "session-3"},
            json={"input": "", "language": "en"},
        )
        assert response.status_code == 422
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_run_tool_inactive() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            db.add(Tool(slug="translator", name="Translator", is_active=False))
            db.commit()

        response = client.post(
            "/api/v1/tools/translator/run",
            headers={"X-Session-ID": "session-4"},
            json={"input": "Hello", "language": "en"},
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Tool is inactive"
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_run_tool_provider_failure_returns_safe_502(monkeypatch) -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    class FailingProvider:
        def generate_text(self, prompt: str, user_input: str = "") -> str:
            raise RuntimeError("upstream timeout")

    monkeypatch.setattr("app.services.tool_runner.get_provider", lambda: FailingProvider())

    try:
        with testing_session_local() as db:
            db.add(Tool(slug="translator", name="Translator", is_active=True))
            db.commit()

        response = client.post(
            "/api/v1/tools/translator/run",
            headers={"X-Session-ID": "session-5"},
            json={"input": "Translate this", "language": "en"},
        )
        assert response.status_code == 502
        assert response.json()["detail"] == "AI provider request failed"
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)
