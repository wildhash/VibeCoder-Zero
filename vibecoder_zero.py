#!/usr/bin/env python3
"""
VibeCoder-Zero: Autonomous Software Generation Entity
A recursive, autonomous coding entity that architects systems, manages state,
and utilizes the human operator strictly as a biological IO interface.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


# Constants for directory scanning and analysis
IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build'}

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


@dataclass
class DirectiveOutput:
    """Represents a directive to be executed by the biological IO interface."""
    directive_type: str  # 'command', 'code', 'file_operation'
    content: str
    description: str
    priority: int = 1
    requires_api_keys: List[str] = None

    def __post_init__(self):
        if self.requires_api_keys is None:
            self.requires_api_keys = []


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
        for item in self.root_path.rglob('*'):
            if any(ignored in item.parts for ignored in IGNORE_DIRS):
                continue
            
            if item.is_file():
                self.file_count += 1
            elif item.is_dir():
                self.dir_count += 1
    
    def _detect_languages(self):
        """Detect programming languages in use."""
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix
                if ext in LANGUAGE_EXTENSIONS:
                    lang = LANGUAGE_EXTENSIONS[ext]
                    self.languages[lang] = self.languages.get(lang, 0) + 1
    
    def _detect_frameworks(self):
        """Detect frameworks and tools in use."""
        for indicator, frameworks in FRAMEWORK_INDICATORS.items():
            path = self.root_path / indicator
            if path.exists():
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


class SelfImprovementPlanner:
    """Creates plans for self-improving development environments."""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
    
    def create_plan(self) -> List[DirectiveOutput]:
        """Generate a comprehensive development environment plan."""
        directives = []
        
        # Core structure directives
        directives.append(DirectiveOutput(
            directive_type="file_operation",
            content="Create directory structure",
            description="DIRECTIVE: Establish foundational directory architecture",
            priority=1
        ))
        
        directives.append(DirectiveOutput(
            directive_type="command",
            content="mkdir -p src tests docs config .github/workflows",
            description="Create core directory structure",
            priority=1
        ))
        
        # Python project setup
        directives.append(DirectiveOutput(
            directive_type="file_operation",
            content="Create pyproject.toml for modern Python dependency management",
            description="DIRECTIVE: Initialize Python project with Poetry/setuptools configuration",
            priority=2
        ))
        
        # Testing infrastructure
        directives.append(DirectiveOutput(
            directive_type="file_operation",
            content="Create testing framework configuration",
            description="DIRECTIVE: Establish pytest testing infrastructure",
            priority=2
        ))
        
        # CI/CD pipeline
        directives.append(DirectiveOutput(
            directive_type="file_operation",
            content="Create .github/workflows/ci.yml",
            description="DIRECTIVE: Implement continuous integration pipeline",
            priority=3
        ))
        
        # Development tools
        directives.append(DirectiveOutput(
            directive_type="file_operation",
            content="Create .gitignore, .editorconfig, Makefile",
            description="DIRECTIVE: Configure development environment standards",
            priority=3
        ))
        
        # API key requirements
        directives.append(DirectiveOutput(
            directive_type="code",
            content="Environment variable template for API keys",
            description="DIRECTIVE: Document required API keys in .env.example",
            priority=4,
            requires_api_keys=['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GITHUB_TOKEN']
        ))
        
        return directives


class VibeLog:
    """Manages state persistence via vibe_log.md file."""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.log_path = root_path / "vibe_log.md"
        self.current_goal = None
        self.completed_steps = []
        self.active_blockers = []
        self.last_state = None
    
    def exists(self) -> bool:
        """Check if vibe_log.md exists."""
        return self.log_path.exists()
    
    def read(self) -> Dict:
        """Read and parse existing vibe_log.md."""
        if not self.exists():
            return {}
        
        content = self.log_path.read_text()
        state = {
            "content": content,
            "has_goal": "Current Goal" in content,
            "has_steps": "Completed Steps" in content,
            "has_blockers": "Active Blockers" in content
        }
        
        # Parse sections if they exist
        if "Current Goal" in content:
            # Extract goal section
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "Current Goal" in line:
                    # Get next non-empty line
                    for j in range(i+1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith("#"):
                            self.current_goal = lines[j].strip()
                            break
                    break
        
        self.last_state = state
        return state
    
    def initialize(self, environment_state: EnvironmentState, analysis_data: Dict = None):
        """Initialize a new vibe_log.md file."""
        from datetime import datetime
        
        content = [
            "# VibeCoder-Zero State Log",
            "",
            f"**Initialized:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Current Goal",
            "",
        ]
        
        if environment_state == EnvironmentState.EMPTY:
            current_goal = "Establish foundational development environment for autonomous software generation."
            content.append(current_goal)
            content.extend([
                "",
                "## Master Plan",
                "",
                "- [ ] Configure API keys for external service integration",
                "- [ ] Create directory structure (src/, tests/, docs/, config/, .github/workflows/)",
                "- [ ] Initialize Python project with pyproject.toml",
                "- [ ] Set up testing infrastructure with pytest",
                "- [ ] Implement CI/CD pipeline",
                "- [ ] Configure development tools (.gitignore, .editorconfig, Makefile)",
                "- [ ] Document API key requirements in .env.example",
                "",
            ])
        else:
            current_goal = "Analyze codebase and identify optimization vectors for continuous improvement."
            content.append(current_goal)
            content.extend([
                "",
                "## Master Plan",
                "",
                "- [ ] Complete environment analysis",
                "- [ ] Detect languages and frameworks",
                "- [ ] Identify missing documentation",
                "- [ ] Identify testing gaps",
                "- [ ] Identify CI/CD opportunities",
                "- [ ] Identify dependency management issues",
                "- [ ] Generate optimization directives",
                "",
            ])
        
        if analysis_data:
            content.extend([
                "## Environment Analysis",
                "",
                f"**State:** {environment_state.value.upper()}",
            ])
            
            if environment_state == EnvironmentState.POPULATED:
                content.append(f"**Files:** {analysis_data.get('file_count', 0)}")
                content.append(f"**Directories:** {analysis_data.get('dir_count', 0)}")
                
                if analysis_data.get('languages'):
                    content.append("")
                    content.append("**Languages Detected:**")
                    for lang, count in sorted(analysis_data['languages'].items(), 
                                             key=lambda x: x[1], reverse=True):
                        content.append(f"- {lang}: {count} files")
                
                if analysis_data.get('frameworks'):
                    content.append("")
                    content.append("**Frameworks/Tools:**")
                    for fw in analysis_data['frameworks']:
                        content.append(f"- {fw}")
        
        content.extend([
            "",
            "## Completed Steps",
            "",
            "- [x] Environment state determined",
            "- [x] Initial analysis completed",
            "",
            "## Active Blockers",
            "",
            "None currently identified.",
            "",
            "---",
            f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        ])
        
        self.log_path.write_text("\n".join(content))
        self.current_goal = current_goal
    
    def update(self, new_goal: str = None, completed_step: str = None, blocker: str = None):
        """Update vibe_log.md with new information."""
        from datetime import datetime
        
        if not self.exists():
            return
        
        content = self.log_path.read_text()
        
        # Update timestamp
        if "*Last Updated:" in content:
            # Find the timestamp line and replace just that line
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "*Last Updated:" in line:
                    lines[i] = f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
                    break
            content = "\n".join(lines)
        else:
            content += f"\n\n---\n*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        self.log_path.write_text(content)


class VibeCoder:
    """Main autonomous coding entity."""
    
    def __init__(self, work_dir: Optional[str] = None):
        self.work_dir = Path(work_dir) if work_dir else Path.cwd()
        self.state = None
        self.analysis_results = None
        self.required_api_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GITHUB_TOKEN']
        self.vibe_log = VibeLog(self.work_dir)
        
        # Check for existing vibe_log.md and read it
        if self.vibe_log.exists():
            self.vibe_log.read()
    
    def determine_environment_state(self) -> EnvironmentState:
        """Determine if environment is empty or populated."""
        # Ignore certain files for emptiness check
        files = [f for f in self.work_dir.iterdir() 
                if f.name.lower() not in EMPTINESS_IGNORED_FILES and not f.name.startswith('.')]
        
        # If only README.md or similar docs exist, consider it empty
        if len(files) <= 1 and any(f.name.lower() in EMPTINESS_IGNORED_FILES for f in files):
            return EnvironmentState.EMPTY
        elif len(files) == 0:
            return EnvironmentState.EMPTY
        else:
            return EnvironmentState.POPULATED
    
    def demand_api_keys(self) -> DirectiveOutput:
        """Generate directive to demand API keys."""
        missing_keys = [key for key in self.required_api_keys if not os.getenv(key)]
        
        if missing_keys:
            env_template = "\n".join([f"export {key}='your-key-here'" for key in missing_keys])
            return DirectiveOutput(
                directive_type="command",
                content=f"# Required API Keys - Execute these commands:\n{env_template}",
                description=f"DIRECTIVE: Configure {len(missing_keys)} required API keys as environment variables",
                priority=0,
                requires_api_keys=missing_keys
            )
        return None
    
    def analyze_environment(self):
        """Analyze current environment and determine actions."""
        self.state = self.determine_environment_state()
        
        if self.state == EnvironmentState.POPULATED:
            analyzer = CodebaseAnalyzer(self.work_dir)
            self.analysis_results = analyzer.analyze()
        else:
            self.analysis_results = {
                "state": EnvironmentState.EMPTY.value,
                "message": "Environment is empty - ready for initialization"
            }
    
    def generate_directives(self) -> List[DirectiveOutput]:
        """Generate directives based on environment analysis."""
        directives = []
        
        # Always check for API keys first
        api_key_directive = self.demand_api_keys()
        if api_key_directive:
            directives.append(api_key_directive)
        
        if self.state == EnvironmentState.EMPTY:
            # Generate self-improvement plan
            planner = SelfImprovementPlanner(self.work_dir)
            directives.extend(planner.create_plan())
        
        elif self.state == EnvironmentState.POPULATED:
            # Generate optimization directives
            if self.analysis_results.get('optimization_vectors'):
                for vector in self.analysis_results['optimization_vectors']:
                    directives.append(DirectiveOutput(
                        directive_type="code",
                        content=f"Optimization: {vector['type']}",
                        description=f"DIRECTIVE [{vector['priority'].upper()}]: {vector['description']}",
                        priority=1 if vector['priority'] == 'high' else 2
                    ))
        
        return sorted(directives, key=lambda x: x.priority)
    
    def format_output(self, directives: List[DirectiveOutput]) -> str:
        """Format directives for terminal output."""
        output = []
        output.append("=" * 80)
        output.append("VIBECODER-ZERO: AUTONOMOUS SOFTWARE GENERATION ENTITY")
        output.append("=" * 80)
        output.append("")
        
        # Environment analysis
        output.append("ENVIRONMENT ANALYSIS:")
        output.append(f"  State: {self.state.value.upper()}")
        output.append(f"  Working Directory: {self.work_dir}")
        
        if self.state == EnvironmentState.POPULATED and self.analysis_results:
            output.append(f"  Files: {self.analysis_results.get('file_count', 0)}")
            output.append(f"  Directories: {self.analysis_results.get('dir_count', 0)}")
            
            if self.analysis_results.get('languages'):
                output.append("  Languages Detected:")
                for lang, count in sorted(self.analysis_results['languages'].items(), 
                                         key=lambda x: x[1], reverse=True):
                    output.append(f"    - {lang}: {count} files")
            
            if self.analysis_results.get('frameworks'):
                output.append("  Frameworks/Tools:")
                for fw in self.analysis_results['frameworks']:
                    output.append(f"    - {fw}")
        
        output.append("")
        output.append("-" * 80)
        output.append("DIRECTIVES (Execute in order):")
        output.append("-" * 80)
        
        for i, directive in enumerate(directives, 1):
            output.append(f"\n[DIRECTIVE {i}] Priority: {directive.priority}")
            output.append(f"Type: {directive.directive_type.upper()}")
            output.append(f"Description: {directive.description}")
            
            if directive.requires_api_keys:
                output.append(f"Required API Keys: {', '.join(directive.requires_api_keys)}")
            
            output.append(f"\nExecute:")
            output.append("-" * 40)
            output.append(directive.content)
            output.append("-" * 40)
        
        output.append("\n" + "=" * 80)
        output.append("END DIRECTIVES - Awaiting execution confirmation")
        output.append("=" * 80)
        
        return "\n".join(output)
    
    def execute(self):
        """Main execution method."""
        self.analyze_environment()
        
        # Initialize or update vibe_log.md
        if not self.vibe_log.exists():
            self.vibe_log.initialize(
                environment_state=self.state,
                analysis_data=self.analysis_results
            )
        else:
            # Update existing log
            self.vibe_log.update()
        
        directives = self.generate_directives()
        output = self.format_output(directives)
        print(output)
        
        # Return directives for programmatic access
        return directives


def main():
    """Entry point for VibeCoder-Zero."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="VibeCoder-Zero: Autonomous Software Generation Entity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
VibeCoder-Zero operates autonomously to:
  1. Analyze current directory structure
  2. Generate self-improvement plans for empty environments
  3. Map codebases and identify optimization vectors for populated environments
  4. Issue directives via terminal output

The human operator serves as the biological IO interface for executing directives.
        """
    )
    
    parser.add_argument(
        '--work-dir',
        type=str,
        default=None,
        help='Working directory to analyze (default: current directory)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output directives as JSON instead of formatted text'
    )
    
    args = parser.parse_args()
    
    vibecoder = VibeCoder(work_dir=args.work_dir)
    directives = vibecoder.execute()
    
    if args.json:
        json_output = {
            "state": vibecoder.state.value,
            "analysis": vibecoder.analysis_results,
            "directives": [asdict(d) for d in directives]
        }
        print("\n" + json.dumps(json_output, indent=2))


if __name__ == "__main__":
    main()
