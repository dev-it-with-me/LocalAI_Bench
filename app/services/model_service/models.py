"""
Data models for model service.
"""

from typing import Any
from pydantic import BaseModel, Field

from app.models import BaseEntityModel
from app.enums import ModelTypeEnum


class ModelParameters(BaseModel):
    """Model for AI model parameters."""
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    max_tokens: int | None = None
    stop_sequences: list[str] | None = None
    
    # Additional model-specific parameters
    extra_params: dict[str, Any] = Field(default_factory=dict)


class Model(BaseEntityModel[str]):
    """Model for AI models configuration."""
    name: str
    type: ModelTypeEnum
    description: str = ""
    
    # Model identifier
    model_id: str  # HF model ID, Ollama model name, or API model identifier
    
    # API configuration
    api_url: str | None = None
    api_key: str | None = None
    api_version: str | None = None
    
    # Model parameters
    parameters: ModelParameters = Field(default_factory=ModelParameters)
    
    # Resource requirements
    memory_required: float | None = None  # GB
    gpu_required: bool = False
    quantization: str | None = None  # e.g., "int8", "fp16"