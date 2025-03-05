"""
Model service implementation.
"""

from typing import Any

from app.adapters.base import ModelAdapterFactory
from app.enums import ModelTypeEnum
from app.exceptions import ValidationError, ModelTestError
from app.services.model_service.repositories import ModelRepository
from app.utils import get_logger
from app.services.model_service.schemas import ModelParametersSchema

from app.services.model_service.models import Model


class ModelService:
    """Service for managing AI models."""

    def __init__(self):
        """Initialize the model service."""
        self.logger = get_logger("ModelService")
        self.model_repo = ModelRepository()
        self.model_factory = ModelAdapterFactory()

    async def create_model(
        self,
        name: str,
        type: ModelTypeEnum,
        model_id: str,
        description: str = "",
        api_url: str | None = None,
        api_key: str | None = None,
        api_version: str | None = None,
        parameters: None | dict[str, Any] = None,
        memory_required: None | float = None,
        gpu_required: bool = False,
        quantization: None | str = None,
    ) -> Model:
        """Create a new model."""
        model = Model(
            name=name,
            type=type,
            model_id=model_id,
            description=description,
            api_url=api_url,
            api_key=api_key,
            api_version=api_version,
            parameters=ModelParametersSchema(**(parameters or {})),
            memory_required=memory_required,
            gpu_required=gpu_required,
            quantization=quantization
        )
        
        if self.model_repo.create(model):
            self.logger.info(f"Created model: {model.id}")
            return model
        else:
            raise ValidationError("Failed to create model")

    async def get_model(self, model_id: str) -> Model:
        """Get a model by ID."""
        model = self.model_repo.get_by_id(model_id)
        if not model:
            raise ValidationError(f"Model not found: {model_id}")
        return model

    async def list_models(self, type: None |ModelTypeEnum = None) -> list[Model]:
        """Get all models, optionally filtered by type."""
        models = self.model_repo.list_all()
        if type:
            models = [m for m in models if m.type == type]
        return models

    async def update_model(
        self,
        model_id: str,
        name: None |str = None,
        description: None |str = None,
        api_url: None |str = None,
        api_key: None |str = None,
        api_version: None |str = None,
        parameters: None |dict[str, Any] = None,
        memory_required: None |float = None,
        gpu_required: bool = False,
        quantization: None |str = None,
    ) -> Model:
        """Update a model."""
        model = await self.get_model(model_id)
        
        # Update fields if provided
        if name is not None:
            model.name = name
        if description is not None:
            model.description = description
        if api_url is not None:
            model.api_url = api_url
        if api_key is not None:
            model.api_key = api_key
        if api_version is not None:
            model.api_version = api_version
        if parameters is not None:
            model.parameters = ModelParametersSchema(**parameters)
        if memory_required is not None:
            model.memory_required = memory_required
        if gpu_required is not None:
            model.gpu_required = gpu_required
        if quantization is not None:
            model.quantization = quantization
            
        if self.model_repo.update(model):
            self.logger.info(f"Updated model: {model_id}")
            return model
        else:
            raise ValidationError("Failed to update model")

    async def delete_model(self, model_id: str) -> None:
        """Delete a model."""
        # Check if model exists
        await self.get_model(model_id)
        
        # Delete model
        if not self.model_repo.delete(model_id):
            raise ValidationError("Failed to delete model")
            
        self.logger.info(f"Deleted model: {model_id}")

    async def test_model(self, model_id: str) -> dict[str, Any]:
        """Test model connectivity and functionality."""
        model = await self.get_model(model_id)
        
        try:
            # Create adapter and test basic functionality
            adapter = self.model_factory.create_adapter(model)
            await adapter.initialize()
            
            # Run a simple test prompt
            test_prompt = "Test prompt for model verification."
            test_result = await adapter.generate(test_prompt)
            
            return {
                "status": "success",
                "model_id": model_id,
                "test_output": test_result,
                "statistics": adapter.get_statistics()
            }
            
        except Exception as e:
            raise ModelTestError(
                f"Model test failed: {str(e)}",
                model_id=model_id
            )