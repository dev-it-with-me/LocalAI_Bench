"""
Common base schemas for LocalAI Bench application.

This module contains base Pydantic models used across multiple services.
"""

from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Base response schema with status and message."""
    status: str = "success"
    message: str = ""


class ErrorResponse(BaseResponse):
    """Error response schema with additional error details."""
    status: str = "error"
    error_type: str
    details: dict | None = None

    class Config:
        """Configure schema behavior."""
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Failed to execute benchmark",
                "error_type": "benchmark_execution_error",
                "details": {
                    "benchmark_id": "123",
                    "task_id": "456",
                    "model_id": "789"
                }
            }
        }