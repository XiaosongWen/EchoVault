from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnv = Literal["development", "testing", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "EchoVault"
    app_version: str = "0.1.0"
    app_env: AppEnv = "development"
    log_level: LogLevel = "INFO"
    log_format: Literal["auto", "json", "console"] = "auto"
    request_id_header: str = "X-Request-ID"

    database_url: str = ""
    db_schema: str = "echovault"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_recycle: int = 1800
    db_pool_timeout: int = 30

    supabase_url: str = ""
    supabase_jwt_secret: SecretStr = SecretStr("")
    supabase_service_role_key: SecretStr = SecretStr("")
    llm_api_key: SecretStr = SecretStr("")

    @property
    def async_database_url(self) -> str:
        """Return the database URL normalized for asynchronous drivers."""
        url = self.database_url.strip()
        if not url:
            return ""
        if url.startswith("postgres://"):
            url = "postgresql+asyncpg://" + url[len("postgres://") :]
        elif url.startswith("postgresql://"):
            url = "postgresql+asyncpg://" + url[len("postgresql://") :]
        elif url.startswith("sqlite://") and not url.startswith("sqlite+aiosqlite://"):
            url = "sqlite+aiosqlite://" + url[len("sqlite://") :]
        return url

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
