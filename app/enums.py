"""
Enum definitions for LocalAI Bench application.

This module contains enum classes that define constants used throughout the application.
"""

from enum import Enum, auto


class TaskStatusEnum(Enum):
    """Status of a benchmark task."""
    DRAFT = "draft"
    READY = "ready" 
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"


class TemplateTypeEnum(Enum):
    """Types of task templates."""
    CODE_UI_VISION = "code_ui_vision"
    DOCUMENT_UNDERSTANDING = "document_understanding"
    RECRUITMENT_PROCESS = "recruitment_process"
    CUSTOM = "custom"


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
    

class DataTypeEnum(Enum):
    """Data types supported in templates."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    IMAGE_PATH = "image_path"
    TEXT = "text"
    STRING_ARRAY = "string_array"
    JSON_OBJECT = "json_object"


class ImportExportTypeEnum(Enum):
    """Types of import/export operations."""
    FULL_SUITE = "full_suite"
    CATEGORY = "category"
    TASK_SET = "task_set"
    RESULTS = "results"
    TEMPLATE = "template"