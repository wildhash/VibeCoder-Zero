"""State persistence management via vibe_log.md."""

from pathlib import Path
from typing import Dict
from vibecoder.core.analyzer import EnvironmentState


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
