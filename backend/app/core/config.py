from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins_raw: str = Field(
        default="http://localhost:5173,http://localhost:8080",
        alias="BACKEND_CORS_ORIGINS",
    )

    database_url: str = "postgresql+psycopg://crm_user:crm_password@localhost:5432/merea_crm"
    excel_data_path: str = "./data/crm-data.xlsx"
    excel_backup_dir: str = "./data/backups"
    n8n_webhook_token: str = "change-me"
    propstack_api_key: str = ""
    propstack_base_url: str = "https://api.propstack.de"

    @property
    def backend_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

