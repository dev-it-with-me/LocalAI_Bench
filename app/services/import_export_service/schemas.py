"""
Schemas for the import/export service.
"""

from typing import Any
from pydantic import BaseModel

from app.enums import ImportExportTypeEnum
from app.schemas import BaseResponse

class ExportRequest(BaseModel):
    """Schema for export request."""
    export_type: ImportExportTypeEnum
    entity_ids: list[str]

class ExportResponse(BaseResponse):
    """Schema for export response."""
    export_data: dict[str, Any]
    file_name: str

class ImportRequest(BaseModel):
    """Schema for import request."""
    import_data: dict[str, Any]

class ImportPreviewData(BaseModel):
    """Schema for import preview data."""
    type: str
    id: str
    name: str
    status: str = "new"  # new, update, conflict
    conflicts: None | list[str] = None

class ImportPreviewResponse(BaseResponse):
    """Schema for import preview response."""
    import_type: ImportExportTypeEnum
    entities_to_import: dict[str, list[ImportPreviewData]]
    conflicts: dict[str, list[ImportPreviewData]]

class ImportExecuteRequest(BaseModel):
    """Schema for import execution request."""
    import_data: dict[str, Any]
    conflict_resolution: dict[str, str] = {}  # id -> "skip" | "overwrite" | "rename"

class ImportProgressResponse(BaseResponse):
    """Schema for import progress response."""
    status: str  # "in_progress" | "completed" | "failed"
    progress: float  # 0-100
    entities_processed: int
    total_entities: int
    errors: list[str] = []