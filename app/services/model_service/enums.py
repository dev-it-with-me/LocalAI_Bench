"""
Enum definitions for model service.
"""

from enum import Enum


class QuantizationTypeEnum(Enum):
    """Types of model quantization."""
    NONE = "none"
    INT8 = "int8"
    INT4 = "int4"
    FP16 = "fp16"


class ModelStatusEnum(Enum):
    """Status of a model."""
    AVAILABLE = "available"
    LOADING = "loading"
    ERROR = "error"
    OFFLINE = "offline"