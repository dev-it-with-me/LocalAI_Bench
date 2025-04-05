"""
Repository for model service.
"""

from app.config import settings
from app.modules.model_service.models import Model
from app.repositories import BaseRepository


class ModelRepository(BaseRepository[Model]):
    """Repository for model operations."""

    def __init__(self):
        """Initialize the model repository."""
        directory = settings.data_subdirs()["models"]
        super().__init__(directory, Model)

    def get_by_type(self, model_type: str) -> list[Model]:
        """Get all models of a specific type."""
        result = []
        for model in self.list_all():
            if model.type.value == model_type:
                result.append(model)
        return result
