"""
Schemas for the model service.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from app.enums import ModelTypeEnum
from app.schemas import BaseResponse

class ModelParametersSchema(BaseModel):
    """Schema for model parameters."""
    temperature: None | float = None
    top_p: None | float = None
    top_k: None | int = None
    max_tokens: None | int = None
    stop_sequences: None | list[str] = None
    extra_params: dict[str, Any] = Field(default_factory=dict)

class ModelCreateRequest(BaseModel):
    """Schema for creating a new model."""
    name: str
    type: ModelTypeEnum
    description: str = ""
    model_id: str
    api_url: None | str = None
    api_key: None | str = None
    api_version: None | str = None
    parameters: ModelParametersSchema = Field(default_factory=ModelParametersSchema)
    memory_required: None | float = None
    gpu_required: bool = False
    quantization: None | str = None

class ModelUpdateRequest(BaseModel):
    """Schema for updating an existing model."""
    name: None | str = None
    description: None | str = None
    api_url: None | str = None
    api_key: None | str = None
    api_version: None | str = None
    parameters: None | ModelParametersSchema = None
    memory_required: None | float = None
    gpu_required: None | bool = None
    quantization: None | str = None

class ModelResponse(BaseModel):
    """Schema for model response."""
    id: str
    name: str
    type: ModelTypeEnum
    description: str
    model_id: str
    api_url: None | str
    api_version: None | str
    parameters: ModelParametersSchema
    memory_required: None | float
    gpu_required: bool
    quantization: None | str
    created_at: datetime
    updated_at: datetime

class ModelsResponse(BaseResponse):
    """Response schema for multiple models."""
    models: list[ModelResponse]