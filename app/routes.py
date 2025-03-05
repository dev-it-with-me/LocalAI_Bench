"""
API routes for LocalAI Bench application.

This module contains FastAPI route definitions for all API endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.schemas import (
    # Category schemas
    CategoriesResponse,
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
    
    # Template schemas
    TemplateCreateRequest,
    TemplateResponse,
    TemplatesResponse,
    TemplateUpdateRequest,
    
    # Task schemas
    TaskCreateRequest,
    TaskResponse,
    TasksResponse,
    TaskUpdateRequest,
    
    # Model schemas
    ModelCreateRequest,
    ModelResponse,
    ModelsResponse,
    ModelUpdateRequest,
    
    # Benchmark schemas
    BenchmarkCreateRequest,
    BenchmarkResponse,
    BenchmarkResultsResponse,
    BenchmarkStatusResponse,
    BenchmarksResponse,
    
    # Import/Export schemas
    ExportRequest,
    ExportResponse,
    ImportPreviewResponse,
    ImportRequest,
    
    # Base response
    BaseResponse,
)

# Import updated services
from app.services import BenchmarkService, ModelService, CategoryService, TemplateService, TaskService, ImportExportService
from app.enums import ModelTypeEnum, TemplateTypeEnum, TaskStatusEnum

# Create routers
category_router = APIRouter(prefix="/categories", tags=["Categories"])
template_router = APIRouter(prefix="/templates", tags=["Templates"])
task_router = APIRouter(prefix="/tasks", tags=["Tasks"])
model_router = APIRouter(prefix="/models", tags=["Models"])
benchmark_router = APIRouter(prefix="/benchmarks", tags=["Benchmarks"])
import_export_router = APIRouter(prefix="/import-export", tags=["Import/Export"])


# ======== Category Routes ========
@category_router.get("", response_model=CategoriesResponse)
async def list_categories() -> CategoriesResponse:
    """Get all categories."""
    category_service = CategoryService()
    categories = await category_service.list_categories()
    return CategoriesResponse(
        message="Categories retrieved successfully",
        categories=categories
    )


@category_router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreateRequest) -> CategoryResponse:
    """Create a new category."""
    category_service = CategoryService()
    created_category = await category_service.create_category(
        name=category.name,
        description=category.description,
        time_weight=category.time_weight,
        quality_weight=category.quality_weight,
        complexity_weight=category.complexity_weight,
        cost_weight=category.cost_weight,
        memory_weight=category.memory_weight
    )
    return created_category


@category_router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str = Path(..., title="Category ID")) -> CategoryResponse:
    """Get a category by ID."""
    category_service = CategoryService()
    category = await category_service.get_category(category_id)
    return category


@category_router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category: CategoryUpdateRequest, category_id: str = Path(..., title="Category ID")
) -> CategoryResponse:
    """Update a category."""
    category_service = CategoryService()
    updated_category = await category_service.update_category(
        category_id=category_id,
        name=category.name,
        description=category.description,
        time_weight=category.time_weight,
        quality_weight=category.quality_weight,
        complexity_weight=category.complexity_weight,
        cost_weight=category.cost_weight,
        memory_weight=category.memory_weight
    )
    return updated_category


@category_router.delete("/{category_id}", response_model=BaseResponse)
async def delete_category(category_id: str = Path(..., title="Category ID")) -> BaseResponse:
    """Delete a category."""
    category_service = CategoryService()
    await category_service.delete_category(category_id)
    return BaseResponse(
        message=f"Category deleted: {category_id}"
    )


@category_router.get("/{category_id}/tasks", response_model=TasksResponse)
async def get_category_tasks(category_id: str = Path(..., title="Category ID")) -> TasksResponse:
    """Get all tasks in a category."""
    category_service = CategoryService()
    tasks = await category_service.get_category_tasks(category_id)
    return TasksResponse(
        message="Category tasks retrieved successfully",
        tasks=tasks
    )


@category_router.post("/{category_id}/tasks/{task_id}", response_model=CategoryResponse)
async def add_task_to_category(
    category_id: str = Path(..., title="Category ID"),
    task_id: str = Path(..., title="Task ID"),
) -> CategoryResponse:
    """Add a task to a category."""
    category_service = CategoryService()
    updated_category = await category_service.add_task_to_category(category_id, task_id)
    return updated_category


@category_router.delete("/{category_id}/tasks/{task_id}", response_model=CategoryResponse)
async def remove_task_from_category(
    category_id: str = Path(..., title="Category ID"),
    task_id: str = Path(..., title="Task ID"),
) -> CategoryResponse:
    """Remove a task from a category."""
    category_service = CategoryService()
    updated_category = await category_service.remove_task_from_category(category_id, task_id)
    return updated_category


# ======== Template Routes ========
@template_router.get("", response_model=TemplatesResponse)
async def list_templates(
    category: Optional[str] = Query(None, title="Filter by template category")
) -> TemplatesResponse:
    """Get all templates, optionally filtered by category."""
    template_service = TemplateService()
    templates = await template_service.list_templates(
        TemplateTypeEnum(category) if category else None
    )
    return TemplatesResponse(
        message="Templates retrieved successfully",
        templates=templates
    )


@template_router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(template: TemplateCreateRequest) -> TemplateResponse:
    """Create a new template."""
    template_service = TemplateService()
    created_template = await template_service.create_template(
        name=template.name,
        template_id=template.template_id,
        category=template.category,
        description=template.description,
        input_schema=template.input_schema,
        output_schema=template.output_schema,
        evaluation_criteria=template.evaluation_criteria,
        test_cases=template.test_cases
    )
    return created_template


@template_router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str = Path(..., title="Template ID")) -> TemplateResponse:
    """Get a template by ID."""
    template_service = TemplateService()
    template = await template_service.get_template(template_id)
    return template


@template_router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template: TemplateUpdateRequest, template_id: str = Path(..., title="Template ID")
) -> TemplateResponse:
    """Update a template."""
    template_service = TemplateService()
    updated_template = await template_service.update_template(
        template_id=template_id,
        name=template.name,
        description=template.description,
        input_schema=template.input_schema,
        output_schema=template.output_schema,
        evaluation_criteria=template.evaluation_criteria,
        test_cases=template.test_cases
    )
    return updated_template


@template_router.delete("/{template_id}", response_model=BaseResponse)
async def delete_template(template_id: str = Path(..., title="Template ID")) -> BaseResponse:
    """Delete a template."""
    template_service = TemplateService()
    await template_service.delete_template(template_id)
    return BaseResponse(
        message=f"Template deleted: {template_id}"
    )


@template_router.get("/{template_id}/tasks", response_model=TasksResponse)
async def get_template_tasks(template_id: str = Path(..., title="Template ID")) -> TasksResponse:
    """Get all tasks using a template."""
    template_service = TemplateService()
    tasks = await template_service.get_template_tasks(template_id)
    return TasksResponse(
        message="Template tasks retrieved successfully",
        tasks=tasks
    )


# ======== Task Routes ========
@task_router.get("", response_model=TasksResponse)
async def list_tasks(
    category_id: Optional[str] = Query(None, title="Filter by category ID"),
    status: Optional[str] = Query(None, title="Filter by task status"),
) -> TasksResponse:
    """Get all tasks, optionally filtered by category or status."""
    task_service = TaskService()
    tasks = await task_service.list_tasks(
        category_id=category_id,
        status=TaskStatusEnum(status) if status else None
    )
    return TasksResponse(
        message="Tasks retrieved successfully",
        tasks=tasks
    )


@task_router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreateRequest) -> TaskResponse:
    """Create a new task."""
    task_service = TaskService()
    created_task = await task_service.create_task(
        name=task.name,
        template_id=task.template_id,
        description=task.description,
        category_id=task.category_id,
        input_data=task.input_data,
        expected_output=task.expected_output,
        evaluation_weights=task.evaluation_weights,
        status=task.status
    )
    return created_task


@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str = Path(..., title="Task ID")) -> TaskResponse:
    """Get a task by ID."""
    task_service = TaskService()
    task = await task_service.get_task(task_id)
    return task


@task_router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task: TaskUpdateRequest, task_id: str = Path(..., title="Task ID")
) -> TaskResponse:
    """Update a task."""
    task_service = TaskService()
    updated_task = await task_service.update_task(
        task_id=task_id,
        name=task.name,
        description=task.description,
        category_id=task.category_id,
        input_data=task.input_data,
        expected_output=task.expected_output,
        evaluation_weights=task.evaluation_weights,
        status=task.status
    )
    return updated_task


@task_router.delete("/{task_id}", response_model=BaseResponse)
async def delete_task(task_id: str = Path(..., title="Task ID")) -> BaseResponse:
    """Delete a task."""
    task_service = TaskService()
    await task_service.delete_task(task_id)
    return BaseResponse(
        message=f"Task deleted: {task_id}"
    )


# ======== Model Routes ========
@model_router.get("", response_model=ModelsResponse)
async def list_models(
    type: Optional[str] = Query(None, title="Filter by model type")
) -> ModelsResponse:
    """Get all models, optionally filtered by type."""
    model_service = ModelService()
    models = await model_service.list_models(
        ModelTypeEnum(type) if type else None
    )
    return ModelsResponse(
        message="Models retrieved successfully",
        models=models
    )


@model_router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(model: ModelCreateRequest) -> ModelResponse:
    """Create a new model."""
    model_service = ModelService()
    created_model = await model_service.create_model(
        name=model.name,
        type=model.type,
        model_id=model.model_id,
        description=model.description,
        api_url=model.api_url,
        api_key=model.api_key,
        api_version=model.api_version,
        parameters=model.parameters.model_dump() if model.parameters else None,
        memory_required=model.memory_required,
        gpu_required=model.gpu_required,
        quantization=model.quantization
    )
    return created_model


@model_router.get("/{model_id}", response_model=ModelResponse)
async def get_model(model_id: str = Path(..., title="Model ID")) -> ModelResponse:
    """Get a model by ID."""
    model_service = ModelService()
    model = await model_service.get_model(model_id)
    return model


@model_router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model: ModelUpdateRequest,
    model_id: str = Path(..., title="Model ID")
) -> ModelResponse:
    """Update a model."""
    model_service = ModelService()
    updated_model = await model_service.update_model(
        model_id=model_id,
        name=model.name,
        description=model.description,
        api_url=model.api_url,
        api_key=model.api_key,
        api_version=model.api_version,
        parameters=model.parameters.model_dump() if model.parameters else None,
        memory_required=model.memory_required,
        gpu_required=model.gpu_required,
        quantization=model.quantization
    )
    return updated_model


@model_router.delete("/{model_id}", response_model=BaseResponse)
async def delete_model(model_id: str = Path(..., title="Model ID")) -> BaseResponse:
    """Delete a model."""
    model_service = ModelService()
    await model_service.delete_model(model_id)
    return BaseResponse(
        message=f"Model deleted: {model_id}"
    )


@model_router.post("/{model_id}/test", response_model=BaseResponse)
async def test_model(model_id: str = Path(..., title="Model ID")) -> BaseResponse:
    """Test model connectivity and functionality."""
    model_service = ModelService()
    test_result = await model_service.test_model(model_id)
    return BaseResponse(
        status=test_result["status"],
        message="Model test completed successfully" if test_result["status"] == "success" else test_result["error"]
    )


# ======== Benchmark Routes ========
@benchmark_router.get("", response_model=BenchmarksResponse)
async def list_benchmarks() -> BenchmarksResponse:
    """Get all benchmark runs."""
    benchmark_service = BenchmarkService()
    benchmarks = await benchmark_service.list_benchmark_runs()
    return BenchmarksResponse(
        message="Benchmark runs retrieved successfully",
        benchmarks=benchmarks
    )


@benchmark_router.post("", response_model=BenchmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_benchmark(benchmark: BenchmarkCreateRequest) -> BenchmarkResponse:
    """Create a new benchmark run."""
    benchmark_service = BenchmarkService()
    benchmark_run = await benchmark_service.create_benchmark_run(
        name=benchmark.name,
        model_ids=benchmark.model_ids,
        category_ids=benchmark.category_ids,
        task_ids=benchmark.task_ids,
        description=benchmark.description
    )
    return benchmark_run


@benchmark_router.get("/{benchmark_id}", response_model=BenchmarkResponse)
async def get_benchmark(benchmark_id: str = Path(..., title="Benchmark ID")) -> BenchmarkResponse:
    """Get a benchmark run by ID."""
    benchmark_service = BenchmarkService()
    benchmark_run = await benchmark_service.get_benchmark_run(benchmark_id)
    return benchmark_run


@benchmark_router.post("/{benchmark_id}/start", response_model=BenchmarkResponse)
async def start_benchmark(benchmark_id: str = Path(..., title="Benchmark ID")) -> BenchmarkResponse:
    """Start a benchmark run."""
    benchmark_service = BenchmarkService()
    benchmark_run = await benchmark_service.start_benchmark(benchmark_id)
    return benchmark_run


@benchmark_router.post("/{benchmark_id}/cancel", response_model=BaseResponse)
async def cancel_benchmark(benchmark_id: str = Path(..., title="Benchmark ID")) -> BaseResponse:
    """Cancel a running benchmark."""
    benchmark_service = BenchmarkService()
    cancelled = await benchmark_service.cancel_benchmark(benchmark_id)
    return BaseResponse(
        status="success" if cancelled else "error",
        message=f"Benchmark {'cancelled' if cancelled else 'not running'}: {benchmark_id}"
    )


@benchmark_router.get("/{benchmark_id}/status", response_model=BenchmarkStatusResponse)
async def get_benchmark_status(
    benchmark_id: str = Path(..., title="Benchmark ID")
) -> BenchmarkStatusResponse:
    """Get the status of a benchmark run."""
    benchmark_service = BenchmarkService()
    status = await benchmark_service.get_benchmark_status(benchmark_id)
    return BenchmarkStatusResponse(**status)


@benchmark_router.get("/{benchmark_id}/results", response_model=BenchmarkResultsResponse)
async def get_benchmark_results(
    benchmark_id: str = Path(..., title="Benchmark ID")
) -> BenchmarkResultsResponse:
    """Get the results of a benchmark run."""
    benchmark_service = BenchmarkService()
    results = await benchmark_service.get_benchmark_results(benchmark_id)
    return BenchmarkResultsResponse(
        message="Benchmark results retrieved successfully",
        **results
    )


@benchmark_router.delete("/{benchmark_id}", response_model=BaseResponse)
async def delete_benchmark(benchmark_id: str = Path(..., title="Benchmark ID")) -> BaseResponse:
    """Delete a benchmark run."""
    benchmark_service = BenchmarkService()
    await benchmark_service.delete_benchmark(benchmark_id)
    return BaseResponse(
        message=f"Benchmark run deleted: {benchmark_id}"
    )


# ======== Import/Export Routes ========
@import_export_router.post("/export", response_model=ExportResponse)
async def export_data(export_request: ExportRequest) -> ExportResponse:
    """Export data based on the specified export type and entity IDs."""
    import_export_service = ImportExportService()
    export_data = await import_export_service.export_data(
        export_type=export_request.export_type,
        entity_ids=export_request.entity_ids
    )
    
    # Generate filename based on export type and timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"localai_bench_{export_request.export_type.value}_{timestamp}.json"
    
    return ExportResponse(
        message="Data exported successfully",
        export_data=export_data,
        file_name=file_name
    )


@import_export_router.post("/import/preview", response_model=ImportPreviewResponse)
async def preview_import(import_request: ImportRequest) -> ImportPreviewResponse:
    """Preview data import to check for conflicts."""
    import_export_service = ImportExportService()
    preview_data = await import_export_service.preview_import(import_request.import_data)
    
    return ImportPreviewResponse(
        message="Import preview completed",
        **preview_data
    )


@import_export_router.post("/import", response_model=BaseResponse)
async def import_data(import_request: ImportRequest) -> BaseResponse:
    """Import data."""
    import_export_service = ImportExportService()
    await import_export_service.import_data(import_request.import_data)
    
    return BaseResponse(
        message="Data imported successfully"
    )