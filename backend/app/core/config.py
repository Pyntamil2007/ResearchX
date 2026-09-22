import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base Directory: backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "ResearchX – Web Research Analyzer"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Security / JWT
    SECRET_KEY: str = "researchx_super_secret_jwt_key_2026_change_in_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'researchx.db'}"
    
    # Frontend URL & CORS
    FRONTEND_URL: str = "http://127.0.0.1:5173"
    CORS_ORIGINS: str = ""
    
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    DEMO_DIR: Path = BASE_DIR / "demo_papers"
    MAX_FILE_SIZE_MB: int = 100  # 100 MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".doc", ".jpg", ".jpeg", ".png", ".webp"]
    
    # Password Reset & Recovery
    RESET_TOKEN_EXPIRE_MINUTES: int = 15

    # Administrator Initial Configuration
    ADMIN_EMAIL: str = "admin@researchx.com"
    ADMIN_PASSWORD: str = "Admin@2026"

    # Optional External AI / LLM Keys
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Optional SMTP Email Configuration
    SMTP_EMAIL: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_FROM_NAME: str = "ResearchX Team"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure storage directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.DEMO_DIR.mkdir(parents=True, exist_ok=True)
