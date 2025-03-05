"""
Pydantic data models for LocalAI Bench application.

This module contains Pydantic models that define the data structures
used throughout the application.
"""

import uuid
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, model_validator

from app.enums import (
    DataTypeEnum, 
    EvaluationCriteriaTypeEnum,
    ImportExportTypeEnum, 
    ModelTypeEnum,
    TaskStatusEnum, 
    TemplateTypeEnum
)


# Generic type for ID fields
T = TypeVar('T')


class BaseEntityModel(BaseModel, Generic[T]):
    """Base model for all entity models with ID and timestamps."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class EvaluationCriteriaModel(BaseModel):
    """Model for evaluation criteria used in task templates."""
    weight: float = Field(gt=0, le=1)
    type: EvaluationCriteriaTypeEnum


class InputSchemaFieldModel(BaseModel):
    """Model for a field in a template input schema."""
    type: DataTypeEnum
    description: str = ""
    required: bool = True
    default: Any | None = None


class OutputSchemaFieldModel(BaseModel):
    """Model for a field in a template output schema."""
    type: DataTypeEnum
    description: str = ""


class TestCaseModel(BaseModel):
    """Model for a test case in a task template."""
    input: str  # Path to input file
    expected: str  # Path to expected output file


class TemplateModel(BaseEntityModel[str]):
    """Model for task templates."""
    template_id: str
    name: str
    category: TemplateTypeEnum
    description: str
    input_schema: dict[str, InputSchemaFieldModel]
    evaluation_criteria: dict[str, EvaluationCriteriaModel]
    output_schema: dict[str, OutputSchemaFieldModel]
    test_cases: list[TestCaseModel] = Field(default_factory=list)
    
    @model_validator(mode="after")
    def validate_weights(self) -> "TemplateModel":
        """Validate that the sum of all weights in evaluation_criteria is 1.0."""
        total_weight = sum(criteria.weight for criteria in self.evaluation_criteria.values())
        if not 0.99 <= total_weight <= 1.01:  # Allow small floating point errors
            raise ValueError(f"Sum of evaluation criteria weights must be 1.0, got {total_weight}")
        return self


class TaskModel(BaseEntityModel[str]):
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


class CategoryModel(BaseEntityModel[str]):
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


class ModelParametersModel(BaseModel):
    """Model for AI model parameters."""
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    max_tokens: int | None = None
    stop_sequences: list[str] | None = None
    
    # Additional model-specific parameters
    extra_params: dict[str, Any] = Field(default_factory=dict)


class ModelModel(BaseEntityModel[str]):
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
    parameters: ModelParametersModel = Field(default_factory=ModelParametersModel)
    
    # Resource requirements
    memory_required: float | None = None  # GB
    gpu_required: bool = False
    quantization: str | None = None  # e.g., "int8", "fp16"


class ScoreComponentModel(BaseModel):
    """Model for an individual score component."""
    raw_score: float
    normalized_score: float
    weight: float
    description: str | None = None


class TaskResultModel(BaseEntityModel[str]):
    """Model for the result of a benchmark task for a specific model."""
    task_id: str
    model_id: str
    benchmark_run_id: str | None = None
    
    # Execution metrics
    execution_time_seconds: float | None = None
    memory_usage_mb: float | None = None
    token_count: int | None = None
    
    # Scores
    time_score: ScoreComponentModel | None = None
    quality_score: ScoreComponentModel | None = None
    complexity_score: ScoreComponentModel | None = None
    cost_score: ScoreComponentModel | None = None
    memory_score: ScoreComponentModel | None = None
    
    # Overall score
    ultimate_score: float | None = None
    
    # Output data
    output_data: dict[str, Any] | None = None
    
    # Error information
    error: str | None = None


class BenchmarkRunModel(BaseEntityModel[str]):
    """Model for a benchmark run containing multiple task results."""
    name: str
    description: str = ""
    category_ids: list[str] | None = None
    task_ids: list[str] | None = None
    model_ids: list[str]
    
    # Results (populated after benchmark execution)
    task_results: list[str] = Field(default_factory=list)  # TaskResultModel IDs
    
    # Aggregate scores per model and category
    aggregate_scores: dict[str, dict[str, float]] = Field(default_factory=dict)  # model_id -> category_id -> score
    
    # Status information
    status: TaskStatusEnum = TaskStatusEnum.DRAFT
    start_time: datetime | None = None
    end_time: datetime | None = None
    
    # Error information
    error: str | None = None


class ExportModel(BaseModel):
    """Model for exported data."""
    export_type: ImportExportTypeEnum
    export_date: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"
    content: dict[str, Any]  # Type depends on export_type