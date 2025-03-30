"""
Core benchmark engine and service implementation.
"""

import asyncio
import time
from datetime import datetime
from typing import Any

from app.adapters.base import ModelAdapter
from app.enums import TaskStatusEnum
from app.exceptions import BenchmarkExecutionError, ValidationError
from app.services.benchmark_service.repositories import (
    BenchmarkRunRepository,
    TaskResultRepository,
)
from app.services.task_service.repositories import TaskRepository
from app.services.model_service.repositories import ModelRepository
from app.services.category_service.repositories import CategoryRepository
from app.services.model_service.models import Model
from app.services.task_service.models import Task
from .models import BenchmarkRun, TaskResult, ScoreComponent
from .enums import ScoreTypeEnum

from app.utils import get_logger


class BenchmarkEngine:
    """Core service for executing benchmarks against models."""

    def __init__(self):
        """Initialize the benchmark engine."""
        self.logger = get_logger("BenchmarkEngine")
        self.task_repo = TaskRepository()
        self.model_repo = ModelRepository()
        self.category_repo = CategoryRepository()
        self.benchmark_repo = BenchmarkRunRepository()
        self.task_result_repo = TaskResultRepository()

    async def run_single_task(
        self, task_id: str, model_id: str, benchmark_run_id: str | None = None
    ) -> TaskResult:
        """Execute a single task with a specific model."""
        start_time = time.time()
        
        # Get task and model
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise ValidationError(f"Task {task_id} not found")
            
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise ValidationError(f"Model {model_id} not found")
            
        # Create task result
        task_result = TaskResult(
            task_id=task_id,
            model_id=model_id,
            benchmark_run_id=benchmark_run_id,
        )
        
        try:
            # Initialize model adapter
            adapter = self._get_model_adapter(model)
            await adapter.initialize()
            
            # Execute task
            output = await adapter.generate(task.prompt)
            execution_time = time.time() - start_time
            
            # Update task result with metrics
            task_result.execution_time_seconds = execution_time
            task_result.output_data = {"response": output}
            token_count = await adapter.get_token_count(output)
            task_result.token_count = token_count
            
            # Save result
            await self.task_result_repo.create(task_result)
            
            return task_result
            
        except Exception as e:
            self.logger.error(f"Error executing task {task_id} with model {model_id}: {str(e)}")
            task_result.error = str(e)
            await self.task_result_repo.create(task_result)
            raise BenchmarkExecutionError(f"Task execution failed: {str(e)}")
            
        finally:
            if adapter:
                await adapter.cleanup()

    async def run_task_list(
        self, task_ids: list[str], model_id: str, benchmark_run_id: str | None = None
    ) -> list[TaskResult]:
        """Execute a list of tasks with a specific model."""
        results = []
        
        for task_id in task_ids:
            try:
                result = await self.run_single_task(task_id, model_id, benchmark_run_id)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error executing task {task_id}: {str(e)}")
                # Continue with next task even if one fails
                continue
                
        return results

    async def run_category(
        self, category_id: str, model_id: str, benchmark_run_id: str | None = None
    ) -> list[TaskResult]:
        """Execute all tasks in a category with a specific model."""
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise ValidationError(f"Category {category_id} not found")
            
        if not category.task_ids:
            raise ValidationError(f"Category {category_id} has no tasks")
            
        return await self.run_task_list(category.task_ids, model_id, benchmark_run_id)

    async def update_task_result_score(
        self, 
        task_result_id: str, 
        quality_score: float
    ) -> TaskResult:
        """Update task result with user-provided quality score and calculate ultimate score."""
        task_result = await self.task_result_repo.get_by_id(task_result_id)
        if not task_result:
            raise ValidationError(f"Task result {task_result_id} not found")
        
        # Get task for evaluation weights
        task = await self.task_repo.get_by_id(task_result.task_id)
        if not task:
            raise ValidationError(f"Task {task_result.task_id} not found")

        evaluation_weights = task.evaluation_weights or EvaluationWeights()
        
        # Update quality score
        task_result.quality_score = ScoreComponent(
            raw_score=quality_score,
            normalized_score=quality_score / 10.0,  # Normalize to 0-1 range
            weight=evaluation_weights.accuracy,
            description="User-provided quality score"
        )
        
        # Calculate time score (normalized between 0.8 and 1.2)
        time_score = 1.0
        if task_result.execution_time_seconds:
            if task.expected_output and task_result.execution_time_seconds > task.expected_output:
                time_score = max(0.8, 1.0 - (task_result.execution_time_seconds - task.expected_output) / task.expected_output)
            else:
                time_score = min(1.2, 1.0 + (task.expected_output - task_result.execution_time_seconds) / task.expected_output)
                
        task_result.time_score = ScoreComponent(
            raw_score=time_score,
            normalized_score=time_score,
            weight=evaluation_weights.latency,
            description="Execution time score"
        )
        
        # Set complexity score
        task_result.complexity_score = ScoreComponent(
            raw_score=evaluation_weights.complexity,
            normalized_score=evaluation_weights.complexity / 5.0,  # Normalize to 0-1 range
            weight=evaluation_weights.complexity,
            description="Task complexity score"
        )
        
        # Calculate ultimate score
        ultimate_score = (
            task_result.time_score.normalized_score * evaluation_weights.latency +
            task_result.quality_score.normalized_score * evaluation_weights.accuracy +
            task_result.complexity_score.normalized_score * evaluation_weights.complexity
        )
        
        if task_result.cost_score:
            ultimate_score += task_result.cost_score.normalized_score * evaluation_weights.cost_memory_usage
            
        if task_result.memory_score:
            ultimate_score += task_result.memory_score.normalized_score * evaluation_weights.cost_memory_usage
            
        task_result.ultimate_score = ultimate_score * 10  # Scale to 0-10 range
        
        # Save updated result
        await self.task_result_repo.update(task_result)
        
        return task_result
    
    def _get_model_adapter(self, model: Model) -> ModelAdapter:
        """Get the appropriate model adapter for a model."""
        from app.adapters.base import ModelAdapterFactory
        return ModelAdapterFactory.create_adapter(model)


class BenchmarkService:
    """Service for managing benchmark operations."""

    def __init__(self):
        """Initialize the benchmark service."""
        self.engine = BenchmarkEngine()
        self.benchmark_repo = BenchmarkRunRepository()
        self.logger = get_logger("BenchmarkService")

    async def create_benchmark_run(
        self,
        name: str,
        model_ids: list[str],
        category_ids: list[str] | None = None,
        task_ids: list[str] | None = None,
        description: str = "",
    ) -> BenchmarkRun:
        """Create a new benchmark run."""
        benchmark_run = BenchmarkRun(
            name=name,
            description=description,
            model_ids=model_ids,
            category_ids=category_ids,
            task_ids=task_ids,
            status=TaskStatusEnum.DRAFT
        )
        
        return await self.benchmark_repo.create(benchmark_run)

    async def start_benchmark_run(self, benchmark_run_id: str) -> BenchmarkRun:
        """Start executing a benchmark run."""
        benchmark_run = await self.benchmark_repo.get_by_id(benchmark_run_id)
        if not benchmark_run:
            raise ValidationError(f"Benchmark run {benchmark_run_id} not found")
            
        if benchmark_run.status != TaskStatusEnum.DRAFT:
            raise ValidationError(f"Benchmark run {benchmark_run_id} is not in DRAFT status")
            
        benchmark_run.status = TaskStatusEnum.IN_PROGRESS
        benchmark_run.start_time = datetime.now()
        await self.benchmark_repo.update(benchmark_run)
        
        try:
            # Execute tasks for each model
            for model_id in benchmark_run.model_ids:
                # Run category tasks if specified
                if benchmark_run.category_ids:
                    for category_id in benchmark_run.category_ids:
                        results = await self.engine.run_category(
                            category_id,
                            model_id,
                            benchmark_run_id
                        )
                        benchmark_run.task_results.extend([r.id for r in results])
                
                # Run individual tasks if specified
                if benchmark_run.task_ids:
                    results = await self.engine.run_task_list(
                        benchmark_run.task_ids,
                        model_id,
                        benchmark_run_id
                    )
                    benchmark_run.task_results.extend([r.id for r in results])
            
            benchmark_run.status = TaskStatusEnum.COMPLETED
            benchmark_run.end_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error executing benchmark run {benchmark_run_id}: {str(e)}")
            benchmark_run.status = TaskStatusEnum.ERROR
            benchmark_run.error = str(e)
            benchmark_run.end_time = datetime.now()
            raise BenchmarkExecutionError(f"Benchmark run failed: {str(e)}")
            
        finally:
            await self.benchmark_repo.update(benchmark_run)
            
        return benchmark_run

    async def get_benchmark_status(self, benchmark_run_id: str) -> dict[str, Any]:
        """Get the current status of a benchmark run."""
        benchmark_run = await self.benchmark_repo.get_by_id(benchmark_run_id)
        if not benchmark_run:
            raise ValidationError(f"Benchmark run {benchmark_run_id} not found")
            
        return {
            "id": benchmark_run.id,
            "name": benchmark_run.name,
            "status": benchmark_run.status.value,
            "start_time": benchmark_run.start_time,
            "end_time": benchmark_run.end_time,
            "progress": {
                "total_tasks": len(benchmark_run.task_results),
                "completed_tasks": len([r for r in benchmark_run.task_results if r.status == TaskStatusEnum.COMPLETED]),
                "error_tasks": len([r for r in benchmark_run.task_results if r.status == TaskStatusEnum.ERROR])
            },
            "is_active": benchmark_run.status == TaskStatusEnum.IN_PROGRESS,
            "error": benchmark_run.error
        }

    async def update_result_score(
        self,
        benchmark_run_id: str,
        task_result_id: str,
        quality_score: float,
        weights: dict[str, float] | None = None,
    ) -> TaskResult:
        """Update a task result with user scoring."""
        benchmark_run = await self.benchmark_repo.get_by_id(benchmark_run_id)
        if not benchmark_run:
            raise ValidationError(f"Benchmark run {benchmark_run_id} not found")
            
        if task_result_id not in benchmark_run.task_results:
            raise ValidationError(f"Task result {task_result_id} not found in benchmark run {benchmark_run_id}")
            
        default_weights = {
            "time": 0.2,
            "quality": 0.4,
            "complexity": 0.2,
            "cost": 0.1,
            "memory": 0.1
        }
        
        weights = weights or default_weights
        
        return await self.engine.update_task_result_score(
            task_result_id,
            quality_score,
            time_weight=weights.get("time", default_weights["time"]),
            quality_weight=weights.get("quality", default_weights["quality"]),
            complexity_weight=weights.get("complexity", default_weights["complexity"]),
            cost_weight=weights.get("cost", default_weights["cost"]),
            memory_weight=weights.get("memory", default_weights["memory"])
        )