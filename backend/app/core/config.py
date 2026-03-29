"""Core configuration module using pydantic-settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Sponsor Outreach Platform"
    APP_ENV: str = "development"
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    TRACKING_BASE_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/sponsor_platform"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@postgres:5432/sponsor_platform"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # RabbitMQ / Celery
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    # JWT
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI
    OPENAI_API_KEY: str = ""

    # SendGrid
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "outreach@yourdomain.com"
    SENDGRID_FROM_NAME: str = "Sponsor Outreach"

    # Search API
    SEARCH_API_KEY: str = ""
    SEARCH_API_URL: str = "https://www.searchapi.io/api/v1/search"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
