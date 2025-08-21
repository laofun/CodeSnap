"""Configuration classes for CodeSnap."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.exceptions import ConfigurationError


@dataclass
class ScanConfig:
    """Configuration for file scanning."""

    extensions: List[str] = field(
        default_factory=lambda: [
            ".py",
            ".js",
            ".java",
            ".cpp",
            ".c",
            ".html",
            ".css",
            ".ts",
            ".go",
            ".dart",
            ".rs",
            ".rb",
            ".php",
            ".swift",
        ]
    )
    exclude_dirs: List[str] = field(
        default_factory=lambda: [
            "node_modules",
            ".git",
            "__pycache__",
            ".vscode",
            ".github",
            "mocks",
            ".gitkeep",
            "build",
            "dist",
            "tmp",
            "bin",
        ]
    )
    exclude_patterns: List[str] = field(
        default_factory=lambda: ["*.g.dart", "*.freezed.dart", "*.md", ".DS_Store"]
    )
    max_file_size_mb: float = 2.0
    scan_subfolders: bool = True


@dataclass
class OutputConfig:
    """Configuration for output generation."""

    base_name: str = "codesnap"
    max_tokens_per_part: int = 12000
    include_structure: bool = True
    format_style: str = "markdown"  # Future: support other formats


@dataclass
class GitConfig:
    """Configuration for Git operations."""

    clone_depth: int = 1
    temp_dir_name: str = "codesnap_temp"


@dataclass
class CodeSnapConfig:
    """Main configuration class for CodeSnap."""

    scan: ScanConfig = field(default_factory=ScanConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    git: GitConfig = field(default_factory=GitConfig)
    debug: bool = False
    log_file: Optional[Path] = None

    @classmethod
    def from_file(cls, config_path: Path) -> "CodeSnapConfig":
        """Load configuration from JSON file."""
        try:
            with config_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigurationError(
                f"Failed to load config from {config_path}", details=str(e)
            )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodeSnapConfig":
        """Create configuration from dictionary."""
        config = cls()

        # Update scan config
        if "extensions" in data:
            config.scan.extensions = data["extensions"]
        if "exclude_dirs" in data:
            config.scan.exclude_dirs.extend(data["exclude_dirs"])
        if "exclude_patterns" in data:
            config.scan.exclude_patterns.extend(data["exclude_patterns"])
        if "max_size" in data:
            config.scan.max_file_size_mb = float(data["max_size"])
        if "no_subfolders" in data:
            config.scan.scan_subfolders = not bool(data["no_subfolders"])

        # Update output config
        if "output" in data:
            config.output.base_name = data["output"]
        if "max_tokens" in data:
            config.output.max_tokens_per_part = int(data["max_tokens"])

        # Update debug
        if "debug" in data:
            config.debug = bool(data["debug"])

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "extensions": self.scan.extensions,
            "exclude_dirs": self.scan.exclude_dirs,
            "exclude_patterns": self.scan.exclude_patterns,
            "max_size": self.scan.max_file_size_mb,
            "no_subfolders": not self.scan.scan_subfolders,
            "output": self.output.base_name,
            "max_tokens": self.output.max_tokens_per_part,
            "debug": self.debug,
        }

    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to JSON file."""
        try:
            with config_path.open("w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
        except IOError as e:
            raise ConfigurationError(
                f"Failed to save config to {config_path}", details=str(e)
            )
