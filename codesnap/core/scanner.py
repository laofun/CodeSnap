"""File scanning and collection functionality."""

import os
from fnmatch import fnmatch
from pathlib import Path
from typing import Generator, List, Tuple

from ..config.settings import ScanConfig
from ..utils.exceptions import FileProcessingError
from ..utils.logger import get_logger


class CodeScanner:
    """Scans directories for code files based on configuration."""

    def __init__(self, config: ScanConfig) -> None:
        self.config = config
        self.logger = get_logger()

    def scan_directory(self, root_path: Path) -> List[Tuple[Path, Path]]:
        """
        Scan directory for files matching the configuration.

        Args:
            root_path: Root directory to scan

        Returns:
            List of tuples (file_path, root_path) for each matching file

        Raises:
            FileProcessingError: If root path is invalid
        """
        if not root_path.exists() or not root_path.is_dir():
            raise FileProcessingError(
                f"Invalid directory path: {root_path}", file_path=str(root_path)
            )

        files = list(self._collect_files(root_path))
        self.logger.info(f"Found {len(files)} files to process in {root_path}")
        return files

    def _collect_files(self, root: Path) -> Generator[Tuple[Path, Path], None, None]:
        """
        Internal generator to collect files matching criteria.

        Args:
            root: Root directory path

        Yields:
            Tuples of (file_path, root_path)
        """
        for current_dir, dirnames, filenames in os.walk(root):
            current_path = Path(current_dir)

            # Skip excluded directories
            if self._should_exclude_directory(current_path, root):
                dirnames.clear()  # Don't descend into this directory
                continue

            # Filter out excluded directories from further traversal
            dirnames[:] = [d for d in dirnames if d not in self.config.exclude_dirs]

            # Stop recursion if not scanning subfolders and we're not at root
            if not self.config.scan_subfolders and current_path != root:
                dirnames.clear()
                continue

            # Process files in current directory
            for filename in filenames:
                file_path = current_path / filename

                if self._should_include_file(file_path):
                    yield (file_path, root)

    def _should_exclude_directory(self, current_path: Path, root: Path) -> bool:
        """
        Check if directory should be excluded.

        Args:
            current_path: Current directory being checked
            root: Root scan directory

        Returns:
            True if directory should be excluded
        """
        if current_path == root:
            return False

        # Check if any part of the relative path is in exclude_dirs
        try:
            rel_parts = current_path.relative_to(root).parts
            return any(part in self.config.exclude_dirs for part in rel_parts)
        except ValueError:
            # current_path is not relative to root
            return True

    def _should_include_file(self, file_path: Path) -> bool:
        """
        Check if file should be included based on configuration.

        Args:
            file_path: File path to check

        Returns:
            True if file should be included
        """
        # Check file extension
        if file_path.suffix.lower() not in self.config.extensions:
            return False

        # Check exclude patterns
        filename = file_path.name
        if any(fnmatch(filename, pattern) for pattern in self.config.exclude_patterns):
            return False

        # Check file size
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > self.config.max_file_size_mb:
                self.logger.debug(
                    f"Skipping large file: {file_path} "
                    f"({size_mb:.2f} MB > {self.config.max_file_size_mb} MB)"
                )
                return False
        except OSError as e:
            self.logger.warning(f"Could not check size for {file_path}: {e}")
            return False

        return True

    def generate_directory_tree(self, root: Path, repo_name: str = None) -> str:
        """
        Generate a tree-like representation of directory structure.

        Args:
            root: Root directory
            repo_name: Optional repository name for display

        Returns:
            Tree representation as string
        """

        def _walk_dir(path: Path, prefix: str = "") -> List[str]:
            lines: List[str] = []

            try:
                entries = sorted(path.iterdir(), key=lambda e: e.name.lower())
                filtered_entries = []

                for entry in entries:
                    # Skip excluded directories
                    if entry.is_dir() and entry.name in self.config.exclude_dirs:
                        continue

                    # Skip excluded files
                    if entry.is_file():
                        if any(
                            fnmatch(entry.name, pattern)
                            for pattern in self.config.exclude_patterns
                        ):
                            continue
                        filtered_entries.append(entry)
                        continue

                    # Include non-excluded directories
                    filtered_entries.append(entry)

                entries = filtered_entries

            except PermissionError:
                return [prefix + "└── [Permission Denied]"]

            for idx, entry in enumerate(entries):
                is_last = idx == len(entries) - 1
                connector = "└── " if is_last else "├── "
                line = prefix + connector + entry.name

                if entry.is_symlink():
                    try:
                        target = os.readlink(str(entry))
                        line += f" -> {target}"
                    except Exception:
                        line += " -> [Broken Symlink]"

                lines.append(line)

                if entry.is_dir():
                    sub_prefix = "    " if is_last else "│   "
                    lines.extend(_walk_dir(entry, prefix + sub_prefix))

            return lines

        root_name = repo_name or root.name
        header = [root_name]
        body = _walk_dir(root)
        return "\n".join(header + body)
