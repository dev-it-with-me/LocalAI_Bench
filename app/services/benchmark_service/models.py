"""
Data models for benchmark service.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from app.models import BaseEntityModel
from app.enums import TaskStatusEnum
from .enums import ScoreTypeEnum


class ScoreComponent(BaseModel):
    """Model for an individual score component."""
    raw_score: float
    normalized_score: float
    weight: float
    description: str | None = None


class TaskResult(BaseEntityModel[str]):
    """Model for the result of a benchmark task for a specific model."""
    task_id: str
    model_id: str
    benchmark_run_id: str | None = None
    
    # Execution metrics
    execution_time_seconds: float | None = None
    memory_usage_mb: float | None = None
    token_count: int | None = None
    
    # Scores
    time_score: ScoreComponent | None = None
    quality_score: ScoreComponent | None = None
    complexity_score: ScoreComponent | None = None
    cost_score: ScoreComponent | None = None
    memory_score: ScoreComponent | None = None
    
    # Overall score
    ultimate_score: float | None = None
    
    # Output data
    output_data: dict[str, Any] | None = None
    
    # Error information
    error: str | None = None


class BenchmarkRun(BaseEntityModel[str]):
    """Model for a benchmark run containing multiple task results."""
    name: str
    description: str = ""
    category_ids: list[str] | None = None
    task_ids: list[str] | None = None
    model_ids: list[str]
    
    # Results (populated after benchmark execution)
    task_results: list[str] = Field(default_factory=list)  # TaskResult IDs
    
    # Aggregate scores per model and category
    aggregate_scores: dict[str, dict[str, float]] = Field(default_factory=dict)  # model_id -> category_id -> score
    
    # Status information
    status: TaskStatusEnum = TaskStatusEnum.DRAFT
    start_time: datetime | None = None
    end_time: datetime | None = None
    
    # Error information
    error: str | None = None