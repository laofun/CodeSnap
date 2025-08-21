"""Tests for the FileProcessor module."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ..config.settings import ScanConfig
from ..core.processor import FileContent, FileProcessor


class TestFileProcessor(unittest.TestCase):
    """Test cases for FileProcessor."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ScanConfig()
        self.processor = FileProcessor(self.config)

        # Create temporary test files
        self.temp_dir = Path(tempfile.mkdtemp())

        self.test_py = self.temp_dir / "test.py"
        self.test_py.write_text("def hello():\n    print('Hello, World!')")

        self.test_js = self.temp_dir / "test.js"
        self.test_js.write_text(
            "function hello() {\n    console.log('Hello, World!');\n}"
        )

        self.test_md = self.temp_dir / "README.md"
        self.test_md.write_text("# Test Project\n\nThis is a test.")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_process_files_empty_list(self):
        """Test processing empty file list."""
        result = self.processor.process_files([])
        self.assertEqual(result, [])

    def test_process_files_success(self):
        """Test successful file processing."""
        files = [
            (self.test_py, self.temp_dir),
            (self.test_js, self.temp_dir),
            (self.test_md, self.temp_dir),
        ]

        results = self.processor.process_files(files, max_workers=1)

        # Should process all files
        self.assertEqual(len(results), 3)

        # Check that FileContent objects are created correctly
        for result in results:
            self.assertIsInstance(result, FileContent)
            self.assertTrue(result.content)
            self.assertTrue(result.extension)

    def test_file_content_properties(self):
        """Test FileContent object properties."""
        files = [(self.test_py, self.temp_dir)]
        results = self.processor.process_files(files, max_workers=1)

        content = results[0]
        self.assertEqual(content.file_path, self.test_py)
        self.assertEqual(content.relative_path, Path("test.py"))
        self.assertEqual(content.extension, "py")
        self.assertIn("def hello", content.content)
        self.assertGreater(content.size_bytes, 0)
        self.assertGreater(content.size_mb, 0)

    def test_estimate_token_count(self):
        """Test token count estimation."""
        text = "This is a test string with some content."
        tokens = self.processor.estimate_token_count(text)

        # Should be roughly len(text) // 4
        expected = len(text) // 4
        self.assertAlmostEqual(tokens, expected, delta=2)

    @patch("codesnap.core.processor.get_logger")
    def test_logging_integration(self, mock_logger):
        """Test logging integration."""
        # Mock the logger that will be used by the FileProcessor
        mock_logger_instance = mock_logger.return_value

        # Create a new processor that will use the mocked logger
        processor = FileProcessor(self.config)
        processor.logger = mock_logger_instance

        files = [(self.test_py, self.temp_dir)]
        processor.process_files(files, max_workers=1)

        # Should log processing information
        mock_logger_instance.info.assert_called()

    def test_large_file_exclusion(self):
        """Test that large files are excluded."""
        # Create a file larger than the limit
        large_file = self.temp_dir / "large.py"
        large_content = "# " + "x" * (
            int(self.config.max_file_size_mb * 1024 * 1024) + 1000
        )
        large_file.write_text(large_content)

        files = [(large_file, self.temp_dir)]
        results = self.processor.process_files(files, max_workers=1)

        # Large file should be excluded
        self.assertEqual(len(results), 0)

    def test_unicode_handling(self):
        """Test handling of Unicode content."""
        unicode_file = self.temp_dir / "unicode.py"
        unicode_content = (
            "# -*- coding: utf-8 -*-\ndef greet():\n    print('Héllo, Wörld! 🌍')"
        )
        unicode_file.write_text(unicode_content, encoding="utf-8")

        files = [(unicode_file, self.temp_dir)]
        results = self.processor.process_files(files, max_workers=1)

        self.assertEqual(len(results), 1)
        self.assertIn("🌍", results[0].content)
        self.assertIn("Héllo", results[0].content)


if __name__ == "__main__":
    unittest.main()
