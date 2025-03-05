"""
Service for import/export operations.
"""

from typing import Any

from app.enums import ImportExportTypeEnum
from app.exceptions import ImportConflictError
from app.services.category_service.repositories import CategoryRepository
from app.services.model_service.repositories import ModelRepository
from app.services.task_service.repositories import TaskRepository
from app.services.template_service.repositories import TemplateRepository

class ImportExportService:
    """Service for import/export operations."""

    def __init__(self) -> None:
        """Initialize the import/export service."""
        self.category_repository = CategoryRepository()
        self.model_repository = ModelRepository()
        self.task_repository = TaskRepository()
        self.template_repository = TemplateRepository()

    async def export_data(
        self, export_type: ImportExportTypeEnum, entity_ids: list[str]
    ) -> dict[str, Any]:
        """Export data based on type and entity IDs."""
        repository = self._get_repository(export_type)
        entities = []
        
        for entity_id in entity_ids:
            entity = await repository.get(entity_id)
            if entity:
                entities.append(entity.model_dump())

        return {
            "type": export_type.value,
            "version": "1.0",
            "entities": entities
        }

    async def preview_import(self, import_data: dict[str, Any]) -> dict[str, Any]:
        """Preview import data and detect conflicts."""
        import_type = ImportExportTypeEnum(import_data["type"])
        repository = self._get_repository(import_type)
        entities_to_import = []
        conflicts = []

        for entity in import_data["entities"]:
            existing = await repository.get(entity["id"])
            if existing:
                conflicts.append({
                    "type": import_type.value,
                    "id": entity["id"],
                    "name": entity["name"],
                    "status": "conflict"
                })
            else:
                entities_to_import.append({
                    "type": import_type.value,
                    "id": entity["id"],
                    "name": entity["name"],
                    "status": "new"
                })

        return {
            "import_type": import_type,
            "entities_to_import": {import_type.value: entities_to_import},
            "conflicts": {import_type.value: conflicts}
        }

    async def import_data(
        self, 
        import_data: dict[str, Any],
        conflict_resolution: dict[str, str]
    ) -> None:
        """Import data with conflict resolution."""
        import_type = ImportExportTypeEnum(import_data["type"])
        repository = self._get_repository(import_type)

        for entity in import_data["entities"]:
            entity_id = entity["id"]
            resolution = conflict_resolution.get(entity_id, "error")
            
            existing = await repository.get(entity_id)
            if existing:
                if resolution == "skip":
                    continue
                elif resolution == "overwrite":
                    await repository.save(entity)
                elif resolution == "rename":
                    entity["id"] = f"{entity_id}_imported"
                    await repository.save(entity)
                else:
                    raise ImportConflictError(
                        f"Conflict detected for {entity_id} and no valid resolution provided"
                    )
            else:
                await repository.save(entity)

    def _get_repository(self, type: ImportExportTypeEnum) -> Any:
        """Get the appropriate repository for the given type."""
        repositories = {
            ImportExportTypeEnum.CATEGORY: self.category_repository,
            ImportExportTypeEnum.MODEL: self.model_repository,
            ImportExportTypeEnum.TASK_SET: self.task_repository,
            ImportExportTypeEnum.TEMPLATE: self.template_repository,
        }
        return repositories[type]