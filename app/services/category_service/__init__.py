"""
Category service for managing benchmark categories and their associations.
"""

from .routes import category_router
from .service import CategoryService

__all__ = ["category_router", "CategoryService"]