"""Professional logging setup for CodeSnap."""

import logging
import sys
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.logging import RichHandler

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def setup_logger(
    name: str = "codesnap",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    enable_rich: bool = True,
    debug: bool = False,
) -> logging.Logger:
    """
    Set up a professional logger with console and optional file output.

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional file path for logging
        enable_rich: Use rich formatting if available
        debug: Enable debug mode

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG if debug else level)

    # Format for console and file
    console_format = "%(message)s"
    file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Console handler with rich formatting if available
    if RICH_AVAILABLE and enable_rich:
        console_handler = RichHandler(
            console=Console(stderr=True), show_time=False, show_path=False, markup=True
        )
        console_handler.setFormatter(logging.Formatter(console_format))
    else:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )

    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(file_format))
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "codesnap") -> logging.Logger:
    """Get an existing logger instance."""
    return logging.getLogger(name)
