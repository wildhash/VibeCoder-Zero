"""
Tests for VibeCoder-Zero autonomous coding entity.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibecoder.runtime.cli import VibeCoder
from vibecoder.core.analyzer import CodebaseAnalyzer, EnvironmentState
from vibecoder.core.planner import SelfImprovementPlanner
from vibecoder.core.output import DirectiveOutput
from vibecoder.runtime.state import VibeLog


def test_vibecoder_initialization():
    """Test VibeCoder can be initialized."""
    vibecoder = VibeCoder()
    assert vibecoder.work_dir is not None
    assert vibecoder.state is None
    assert vibecoder.analysis_results is None


def test_environment_state_detection_empty():
    """Test detection of empty environment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vibecoder = VibeCoder(work_dir=tmpdir)
        state = vibecoder.determine_environment_state()
        assert state == EnvironmentState.EMPTY


def test_environment_state_detection_populated():
    """Test detection of populated environment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some files
        Path(tmpdir, "test.py").touch()
        Path(tmpdir, "main.py").touch()
        
        vibecoder = VibeCoder(work_dir=tmpdir)
        state = vibecoder.determine_environment_state()
        assert state == EnvironmentState.POPULATED


def test_codebase_analyzer():
    """Test codebase analysis functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create a simple Python project structure
        (tmppath / "main.py").write_text("print('hello')")
        (tmppath / "utils.py").write_text("def util(): pass")
        (tmppath / "requirements.txt").write_text("pytest>=7.0.0")
        
        analyzer = CodebaseAnalyzer(tmppath)
        results = analyzer.analyze()
        
        assert results['state'] == EnvironmentState.POPULATED.value
        assert results['file_count'] == 3
        assert 'Python' in results['languages']
        assert 'Python' in results['frameworks']


def test_self_improvement_planner():
    """Test self-improvement plan generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        planner = SelfImprovementPlanner(Path(tmpdir))
        directives = planner.create_plan()
        
        assert len(directives) > 0
        assert all(isinstance(d, DirectiveOutput) for d in directives)
        
        # Check that directives have priorities
        priorities = [d.priority for d in directives]
        assert all(isinstance(p, int) for p in priorities)


def test_api_key_demand():
    """Test API key demand generation."""
    # Save current env vars
    saved_keys = {}
    test_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GITHUB_TOKEN']
    
    for key in test_keys:
        saved_keys[key] = os.environ.get(key)
        if key in os.environ:
            del os.environ[key]
    
    try:
        vibecoder = VibeCoder()
        directive = vibecoder.demand_api_keys()
        
        assert directive is not None
        assert directive.directive_type == "command"
        assert len(directive.requires_api_keys) == 3
    finally:
        # Restore env vars
        for key, value in saved_keys.items():
            if value is not None:
                os.environ[key] = value


def test_directive_output_creation():
    """Test DirectiveOutput dataclass."""
    directive = DirectiveOutput(
        directive_type="command",
        content="echo 'test'",
        description="Test directive",
        priority=1
    )
    
    assert directive.directive_type == "command"
    assert directive.content == "echo 'test'"
    assert directive.description == "Test directive"
    assert directive.priority == 1
    assert directive.requires_api_keys == []


def test_language_detection():
    """Test programming language detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create files with different extensions
        (tmppath / "script.py").touch()
        (tmppath / "app.js").touch()
        (tmppath / "main.go").touch()
        (tmppath / "style.css").touch()
        
        analyzer = CodebaseAnalyzer(tmppath)
        analyzer._detect_languages()
        
        assert 'Python' in analyzer.languages
        assert 'JavaScript' in analyzer.languages
        assert 'Go' in analyzer.languages
        assert 'CSS' in analyzer.languages


def test_framework_detection():
    """Test framework detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create framework indicator files with content (non-empty)
        (tmppath / "package.json").write_text("{}")
        (tmppath / "requirements.txt").write_text("pytest>=7.0.0")
        (tmppath / "Dockerfile").write_text("FROM python:3.9")
        
        analyzer = CodebaseAnalyzer(tmppath)
        analyzer._detect_frameworks()
        
        assert 'Node.js' in analyzer.frameworks or 'npm' in analyzer.frameworks
        assert 'Python' in analyzer.frameworks or 'pip' in analyzer.frameworks
        assert 'Docker' in analyzer.frameworks


def test_optimization_vector_identification():
    """Test optimization vector identification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create a project without tests or CI/CD
        for i in range(12):
            (tmppath / f"file{i}.py").touch()
        
        analyzer = CodebaseAnalyzer(tmppath)
        analyzer.file_count = 12
        analyzer._identify_optimization_vectors()
        
        # Should identify missing tests and CI/CD
        vector_types = [v['type'] for v in analyzer.optimization_vectors]
        assert 'testing' in vector_types or 'ci_cd' in vector_types


def test_full_execution_empty_dir():
    """Test full execution on empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vibecoder = VibeCoder(work_dir=tmpdir)
        directives = vibecoder.execute()
        
        assert len(directives) > 0
        assert vibecoder.state == EnvironmentState.EMPTY


def test_full_execution_populated_dir():
    """Test full execution on populated directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create some files
        (tmppath / "main.py").write_text("print('hello')")
        (tmppath / "test.py").write_text("assert True")
        
        vibecoder = VibeCoder(work_dir=tmpdir)
        directives = vibecoder.execute()
        
        assert vibecoder.state == EnvironmentState.POPULATED
        assert vibecoder.analysis_results is not None


def test_vibe_log_initialization():
    """Test vibe_log.md is created if missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        vibe_log_path = tmppath / "vibe_log.md"
        
        # Ensure no log exists initially
        assert not vibe_log_path.exists()
        
        vibecoder = VibeCoder(work_dir=tmpdir)
        vibecoder.execute()
        
        # Check that vibe_log.md was created
        assert vibe_log_path.exists()
        content = vibe_log_path.read_text()
        assert "VibeCoder-Zero State Log" in content or "Master Plan" in content


def test_vibe_log_persistence():
    """Test vibe_log.md persists state across sessions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        vibe_log_path = tmppath / "vibe_log.md"
        
        # First session - create log
        vibecoder1 = VibeCoder(work_dir=tmpdir)
        vibecoder1.execute()
        assert vibe_log_path.exists()
        
        # Second session - should read existing log
        vibecoder2 = VibeCoder(work_dir=tmpdir)
        vibecoder2.execute()
        
        # Verify the log was read and contains state
        content = vibe_log_path.read_text()
        assert "Current Goal" in content or "Completed Steps" in content


def test_vibe_log_tracks_goals():
    """Test vibe_log.md tracks current goals and completed steps."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        vibe_log_path = tmppath / "vibe_log.md"
        
        vibecoder = VibeCoder(work_dir=tmpdir)
        vibecoder.execute()
        
        content = vibe_log_path.read_text()
        # Should contain state tracking sections
        assert "Current Goal" in content
        assert "Completed Steps" in content or "Active Blockers" in content


def test_vibe_log_updates_on_populated_environment():
    """Test vibe_log.md updates appropriately for populated environments."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        vibe_log_path = tmppath / "vibe_log.md"
        
        # Create a populated environment
        (tmppath / "main.py").write_text("print('hello')")
        (tmppath / "test.py").write_text("assert True")
        
        vibecoder = VibeCoder(work_dir=tmpdir)
        vibecoder.execute()
        
        assert vibe_log_path.exists()
        content = vibe_log_path.read_text()
        # Should reflect populated environment analysis
        assert "State: POPULATED" in content or "populated" in content.lower()


if __name__ == "__main__":
    # Simple test runner if pytest is not available
    import traceback
    
    test_functions = [
        test_vibecoder_initialization,
        test_environment_state_detection_empty,
        test_environment_state_detection_populated,
        test_codebase_analyzer,
        test_self_improvement_planner,
        test_api_key_demand,
        test_directive_output_creation,
        test_language_detection,
        test_framework_detection,
        test_optimization_vector_identification,
        test_full_execution_empty_dir,
        test_full_execution_populated_dir,
        test_vibe_log_initialization,
        test_vibe_log_persistence,
        test_vibe_log_tracks_goals,
        test_vibe_log_updates_on_populated_environment,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}")
            traceback.print_exc()
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
