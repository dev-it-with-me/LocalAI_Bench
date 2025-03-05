"""
Repository for template service.
"""

from app.config import settings
from app.services.template_service.models import Template
from app.repositories import BaseRepository


class TemplateRepository(BaseRepository[Template]):
    """Repository for template operations."""
    
    def __init__(self):
        """Initialize the template repository."""
        directory = settings.data_subdirs()["templates"]
        super().__init__(directory, Template)
        
    def get_by_category(self, category: str) -> list[Template]:
        """Get all templates for a category."""
        result = []
        for template in self.list_all():
            if template.category.value == category:
                result.append(template)
        return result