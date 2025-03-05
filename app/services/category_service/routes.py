"""
API routes for category operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from .schemas import (
    CategoriesResponse,
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)
from .service import CategoryService

category_router = APIRouter(prefix="/categories", tags=["Categories"])
category_service = CategoryService()

@category_router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreateRequest) -> CategoryResponse:
    """Create a new category."""
    return await category_service.create_category(**category.model_dump())

@category_router.get("", response_model=CategoriesResponse)
async def list_categories() -> CategoriesResponse:
    """Get all categories."""
    categories = await category_service.list_categories()
    return CategoriesResponse(categories=categories)

@category_router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str) -> CategoryResponse:
    """Get a category by ID."""
    return await category_service.get_category(category_id)

@category_router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str, category: CategoryUpdateRequest
) -> CategoryResponse:
    """Update a category."""
    return await category_service.update_category(category_id, **category.model_dump())

@category_router.delete("/{category_id}")
async def delete_category(category_id: str) -> dict:
    """Delete a category."""
    await category_service.delete_category(category_id)
    return {"success": True}

@category_router.post("/{category_id}/tasks/{task_id}", response_model=CategoryResponse)
async def add_task_to_category(category_id: str, task_id: str) -> CategoryResponse:
    """Add a task to a category."""
    return await category_service.add_task_to_category(category_id, task_id)

@category_router.delete("/{category_id}/tasks/{task_id}", response_model=CategoryResponse)
async def remove_task_from_category(category_id: str, task_id: str) -> CategoryResponse:
    """Remove a task from a category."""
    return await category_service.remove_task_from_category(category_id, task_id)

@category_router.get("/{category_id}/tasks", response_model=list[dict])
async def get_category_tasks(category_id: str) -> list[dict]:
    """Get all tasks in a category."""
    return await category_service.get_category_tasks(category_id)