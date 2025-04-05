"""
API routes for task operations.
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.enums import TaskStatusEnum
from .schemas import (
    TaskCreateRequest,
    TaskResponse,
    TaskUpdateRequest,
)
from .service import TaskService

task_router = APIRouter(prefix="/tasks", tags=["Tasks"])
task_service = TaskService()

@task_router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreateRequest) -> TaskResponse:
    """Create a new task."""
    try:
        task_model = await task_service.create_task(**task.model_dump())
        return TaskResponse(**task_model.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@task_router.get("", response_model=list[TaskResponse])
async def list_tasks(
    category_id: None | str = Query(None),
    status: None | TaskStatusEnum = Query(None),
) -> list[TaskResponse]:
    """Get all tasks, optionally filtered by category and/or status."""
    try:
        tasks = await task_service.list_tasks(category_id=category_id, status=status)
        return [TaskResponse(**task.model_dump()) for task in tasks]
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    """Get a task by ID."""
    try:
        task = await task_service.get_task(task_id)
        return TaskResponse(**task.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

@task_router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskUpdateRequest) -> TaskResponse:
    """Update a task."""
    try:
        updated_task = await task_service.update_task(task_id, **task.model_dump(mode="json"))
        return TaskResponse(**updated_task.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@task_router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(task_id: str) -> dict[str, bool]:
    """Delete a task."""
    try:
        await task_service.delete_task(task_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )