"""Git repository handling functionality."""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from ..config.settings import GitConfig
from ..utils.exceptions import GitOperationError
from ..utils.logger import get_logger


class GitHandler:
    """Handles Git repository operations."""

    def __init__(self, config: GitConfig) -> None:
        self.config = config
        self.logger = get_logger()

    def clone_repository(
        self, repo_url: str, target_dir: Optional[Path] = None
    ) -> Path:
        """
        Clone a Git repository with shallow clone.

        Args:
            repo_url: Repository URL to clone
            target_dir: Optional target directory (default: temp directory)

        Returns:
            Path to cloned repository

        Raises:
            GitOperationError: If cloning fails
        """
        if target_dir is None:
            # Create temp directory next to the script
            script_dir = Path(__file__).resolve().parent.parent.parent
            target_dir = script_dir / self.config.temp_dir_name

        # Clean up existing directory
        if target_dir.exists():
            self.logger.info(f"Removing existing directory: {target_dir}")
            shutil.rmtree(target_dir)

        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.logger.info(f"Cloning repository: {repo_url}")
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    str(self.config.clone_depth),
                    repo_url,
                    str(target_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.logger.info(f"Successfully cloned to: {target_dir}")
            return target_dir

        except subprocess.CalledProcessError as e:
            # Clean up failed clone directory
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)

            error_msg = e.stderr or str(e)
            raise GitOperationError(
                f"Failed to clone repository: {repo_url}", details=error_msg
            )
        except Exception as e:
            # Clean up on unexpected error
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)

            raise GitOperationError(
                f"Unexpected error during clone: {repo_url}", details=str(e)
            )

    def extract_repo_name(self, repo_url: str) -> str:
        """
        Extract repository name from URL.

        Args:
            repo_url: Repository URL

        Returns:
            Repository name
        """
        # Handle common Git URL formats
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]

        # Extract name from URL
        return Path(repo_url.rstrip("/")).name

    def cleanup_temp_directory(self, temp_dir: Path) -> None:
        """
        Clean up temporary clone directory.

        Args:
            temp_dir: Directory to clean up
        """
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                self.logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to clean up {temp_dir}: {e}")

    def is_git_repository(self, path: Path) -> bool:
        """
        Check if path is a Git repository.

        Args:
            path: Directory path to check

        Returns:
            True if path is a Git repository
        """
        git_dir = path / ".git"
        return git_dir.exists() and (git_dir.is_dir() or git_dir.is_file())

    def get_repository_info(self, repo_path: Path) -> dict:
        """
        Get repository information.

        Args:
            repo_path: Path to repository

        Returns:
            Dictionary with repository information
        """
        if not self.is_git_repository(repo_path):
            return {}

        try:
            # Get remote URL
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            remote_url = result.stdout.strip()

            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            current_branch = result.stdout.strip()

            return {
                "remote_url": remote_url,
                "current_branch": current_branch,
                "repo_name": self.extract_repo_name(remote_url),
            }

        except subprocess.CalledProcessError:
            return {}
