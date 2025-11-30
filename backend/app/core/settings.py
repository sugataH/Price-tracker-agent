import os
from dotenv import load_dotenv

# Load .env once
load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    DATABASE_URL: str = os.getenv("DATABASE_URL")

    SMTP_EMAIL: str = os.getenv("SMTP_EMAIL")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_HOST: str = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))

settings = Settings()
