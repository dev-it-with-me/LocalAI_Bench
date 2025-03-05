"""
Hugging Face model adapter for LocalAI Bench.

This module provides an adapter for interacting with models from the Hugging Face Hub.
"""

import asyncio
from typing import Any, AsyncIterator

import torch
from huggingface_hub import HfApi
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    TextIteratorStreamer,
)

from app.adapters.base import ModelAdapter, ModelAdapterFactory
from app.config import settings
from app.enums import ModelTypeEnum
from app.exceptions import ModelAdapterError
from app.models import ModelModel


class HuggingFaceAdapter(ModelAdapter[str]):
    """Adapter for Hugging Face models."""
    
    def __init__(self, model_config: ModelModel):
        """Initialize the Hugging Face adapter."""
        super().__init__(model_config)
        self.tokenizer: PreTrainedTokenizer | None = None
        self.model: PreTrainedModel | None = None
        self.device = "cuda" if torch.cuda.is_available() and model_config.gpu_required else "cpu"
        self.api = HfApi(token=settings.HUGGINGFACE_API_TOKEN)
        
    async def initialize(self) -> None:
        """Initialize the model and tokenizer."""
        try:
            # Run in a thread to avoid blocking the event loop
            self.logger.info(f"Initializing model {self.model_config.model_id} on {self.device}")
            
            # Apply quantization if specified
            kwargs = {}
            if self.model_config.quantization:
                if self.model_config.quantization == "int8":
                    kwargs["load_in_8bit"] = True
                elif self.model_config.quantization == "int4":
                    kwargs["load_in_4bit"] = True
                elif self.model_config.quantization == "fp16":
                    kwargs["torch_dtype"] = torch.float16
            
            # Load model and tokenizer
            loop = asyncio.get_event_loop()
            self.tokenizer = await loop.run_in_executor(
                None, 
                lambda: AutoTokenizer.from_pretrained(self.model_config.model_id)
            )
            
            self.model = await loop.run_in_executor(
                None,
                lambda: AutoModelForCausalLM.from_pretrained(
                    self.model_config.model_id, 
                    device_map=self.device,
                    **kwargs
                )
            )
            
            self.logger.info(f"Model {self.model_config.model_id} initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize Hugging Face model {self.model_config.model_id}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.HUGGINGFACE.value,
                model_id=self.model_config.model_id
            )
            
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model."""
        if self.model is None or self.tokenizer is None:
            raise ModelAdapterError(
                "Model or tokenizer not initialized. Call initialize() first.",
                model_type=ModelTypeEnum.HUGGINGFACE.value,
                model_id=self.model_config.model_id
            )
            
        try:
            # Merge parameters from model config with any overrides
            params = self.model_config.parameters.model_dump()
            params.update(kwargs)
            
            # Remove any None values and extra_params
            extra_params = params.pop("extra_params", {})
            params = {k: v for k, v in params.items() if v is not None}
            params.update(extra_params)
            
            # Convert parameters to proper names expected by the model
            if "max_tokens" in params:
                params["max_new_tokens"] = params.pop("max_tokens")
            if "stop_sequences" in params:
                params["stopping_criteria"] = params.pop("stop_sequences")
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            if self.device != "cpu":
                inputs = inputs.to(self.device)
            
            # Generate response
            loop = asyncio.get_event_loop()
            outputs = await loop.run_in_executor(
                None,
                lambda: self.model.generate(**inputs, **params)
            )
            
            # Decode and return the response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the prompt from the response if it's included
            if response.startswith(prompt):
                response = response[len(prompt):]
                
            return response.strip()
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.HUGGINGFACE.value,
                model_id=self.model_config.model_id
            )
            
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Generate a streaming response from the model."""
        if self.model is None or self.tokenizer is None:
            raise ModelAdapterError(
                "Model or tokenizer not initialized. Call initialize() first.",
                model_type=ModelTypeEnum.HUGGINGFACE.value,
                model_id=self.model_config.model_id
            )
            
        try:
            # Merge parameters from model config with any overrides
            params = self.model_config.parameters.model_dump()
            params.update(kwargs)
            
            # Remove any None values and extra_params
            extra_params = params.pop("extra_params", {})
            params = {k: v for k, v in params.items() if v is not None}
            params.update(extra_params)
            
            # Convert parameters to proper names expected by the model
            if "max_tokens" in params:
                params["max_new_tokens"] = params.pop("max_tokens")
            if "stop_sequences" in params:
                params["stopping_criteria"] = params.pop("stop_sequences")
            
            # Set up the streamer
            streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True)
            params["streamer"] = streamer
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            if self.device != "cpu":
                inputs = inputs.to(self.device)
            
            # Start generation in a separate thread
            generation_kwargs = {**inputs, **params}
            task = asyncio.create_task(
                asyncio.to_thread(self.model.generate, **generation_kwargs)
            )
            
            # Yield from the streamer
            for text in streamer:
                yield text
                
            # Make sure generation is complete
            await task
            
        except Exception as e:
            error_msg = f"Error generating streaming response: {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.HUGGINGFACE.value,
                model_id=self.model_config.model_id
            )
            
    async def get_token_count(self, text: str) -> int:
        """Get the number of tokens in the text."""
        if self.tokenizer is None:
            raise ModelAdapterError(
                "Tokenizer not initialized. Call initialize() first.",
                model_type=ModelTypeEnum.HUGGINGFACE.value,
                model_id=self.model_config.model_id
            )
            
        try:
            tokens = self.tokenizer.encode(text)
            return len(tokens)
        except Exception as e:
            error_msg = f"Error counting tokens: {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.HUGGINGFACE.value,
                model_id=self.model_config.model_id
            )
            
    async def cleanup(self) -> None:
        """Clean up resources used by the model."""
        try:
            # Free memory
            if self.model is not None:
                del self.model
            if self.tokenizer is not None:
                del self.tokenizer
                
            # Force garbage collection
            import gc
            gc.collect()
            
            if self.device != "cpu":
                torch.cuda.empty_cache()
                
            self.model = None
            self.tokenizer = None
            self.logger.info(f"Cleaned up resources for model {self.model_config.model_id}")
        except Exception as e:
            error_msg = f"Error cleaning up resources: {str(e)}"
            self.logger.error(error_msg)
            raise ModelAdapterError(
                error_msg,
                model_type=ModelTypeEnum.HUGGINGFACE.value,
                model_id=self.model_config.model_id
            )
            
    @classmethod
    def supported_model_type(cls) -> ModelTypeEnum:
        """Return the model type supported by this adapter."""
        return ModelTypeEnum.HUGGINGFACE


# Register the adapter with the factory
ModelAdapterFactory.register_adapter(HuggingFaceAdapter)