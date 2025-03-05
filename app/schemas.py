"""
API request and response schemas for LocalAI Bench application.

This module contains Pydantic models used for API request validation
and response serialization.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.enums import (
    DataTypeEnum, 
    EvaluationCriteriaTypeEnum,
    ImportExportTypeEnum, 
    ModelTypeEnum,
    TaskStatusEnum, 
    TemplateTypeEnum
)


# Base response schema with status and message
class BaseResponse(BaseModel):
    """Base response schema with status and message."""
    status: str = "success"
    message: str = ""


# ======== Category Schemas ========
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
    name: Optional[str] = None
    description: Optional[str] = None
    time_weight: Optional[float] = Field(default=None, gt=0, le=5.0)
    quality_weight: Optional[float] = Field(default=None, gt=0, le=5.0)
    complexity_weight: Optional[float] = Field(default=None, gt=0, le=5.0)
    cost_weight: Optional[float] = Field(default=None, gt=0, le=5.0)
    memory_weight: Optional[float] = Field(default=None, gt=0, le=5.0)


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: str
    name: str
    description: str
    task_ids: List[str]
    time_weight: float
    quality_weight: float
    complexity_weight: float
    cost_weight: float
    memory_weight: float
    created_at: datetime
    updated_at: datetime


class CategoriesResponse(BaseResponse):
    """Response schema for multiple categories."""
    categories: List[CategoryResponse]


# ======== Template Schemas ========
class InputSchemaFieldSchema(BaseModel):
    """Schema for a field in a template input schema."""
    type: DataTypeEnum
    description: str = ""
    required: bool = True
    default: Any = None


class OutputSchemaFieldSchema(BaseModel):
    """Schema for a field in a template output schema."""
    type: DataTypeEnum
    description: str = ""


class EvaluationCriteriaSchema(BaseModel):
    """Schema for evaluation criteria."""
    weight: float = Field(gt=0, le=1)
    type: EvaluationCriteriaTypeEnum


class TestCaseSchema(BaseModel):
    """Schema for a test case."""
    input: str  # Path to input file
    expected: str  # Path to expected output file


class TemplateCreateRequest(BaseModel):
    """Schema for creating a new template."""
    name: str
    template_id: str
    category: TemplateTypeEnum
    description: str
    input_schema: Dict[str, InputSchemaFieldSchema]
    output_schema: Dict[str, OutputSchemaFieldSchema]
    evaluation_criteria: Dict[str, EvaluationCriteriaSchema]
    test_cases: List[TestCaseSchema] = Field(default_factory=list)


class TemplateUpdateRequest(BaseModel):
    """Schema for updating an existing template."""
    name: Optional[str] = None
    category: Optional[TemplateTypeEnum] = None
    description: Optional[str] = None
    input_schema: Optional[Dict[str, InputSchemaFieldSchema]] = None
    output_schema: Optional[Dict[str, OutputSchemaFieldSchema]] = None
    evaluation_criteria: Optional[Dict[str, EvaluationCriteriaSchema]] = None
    test_cases: Optional[List[TestCaseSchema]] = None


class TemplateResponse(BaseModel):
    """Schema for template response."""
    id: str
    template_id: str
    name: str
    category: TemplateTypeEnum
    description: str
    input_schema: Dict[str, InputSchemaFieldSchema]
    output_schema: Dict[str, OutputSchemaFieldSchema]
    evaluation_criteria: Dict[str, EvaluationCriteriaSchema]
    test_cases: List[TestCaseSchema]
    created_at: datetime
    updated_at: datetime


class TemplatesResponse(BaseResponse):
    """Response schema for multiple templates."""
    templates: List[TemplateResponse]


# ======== Task Schemas ========
class TaskCreateRequest(BaseModel):
    """Schema for creating a new task."""
    name: str
    template_id: str
    description: str = ""
    category_id: Optional[str] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)
    expected_output: Optional[Dict[str, Any]] = None
    evaluation_weights: Optional[Dict[str, float]] = None
    status: TaskStatusEnum = TaskStatusEnum.DRAFT


class TaskUpdateRequest(BaseModel):
    """Schema for updating an existing task."""
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    expected_output: Optional[Dict[str, Any]] = None
    evaluation_weights: Optional[Dict[str, float]] = None
    status: Optional[TaskStatusEnum] = None


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: str
    name: str
    template_id: str
    description: str
    category_id: Optional[str]
    status: TaskStatusEnum
    input_data: Dict[str, Any]
    expected_output: Optional[Dict[str, Any]]
    evaluation_weights: Optional[Dict[str, float]]
    created_at: datetime
    updated_at: datetime


class TasksResponse(BaseResponse):
    """Response schema for multiple tasks."""
    tasks: List[TaskResponse]


# ======== Model Schemas ========
class ModelParametersSchema(BaseModel):
    """Schema for model parameters."""
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    max_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    extra_params: Dict[str, Any] = Field(default_factory=dict)


class ModelCreateRequest(BaseModel):
    """Schema for creating a new model."""
    name: str
    type: ModelTypeEnum
    description: str = ""
    model_id: str
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    parameters: ModelParametersSchema = Field(default_factory=ModelParametersSchema)
    memory_required: Optional[float] = None
    gpu_required: bool = False
    quantization: Optional[str] = None


class ModelUpdateRequest(BaseModel):
    """Schema for updating an existing model."""
    name: Optional[str] = None
    description: Optional[str] = None
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    parameters: Optional[ModelParametersSchema] = None
    memory_required: Optional[float] = None
    gpu_required: Optional[bool] = None
    quantization: Optional[str] = None


class ModelResponse(BaseModel):
    """Schema for model response."""
    id: str
    name: str
    type: ModelTypeEnum
    description: str
    model_id: str
    api_url: Optional[str]
    api_version: Optional[str]
    parameters: ModelParametersSchema
    memory_required: Optional[float]
    gpu_required: bool
    quantization: Optional[str]
    created_at: datetime
    updated_at: datetime


class ModelsResponse(BaseResponse):
    """Response schema for multiple models."""
    models: List[ModelResponse]


# ======== Benchmark Schemas ========
class BenchmarkCreateRequest(BaseModel):
    """Schema for creating a new benchmark run."""
    name: str
    model_ids: List[str]
    category_ids: Optional[List[str]] = None
    task_ids: Optional[List[str]] = None
    description: str = ""


class ScoreComponentSchema(BaseModel):
    """Schema for score component."""
    raw_score: float
    normalized_score: float
    weight: float
    description: Optional[str] = None


class TaskResultSchema(BaseModel):
    """Schema for task result."""
    id: str
    task_id: str
    model_id: str
    benchmark_run_id: str
    execution_time_seconds: Optional[float]
    memory_usage_mb: Optional[float]
    token_count: Optional[int]
    time_score: Optional[ScoreComponentSchema]
    quality_score: Optional[ScoreComponentSchema]
    complexity_score: Optional[ScoreComponentSchema]
    cost_score: Optional[ScoreComponentSchema]
    memory_score: Optional[ScoreComponentSchema]
    ultimate_score: Optional[float]
    output_data: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: datetime


class BenchmarkResponse(BaseModel):
    """Schema for benchmark response."""
    id: str
    name: str
    description: str
    model_ids: List[str]
    category_ids: Optional[List[str]]
    task_ids: Optional[List[str]]
    status: TaskStatusEnum
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime


class BenchmarkStatusResponse(BaseResponse):
    """Schema for benchmark status response."""
    id: str
    name: str
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    progress: Dict[str, Any]
    is_active: bool
    error: Optional[str]


class BenchmarkResultsResponse(BaseResponse):
    """Schema for benchmark results response."""
    benchmark_run: Dict[str, Any]
    models: Dict[str, Dict[str, str]]
    categories: Dict[str, Dict[str, str]]
    results_by_model: Dict[str, Dict[str, List[Dict[str, Any]]]]
    aggregate_scores: Dict[str, Dict[str, float]]


class BenchmarksResponse(BaseResponse):
    """Response schema for multiple benchmarks."""
    benchmarks: List[BenchmarkResponse]


# ======== Import/Export Schemas ========
class ExportRequest(BaseModel):
    """Schema for export request."""
    export_type: ImportExportTypeEnum
    entity_ids: List[str]


class ExportResponse(BaseResponse):
    """Schema for export response."""
    export_data: Dict[str, Any]
    file_name: str


class ImportRequest(BaseModel):
    """Schema for import request."""
    import_data: Dict[str, Any]


class ImportPreviewResponse(BaseResponse):
    """Schema for import preview response."""
    import_type: ImportExportTypeEnum
    entities_to_import: Dict[str, List[Dict[str, Any]]]
    conflicts: Dict[str, List[Dict[str, Any]]]


# ======== Error Schemas ========
class ErrorResponse(BaseModel):
    """Schema for error response."""
    status: str = "error"
    message: str
    error_type: str
    details: Optional[Dict[str, Any]] = None