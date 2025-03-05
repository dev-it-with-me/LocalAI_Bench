"""
Repository for category service.
"""

from app.config import settings
from app.services.task_service.models import Task
from app.services.category_service.models import Category
from app.repositories import BaseRepository
from app.repositories import TaskRepository


class CategoryRepository(BaseRepository[Category]):
    """Repository for category operations."""
    
    def __init__(self):
        """Initialize the category repository."""
        directory = settings.data_subdirs()["categories"]
        super().__init__(directory, Category)
        
    def get_with_tasks(self, category_id: str) -> tuple[Category | None, list[Task]]:
        """Get a category with its tasks."""
        category = self.get_by_id(category_id)
        if not category:
            return None, []
            
        task_repo = TaskRepository()
        tasks = []
        for task_id in category.task_ids:
            task = task_repo.get_by_id(task_id)
            if task:
                tasks.append(task)
                
        return category, tasks
        
    def add_task(self, category_id: str, task_id: str) -> bool:
        """Add a task to a category."""
        category = self.get_by_id(category_id)
        if not category:
            return False
            
        # Check if task exists
        task_repo = TaskRepository()
        if not task_repo.exists(task_id):
            return False
            
        # Add task ID if not already in the category
        if task_id not in category.task_ids:
            category.task_ids.append(task_id)
            return self.update(category)
            
        return True
        
    def remove_task(self, category_id: str, task_id: str) -> bool:
        """Remove a task from a category."""
        category = self.get_by_id(category_id)
        if not category:
            return False
            
        # Remove task ID if present
        if task_id in category.task_ids:
            category.task_ids.remove(task_id)
            return self.update(category)
            
        return True