"""Utility modules for CodeSnap."""

from .exceptions import (
    CodeSnapError,
    ConfigurationError,
    FileProcessingError,
    GitOperationError,
)
from .logger import setup_logger

__all__ = [
    "CodeSnapError",
    "ConfigurationError",
    "FileProcessingError",
    "GitOperationError",
    "setup_logger",
]
