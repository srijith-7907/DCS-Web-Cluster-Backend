from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/event_ticketing"
    JWT_SECRET_KEY: str = "change-me-super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@events.local"
    SMTP_USE_TLS: bool = False
    APP_NAME: str = "Event Ticketing API"
    APP_ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
