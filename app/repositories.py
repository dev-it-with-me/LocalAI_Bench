"""
Repository classes for data access in LocalAI Bench application.

This module provides repository classes that handle CRUD operations
for various entity types using JSON file storage.
"""

import os
from typing import Any, Generic, Type, TypeVar

from app.config import settings
from app.models import (
    BenchmarkRunModel,
    CategoryModel,
    ModelModel,
    TaskModel,
    TaskResultModel,
    TemplateModel,
)
from app.utils import JsonFileHandler, get_logger

# Type variable for generic repository
T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository class for entity operations."""

    def __init__(self, directory: str, model_cls: Type[T]):
        """Initialize the repository.
        
        Args:
            directory: Directory where entity files are stored
            model_cls: Pydantic model class for the entity
        """
        self.handler = JsonFileHandler(directory, model_cls)
        self.model_cls = model_cls
        self.logger = get_logger(f"Repository:{model_cls.__name__}")
        
    def get_by_id(self, entity_id: str) -> T | None:
        """Get an entity by ID."""
        return self.handler.read(entity_id)
        
    def list_all(self) -> list[T]:
        """List all entities."""
        result = []
        for entity_id in self.handler.list_files():
            entity = self.handler.read(entity_id)
            if entity:
                result.append(entity)
        return result
        
    def list_ids(self) -> list[str]:
        """List all entity IDs."""
        return self.handler.list_files()
        
    def create(self, entity: T) -> bool:
        """Create a new entity."""
        # Get ID from the entity
        entity_id = getattr(entity, "id")
        if self.handler.exists(entity_id):
            self.logger.warning(f"Entity with ID {entity_id} already exists")
            return False
            
        return self.handler.write(entity_id, entity, create_version=False)
        
    def update(self, entity: T) -> bool:
        """Update an existing entity."""
        entity_id = getattr(entity, "id")
        if not self.handler.exists(entity_id):
            self.logger.warning(f"Entity with ID {entity_id} does not exist for update")
            return False
            
        # Update the timestamp
        if hasattr(entity, "update_timestamp"):
            entity.update_timestamp()
            
        return self.handler.write(entity_id, entity)
        
    def delete(self, entity_id: str) -> bool:
        """Delete an entity by ID."""
        return self.handler.delete(entity_id)
        
    def exists(self, entity_id: str) -> bool:
        """Check if an entity with the given ID exists."""
        return self.handler.exists(entity_id)


class CategoryRepository(BaseRepository[CategoryModel]):
    """Repository for category operations."""
    
    def __init__(self):
        """Initialize the category repository."""
        directory = settings.data_subdirs["categories"]
        super().__init__(directory, CategoryModel)
        
    def get_with_tasks(self, category_id: str) -> tuple[CategoryModel | None, list[TaskModel]]:
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


class TaskRepository(BaseRepository[TaskModel]):
    """Repository for task operations."""
    
    def __init__(self):
        """Initialize the task repository."""
        directory = settings.data_subdirs["tasks"]
        super().__init__(directory, TaskModel)
        
    def get_by_category(self, category_id: str) -> list[TaskModel]:
        """Get all tasks for a category."""
        result = []
        for task in self.list_all():
            if task.category_id == category_id:
                result.append(task)
        return result
        
    def get_by_template(self, template_id: str) -> list[TaskModel]:
        """Get all tasks using a template."""
        result = []
        for task in self.list_all():
            if task.template_id == template_id:
                result.append(task)
        return result


class TemplateRepository(BaseRepository[TemplateModel]):
    """Repository for template operations."""
    
    def __init__(self):
        """Initialize the template repository."""
        directory = settings.data_subdirs["templates"]
        super().__init__(directory, TemplateModel)
        
    def get_by_category(self, category: str) -> list[TemplateModel]:
        """Get all templates for a category."""
        result = []
        for template in self.list_all():
            if template.category.value == category:
                result.append(template)
        return result


class ModelRepository(BaseRepository[ModelModel]):
    """Repository for model operations."""
    
    def __init__(self):
        """Initialize the model repository."""
        directory = settings.data_subdirs["models"]
        super().__init__(directory, ModelModel)
        
    def get_by_type(self, model_type: str) -> list[ModelModel]:
        """Get all models of a specific type."""
        result = []
        for model in self.list_all():
            if model.type.value == model_type:
                result.append(model)
        return result


class TaskResultRepository(BaseRepository[TaskResultModel]):
    """Repository for task result operations."""
    
    def __init__(self):
        """Initialize the task result repository."""
        directory = os.path.join(settings.data_subdirs["results"], "task_results")
        os.makedirs(directory, exist_ok=True)
        super().__init__(directory, TaskResultModel)
        
    def get_by_task(self, task_id: str) -> list[TaskResultModel]:
        """Get all results for a task."""
        result = []
        for task_result in self.list_all():
            if task_result.task_id == task_id:
                result.append(task_result)
        return result
        
    def get_by_model(self, model_id: str) -> list[TaskResultModel]:
        """Get all results for a model."""
        result = []
        for task_result in self.list_all():
            if task_result.model_id == model_id:
                result.append(task_result)
        return result
        
    def get_by_benchmark_run(self, benchmark_run_id: str) -> list[TaskResultModel]:
        """Get all results for a benchmark run."""
        result = []
        for task_result in self.list_all():
            if task_result.benchmark_run_id == benchmark_run_id:
                result.append(task_result)
        return result


class BenchmarkRunRepository(BaseRepository[BenchmarkRunModel]):
    """Repository for benchmark run operations."""
    
    def __init__(self):
        """Initialize the benchmark run repository."""
        directory = os.path.join(settings.data_subdirs["results"], "benchmark_runs")
        os.makedirs(directory, exist_ok=True)
        super().__init__(directory, BenchmarkRunModel)
        
    def get_with_results(self, benchmark_run_id: str) -> tuple[BenchmarkRunModel | None, list[TaskResultModel]]:
        """Get a benchmark run with its task results."""
        benchmark_run = self.get_by_id(benchmark_run_id)
        if not benchmark_run:
            return None, []
            
        task_result_repo = TaskResultRepository()
        return benchmark_run, task_result_repo.get_by_benchmark_run(benchmark_run_id)