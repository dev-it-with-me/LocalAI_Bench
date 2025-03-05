"""
Task service implementation.
"""

from typing import Any, Dict, List, Optional

from app.enums import TaskStatusEnum
from app.exceptions import ValidationError
from app.models import TaskModel
from app.repositories import CategoryRepository, TaskRepository, TemplateRepository
from app.utils import get_logger


class TaskService:
    """Service for managing benchmark tasks."""

    def __init__(self):
        """Initialize the task service."""
        self.logger = get_logger("TaskService")
        self.task_repo = TaskRepository()
        self.template_repo = TemplateRepository()
        self.category_repo = CategoryRepository()

    async def create_task(
        self,
        name: str,
        template_id: str,
        description: str = "",
        category_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        expected_output: Optional[Dict[str, Any]] = None,
        evaluation_weights: Optional[Dict[str, float]] = None,
        status: TaskStatusEnum = TaskStatusEnum.DRAFT,
    ) -> TaskModel:
        """Create a new task."""
        # Validate template exists
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise ValidationError(f"Template not found: {template_id}")

        # Validate category exists if provided
        if category_id:
            category = self.category_repo.get_by_id(category_id)
            if not category:
                raise ValidationError(f"Category not found: {category_id}")

        # Validate input data against template schema
        if input_data:
            for field_name, field_schema in template.input_schema.items():
                if field_schema.required and field_name not in input_data:
                    raise ValidationError(f"Required input field missing: {field_name}")

        # Create task
        task = TaskModel(
            name=name,
            template_id=template_id,
            description=description,
            category_id=category_id,
            input_data=input_data or {},
            expected_output=expected_output,
            evaluation_weights=evaluation_weights,
            status=status,
        )

        if self.task_repo.create(task):
            # Add task to category if specified
            if category_id:
                category = self.category_repo.get_by_id(category_id)
                if category:
                    category.task_ids.append(task.id)
                    self.category_repo.update(category)

            self.logger.info(f"Created task: {task.id}")
            return task
        else:
            raise ValidationError("Failed to create task")

    async def get_task(self, task_id: str) -> TaskModel:
        """Get a task by ID."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValidationError(f"Task not found: {task_id}")
        return task

    async def list_tasks(
        self,
        category_id: Optional[str] = None,
        status: Optional[TaskStatusEnum] = None,
    ) -> List[TaskModel]:
        """Get all tasks, optionally filtered by category and/or status."""
        tasks = self.task_repo.get_all()

        # Apply category filter
        if category_id:
            tasks = [t for t in tasks if t.category_id == category_id]

        # Apply status filter
        if status:
            tasks = [t for t in tasks if t.status == status]

        return tasks

    async def update_task(
        self,
        task_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        expected_output: Optional[Dict[str, Any]] = None,
        evaluation_weights: Optional[Dict[str, float]] = None,
        status: Optional[TaskStatusEnum] = None,
    ) -> TaskModel:
        """Update a task."""
        task = await self.get_task(task_id)

        # Handle category change
        if category_id is not None and category_id != task.category_id:
            # Remove from old category
            if task.category_id:
                old_category = self.category_repo.get_by_id(task.category_id)
                if old_category and task_id in old_category.task_ids:
                    old_category.task_ids.remove(task_id)
                    self.category_repo.update(old_category)

            # Add to new category
            if category_id:
                new_category = self.category_repo.get_by_id(category_id)
                if not new_category:
                    raise ValidationError(f"Category not found: {category_id}")
                new_category.task_ids.append(task_id)
                self.category_repo.update(new_category)

        # Validate input data against template if provided
        if input_data is not None:
            template = self.template_repo.get_by_id(task.template_id)
            if template:
                for field_name, field_schema in template.input_schema.items():
                    if field_schema.required and field_name not in input_data:
                        raise ValidationError(f"Required input field missing: {field_name}")

        # Update fields if provided
        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        if category_id is not None:
            task.category_id = category_id
        if input_data is not None:
            task.input_data = input_data
        if expected_output is not None:
            task.expected_output = expected_output
        if evaluation_weights is not None:
            task.evaluation_weights = evaluation_weights
        if status is not None:
            task.status = status

        if self.task_repo.update(task):
            self.logger.info(f"Updated task: {task_id}")
            return task
        else:
            raise ValidationError("Failed to update task")

    async def delete_task(self, task_id: str) -> None:
        """Delete a task."""
        task = await self.get_task(task_id)

        # Remove from category if assigned
        if task.category_id:
            category = self.category_repo.get_by_id(task.category_id)
            if category and task_id in category.task_ids:
                category.task_ids.remove(task_id)
                self.category_repo.update(category)

        # Delete task
        if not self.task_repo.delete(task_id):
            raise ValidationError("Failed to delete task")

        self.logger.info(f"Deleted task: {task_id}")

    async def validate_task(self, task: TaskModel) -> None:
        """Validate a task's configuration."""
        # Get template for validation
        template = self.template_repo.get_by_id(task.template_id)
        if not template:
            raise ValidationError(
                f"Template not found: {task.template_id}",
                details={"task_id": task.id}
            )

        # Validate input data against template schema
        for field_name, field_schema in template.input_schema.items():
            if field_schema.required and field_name not in task.input_data:
                raise ValidationError(
                    f"Required input field missing: {field_name}",
                    details={
                        "task_id": task.id,
                        "field": field_name
                    }
                )

        # Validate evaluation weights if provided
        if task.evaluation_weights:
            for criterion in task.evaluation_weights:
                if criterion not in template.evaluation_criteria:
                    raise ValidationError(
                        f"Invalid evaluation criterion: {criterion}",
                        details={
                            "task_id": task.id,
                            "criterion": criterion
                        }
                    )

        # Validate category if assigned
        if task.category_id:
            category = self.category_repo.get_by_id(task.category_id)
            if not category:
                raise ValidationError(
                    f"Category not found: {task.category_id}",
                    details={
                        "task_id": task.id,
                        "category_id": task.category_id
                    }
                )