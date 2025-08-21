# Changelog

All notable changes to CodeSnap will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-08-21

### Added
- 🏗️ **Complete architectural refactor** from monolithic to modular design
- ⚡ **Parallel file processing** with progress tracking
- 🎨 **Rich console output** with beautiful formatting
- 🔧 **Professional configuration system** with JSON configs and CLI overrides
- 🛡️ **Type safety** with comprehensive type hints throughout
- ✅ **Comprehensive test suite** with 32 unit tests
- 📦 **Modern packaging** with pyproject.toml and setup.py
- 🔍 **Smart filtering** with advanced exclusion patterns
- 📊 **Professional logging** with debug support
- 🧪 **Test mode** for previewing project structure
- 📁 **Git integration** with shallow cloning support
- 🎯 **Token management** with intelligent output splitting

### Changed
- **Breaking**: Complete rewrite of codebase structure
- **Breaking**: New CLI interface with improved argument handling
- **Breaking**: Configuration format changes for better organization
- Improved error handling with custom exception classes
- Enhanced file processing with better Unicode support
- Better memory efficiency for large projects

### Removed
- Monolithic `codesnap.py` file (replaced with modular structure)
- Legacy command-line argument format
- Basic console output (replaced with rich formatting)

## [1.0.0] - Previous Version

### Added
- Basic code scanning functionality
- Simple Markdown output generation
- Git repository cloning
- Basic file filtering
- Command-line interface

---

**Migration Guide from 1.x to 2.0:**

1. **Installation**: Install new version with `pip install -e .`
2. **CLI**: Use new `codesnap` command instead of `python codesnap.py`
3. **Config**: Update configuration files to new JSON format (see `config.example.json`)
4. **Output**: Output files now include AI processing instructions and better formatting