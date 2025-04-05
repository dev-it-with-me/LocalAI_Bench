"""
API routes for benchmark operations.
"""

from fastapi import APIRouter, HTTPException

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
    # TODO Create benchmark run
    # TODO Add proper error handling
    pass

@benchmark_router.post("/", response_model=BenchmarkResultsResponse)
async def modify_benchmark(request: BenchmarkCreateRequest) -> BenchmarkResultsResponse:
    """Create a new benchmark run."""
    # TODO Modify existing benchmark run
    # TODO Add proper error handling
    pass

@benchmark_router.post("/", response_model=BenchmarkResultsResponse)
async def copy_benchmark(request: BenchmarkCreateRequest) -> BenchmarkResultsResponse:
    """Create a new benchmark run."""
    # TODO Copy existing benchmark run
    # TODO Add proper error handling
    pass


@benchmark_router.post("/{benchmark_id}/start", response_model=BenchmarkStatusResponse)
async def start_benchmark(benchmark_id: str) -> BenchmarkStatusResponse:
    """Start a benchmark run."""
    # TODO Start benchmark run
    # TODO Add proper error handling
    pass

@benchmark_router.get("/{benchmark_id}/status", response_model=BenchmarkStatusResponse)
async def get_benchmark_status(benchmark_id: str) -> BenchmarkStatusResponse:
    """Get the status of a benchmark run."""
    # TODO Get benchmark status
    # TODO Add proper error handling
    pass

@benchmark_router.post("/{benchmark_id}/results/{task_result_id}/score")
async def update_task_score(
    benchmark_id: str,
    task_result_id: str,
    quality_score: float,
    weights: dict[str, float] | None = None,
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
async def list_benchmarks() -> BenchmarksResponse:
    """List all benchmark runs."""
    # TODO List all benchmark runs
    # TODO Add proper error handling
    pass
