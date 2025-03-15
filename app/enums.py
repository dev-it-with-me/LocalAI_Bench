"""
Shared enum definitions for LocalAI Bench application.

This module contains enum classes used across multiple services.
"""

from enum import Enum


class TaskStatusEnum(Enum):
    """Status of a benchmark task."""
    DRAFT = "draft"
    READY = "ready" 
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"



class EvaluationCriteriaTypeEnum(Enum):
    """Types of evaluation criteria for tasks."""
    UNIT_TEST = "unit_test"
    MANUAL_REVIEW = "manual_review"
    STATIC_ANALYSIS = "static_analysis"
    BENCHMARK = "benchmark"
    GROUND_TRUTH_COMPARISON = "ground_truth_comparison"
    TIME_MEASUREMENT = "time_measurement"


class ModelTypeEnum(Enum):
    """Types of AI models supported."""
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM_API = "custom_api"

class ImportExportTypeEnum(Enum):
    """Types of import/export operations."""
    MODEL = "model"
    CATEGORY = "category"
    TASK_SET = "task_set"