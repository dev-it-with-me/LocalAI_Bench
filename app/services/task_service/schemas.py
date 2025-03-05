"""
Schemas for the task service.
"""

from typing import Any
from datetime import datetime
from pydantic import BaseModel

from app.enums import TaskStatusEnum
from app.schemas import BaseResponse

class TaskCreateRequest(BaseModel):
    """Schema for creating a new task."""
    name: str
    template_id: str
    description: str = ""
    category_id: None |str = None
    input_data: None |dict[str, Any] = None
    expected_output: None |dict[str, Any] = None
    evaluation_weights: None |dict[str, float] = None
    status: TaskStatusEnum = TaskStatusEnum.DRAFT

class TaskUpdateRequest(BaseModel):
    """Schema for updating an existing task."""
    name: None |str = None
    description: None |str = None
    category_id: None |str = None
    input_data: None |dict[str, Any] = None
    expected_output: None |dict[str, Any]= None
    evaluation_weights: None |dict[str, float] = None
    status: None |TaskStatusEnum = None

class TaskResponse(BaseModel):
    """Schema for task response."""
    id: str
    name: str
    template_id: str
    description: str
    category_id: None |str
    status: TaskStatusEnum
    input_data: dict[str, Any]
    expected_output: None |dict[str, Any]
    evaluation_weights: None |dict[str, float]
    created_at: datetime
    updated_at: datetime

class TasksResponse(BaseResponse):
    """Response schema for multiple tasks."""
    tasks: list[TaskResponse]