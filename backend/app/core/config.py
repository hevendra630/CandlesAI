from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://stockuser:stockpass@postgres:5432/stockdb"
    secret_key: str = "supersecretkey-change-in-production-min32chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    news_api_key: str = ""
    redis_url: str = "redis://redis:6379"
    ai_service_url: str = "http://ai_service:8001"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
