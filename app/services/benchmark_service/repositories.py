"""
Repositories for benchmark service.
"""

import os
from app.config import settings
from app.services.benchmark_service.models import BenchmarkRun, TaskResult
from app.repositories import BaseRepository


class TaskResultRepository(BaseRepository[TaskResult]):
    """Repository for task result operations."""
    
    def __init__(self):
        """Initialize the task result repository."""
        directory = os.path.join(settings.RESULTS_DIR, "task_results")
        os.makedirs(directory, exist_ok=True)
        super().__init__(directory, TaskResult)
        
    def get_by_task(self, task_id: str) -> list[TaskResult]:
        """Get all results for a task."""
        result = []
        for task_result in self.list_all():
            if task_result.task_id == task_id:
                result.append(task_result)
        return result
        
    def get_by_model(self, model_id: str) -> list[TaskResult]:
        """Get all results for a model."""
        result = []
        for task_result in self.list_all():
            if task_result.model_id == model_id:
                result.append(task_result)
        return result
        
    def get_by_benchmark_run(self, benchmark_run_id: str) -> list[TaskResult]:
        """Get all results for a benchmark run."""
        result = []
        for task_result in self.list_all():
            if task_result.benchmark_run_id == benchmark_run_id:
                result.append(task_result)
        return result


class BenchmarkRunRepository(BaseRepository[BenchmarkRun]):
    """Repository for benchmark run operations."""
    
    def __init__(self):
        """Initialize the benchmark run repository."""
        directory = os.path.join(settings.RESULTS_DIR, "benchmark_runs")
        os.makedirs(directory, exist_ok=True)
        super().__init__(directory, BenchmarkRun)
        
    def get_with_results(self, benchmark_run_id: str) -> tuple[BenchmarkRun | None, list[TaskResult]]:
        """Get a benchmark run with its task results."""
        benchmark_run = self.get_by_id(benchmark_run_id)
        if not benchmark_run:
            return None, []
            
        task_result_repo = TaskResultRepository()
        return benchmark_run, task_result_repo.get_by_benchmark_run(benchmark_run_id)