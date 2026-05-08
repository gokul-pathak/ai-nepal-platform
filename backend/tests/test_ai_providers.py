from app.core.config import Settings
from app.services.ai import provider_factory


def test_settings_load_openai_env(monkeypatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")
    cfg = Settings()
    assert cfg.ai_provider == "openai"
    assert cfg.openai_api_key == "test-openai-key"
    assert cfg.openai_model == "gpt-4.1-mini"


def test_settings_load_gemini_env(monkeypatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-1.5-flash")
    cfg = Settings()
    assert cfg.ai_provider == "gemini"
    assert cfg.gemini_api_key == "test-gemini-key"
    assert cfg.gemini_model == "gemini-1.5-flash"


def test_provider_factory_selects_openai(monkeypatch) -> None:
    monkeypatch.setattr(provider_factory.settings, "ai_provider", "openai")

    class DummyOpenAI:
        pass

    monkeypatch.setattr(provider_factory, "OpenAIProvider", DummyOpenAI)
    provider = provider_factory.get_provider()
    assert isinstance(provider, DummyOpenAI)


def test_provider_factory_selects_gemini(monkeypatch) -> None:
    monkeypatch.setattr(provider_factory.settings, "ai_provider", "gemini")

    class DummyGemini:
        pass

    monkeypatch.setattr(provider_factory, "GeminiProvider", DummyGemini)
    provider = provider_factory.get_provider()
    assert isinstance(provider, DummyGemini)
