"""
Configuration settings for the LocalAI Bench application.

This module provides a centralized configuration system using Pydantic Settings.
Environment variables can override default settings by using the prefix LOCALAI_BENCH_.
"""

import os
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings including paths, API credentials, and operational parameters."""
    
    # Environment and application info
    APP_NAME: str = "LocalAI Bench"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Path settings
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = Path(BASE_DIR / "data")
    LOG_DIR: Path = Path(BASE_DIR / "logs")
    STATIC_DIR: Path = Path(BASE_DIR / "static")
    
    # Data storage settings
    CATEGORIES_DIR: Path = DATA_DIR / "categories"
    TASKS_DIR: Path = DATA_DIR / "tasks"
    TEMPLATES_DIR: Path = DATA_DIR / "templates"
    MODELS_DIR: Path = DATA_DIR / "models"
    RESULTS_DIR: Path = DATA_DIR / "results"
    IMAGES_DIR: Path = DATA_DIR / "images"

    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Model provider settings
    HUGGINGFACE_API_TOKEN: str | None = None
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    
    # Ollama settings
    OLLAMA_HOST: str = "http://localhost:11434"
    
    # Benchmark settings
    DEFAULT_TIMEOUT: int = 300  # 5 minutes in seconds
    MAX_MEMORY_USAGE: int = 8  # GB
    
    # UI settings
    ENABLE_CORS: bool = True
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]  # Default Vite dev server

    @field_validator("DATA_DIR", "LOG_DIR")
    def validate_dir_exists(cls, path_str: str) -> str:
        """Validate that directories exist and create them if they don't."""
        path = Path(path_str)
        if not path.exists():
            path.mkdir(parents=True)
        return str(path)

    
    model_config = SettingsConfigDict(
        env_prefix="LOCALAI_BENCH_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Create a global settings instance
settings = AppSettings()