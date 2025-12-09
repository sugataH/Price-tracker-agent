# backend/app/core/settings.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "AI Price Tracker Backend"
    environment: str = "development"

    # MongoDB
    database_url: str = "mongodb://localhost:27017"
    mongo_db_name: str = "price_tracker"

    # Email / SMTP
    smtp_email: str | None = None
    smtp_password: str | None = None
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587

    # LLM (Groq)
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
