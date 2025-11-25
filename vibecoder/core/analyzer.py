"""Codebase analysis functionality."""

from pathlib import Path
from typing import Dict
from enum import Enum


# Constants for directory scanning and analysis
IGNORE_DIRS = {
    '.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build',
    '.mypy_cache', '.pytest_cache', '.coverage', 'htmlcov', '.tox', '.eggs',
    '.cache', '.ruff_cache', 'coverage', '.hypothesis'
}

LANGUAGE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.java': 'Java',
    '.cpp': 'C++',
    '.c': 'C',
    '.go': 'Go',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.cs': 'C#',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.sh': 'Shell',
    '.html': 'HTML',
    '.css': 'CSS',
    '.sql': 'SQL',
}

FRAMEWORK_INDICATORS = {
    'package.json': ['Node.js', 'npm'],
    'requirements.txt': ['Python', 'pip'],
    'Pipfile': ['Python', 'pipenv'],
    'pyproject.toml': ['Python', 'Poetry'],
    'Cargo.toml': ['Rust', 'Cargo'],
    'go.mod': ['Go', 'Go Modules'],
    'pom.xml': ['Java', 'Maven'],
    'build.gradle': ['Java/Kotlin', 'Gradle'],
    'Gemfile': ['Ruby', 'Bundler'],
    'composer.json': ['PHP', 'Composer'],
    'Makefile': ['Make'],
    'CMakeLists.txt': ['CMake'],
    'Dockerfile': ['Docker'],
    'docker-compose.yml': ['Docker Compose'],
    '.github/workflows': ['GitHub Actions'],
}

TEST_DIRS = ['tests', 'test', '__tests__', 'spec']

CI_FILES = ['.github/workflows', '.gitlab-ci.yml', '.travis.yml', 'Jenkinsfile']

EMPTINESS_IGNORED_FILES = {'.git', '.gitignore', 'readme.md', 'readme.txt', 'readme'}


class EnvironmentState(Enum):
    """Represents the current state of the working environment."""
    EMPTY = "empty"
    POPULATED = "populated"
    INITIALIZED = "initialized"


class CodebaseAnalyzer:
    """Analyzes existing codebases to identify optimization vectors."""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.file_count = 0
        self.dir_count = 0
        self.languages = {}
        self.frameworks = []
        self.optimization_vectors = []
    
    def analyze(self) -> Dict:
        """Perform comprehensive codebase analysis."""
        self._scan_directory()
        self._detect_languages()
        self._detect_frameworks()
        self._identify_optimization_vectors()
        
        return {
            "state": EnvironmentState.POPULATED.value,
            "file_count": self.file_count,
            "dir_count": self.dir_count,
            "languages": self.languages,
            "frameworks": self.frameworks,
            "optimization_vectors": self.optimization_vectors
        }
    
    def _scan_directory(self):
        """Scan directory structure."""
        resolved_root = self.root_path.resolve()
        for item in self.root_path.rglob('*'):
            if any(ignored in item.parts for ignored in IGNORE_DIRS):
                continue
            
            # Prevent directory traversal via symlinks
            try:
                if not item.resolve().is_relative_to(resolved_root):
                    continue
            except (ValueError, OSError):
                continue
            
            if item.is_file():
                self.file_count += 1
            elif item.is_dir():
                self.dir_count += 1
    
    def _detect_languages(self):
        """Detect programming languages in use."""
        resolved_root = self.root_path.resolve()
        for file_path in self.root_path.rglob('*'):
            # Prevent directory traversal via symlinks
            try:
                if not file_path.resolve().is_relative_to(resolved_root):
                    continue
            except (ValueError, OSError):
                continue
            
            if file_path.is_file():
                ext = file_path.suffix
                if ext in LANGUAGE_EXTENSIONS:
                    lang = LANGUAGE_EXTENSIONS[ext]
                    self.languages[lang] = self.languages.get(lang, 0) + 1
    
    def _detect_frameworks(self):
        """Detect frameworks and tools in use."""
        for indicator, frameworks in FRAMEWORK_INDICATORS.items():
            path = self.root_path / indicator
            # Check file exists and has content (not empty)
            if path.exists() and (path.is_dir() or path.stat().st_size > 0):
                self.frameworks.extend(frameworks)
    
    def _identify_optimization_vectors(self):
        """Identify potential optimization opportunities."""
        vectors = []
        
        # Check for missing documentation
        if not (self.root_path / 'README.md').exists():
            vectors.append({
                "type": "documentation",
                "priority": "high",
                "description": "Missing README.md - should add project documentation"
            })
        
        # Check for missing tests
        has_tests = any((self.root_path / d).exists() for d in TEST_DIRS)
        if not has_tests and self.file_count > 5:
            vectors.append({
                "type": "testing",
                "priority": "high",
                "description": "No test directory found - should implement testing infrastructure"
            })
        
        # Check for missing CI/CD
        has_ci = any((self.root_path / f).exists() for f in CI_FILES)
        if not has_ci and self.file_count > 10:
            vectors.append({
                "type": "ci_cd",
                "priority": "medium",
                "description": "No CI/CD configuration found - should add automated pipelines"
            })
        
        # Check for dependency management
        if 'Python' in self.languages and not any([
            (self.root_path / 'requirements.txt').exists(),
            (self.root_path / 'Pipfile').exists(),
            (self.root_path / 'pyproject.toml').exists()
        ]):
            vectors.append({
                "type": "dependency_management",
                "priority": "high",
                "description": "Python project without dependency management - should add requirements.txt or pyproject.toml"
            })
        
        self.optimization_vectors = vectors
