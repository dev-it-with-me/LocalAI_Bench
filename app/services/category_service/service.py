"""
Category service implementation.
"""

from typing import List, Optional

from app.exceptions import ValidationError
from app.models import CategoryModel, TaskModel
from app.repositories import CategoryRepository, TaskRepository
from app.utils import get_logger


class CategoryService:
    """Service for managing benchmark categories."""

    def __init__(self):
        """Initialize the category service."""
        self.logger = get_logger("CategoryService")
        self.category_repo = CategoryRepository()
        self.task_repo = TaskRepository()

    async def create_category(
        self,
        name: str,
        description: str = "",
        time_weight: float = 1.0,
        quality_weight: float = 1.0,
        complexity_weight: float = 1.0,
        cost_weight: float = 1.0,
        memory_weight: float = 1.0,
    ) -> CategoryModel:
        """Create a new category."""
        category = CategoryModel(
            name=name,
            description=description,
            time_weight=time_weight,
            quality_weight=quality_weight,
            complexity_weight=complexity_weight,
            cost_weight=cost_weight,
            memory_weight=memory_weight,
            task_ids=[]
        )

        if self.category_repo.create(category):
            self.logger.info(f"Created category: {category.id}")
            return category
        else:
            raise ValidationError("Failed to create category")

    async def get_category(self, category_id: str) -> CategoryModel:
        """Get a category by ID."""
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise ValidationError(f"Category not found: {category_id}")
        return category

    async def list_categories(self) -> List[CategoryModel]:
        """Get all categories."""
        return self.category_repo.get_all()

    async def update_category(
        self,
        category_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        time_weight: Optional[float] = None,
        quality_weight: Optional[float] = None,
        complexity_weight: Optional[float] = None,
        cost_weight: Optional[float] = None,
        memory_weight: Optional[float] = None,
    ) -> CategoryModel:
        """Update a category."""
        category = await self.get_category(category_id)

        # Update fields if provided
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        if time_weight is not None:
            category.time_weight = time_weight
        if quality_weight is not None:
            category.quality_weight = quality_weight
        if complexity_weight is not None:
            category.complexity_weight = complexity_weight
        if cost_weight is not None:
            category.cost_weight = cost_weight
        if memory_weight is not None:
            category.memory_weight = memory_weight

        if self.category_repo.update(category):
            self.logger.info(f"Updated category: {category_id}")
            return category
        else:
            raise ValidationError("Failed to update category")

    async def delete_category(self, category_id: str) -> None:
        """Delete a category."""
        category = await self.get_category(category_id)

        # Check if category has tasks
        if category.task_ids:
            raise ValidationError(
                f"Cannot delete category with tasks: {category_id}",
                details={"task_count": len(category.task_ids)}
            )

        # Delete category
        if not self.category_repo.delete(category_id):
            raise ValidationError("Failed to delete category")

        self.logger.info(f"Deleted category: {category_id}")

    async def get_category_tasks(self, category_id: str) -> List[TaskModel]:
        """Get all tasks in a category."""
        category = await self.get_category(category_id)

        tasks = []
        for task_id in category.task_ids:
            task = self.task_repo.get_by_id(task_id)
            if task:
                tasks.append(task)

        return tasks

    async def add_task_to_category(
        self, category_id: str, task_id: str
    ) -> CategoryModel:
        """Add a task to a category."""
        category = await self.get_category(category_id)

        # Check if task exists
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValidationError(f"Task not found: {task_id}")

        # Check if task already in category
        if task_id in category.task_ids:
            raise ValidationError(
                f"Task already in category: {task_id}",
                details={
                    "category_id": category_id,
                    "task_id": task_id
                }
            )

        # Add task to category
        category.task_ids.append(task_id)

        if self.category_repo.update(category):
            self.logger.info(f"Added task {task_id} to category {category_id}")
            return category
        else:
            raise ValidationError("Failed to update category")

    async def remove_task_from_category(
        self, category_id: str, task_id: str
    ) -> CategoryModel:
        """Remove a task from a category."""
        category = await self.get_category(category_id)

        # Check if task in category
        if task_id not in category.task_ids:
            raise ValidationError(
                f"Task not in category: {task_id}",
                details={
                    "category_id": category_id,
                    "task_id": task_id
                }
            )

        # Remove task from category
        category.task_ids.remove(task_id)

        if self.category_repo.update(category):
            self.logger.info(f"Removed task {task_id} from category {category_id}")
            return category
        else:
            raise ValidationError("Failed to update category")