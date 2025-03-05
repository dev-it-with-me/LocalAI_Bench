"""
API routes for task operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.enums import TaskStatusEnum
from .schemas import (
    TaskCreateRequest,
    TaskResponse,
    TasksResponse,
    TaskUpdateRequest,
)
from .service import TaskService

task_router = APIRouter(prefix="/tasks", tags=["Tasks"])
task_service = TaskService()

@task_router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreateRequest) -> TaskResponse:
    """Create a new task."""
    return await task_service.create_task(**task.model_dump())

@task_router.get("", response_model=TasksResponse)
async def list_tasks(
    category_id: None |str = Query(None),
    status: None |TaskStatusEnum = Query(None),
) -> TasksResponse:
    """Get all tasks, optionally filtered by category and/or status."""
    tasks = await task_service.list_tasks(category_id=category_id, status=status)
    return TasksResponse(tasks=tasks)

@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    """Get a task by ID."""
    return await task_service.get_task(task_id)

@task_router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskUpdateRequest) -> TaskResponse:
    """Update a task."""
    return await task_service.update_task(task_id, **task.model_dump())

@task_router.delete("/{task_id}")
async def delete_task(task_id: str) -> dict:
    """Delete a task."""
    await task_service.delete_task(task_id)
    return {"success": True}