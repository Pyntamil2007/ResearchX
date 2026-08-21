import os
from pathlib import Path
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
    
    # Uploads & Storage
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    DEMO_DIR: Path = BASE_DIR / "demo_papers"
    MAX_FILE_SIZE_MB: int = 100  # 100 MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".jpg", ".jpeg", ".png", ".webp"]
    
    # Password Reset & Recovery
    RESET_TOKEN_EXPIRE_MINUTES: int = 15

    # Administrator Initial Configuration
    ADMIN_EMAIL: str = "admin@researchx.com"
    ADMIN_PASSWORD: str = "Admin@2026"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.DEMO_DIR.mkdir(parents=True, exist_ok=True)
