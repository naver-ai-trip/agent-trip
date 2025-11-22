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
    
    # Naver API Configuration (for place search)
    NAVER_CLIENT_ID: Optional[str] = None
    NAVER_CLIENT_SECRET: Optional[str] = None
    
    # Naver Clova Studio API Configuration (for RAG)
    NAVER_CLOVA_API_KEY: Optional[str] = None
    NAVER_CLOVA_APIGW_API_KEY: Optional[str] = None
    NAVER_CLOVA_REQUEST_ID: Optional[str] = None
    
    # RAG Configuration
    RAG_ENABLED: bool = True
    EMBEDDING_MODEL: str = "bge-m3"  # Naver Embedding v2
    EMBEDDING_DIMENSION: int = 1024
    
    # Vector Database Configuration (Pinecone)
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None  # e.g., "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "travel-documents"
    
    # RAG Search Parameters
    RAG_TOP_K: int = 10  # Initial retrieval count
    RAG_RERANK_TOP_K: int = 3  # After reranking
    RAG_MAX_TOKENS: int = 1024
    RAG_TEMPERATURE: float = 0.5
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()
