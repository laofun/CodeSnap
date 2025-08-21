"""Setup script for CodeSnap."""

from pathlib import Path
from setuptools import setup, find_packages

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read version from package
version_file = Path(__file__).parent / "codesnap" / "__init__.py"
version = "2.0.0"
if version_file.exists():
    for line in version_file.read_text(encoding="utf-8").split("\n"):
        if line.startswith("__version__"):
            version = line.split('"')[1]
            break

setup(
    name="codesnap",
    version=version,
    author="CodeSnap Team",
    author_email="codesnap@example.com",
    description="Professional code analysis and documentation generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/laofun/CodeSnap",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "tqdm>=4.65.0",
    ],
    extras_require={
        "rich": ["rich>=13.0.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "codesnap=codesnap.cli:main",
        ],
    },
    keywords="code analysis documentation markdown git repository scanner",
    project_urls={
        "Bug Reports": "https://github.com/laofun/CodeSnap/issues",
        "Source": "https://github.com/laofun/CodeSnap",
        "Documentation": "https://github.com/laofun/CodeSnap/blob/main/README.md",
    },
    include_package_data=True,
    zip_safe=False,
)