"""
Schemas for the category service.
"""

from datetime import datetime
from pydantic import BaseModel
from app.schemas import BaseResponse

class CategoryCreateRequest(BaseModel):
    """Schema for creating a new category."""
    name: str
    description: str = ""

class CategoryUpdateRequest(BaseModel):
    """Schema for updating an existing category."""
    name: None | str = None
    description: None | str = None

class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: str
    name: str
    description: str
    task_ids: list[str]
    created_at: datetime
    updated_at: datetime

class CategoriesResponse(BaseResponse):
    """Response schema for multiple categories."""
    categories: list[CategoryResponse]