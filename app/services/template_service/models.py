"""
Data models for template service.
"""

from typing import Any
from pydantic import BaseModel, Field

from app.models import BaseEntityModel
from app.enums import DataTypeEnum, EvaluationCriteriaTypeEnum, TemplateTypeEnum


class InputSchemaField(BaseModel):
    """Model for a field in a template input schema."""
    type: DataTypeEnum
    description: str = ""
    required: bool = True
    default: Any | None = None


class OutputSchemaField(BaseModel):
    """Model for a field in a template output schema."""
    type: DataTypeEnum
    description: str = ""


class EvaluationCriteria(BaseModel):
    """Model for evaluation criteria used in task templates."""
    weight: float = Field(gt=0, le=1)
    type: EvaluationCriteriaTypeEnum


class TestCase(BaseModel):
    """Model for a test case in a task template."""
    input: str  # Path to input file
    expected: str  # Path to expected output file


class Template(BaseEntityModel[str]):
    """Model for task templates."""
    template_id: str
    name: str
    category: TemplateTypeEnum
    description: str
    input_schema: dict[str, InputSchemaField]
    evaluation_criteria: dict[str, EvaluationCriteria]
    output_schema: dict[str, OutputSchemaField]
    test_cases: list[TestCase] = Field(default_factory=list)