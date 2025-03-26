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
    try:
        benchmark_run = await service.create_benchmark_run(
            name=request.name,
            model_ids=request.model_ids,
            category_ids=request.category_ids,
            task_ids=request.task_ids,
            description=request.description,
        )
        return BenchmarkResultsResponse(benchmark_run=benchmark_run.model_dump())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@benchmark_router.post("/{benchmark_id}/start", response_model=BenchmarkStatusResponse)
async def start_benchmark(benchmark_id: str) -> BenchmarkStatusResponse:
    """Start a benchmark run."""
    try:
        benchmark_run = await service.start_benchmark_run(benchmark_id)
        status = await service.get_benchmark_status(benchmark_id)
        return BenchmarkStatusResponse(**status)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BenchmarkExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))

@benchmark_router.get("/{benchmark_id}/status", response_model=BenchmarkStatusResponse)
async def get_benchmark_status(benchmark_id: str) -> BenchmarkStatusResponse:
    """Get the status of a benchmark run."""
    try:
        status = await service.get_benchmark_status(benchmark_id)
        return BenchmarkStatusResponse(**status)
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))

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
    try:
        benchmarks = await service.benchmark_repo.list_all()
        return BenchmarksResponse(benchmarks=benchmarks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))