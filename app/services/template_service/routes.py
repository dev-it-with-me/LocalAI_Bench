"""
API routes for template operations.
"""

from fastapi import APIRouter, Query, status

from app.enums import TemplateTypeEnum
from .schemas import (
    TemplateCreateRequest,
    TemplateResponse,
    TemplatesResponse,
    TemplateUpdateRequest,
)
from .service import TemplateService

template_router = APIRouter(prefix="/templates", tags=["Templates"])
template_service = TemplateService()

@template_router.get("", response_model=TemplatesResponse)
async def list_templates(
    category: None | str = Query(None, title="Filter by template category")
) -> TemplatesResponse:
    """Get all templates, optionally filtered by category."""
    templates = await template_service.list_templates(
        TemplateTypeEnum(category) if category else None
    )
    return TemplatesResponse(
        message="Templates retrieved successfully",
        templates=templates
    )

@template_router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(template: TemplateCreateRequest) -> TemplateResponse:
    """Create a new template."""
    return await template_service.create_template(**template.model_dump())

@template_router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str) -> TemplateResponse:
    """Get a template by ID."""
    return await template_service.get_template(template_id)

@template_router.patch("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template: TemplateUpdateRequest
) -> TemplateResponse:
    """Update a template."""
    return await template_service.update_template(template_id, **template.model_dump())

@template_router.delete("/{template_id}")
async def delete_template(template_id: str) -> dict:
    """Delete a template."""
    await template_service.delete_template(template_id)
    return {"success": True}

@template_router.get("/{template_id}/tasks", response_model=list[dict])
async def get_template_tasks(template_id: str) -> list[dict]:
    """Get all tasks using this template."""
    return await template_service.get_template_tasks(template_id)