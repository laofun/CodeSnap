"""
CodeSnap - Professional code analysis and documentation generator.

A Python tool that generates Markdown summaries of source code and project
structure from folders or Git repositories.
"""

__version__ = "2.0.0"
__author__ = "CodeSnap Team"
__license__ = "MIT"

from .config.settings import CodeSnapConfig
from .core.formatter import MarkdownFormatter
from .core.processor import FileProcessor
from .core.scanner import CodeScanner

__all__ = [
    "CodeScanner",
    "FileProcessor",
    "MarkdownFormatter",
    "CodeSnapConfig",
]
