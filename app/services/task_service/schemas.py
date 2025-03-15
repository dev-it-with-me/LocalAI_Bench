"""
Schemas for the task service.
"""

from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.enums import TaskStatusEnum
from app.schemas import BaseResponse
from app.services.task_service.models import InputData, EvaluationWeights

class InputDataRequest(BaseModel):
    """Schema for input data request."""
    user_instruction: str = Field(default="", description="User instruction")
    system_prompt: None | str = Field(default=None, description="System prompt")
    image: None | list[dict[str, str]] = Field(default=None, description="List of image input data")

class EvaluationWeightsRequest(BaseModel):
    """Schema for evaluation weights request."""
    complexity: float = Field(default=1.0, description="Complexity weight")
    accuracy: float = Field(default=1.0, description="Accuracy weight")
    latency: float = Field(default=1.0, description="Latency weight")
    cost_memory_usage: float = Field(default=1.0, description="Cost/Memory usage weight")

class TaskCreateRequest(BaseModel):
    """Schema for creating a new task."""
    name: str
    description: str = ""
    category_id: None | str = None
    input_data: None | InputDataRequest = None
    expected_output: None | str = None
    evaluation_weights: None | EvaluationWeightsRequest = None
    status: TaskStatusEnum = TaskStatusEnum.DRAFT

    class Config:
        use_enum_values = True

class TaskUpdateRequest(BaseModel):
    """Schema for updating an existing task."""
    name: None | str = None
    description: None | str = None
    category_id: None | str = None
    input_data: None | InputDataRequest = None
    expected_output: None | str = None
    evaluation_weights: None | EvaluationWeightsRequest = None
    status: None | TaskStatusEnum = None

    class Config:
        use_enum_values = True

class TaskResponse(BaseModel):
    """Schema for task response."""
    id: str
    name: str
    description: str
    category_id: str
    status: TaskStatusEnum
    input_data: InputData
    expected_output: None | str
    evaluation_weights: None | EvaluationWeights
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True

class TasksResponse(BaseResponse):
    """Response schema for multiple tasks."""
    tasks: list[TaskResponse]

    class Config:
        use_enum_values = True