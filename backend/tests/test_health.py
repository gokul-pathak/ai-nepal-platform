from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "ai-nepal-platform-backend"
    assert payload["status"] in {"ok", "degraded"}
    assert "checks" in payload
    assert "database" in payload["checks"]
    assert "ai_provider" in payload["checks"]
    assert "uptime" in payload
    assert "started_at" in payload["uptime"]
    assert "uptime_seconds" in payload["uptime"]
