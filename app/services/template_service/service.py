"""
Template service implementation.
"""

from app.enums import TemplateTypeEnum
from app.exceptions import ValidationError
from app.services.template_service.models import Template
from app.services.task_service.models import Task
from app.services.task_service.repositories import TaskRepository
from app.services.template_service.repositories import TemplateRepository
from app.services.template_service.schemas import (
    InputSchemaFieldSchema,
    OutputSchemaFieldSchema,
    EvaluationCriteriaSchema,
    TestCaseSchema
)

from app.utils import get_logger


class TemplateService:
    """Service for managing task templates."""

    def __init__(self):
        """Initialize the template service."""
        self.logger = get_logger("TemplateService")
        self.template_repo = TemplateRepository()
        self.task_repo = TaskRepository()

    async def create_template(
        self,
        name: str,
        template_id: str,
        category: TemplateTypeEnum,
        description: str,
        input_schema: dict[str, InputSchemaFieldSchema],
        output_schema: dict[str, OutputSchemaFieldSchema],
        evaluation_criteria: dict[str, EvaluationCriteriaSchema],
        test_cases: None | list[TestCaseSchema] = None,
    ) -> Template:
        """Create a new template."""
        template = Template(
            name=name,
            template_id=template_id,
            category=category,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            evaluation_criteria=evaluation_criteria,
            test_cases=test_cases or []
        )

        # Validate schema
        await self.validate_template_schema(template)
        
        if self.template_repo.create(template):
            self.logger.info(f"Created template: {template.id}")
            return template
        else:
            raise ValidationError("Failed to create template")

    async def get_template(self, template_id: str) -> Template:
        """Get a template by ID."""
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise ValidationError(f"Template not found: {template_id}")
        return template

    async def list_templates(
        self, category: None | TemplateTypeEnum = None
    ) -> list[Template]:
        """Get all templates, optionally filtered by category."""
        templates = self.template_repo.list_all()
        if category:
            templates = [t for t in templates if t.category == category]
        return templates

    async def update_template(
        self,
        template_id: str,
        name: None | str = None,
        description: None | str = None,
        input_schema: None | dict[str, InputSchemaFieldSchema] = None,
        output_schema: None | dict[str, OutputSchemaFieldSchema] = None,
        evaluation_criteria: None | dict[str, EvaluationCriteriaSchema] = None,
        test_cases: None | list[TestCaseSchema] = None,
    ) -> Template:
        """Update a template."""
        template = await self.get_template(template_id)
        
        # Update fields if provided
        if name is not None:
            template.name = name
        if description is not None:
            template.description = description
        if input_schema is not None:
            template.input_schema = input_schema
        if output_schema is not None:
            template.output_schema = output_schema
        if evaluation_criteria is not None:
            template.evaluation_criteria = evaluation_criteria
        if test_cases is not None:
            template.test_cases = test_cases
        
        # Validate schema after updates
        await self.validate_template_schema(template)
            
        if self.template_repo.update(template):
            self.logger.info(f"Updated template: {template_id}")
            return template
        else:
            raise ValidationError("Failed to update template")

    async def delete_template(self, template_id: str) -> None:
        """Delete a template."""
        template = await self.get_template(template_id)
        
        # Check if template is used by any tasks
        tasks = self.task_repo.list_all()
        tasks_using_template = [t for t in tasks if t.template_id == template_id]
        if tasks_using_template:
            raise ValidationError(
                f"Template is in use by {len(tasks_using_template)} tasks",
            )
        
        # Delete template
        if not self.template_repo.delete(template_id):
            raise ValidationError("Failed to delete template")
            
        self.logger.info(f"Deleted template: {template_id}")

    async def validate_template_schema(self, template: Template) -> None:
        """Validate a template's schema against test cases."""
        if not template.input_schema:
            raise ValidationError(
                "Template must have input schema",
            )
            
        if not template.output_schema:
            raise ValidationError(
                "Template must have output schema",
            )
            
        if not template.evaluation_criteria:
            raise ValidationError(
                "Template must have evaluation criteria",
            )
            
        # Validate test cases if present
        if template.test_cases:
            for test_case in template.test_cases:
                # Validate input data against schema
                for field_name, field_schema in template.input_schema.items():
                    if field_schema.required and field_name not in test_case.input_data:
                        raise ValidationError(
                            f"Test case missing required input field: {field_name}",
                        )
                
                # Validate expected output against schema
                if test_case.expected_output:
                    for field_name, field_schema in template.output_schema.items():
                        if field_schema.required and field_name not in test_case.expected_output:
                            raise ValidationError(
                                f"Test case missing required output field: {field_name}"
                            )

    async def get_template_tasks(self, template_id: str) -> list[Task]:
        """Get all tasks using a template."""
        template = await self.get_template(template_id)
        
        tasks = []
        for task in self.task_repo.list_all():
            if task.template_id == template_id:
                tasks.append(task)
                
        return tasks