"""Self-improvement planning functionality."""

from pathlib import Path
from typing import List
from .output import DirectiveOutput


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
