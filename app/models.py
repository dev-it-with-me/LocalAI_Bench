"""
Shared base models for LocalAI Bench application.

This module contains Pydantic base models used across multiple services.
"""

import uuid
from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

# Generic type for ID fields
T = TypeVar('T')


class BaseEntityModel(BaseModel, Generic[T]):
    """Base model for all entity models with ID and timestamps."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)