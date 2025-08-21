"""Command-line interface for CodeSnap."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from .config.settings import CodeSnapConfig
from .config.validator import ConfigValidator
from .core.formatter import MarkdownFormatter
from .core.git_handler import GitHandler
from .core.processor import FileProcessor
from .core.scanner import CodeScanner
from .utils.exceptions import CodeSnapError, ValidationError
from .utils.logger import setup_logger


class CodeSnapCLI:
    """Command-line interface for CodeSnap."""

    def __init__(self) -> None:
        self.config: Optional[CodeSnapConfig] = None
        self.logger = None

    def run(self, args: Optional[list] = None) -> int:
        """
        Run the CLI application.

        Args:
            args: Optional command line arguments (uses sys.argv if None)

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            # Parse arguments
            parsed_args = self._parse_arguments(args)

            # Load and validate configuration
            self.config = self._load_configuration(parsed_args)
            ConfigValidator.validate_config(self.config)

            # Setup logging
            self.logger = setup_logger(
                level=logging.DEBUG if self.config.debug else logging.INFO,
                log_file=self.config.log_file,
                debug=self.config.debug,
            )

            # Handle test mode
            if parsed_args.test:
                return self._run_test_mode(parsed_args)

            # Determine source path
            source_path, repo_info = self._resolve_source_path(parsed_args)

            # Execute main workflow
            return self._execute_workflow(source_path, repo_info)

        except KeyboardInterrupt:
            print("\nOperation cancelled by user", file=sys.stderr)
            return 130
        except CodeSnapError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            if self.config and self.config.debug:
                import traceback

                traceback.print_exc()
            return 1

    def _parse_arguments(self, args: Optional[list]) -> argparse.Namespace:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(
            description="Generate Markdown summaries of code projects",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s /path/to/project
  %(prog)s --repo https://github.com/laofun/CodeSnap.git
  %(prog)s --config config.json /path/to/project
  %(prog)s --test /path/to/project
            """,
        )

        # Positional arguments
        parser.add_argument(
            "folder",
            nargs="?",
            help="Path to local folder to scan (ignored if --repo is used)",
        )

        # Output options
        parser.add_argument(
            "-o",
            "--output",
            default="codesnap",
            help="Base name for output files (default: codesnap)",
        )

        # File filtering options
        parser.add_argument(
            "-e",
            "--extensions",
            nargs="+",
            help="File extensions to include (e.g., .py .js .ts)",
        )

        parser.add_argument(
            "-x", "--exclude-dirs", nargs="+", help="Additional directories to exclude"
        )

        parser.add_argument(
            "-p",
            "--exclude-patterns",
            nargs="+",
            help="File patterns to exclude (fnmatch syntax)",
        )

        parser.add_argument(
            "-f", "--exclude-files", nargs="+", help="Specific filenames to exclude"
        )

        # Size and token limits
        parser.add_argument(
            "-m",
            "--max-size",
            type=float,
            help="Maximum file size in MB (default: from config)",
        )

        parser.add_argument(
            "-t",
            "--max-tokens",
            type=int,
            help="Maximum tokens per output part (default: from config)",
        )

        # Configuration
        parser.add_argument(
            "-c", "--config", type=Path, help="Path to JSON configuration file"
        )

        # Git options
        parser.add_argument("-r", "--repo", help="Git repository URL to clone and scan")

        # Scanning options
        parser.add_argument(
            "-n",
            "--no-subfolders",
            action="store_true",
            help="Only scan top-level directory (no recursion)",
        )

        # Utility options
        parser.add_argument(
            "--test",
            action="store_true",
            help="Show project structure and exit (no file processing)",
        )

        parser.add_argument("--debug", action="store_true", help="Enable debug logging")

        parser.add_argument("--version", action="version", version="%(prog)s 2.0.0")

        return parser.parse_args(args)

    def _load_configuration(self, args: argparse.Namespace) -> CodeSnapConfig:
        """Load configuration from file and command line arguments."""
        # Start with default config
        if args.config and args.config.exists():
            config = CodeSnapConfig.from_file(args.config)
        else:
            config = CodeSnapConfig()

        # Override with command line arguments
        self._apply_cli_overrides(config, args)

        return config

    def _apply_cli_overrides(
        self, config: CodeSnapConfig, args: argparse.Namespace
    ) -> None:
        """Apply command line argument overrides to configuration."""
        # Scan configuration
        if args.extensions:
            # Normalize extensions
            extensions = [
                ext if ext.startswith(".") else f".{ext}" for ext in args.extensions
            ]
            config.scan.extensions = extensions

        if args.exclude_dirs:
            config.scan.exclude_dirs.extend(args.exclude_dirs)

        if args.exclude_patterns:
            config.scan.exclude_patterns.extend(args.exclude_patterns)

        if args.exclude_files:
            config.scan.exclude_patterns.extend(args.exclude_files)

        if args.max_size is not None:
            config.scan.max_file_size_mb = args.max_size

        if args.no_subfolders:
            config.scan.scan_subfolders = False

        # Output configuration
        if args.output:
            config.output.base_name = args.output

        if args.max_tokens is not None:
            config.output.max_tokens_per_part = args.max_tokens

        # Debug
        if args.debug:
            config.debug = True

    def _resolve_source_path(self, args: argparse.Namespace) -> tuple[Path, dict]:
        """
        Resolve source path and repository information.

        Returns:
            Tuple of (source_path, repo_info)
        """
        if args.repo:
            # Clone repository
            git_handler = GitHandler(self.config.git)
            repo_path = git_handler.clone_repository(args.repo)
            repo_info = {
                "url": args.repo,
                "name": git_handler.extract_repo_name(args.repo),
                "temp_dir": repo_path,
            }
            return repo_path, repo_info
        else:
            # Use local folder
            if not args.folder:
                raise ValidationError("Must specify folder path or use --repo")

            folder_path = Path(args.folder).resolve()
            if not folder_path.exists() or not folder_path.is_dir():
                raise ValidationError(f"Invalid directory: {folder_path}")

            # Check if it's a git repository
            git_handler = GitHandler(self.config.git)
            repo_info = git_handler.get_repository_info(folder_path)

            return folder_path, repo_info

    def _run_test_mode(self, args: argparse.Namespace) -> int:
        """Run in test mode (show structure only)."""
        source_path, repo_info = self._resolve_source_path(args)

        try:
            scanner = CodeScanner(self.config.scan)
            structure = scanner.generate_directory_tree(
                source_path, repo_info.get("name")
            )

            print("Project Structure:\n")
            print(structure)

            return 0

        finally:
            # Cleanup temp directory if needed
            if "temp_dir" in repo_info:
                GitHandler(self.config.git).cleanup_temp_directory(
                    repo_info["temp_dir"]
                )

    def _execute_workflow(self, source_path: Path, repo_info: dict) -> int:
        """Execute main processing workflow."""
        try:
            # Initialize components
            scanner = CodeScanner(self.config.scan)
            processor = FileProcessor(self.config.scan)
            formatter = MarkdownFormatter(self.config.output)

            # Scan for files
            self.logger.info(f"Scanning directory: {source_path}")
            files = scanner.scan_directory(source_path)

            if not files:
                self.logger.warning("No files found to process")
                return 0

            # Generate project structure
            structure = scanner.generate_directory_tree(
                source_path, repo_info.get("name")
            )

            # Process files
            file_contents = processor.process_files(files)

            if not file_contents:
                self.logger.warning("No files were successfully processed")
                return 0

            # Format output
            parts = formatter.format_content(
                files=file_contents,
                project_structure=structure,
                root_path=source_path,
                repo_url=repo_info.get("url"),
                repo_name=repo_info.get("name"),
            )

            # Save output files
            output_dir = Path.cwd()
            created_files = formatter.save_parts(parts, output_dir)

            self.logger.info(f"Created {len(created_files)} output files:")
            for file_path in created_files:
                self.logger.info(f"  - {file_path.name}")

            return 0

        finally:
            # Cleanup temp directory if needed
            if "temp_dir" in repo_info:
                GitHandler(self.config.git).cleanup_temp_directory(
                    repo_info["temp_dir"]
                )


def main() -> int:
    """Main entry point for the CLI."""
    cli = CodeSnapCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
