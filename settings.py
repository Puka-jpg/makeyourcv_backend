import os

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application settings
    ENV: str = "local"
    DEBUG: int = 0

    # Database settings
    DB_URL: str = "postgresql+asyncpg://postgres:password@localhost:5433/makeyourcv"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # JWT settings
    JWT_REFRESH_EXPIRATION_MINUTES: int = (
        15 * 24 * 60
    )  # 15 days: int = 15 * 24 * 60  # 15 days
    JWT_ACCESS_EXPIRATION_MINUTES: int = 30  # 15 minutes
    JWT_SECRET: str = "topsecretkey"

    # AI Settings
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""

    # AI models
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    GOOGLE_MODEL: str = "gemini-2.0-flash"
    OPENROUTER_MODEL: str = ""

    # Gunicorn settings
    GUNICORN_WORKERS: int = 4
    GUNICORN_THREADS: int = 1  # Uvicorn workers don't use Gunicorn threads
    GUNICORN_TIMEOUT: int = 300
    GUNICORN_ACCESS_LOG: str = "-"
    GUNICORN_ERROR_LOG: str = "-"

    # MCP Settings
    # MCP_MODE: "local" (stdio), "remote" (SSE), or "disabled"
    MCP_MODE: str = "local"
    RENDER_CV_MCP_URL: str = "http://localhost:9000/sse/"
    # Local MCP server settings (for stdio mode)
    RENDER_CV_MCP_COMMAND: str = "uv"
    RENDER_CV_MCP_ARGS: str = (
        "run,--frozen,--all-extras,python,rendercv/mcp/server.py,--stdio"
    )
    RENDER_CV_MCP_CWD: str = "/home/pukar-kafle/Documents/rendercv/rendercv"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def validate_debug(cls, v: str) -> int:
        if int(v) in [0, 1]:
            return int(v)
        raise ValueError("Debug must be 0 or 1")

    @field_validator("GUNICORN_WORKERS", mode="before")
    @classmethod
    def validate_gunicorn_workers(cls, v: str) -> int:
        if int(v) > 0:
            return int(v)
        raise ValueError("Gunicorn_WORKERS must be a positive integers")

    @field_validator("GUNICORN_THREADS", mode="before")
    @classmethod
    def validate_gunicorn_threads(cls, v: str) -> int:
        if int(v) > 0:
            return int(v)
        raise ValueError("Gunicorn_THREADS works must be a positive integers")

    @field_validator("DB_URL", mode="before")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if not v:
            # Fallback to default if empty string is provided via env
            return "postgresql+asyncpg://postgres:password@localhost:5433/makeyourcv"
        return v


settings = Settings()


# Add required settings to process environment variables
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
os.environ["OPENROUTER_API_KEY"] = settings.OPENROUTER_API_KEY
os.environ["RENDER_CV_MCP_URL"] = settings.RENDER_CV_MCP_URL
