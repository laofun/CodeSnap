"""Tests for configuration management."""

import json
import tempfile
import unittest
from pathlib import Path

from ..config.settings import CodeSnapConfig, OutputConfig, ScanConfig
from ..config.validator import ConfigValidator
from ..utils.exceptions import ConfigurationError, ValidationError


class TestCodeSnapConfig(unittest.TestCase):
    """Test cases for CodeSnapConfig."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_config(self):
        """Test default configuration creation."""
        config = CodeSnapConfig()

        # Check default values
        self.assertIsInstance(config.scan, ScanConfig)
        self.assertIsInstance(config.output, OutputConfig)
        self.assertFalse(config.debug)
        self.assertIsNone(config.log_file)

        # Check scan defaults
        self.assertIn(".py", config.scan.extensions)
        self.assertIn("node_modules", config.scan.exclude_dirs)
        self.assertEqual(config.scan.max_file_size_mb, 2.0)
        self.assertTrue(config.scan.scan_subfolders)

    def test_from_dict(self):
        """Test configuration creation from dictionary."""
        data = {
            "extensions": [".py", ".js"],
            "exclude_dirs": ["build", "dist"],
            "max_size": 5.0,
            "output": "my_codesnap",
            "max_tokens": 15000,
            "debug": True,
        }

        config = CodeSnapConfig.from_dict(data)

        self.assertEqual(config.scan.extensions, [".py", ".js"])
        self.assertIn("build", config.scan.exclude_dirs)
        self.assertEqual(config.scan.max_file_size_mb, 5.0)
        self.assertEqual(config.output.base_name, "my_codesnap")
        self.assertEqual(config.output.max_tokens_per_part, 15000)
        self.assertTrue(config.debug)

    def test_from_file(self):
        """Test configuration loading from JSON file."""
        config_data = {
            "extensions": [".go", ".rs"],
            "output": "test_output",
            "debug": True,
        }

        config_file = self.temp_dir / "config.json"
        with config_file.open("w") as f:
            json.dump(config_data, f)

        config = CodeSnapConfig.from_file(config_file)

        self.assertEqual(config.scan.extensions, [".go", ".rs"])
        self.assertEqual(config.output.base_name, "test_output")
        self.assertTrue(config.debug)

    def test_from_file_not_found(self):
        """Test loading from non-existent file."""
        config_file = self.temp_dir / "nonexistent.json"

        with self.assertRaises(ConfigurationError):
            CodeSnapConfig.from_file(config_file)

    def test_from_file_invalid_json(self):
        """Test loading from invalid JSON file."""
        config_file = self.temp_dir / "invalid.json"
        config_file.write_text("{ invalid json }")

        with self.assertRaises(ConfigurationError):
            CodeSnapConfig.from_file(config_file)

    def test_to_dict(self):
        """Test configuration conversion to dictionary."""
        config = CodeSnapConfig()
        config.scan.extensions = [".py", ".js"]
        config.output.base_name = "test"
        config.debug = True

        data = config.to_dict()

        self.assertEqual(data["extensions"], [".py", ".js"])
        self.assertEqual(data["output"], "test")
        self.assertTrue(data["debug"])

    def test_save_to_file(self):
        """Test saving configuration to file."""
        config = CodeSnapConfig()
        config.output.base_name = "saved_config"

        config_file = self.temp_dir / "saved.json"
        config.save_to_file(config_file)

        # Verify file was created and contains expected data
        self.assertTrue(config_file.exists())

        with config_file.open() as f:
            data = json.load(f)

        self.assertEqual(data["output"], "saved_config")


class TestConfigValidator(unittest.TestCase):
    """Test cases for ConfigValidator."""

    def test_validate_extensions_success(self):
        """Test successful extension validation."""
        extensions = [".py", ".js", ".ts"]
        ConfigValidator.validate_extensions(extensions)  # Should not raise

    def test_validate_extensions_empty(self):
        """Test validation with empty extensions."""
        with self.assertRaises(ValidationError):
            ConfigValidator.validate_extensions([])

    def test_validate_extensions_no_dot(self):
        """Test validation with extensions missing dots."""
        with self.assertRaises(ValidationError):
            ConfigValidator.validate_extensions(["py", "js"])

    def test_validate_file_size_success(self):
        """Test successful file size validation."""
        ConfigValidator.validate_file_size(2.5)  # Should not raise

    def test_validate_file_size_negative(self):
        """Test validation with negative file size."""
        with self.assertRaises(ValidationError):
            ConfigValidator.validate_file_size(-1.0)

    def test_validate_file_size_too_large(self):
        """Test validation with excessively large file size."""
        with self.assertRaises(ValidationError):
            ConfigValidator.validate_file_size(150.0)

    def test_validate_tokens_success(self):
        """Test successful token validation."""
        ConfigValidator.validate_tokens(10000)  # Should not raise

    def test_validate_tokens_too_small(self):
        """Test validation with too few tokens."""
        with self.assertRaises(ValidationError):
            ConfigValidator.validate_tokens(500)

    def test_validate_tokens_too_large(self):
        """Test validation with too many tokens."""
        with self.assertRaises(ValidationError):
            ConfigValidator.validate_tokens(200000)

    def test_validate_config_success(self):
        """Test successful complete configuration validation."""
        config = CodeSnapConfig()
        ConfigValidator.validate_config(config)  # Should not raise

    def test_validate_config_with_errors(self):
        """Test configuration validation with errors."""
        config = CodeSnapConfig()
        config.scan.extensions = []  # Invalid

        with self.assertRaises(ValidationError):
            ConfigValidator.validate_config(config)


if __name__ == "__main__":
    unittest.main()
