"""
Configuration settings for the LocalAI Bench application.

This module provides a centralized configuration system using Pydantic Settings.
Environment variables can override default settings by using the prefix LOCALAI_BENCH_.
"""

import os
from pathlib import Path
from typing import Any

from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings including paths, API credentials, and operational parameters."""
    
    # Environment and application info
    APP_NAME: str = "LocalAI Bench"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Path settings
    BASE_DIR: str = str(Path(__file__).parent.parent)
    DATA_DIR: str = str(Path(BASE_DIR) / "data")
    LOG_DIR: str = str(Path(BASE_DIR) / "logs")
    
    # Data storage settings
    CATEGORIES_DIR: str | None = None
    TASKS_DIR: str | None = None
    TEMPLATES_DIR: str | None = None
    MODELS_DIR: str | None = None
    RESULTS_DIR: str | None = None
    IMAGES_DIR: str | None = None

    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "development_secret_key_change_this_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
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
    
    @computed_field
    def data_subdirs(self) -> dict[str, str]:
        """Return all data subdirectories for easy access."""
        base_data_dir = Path(self.DATA_DIR)
        
        # Set default values for subdirectories if not explicitly set
        categories_dir = self.CATEGORIES_DIR or str(base_data_dir / "categories")
        tasks_dir = self.TASKS_DIR or str(base_data_dir / "tasks")
        templates_dir = self.TEMPLATES_DIR or str(base_data_dir / "templates")
        models_dir = self.MODELS_DIR or str(base_data_dir / "models")
        results_dir = self.RESULTS_DIR or str(base_data_dir / "results")
        images_dir = self.IMAGES_DIR or str(base_data_dir / "images")
        
        # Create directories if they don't exist
        for dir_path in [categories_dir, tasks_dir, templates_dir, models_dir, results_dir, images_dir]:
            os.makedirs(dir_path, exist_ok=True)
            
        return {
            "categories": categories_dir,
            "tasks": tasks_dir,
            "templates": templates_dir,
            "models": models_dir,
            "results": results_dir,
            "images": images_dir,
        }
    
    model_config = SettingsConfigDict(
        env_prefix="LOCALAI_BENCH_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Create a global settings instance
settings = AppSettings()