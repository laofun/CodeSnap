"""Output formatting and generation."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..config.settings import OutputConfig
from ..utils.exceptions import FileProcessingError
from ..utils.logger import get_logger
from .processor import FileContent


class MarkdownFormatter:
    """Formats processed files into Markdown output."""

    def __init__(self, config: OutputConfig) -> None:
        self.config = config
        self.logger = get_logger()

    def format_content(
        self,
        files: List[FileContent],
        project_structure: str,
        root_path: Path,
        repo_url: Optional[str] = None,
        repo_name: Optional[str] = None,
    ) -> List[str]:
        """
        Format file contents into Markdown parts.

        Args:
            files: List of processed file contents
            project_structure: Directory tree structure
            root_path: Root directory path
            repo_url: Optional repository URL
            repo_name: Optional repository name

        Returns:
            List of formatted Markdown strings
        """
        if not files:
            self.logger.warning("No files to format")
            return []

        # Format individual file snippets
        snippets = [self._format_file_snippet(file_content) for file_content in files]

        # Split into parts based on token limits
        parts = self._split_into_parts(snippets)

        # Add headers to each part
        formatted_parts = []
        for idx, part_content in enumerate(parts, 1):
            header = self._generate_header(
                part_number=idx,
                total_parts=len(parts),
                project_structure=project_structure if idx == 1 else None,
                root_path=root_path,
                repo_url=repo_url,
                repo_name=repo_name,
            )
            formatted_parts.append(header + part_content)

        return formatted_parts

    def _format_file_snippet(self, file_content: FileContent) -> str:
        """
        Format a single file into a Markdown snippet.

        Args:
            file_content: File content to format

        Returns:
            Formatted Markdown snippet
        """
        separator = "---\n"
        file_header = f"### File: {file_content.relative_path}\n"

        if file_content.extension == "md":
            # Markdown files are included as plain text
            return f"{separator}{file_header}\n{file_content.content}\n{separator}"
        else:
            # Other files are wrapped in code blocks
            return (
                f"{separator}{file_header}"
                f"```{file_content.extension}\n"
                f"{file_content.content}\n"
                f"```\n{separator}"
            )

    def _split_into_parts(self, snippets: List[str]) -> List[str]:
        """
        Split snippets into parts based on token limits.

        Args:
            snippets: List of formatted file snippets

        Returns:
            List of part contents
        """
        parts = []
        current_part = ""

        for snippet in snippets:
            # Rough token estimation
            current_tokens = len(current_part) // 4
            snippet_tokens = len(snippet) // 4

            if (
                current_part
                and (current_tokens + snippet_tokens) > self.config.max_tokens_per_part
            ):
                # Start new part
                parts.append(current_part)
                current_part = snippet
            else:
                current_part += snippet

        # Add the last part
        if current_part:
            parts.append(current_part)

        return parts

    def _generate_header(
        self,
        part_number: int,
        total_parts: int,
        project_structure: Optional[str],
        root_path: Path,
        repo_url: Optional[str] = None,
        repo_name: Optional[str] = None,
    ) -> str:
        """
        Generate header for a part.

        Args:
            part_number: Current part number
            total_parts: Total number of parts
            project_structure: Directory structure (only for first part)
            root_path: Root directory path
            repo_url: Optional repository URL
            repo_name: Optional repository name

        Returns:
            Formatted header string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        project_display = repo_name or root_path.name

        if part_number == 1:
            # First part gets full header with instructions
            header = self._generate_instructions()
            header += f"# Code Summary (Part {part_number} of {total_parts})\n\n"
            header += f"**Generated on:** {timestamp}\n"
            header += f"**Project:** {project_display}\n"

            if repo_url:
                header += f"**Repository:** {repo_url}\n"

            if project_structure and self.config.include_structure:
                header += "\n## Project Structure\n\n"
                header += "```\n"
                header += f"{project_structure}\n"
                header += "```\n\n"

            header += "## Files\n\n"
        else:
            # Continuation parts get simplified header
            header = (
                f"# Code Summary (Part {part_number} of {total_parts}) - Continued\n\n"
            )
            header += f"**Generated on:** {timestamp}\n"
            header += f"**Project:** {project_display}\n"

            if repo_url:
                header += f"**Repository:** {repo_url}\n"

            header += "\n## Files (Continued)\n\n"

        return header

    def _generate_instructions(self) -> str:
        """Generate AI processing instructions."""
        return """# Instructions for AI

This file contains a structured summary of a codebase for analysis. Please:

1. **Parse Content**: Each file is delimited by `---` separators under
   `### File:` headings
2. **Use Structure**: Reference the Project Structure tree to understand
   organization
3. **Analyze Relationships**: Identify imports, dependencies, and file roles
4. **Wait for All Parts**: Process all parts (e.g., codesnap_part_X.md)
   before responding
5. **Focus on Logic**: Explain functionality, suggest improvements, or
   identify issues

**Important**: Only begin analysis once all parts are available. Focus on
code logic and project architecture!

---

"""

    def save_parts(
        self, parts: List[str], output_dir: Path, overwrite_existing: bool = False
    ) -> List[Path]:
        """
        Save formatted parts to files.

        Args:
            parts: List of formatted part contents
            output_dir: Directory to save files in
            overwrite_existing: Whether to overwrite existing files

        Returns:
            List of created file paths

        Raises:
            FileProcessingError: If saving fails
        """
        if not parts:
            raise FileProcessingError("No parts to save")

        output_dir.mkdir(parents=True, exist_ok=True)
        created_files = []

        for idx, part_content in enumerate(parts, 1):
            filename = f"{self.config.base_name}_part_{idx}.md"
            file_path = output_dir / filename

            # Handle existing files
            if file_path.exists() and not overwrite_existing:
                response = (
                    input(f"File '{filename}' exists. Overwrite? [y/N]: ")
                    .strip()
                    .lower()
                )
                if response != "y":
                    self.logger.warning(
                        f"Skipped {filename} (user chose not to overwrite)"
                    )
                    continue

            try:
                file_path.write_text(part_content, encoding="utf-8")
                created_files.append(file_path)
                self.logger.info(f"Created {filename}")
            except OSError as e:
                raise FileProcessingError(
                    f"Failed to write {filename}",
                    file_path=str(file_path),
                    details=str(e),
                )

        return created_files
