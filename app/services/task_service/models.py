"""
Data models for task service.
"""

from typing import Any
from pydantic import BaseModel, Field

from app.models import BaseEntityModel
from app.enums import TaskStatusEnum


class Task(BaseEntityModel[str]):
    """Model for benchmark tasks."""
    name: str
    template_id: str
    description: str = ""
    status: TaskStatusEnum = TaskStatusEnum.DRAFT
    category_id: str | None = None
    input_data: dict[str, Any] = Field(default_factory=dict)
    expected_output: dict[str, Any] | None = None
    
    # Custom weights for this specific task (overrides template defaults)
    evaluation_weights: dict[str, float] | None = None