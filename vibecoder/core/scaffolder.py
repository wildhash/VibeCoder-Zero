"""Project scaffolding for VibeCoder-Zero.

This module provides autonomous project generation capabilities,
creating complete, tested, and executable project structures.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json


@dataclass
class ProjectSpec:
    """Specification for a project to be generated."""
    name: str
    description: str
    language: str  # 'python', 'javascript', 'typescript', etc.
    project_type: str  # 'cli', 'web', 'api', 'library'
    features: List[str]  # ['testing', 'ci', 'docker', 'docs']
    dependencies: List[str] = field(default_factory=list)


@dataclass 
class GeneratedFile:
    """Represents a file to be generated."""
    path: str
    content: str
    executable: bool = False


class ProjectScaffolder:
    """Generates complete project structures based on specifications."""
    
    PYTHON_TEMPLATES = {
        'cli': {
            'main.py': '''#!/usr/bin/env python3
"""Main entry point for {name}."""

import argparse
import sys


def main():
    """Main function for {name}."""
    parser = argparse.ArgumentParser(
        description="{description}"
    )
    parser.add_argument('--version', action='version', version='1.0.0')
    args = parser.parse_args()
    
    print("{name} is running!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''',
            'src/__init__.py': '''"""{name} - {description}"""

__version__ = "1.0.0"
''',
            'src/core.py': '''"""Core functionality for {name}."""


class {class_name}:
    """Main class for {name}."""
    
    def __init__(self):
        """Initialize {class_name}."""
        self._initialized = True
    
    def run(self) -> str:
        """Execute main functionality.
        
        Returns:
            str: Result message
        """
        return "Success"
''',
            'tests/__init__.py': '"""Tests for {name}."""\n',
            'tests/test_core.py': '''"""Tests for core functionality."""

import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import {class_name}


def test_{name_lower}_initialization():
    """Test {class_name} can be initialized."""
    instance = {class_name}()
    assert instance._initialized is True


def test_{name_lower}_run():
    """Test {class_name} run method."""
    instance = {class_name}()
    result = instance.run()
    assert result == "Success"


if __name__ == "__main__":
    test_{name_lower}_initialization()
    test_{name_lower}_run()
    print("All tests passed!")
''',
        },
        'api': {
            'main.py': '''#!/usr/bin/env python3
"""API server for {name}."""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class APIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for {name} API."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self._send_json({{"status": "healthy", "service": "{name}"}})
        elif self.path == '/api/v1/status':
            self._send_json({{"name": "{name}", "version": "1.0.0", "status": "running"}})
        else:
            self._send_error(404, "Not found")
    
    def _send_json(self, data: dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, status: int, message: str):
        """Send error response."""
        self._send_json({{"error": message}}, status)


def main():
    """Start the API server."""
    server = HTTPServer(('localhost', 8080), APIHandler)
    print(f"Starting {name} API on http://localhost:8080")
    server.serve_forever()


if __name__ == "__main__":
    main()
''',
        },
        'library': {
            'src/__init__.py': '''"""{name} - {description}

This is a Python library for {description}.
"""

__version__ = "1.0.0"

from .core import {class_name}

__all__ = ["{class_name}"]
''',
        }
    }

    CONFIG_TEMPLATES = {
        'pyproject.toml': '''[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "1.0.0"
description = "{description}"
readme = "README.md"
requires-python = ">=3.8"
license = {{text = "MIT"}}
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [{dependencies}]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "pylint>=2.0.0",
]

[project.scripts]
{name} = "{name}.main:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"

[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']
''',
        'README.md': '''# {name}

{description}

## Installation

```bash
pip install {name}
```

## Usage

```python
from {name} import {class_name}

# Create instance
instance = {class_name}()

# Run
result = instance.run()
print(result)
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .

# Lint code
pylint src/
```

## License

MIT License
''',
        '.gitignore': '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.eggs/
venv/
.venv/
env/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db
''',
        'Makefile': '''.PHONY: help install test lint format clean

help:
\t@echo "{name} - {description}"
\t@echo ""
\t@echo "Commands:"
\t@echo "  make install  - Install dependencies"
\t@echo "  make test     - Run tests"
\t@echo "  make lint     - Run linter"
\t@echo "  make format   - Format code"
\t@echo "  make clean    - Clean build artifacts"

install:
\tpip install -e ".[dev]"

test:
\tpytest -v

lint:
\tpylint src/

format:
\tblack .

clean:
\tfind . -type d -name __pycache__ -exec rm -rf {{}} + 2>/dev/null || true
\tfind . -type f -name "*.pyc" -delete
\trm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/
''',
    }

    CI_TEMPLATES = {
        '.github/workflows/ci.yml': '''name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{{{ matrix.python-version }}}}
        uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python-version }}}}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      
      - name: Lint with pylint
        run: pylint src/ || true
      
      - name: Test with pytest
        run: pytest -v --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
''',
    }

    DOCKER_TEMPLATES = {
        'Dockerfile': '''FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install dependencies
RUN pip install --no-cache-dir .

# Run the application
CMD ["{name}"]
''',
        'docker-compose.yml': '''version: "3.8"

services:
  {name}:
    build: .
    container_name: {name}
    ports:
      - "8080:8080"
    environment:
      - ENVIRONMENT=development
    restart: unless-stopped
''',
    }

    def __init__(self, target_dir: Path):
        """Initialize scaffolder with target directory."""
        self.target_dir = Path(target_dir)
    
    def scaffold(self, spec: ProjectSpec) -> List[GeneratedFile]:
        """Generate a complete project based on specification.
        
        Args:
            spec: Project specification
            
        Returns:
            List of generated files
        """
        files = []
        
        # Create template variables
        template_vars = self._create_template_vars(spec)
        
        if spec.language == 'python':
            files.extend(self._scaffold_python(spec, template_vars))
        
        # Add configuration files
        files.extend(self._scaffold_config(spec, template_vars))
        
        # Add CI/CD if requested
        if 'ci' in spec.features:
            files.extend(self._scaffold_ci(spec, template_vars))
        
        # Add Docker if requested
        if 'docker' in spec.features:
            files.extend(self._scaffold_docker(spec, template_vars))
        
        return files
    
    def write_files(self, files: List[GeneratedFile]) -> List[Path]:
        """Write generated files to disk.
        
        Args:
            files: List of files to write
            
        Returns:
            List of created file paths
        """
        created = []
        
        for file in files:
            file_path = self.target_dir / file.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file.content)
            
            if file.executable:
                file_path.chmod(0o755)
            
            created.append(file_path)
        
        return created
    
    def _create_template_vars(self, spec: ProjectSpec) -> Dict[str, str]:
        """Create template variables from spec."""
        name_lower = spec.name.lower().replace('-', '_').replace(' ', '_')
        class_name = ''.join(word.capitalize() for word in spec.name.replace('-', ' ').replace('_', ' ').split())
        
        deps_str = ', '.join(f'"{dep}"' for dep in spec.dependencies) if spec.dependencies else ''
        
        return {
            'name': spec.name,
            'name_lower': name_lower,
            'class_name': class_name,
            'description': spec.description,
            'dependencies': deps_str,
        }
    
    def _scaffold_python(self, spec: ProjectSpec, vars: Dict[str, str]) -> List[GeneratedFile]:
        """Generate Python project files."""
        files = []
        
        # Get base templates for project type
        templates = self.PYTHON_TEMPLATES.get('cli', {}).copy()
        
        # Merge project type specific templates
        if spec.project_type in self.PYTHON_TEMPLATES:
            templates.update(self.PYTHON_TEMPLATES[spec.project_type])
        
        # Generate files from templates
        for path, template in templates.items():
            content = template.format(**vars)
            executable = path.endswith('.py') and '#!/' in content
            files.append(GeneratedFile(path=path, content=content, executable=executable))
        
        return files
    
    def _scaffold_config(self, spec: ProjectSpec, vars: Dict[str, str]) -> List[GeneratedFile]:
        """Generate configuration files."""
        files = []
        
        for path, template in self.CONFIG_TEMPLATES.items():
            content = template.format(**vars)
            files.append(GeneratedFile(path=path, content=content))
        
        return files
    
    def _scaffold_ci(self, spec: ProjectSpec, vars: Dict[str, str]) -> List[GeneratedFile]:
        """Generate CI/CD configuration."""
        files = []
        
        for path, template in self.CI_TEMPLATES.items():
            content = template.format(**vars)
            files.append(GeneratedFile(path=path, content=content))
        
        return files
    
    def _scaffold_docker(self, spec: ProjectSpec, vars: Dict[str, str]) -> List[GeneratedFile]:
        """Generate Docker configuration."""
        files = []
        
        for path, template in self.DOCKER_TEMPLATES.items():
            content = template.format(**vars)
            files.append(GeneratedFile(path=path, content=content))
        
        return files


def parse_project_input(input_text: str) -> ProjectSpec:
    """Parse natural language project description into ProjectSpec.
    
    Args:
        input_text: Natural language description like 
                   "Create a Python CLI tool for data processing"
                   
    Returns:
        ProjectSpec with parsed information
    """
    input_lower = input_text.lower()
    
    # Detect language
    language = 'python'  # Default
    if 'javascript' in input_lower or 'node' in input_lower:
        language = 'javascript'
    elif 'typescript' in input_lower:
        language = 'typescript'
    elif 'go' in input_lower or 'golang' in input_lower:
        language = 'go'
    elif 'rust' in input_lower:
        language = 'rust'
    
    # Detect project type
    project_type = 'cli'  # Default
    if 'api' in input_lower or 'rest' in input_lower or 'server' in input_lower:
        project_type = 'api'
    elif 'web' in input_lower or 'frontend' in input_lower:
        project_type = 'web'
    elif 'library' in input_lower or 'lib' in input_lower or 'package' in input_lower:
        project_type = 'library'
    
    # Detect features
    features = ['testing']  # Always include testing
    if 'ci' in input_lower or 'github' in input_lower or 'actions' in input_lower:
        features.append('ci')
    if 'docker' in input_lower or 'container' in input_lower:
        features.append('docker')
    if 'docs' in input_lower or 'documentation' in input_lower:
        features.append('docs')
    
    # Extract name (improved heuristic)
    words = input_text.split()
    name = None
    
    # Try to find explicit name
    for i, word in enumerate(words):
        if word.lower() in ['called', 'named']:
            if i + 1 < len(words):
                name = words[i + 1].strip('.,;:"\'-')
                break
    
    if not name:
        # Look for key nouns after common project words
        skip_words = {'create', 'a', 'an', 'the', 'make', 'build', 'for', 'with', 
                      'python', 'javascript', 'typescript', 'go', 'rust', 'node',
                      'cli', 'api', 'rest', 'web', 'library', 'tool', 'server',
                      'application', 'app', 'service', 'utility'}
        
        # Find meaningful words
        meaningful_words = [w.lower() for w in words if w.lower() not in skip_words 
                          and len(w) > 2 and w.isalpha()]
        
        if meaningful_words:
            # Use up to 2 meaningful words
            name = '-'.join(meaningful_words[:2])
        else:
            # Fall back to project type based name
            name = f"my-{project_type}"
    
    # Ensure name is valid (alphanumeric and hyphens only)
    name = ''.join(c if c.isalnum() or c == '-' else '-' for c in name)
    name = '-'.join(part for part in name.split('-') if part)  # Remove empty parts
    
    if not name:
        name = 'my-project'
    
    return ProjectSpec(
        name=name,
        description=input_text,
        language=language,
        project_type=project_type,
        features=features
    )
