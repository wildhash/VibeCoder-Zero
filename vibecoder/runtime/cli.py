"""Main CLI and VibeCoder class."""

import os
import sys
import json
from pathlib import Path
from typing import List, Optional
from dataclasses import asdict

from vibecoder.core.output import DirectiveOutput
from vibecoder.core.analyzer import (
    EnvironmentState,
    CodebaseAnalyzer,
    EMPTINESS_IGNORED_FILES
)
from vibecoder.core.planner import SelfImprovementPlanner
from vibecoder.runtime.state import VibeLog
from vibecoder.runtime.executor import execute_command
from vibecoder.vibe.context_manager import load_context, save_context
from vibecoder.llm.client import LLMClient


class VibeCoder:
    """Main autonomous coding entity."""
    
    def __init__(self, work_dir: Optional[str] = None, llm_client: Optional[LLMClient] = None, auto_execute: bool = False):
        self.work_dir = Path(work_dir) if work_dir else Path.cwd()
        self.state = None
        self.analysis_results = None
        self.required_api_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GITHUB_TOKEN']
        self.vibe_log = VibeLog(self.work_dir)
        self.llm_client = llm_client
        self.auto_execute = auto_execute
        
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
            
            # Auto-execute if enabled
            if self.auto_execute and directive.directive_type == "command":
                result = execute_command(directive.content, auto=True)
                if result.stdout:
                    output.append(f"Output: {result.stdout}")
                if result.stderr:
                    output.append(f"Error: {result.stderr}")
        
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
    
    parser.add_argument(
        '--auto-execute',
        action='store_true',
        help='Enable auto execution of safe commands'
    )
    
    parser.add_argument(
        '--self-reflect',
        action='store_true',
        help='Trigger self-reflection mode'
    )
    
    args = parser.parse_args()
    
    # Initialize LLM client if API keys are available
    llm_client = None
    if os.getenv('OPENAI_API_KEY'):
        try:
            llm_client = LLMClient(
                provider="openai",
                plan_model="gpt-4",
                code_model="gpt-4",
                reflect_model="gpt-4"
            )
        except Exception as e:
            print(f"Warning: Could not initialize OpenAI client: {e}", file=sys.stderr)
    elif os.getenv('ANTHROPIC_API_KEY'):
        try:
            llm_client = LLMClient(
                provider="anthropic",
                plan_model="claude-3-5-sonnet-20241022",
                code_model="claude-3-5-sonnet-20241022",
                reflect_model="claude-3-5-sonnet-20241022"
            )
        except Exception as e:
            print(f"Warning: Could not initialize Anthropic client: {e}", file=sys.stderr)
    
    # Handle self-reflection mode
    if args.self_reflect:
        if llm_client is None:
            print("Error: Self-reflection requires OPENAI_API_KEY or ANTHROPIC_API_KEY", file=sys.stderr)
            sys.exit(1)
        
        from vibecoder.self_reflector.reflector import run_self_reflection
        work_dir = Path(args.work_dir) if args.work_dir else Path.cwd()
        output_path = run_self_reflection(work_dir, llm_client)
        print(f"Self-reflection output written to: {output_path}")
        return
    
    vibecoder = VibeCoder(work_dir=args.work_dir, llm_client=llm_client, auto_execute=args.auto_execute)
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
