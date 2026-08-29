"""Configuration management using Pydantic Settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Agentic Multimodal Research Platform"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Database
    database_url: str = "postgresql+asyncpg://research:research@localhost:5432/research"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Vector Store (ChromaDB)
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Model Providers
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_web2api_base_url: str = "http://127.0.0.1:8081/v1"
    gemini_web2api_api_key: Optional[str] = None
    gemini_web2api_timeout: float = 60.0
    gemini_web2api_max_retries: int = 2

    # Default Models
    default_llm_model: str = "llama3.1"
    gemini_default_model: str = "gemini-3.7-flash"
    default_vision_model: str = "llava"
    default_embedding_model: str = "nomic-embed-text"
    default_reranker_model: str = "bge-reranker-base"
    
    # Search API (optional)
    search_api_url: Optional[str] = None
    search_api_key: Optional[str] = None
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    
    # File Upload
    upload_dir: Path = Path("./uploads")
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or console
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Rate Limiting
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()