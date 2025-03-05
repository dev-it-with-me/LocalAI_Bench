"""
Custom exceptions for LocalAI Bench application.

This module defines custom exceptions used throughout the application.
"""


class LocalAIBenchError(Exception):
    """Base class for all LocalAI Bench application exceptions."""
    
    def __init__(self, message: str = "An error occurred in the LocalAI Bench application"):
        self.message = message
        super().__init__(self.message)


class ConfigurationError(LocalAIBenchError):
    """Exception raised for errors in application configuration."""
    
    def __init__(self, message: str = "Configuration error"):
        super().__init__(f"Configuration error: {message}")


class DataStorageError(LocalAIBenchError):
    """Exception raised for errors in data storage operations."""
    
    def __init__(self, message: str = "Data storage error", entity_type: str | None = None, 
                 entity_id: str | None = None):
        msg = f"Data storage error: {message}"
        if entity_type:
            msg += f" [Entity Type: {entity_type}"
            if entity_id:
                msg += f", ID: {entity_id}"
            msg += "]"
        super().__init__(msg)
        self.entity_type = entity_type
        self.entity_id = entity_id


class ModelAdapterError(LocalAIBenchError):
    """Exception raised for errors in model adapters."""
    
    def __init__(self, message: str = "Model adapter error", model_type: str | None = None,
                 model_id: str | None = None):
        msg = f"Model adapter error: {message}"
        if model_type:
            msg += f" [Model Type: {model_type}"
            if model_id:
                msg += f", ID: {model_id}"
            msg += "]"
        super().__init__(msg)
        self.model_type = model_type
        self.model_id = model_id


class ValidationError(LocalAIBenchError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str = "Validation error", field: str | None = None):
        msg = f"Validation error: {message}"
        if field:
            msg += f" [Field: {field}]"
        super().__init__(msg)
        self.field = field


class BenchmarkExecutionError(LocalAIBenchError):
    """Exception raised for errors during benchmark execution."""
    
    def __init__(self, message: str = "Benchmark execution error", 
                 benchmark_id: str | None = None, task_id: str | None = None,
                 model_id: str | None = None):
        msg = f"Benchmark execution error: {message}"
        context_parts = []
        if benchmark_id:
            context_parts.append(f"Benchmark: {benchmark_id}")
        if task_id:
            context_parts.append(f"Task: {task_id}")
        if model_id:
            context_parts.append(f"Model: {model_id}")
        
        if context_parts:
            msg += f" [{', '.join(context_parts)}]"
            
        super().__init__(msg)
        self.benchmark_id = benchmark_id
        self.task_id = task_id
        self.model_id = model_id


class ResourceError(LocalAIBenchError):
    """Exception raised for resource-related errors."""
    
    def __init__(self, message: str = "Resource error", resource_type: str | None = None):
        msg = f"Resource error: {message}"
        if resource_type:
            msg += f" [Resource Type: {resource_type}]"
        super().__init__(msg)
        self.resource_type = resource_type


class AuthenticationError(LocalAIBenchError):
    """Exception raised for authentication errors."""
    
    def __init__(self, message: str = "Authentication error", provider: str | None = None):
        msg = f"Authentication error: {message}"
        if provider:
            msg += f" [Provider: {provider}]"
        super().__init__(msg)
        self.provider = provider


class ImportExportError(LocalAIBenchError):
    """Exception raised for import/export errors."""
    
    def __init__(self, message: str = "Import/export error", operation: str | None = None):
        msg = f"Import/export error: {message}"
        if operation:
            msg += f" [Operation: {operation}]"
        super().__init__(msg)
        self.operation = operation