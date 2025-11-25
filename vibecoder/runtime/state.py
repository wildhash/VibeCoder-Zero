"""State persistence management via vibe_log.md."""

from pathlib import Path
from typing import Dict
from vibecoder.core.analyzer import EnvironmentState


class VibeLog:
    """Manages state persistence via vibe_log.md file."""
    
    def __init__(self, root_path: Path):
        """
        Initialize the VibeLog with a root directory and set up internal paths and state placeholders.
        
        Parameters:
            root_path (Path): Base directory where `vibe_log.md` will be created and managed.
        
        Attributes:
            root_path (Path): The provided base directory.
            log_path (Path): Path to the `vibe_log.md` file (root_path / "vibe_log.md").
            current_goal (Optional[str]): Parsed current goal from the log, or None.
            completed_steps (List[str]): Collected completed steps (initially empty).
            active_blockers (List[str]): Collected active blockers (initially empty).
            last_state (Optional[dict]): Last parsed state snapshot of the log, or None.
        """
        self.root_path = root_path
        self.log_path = root_path / "vibe_log.md"
        self.current_goal = None
        self.completed_steps = []
        self.active_blockers = []
        self.last_state = None
    
    def exists(self) -> bool:
        """
        Determine whether the vibe_log.md file exists at the instance's log path.
        
        Returns:
            True if the file exists at `log_path`, False otherwise.
        """
        return self.log_path.exists()
    
    def read(self) -> Dict:
        """
        Read and parse the vibe_log.md file under the configured root path.
        
        If the file exists, sets `self.current_goal` to the first non-empty, non-heading line following the "Current Goal" marker (when present) and stores a snapshot in `self.last_state`.
        
        Returns:
            state (Dict): A mapping with:
                - content (str): Full file content.
                - has_goal (bool): `True` if "Current Goal" appears in the content, `False` otherwise.
                - has_steps (bool): `True` if "Completed Steps" appears in the content, `False` otherwise.
                - has_blockers (bool): `True` if "Active Blockers" appears in the content, `False` otherwise.
        """
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
        """
        Initialize or overwrite the vibe_log.md file at the VibeLog's log path with a structured project log.
        
        Builds a Markdown template and writes it to the log file, setting the instance's current_goal accordingly.
        
        Parameters:
            environment_state (EnvironmentState): Determines the goal and master plan template; commonly
                EnvironmentState.EMPTY (creates a foundational setup plan) or EnvironmentState.POPULATED
                (creates an analysis-oriented plan).
            analysis_data (Dict, optional): Additional environment analysis used to populate the
                "Environment Analysis" section. Expected keys include:
                - 'file_count' (int): total files count
                - 'dir_count' (int): total directories count
                - 'languages' (Mapping[str, int]): mapping of language name to file count
                - 'frameworks' (Iterable[str]): detected frameworks or tools
        
        Side effects:
            - Writes or overwrites the vibe_log.md file at self.log_path with the generated content.
            - Updates self.current_goal to the goal inserted into the file.
        """
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
        """
        Update the file's 'Last Updated' timestamp in vibe_log.md.
        
        If the log file does not exist, no action is taken. Replaces an existing "*Last Updated:" line with the current timestamp; if no such line exists, appends a separator and a new "*Last Updated: YYYY-MM-DD HH:MM:SS*" line.
        
        Parameters:
            new_goal (str): Accepted but not used.
            completed_step (str): Accepted but not used.
            blocker (str): Accepted but not used.
        """
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