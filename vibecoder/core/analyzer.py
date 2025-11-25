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
        """
        Initialize the analyzer for a codebase rooted at the given path.
        
        Parameters:
            root_path (Path): Filesystem path of the project root to analyze. Initializes analysis counters and collections:
                - file_count: total files encountered (starts at 0)
                - dir_count: total directories encountered (starts at 0)
                - languages: mapping of detected language names to counts (starts empty)
                - frameworks: list of detected frameworks/tools (starts empty)
                - optimization_vectors: list of identified improvement opportunities (starts empty)
        """
        self.root_path = root_path
        self.file_count = 0
        self.dir_count = 0
        self.languages = {}
        self.frameworks = []
        self.optimization_vectors = []
    
    def analyze(self) -> Dict:
        """
        Analyze the repository rooted at the analyzer's root_path and produce a summary of its contents and improvement opportunities.
        
        Returns:
            result (Dict): Summary dictionary with the following keys:
                - state (str): EnvironmentState value describing detected environment (e.g., "populated").
                - file_count (int): Total number of files encountered.
                - dir_count (int): Total number of directories encountered.
                - languages (Dict[str, int]): Mapping from detected language name to occurrence count.
                - frameworks (List[str]): List of detected frameworks or tooling indicators.
                - optimization_vectors (List[Dict]): List of identified optimization opportunities, each described with keys like `type`, `priority`, and `description`.
        """
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
        """
        Scan the analyzer's root path and count contained files and directories.
        
        Counts files and directories found under `self.root_path` while skipping paths that contain any names from `IGNORE_DIRS` and avoiding traversal into symlinked locations outside the resolved root. Updates `self.file_count` and `self.dir_count` in place.
        """
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
        """
        Identify and count programming languages present under the analyzer's root path.
        
        Updates self.languages with counts keyed by language name using file extensions defined in LANGUAGE_EXTENSIONS. Files reachable only via symlinks that resolve outside the analyzer's resolved root are ignored.
        """
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
        """
        Scan the analyzer's root_path for known framework/tool indicator files or directories and record any matched frameworks.
        
        For each entry in FRAMEWORK_INDICATORS, if the corresponding path exists under root_path and is either a directory or a file with content, the associated frameworks are appended to self.frameworks.
        """
        for indicator, frameworks in FRAMEWORK_INDICATORS.items():
            path = self.root_path / indicator
            # Check file exists and has content (not empty)
            if path.exists() and (path.is_dir() or path.stat().st_size > 0):
                self.frameworks.extend(frameworks)
    
    def _identify_optimization_vectors(self):
        """
        Populate self.optimization_vectors with detected improvement opportunities based on repository contents.
        
        Detects and adds vectors for missing project documentation, testing, CI/CD configuration, and Python dependency management. Each vector is a dict with keys "type", "priority", and "description". Detection rules:
        - Adds a documentation vector if README.md is absent.
        - Adds a testing vector if no test directories exist and file_count > 5.
        - Adds a CI/CD vector if no CI files exist and file_count > 10.
        - Adds a dependency_management vector if Python is detected and no common Python dependency files (requirements.txt, Pipfile, pyproject.toml) are present.
        """
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