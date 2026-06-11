from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ai-nepal-platform-backend"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ai_nepal_platform"
    ai_provider: str = "gemini"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    backend_cors_origins: str = ""
    allowed_origins: str = ""
    admin_api_key: str = ""
    
    # Rate limiting configuration (public API abuse prevention)
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 20  # Max requests per window
    rate_limit_window_seconds: int = 60  # Time window in seconds

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
