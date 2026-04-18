from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "rdvd-be"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./rdvd.db"
    secret_key: str = "change-me-in-production"

    model_config = {"env_file": ".env"}

@lru_cache
def get_settings() -> Settings:
    return Settings()
