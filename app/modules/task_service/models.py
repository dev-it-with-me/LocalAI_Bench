"""
Data models for task service.
"""

from pydantic import BaseModel, Field

from app.models import BaseEntityModel
from app.enums import TaskStatusEnum

class ImageInputData(BaseModel):
    """Model for image input data."""
    id: str = Field(default=..., description="ID of the image")
    filename: str = Field(default=..., description="Filename of the image")
    filepath: str = Field(default=..., description="Filepath of the image")

class InputData(BaseModel):
    """Model for task input data."""
    user_instruction: str = Field(default="", description="User instruction")
    system_prompt: str | None = Field(default=None, description="System prompt")
    image: list[ImageInputData] | None = Field(default=None, description="List of image input data")

class EvaluationWeights(BaseModel):
    """Model for evaluation weights."""
    complexity: float = Field(default=1.0, description="Complexity weight")
    accuracy: float = Field(default=1.0, description="Accuracy weight")
    latency: float = Field(default=1.0, description="Latency weight")
    cost_memory_usage: float = Field(default=1.0, description="Cost/Memory usage weight")

class Task(BaseEntityModel[str]):
    """Model for benchmark tasks."""
    name: str = Field(default=..., description="Task name")
    description: str = Field(default="", description="Task description")
    status: TaskStatusEnum = Field(default=TaskStatusEnum.DRAFT, description="Task status")
    category_id: str = Field(default=..., description="ID of the task category")
    input_data: InputData = Field(default=..., description="Task input data")
    expected_output: str | None = Field(default=None, description="Expected output")

    evaluation_weights: EvaluationWeights | None = Field(default=None, description="Evaluation weights for the task")

    class Config:
        use_enum_values = True