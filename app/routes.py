"""
API routes for LocalAI Bench application.

This module imports and configures all API routes from service-specific route modules.
"""

from fastapi import APIRouter

# from app.services.benchmark_service.routes import benchmark_router
from app.modules.category_service.routes import category_router
from app.modules.import_export_service.routes import import_export_router
from app.modules.model_service.routes import model_router
from app.modules.task_service.routes import task_router

# Create the main API router
api_router = APIRouter(prefix="/api")

# Include all service routers
# api_router.include_router(benchmark_router)
api_router.include_router(category_router)
api_router.include_router(import_export_router)
api_router.include_router(model_router)
api_router.include_router(task_router)
