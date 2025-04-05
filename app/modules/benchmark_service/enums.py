"""
Enum definitions for benchmark service.
"""

from enum import Enum, auto


class ScoreTypeEnum(Enum):
    """Types of scores in benchmark results."""
    TIME = "time"
    QUALITY = "quality"
    COMPLEXITY = "complexity"
    COST = "cost"
    MEMORY = "memory"
    ULTIMATE = "ultimate"