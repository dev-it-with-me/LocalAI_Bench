"""
Core benchmark engine services for LocalAI Bench application.

This module contains services that implement the core benchmark engine logic,
including task execution, scoring calculation, and result management.
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, cast

from app.adapters.base import ModelAdapter, ModelAdapterFactory
from app.config import settings
from app.enums import TaskStatusEnum
from app.exceptions import BenchmarkExecutionError, ValidationError
from app.models import (
    BenchmarkRunModel,
    CategoryModel,
    ModelModel,
    ScoreComponentModel,
    TaskModel,
    TaskResultModel,
    TemplateModel,
)
from app.repositories import (
    BenchmarkRunRepository,
    CategoryRepository,
    ModelRepository,
    TaskRepository,
    TaskResultRepository,
    TemplateRepository,
)
from app.utils import get_logger

# Type variable for generic functions
T = TypeVar("T")


class BenchmarkEngine:
    """Core service for executing benchmarks against models."""

    def __init__(self):
        """Initialize the benchmark engine."""
        self.logger = get_logger("BenchmarkEngine")
        self.task_repo = TaskRepository()
        self.model_repo = ModelRepository()
        self.category_repo = CategoryRepository()
        self.template_repo = TemplateRepository()
        self.benchmark_repo = BenchmarkRunRepository()
        self.task_result_repo = TaskResultRepository()

    async def execute_benchmark(self, benchmark_id: str) -> BenchmarkRunModel:
        """Execute a benchmark run.
        
        Args:
            benchmark_id: ID of the benchmark run to execute
            
        Returns:
            The updated benchmark run model with results
            
        Raises:
            BenchmarkExecutionError: If benchmark execution fails
        """
        # Get the benchmark run
        benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
        if not benchmark_run:
            raise BenchmarkExecutionError(
                f"Benchmark run not found: {benchmark_id}",
                benchmark_id=benchmark_id
            )
            
        # Update status and start time
        benchmark_run.status = TaskStatusEnum.RUNNING
        benchmark_run.start_time = datetime.utcnow()
        self.benchmark_repo.update(benchmark_run)
        
        self.logger.info(f"Starting benchmark run: {benchmark_id}")
        
        try:
            # Get models to benchmark
            models = []
            for model_id in benchmark_run.model_ids:
                model = self.model_repo.get_by_id(model_id)
                if not model:
                    raise BenchmarkExecutionError(
                        f"Model not found: {model_id}",
                        benchmark_id=benchmark_id,
                        model_id=model_id
                    )
                models.append(model)
            
            # Get tasks to execute
            tasks = []
            if benchmark_run.task_ids:
                # Execute specific tasks
                for task_id in benchmark_run.task_ids:
                    task = self.task_repo.get_by_id(task_id)
                    if not task:
                        raise BenchmarkExecutionError(
                            f"Task not found: {task_id}",
                            benchmark_id=benchmark_id,
                            task_id=task_id
                        )
                    tasks.append(task)
            elif benchmark_run.category_ids:
                # Execute all tasks in the specified categories
                for category_id in benchmark_run.category_ids:
                    category, category_tasks = self.category_repo.get_with_tasks(category_id)
                    if not category:
                        raise BenchmarkExecutionError(
                            f"Category not found: {category_id}",
                            benchmark_id=benchmark_id
                        )
                    tasks.extend(category_tasks)
            else:
                raise BenchmarkExecutionError(
                    "No tasks or categories specified for benchmark",
                    benchmark_id=benchmark_id
                )
            
            # Execute tasks for each model
            benchmark_run.task_results = []
            benchmark_run.aggregate_scores = {}
            
            for model in models:
                model_scores_by_category: Dict[str, List[float]] = {}
                self.logger.info(f"Benchmarking model: {model.name} ({model.id})")
                
                for task in tasks:
                    self.logger.info(f"Executing task: {task.name} ({task.id})")
                    
                    # Execute task and get result
                    task_result = await self._execute_task(task, model, benchmark_id)
                    
                    # Save task result
                    if self.task_result_repo.create(task_result):
                        benchmark_run.task_results.append(task_result.id)
                    
                    # Group scores by category for aggregation
                    if task.category_id and task_result.ultimate_score is not None:
                        if task.category_id not in model_scores_by_category:
                            model_scores_by_category[task.category_id] = []
                        model_scores_by_category[task.category_id].append(task_result.ultimate_score)
                
                # Calculate aggregate scores by category
                benchmark_run.aggregate_scores[model.id] = {}
                for category_id, scores in model_scores_by_category.items():
                    if scores:
                        benchmark_run.aggregate_scores[model.id][category_id] = sum(scores) / len(scores)
            
            # Update benchmark run status
            benchmark_run.status = TaskStatusEnum.COMPLETED
            benchmark_run.end_time = datetime.utcnow()
            self.benchmark_repo.update(benchmark_run)
            
            self.logger.info(f"Benchmark run completed: {benchmark_id}")
            return benchmark_run
            
        except Exception as e:
            # Update benchmark run status on error
            benchmark_run.status = TaskStatusEnum.FAILED
            benchmark_run.end_time = datetime.utcnow()
            benchmark_run.error = str(e)
            self.benchmark_repo.update(benchmark_run)
            
            self.logger.error(f"Benchmark run failed: {benchmark_id}", exc_info=True)
            raise BenchmarkExecutionError(
                f"Benchmark execution failed: {str(e)}",
                benchmark_id=benchmark_id
            )

    async def _execute_task(
        self, task: TaskModel, model: ModelModel, benchmark_run_id: str
    ) -> TaskResultModel:
        """Execute a single task on a model.
        
        Args:
            task: The task to execute
            model: The model to use
            benchmark_run_id: ID of the benchmark run
            
        Returns:
            Task result with execution metrics and scores
        """
        template = self.template_repo.get_by_id(task.template_id)
        if not template:
            raise BenchmarkExecutionError(
                f"Template not found: {task.template_id}",
                task_id=task.id,
                model_id=model.id
            )
        
        # Create a new task result
        task_result = TaskResultModel(
            task_id=task.id,
            model_id=model.id,
            benchmark_run_id=benchmark_run_id
        )
        
        try:
            # Create model adapter
            adapter = ModelAdapterFactory.create_adapter(model)
            await adapter.initialize()
            
            # Prepare input prompt based on template and task input
            prompt = self._prepare_prompt(task, template)
            
            # Execute model
            start_time = time.time()
            
            try:
                # Generate response from model
                response = await adapter.generate(prompt)
                
                # Process response
                output_data = self._process_output(response, template)
                task_result.output_data = output_data
                
                # Calculate token count
                task_result.token_count = await adapter.get_token_count(prompt + str(response))
                
            finally:
                # Always record execution time
                execution_time = time.time() - start_time
                task_result.execution_time_seconds = execution_time
                
                # Clean up adapter resources
                await adapter.cleanup()
            
            # Evaluate the result
            await self._evaluate_task_result(task_result, task, template)
            
            return task_result
            
        except Exception as e:
            # Handle exceptions and create error result
            task_result.error = str(e)
            self.logger.error(
                f"Task execution failed: {task.id} on model {model.id}",
                exc_info=True
            )
            return task_result

    def _prepare_prompt(self, task: TaskModel, template: TemplateModel) -> str:
        """Prepare the prompt for a task based on its template and input data.
        
        Args:
            task: The task to prepare prompt for
            template: The template to use
            
        Returns:
            The prepared prompt string
            
        Raises:
            ValidationError: If required input fields are missing
        """
        # This is a simplified implementation
        # In a real system, this would handle various prompt formats
        # and input schemas based on template requirements
        
        # Validate required inputs are present
        for field_name, field_schema in template.input_schema.items():
            if field_schema.required and field_name not in task.input_data:
                raise ValidationError(
                    f"Required input field '{field_name}' missing",
                    field=field_name
                )
        
        # In a real implementation, we would format a prompt based on the template
        # For now, we'll just use a simple format that includes task description
        # and input data as a formatted string
        prompt = f"Task: {task.name}\n\n"
        prompt += f"Description: {task.description}\n\n"
        prompt += "Input Data:\n"
        
        for key, value in task.input_data.items():
            prompt += f"{key}: {value}\n"
            
        return prompt

    def _process_output(self, response: Any, template: TemplateModel) -> Dict[str, Any]:
        """Process the model output according to the template's output schema.
        
        Args:
            response: The raw model output
            template: The template with output schema
            
        Returns:
            Processed output data conforming to the schema
        """
        # In a real implementation, this would process the response
        # to extract structured data according to the output schema
        
        # For now, we'll return a simple dict with the raw response
        return {"raw_response": str(response)}

    async def _evaluate_task_result(
        self, task_result: TaskResultModel, task: TaskModel, template: TemplateModel
    ) -> None:
        """Evaluate a task result and calculate scores.
        
        Args:
            task_result: The task result to evaluate
            task: The original task
            template: The task template
            
        Modifies task_result in place to add scores.
        """
        # Get category for weights
        category = None
        if task.category_id:
            category = self.category_repo.get_by_id(task.category_id)
        
        # Use default weights if no category
        time_weight = 1.0
        quality_weight = 1.0
        complexity_weight = 1.0
        cost_weight = 1.0
        memory_weight = 1.0
        
        if category:
            time_weight = category.time_weight
            quality_weight = category.quality_weight
            complexity_weight = category.complexity_weight
            cost_weight = category.cost_weight
            memory_weight = category.memory_weight
        
        # Calculate time score - normalize between 0.8 and 1.2
        # Lower execution time is better (higher score)
        if task_result.execution_time_seconds is not None:
            time_score_raw = max(0.8, min(1.2, 1.0 / (task_result.execution_time_seconds / 10.0 + 0.5)))
            task_result.time_score = ScoreComponentModel(
                raw_score=task_result.execution_time_seconds,
                normalized_score=time_score_raw,
                weight=time_weight,
                description=f"Execution time: {task_result.execution_time_seconds:.2f}s"
            )
        
        # For other scores, in a real implementation, we would:
        # 1. Run automated evaluations based on template.evaluation_criteria
        # 2. For manual review criteria, either skip or use default values
        
        # For this implementation, we'll use placeholder values:
        
        # Quality score (placeholder - would normally be based on evaluation)
        quality_score_raw = 0.7  # Default placeholder value (70%)
        task_result.quality_score = ScoreComponentModel(
            raw_score=quality_score_raw * 10,  # Scale to 1-10
            normalized_score=quality_score_raw,
            weight=quality_weight,
            description="Quality evaluation placeholder"
        )
        
        # Complexity score (based on template)
        complexity_level = 3  # Medium complexity (1-5 scale)
        complexity_score_normalized = complexity_level / 5.0
        task_result.complexity_score = ScoreComponentModel(
            raw_score=complexity_level,
            normalized_score=complexity_score_normalized,
            weight=complexity_weight,
            description=f"Task complexity level: {complexity_level}/5"
        )
        
        # Cost score based on token count
        if task_result.token_count:
            # Lower token count is better (higher score)
            cost_score_raw = max(0.5, min(1.0, 10000 / (task_result.token_count + 1000)))
            task_result.cost_score = ScoreComponentModel(
                raw_score=task_result.token_count,
                normalized_score=cost_score_raw,
                weight=cost_weight,
                description=f"Token count: {task_result.token_count}"
            )
        
        # Memory score (placeholder - would be measured during execution)
        memory_usage = 1024.0  # Placeholder MB
        task_result.memory_usage_mb = memory_usage
        memory_score_raw = max(0.5, min(1.0, 2048 / (memory_usage + 100)))
        task_result.memory_score = ScoreComponentModel(
            raw_score=memory_usage,
            normalized_score=memory_score_raw,
            weight=memory_weight,
            description=f"Memory usage: {memory_usage:.1f}MB"
        )
        
        # Calculate ultimate score using the formula from the project plan
        score_components = []
        
        if task_result.time_score:
            score_components.append(task_result.time_score.normalized_score * task_result.time_score.weight)
        if task_result.quality_score:
            score_components.append(task_result.quality_score.normalized_score * task_result.quality_score.weight)
        if task_result.complexity_score:
            score_components.append(task_result.complexity_score.normalized_score * task_result.complexity_score.weight)
        if task_result.cost_score:
            score_components.append(task_result.cost_score.normalized_score * task_result.cost_score.weight)
        if task_result.memory_score:
            score_components.append(task_result.memory_score.normalized_score * task_result.memory_score.weight)
        
        # Calculate ultimate score as product of weighted components
        ultimate_score = 1.0
        for component in score_components:
            ultimate_score *= component
        
        # Scale to 0-100 range for better readability
        task_result.ultimate_score = ultimate_score * 100


class BenchmarkService:
    """Service for managing benchmark runs and results."""

    def __init__(self):
        """Initialize the benchmark service."""
        self.logger = get_logger("BenchmarkService")
        self.engine = BenchmarkEngine()
        self.benchmark_repo = BenchmarkRunRepository()
        self.task_result_repo = TaskResultRepository()
        self.category_repo = CategoryRepository()
        self.model_repo = ModelRepository()
        self._active_runs: Dict[str, asyncio.Task] = {}

    async def create_benchmark_run(
        self,
        name: str,
        model_ids: List[str],
        category_ids: Optional[List[str]] = None,
        task_ids: Optional[List[str]] = None,
        description: str = "",
    ) -> BenchmarkRunModel:
        """Create a new benchmark run.
        
        Args:
            name: Name of the benchmark run
            model_ids: List of model IDs to benchmark
            category_ids: Optional list of category IDs to benchmark
            task_ids: Optional list of task IDs to benchmark
            description: Optional description
            
        Returns:
            The created benchmark run
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate at least one of category_ids or task_ids is provided
        if not category_ids and not task_ids:
            raise ValidationError(
                "Either category_ids or task_ids must be provided"
            )
            
        # Validate that models exist
        for model_id in model_ids:
            if not self.model_repo.exists(model_id):
                raise ValidationError(
                    f"Model not found: {model_id}",
                    field="model_ids"
                )
        
        # Validate that categories exist if provided
        if category_ids:
            for category_id in category_ids:
                if not self.category_repo.exists(category_id):
                    raise ValidationError(
                        f"Category not found: {category_id}",
                        field="category_ids"
                    )
        
        # Create benchmark run
        benchmark_run = BenchmarkRunModel(
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

    async def start_benchmark(self, benchmark_id: str) -> BenchmarkRunModel:
        """Start a benchmark run asynchronously.
        
        Args:
            benchmark_id: ID of the benchmark run to start
            
        Returns:
            The updated benchmark run
            
        Raises:
            BenchmarkExecutionError: If benchmark cannot be started
        """
        # Check if benchmark exists
        benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
        if not benchmark_run:
            raise BenchmarkExecutionError(
                f"Benchmark run not found: {benchmark_id}",
                benchmark_id=benchmark_id
            )
        
        # Check if benchmark is in a state where it can be started
        if benchmark_run.status == TaskStatusEnum.RUNNING:
            self.logger.warning(f"Benchmark run already running: {benchmark_id}")
            return benchmark_run
        
        if benchmark_run.status not in (TaskStatusEnum.READY, TaskStatusEnum.DRAFT):
            raise BenchmarkExecutionError(
                f"Benchmark run cannot be started in status: {benchmark_run.status.value}",
                benchmark_id=benchmark_id
            )
        
        # Start the benchmark run asynchronously
        task = asyncio.create_task(self.engine.execute_benchmark(benchmark_id))
        self._active_runs[benchmark_id] = task
        
        # Get the updated benchmark run
        benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
        
        self.logger.info(f"Started benchmark run: {benchmark_id}")
        return benchmark_run or cast(BenchmarkRunModel, None)

    async def get_benchmark_status(self, benchmark_id: str) -> Dict[str, Any]:
        """Get the status of a benchmark run.
        
        Args:
            benchmark_id: ID of the benchmark run
            
        Returns:
            Dictionary with status information
        """
        benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
        if not benchmark_run:
            raise BenchmarkExecutionError(
                f"Benchmark run not found: {benchmark_id}",
                benchmark_id=benchmark_id
            )
        
        # Get task results if any
        task_results = []
        if benchmark_run.task_results:
            task_results = [
                self.task_result_repo.get_by_id(result_id)
                for result_id in benchmark_run.task_results
            ]
            task_results = [r for r in task_results if r is not None]
        
        # Calculate progress
        total_tasks = 0
        completed_tasks = 0
        
        if benchmark_run.task_ids:
            total_tasks = len(benchmark_run.task_ids) * len(benchmark_run.model_ids)
        elif benchmark_run.category_ids:
            # Count tasks in categories
            for category_id in benchmark_run.category_ids:
                category = self.category_repo.get_by_id(category_id)
                if category:
                    total_tasks += len(category.task_ids) * len(benchmark_run.model_ids)
        
        completed_tasks = len(task_results)
        
        # Check if still running in _active_runs
        is_active = benchmark_id in self._active_runs and not self._active_runs[benchmark_id].done()
        
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

    async def get_benchmark_results(self, benchmark_id: str) -> Dict[str, Any]:
        """Get the results of a benchmark run.
        
        Args:
            benchmark_id: ID of the benchmark run
            
        Returns:
            Dictionary with benchmark results
        """
        benchmark_run, task_results = self.benchmark_repo.get_with_results(benchmark_id)
        if not benchmark_run:
            raise BenchmarkExecutionError(
                f"Benchmark run not found: {benchmark_id}",
                benchmark_id=benchmark_id
            )
        
        # Get models
        models = {}
        for model_id in benchmark_run.model_ids:
            model = self.model_repo.get_by_id(model_id)
            if model:
                models[model_id] = {"id": model_id, "name": model.name}
        
        # Get categories if specified
        categories = {}
        if benchmark_run.category_ids:
            for category_id in benchmark_run.category_ids:
                category = self.category_repo.get_by_id(category_id)
                if category:
                    categories[category_id] = {"id": category_id, "name": category.name}
        
        # Organize results by model and category
        results_by_model: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        
        for task_result in task_results:
            task = self.task_repo.get_by_id(task_result.task_id)
            if not task:
                continue
                
            category_id = task.category_id or "uncategorized"
            
            if task_result.model_id not in results_by_model:
                results_by_model[task_result.model_id] = {}
                
            if category_id not in results_by_model[task_result.model_id]:
                results_by_model[task_result.model_id][category_id] = []
            
            # Add task result
            results_by_model[task_result.model_id][category_id].append({
                "id": task_result.id,
                "task_id": task_result.task_id,
                "task_name": task.name if task else task_result.task_id,
                "execution_time": task_result.execution_time_seconds,
                "token_count": task_result.token_count,
                "memory_usage": task_result.memory_usage_mb,
                "ultimate_score": task_result.ultimate_score,
                "error": task_result.error,
            })
        
        return {
            "benchmark_run": {
                "id": benchmark_run.id,
                "name": benchmark_run.name,
                "status": benchmark_run.status.value,
                "start_time": benchmark_run.start_time,
                "end_time": benchmark_run.end_time,
            },
            "models": models,
            "categories": categories,
            "results_by_model": results_by_model,
            "aggregate_scores": benchmark_run.aggregate_scores
        }

    async def cancel_benchmark(self, benchmark_id: str) -> bool:
        """Cancel a running benchmark.
        
        Args:
            benchmark_id: ID of the benchmark run to cancel
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        if benchmark_id in self._active_runs:
            task = self._active_runs[benchmark_id]
            if not task.done():
                task.cancel()
                
            # Update benchmark run status
            benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
            if benchmark_run and benchmark_run.status == TaskStatusEnum.RUNNING:
                benchmark_run.status = TaskStatusEnum.FAILED
                benchmark_run.error = "Benchmark cancelled by user"
                benchmark_run.end_time = datetime.utcnow()
                self.benchmark_repo.update(benchmark_run)
                
            self.logger.info(f"Cancelled benchmark run: {benchmark_id}")
            return True
            
        return False

    async def get_benchmark_run(self, benchmark_id: str) -> BenchmarkRunModel:
        """Get a benchmark run by ID.

        Args:
            benchmark_id: ID of the benchmark run

        Returns:
            The benchmark run model

        Raises:
            ValidationError: If benchmark run not found
        """
        benchmark_run = self.benchmark_repo.get_by_id(benchmark_id)
        if not benchmark_run:
            raise ValidationError(
                f"Benchmark run not found: {benchmark_id}",
                details={"benchmark_id": benchmark_id}
            )
        return benchmark_run

    async def list_benchmark_runs(self) -> List[BenchmarkRunModel]:
        """Get all benchmark runs.

        Returns:
            List of benchmark run models
        """
        return self.benchmark_repo.get_all()

    async def delete_benchmark(self, benchmark_id: str) -> None:
        """Delete a benchmark run and its results.

        Args:
            benchmark_id: ID of the benchmark run to delete

        Raises:
            ValidationError: If benchmark run not found or still running
        """
        # Check if benchmark is running
        if benchmark_id in self._active_runs:
            raise ValidationError(
                f"Cannot delete active benchmark run: {benchmark_id}",
                details={"benchmark_id": benchmark_id}
            )

        # Get benchmark run for results cleanup
        benchmark_run = await self.get_benchmark_run(benchmark_id)

        # Delete all associated task results
        for task_result_id in benchmark_run.task_results:
            self.task_result_repo.delete(task_result_id)

        # Delete benchmark run
        if not self.benchmark_repo.delete(benchmark_id):
            raise ValidationError(
                f"Failed to delete benchmark run: {benchmark_id}",
                details={"benchmark_id": benchmark_id}
            )

        self.logger.info(f"Deleted benchmark run: {benchmark_id}")


class ModelService:
    """Service for managing AI models."""

    def __init__(self):
        """Initialize the model service."""
        self.logger = get_logger("ModelService")
        self.model_repo = ModelRepository()
        self.model_factory = ModelAdapterFactory()

    async def create_model(
        self,
        name: str,
        type: ModelTypeEnum,
        model_id: str,
        description: str = "",
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        memory_required: Optional[float] = None,
        gpu_required: bool = False,
        quantization: Optional[str] = None,
    ) -> ModelModel:
        """Create a new model.
        
        Args:
            name: Display name for the model
            type: Type of the model (HuggingFace, Ollama, etc.)
            model_id: Model identifier in its source system
            description: Optional description
            api_url: Optional API URL for hosted models
            api_key: Optional API key for authentication
            api_version: Optional API version
            parameters: Optional model parameters
            memory_required: Optional memory requirement in MB
            gpu_required: Whether GPU is required
            quantization: Optional quantization settings
            
        Returns:
            Created model
            
        Raises:
            ValidationError: If validation fails
        """
        model = ModelModel(
            name=name,
            type=type,
            model_id=model_id,
            description=description,
            api_url=api_url,
            api_key=api_key,
            api_version=api_version,
            parameters=ModelParametersSchema(**(parameters or {})),
            memory_required=memory_required,
            gpu_required=gpu_required,
            quantization=quantization
        )
        
        if self.model_repo.create(model):
            self.logger.info(f"Created model: {model.id} ({name})")
            return model
        else:
            raise ValidationError("Failed to create model")

    async def get_model(self, model_id: str) -> ModelModel:
        """Get a model by ID.
        
        Args:
            model_id: ID of the model
            
        Returns:
            The model
            
        Raises:
            ValidationError: If model not found
        """
        model = self.model_repo.get_by_id(model_id)
        if not model:
            raise ValidationError(
                f"Model not found: {model_id}",
                details={"model_id": model_id}
            )
        return model

    async def list_models(self, type: Optional[ModelTypeEnum] = None) -> List[ModelModel]:
        """Get all models, optionally filtered by type.
        
        Args:
            type: Optional model type to filter by
            
        Returns:
            List of models
        """
        models = self.model_repo.get_all()
        if type:
            models = [m for m in models if m.type == type]
        return models

    async def update_model(
        self,
        model_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        memory_required: Optional[float] = None,
        gpu_required: Optional[bool] = None,
        quantization: Optional[str] = None,
    ) -> ModelModel:
        """Update a model.
        
        Args:
            model_id: ID of the model to update
            name: Optional new name
            description: Optional new description
            api_url: Optional new API URL
            api_key: Optional new API key
            api_version: Optional new API version
            parameters: Optional new parameters
            memory_required: Optional new memory requirement
            gpu_required: Optional new GPU requirement
            quantization: Optional new quantization settings
            
        Returns:
            Updated model
            
        Raises:
            ValidationError: If model not found or validation fails
        """
        model = await self.get_model(model_id)
        
        # Update fields if provided
        if name is not None:
            model.name = name
        if description is not None:
            model.description = description
        if api_url is not None:
            model.api_url = api_url
        if api_key is not None:
            model.api_key = api_key
        if api_version is not None:
            model.api_version = api_version
        if parameters is not None:
            model.parameters = ModelParametersSchema(**parameters)
        if memory_required is not None:
            model.memory_required = memory_required
        if gpu_required is not None:
            model.gpu_required = gpu_required
        if quantization is not None:
            model.quantization = quantization
            
        if self.model_repo.update(model):
            self.logger.info(f"Updated model: {model.id}")
            return model
        else:
            raise ValidationError("Failed to update model")

    async def delete_model(self, model_id: str) -> None:
        """Delete a model.
        
        Args:
            model_id: ID of the model to delete
            
        Raises:
            ValidationError: If model not found or deletion fails
        """
        # Check if model exists
        await self.get_model(model_id)
        
        # Delete model
        if not self.model_repo.delete(model_id):
            raise ValidationError(
                f"Failed to delete model: {model_id}",
                details={"model_id": model_id}
            )
            
        self.logger.info(f"Deleted model: {model_id}")

    async def test_model(self, model_id: str) -> Dict[str, Any]:
        """Test model connectivity and functionality.
        
        Args:
            model_id: ID of the model to test
            
        Returns:
            Dictionary with test results
            
        Raises:
            ValidationError: If model not found
            ModelTestError: If test fails
        """
        model = await self.get_model(model_id)
        
        try:
            # Create adapter for model
            adapter = self.model_factory.create_adapter(model)
            
            # Initialize adapter
            start_time = time.time()
            await adapter.initialize()
            init_time = time.time() - start_time
            
            # Test with simple prompt
            test_prompt = "Test prompt: 1 + 1 ="
            start_time = time.time()
            response = await adapter.generate(test_prompt)
            generation_time = time.time() - start_time
            
            # Get token count
            token_count = await adapter.get_token_count(test_prompt)
            
            return {
                "status": "success",
                "initialization_time": init_time,
                "generation_time": generation_time,
                "token_count": token_count,
                "response": response
            }
            
        except Exception as e:
            self.logger.error(f"Model test failed: {model_id}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
        finally:
            if 'adapter' in locals():
                await adapter.cleanup()


class CategoryService:
    """Service for managing benchmark categories."""

    def __init__(self):
        """Initialize the category service."""
        self.logger = get_logger("CategoryService")
        self.category_repo = CategoryRepository()
        self.task_repo = TaskRepository()

    async def create_category(
        self,
        name: str,
        description: str = "",
        time_weight: float = 1.0,
        quality_weight: float = 1.0,
        complexity_weight: float = 1.0,
        cost_weight: float = 1.0,
        memory_weight: float = 1.0,
    ) -> CategoryModel:
        """Create a new category.
        
        Args:
            name: Name of the category
            description: Optional description
            time_weight: Weight for time score (0-5)
            quality_weight: Weight for quality score (0-5)
            complexity_weight: Weight for complexity score (0-5)
            cost_weight: Weight for cost score (0-5)
            memory_weight: Weight for memory score (0-5)
            
        Returns:
            Created category
            
        Raises:
            ValidationError: If validation fails
        """
        category = CategoryModel(
            name=name,
            description=description,
            time_weight=time_weight,
            quality_weight=quality_weight,
            complexity_weight=complexity_weight,
            cost_weight=cost_weight,
            memory_weight=memory_weight,
            task_ids=[]
        )
        
        if self.category_repo.create(category):
            self.logger.info(f"Created category: {category.id} ({name})")
            return category
        else:
            raise ValidationError("Failed to create category")

    async def get_category(self, category_id: str) -> CategoryModel:
        """Get a category by ID.
        
        Args:
            category_id: ID of the category
            
        Returns:
            The category
            
        Raises:
            ValidationError: If category not found
        """
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise ValidationError(
                f"Category not found: {category_id}",
                details={"category_id": category_id}
            )
        return category

    async def list_categories(self) -> List[CategoryModel]:
        """Get all categories.
        
        Returns:
            List of categories
        """
        return self.category_repo.get_all()

    async def update_category(
        self,
        category_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        time_weight: Optional[float] = None,
        quality_weight: Optional[float] = None,
        complexity_weight: Optional[float] = None,
        cost_weight: Optional[float] = None,
        memory_weight: Optional[float] = None,
    ) -> CategoryModel:
        """Update a category.
        
        Args:
            category_id: ID of the category to update
            name: Optional new name
            description: Optional new description
            time_weight: Optional new time weight
            quality_weight: Optional new quality weight
            complexity_weight: Optional new complexity weight
            cost_weight: Optional new cost weight
            memory_weight: Optional new memory weight
            
        Returns:
            Updated category
            
        Raises:
            ValidationError: If category not found or validation fails
        """
        category = await self.get_category(category_id)
        
        # Update fields if provided
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        if time_weight is not None:
            category.time_weight = time_weight
        if quality_weight is not None:
            category.quality_weight = quality_weight
        if complexity_weight is not None:
            category.complexity_weight = complexity_weight
        if cost_weight is not None:
            category.cost_weight = cost_weight
        if memory_weight is not None:
            category.memory_weight = memory_weight
            
        if self.category_repo.update(category):
            self.logger.info(f"Updated category: {category.id}")
            return category
        else:
            raise ValidationError("Failed to update category")

    async def delete_category(self, category_id: str) -> None:
        """Delete a category.
        
        Args:
            category_id: ID of the category to delete
            
        Raises:
            ValidationError: If category not found or has associated tasks
        """
        category = await self.get_category(category_id)
        
        # Check if category has tasks
        if category.task_ids:
            raise ValidationError(
                f"Cannot delete category with associated tasks: {category_id}",
                details={
                    "category_id": category_id,
                    "task_count": len(category.task_ids)
                }
            )
        
        # Delete category
        if not self.category_repo.delete(category_id):
            raise ValidationError(
                f"Failed to delete category: {category_id}",
                details={"category_id": category_id}
            )
            
        self.logger.info(f"Deleted category: {category_id}")

    async def get_category_tasks(self, category_id: str) -> List[TaskModel]:
        """Get all tasks in a category.
        
        Args:
            category_id: ID of the category
            
        Returns:
            List of tasks in the category
            
        Raises:
            ValidationError: If category not found
        """
        category = await self.get_category(category_id)
        
        tasks = []
        for task_id in category.task_ids:
            task = self.task_repo.get_by_id(task_id)
            if task:
                tasks.append(task)
                
        return tasks

    async def add_task_to_category(
        self, category_id: str, task_id: str
    ) -> CategoryModel:
        """Add a task to a category.
        
        Args:
            category_id: ID of the category
            task_id: ID of the task to add
            
        Returns:
            Updated category
            
        Raises:
            ValidationError: If category or task not found
        """
        category = await self.get_category(category_id)
        
        # Check if task exists
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValidationError(
                f"Task not found: {task_id}",
                details={"task_id": task_id}
            )
        
        # Check if task already in category
        if task_id in category.task_ids:
            raise ValidationError(
                f"Task already in category: {task_id}",
                details={
                    "category_id": category_id,
                    "task_id": task_id
                }
            )
        
        # Add task to category
        category.task_ids.append(task_id)
        
        if self.category_repo.update(category):
            self.logger.info(f"Added task {task_id} to category {category_id}")
            return category
        else:
            raise ValidationError("Failed to update category")

    async def remove_task_from_category(
        self, category_id: str, task_id: str
    ) -> CategoryModel:
        """Remove a task from a category.
        
        Args:
            category_id: ID of the category
            task_id: ID of the task to remove
            
        Returns:
            Updated category
            
        Raises:
            ValidationError: If category not found or task not in category
        """
        category = await self.get_category(category_id)
        
        # Check if task in category
        if task_id not in category.task_ids:
            raise ValidationError(
                f"Task not in category: {task_id}",
                details={
                    "category_id": category_id,
                    "task_id": task_id
                }
            )
        
        # Remove task from category
        category.task_ids.remove(task_id)
        
        if self.category_repo.update(category):
            self.logger.info(f"Removed task {task_id} from category {category_id}")
            return category
        else:
            raise ValidationError("Failed to update category")


class TemplateService:
    """Service for managing task templates."""

    def __init__(self):
        """Initialize the template service."""
        self.logger = get_logger("TemplateService")
        self.template_repo = TemplateRepository()
        self.task_repo = TaskRepository()

    async def create_template(
        self,
        name: str,
        template_id: str,
        category: TemplateTypeEnum,
        description: str,
        input_schema: Dict[str, InputSchemaFieldSchema],
        output_schema: Dict[str, OutputSchemaFieldSchema],
        evaluation_criteria: Dict[str, EvaluationCriteriaSchema],
        test_cases: Optional[List[TestCaseSchema]] = None,
    ) -> TemplateModel:
        """Create a new template.
        
        Args:
            name: Name of the template
            template_id: Unique identifier for the template
            category: Type/category of the template
            description: Description of what the template does
            input_schema: Schema for input validation
            output_schema: Schema for output validation
            evaluation_criteria: Criteria for evaluating task results
            test_cases: Optional list of test cases
            
        Returns:
            Created template
            
        Raises:
            ValidationError: If validation fails
        """
        template = TemplateModel(
            name=name,
            template_id=template_id,
            category=category,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            evaluation_criteria=evaluation_criteria,
            test_cases=test_cases or []
        )
        
        if self.template_repo.create(template):
            self.logger.info(f"Created template: {template.id} ({name})")
            return template
        else:
            raise ValidationError("Failed to create template")

    async def get_template(self, template_id: str) -> TemplateModel:
        """Get a template by ID.
        
        Args:
            template_id: ID of the template
            
        Returns:
            The template
            
        Raises:
            ValidationError: If template not found
        """
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise ValidationError(
                f"Template not found: {template_id}",
                details={"template_id": template_id}
            )
        return template

    async def list_templates(
        self, category: Optional[TemplateTypeEnum] = None
    ) -> List[TemplateModel]:
        """Get all templates, optionally filtered by category.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of templates
        """
        templates = self.template_repo.get_all()
        if category:
            templates = [t for t in templates if t.category == category]
        return templates

    async def update_template(
        self,
        template_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        input_schema: Optional[Dict[str, InputSchemaFieldSchema]] = None,
        output_schema: Optional[Dict[str, OutputSchemaFieldSchema]] = None,
        evaluation_criteria: Optional[Dict[str, EvaluationCriteriaSchema]] = None,
        test_cases: Optional[List[TestCaseSchema]] = None,
    ) -> TemplateModel:
        """Update a template.
        
        Args:
            template_id: ID of the template to update
            name: Optional new name
            description: Optional new description
            input_schema: Optional new input schema
            output_schema: Optional new output schema
            evaluation_criteria: Optional new evaluation criteria
            test_cases: Optional new test cases
            
        Returns:
            Updated template
            
        Raises:
            ValidationError: If template not found or validation fails
        """
        template = await self.get_template(template_id)
        
        # Update fields if provided
        if name is not None:
            template.name = name
        if description is not None:
            template.description = description
        if input_schema is not None:
            template.input_schema = input_schema
        if output_schema is not None:
            template.output_schema = output_schema
        if evaluation_criteria is not None:
            template.evaluation_criteria = evaluation_criteria
        if test_cases is not None:
            template.test_cases = test_cases
            
        if self.template_repo.update(template):
            self.logger.info(f"Updated template: {template.id}")
            return template
        else:
            raise ValidationError("Failed to update template")

    async def delete_template(self, template_id: str) -> None:
        """Delete a template.
        
        Args:
            template_id: ID of the template to delete
            
        Raises:
            ValidationError: If template not found or in use by tasks
        """
        template = await self.get_template(template_id)
        
        # Check if template is used by any tasks
        tasks = self.task_repo.get_all()
        tasks_using_template = [t for t in tasks if t.template_id == template_id]
        if tasks_using_template:
            raise ValidationError(
                f"Cannot delete template in use by tasks: {template_id}",
                details={
                    "template_id": template_id,
                    "task_count": len(tasks_using_template)
                }
            )
        
        # Delete template
        if not self.template_repo.delete(template_id):
            raise ValidationError(
                f"Failed to delete template: {template_id}",
                details={"template_id": template_id}
            )
            
        self.logger.info(f"Deleted template: {template_id}")

    async def validate_template_schema(self, template: TemplateModel) -> None:
        """Validate a template's schema against test cases.
        
        Args:
            template: The template to validate
            
        Raises:
            ValidationError: If template schema validation fails
        """
        # This is where we would validate that:
        # 1. Input schema matches test case inputs
        # 2. Output schema matches test case expected outputs
        # 3. Evaluation criteria are valid for the output schema
        # 4. All required fields have descriptions
        # 5. Schema types are supported
        # etc.
        
        # For now, we'll just do a basic validation
        if not template.input_schema:
            raise ValidationError(
                "Template must have input schema",
                details={"template_id": template.id}
            )
            
        if not template.output_schema:
            raise ValidationError(
                "Template must have output schema",
                details={"template_id": template.id}
            )
            
        if not template.evaluation_criteria:
            raise ValidationError(
                "Template must have evaluation criteria",
                details={"template_id": template.id}
            )
            
        # Validate test cases if present
        if template.test_cases:
            for test_case in template.test_cases:
                if not test_case.input:
                    raise ValidationError(
                        "Test case must have input",
                        details={"template_id": template.id}
                    )
                if not test_case.expected:
                    raise ValidationError(
                        "Test case must have expected output",
                        details={"template_id": template.id}
                    )

    async def get_template_tasks(self, template_id: str) -> List[TaskModel]:
        """Get all tasks using a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            List of tasks using the template
            
        Raises:
            ValidationError: If template not found
        """
        template = await self.get_template(template_id)
        
        tasks = []
        for task in self.task_repo.get_all():
            if task.template_id == template_id:
                tasks.append(task)
                
        return tasks


class TaskService:
    """Service for managing benchmark tasks."""

    def __init__(self):
        """Initialize the task service."""
        self.logger = get_logger("TaskService")
        self.task_repo = TaskRepository()
        self.template_repo = TemplateRepository()
        self.category_repo = CategoryRepository()

    async def create_task(
        self,
        name: str,
        template_id: str,
        description: str = "",
        category_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        expected_output: Optional[Dict[str, Any]] = None,
        evaluation_weights: Optional[Dict[str, float]] = None,
        status: TaskStatusEnum = TaskStatusEnum.DRAFT,
    ) -> TaskModel:
        """Create a new task.
        
        Args:
            name: Name of the task
            template_id: ID of the template to use
            description: Optional description
            category_id: Optional category ID
            input_data: Optional input data for the task
            expected_output: Optional expected output
            evaluation_weights: Optional custom weights for evaluation criteria
            status: Initial task status
            
        Returns:
            Created task
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate template exists
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise ValidationError(
                f"Template not found: {template_id}",
                details={"template_id": template_id}
            )
        
        # Validate category exists if provided
        if category_id:
            category = self.category_repo.get_by_id(category_id)
            if not category:
                raise ValidationError(
                    f"Category not found: {category_id}",
                    details={"category_id": category_id}
                )
        
        # Validate input data against template schema
        if input_data:
            for field_name, field_schema in template.input_schema.items():
                if field_schema.required and field_name not in input_data:
                    raise ValidationError(
                        f"Required input field missing: {field_name}",
                        details={"field": field_name}
                    )
        
        # Create task
        task = TaskModel(
            name=name,
            template_id=template_id,
            description=description,
            category_id=category_id,
            input_data=input_data or {},
            expected_output=expected_output,
            evaluation_weights=evaluation_weights,
            status=status,
        )
        
        if self.task_repo.create(task):
            # If category provided, add task to category
            if category_id:
                category = self.category_repo.get_by_id(category_id)
                if category and task.id not in category.task_ids:
                    category.task_ids.append(task.id)
                    self.category_repo.update(category)
                    
            self.logger.info(f"Created task: {task.id} ({name})")
            return task
        else:
            raise ValidationError("Failed to create task")

    async def get_task(self, task_id: str) -> TaskModel:
        """Get a task by ID.
        
        Args:
            task_id: ID of the task
            
        Returns:
            The task
            
        Raises:
            ValidationError: If task not found
        """
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValidationError(
                f"Task not found: {task_id}",
                details={"task_id": task_id}
            )
        return task

    async def list_tasks(
        self,
        category_id: Optional[str] = None,
        status: Optional[TaskStatusEnum] = None,
    ) -> List[TaskModel]:
        """Get all tasks, optionally filtered by category and/or status.
        
        Args:
            category_id: Optional category ID to filter by
            status: Optional status to filter by
            
        Returns:
            List of tasks
        """
        tasks = self.task_repo.get_all()
        
        # Apply category filter
        if category_id:
            tasks = [t for t in tasks if t.category_id == category_id]
            
        # Apply status filter
        if status:
            tasks = [t for t in tasks if t.status == status]
            
        return tasks

    async def update_task(
        self,
        task_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        expected_output: Optional[Dict[str, Any]] = None,
        evaluation_weights: Optional[Dict[str, float]] = None,
        status: Optional[TaskStatusEnum] = None,
    ) -> TaskModel:
        """Update a task.
        
        Args:
            task_id: ID of the task to update
            name: Optional new name
            description: Optional new description
            category_id: Optional new category ID
            input_data: Optional new input data
            expected_output: Optional new expected output
            evaluation_weights: Optional new evaluation weights
            status: Optional new status
            
        Returns:
            Updated task
            
        Raises:
            ValidationError: If task not found or validation fails
        """
        task = await self.get_task(task_id)
        
        # Handle category change
        if category_id is not None and category_id != task.category_id:
            # Remove from old category if exists
            if task.category_id:
                old_category = self.category_repo.get_by_id(task.category_id)
                if old_category and task_id in old_category.task_ids:
                    old_category.task_ids.remove(task_id)
                    self.category_repo.update(old_category)
            
            # Add to new category if provided
            if category_id:
                new_category = self.category_repo.get_by_id(category_id)
                if not new_category:
                    raise ValidationError(
                        f"Category not found: {category_id}",
                        details={"category_id": category_id}
                    )
                if task_id not in new_category.task_ids:
                    new_category.task_ids.append(task_id)
                    self.category_repo.update(new_category)
        
        # Validate input data against template if provided
        if input_data is not None:
            template = self.template_repo.get_by_id(task.template_id)
            if template:
                for field_name, field_schema in template.input_schema.items():
                    if field_schema.required and field_name not in input_data:
                        raise ValidationError(
                            f"Required input field missing: {field_name}",
                            details={"field": field_name}
                        )
        
        # Update fields if provided
        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        if category_id is not None:
            task.category_id = category_id
        if input_data is not None:
            task.input_data = input_data
        if expected_output is not None:
            task.expected_output = expected_output
        if evaluation_weights is not None:
            task.evaluation_weights = evaluation_weights
        if status is not None:
            task.status = status
            
        if self.task_repo.update(task):
            self.logger.info(f"Updated task: {task.id}")
            return task
        else:
            raise ValidationError("Failed to update task")

    async def delete_task(self, task_id: str) -> None:
        """Delete a task.
        
        Args:
            task_id: ID of the task to delete
            
        Raises:
            ValidationError: If task not found or deletion fails
        """
        task = await self.get_task(task_id)
        
        # Remove from category if assigned
        if task.category_id:
            category = self.category_repo.get_by_id(task.category_id)
            if category and task_id in category.task_ids:
                category.task_ids.remove(task_id)
                self.category_repo.update(category)
        
        # Delete task
        if not self.task_repo.delete(task_id):
            raise ValidationError(
                f"Failed to delete task: {task_id}",
                details={"task_id": task_id}
            )
            
        self.logger.info(f"Deleted task: {task_id}")

    async def validate_task(self, task: TaskModel) -> None:
        """Validate a task's configuration.
        
        Args:
            task: The task to validate
            
        Raises:
            ValidationError: If task validation fails
        """
        # Get template for validation
        template = self.template_repo.get_by_id(task.template_id)
        if not template:
            raise ValidationError(
                f"Template not found: {task.template_id}",
                details={"task_id": task.id}
            )
        
        # Validate input data against template schema
        for field_name, field_schema in template.input_schema.items():
            if field_schema.required and field_name not in task.input_data:
                raise ValidationError(
                    f"Required input field missing: {field_name}",
                    details={
                        "task_id": task.id,
                        "field": field_name
                    }
                )
        
        # Validate evaluation weights if provided
        if task.evaluation_weights:
            for criterion in task.evaluation_weights:
                if criterion not in template.evaluation_criteria:
                    raise ValidationError(
                        f"Invalid evaluation criterion: {criterion}",
                        details={
                            "task_id": task.id,
                            "criterion": criterion
                        }
                    )
        
        # Validate category if assigned
        if task.category_id:
            category = self.category_repo.get_by_id(task.category_id)
            if not category:
                raise ValidationError(
                    f"Category not found: {task.category_id}",
                    details={
                        "task_id": task.id,
                        "category_id": task.category_id
                    }
                )


class ImportExportService:
    """Service for handling data import and export operations."""

    def __init__(self):
        """Initialize the import/export service."""
        self.logger = get_logger("ImportExportService")
        self.category_repo = CategoryRepository()
        self.template_repo = TemplateRepository()
        self.task_repo = TaskRepository()
        self.model_repo = ModelRepository()
        self.benchmark_repo = BenchmarkRunRepository()

    async def export_data(
        self, export_type: ImportExportTypeEnum, entity_ids: List[str]
    ) -> Dict[str, Any]:
        """Export data based on type and entity IDs.
        
        Args:
            export_type: Type of export (category, template, etc.)
            entity_ids: List of entity IDs to export
            
        Returns:
            Dictionary with export data and metadata
            
        Raises:
            ValidationError: If validation fails
        """
        export_data: Dict[str, Any] = {
            "export_type": export_type,
            "export_date": datetime.utcnow().isoformat(),
            "version": "1.0",
            "content": {}
        }
        
        try:
            if export_type == ImportExportTypeEnum.CATEGORY:
                categories = []
                tasks = []
                
                for category_id in entity_ids:
                    category = self.category_repo.get_by_id(category_id)
                    if not category:
                        raise ValidationError(
                            f"Category not found: {category_id}",
                            details={"category_id": category_id}
                        )
                        
                    categories.append(category.model_dump())
                    
                    # Include associated tasks
                    for task_id in category.task_ids:
                        task = self.task_repo.get_by_id(task_id)
                        if task:
                            tasks.append(task.model_dump())
                            
                export_data["content"]["categories"] = categories
                export_data["content"]["tasks"] = tasks
                
            elif export_type == ImportExportTypeEnum.TEMPLATE:
                templates = []
                tasks = []
                
                for template_id in entity_ids:
                    template = self.template_repo.get_by_id(template_id)
                    if not template:
                        raise ValidationError(
                            f"Template not found: {template_id}",
                            details={"template_id": template_id}
                        )
                        
                    templates.append(template.model_dump())
                    
                    # Include tasks using this template
                    for task in self.task_repo.get_all():
                        if task.template_id == template_id:
                            tasks.append(task.model_dump())
                            
                export_data["content"]["templates"] = templates
                export_data["content"]["tasks"] = tasks
                
            elif export_type == ImportExportTypeEnum.TASK:
                tasks = []
                templates_ids = set()
                category_ids = set()
                
                for task_id in entity_ids:
                    task = self.task_repo.get_by_id(task_id)
                    if not task:
                        raise ValidationError(
                            f"Task not found: {task_id}",
                            details={"task_id": task_id}
                        )
                        
                    tasks.append(task.model_dump())
                    templates_ids.add(task.template_id)
                    if task.category_id:
                        category_ids.add(task.category_id)
                
                # Include referenced templates
                templates = []
                for template_id in templates_ids:
                    template = self.template_repo.get_by_id(template_id)
                    if template:
                        templates.append(template.model_dump())
                
                # Include referenced categories
                categories = []
                for category_id in category_ids:
                    category = self.category_repo.get_by_id(category_id)
                    if category:
                        categories.append(category.model_dump())
                
                export_data["content"]["tasks"] = tasks
                export_data["content"]["templates"] = templates
                export_data["content"]["categories"] = categories
                
            elif export_type == ImportExportTypeEnum.MODEL:
                models = []
                
                for model_id in entity_ids:
                    model = self.model_repo.get_by_id(model_id)
                    if not model:
                        raise ValidationError(
                            f"Model not found: {model_id}",
                            details={"model_id": model_id}
                        )
                        
                    models.append(model.model_dump())
                    
                export_data["content"]["models"] = models
                
            elif export_type == ImportExportTypeEnum.BENCHMARK:
                benchmarks = []
                task_ids = set()
                model_ids = set()
                category_ids = set()
                
                for benchmark_id in entity_ids:
                    benchmark = self.benchmark_repo.get_by_id(benchmark_id)
                    if not benchmark:
                        raise ValidationError(
                            f"Benchmark not found: {benchmark_id}",
                            details={"benchmark_id": benchmark_id}
                        )
                        
                    benchmarks.append(benchmark.model_dump())
                    
                    # Collect referenced IDs
                    if benchmark.task_ids:
                        task_ids.update(benchmark.task_ids)
                    if benchmark.model_ids:
                        model_ids.update(benchmark.model_ids)
                    if benchmark.category_ids:
                        category_ids.update(benchmark.category_ids)
                
                # Include referenced entities
                tasks = []
                for task_id in task_ids:
                    task = self.task_repo.get_by_id(task_id)
                    if task:
                        tasks.append(task.model_dump())
                
                models = []
                for model_id in model_ids:
                    model = self.model_repo.get_by_id(model_id)
                    if model:
                        models.append(model.model_dump())
                
                categories = []
                for category_id in category_ids:
                    category = self.category_repo.get_by_id(category_id)
                    if category:
                        categories.append(category.model_dump())
                
                export_data["content"]["benchmarks"] = benchmarks
                export_data["content"]["tasks"] = tasks
                export_data["content"]["models"] = models
                export_data["content"]["categories"] = categories
            
            return export_data
            
        except Exception as e:
            self.logger.error("Export failed", exc_info=True)
            raise ValidationError(
                f"Export failed: {str(e)}",
                details={"export_type": export_type}
            )

    async def preview_import(self, import_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preview data import to identify potential conflicts.
        
        Args:
            import_data: Data to be imported
            
        Returns:
            Dictionary with preview information and potential conflicts
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate import data structure
        if "export_type" not in import_data or "content" not in import_data:
            raise ValidationError(
                "Invalid import data structure",
                details={"required_fields": ["export_type", "content"]}
            )
        
        import_type = ImportExportTypeEnum(import_data["export_type"])
        content = import_data["content"]
        
        preview: Dict[str, Any] = {
            "import_type": import_type,
            "entities_to_import": {},
            "conflicts": {}
        }
        
        try:
            # Check for conflicts based on entity type
            if "categories" in content:
                categories_to_import = []
                category_conflicts = []
                
                for category_data in content["categories"]:
                    existing = self.category_repo.get_by_id(category_data["id"])
                    if existing:
                        category_conflicts.append({
                            "id": category_data["id"],
                            "name": category_data["name"],
                            "type": "category",
                            "reason": "ID already exists"
                        })
                    else:
                        categories_to_import.append(category_data)
                        
                if categories_to_import:
                    preview["entities_to_import"]["categories"] = categories_to_import
                if category_conflicts:
                    preview["conflicts"]["categories"] = category_conflicts
            
            if "templates" in content:
                templates_to_import = []
                template_conflicts = []
                
                for template_data in content["templates"]:
                    existing = self.template_repo.get_by_id(template_data["id"])
                    if existing:
                        template_conflicts.append({
                            "id": template_data["id"],
                            "name": template_data["name"],
                            "type": "template",
                            "reason": "ID already exists"
                        })
                    else:
                        templates_to_import.append(template_data)
                        
                if templates_to_import:
                    preview["entities_to_import"]["templates"] = templates_to_import
                if template_conflicts:
                    preview["conflicts"]["templates"] = template_conflicts
            
            if "tasks" in content:
                tasks_to_import = []
                task_conflicts = []
                
                for task_data in content["tasks"]:
                    existing = self.task_repo.get_by_id(task_data["id"])
                    if existing:
                        task_conflicts.append({
                            "id": task_data["id"],
                            "name": task_data["name"],
                            "type": "task",
                            "reason": "ID already exists"
                        })
                    else:
                        # Check template existence
                        template = self.template_repo.get_by_id(task_data["template_id"])
                        if not template:
                            task_conflicts.append({
                                "id": task_data["id"],
                                "name": task_data["name"],
                                "type": "task",
                                "reason": f"Template not found: {task_data['template_id']}"
                            })
                        else:
                            tasks_to_import.append(task_data)
                        
                if tasks_to_import:
                    preview["entities_to_import"]["tasks"] = tasks_to_import
                if task_conflicts:
                    preview["conflicts"]["tasks"] = task_conflicts
            
            if "models" in content:
                models_to_import = []
                model_conflicts = []
                
                for model_data in content["models"]:
                    existing = self.model_repo.get_by_id(model_data["id"])
                    if existing:
                        model_conflicts.append({
                            "id": model_data["id"],
                            "name": model_data["name"],
                            "type": "model",
                            "reason": "ID already exists"
                        })
                    else:
                        models_to_import.append(model_data)
                        
                if models_to_import:
                    preview["entities_to_import"]["models"] = models_to_import
                if model_conflicts:
                    preview["conflicts"]["models"] = model_conflicts
            
            if "benchmarks" in content:
                benchmarks_to_import = []
                benchmark_conflicts = []
                
                for benchmark_data in content["benchmarks"]:
                    existing = self.benchmark_repo.get_by_id(benchmark_data["id"])
                    if existing:
                        benchmark_conflicts.append({
                            "id": benchmark_data["id"],
                            "name": benchmark_data["name"],
                            "type": "benchmark",
                            "reason": "ID already exists"
                        })
                    else:
                        # Check referenced entities
                        invalid_refs = []
                        
                        if benchmark_data.get("model_ids"):
                            for model_id in benchmark_data["model_ids"]:
                                if not self.model_repo.get_by_id(model_id):
                                    invalid_refs.append(f"Model not found: {model_id}")
                                    
                        if benchmark_data.get("task_ids"):
                            for task_id in benchmark_data["task_ids"]:
                                if not self.task_repo.get_by_id(task_id):
                                    invalid_refs.append(f"Task not found: {task_id}")
                                    
                        if benchmark_data.get("category_ids"):
                            for category_id in benchmark_data["category_ids"]:
                                if not self.category_repo.get_by_id(category_id):
                                    invalid_refs.append(f"Category not found: {category_id}")
                        
                        if invalid_refs:
                            benchmark_conflicts.append({
                                "id": benchmark_data["id"],
                                "name": benchmark_data["name"],
                                "type": "benchmark",
                                "reason": "Invalid references: " + "; ".join(invalid_refs)
                            })
                        else:
                            benchmarks_to_import.append(benchmark_data)
                        
                if benchmarks_to_import:
                    preview["entities_to_import"]["benchmarks"] = benchmarks_to_import
                if benchmark_conflicts:
                    preview["conflicts"]["benchmarks"] = benchmark_conflicts
            
            return preview
            
        except Exception as e:
            self.logger.error("Import preview failed", exc_info=True)
            raise ValidationError(
                f"Import preview failed: {str(e)}",
                details={"import_type": import_type}
            )

    async def import_data(self, import_data: Dict[str, Any]) -> None:
        """Import data into the system.
        
        Args:
            import_data: Data to be imported
            
        Raises:
            ValidationError: If validation fails
        """
        # First preview the import to check for conflicts
        preview = await self.preview_import(import_data)
        
        # If there are conflicts, reject the import
        if preview.get("conflicts"):
            raise ValidationError(
                "Cannot import due to conflicts",
                details=preview["conflicts"]
            )
        
        try:
            # Import entities in the correct order to maintain referential integrity
            content = import_data["content"]
            
            # 1. Import categories first
            if "categories" in content:
                for category_data in content["categories"]:
                    category = CategoryModel(**category_data)
                    self.category_repo.create(category)
            
            # 2. Import templates
            if "templates" in content:
                for template_data in content["templates"]:
                    template = TemplateModel(**template_data)
                    self.template_repo.create(template)
            
            # 3. Import models
            if "models" in content:
                for model_data in content["models"]:
                    model = ModelModel(**model_data)
                    self.model_repo.create(model)
            
            # 4. Import tasks (depends on templates and categories)
            if "tasks" in content:
                for task_data in content["tasks"]:
                    task = TaskModel(**task_data)
                    self.task_repo.create(task)
                    
                    # Update category if assigned
                    if task.category_id:
                        category = self.category_repo.get_by_id(task.category_id)
                        if category and task.id not in category.task_ids:
                            category.task_ids.append(task.id)
                            self.category_repo.update(category)
            
            # 5. Import benchmarks (depends on all other entities)
            if "benchmarks" in content:
                for benchmark_data in content["benchmarks"]:
                    benchmark = BenchmarkRunModel(**benchmark_data)
                    self.benchmark_repo.create(benchmark)
            
            self.logger.info("Import completed successfully")
            
        except Exception as e:
            self.logger.error("Import failed", exc_info=True)
            raise ValidationError(
                f"Import failed: {str(e)}",
                details={"error": str(e)}
            )