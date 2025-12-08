# backend/app/core/settings.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "AI Price Tracker Backend"
    environment: str = "development"

    # MongoDB
    mongo_uri: str | None = None
    mongo_db: str = "price_tracker_db"

    # Email / SMTP
    smtp_email: str | None = None
    smtp_password: str | None = None
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587

    # LLM (Groq)
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
