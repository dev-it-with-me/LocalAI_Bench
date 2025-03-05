"""
Enum definitions for template service.
"""

from enum import Enum


class InputValidationTypeEnum(Enum):
    """Types of input validation."""
    REQUIRED = "required"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    RANGE = "range"
    ENUM = "enum"
    FILE_EXISTS = "file_exists"
    FILE_TYPE = "file_type"


class OutputValidationTypeEnum(Enum):
    """Types of output validation."""
    TYPE_CHECK = "type_check"
    SCHEMA_VALIDATION = "schema_validation"
    CONTENT_CHECK = "content_check"
    FORMAT_CHECK = "format_check"
    CUSTOM_VALIDATOR = "custom_validator"