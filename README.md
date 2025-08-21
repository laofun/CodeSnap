# CodeSnap 2.0 🚀

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](https://mypy.readthedocs.io/)

> Professional code analysis and documentation generator for AI-assisted development

CodeSnap transforms your codebase into comprehensive Markdown summaries, perfect for AI code analysis, documentation, and project understanding. Built with modern Python practices and enterprise-grade architecture.

## ✨ Key Features

- **🔍 Intelligent Scanning** - Smart file discovery with advanced filtering
- **⚡ Lightning Fast** - Parallel processing with beautiful progress tracking  
- **🎯 Highly Configurable** - JSON configs + CLI overrides for maximum flexibility
- **📁 Git Native** - Clone and analyze any repository instantly
- **🎨 Beautiful Output** - Rich console formatting and structured Markdown
- **🧪 Test Mode** - Preview project structure before processing
- **🛡️ Type Safe** - Full type hints and validation throughout
- **🔧 Developer Friendly** - Comprehensive test suite and modern tooling

## 🏃‍♂️ Quick Start

### Installation

**Prerequisites**: Python 3.8+ required

```bash
# Clone the repository
git clone https://github.com/laofun/CodeSnap.git
cd codesnap

# Install for regular use
pip install -e .

# Install for development (includes dev dependencies)
make dev-setup

# Verify installation
codesnap --version
```

### Basic Usage

```bash
# Analyze local project
codesnap /path/to/your/project

# Analyze GitHub repository
codesnap --repo https://github.com/laofun/CodeSnap.git

# Preview structure only
codesnap --test /path/to/project

# Custom output name
codesnap /path/to/project -o my_analysis
```

## 📖 Usage Examples

### Analyze Different Project Types

```bash
# Python project
codesnap /path/to/python-project -e .py .pyi -x tests __pycache__

# JavaScript/TypeScript project  
codesnap /path/to/web-project -e .js .ts .jsx .tsx -x node_modules dist

# Go project
codesnap /path/to/go-project -e .go -x vendor

# Multi-language project
codesnap /path/to/project -e .py .js .go .rs .java
```

### Advanced Configuration

```bash
# Custom token limits and file size
codesnap /path/to/project -t 20000 -m 5.0

# Exclude specific patterns
codesnap /path/to/project -p "*.test.js" -p "*.spec.ts" -p "*.min.*"

# Debug mode with detailed logging
codesnap --debug /path/to/project

# No subdirectories (root level only)
codesnap --no-subfolders /path/to/project
```

## ⚙️ Configuration

### Command Line Options

```
codesnap [FOLDER] [OPTIONS]

POSITIONAL ARGUMENTS:
  folder                    Local folder path to analyze

CORE OPTIONS:
  -r, --repo URL           Git repository URL to clone and analyze
  -o, --output NAME        Output file base name (default: codesnap)
  -c, --config FILE        JSON configuration file path

FILE FILTERING:
  -e, --extensions EXT     File extensions to include (.py .js .ts)
  -x, --exclude-dirs DIR   Additional directories to exclude  
  -p, --exclude-patterns   File patterns to exclude (supports wildcards)
  -f, --exclude-files FILE Specific filenames to exclude
  -m, --max-size MB        Maximum file size in MB (default: 2.0)

OUTPUT CONTROL:
  -t, --max-tokens NUM     Maximum tokens per output part (default: 12000)
  -n, --no-subfolders      Only scan top-level directory

UTILITY:
  --test                   Show project structure and exit
  --debug                  Enable detailed debug logging
  --version                Show version information
  -h, --help               Show help message
```

### JSON Configuration

Create a `config.json` for reusable settings:

```json
{
  "extensions": [".py", ".js", ".ts", ".go", ".rs"],
  "exclude_dirs": [
    "node_modules", "dist", "build", "__pycache__", 
    ".git", ".vscode", "vendor", "target"
  ],
  "exclude_patterns": [
    "*.test.js", "*.spec.ts", "*.min.*", 
    "*.bundle.*", "*.generated.*"
  ],
  "max_size": 3.0,
  "max_tokens": 15000,
  "output": "my_project_analysis",
  "debug": false
}
```

Use configuration file:
```bash
codesnap --config config.json /path/to/project
```

## 📁 Output Structure

CodeSnap generates structured Markdown files:

```
my_project_part_1.md     # Main analysis with project structure
my_project_part_2.md     # Continuation (if needed)
my_project_part_N.md     # Additional parts for large projects
```

Each output includes:
- **AI Processing Instructions** - Clear guidance for AI analysis
- **Project Structure Tree** - Visual directory layout  
- **File Contents** - Organized code with syntax highlighting
- **Metadata** - Timestamps, repository info, generation details

## 🏗️ Architecture

CodeSnap 2.0 features a clean, modular architecture:

```
codesnap/
├── core/                 # Core functionality
│   ├── scanner.py       # File discovery and filtering
│   ├── processor.py     # Parallel file processing
│   ├── formatter.py     # Markdown output generation
│   └── git_handler.py   # Git repository operations
├── config/              # Configuration management
│   ├── settings.py      # Configuration classes
│   └── validator.py     # Input validation
├── utils/               # Shared utilities
│   ├── exceptions.py    # Custom exception types
│   └── logger.py        # Professional logging
├── tests/               # Comprehensive test suite
└── cli.py               # Command-line interface
```

## 📦 Dependencies

### Core Requirements
- **Python 3.8+** - Modern Python version
- **tqdm** - Progress bars and terminal output
- **rich** (optional) - Enhanced console formatting

### Development Dependencies
- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **black** - Code formatting
- **isort** - Import sorting
- **mypy** - Static type checking
- **flake8** - Linting

Install all dependencies:
```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies  
pip install -r requirements-dev.txt
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/laofun/CodeSnap.git
cd codesnap
make dev-setup

# Verify installation
make check
```

### Development Commands

```bash
# Testing
make test              # Run test suite
make test-cov          # Run tests with coverage report

# Code Quality
make lint              # Run flake8 linting
make format            # Format code with black + isort
make type-check        # Run mypy type checking
make check             # Run all quality checks

# Build & Distribution
make build             # Build distribution packages
make clean             # Clean build artifacts
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=codesnap --cov-report=html

# Run specific test file
python -m pytest codesnap/tests/test_scanner.py
```

## 🎯 Use Cases

- **🤖 AI Code Analysis** - Generate comprehensive summaries for ChatGPT, Claude, etc.
- **📚 Documentation** - Create project overviews and onboarding materials
- **🔍 Code Review** - Understand large codebases quickly
- **📊 Project Assessment** - Analyze structure and complexity
- **🔄 Migration Planning** - Document legacy systems before refactoring
- **🎓 Learning** - Explore open source projects systematically

## 🚀 Performance

- **Parallel Processing** - Utilizes all CPU cores for file processing
- **Smart Filtering** - Efficient exclusion of unwanted files and directories
- **Memory Efficient** - Streams large files without loading everything into memory
- **Progress Tracking** - Real-time progress bars with ETA
- **Incremental Output** - Splits large projects into manageable parts

## 🔧 Troubleshooting

### Common Issues

**Command not found: `codesnap`**
```bash
# Make sure you installed the package
pip install -e .

# Or check if it's in your PATH
python -m codesnap.cli --help
```

**Import errors or module not found**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# For development
make dev-setup
```

**Permission denied when cloning repositories**
```bash
# Make sure you have git installed
git --version

# Check SSH keys for private repos
ssh -T git@github.com
```

**Large files causing memory issues**
```bash
# Reduce file size limit
codesnap /path/to/project --max-size 1.0

# Exclude large directories
codesnap /path/to/project -x node_modules dist build
```

**Getting help**
```bash
# Show all available options
codesnap --help

# Enable debug mode for detailed logs
codesnap --debug /path/to/project
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
4. **Make** your changes
5. **Test** your changes (`make check`)
6. **Commit** with clear messages (`git commit -m 'Add amazing feature'`)
7. **Push** to your branch (`git push origin feature/amazing-feature`)
8. **Create** a Pull Request

### Development Guidelines

- Write comprehensive tests for new features
- Follow existing code style (black + isort)
- Add type hints for all new code
- Update documentation for user-facing changes
- Ensure all quality checks pass (`make check`)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python best practices
- Inspired by the need for better AI-assisted code analysis
- Thanks to the open source community for excellent tools and libraries

---

**Made with ❤️ for developers who love clean code and powerful tools**