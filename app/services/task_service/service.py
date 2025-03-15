"""
Task service implementation.
"""
from typing import Any

from app.enums import TaskStatusEnum
from app.exceptions import ValidationError
from app.services.task_service.models import Task, InputData, EvaluationWeights
from app.services.category_service.repositories import CategoryRepository
from app.services.task_service.repositories import TaskRepository

from app.utils import get_logger


class TaskService:
    """Service for managing benchmark tasks."""

    def __init__(self):
        """Initialize the task service."""
        self.logger = get_logger("TaskService")
        self.task_repo = TaskRepository()
        self.category_repo = CategoryRepository()

    async def create_task(
        self,
        name: str,
        description: str = "",
        category_id: None | str = None,
        input_data: None | dict[str, Any] = None,
        expected_output: None | str = None,
        evaluation_weights: None | dict[str, float] = None,
        status: TaskStatusEnum = TaskStatusEnum.DRAFT,
    ) -> Task:
        """Create a new task."""
        # Validate category exists if provided
        if category_id:
            category = self.category_repo.get_by_id(category_id)
            if not category:
                raise ValidationError(f"Category not found: {category_id}")
        # Convert dictionaries to Pydantic models
        input_data_model = InputData(**(input_data or {}))
        evaluation_weights_model = EvaluationWeights(**(evaluation_weights or {})) if evaluation_weights else None

        # Create task
        task = Task(
            name=name,
            description=description,
            category_id=category_id or "",  # Using empty string as default per model definition
            input_data=input_data_model,
            expected_output=expected_output,
            evaluation_weights=evaluation_weights_model,
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

    async def get_task(self, task_id: str) -> Task:
        """Get a task by ID."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValidationError(f"Task not found: {task_id}")
        return task

    async def list_tasks(
        self,
        category_id: None | str = None,
        status: None | TaskStatusEnum = None,
    ) -> list[Task]:
        """Get all tasks, optionally filtered by category and/or status."""
        tasks = self.task_repo.list_all()

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
        name: None | str = None,
        description: None | str = None,
        category_id: None | str = None,
        input_data: None | dict[str, Any] = None,
        expected_output: None | str = None,
        evaluation_weights: None | dict[str, float] = None,
        status: None | TaskStatusEnum = None,
    ) -> Task:
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

        # Update fields if provided
        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        if category_id is not None:
            task.category_id = category_id
        if input_data is not None:
            task.input_data = InputData(**input_data)
        if expected_output is not None:
            task.expected_output = expected_output
        if evaluation_weights is not None:
            task.evaluation_weights = EvaluationWeights(**evaluation_weights)
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

    async def validate_task(self, task: Task) -> None:
        """Validate a task's configuration."""

        # Validate category if assigned
        if task.category_id:
            category = self.category_repo.get_by_id(task.category_id)
            if not category:
                raise ValidationError(
                    f"Category not found: {task.category_id}"
                )