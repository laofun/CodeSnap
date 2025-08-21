"""Tests for the CodeScanner module."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ..config.settings import ScanConfig
from ..core.scanner import CodeScanner
from ..utils.exceptions import FileProcessingError


class TestCodeScanner(unittest.TestCase):
    """Test cases for CodeScanner."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ScanConfig()
        self.scanner = CodeScanner(self.config)

        # Create temporary directory structure for testing
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test files
        (self.temp_dir / "test.py").write_text("print('hello')")
        (self.temp_dir / "test.js").write_text("console.log('hello')")
        (self.temp_dir / "README.md").write_text("# Test")

        # Create subdirectory
        subdir = self.temp_dir / "src"
        subdir.mkdir()
        (subdir / "main.py").write_text("def main(): pass")

        # Create excluded directory
        excluded = self.temp_dir / "node_modules"
        excluded.mkdir()
        (excluded / "package.js").write_text("module.exports = {}")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scan_directory_success(self):
        """Test successful directory scanning."""
        files = self.scanner.scan_directory(self.temp_dir)

        # Should find .py and .js files, excluding .md and node_modules
        file_names = [f[0].name for f in files]

        self.assertIn("test.py", file_names)
        self.assertIn("test.js", file_names)
        self.assertIn("main.py", file_names)
        self.assertNotIn("README.md", file_names)  # Excluded by pattern
        self.assertNotIn("package.js", file_names)  # In excluded directory

    def test_scan_invalid_directory(self):
        """Test scanning invalid directory."""
        invalid_path = Path("/nonexistent/directory")

        with self.assertRaises(FileProcessingError):
            self.scanner.scan_directory(invalid_path)

    def test_exclude_patterns(self):
        """Test file exclusion patterns."""
        # Add custom exclude pattern
        self.config.exclude_patterns.append("test.*")
        scanner = CodeScanner(self.config)

        files = scanner.scan_directory(self.temp_dir)
        file_names = [f[0].name for f in files]

        # test.py and test.js should be excluded
        self.assertNotIn("test.py", file_names)
        self.assertNotIn("test.js", file_names)
        self.assertIn("main.py", file_names)  # Should still be included

    def test_no_subfolders(self):
        """Test scanning without subfolders."""
        self.config.scan_subfolders = False
        scanner = CodeScanner(self.config)

        files = scanner.scan_directory(self.temp_dir)
        file_names = [f[0].name for f in files]

        # Should only find files in root directory
        self.assertIn("test.py", file_names)
        self.assertIn("test.js", file_names)
        self.assertNotIn("main.py", file_names)  # In subdirectory

    def test_file_size_limit(self):
        """Test file size limiting."""
        # Create a large file
        large_file = self.temp_dir / "large.py"
        large_content = "# " + "x" * (
            int(self.config.max_file_size_mb * 1024 * 1024) + 1000
        )
        large_file.write_text(large_content)

        files = self.scanner.scan_directory(self.temp_dir)
        file_names = [f[0].name for f in files]

        # Large file should be excluded
        self.assertNotIn("large.py", file_names)

    def test_generate_directory_tree(self):
        """Test directory tree generation."""
        tree = self.scanner.generate_directory_tree(self.temp_dir)

        # Should contain directory structure
        self.assertIn(self.temp_dir.name, tree)
        self.assertIn("src", tree)
        self.assertIn("test.py", tree)
        self.assertNotIn("node_modules", tree)  # Excluded

    @patch("codesnap.core.scanner.get_logger")
    def test_logging_integration(self, mock_logger):
        """Test logging integration."""
        # Mock the logger that will be used by the CodeScanner
        mock_logger_instance = mock_logger.return_value

        # Create a new scanner that will use the mocked logger
        scanner = CodeScanner(self.config)
        scanner.logger = mock_logger_instance

        scanner.scan_directory(self.temp_dir)

        # Should log the number of files found
        mock_logger_instance.info.assert_called()


if __name__ == "__main__":
    unittest.main()
