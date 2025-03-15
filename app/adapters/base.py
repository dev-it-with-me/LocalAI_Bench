# ModelAdapter (Base Class)
import abc
from typing import TypeVar, Generic
from collections.abc import AsyncIterator
from app.enums import ModelTypeEnum
from app.services.model_service.models import Model
from app.exceptions import ModelAdapterError

# Type variable for response types
T = TypeVar('T')


class ModelAdapter(Generic[T], abc.ABC):
    """Base adapter interface for interacting with AI models."""

    def __init__(self, model_config: Model):
        """Initialize the model adapter.

        Args:
            model_config: Configuration for the model
        """
        self.model_config = model_config
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Set up a logger for the adapter."""
        from app.utils import get_logger
        return get_logger(f"ModelAdapter:{self.model_config.name}")

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the model and any resources required.

        Should be called before using the model. May download models,
        establish connections, or allocate resources.

        Raises:
            ModelAdapterError: If initialization fails
        """
        pass

    @abc.abstractmethod
    async def generate(self, prompt: str, **kwargs) -> T:
        """Generate a response from the model.

        Args:
            prompt: The input prompt to send to the model
            **kwargs: Additional model-specific parameters

        Returns:
            The model response

        Raises:
            ModelAdapterError: If generation fails
        """
        pass

    @abc.abstractmethod
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[T]:  # Corrected type hint
        """Generate a streaming response from the model.

        Args:
            prompt: The input prompt to send to the model
            **kwargs: Additional model-specific parameters

        Returns:
            An async iterator of model responses

        Raises:
            ModelAdapterError: If generation fails
        """
        pass

    @abc.abstractmethod
    async def get_token_count(self, text: str) -> int:
        """Get the number of tokens in the text.

        Args:
            text: The text to count tokens for

        Returns:
            The number of tokens

        Raises:
            ModelAdapterError: If token counting fails
        """
        pass

    @abc.abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources used by the model.

        Should be called when the adapter is no longer needed.

        Raises:
            ModelAdapterError: If cleanup fails
        """
        pass

    @classmethod
    @abc.abstractmethod
    def supported_model_type(cls) -> ModelTypeEnum:
        """Return the model type supported by this adapter."""
        pass