"""
Schemas for the category service.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas import BaseResponse

class CategoryCreateRequest(BaseModel):
    """Schema for creating a new category."""
    name: str
    description: str = ""
    time_weight: float = Field(default=1.0, gt=0, le=5.0)
    quality_weight: float = Field(default=1.0, gt=0, le=5.0)
    complexity_weight: float = Field(default=1.0, gt=0, le=5.0)
    cost_weight: float = Field(default=1.0, gt=0, le=5.0)
    memory_weight: float = Field(default=1.0, gt=0, le=5.0)

class CategoryUpdateRequest(BaseModel):
    """Schema for updating an existing category."""
    name: None | str = None
    description: None | str = None
    time_weight: None | float = Field(default=None, gt=0, le=5.0)
    quality_weight: None | float = Field(default=None, gt=0, le=5.0)
    complexity_weight: None | float = Field(default=None, gt=0, le=5.0)
    cost_weight: None | float = Field(default=None, gt=0, le=5.0)
    memory_weight: None | float = Field(default=None, gt=0, le=5.0)

class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: str
    name: str
    description: str
    task_ids: list[str]
    time_weight: float
    quality_weight: float
    complexity_weight: float
    cost_weight: float
    memory_weight: float
    created_at: datetime
    updated_at: datetime

class CategoriesResponse(BaseResponse):
    """Response schema for multiple categories."""
    categories: list[CategoryResponse]