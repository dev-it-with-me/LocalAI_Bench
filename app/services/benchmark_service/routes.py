"""
API routes for benchmark operations.
"""

from fastapi import APIRouter, HTTPException, status

from app.exceptions import ValidationError, BenchmarkExecutionError
from app.utils import get_logger

from .schemas import (
    BenchmarkCreateRequest,
    BenchmarkResultsResponse,
    BenchmarkStatusResponse,
    BenchmarksResponse,
)
from .models import BenchmarkRun
from .service import BenchmarkService


# Initialize router and service
benchmark_router = APIRouter(prefix="/benchmarks", tags=["Benchmarks"])
benchmark_service = BenchmarkService()
logger = get_logger("benchmark_routes")


@benchmark_router.post(
    "",
    response_model=BenchmarkRun,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid request data"},
        500: {"description": "Internal server error"},
    },
)
async def create_benchmark(benchmark: BenchmarkCreateRequest) -> BenchmarkRun:
    """Create a new benchmark run."""
    try:
        logger.info(f"Creating benchmark: {benchmark.name}")
        result = await benchmark_service.create_benchmark_run(**benchmark.model_dump())
        return result
    except ValidationError as e:
        logger.error(f"Validation error creating benchmark: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        logger.error("Error creating benchmark", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@benchmark_router.get(
    "",
    response_model=BenchmarksResponse,
    responses={500: {"description": "Internal server error"}},
)
async def list_benchmarks() -> BenchmarksResponse:
    """Get all benchmark runs."""
    try:
        logger.info("Listing all benchmarks")
        benchmarks = await benchmark_service.list_benchmark_runs()
        return BenchmarksResponse(
            benchmarks=benchmarks,
            message="Benchmark runs retrieved successfully",
        )
    except Exception:
        logger.error("Error listing benchmarks", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@benchmark_router.get(
    "/{benchmark_id}",
    response_model=BenchmarkRun,
    responses={
        404: {"description": "Benchmark not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_benchmark(benchmark_id: str) -> BenchmarkRun:
    """Get a benchmark run by ID.
    
    Args:
        benchmark_id: ID of benchmark to retrieve
        
    Returns:
        BenchmarkRun: Benchmark run details
        
    Raises:
        HTTPException: If benchmark not found or internal error occurs
    """
    try:
        logger.info(f"Getting benchmark: {benchmark_id}")
        return await benchmark_service.get_benchmark_run(benchmark_id)
    except ValidationError as e:
        logger.error(f"Benchmark not found: {benchmark_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.error(f"Error getting benchmark {benchmark_id}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@benchmark_router.post(
    "/{benchmark_id}/start",
    response_model=BenchmarkRun,
    responses={
        404: {"description": "Benchmark not found"},
        400: {"description": "Invalid benchmark state"},
        500: {"description": "Internal server error"},
    },
)
async def start_benchmark(benchmark_id: str) -> BenchmarkRun:
    """Start a benchmark run.
    
    Args:
        benchmark_id: ID of benchmark to start
        
    Returns:
        BenchmarkRun: Updated benchmark run details
        
    Raises:
        HTTPException: If benchmark not found, in invalid state, or internal error occurs
    """
    try:
        logger.info(f"Starting benchmark: {benchmark_id}")
        return await benchmark_service.start_benchmark(benchmark_id)
    except ValidationError as e:
        logger.error(f"Error starting benchmark {benchmark_id}: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BenchmarkExecutionError as e:
        logger.error(f"Execution error for benchmark {benchmark_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        logger.error(f"Error starting benchmark {benchmark_id}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@benchmark_router.get(
    "/{benchmark_id}/status",
    response_model=BenchmarkStatusResponse,
    responses={
        404: {"description": "Benchmark not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_benchmark_status(benchmark_id: str) -> BenchmarkStatusResponse:
    """Get the status of a benchmark run.
    
    Args:
        benchmark_id: ID of benchmark to get status for
        
    Returns:
        BenchmarkStatusResponse: Current benchmark status
        
    Raises:
        HTTPException: If benchmark not found or internal error occurs
    """
    try:
        logger.info(f"Getting status for benchmark: {benchmark_id}")
        status_data = await benchmark_service.get_benchmark_status(benchmark_id)
        return BenchmarkStatusResponse(**status_data)
    except ValidationError as e:
        logger.error(f"Benchmark not found: {benchmark_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.error(f"Error getting benchmark status {benchmark_id}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@benchmark_router.get(
    "/{benchmark_id}/results",
    response_model=BenchmarkResultsResponse,
    responses={
        404: {"description": "Benchmark not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_benchmark_results(benchmark_id: str) -> BenchmarkResultsResponse:
    """Get the results of a benchmark run.
    
    Args:
        benchmark_id: ID of benchmark to get results for
        
    Returns:
        BenchmarkResultsResponse: Benchmark results
        
    Raises:
        HTTPException: If benchmark not found or internal error occurs
    """
    try:
        logger.info(f"Getting results for benchmark: {benchmark_id}")
        results = await benchmark_service.get_benchmark_results(benchmark_id)
        return BenchmarkResultsResponse(**results)
    except ValidationError as e:
        logger.error(f"Benchmark not found: {benchmark_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.error(f"Error getting benchmark results {benchmark_id}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@benchmark_router.post(
    "/{benchmark_id}/cancel",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Benchmark not found"},
        400: {"description": "Benchmark cannot be cancelled"},
        500: {"description": "Internal server error"},
    },
)
async def cancel_benchmark(benchmark_id: str) -> dict:
    """Cancel a running benchmark.
    
    Args:
        benchmark_id: ID of benchmark to cancel
        
    Returns:
        dict: Success status
        
    Raises:
        HTTPException: If benchmark not found, cannot be cancelled, or internal error occurs
    """
    try:
        logger.info(f"Cancelling benchmark: {benchmark_id}")
        success = await benchmark_service.cancel_benchmark(benchmark_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Benchmark cannot be cancelled"
            )
        return {"success": True}
    except ValidationError as e:
        logger.error(f"Benchmark not found: {benchmark_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        logger.error(f"Error cancelling benchmark {benchmark_id}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@benchmark_router.delete(
    "/{benchmark_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Benchmark not found"},
        400: {"description": "Benchmark cannot be deleted"},
        500: {"description": "Internal server error"},
    },
)
async def delete_benchmark(benchmark_id: str) -> dict:
    """Delete a benchmark run."""
    try:
        logger.info(f"Deleting benchmark: {benchmark_id}")
        await benchmark_service.delete_benchmark(benchmark_id)
        return {"success": True}
    except ValidationError as e:
        if "active benchmark" in str(e).lower():
            logger.error(f"Cannot delete active benchmark: {benchmark_id}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        logger.error(f"Benchmark not found: {benchmark_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.error(f"Error deleting benchmark {benchmark_id}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )