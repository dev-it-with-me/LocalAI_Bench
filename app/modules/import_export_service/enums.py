"""
Enum definitions for import/export service.
"""

from enum import Enum


class ConflictResolutionTypeEnum(Enum):
    """Types of conflict resolution strategies."""
    SKIP = "skip"
    OVERWRITE = "overwrite"
    RENAME = "rename"
    ERROR = "error"


class ImportStatusEnum(Enum):
    """Status of an import operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"