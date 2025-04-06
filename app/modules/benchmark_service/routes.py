"""
API routes for benchmark operations.
"""

from fastapi import APIRouter, HTTPException, Path, Query, Body

from app.exceptions import BenchmarkExecutionError, ValidationError
from .service import BenchmarkService
from .schemas import (
    BenchmarkCreateRequest,
    BenchmarkStatusResponse,
    BenchmarkResultsResponse,
    BenchmarksResponse,
)

benchmark_router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])
service = BenchmarkService()


@benchmark_router.post("/", response_model=BenchmarkResultsResponse)
async def create_benchmark(request: BenchmarkCreateRequest) -> BenchmarkResultsResponse:
    """Create a new benchmark run."""
    try:
        benchmark_run = await service.create_benchmark_run(
            name=request.name,
            model_ids=request.model_ids,
            category_ids=request.category_ids,
            task_ids=request.task_ids,
            description=request.description,
        )

        # Return a structured response
        return BenchmarkResultsResponse(
            benchmark_run=benchmark_run.model_dump(),
            models={},  # These would be populated with actual model data
            categories={},  # These would be populated with actual category data
            results_by_model={},  # Initially empty until benchmark is run
            aggregate_scores=benchmark_run.aggregate_scores or {},
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create benchmark: {str(e)}"
        )


@benchmark_router.put("/{benchmark_id}", response_model=BenchmarkResultsResponse)
async def modify_benchmark(
    benchmark_id: str = Path(..., description="The ID of the benchmark to modify"),
    request: BenchmarkCreateRequest = Body(...),
) -> BenchmarkResultsResponse:
    """Modify an existing benchmark run."""
    try:
        # First get the existing benchmark
        benchmark_run = await service.benchmark_repo.get_by_id(benchmark_id)
        if not benchmark_run:
            raise ValidationError(f"Benchmark {benchmark_id} not found")

        # Update fields
        benchmark_run.name = request.name
        benchmark_run.description = request.description
        benchmark_run.model_ids = request.model_ids
        benchmark_run.category_ids = request.category_ids
        benchmark_run.task_ids = request.task_ids

        # Save the updated benchmark
        updated_benchmark = await service.benchmark_repo.update(benchmark_run)

        return BenchmarkResultsResponse(
            benchmark_run=updated_benchmark.model_dump(),
            models={},
            categories={},
            results_by_model={},
            aggregate_scores=updated_benchmark.aggregate_scores or {},
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to modify benchmark: {str(e)}"
        )


@benchmark_router.post("/{benchmark_id}/copy", response_model=BenchmarkResultsResponse)
async def copy_benchmark(
    benchmark_id: str = Path(..., description="The ID of the benchmark to copy"),
    name: str = Query(None, description="New name for the copied benchmark"),
) -> BenchmarkResultsResponse:
    """Create a copy of an existing benchmark run."""
    try:
        # Get the existing benchmark
        original_benchmark = await service.benchmark_repo.get_by_id(benchmark_id)
        if not original_benchmark:
            raise ValidationError(f"Benchmark {benchmark_id} not found")

        # Create a new benchmark with the same configuration
        new_name = name or f"Copy of {original_benchmark.name}"
        new_benchmark = await service.create_benchmark_run(
            name=new_name,
            model_ids=original_benchmark.model_ids,
            category_ids=original_benchmark.category_ids,
            task_ids=original_benchmark.task_ids,
            description=original_benchmark.description,
        )

        return BenchmarkResultsResponse(
            benchmark_run=new_benchmark.model_dump(),
            models={},
            categories={},
            results_by_model={},
            aggregate_scores={},
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to copy benchmark: {str(e)}"
        )


@benchmark_router.post("/{benchmark_id}/start", response_model=BenchmarkStatusResponse)
async def start_benchmark(benchmark_id: str) -> BenchmarkStatusResponse:
    """Start a benchmark run."""
    try:
        benchmark_run = await service.start_benchmark_run(benchmark_id)
        return BenchmarkStatusResponse(
            id=benchmark_run.id,
            name=benchmark_run.name,
            status=benchmark_run.status.value,
            start_time=benchmark_run.start_time,
            end_time=benchmark_run.end_time,
            progress={
                "total_tasks": len(benchmark_run.task_results),
                "completed_tasks": len(
                    [r for r in benchmark_run.task_results if not benchmark_run.error]
                ),
                "error_tasks": len(
                    [r for r in benchmark_run.task_results if benchmark_run.error]
                ),
            },
            is_active=benchmark_run.status == "IN_PROGRESS",
            error=benchmark_run.error,
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BenchmarkExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start benchmark: {str(e)}"
        )


@benchmark_router.get("/{benchmark_id}/status", response_model=BenchmarkStatusResponse)
async def get_benchmark_status(benchmark_id: str) -> BenchmarkStatusResponse:
    """Get the status of a benchmark run."""
    try:
        status = await service.get_benchmark_status(benchmark_id)
        return BenchmarkStatusResponse(**status)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get benchmark status: {str(e)}"
        )


@benchmark_router.post("/{benchmark_id}/results/{task_result_id}/score")
async def update_task_score(
    benchmark_id: str,
    task_result_id: str,
    quality_score: float = Query(
        ..., ge=0, le=10, description="Quality score between 0-10"
    ),
    weights: dict[str, float] | None = Body(
        None, description="Optional custom weights for scoring"
    ),
) -> dict:
    """Update the quality score for a task result."""
    try:
        result = await service.update_result_score(
            benchmark_id,
            task_result_id,
            quality_score,
            weights,
        )
        return result.model_dump()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@benchmark_router.get("/", response_model=BenchmarksResponse)
async def list_benchmarks(
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of results to return"
    ),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
) -> BenchmarksResponse:
    """List all benchmark runs."""
    try:
        # TODO Add limit to the list_all method in the repository
        # to support pagination
        benchmarks = await service.benchmark_repo.list_all(limit=limit, offset=offset)
        return BenchmarksResponse(
            benchmarks=benchmarks,
            total=len(benchmarks),
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list benchmarks: {str(e)}"
        )
