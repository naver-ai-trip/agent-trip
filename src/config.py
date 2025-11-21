"""Configuration management for the AI Travel Agent."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Backend API
    BE_API_BASE: str
    DEBUG: bool = True
    
    # LLM Configuration
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: Optional[str] = None
    MODEL_NAME: str = "gpt-4o-mini"
    LLM_MODEL: Optional[str] = None  # Alternative model field
    LLM_TEMPERATURE: Optional[float] = None  # Alternative temperature field
    
    # Agent Configuration
    MAX_ITERATIONS: int = 15
    TIMEOUT_SECONDS: int = 300
    TEMPERATURE: float = 0.7
    STREAMING_ENABLED: bool = True
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()
