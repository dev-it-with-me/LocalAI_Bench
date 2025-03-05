"""
Schemas for the template service.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from app.enums import DataTypeEnum, EvaluationCriteriaTypeEnum, TemplateTypeEnum
from app.schemas import BaseResponse

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
    input_schema: dict[str, InputSchemaFieldSchema]
    output_schema: dict[str, OutputSchemaFieldSchema]
    evaluation_criteria: dict[str, EvaluationCriteriaSchema]
    test_cases: list[TestCaseSchema] = Field(default_factory=list)

class TemplateUpdateRequest(BaseModel):
    """Schema for updating an existing template."""
    name: None | str = None
    category: None | TemplateTypeEnum = None
    description: None | str = None
    input_schema: None | dict[str, InputSchemaFieldSchema] = None
    output_schema: None | dict[str, OutputSchemaFieldSchema] = None
    evaluation_criteria: None | dict[str, EvaluationCriteriaSchema] = None
    test_cases: None | list[TestCaseSchema] = None

class TemplateResponse(BaseModel):
    """Schema for template response."""
    id: str
    template_id: str
    name: str
    category: TemplateTypeEnum
    description: str
    input_schema: dict[str, InputSchemaFieldSchema]
    output_schema: dict[str, OutputSchemaFieldSchema]
    evaluation_criteria: dict[str, EvaluationCriteriaSchema]
    test_cases: list[TestCaseSchema]
    created_at: datetime
    updated_at: datetime

class TemplatesResponse(BaseResponse):
    """Response schema for multiple templates."""
    templates: list[TemplateResponse]