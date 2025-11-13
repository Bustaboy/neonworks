"""Setup script for Neon Works Game Engine."""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="neon-works",
    version="0.1.0",
    description="A comprehensive, project-based 2D game engine for turn-based strategy games",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Neon Works Team",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "neonworks=engine.cli:main",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.1",
            "mypy>=1.7.1",
            "flake8>=6.1.0",
            "pylint>=3.0.3",
            "isort>=5.13.2",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: pygame",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="game-engine pygame 2d turn-based strategy",
    project_urls={
        "Documentation": "https://github.com/yourusername/neon-collapse",
        "Source": "https://github.com/yourusername/neon-collapse",
        "Bug Reports": "https://github.com/yourusername/neon-collapse/issues",
    },
)
