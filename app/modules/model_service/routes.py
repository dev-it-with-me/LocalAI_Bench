"""
API routes for model operations.
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.enums import ModelTypeEnum
from app.exceptions import ValidationError, ModelTestError
from .schemas import (
    ModelCreateRequest,
    ModelResponse,
    ModelsResponse,
    ModelUpdateRequest,
    ModelParametersSchema,
)
from .service import ModelService
from .models import Model

model_router = APIRouter(prefix="/models", tags=["Models"])
model_service = ModelService()

def model_to_response(model: Model) -> ModelResponse:
    """Convert Model to ModelResponse."""
    return ModelResponse(
        id=model.id,
        name=model.name,
        type=model.type,
        description=model.description,
        model_id=model.model_id,
        api_url=model.api_url,
        api_version=model.api_version,
        parameters=ModelParametersSchema(**model.parameters.model_dump()),
        memory_required=model.memory_required,
        gpu_required=model.gpu_required,
        quantization=model.quantization,
        created_at=model.created_at,
        updated_at=model.updated_at
    )

@model_router.get(
    "",
    response_model=ModelsResponse,
    responses={
        500: {"description": "Internal server error"},
    }
)
async def list_models(
    type: None | str = Query(None, title="Filter by model type", description="Filter models by their type")
) -> ModelsResponse:
    """Get all models, optionally filtered by type."""
    try:
        models = await model_service.list_models(
            ModelTypeEnum(type) if type else None
        )
        return ModelsResponse(
            message="Models retrieved successfully",
            models=[model_to_response(m) for m in models]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid model type: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@model_router.post(
    "",
    response_model=ModelResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    }
)
async def create_model(model: ModelCreateRequest) -> ModelResponse:
    """Create a new model."""
    try:
        created = await model_service.create_model(**model.model_dump())
        return model_to_response(created)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@model_router.get(
    "/{model_id}",
    response_model=ModelResponse,
    responses={
        404: {"description": "Model not found"},
        500: {"description": "Internal server error"},
    }
)
async def get_model(model_id: str) -> ModelResponse:
    """Get a model by ID."""
    try:
        model = await model_service.get_model(model_id)
        return model_to_response(model)
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@model_router.patch(
    "/{model_id}",
    response_model=ModelResponse,
    responses={
        404: {"description": "Model not found"},
        400: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    }
)
async def update_model(
    model_id: str,
    model: ModelUpdateRequest
) -> ModelResponse:
    """Update a model."""
    try:
        updated = await model_service.update_model(model_id, **model.model_dump())
        return model_to_response(updated)
    except ValidationError as e:
        raise HTTPException(
            status_code=404 if "not found" in str(e) else 400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@model_router.delete(
    "/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Model not found"},
        500: {"description": "Internal server error"},
    }
)
async def delete_model(model_id: str) -> None:
    """Delete a model."""
    try:
        await model_service.delete_model(model_id)
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@model_router.post(
    "/{model_id}/test",
    responses={
        404: {"description": "Model not found"},
        500: {"description": "Model test failed"},
    }
)
async def test_model(model_id: str) -> dict:
    """Test model connectivity and functionality."""
    try:
        test_result = await model_service.test_model(model_id)
        return test_result
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ModelTestError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))