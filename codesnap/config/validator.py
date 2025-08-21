"""Configuration validation for CodeSnap."""

from pathlib import Path
from typing import List

from ..utils.exceptions import ValidationError
from .settings import CodeSnapConfig


class ConfigValidator:
    """Validates CodeSnap configuration."""

    @staticmethod
    def validate_extensions(extensions: List[str]) -> None:
        """Validate file extensions."""
        if not extensions:
            raise ValidationError("At least one file extension must be specified")

        for ext in extensions:
            if not ext.startswith("."):
                raise ValidationError(f"Extension must start with '.': {ext}")

    @staticmethod
    def validate_file_size(max_size_mb: float) -> None:
        """Validate maximum file size."""
        if max_size_mb <= 0:
            raise ValidationError("Maximum file size must be positive")
        if max_size_mb > 100:
            raise ValidationError("Maximum file size too large (>100MB)")

    @staticmethod
    def validate_tokens(max_tokens: int) -> None:
        """Validate maximum tokens per part."""
        if max_tokens <= 1000:
            raise ValidationError("Maximum tokens too small (<1000)")
        if max_tokens > 100000:
            raise ValidationError("Maximum tokens too large (>100,000)")

    @staticmethod
    def validate_path(path: Path, must_exist: bool = True) -> None:
        """Validate file/directory path."""
        if must_exist and not path.exists():
            raise ValidationError(f"Path does not exist: {path}")

        if must_exist and path.is_file() and not path.is_dir():
            raise ValidationError(f"Expected directory, got file: {path}")

    @classmethod
    def validate_config(cls, config: CodeSnapConfig) -> None:
        """Validate entire configuration."""
        cls.validate_extensions(config.scan.extensions)
        cls.validate_file_size(config.scan.max_file_size_mb)
        cls.validate_tokens(config.output.max_tokens_per_part)

        if (
            config.log_file
            and config.log_file.parent
            and not config.log_file.parent.exists()
        ):
            raise ValidationError(
                f"Log file directory does not exist: {config.log_file.parent}"
            )
