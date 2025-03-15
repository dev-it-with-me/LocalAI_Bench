"""
Utility functions for LocalAI Bench application.

This module provides utility functions for working with JSON files,
logging, and other common tasks.
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Generic, Type, TypeVar

import uuid

from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(os.path.join(settings.LOG_DIR, "app.log")),
        logging.StreamHandler(),
    ],
)

# Type variable for generic model handling
T = TypeVar("T")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name and configured with correlation ID tracking."""
    logger = logging.getLogger(name)
    return logger


class JsonFileHandler(Generic[T]):
    """Handler for reading and writing JSON files with versioning support."""
    
    def __init__(self, directory: Path, model_cls: Type[T] | None = None):
        """Initialize the JSON file handler.
        
        Args:
            directory: The directory where JSON files will be stored
            model_cls: Optional Pydantic model class for parsing JSON data
        """
        self.directory: Path = directory
        self.model_cls = model_cls
        self.logger = get_logger(f"JsonFileHandler:{Path(directory).name}")
        
        # Ensure directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Create version directory if it doesn't exist
        self.versions_dir = os.path.join(directory, "_versions")
        os.makedirs(self.versions_dir, exist_ok=True)
    
    def get_file_path(self, file_id: str) -> str:
        """Get the full path to a JSON file with the given ID."""
        return os.path.join(self.directory, f"{file_id}.json")
    
    def exists(self, file_id: str) -> bool:
        """Check if a file with the given ID exists."""
        return os.path.exists(self.get_file_path(file_id))
    
    def list_files(self) -> list[str]:
        """List all JSON files in the directory, returning just the base IDs (no extension)."""
        files = []
        for file in os.listdir(self.directory):
            if file.endswith(".json") and not file.startswith("_"):
                files.append(file[:-5])  # Remove .json extension
        return files
    
    def create_version(self, file_id: str) -> str:
        """Create a versioned backup of the file."""
        source_path = self.get_file_path(file_id)
        if not os.path.exists(source_path):
            return ""
        
        # Create version folder for this file if it doesn't exist
        file_versions_dir = os.path.join(self.versions_dir, file_id)
        os.makedirs(file_versions_dir, exist_ok=True)
        
        # Create version with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        version_id = f"{timestamp}_{uuid.uuid4().hex[:8]}"
        version_path = os.path.join(file_versions_dir, f"{version_id}.json")
        
        # Copy the file to the version path
        shutil.copy2(source_path, version_path)
        
        return version_id
    
    def read(self, file_id: str) -> T | dict | None:
        """Read a JSON file and return its contents as a Pydantic model if model_cls is provided."""
        file_path = self.get_file_path(file_id)
        if not os.path.exists(file_path):
            self.logger.warning(f"File not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if self.model_cls:
                return self.model_cls.model_validate(data)
            else:
                return data
                
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def write(self, file_id: str, data: T | dict, create_version: bool = True) -> bool:
        """Write data to a JSON file.
        
        Args:
            file_id: The ID of the file to write
            data: The data to write, can be a Pydantic model or dict
            create_version: Whether to create a versioned backup before writing
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = self.get_file_path(file_id)
        
        # Create version if requested and file exists
        if create_version and os.path.exists(file_path):
            self.create_version(file_id)
        
        try:
            # Convert Pydantic model to dict if necessary
            if hasattr(data, "model_dump"):
                data_dict = data.model_dump(mode="json")
            else:
                data_dict = data
            
            # Write to a temporary file first
            temp_file = f"{file_path}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=2, default=str)
            
            # Rename to target file (atomic operation)
            os.replace(temp_file, file_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing file {file_path}: {e}")
            # Clean up temp file if it exists
            if os.path.exists(f"{file_path}.tmp"):
                os.remove(f"{file_path}.tmp")
            return False
    
    def delete(self, file_id: str, create_version: bool = True) -> bool:
        """Delete a JSON file.
        
        Args:
            file_id: The ID of the file to delete
            create_version: Whether to create a versioned backup before deleting
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = self.get_file_path(file_id)
        
        if not os.path.exists(file_path):
            self.logger.warning(f"File not found for deletion: {file_path}")
            return False
        
        try:
            # Create version if requested
            if create_version:
                self.create_version(file_id)
            
            # Delete the file
            os.remove(file_path)
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")
            return False


def batch_process_json_files(
    directory: str,
    processor: Callable[[dict], dict],
    file_filter: Callable[[str], bool] | None = None,
) -> tuple[int, int]:
    """Process multiple JSON files in a directory with a processor function.
    
    Args:
        directory: Directory containing JSON files to process
        processor: Function that takes a parsed JSON dict and returns a modified dict
        file_filter: Optional function to filter files by name
        
    Returns:
        tuple: (files_processed, files_failed)
    """
    if not os.path.isdir(directory):
        return 0, 0
        
    files_processed = 0
    files_failed = 0
    logger = get_logger("batch_process")
    
    for filename in os.listdir(directory):
        if not filename.endswith(".json"):
            continue
            
        if file_filter and not file_filter(filename):
            continue
            
        file_path = os.path.join(directory, filename)
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Process the data
            result = processor(data)
            
            # Write the result back
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
                
            files_processed += 1
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            files_failed += 1
            
    return files_processed, files_failed