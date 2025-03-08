"""
Data models for category service.
"""

from pydantic import Field

from app.models import BaseEntityModel


class Category(BaseEntityModel[str]):
    """Model for benchmark categories."""
    name: str
    description: str = ""
    task_ids: list[str] = Field(default_factory=list)