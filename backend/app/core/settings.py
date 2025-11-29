# backend/app/core/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AI Price Tracker Backend"
    environment: str = "development"

    # Database
    database_url: str | None = None

    # Email / SMTP
    smtp_email: str | None = None
    smtp_password: str | None = None
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587

    # LLM (Groq)
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"

    # Generic
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
