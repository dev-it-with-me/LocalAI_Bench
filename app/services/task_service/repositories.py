"""
Repository for task service.
"""

from app.config import settings
from app.services.task_service.models import Task
from app.repositories import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Repository for task operations."""
    
    def __init__(self):
        """Initialize the task repository."""
        directory = settings.data_subdirs()["tasks"]
        super().__init__(directory, Task)
        
    def get_by_category(self, category_id: str) -> list[Task]:
        """Get all tasks for a category."""
        result = []
        for task in self.list_all():
            if task.category_id == category_id:
                result.append(task)
        return result
        
    def get_by_template(self, template_id: str) -> list[Task]:
        """Get all tasks using a template."""
        result = []
        for task in self.list_all():
            if task.template_id == template_id:
                result.append(task)
        return result