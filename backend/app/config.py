"""
Application configuration settings.
Loads environment variables from .env file.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ===========================================
    # LLM Configuration
    # ===========================================
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "gemini-2.0-flash"
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.7
    
    # ===========================================
    # Database
    # ===========================================
    DATABASE_URL: str = "sqlite:///./gst_compliance.db"
    CHROMA_PERSIST_DIR: str = "./gst_law_db"
    
    # ===========================================
    # Authentication
    # ===========================================
    JWT_SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # ===========================================
    # File Upload
    # ===========================================
    UPLOAD_DIR: str = "./uploads"
    EXPORT_DIR: str = "./exports"
    MAX_UPLOAD_SIZE_MB: int = 50
    
    # ===========================================
    # Server
    # ===========================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # ===========================================
    # Frontend URL (for CORS)
    # ===========================================
    FRONTEND_URL: str = "http://localhost:5173"
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Maximum upload file size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid reloading settings on every call.
    """
    return Settings()


# Convenience access to settings
settings = get_settings()
