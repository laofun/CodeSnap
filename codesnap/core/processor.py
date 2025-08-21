"""File processing and content extraction."""

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Tuple

try:
    from tqdm import tqdm

    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from ..config.settings import ScanConfig
from ..utils.logger import get_logger


class FileContent:
    """Represents processed file content."""

    def __init__(
        self,
        file_path: Path,
        relative_path: Path,
        content: str,
        extension: str,
        size_bytes: int,
    ) -> None:
        self.file_path = file_path
        self.relative_path = relative_path
        self.content = content
        self.extension = extension
        self.size_bytes = size_bytes

    @property
    def size_mb(self) -> float:
        """File size in megabytes."""
        return self.size_bytes / (1024 * 1024)


class FileProcessor:
    """Processes files and extracts content."""

    def __init__(self, config: ScanConfig) -> None:
        self.config = config
        self.logger = get_logger()

    def process_files(
        self, files: List[Tuple[Path, Path]], max_workers: Optional[int] = None
    ) -> List[FileContent]:
        """
        Process multiple files in parallel.

        Args:
            files: List of (file_path, root_path) tuples
            max_workers: Maximum number of worker processes

        Returns:
            List of FileContent objects
        """
        if not files:
            self.logger.warning("No files to process")
            return []

        self.logger.info(f"Processing {len(files)} files...")

        # Prepare arguments for parallel processing
        process_args = [
            (file_path, root_path, self.config.max_file_size_mb)
            for file_path, root_path in files
        ]

        results = []

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_args = {
                executor.submit(_process_single_file, args): args
                for args in process_args
            }

            # Use tqdm for progress tracking if available
            if TQDM_AVAILABLE:
                futures = tqdm(
                    as_completed(future_to_args),
                    total=len(future_to_args),
                    desc="Processing files",
                )
            else:
                futures = as_completed(future_to_args)

            for future in futures:
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    args = future_to_args[future]
                    file_path = args[0]
                    self.logger.error(f"Failed to process {file_path}: {e}")

        self.logger.info(f"Successfully processed {len(results)} files")
        return results

    def estimate_token_count(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4


def _process_single_file(args: Tuple[Path, Path, float]) -> Optional[FileContent]:
    """
    Process a single file (for use in multiprocessing).

    Args:
        args: Tuple of (file_path, root_path, max_size_mb)

    Returns:
        FileContent object or None if processing failed
    """
    file_path, root_path, max_size_mb = args

    try:
        # Check file size
        size_bytes = file_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)

        if size_mb > max_size_mb:
            return None

        # Read file content
        content = file_path.read_text(encoding="utf-8", errors="replace")

        # Calculate relative path
        relative_path = file_path.relative_to(root_path)

        # Get extension
        extension = file_path.suffix.lstrip(".").lower()

        return FileContent(
            file_path=file_path,
            relative_path=relative_path,
            content=content,
            extension=extension,
            size_bytes=size_bytes,
        )

    except Exception:
        # Log error but don't raise (we're in a subprocess)
        return None
