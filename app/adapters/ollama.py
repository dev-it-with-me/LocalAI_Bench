"""
Ollama model adapter for LocalAI Bench.

This module provides an adapter for interacting with models from Ollama API.
"""

import asyncio
from typing import Any, AsyncIterator, cast
import json

import ollama
from ollama.client import AsyncClient

from app.adapters.base import ModelAdapter, ModelAdapterFactory
from app.config import settings
from app.enums import ModelTypeEnum
from app.exceptions import ModelAdapterError
from app.models import ModelModel


class OllamaAdapter(ModelAdapter[str]):
    """Adapter for Ollama models."""
    
    def __init__(self, model_config: ModelModel):
        """Initialize the Ollama adapter."""
        super().__init__(model_config)
        self.client: AsyncClient | None = None
        self.ollama_host = settings.OLLAMA_HOST
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize the connection to Ollama API."""
        try:
            self.logger.info(f"Initializing connection to Ollama API at {self.ollama_host}")
            
            # Create async client
            self.client = AsyncClient(host=self.ollama_host)
            
            # Check if model exists and is ready
            self.logger.info(f"Checking if model {self.model_config.model_id} is available")
            
            # This will pull the model if it doesn't exist locally
            model_info = await self.client.show(model=self.model_config.model_id)
            self.logger.info(f"Model {self.model_config.model_id} is available: {model_info.digest}")
            
            self.is_initialized = True
            self.logger.info(f"Ollama adapter initialized successfully for model {self.model_config.model_id}")
            
        except Exception as e:
            error_msg = f"Failed to initialize Ollama model {self.model_config.model_id}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id
            )
            
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model."""
        if not self.is_initialized or self.client is None:
            raise ModelAdapterError(
                "Ollama client not initialized. Call initialize() first.",
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id
            )
            
        try:
            # Merge parameters from model config with any overrides
            params = self.model_config.parameters.model_dump()
            params.update(kwargs)
            
            # Remove any None values and extract extra_params
            extra_params = params.pop("extra_params", {})
            params = {k: v for k, v in params.items() if v is not None}
            params.update(extra_params)
            
            # Adapt parameters to Ollama API expectations
            ollama_options = {}
            if "temperature" in params:
                ollama_options["temperature"] = params["temperature"]
            if "top_p" in params:
                ollama_options["top_p"] = params["top_p"]
            if "top_k" in params:
                ollama_options["top_k"] = params["top_k"]
            if "max_tokens" in params:
                ollama_options["num_predict"] = params["max_tokens"]
            if "stop_sequences" in params:
                ollama_options["stop"] = params["stop_sequences"]
                
            # Generate response
            response = await self.client.generate(
                model=self.model_config.model_id,
                prompt=prompt,
                options=ollama_options,
                stream=False
            )
            
            return response.response
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id
            )
            
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Generate a streaming response from the model."""
        if not self.is_initialized or self.client is None:
            raise ModelAdapterError(
                "Ollama client not initialized. Call initialize() first.",
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id
            )
            
        try:
            # Merge parameters from model config with any overrides
            params = self.model_config.parameters.model_dump()
            params.update(kwargs)
            
            # Remove any None values and extract extra_params
            extra_params = params.pop("extra_params", {})
            params = {k: v for k, v in params.items() if v is not None}
            params.update(extra_params)
            
            # Adapt parameters to Ollama API expectations
            ollama_options = {}
            if "temperature" in params:
                ollama_options["temperature"] = params["temperature"]
            if "top_p" in params:
                ollama_options["top_p"] = params["top_p"]
            if "top_k" in params:
                ollama_options["top_k"] = params["top_k"]
            if "max_tokens" in params:
                ollama_options["num_predict"] = params["max_tokens"]
            if "stop_sequences" in params:
                ollama_options["stop"] = params["stop_sequences"]
                
            # Generate stream
            stream = await self.client.generate(
                model=self.model_config.model_id,
                prompt=prompt,
                options=ollama_options,
                stream=True
            )
            
            # Yield each chunk
            async for chunk in stream:
                if chunk.response:
                    yield chunk.response
                    
        except Exception as e:
            error_msg = f"Error generating streaming response: {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id
            )
            
    async def get_token_count(self, text: str) -> int:
        """Get the number of tokens in the text."""
        if not self.is_initialized or self.client is None:
            raise ModelAdapterError(
                "Ollama client not initialized. Call initialize() first.",
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id
            )
            
        try:
            # Use Ollama's tokenize endpoint
            response = await self.client.tokenize(model=self.model_config.model_id, prompt=text)
            return len(response.tokens)
            
        except Exception as e:
            error_msg = f"Error counting tokens: {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id
            )
            
    async def cleanup(self) -> None:
        """Clean up resources used by the model."""
        try:
            # Not much to clean up for Ollama, as resources are managed by the Ollama server
            self.client = None
            self.is_initialized = False
            self.logger.info(f"Cleaned up resources for Ollama model {self.model_config.model_id}")
            
        except Exception as e:
            error_msg = f"Error cleaning up resources: {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.OLLAMA.value,
                model_id=self.model_config.model_id
            )
            
    @classmethod
    def supported_model_type(cls) -> ModelTypeEnum:
        """Return the model type supported by this adapter."""
        return ModelTypeEnum.OLLAMA


# Register the adapter with the factory
ModelAdapterFactory.register_adapter(OllamaAdapter)