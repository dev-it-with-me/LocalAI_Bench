"""
Data models for import/export service.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from app.enums import ImportExportTypeEnum


class Export(BaseModel):
    """Model for exported data."""
    export_type: ImportExportTypeEnum
    export_date: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"
    content: dict[str, Any]  # Type depends on export_type


class ImportPreview(BaseModel):
    """Model for import preview data."""
    type: str
    id: str
    name: str
    status: str = "new"  # new, update, conflict
    conflicts: list[str] | None = None