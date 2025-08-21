.PHONY: help install install-dev test test-cov lint format type-check clean build upload

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install package and dependencies"
	@echo "  install-dev  - Install package in development mode with dev dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black, isort)"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  upload       - Upload to PyPI (requires credentials)"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt

# Testing
test:
	python -m pytest codesnap/tests/

test-cov:
	python -m pytest --cov=codesnap --cov-report=html --cov-report=term-missing codesnap/tests/

# Code quality
lint:
	python -m flake8 codesnap/

format:
	python -m black codesnap/
	python -m isort codesnap/

type-check:
	python -m mypy codesnap/

# Quality check all
check: lint type-check test

# Clean up
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build and upload
build: clean
	python -m build

upload: build
	python -m twine upload dist/*

# Development workflow
dev-setup: install-dev
	@echo "Development environment set up successfully!"
	@echo "Run 'make check' to verify everything works."

# Run examples
run-example:
	python -m codesnap.cli --test .

# Create example config
create-example-config:
	@echo "Example config already exists: config.example.json"
	@echo "Copy it to your desired name: cp config.example.json my-config.json"