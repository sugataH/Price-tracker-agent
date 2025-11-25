from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AI Price Tracker Backend"
    environment: str = "development"

    # Secrets
    openai_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
