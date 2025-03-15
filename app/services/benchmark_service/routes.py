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