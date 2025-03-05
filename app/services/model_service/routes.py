"""
API routes for model operations.
"""

from fastapi import APIRouter, Query, status

from app.enums import ModelTypeEnum
from .schemas import (
    ModelCreateRequest,
    ModelResponse,
    ModelsResponse,
    ModelUpdateRequest,
)
from .service import ModelService

model_router = APIRouter(prefix="/models", tags=["Models"])
model_service = ModelService()

@model_router.get("", response_model=ModelsResponse)
async def list_models(
    type: None | str = Query(None, title="Filter by model type")
) -> ModelsResponse:
    """Get all models, optionally filtered by type."""
    models = await model_service.list_models(
        ModelTypeEnum(type) if type else None
    )
    return ModelsResponse(
        message="Models retrieved successfully",
        models=models
    )

@model_router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(model: ModelCreateRequest) -> ModelResponse:
    """Create a new model."""
    return await model_service.create_model(**model.model_dump())

@model_router.get("/{model_id}", response_model=ModelResponse)
async def get_model(model_id: str) -> ModelResponse:
    """Get a model by ID."""
    return await model_service.get_model(model_id)

@model_router.patch("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: str,
    model: ModelUpdateRequest
) -> ModelResponse:
    """Update a model."""
    return await model_service.update_model(model_id, **model.model_dump())

@model_router.delete("/{model_id}")
async def delete_model(model_id: str) -> dict:
    """Delete a model."""
    await model_service.delete_model(model_id)
    return {"success": True}

@model_router.post("/{model_id}/test")
async def test_model(model_id: str) -> dict:
    """Test model connectivity and functionality."""
    test_result = await model_service.test_model(model_id)
    return {
        "success": test_result["status"] == "success",
        "message": "Model test completed successfully" if test_result["status"] == "success" else test_result["error"]
    }