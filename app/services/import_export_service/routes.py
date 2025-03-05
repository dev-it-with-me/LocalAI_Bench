"""
API routes for import/export operations.
"""

from datetime import datetime
from fastapi import APIRouter

from .schemas import (
    ExportRequest,
    ExportResponse,
    ImportPreviewResponse,
    ImportRequest,
    ImportExecuteRequest,
    ImportProgressResponse,
)
from .service import ImportExportService

import_export_router = APIRouter(prefix="/import-export", tags=["Import/Export"])
import_export_service = ImportExportService()

@import_export_router.post("/export", response_model=ExportResponse)
async def export_data(export_request: ExportRequest) -> ExportResponse:
    """Export data based on the specified export type and entity IDs."""
    export_data = await import_export_service.export_data(
        export_type=export_request.export_type,
        entity_ids=export_request.entity_ids
    )
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"localai_bench_{export_request.export_type.value}_{timestamp}.json"
    
    return ExportResponse(
        message="Data exported successfully",
        export_data=export_data,
        file_name=file_name
    )

@import_export_router.post("/import/preview", response_model=ImportPreviewResponse)
async def preview_import(import_request: ImportRequest) -> ImportPreviewResponse:
    """Preview data import to check for conflicts."""
    preview_data = await import_export_service.preview_import(import_request.import_data)
    return ImportPreviewResponse(
        message="Import preview completed",
        **preview_data
    )

@import_export_router.post("/import", response_model=ImportProgressResponse)
async def import_data(import_request: ImportExecuteRequest) -> ImportProgressResponse:
    """Import data with conflict resolution."""
    await import_export_service.import_data(
        import_data=import_request.import_data,
        conflict_resolution=import_request.conflict_resolution
    )
    return ImportProgressResponse(
        message="Data imported successfully",
        status="completed",
        progress=100.0,
        entities_processed=len(import_request.import_data),
        total_entities=len(import_request.import_data)
    )