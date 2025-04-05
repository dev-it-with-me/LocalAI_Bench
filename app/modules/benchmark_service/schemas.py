"""
Schemas for the benchmark service.
"""

from typing import Any
from datetime import datetime
from pydantic import BaseModel

from app.schemas import BaseResponse
from .models import BenchmarkRun

class BenchmarkCreateRequest(BaseModel):
    """Schema for creating a new benchmark run."""
    name: str
    model_ids: list[str]
    category_ids: None | list[str] = None
    task_ids: None | list[str] = None
    description: str = ""

class BenchmarkStatusResponse(BaseModel):
    """Schema for benchmark status response."""
    id: str
    name: str
    status: str
    start_time: None | datetime
    end_time: None | datetime
    progress: dict[str, Any]
    is_active: bool
    error: None | str

class BenchmarkResultsResponse(BaseModel):
    """Schema for benchmark results response."""
    benchmark_run: dict[str, Any]
    models: dict[str, dict[str, str]]
    categories: dict[str, dict[str, str]]
    results_by_model: dict[str, dict[str, list[dict[str, Any]]]]
    aggregate_scores: dict[str, dict[str, float]]

class BenchmarksResponse(BaseResponse):
    """Response schema for multiple benchmarks."""
    benchmarks: list[BenchmarkRun]