"""
Main entry point for the LocalAI Bench application.

This module initializes the FastAPI application, sets up middleware,
exception handlers, and includes API routes.
"""


from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.exceptions import (
    AuthenticationError, 
    BenchmarkExecutionError, 
    ConfigurationError,
    DataStorageError,
    LocalAIBenchError,
    ModelAdapterError,
    ValidationError
)
from app.routes import (
    benchmark_router,
    category_router,
    import_export_router,
    model_router,
    task_router,
    template_router
)
from app.schemas import ErrorResponse
from app.utils import get_logger

# Create logger
logger = get_logger("main")

# Create FastAPI app
app = FastAPI(
    title="LocalAI Bench API",
    description="API for LocalAI Bench application",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            status="error",
            message=exc.message,
            error_type="validation_error",
            details={"field": exc.field} if exc.field else None,
        ).model_dump(),
    )


@app.exception_handler(BenchmarkExecutionError)
async def benchmark_exception_handler(request: Request, exc: BenchmarkExecutionError) -> JSONResponse:
    """Handle benchmark execution errors."""
    logger.error(f"Benchmark execution error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status="error",
            message=exc.message,
            error_type="benchmark_execution_error",
            details={
                "benchmark_id": exc.benchmark_id,
                "task_id": exc.task_id,
                "model_id": exc.model_id,
            },
        ).model_dump(),
    )


@app.exception_handler(ModelAdapterError)
async def model_adapter_exception_handler(request: Request, exc: ModelAdapterError) -> JSONResponse:
    """Handle model adapter errors."""
    logger.error(f"Model adapter error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status="error",
            message=exc.message,
            error_type="model_adapter_error",
            details={
                "model_type": exc.model_type,
                "model_id": exc.model_id,
            },
        ).model_dump(),
    )


@app.exception_handler(DataStorageError)
async def data_storage_exception_handler(request: Request, exc: DataStorageError) -> JSONResponse:
    """Handle data storage errors."""
    logger.error(f"Data storage error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status="error",
            message=exc.message,
            error_type="data_storage_error",
            details={
                "entity_type": exc.entity_type,
                "entity_id": exc.entity_id,
            },
        ).model_dump(),
    )


@app.exception_handler(ConfigurationError)
async def configuration_exception_handler(request: Request, exc: ConfigurationError) -> JSONResponse:
    """Handle configuration errors."""
    logger.error(f"Configuration error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status="error",
            message=exc.message,
            error_type="configuration_error",
        ).model_dump(),
    )


@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    """Handle authentication errors."""
    logger.warning(f"Authentication error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ErrorResponse(
            status="error",
            message=exc.message,
            error_type="authentication_error",
            details={"provider": exc.provider} if exc.provider else None,
        ).model_dump(),
    )


@app.exception_handler(LocalAIBenchError)
async def general_exception_handler(request: Request, exc: LocalAIBenchError) -> JSONResponse:
    """Handle general LocalAI Bench errors."""
    logger.error(f"Application error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status="error",
            message=exc.message,
            error_type="application_error",
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def fallback_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unhandled exceptions."""
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status="error",
            message="An unexpected error occurred",
            error_type="server_error",
            details={"error": str(exc)} if settings.DEBUG else None,
        ).model_dump(),
    )


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan event handler for startup and shutdown."""
    logger.info("Starting LocalAI Bench API")
    
    # Ensure data directories exist
    import os
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.STATIC_DIR, exist_ok=True)
    os.makedirs(settings.CATEGORIES_DIR, exist_ok=True)
    os.makedirs(settings.TASKS_DIR, exist_ok=True)
    os.makedirs(settings.TEMPLATES_DIR, exist_ok=True)
    os.makedirs(settings.MODELS_DIR, exist_ok=True)
    os.makedirs(settings.RESULTS_DIR, exist_ok=True)
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    yield

    logger.info("LocalAI Bench API shutdown")


# Root endpoint
@app.get("/", tags=["Status"])
async def root() -> dict:
    """Root endpoint returning API information."""
    return {
        "name": "LocalAI Bench API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/status", tags=["Status"])
async def _status() -> dict:
    """Status endpoint returning API status."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "debug": settings.DEBUG,
    }


# Include API routers
app.include_router(category_router, prefix="/api")
app.include_router(template_router, prefix="/api")
app.include_router(task_router, prefix="/api")
app.include_router(model_router, prefix="/api")
app.include_router(benchmark_router, prefix="/api")
app.include_router(import_export_router, prefix="/api")

# Include static files for serving UI
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Main application entry point
if __name__ == "__main__":
    import uvicorn

    # Start the server with uvicorn when script is run directly
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )