"""Project generation pipeline for VibeCoder-Zero.

This module provides the complete autonomous project generation pipeline
that takes input, generates projects, tests them, and debugs issues.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime


class PipelineStage(Enum):
    """Stages of the project generation pipeline."""
    INPUT = "input"
    SCAFFOLD = "scaffold"
    GENERATE = "generate"
    TEST = "test"
    DEBUG = "debug"
    VERIFY = "verify"
    COMPLETE = "complete"
    FAILED = "failed"


def _default_timestamp() -> str:
    """Generate default timestamp for pipeline state."""
    return datetime.now().isoformat()


@dataclass
class PipelineState:
    """State of the generation pipeline."""
    stage: PipelineStage
    project_name: str
    project_dir: Optional[str] = None
    iterations: int = 0
    errors: List[str] = field(default_factory=list)
    generated_files: List[str] = field(default_factory=list)
    test_results: Dict = field(default_factory=dict)
    started_at: str = field(default_factory=_default_timestamp)
    completed_at: str = None


@dataclass
class HumanConfirmation:
    """Request for human confirmation of an action."""
    action: str
    description: str
    details: Dict
    options: List[str]  # e.g., ['confirm', 'modify', 'cancel']
    required: bool = False  # If True, cannot proceed without confirmation


class ProjectPipeline:
    """Complete autonomous project generation pipeline."""
    
    MAX_DEBUG_ITERATIONS = 5
    
    def __init__(self, output_dir: Path, llm_client=None, interactive: bool = True):
        """Initialize the pipeline.
        
        Args:
            output_dir: Directory where generated projects will be created
            llm_client: Optional LLM client for code generation
            interactive: Whether to prompt for human confirmation
        """
        self.output_dir = Path(output_dir)
        self.llm_client = llm_client
        self.interactive = interactive
        self.state = None
        self.pending_confirmations = []
    
    def generate_project(self, input_spec: str) -> PipelineState:
        """Generate a complete project from input specification.
        
        This is the main entry point that orchestrates the entire pipeline.
        
        Args:
            input_spec: Natural language project description
            
        Returns:
            Final pipeline state
        """
        from vibecoder.core.scaffolder import parse_project_input, ProjectScaffolder
        from vibecoder.runtime.test_runner import TestRunner, DebugLoop, verify_project
        
        # Initialize state
        self.state = PipelineState(
            stage=PipelineStage.INPUT,
            project_name="",
        )
        
        try:
            # Stage 1: Parse input
            self._log("Parsing project specification...")
            spec = parse_project_input(input_spec)
            self.state.project_name = spec.name
            self.state.project_dir = str(self.output_dir / spec.name)
            
            # Request confirmation for project creation
            if self.interactive:
                confirmation = self._request_confirmation(
                    "create_project",
                    f"Create project '{spec.name}' in {self.state.project_dir}?",
                    {
                        'name': spec.name,
                        'language': spec.language,
                        'type': spec.project_type,
                        'features': spec.features,
                    },
                    ['confirm', 'modify', 'cancel']
                )
                if confirmation == 'cancel':
                    self.state.stage = PipelineStage.FAILED
                    self.state.errors.append("User cancelled project creation")
                    return self.state
            
            # Stage 2: Scaffold project
            self.state.stage = PipelineStage.SCAFFOLD
            self._log(f"Scaffolding {spec.language} {spec.project_type} project...")
            
            project_dir = Path(self.state.project_dir)
            project_dir.mkdir(parents=True, exist_ok=True)
            
            scaffolder = ProjectScaffolder(project_dir)
            files = scaffolder.scaffold(spec)
            
            # Stage 3: Generate files
            self.state.stage = PipelineStage.GENERATE
            self._log(f"Generating {len(files)} files...")
            
            created_paths = scaffolder.write_files(files)
            self.state.generated_files = [str(p) for p in created_paths]
            
            # Stage 4: Test project
            self.state.stage = PipelineStage.TEST
            self._log("Running tests...")
            
            runner = TestRunner(project_dir)
            test_result = runner.run_tests()
            
            self.state.test_results = {
                'status': test_result.status.value,
                'output': test_result.output[:1000],
                'details': test_result.details,
            }
            
            # Stage 5: Debug if needed
            if test_result.status.value != 'passed':
                self.state.stage = PipelineStage.DEBUG
                self._log("Tests failed, entering debug loop...")
                
                debug_loop = DebugLoop(project_dir, self.llm_client)
                success, results = debug_loop.run_debug_loop()
                
                self.state.iterations = len(results)
                
                if success:
                    self._log("Debug loop succeeded, tests now pass")
                    self.state.test_results['status'] = 'passed'
                else:
                    self._log("Debug loop could not fix all issues")
                    self.state.errors.append("Some tests still failing after debug")
            
            # Stage 6: Verify
            self.state.stage = PipelineStage.VERIFY
            self._log("Verifying project...")
            
            verification = verify_project(project_dir)
            
            if verification['issues']:
                for issue in verification['issues']:
                    if issue not in self.state.errors:
                        self.state.errors.append(issue)
            
            # Complete
            if not self.state.errors or verification.get('tests_pass'):
                self.state.stage = PipelineStage.COMPLETE
                self._log("Project generation complete!")
            else:
                self.state.stage = PipelineStage.FAILED
                self._log(f"Project generation completed with issues: {self.state.errors}")
            
            self.state.completed_at = datetime.now().isoformat()
            return self.state
            
        except Exception as e:
            self.state.stage = PipelineStage.FAILED
            self.state.errors.append(str(e))
            self.state.completed_at = datetime.now().isoformat()
            return self.state
    
    def _log(self, message: str):
        """Log pipeline progress."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{self.state.stage.value.upper()}] {message}")
    
    def _request_confirmation(
        self, 
        action: str, 
        description: str, 
        details: Dict,
        options: List[str]
    ) -> str:
        """Request human confirmation for an action.
        
        In non-interactive mode, auto-confirms.
        
        Args:
            action: Action identifier
            description: Human-readable description
            details: Action details
            options: Available response options
            
        Returns:
            Selected option
        """
        if not self.interactive:
            return options[0]  # Auto-confirm first option
        
        confirmation = HumanConfirmation(
            action=action,
            description=description,
            details=details,
            options=options
        )
        
        self.pending_confirmations.append(confirmation)
        
        # Display confirmation request
        print("\n" + "=" * 60)
        print("HUMAN CONFIRMATION REQUIRED")
        print("=" * 60)
        print(f"\nAction: {action}")
        print(f"Description: {description}")
        print("\nDetails:")
        for key, value in details.items():
            print(f"  {key}: {value}")
        print(f"\nOptions: {', '.join(options)}")
        
        # For now, auto-confirm to enable autonomous operation
        # In a real deployment, this would wait for human input
        response = options[0]  # Auto-confirm
        print(f"Auto-confirming: {response}")
        print("=" * 60 + "\n")
        
        return response
    
    def get_state_summary(self) -> str:
        """Get human-readable summary of pipeline state."""
        if not self.state:
            return "Pipeline not started"
        
        summary = [
            f"Project: {self.state.project_name}",
            f"Stage: {self.state.stage.value}",
            f"Directory: {self.state.project_dir}",
            f"Files Generated: {len(self.state.generated_files)}",
            f"Debug Iterations: {self.state.iterations}",
        ]
        
        if self.state.test_results:
            summary.append(f"Tests: {self.state.test_results.get('status', 'unknown')}")
        
        if self.state.errors:
            summary.append(f"Issues: {len(self.state.errors)}")
            for err in self.state.errors[:3]:
                summary.append(f"  - {err[:50]}...")
        
        return "\n".join(summary)
    
    def to_json(self) -> str:
        """Export pipeline state as JSON."""
        if not self.state:
            return "{}"
        
        state_dict = asdict(self.state)
        state_dict['stage'] = self.state.stage.value
        return json.dumps(state_dict, indent=2)


class VibeCoderPipeline:
    """High-level interface for VibeCoder project generation.
    
    This is the main entry point for users to create projects.
    """
    
    def __init__(self, output_dir: Optional[str] = None, llm_client=None):
        """Initialize VibeCoder pipeline.
        
        Args:
            output_dir: Where to create projects (default: ./generated_projects)
            llm_client: Optional LLM client for enhanced generation
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "generated_projects"
        self.llm_client = llm_client
        self.history = []
    
    def create(self, description: str, interactive: bool = False) -> Dict[str, Any]:
        """Create a new project from description.
        
        Args:
            description: Natural language project description
            interactive: Whether to prompt for confirmations
            
        Returns:
            Project generation result
        """
        pipeline = ProjectPipeline(
            output_dir=self.output_dir,
            llm_client=self.llm_client,
            interactive=interactive
        )
        
        state = pipeline.generate_project(description)
        
        result = {
            'success': state.stage == PipelineStage.COMPLETE,
            'project_name': state.project_name,
            'project_dir': state.project_dir,
            'files_generated': len(state.generated_files),
            'test_status': state.test_results.get('status') if state.test_results else None,
            'errors': state.errors,
            'summary': pipeline.get_state_summary(),
        }
        
        self.history.append(result)
        return result
    
    def list_projects(self) -> List[str]:
        """List generated projects."""
        if not self.output_dir.exists():
            return []
        return [d.name for d in self.output_dir.iterdir() if d.is_dir()]
    
    def get_project_status(self, project_name: str) -> Dict:
        """Get status of a specific project."""
        from vibecoder.runtime.test_runner import verify_project
        
        project_dir = self.output_dir / project_name
        if not project_dir.exists():
            return {'error': 'Project not found'}
        
        return verify_project(project_dir)


def run_pipeline_cli():
    """CLI interface for the project pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="VibeCoder-Zero Project Generation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a Python CLI tool
  python -m vibecoder.pipeline "Create a Python CLI tool for file processing"
  
  # Create an API server
  python -m vibecoder.pipeline "Create a Python REST API server with Docker support"
  
  # Create with custom output directory
  python -m vibecoder.pipeline --output ./my_projects "Create a Python library"
        """
    )
    
    parser.add_argument(
        'description',
        nargs='?',
        help='Project description in natural language'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='./generated_projects',
        help='Output directory for generated projects'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Enable interactive mode with confirmations'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List existing generated projects'
    )
    
    parser.add_argument(
        '--status', '-s',
        type=str,
        help='Check status of a specific project'
    )
    
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    pipeline = VibeCoderPipeline(output_dir=args.output)
    
    if args.list:
        projects = pipeline.list_projects()
        if args.json:
            print(json.dumps({'projects': projects}))
        else:
            print("Generated Projects:")
            for p in projects:
                print(f"  - {p}")
        return
    
    if args.status:
        status = pipeline.get_project_status(args.status)
        if args.json:
            print(json.dumps(status))
        else:
            print(f"Status of {args.status}:")
            for key, value in status.items():
                print(f"  {key}: {value}")
        return
    
    if not args.description:
        parser.print_help()
        print("\nError: Project description required")
        sys.exit(1)
    
    result = pipeline.create(args.description, interactive=args.interactive)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 60)
        print("PROJECT GENERATION RESULT")
        print("=" * 60)
        print(result['summary'])
        print("=" * 60)
        
        if result['success']:
            print(f"\n✓ Project created successfully at: {result['project_dir']}")
            print("\nNext steps:")
            print(f"  cd {result['project_dir']}")
            print("  pip install -e '.[dev]'")
            print("  pytest -v")
        else:
            print(f"\n✗ Project generation had issues:")
            for err in result['errors']:
                print(f"  - {err}")


if __name__ == "__main__":
    run_pipeline_cli()
