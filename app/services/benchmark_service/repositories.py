"""
Repositories for benchmark service.
"""

import os
from pathlib import Path # Import Path
from app.config import settings
from app.services.benchmark_service.models import BenchmarkRun, TaskResult
from app.repositories import BaseRepository


class TaskResultRepository(BaseRepository[TaskResult]):
    """Repository for task result operations."""
    
    def __init__(self):
        """Initialize the task result repository."""
        directory = Path(settings.RESULTS_DIR) / "task_results"
        super().__init__(directory=directory, model_cls=TaskResult) # Pass Path object
        
    def get_by_task(self, task_id: str) -> list[TaskResult]:
        """Get all results for a specific task."""
        all_results = self.list_all()
        filtered_results = [result for result in all_results if result.task_id == task_id]
        return filtered_results
        
    def get_by_model(self, model_id: str) -> list[TaskResult]:
        """Get all results for a specific model."""
        all_results = self.list_all()
        filtered_results = [result for result in all_results if result.model_id == model_id]
        return filtered_results
        
    def get_by_benchmark_run(self, benchmark_run_id: str) -> list[TaskResult]:
        """Get all results for a specific benchmark run."""
        all_results = self.list_all()
        filtered_results = [result for result in all_results if result.benchmark_run_id == benchmark_run_id]
        return filtered_results


class BenchmarkRunRepository(BaseRepository[BenchmarkRun]):
    """Repository for benchmark run operations."""
    
    def __init__(self):
        """Initialize the benchmark run repository."""
        directory = Path(settings.RESULTS_DIR) / "benchmark_runs"
        super().__init__(directory=directory, model_cls=BenchmarkRun) # Pass Path object
        
    def get_with_results(self, benchmark_run_id: str) -> tuple[BenchmarkRun | None, list[TaskResult]]:
        """Get a benchmark run along with its associated task results."""
        benchmark_run = self.get_by_id(benchmark_run_id)
        if not benchmark_run:
            return None, []
        task_result_repo = TaskResultRepository()
        task_results = task_result_repo.get_by_benchmark_run(benchmark_run_id)
        return benchmark_run, task_results