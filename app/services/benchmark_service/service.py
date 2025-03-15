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

from app.utils import get_logger

from app.services.model_service.models import Model
from app.services.task_service.models import Task
from .models import BenchmarkRun, TaskResult, ScoreComponent


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

    async def execute_benchmark(self, benchmark_id: str) -> BenchmarkRun:
        """Execute a benchmark run."""
        benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
        if not benchmark_run:
            raise BenchmarkExecutionError(f"Benchmark run not found: {benchmark_id}")
        
        try:
            # Get models to benchmark
            models = []
            for model_id in benchmark_run.model_ids:
                if model := self.model_repo.get_by_id(model_id):
                    models.append(model)
                else:
                    raise BenchmarkExecutionError(f"Model not found: {model_id}")

            # Update status and start time
            benchmark_run.status = TaskStatusEnum.RUNNING
            benchmark_run.start_time = datetime.utcnow()
            self.benchmark_repo.update(benchmark_run)

            # Execute tasks for each model
            for model in models:
                self.logger.info(f"Running benchmark against model: {model.id}")
                model_score = 0.0
                tasks_completed = 0

                # Get tasks to run
                tasks_to_run = []
                if benchmark_run.task_ids:
                    for task_id in benchmark_run.task_ids:
                        if task := self.task_repo.get_by_id(task_id):
                            tasks_to_run.append(task)
                elif benchmark_run.category_ids:
                    # Get tasks from categories
                    for category_id in benchmark_run.category_ids:
                        if category := self.category_repo.get_by_id(category_id):
                            for task_id in category.task_ids:
                                if task := self.task_repo.get_by_id(task_id):
                                    tasks_to_run.append(task)

                # Execute each task
                for task in tasks_to_run:
                    try:
                        task_result = await self._execute_task(
                            task, model, benchmark_run.id
                        )
                        if task_result:
                            benchmark_run.task_results.append(task_result.id)
                            if task_result.ultimate_score:
                                model_score += task_result.ultimate_score
                                tasks_completed += 1

                    except Exception as e:
                        self.logger.error(
                            f"Task execution failed: {task.id}", exc_info=True
                        )
                        continue

                # Update aggregate scores
                if tasks_completed > 0:
                    if model.id not in benchmark_run.aggregate_scores:
                        benchmark_run.aggregate_scores[model.id] = {}
                    benchmark_run.aggregate_scores[model.id]["overall"] = model_score / tasks_completed

            # Update benchmark run status
            benchmark_run.status = TaskStatusEnum.COMPLETED
            benchmark_run.end_time = datetime.utcnow()
            self.benchmark_repo.update(benchmark_run)

            return benchmark_run  # Safe to return since we validated at start

        except Exception as exc:
            # Handle failure
            if benchmark_run:
                benchmark_run.status = TaskStatusEnum.FAILED
                benchmark_run.end_time = datetime.utcnow()
                benchmark_run.error = str(exc)
                self.benchmark_repo.update(benchmark_run)
                self.logger.error(f"Benchmark run failed: {benchmark_id}", exc_info=True)
                return benchmark_run  # Safe to return since we validated at start
            raise BenchmarkExecutionError(str(exc))

    async def _execute_task(
        self, task: Task, model: Model, benchmark_run_id: str
    ) -> TaskResult:
        """Execute a single task on a model."""

        # Create a new task result
        task_result = TaskResult(
            task_id=task.id,
            model_id=model.id,
            benchmark_run_id=benchmark_run_id
        )

        try:
            # Create model adapter
            adapter = ModelAdapterFactory.create_adapter(model)
            await adapter.initialize()

            # Execute model with prepared prompt
            prompt = self._prepare_prompt(task, template)
            start_time = time.time()
            
            try:
                response = await adapter.generate(prompt)
                task_result.execution_time_seconds = time.time() - start_time
                task_result.token_count = await adapter.get_token_count(prompt)
                task_result.output_data = self._process_output(response, template)

                # Evaluate results
                await self._evaluate_task_result(task_result, task, template)

            finally:
                await adapter.cleanup()

            return task_result

        except Exception as exc:
            task_result.error = str(exc)
            self.logger.error(
                f"Task execution failed: {task.id} for model {model.id}",
                exc_info=True
            )
            return task_result

    def _prepare_prompt(self, task: Task, template: Template) -> str:
        """Prepare the prompt for a task based on its template and input data."""
        # Validate required inputs are present
        for field_name, field_schema in template.input_schema.items():
            if field_schema.required and field_name not in task.input_data:
                raise ValidationError(f"Required input field missing: {field_name}")

        # Format prompt with task data
        prompt = f"Task: {task.name}\n\n"
        prompt += f"Description: {task.description}\n\n"
        prompt += "Input Data:\n"
        
        for key, value in task.input_data.items():
            prompt += f"{key}: {value}\n"

        return prompt

    def _process_output(self, response: Any, template: Template) -> dict[str, Any]:
        """Process the model output according to the template's output schema."""
        return {"raw_response": str(response)}

    async def _evaluate_task_result(
        self, task_result: TaskResult, task: Task, template: Template
    ) -> None:
        """Evaluate a task result and calculate scores."""
        # Get category for weights
        category = None
        if task.category_id:
            category = self.category_repo.get_by_id(task.category_id)

        # Use default weights if no category
        time_weight = category.time_weight if category else 1.0
        quality_weight = category.quality_weight if category else 1.0
        complexity_weight = category.complexity_weight if category else 1.0
        cost_weight = category.cost_weight if category else 1.0
        memory_weight = category.memory_weight if category else 1.0

        # Calculate time score (inverse relationship - faster is better)
        if task_result.execution_time_seconds is not None:
            # Normalize between 0.5 and 1.5 using inverse relationship
            time_score_raw = max(0.5, min(1.5, 1.0 / task_result.execution_time_seconds))
            task_result.time_score = ScoreComponent(
                raw_score=task_result.execution_time_seconds,
                normalized_score=time_score_raw,
                weight=time_weight,
                description=f"Execution time: {task_result.execution_time_seconds:.2f}s"
            )

        # Calculate memory score if available
        if task_result.memory_usage_mb is not None:
            # Normalize between 0.5 and 1.5 using inverse relationship (less memory is better)
            memory_score_raw = max(0.5, min(1.5, 100.0 / task_result.memory_usage_mb))
            task_result.memory_score = ScoreComponent(
                raw_score=task_result.memory_usage_mb,
                normalized_score=memory_score_raw,
                weight=memory_weight,
                description=f"Memory usage: {task_result.memory_usage_mb:.2f}MB"
            )

        # Calculate cost score based on token count if available
        if task_result.token_count is not None:
            # Normalize between 0.5 and 1.5 using inverse relationship (fewer tokens is better)
            cost_score_raw = max(0.5, min(1.5, 1000.0 / task_result.token_count))
            task_result.cost_score = ScoreComponent(
                raw_score=task_result.token_count,
                normalized_score=cost_score_raw,
                weight=cost_weight,
                description=f"Token count: {task_result.token_count}"
            )

        # Calculate quality score based on template evaluation criteria
        if template.evaluation_criteria and task_result.output_data:
            quality_score_raw = self._calculate_quality_score(
                task_result.output_data, 
                template.evaluation_criteria
            )
            task_result.quality_score = ScoreComponent(
                raw_score=quality_score_raw * 10,  # Scale to 0-10
                normalized_score=quality_score_raw,
                weight=quality_weight,
                description="Quality evaluation based on template criteria"
            )

        # Calculate complexity score based on task and template
        complexity_score_raw = self._calculate_complexity_score(task, template)
        task_result.complexity_score = ScoreComponent(
            raw_score=complexity_score_raw * 5,  # Scale to 0-5
            normalized_score=complexity_score_raw,
            weight=complexity_weight,
            description="Task complexity evaluation"
        )

        # Calculate ultimate score as weighted product of all scores
        score_components = []
        
        if task_result.time_score:
            score_components.append(
                task_result.time_score.normalized_score * task_result.time_score.weight
            )
        if task_result.quality_score:
            score_components.append(
                task_result.quality_score.normalized_score * task_result.quality_score.weight
            )
        if task_result.complexity_score:
            score_components.append(
                task_result.complexity_score.normalized_score * task_result.complexity_score.weight
            )
        if task_result.cost_score:
            score_components.append(
                task_result.cost_score.normalized_score * task_result.cost_score.weight
            )
        if task_result.memory_score:
            score_components.append(
                task_result.memory_score.normalized_score * task_result.memory_score.weight
            )

        # Calculate ultimate score as product of weighted components
        ultimate_score = 1.0
        for component in score_components:
            ultimate_score *= component

        # Scale to 0-100 range
        task_result.ultimate_score = ultimate_score * 100

    def _calculate_quality_score(
        self, output_data: dict[str, Any], evaluation_criteria: dict[str, Any]
    ) -> float:
        """Calculate quality score based on template evaluation criteria.
        
        Each criterion type has its own evaluation method and the final score
        is weighted based on the criteria weights.
        
        Returns:
            float: Normalized quality score between 0 and 1
        """
        total_weight = 0.0
        weighted_scores = 0.0
        
        for criterion_name, criterion_info in evaluation_criteria.items():
            weight = criterion_info.get("weight", 1.0)
            criterion_type = criterion_info.get("type")
            
            # Calculate score based on criterion type
            criterion_score = 0.0
            
            match criterion_type:
                case "unit_test":
                    # Check if test results are in output data
                    if test_results := output_data.get("test_results"):
                        passed = sum(1 for t in test_results if t.get("passed", False))
                        total = len(test_results)
                        criterion_score = passed / total if total > 0 else 0.0
                
                case "manual_review":
                    # Use provided manual review score if available
                    criterion_score = output_data.get(f"{criterion_name}_score", 0.0) / 10.0
                
                case "static_analysis":
                    # Check static analysis metrics if available
                    if analysis_results := output_data.get("static_analysis"):
                        # Convert issues to score (fewer issues = higher score)
                        issues = analysis_results.get("issues", 0)
                        criterion_score = max(0.0, 1.0 - (issues * 0.1))
                
                case "ground_truth_comparison":
                    # Compare with ground truth if available
                    if (ground_truth := output_data.get("ground_truth")) and \
                       (actual := output_data.get("actual_output")):
                        if isinstance(ground_truth, (list, dict)):
                            # Calculate similarity for structured data
                            if isinstance(ground_truth, dict):
                                matches = sum(1 for k, v in ground_truth.items() 
                                            if actual.get(k) == v)
                                total = len(ground_truth)
                            else:  # list
                                matches = sum(1 for i, v in enumerate(ground_truth)
                                            if i < len(actual) and actual[i] == v)
                                total = len(ground_truth)
                            criterion_score = matches / total if total > 0 else 0.0
                
                case "time_measurement":
                    # Convert time-based metrics to score
                    if execution_time := output_data.get("execution_time_ms"):
                        # Normalize time to score (faster = higher score)
                        # Using reasonable thresholds: 100ms = 1.0, 2000ms = 0.0
                        criterion_score = max(0.0, min(1.0, 
                            1.0 - (execution_time - 100) / 1900))
                
                case _:
                    self.logger.warning(
                        f"Unknown evaluation criterion type: {criterion_type}"
                    )
                    continue
            
            weighted_scores += criterion_score * weight
            total_weight += weight
        
        # Return normalized score between 0 and 1
        return weighted_scores / total_weight if total_weight > 0 else 0.0

    def _calculate_complexity_score(self, task: Task, template: Template) -> float:
        """Calculate complexity score based on task and template properties.
        
        Considers:
        - Input/output schema complexity
        - Number and types of evaluation criteria
        - Task-specific complexity factors
        
        Returns:
            float: Normalized complexity score between 0 and 1
        """
        # Base complexity starts at 0.3 (minimum complexity)
        complexity_score = 0.3
        
        # Add complexity based on input schema
        input_complexity = 0.0
        if template.input_schema:
            # Add complexity for each field type
            for field in template.input_schema.values():
                # Access type directly as attribute
                field_type = field.type.value  # Get enum value
                # Add extra complexity for required fields
                required_multiplier = 1.2 if field.required else 1.0
                
                match field_type:
                    case "image_path" | "file_path":
                        input_complexity += 0.05 * required_multiplier
                    case "json_object" | "dict":
                        input_complexity += 0.07 * required_multiplier
                    case "array" | "list":
                        input_complexity += 0.04 * required_multiplier
                    case _:
                        input_complexity += 0.02 * required_multiplier

            # Normalize input complexity (max 0.2)
            input_complexity = min(0.2, input_complexity)
            complexity_score += input_complexity
        
        # Add complexity based on output requirements
        output_complexity = 0.0
        if template.output_schema:
            for field in template.output_schema.values():
                # Access type directly as attribute
                field_type = field.type.value  # Get enum value
                match field_type:
                    case "json_object" | "dict":
                        output_complexity += 0.08  # Complex structured output
                    case "array" | "list":
                        output_complexity += 0.05  # List output
                    case "number" | "float":
                        output_complexity += 0.03  # Numerical precision adds complexity
                    case _:
                        output_complexity += 0.02  # Basic types
            
            # Normalize output complexity (max 0.2)
            output_complexity = min(0.2, output_complexity)
            complexity_score += output_complexity
        
        # Add complexity based on evaluation criteria
        eval_complexity = 0.0
        if template.evaluation_criteria:
            for criterion in template.evaluation_criteria.values():
                # Access type directly as attribute
                criterion_type = criterion.type.value  # Get enum value
                match criterion_type:
                    case "unit_test":
                        eval_complexity += 0.06  # Tests add significant complexity
                    case "ground_truth_comparison":
                        eval_complexity += 0.05  # Comparisons add moderate complexity
                    case "static_analysis":
                        eval_complexity += 0.04  # Code analysis adds complexity
                    case _:
                        eval_complexity += 0.02  # Basic evaluation types
            
            # Normalize evaluation complexity (max 0.2)
            eval_complexity = min(0.2, eval_complexity)
            complexity_score += eval_complexity
        
        # Add task-specific complexity factors
        task_complexity = 0.0
        
        # Consider task category if available
        if task.category_id:
            category = self.category_repo.get_by_id(task.category_id)
            if category:
                # Different categories might have different base complexity
                match category.name.lower():
                    case s if "coding" in s:
                        task_complexity += 0.08  # Coding tasks are generally complex
                    case s if "document" in s:
                        task_complexity += 0.06  # Document processing moderate complexity
                    case s if "recruitment" in s:
                        task_complexity += 0.04  # Recruitment tasks lower complexity
        
        # Consider task input data size/complexity
        if task.input_data:
            data_size = len(str(task.input_data))  # Rough estimate of data size
            # Add complexity for larger inputs (max 0.1)
            task_complexity += min(0.1, data_size / 10000)
        
        complexity_score += min(0.1, task_complexity)
        
        # Ensure final score is between 0 and 1
        return min(1.0, max(0.0, complexity_score))


class BenchmarkService:
    """Service for managing benchmark runs and results."""

    def __init__(self):
        """Initialize the benchmark service."""
        self.logger = get_logger("BenchmarkService")
        self.engine = BenchmarkEngine()
        self.benchmark_repo = BenchmarkRunRepository()
        self.task_repo = TaskRepository()  # Add task repo
        self.task_result_repo = TaskResultRepository()
        self.category_repo = CategoryRepository()
        self.model_repo = ModelRepository()
        self._active_runs: dict[str, asyncio.Task] = {}

    async def create_benchmark_run(
        self,
        name: str,
        model_ids: list[str],
        category_ids: None | list[str] = None,
        task_ids: None | list[str] = None,
        description: str = "",
    ) -> BenchmarkRun:
        """Create a new benchmark run."""
        if not category_ids and not task_ids:
            raise ValidationError("Either category_ids or task_ids must be provided")

        # Validate that models exist
        for model_id in model_ids:
            if not self.model_repo.get_by_id(model_id):
                raise ValidationError(f"Model not found: {model_id}")

        # Validate that categories exist if provided
        if category_ids:
            for category_id in category_ids:
                if not self.category_repo.get_by_id(category_id):
                    raise ValidationError(f"Category not found: {category_id}")

        # Create benchmark run
        benchmark_run = BenchmarkRun(
            name=name,
            description=description,
            model_ids=model_ids,
            category_ids=category_ids,
            task_ids=task_ids,
            status=TaskStatusEnum.READY,
        )

        if self.benchmark_repo.create(benchmark_run):
            self.logger.info(f"Created benchmark run: {benchmark_run.id}")
            return benchmark_run
        else:
            raise ValidationError("Failed to create benchmark run")

    async def start_benchmark(self, benchmark_id: str) -> BenchmarkRun:
        """Start a benchmark run asynchronously."""
        benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
        if not benchmark_run:
            raise ValidationError(f"Benchmark run not found: {benchmark_id}")

        if benchmark_run.status == TaskStatusEnum.RUNNING:
            raise ValidationError(f"Benchmark run already running: {benchmark_id}")

        if benchmark_run.status not in (TaskStatusEnum.READY, TaskStatusEnum.DRAFT):
            raise ValidationError(
                f"Benchmark run in invalid state: {benchmark_run.status}"
            )

        # Start the benchmark run asynchronously
        task = asyncio.create_task(self.engine.execute_benchmark(benchmark_id))
        self._active_runs[benchmark_id] = task

        # Get the updated benchmark run
        benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
        if not benchmark_run:
            raise ValidationError(f"Benchmark run not found: {benchmark_id}")

        self.logger.info(f"Started benchmark run: {benchmark_id}")
        return benchmark_run

    async def get_benchmark_status(self, benchmark_id: str) -> dict[str, Any]:
        """Get the status of a benchmark run."""
        benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
        if not benchmark_run:
            raise ValidationError(f"Benchmark run not found: {benchmark_id}")

        # Get task results if any
        task_results = []
        if benchmark_run.task_results:
            for result_id in benchmark_run.task_results:
                if result := self.task_result_repo.get_by_id(result_id):
                    task_results.append(result)

        # Calculate progress
        total_tasks = len(benchmark_run.task_ids) if benchmark_run.task_ids else 0
        if not total_tasks and benchmark_run.category_ids:
            for category_id in benchmark_run.category_ids:
                if category := self.category_repo.get_by_id(category_id):
                    total_tasks += len(category.task_ids)

        completed_tasks = len(task_results)

        # Check if still running
        is_active = (
            benchmark_id in self._active_runs 
            and not self._active_runs[benchmark_id].done()
        )

        return {
            "id": benchmark_run.id,
            "name": benchmark_run.name,
            "status": benchmark_run.status.value,
            "start_time": benchmark_run.start_time,
            "end_time": benchmark_run.end_time,
            "progress": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            "is_active": is_active,
            "error": benchmark_run.error
        }

    async def get_benchmark_results(self, benchmark_id: str) -> dict[str, Any]:
        """Get the results of a benchmark run."""
        benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
        if not benchmark_run:
            raise ValidationError(f"Benchmark run not found: {benchmark_id}")

        # Get task results
        task_results = []
        if benchmark_run.task_results:
            for result_id in benchmark_run.task_results:
                if result := self.task_result_repo.get_by_id(result_id):
                    task_results.append(result)

        # Get models
        models = {}
        for model_id in benchmark_run.model_ids:
            if model := self.model_repo.get_by_id(model_id):
                models[model_id] = {
                    "name": model.name,
                    "type": model.type.value
                }

        # Get categories
        categories = {}
        if benchmark_run.category_ids:
            for category_id in benchmark_run.category_ids:
                if category := self.category_repo.get_by_id(category_id):
                    categories[category_id] = {
                        "name": category.name,
                        "description": category.description
                    }

        # Organize results by model
        results_by_model: dict[str, dict[str, list[dict[str, Any]]]] = {}
        for model_id in benchmark_run.model_ids:
            results_by_model[model_id] = {}
            model_results = [r for r in task_results if r.model_id == model_id]

            # Group by category if categories are used
            if benchmark_run.category_ids:
                for category_id in benchmark_run.category_ids:
                    category_results = []
                    for r in model_results:
                        task = self.task_repo.get_by_id(r.task_id)
                        if task and task.category_id == category_id:
                            category_results.append(r.model_dump())
                    results_by_model[model_id][category_id] = category_results
            else:
                results_by_model[model_id]["uncategorized"] = [
                    r.model_dump() for r in model_results
                ]

        return {
            "benchmark_run": benchmark_run.model_dump(),
            "models": models,
            "categories": categories,
            "results_by_model": results_by_model,
            "aggregate_scores": benchmark_run.aggregate_scores
        }

    async def cancel_benchmark(self, benchmark_id: str) -> bool:
        """Cancel a running benchmark."""
        if benchmark_id in self._active_runs:
            task = self._active_runs[benchmark_id]
            if not task.done():
                task.cancel()
                benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
                if benchmark_run:
                    benchmark_run.status = TaskStatusEnum.FAILED  # Changed from CANCELLED to FAILED
                    benchmark_run.end_time = datetime.utcnow()
                    benchmark_run.error = "Benchmark cancelled by user"
                    self.benchmark_repo.update(benchmark_run)
                    self.logger.info(f"Cancelled benchmark run: {benchmark_id}")
                return True
        return False

    async def get_benchmark_run(self, benchmark_id: str) -> BenchmarkRun:
        """Get a benchmark run by ID.
        
        Raises:
            ValidationError: If benchmark run not found
        """
        benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
        if not benchmark_run:
            raise ValidationError(f"Benchmark run not found: {benchmark_id}")
        return benchmark_run # Safe since we raise if None

    async def list_benchmark_runs(self) -> list[BenchmarkRun]:
        """Get all benchmark runs."""
        return self.benchmark_repo.list_all()  # Fixed method name

    async def delete_benchmark(self, benchmark_id: str) -> None:
        """Delete a benchmark run and its results."""
        if benchmark_id in self._active_runs:
            raise ValidationError("Cannot delete active benchmark run")

        benchmark_run = await self.get_benchmark_run(benchmark_id)

        # Delete all associated task results
        for task_result_id in benchmark_run.task_results:
            self.task_result_repo.delete(task_result_id)

        # Delete benchmark run
        if not self.benchmark_repo.delete(benchmark_id):
            raise ValidationError("Failed to delete benchmark run")

        self.logger.info(f"Deleted benchmark run: {benchmark_id}")