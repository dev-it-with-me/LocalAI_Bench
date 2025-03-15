# OllamaAdapter (Subclass)
import asyncio
from typing import Any
from collections.abc import AsyncIterator

from pydantic import BaseModel, Field

from app.adapters.base import ModelAdapter, ModelAdapterFactory  # Import corrected base class and factory
from app.config import settings
from app.enums import ModelTypeEnum
from app.exceptions import ModelAdapterError
from app.services.model_service.models import Model
from ollama import AsyncClient


class OllamaParams(BaseModel):
    """
    Parameters for Ollama API calls.
    """

    temperature: float | None = Field(None, description="The temperature of the model.")
    top_p: float | None = Field(None, description="Top-p (nucleus) sampling.")
    top_k: int | None = Field(None, description="Top-k sampling.")
    max_tokens: int | None = Field(None, alias="num_predict", description="Maximum number of tokens to generate.")
    stop_sequences: list[str] | None = Field(None, alias="stop", description="Sequences at which to stop generation.")
    extra_params: dict[str, Any] = Field(default_factory=dict, description="Additional, non-standard parameters.")


class OllamaAdapter(ModelAdapter[str]):
    """Adapter for Ollama models."""

    def __init__(self, model_config: Model):
        """Initialize the Ollama adapter."""
        super().__init__(model_config)
        self.client: AsyncClient | None = None
        self.ollama_host = settings.OLLAMA_HOST

    async def initialize(self) -> None:
        """Initialize the connection to Ollama API."""
        try:
            self.logger.info(f"Initializing connection to Ollama API at {self.ollama_host}")
            self.client = AsyncClient(host=self.ollama_host)
            self.logger.info(f"Checking if model {self.model_config.model_id} is available")
            model_info = await self.client.show(model=self.model_config.model_id)
            self.logger.info(f"Model {self.model_config.model_id} is available: {model_info['digest']}")

        except Exception as e:
            error_msg = f"Failed to initialize Ollama model {self.model_config.model_id}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id,
            ) from e

    async def _get_ollama_params(self, **kwargs) -> dict:
        """
        Consolidates and prepares parameters for Ollama API calls.
        """
        params = OllamaParams(**self.model_config.parameters.model_dump(), **kwargs)
        ollama_options = params.model_dump(exclude_none=True, by_alias=True)
        ollama_options.update(ollama_options.pop("extra_params", {}))  # Flatten extra_params
        return ollama_options

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model."""
        if self.client is None:
            raise ModelAdapterError(
                "Ollama client not initialized. Call initialize() first.",
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id,
            )

        try:
            ollama_options = await self._get_ollama_params(**kwargs)
            response = await self.client.generate(
                model=self.model_config.model_id,
                prompt=prompt,
                options=ollama_options,
                stream=False,
            )
            return response["response"]

        except Exception as e:
            error_msg = f"Error generating response for prompt '{prompt}': {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id,
            ) from e

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Generate a streaming response from the model."""
        if self.client is None:
            raise ModelAdapterError(
                "Ollama client not initialized. Call initialize() first.",
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id,
            )

        try:
            ollama_options = await self._get_ollama_params(**kwargs)
            stream = await self.client.generate(
                model=self.model_config.model_id,
                prompt=prompt,
                options=ollama_options,
                stream=True,
            )

            async for chunk in stream:
                if "response" in chunk:
                    yield chunk["response"]

        except Exception as e:
            error_msg = f"Error generating streaming response for prompt '{prompt}': {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id,
            ) from e

    async def get_token_count(self, text: str) -> int:
        """Get the number of tokens in the text."""
        # Ollama doesn't support token counting directly
        # This is a placeholder that returns an approximate count
        return len(text.split())

    def get_statistics(self) -> dict[str, Any]:
        """Get model statistics."""
        return {
            "type": self.model_config.type.value,
            "model_id": self.model_config.model_id,
            "initialized": self.client is not None
        }

    async def cleanup(self) -> None:
        """Clean up resources used by the model."""
        try:
            if self.client:
                # Assuming AsyncClient has a close method.  Check the ollama library docs.
                # await self.client.close()
                self.client = None
            self.logger.info(f"Cleaned up resources for Ollama model {self.model_config.model_id}")

        except Exception as e:
            error_msg = f"Error cleaning up resources: {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id,
            ) from e

    @classmethod
    async def check_model_availability(cls, model_id: str, host: str | None = None) -> bool:
        """Check if a model is available on the Ollama instance."""
        try:
            host = host or settings.OLLAMA_HOST
            client = AsyncClient(host=host)
            await client.show(model=model_id)
            return True
        except Exception:
            return False

    @classmethod
    def supported_model_type(cls) -> ModelTypeEnum:
        """Return the model type supported by this adapter."""
        return ModelTypeEnum.OLLAMA


ModelAdapterFactory.register_adapter(OllamaAdapter) # Register adapter