"""
Base repository and re-exports for LocalAI Bench application.

This module provides the base repository class for entity operations
and re-exports service-specific repositories.
"""

from typing import Generic, Protocol, Type, TypeVar, cast
from pydantic import BaseModel

# Re-export service repositories
from app.services.benchmark_service.repositories import BenchmarkRunRepository, TaskResultRepository
from app.services.category_service.repositories import CategoryRepository
from app.services.model_service.repositories import ModelRepository
from app.services.task_service.repositories import TaskRepository
from app.services.template_service.repositories import TemplateRepository
from app.utils import JsonFileHandler, get_logger

# Type variable for generic repository, constrained to BaseModel
T = TypeVar("T", bound=BaseModel)

class EntityProtocol(Protocol):
    """Protocol defining required attributes for entities."""
    id: str
    def update_timestamp(self) -> None: ...


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
        result = self.handler.read(entity_id)
        if isinstance(result, dict):
            return self.model_cls.model_validate(result)
        return result
        
    def list_all(self) -> list[T]:
        """List all entities."""
        result = []
        for entity_id in self.handler.list_files():
            entity = self.get_by_id(entity_id)
            if entity:
                result.append(entity)
        return result
        
    def list_ids(self) -> list[str]:
        """List all entity IDs."""
        return self.handler.list_files()
        
    def create(self, entity: T) -> bool:
        """Create a new entity."""
        # Get ID from the entity
        entity_id = cast(EntityProtocol, entity).id
        if self.handler.exists(entity_id):
            self.logger.warning(f"Entity with ID {entity_id} already exists")
            return False
            
        return self.handler.write(entity_id, entity, create_version=False)
        
    def update(self, entity: T) -> bool:
        """Update an existing entity."""
        entity_id = cast(EntityProtocol, entity).id
        if not self.handler.exists(entity_id):
            self.logger.warning(f"Entity with ID {entity_id} does not exist for update")
            return False
            
        # Update the timestamp if supported
        entity_protocol = cast(EntityProtocol, entity)
        if hasattr(entity_protocol, "update_timestamp"):
            entity_protocol.update_timestamp()
            
        return self.handler.write(entity_id, entity)
        
    def delete(self, entity_id: str) -> bool:
        """Delete an entity by ID."""
        return self.handler.delete(entity_id)
        
    def exists(self, entity_id: str) -> bool:
        """Check if an entity with the given ID exists."""
        return self.handler.exists(entity_id)


__all__ = [
    "BaseRepository",
    "BenchmarkRunRepository", 
    "CategoryRepository",
    "ModelRepository",
    "TaskRepository",
    "TaskResultRepository",
    "TemplateRepository",
]