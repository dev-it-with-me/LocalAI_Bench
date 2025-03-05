"""
Data models for category service.
"""

from pydantic import BaseModel, Field

from app.models import BaseEntityModel


class Category(BaseEntityModel[str]):
    """Model for benchmark categories."""
    name: str
    description: str = ""
    task_ids: list[str] = Field(default_factory=list)
    
    # Custom weights for scoring within this category
    time_weight: float = 1.0
    quality_weight: float = 1.0
    complexity_weight: float = 1.0
    cost_weight: float = 1.0
    memory_weight: float = 1.0