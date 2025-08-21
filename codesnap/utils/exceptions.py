"""Custom exception classes for CodeSnap."""

from typing import Optional


class CodeSnapError(Exception):
    """Base exception class for all CodeSnap errors."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class ConfigurationError(CodeSnapError):
    """Raised when there's an error in configuration."""

    pass


class FileProcessingError(CodeSnapError):
    """Raised when there's an error processing files."""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        self.file_path = file_path
        super().__init__(message, details)

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.file_path:
            return f"{base_msg} (file: {self.file_path})"
        return base_msg


class GitOperationError(CodeSnapError):
    """Raised when there's an error with Git operations."""

    pass


class ValidationError(CodeSnapError):
    """Raised when validation fails."""

    pass
