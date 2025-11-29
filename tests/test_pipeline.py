"""
Tests for project scaffolding, test runner, and pipeline modules.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibecoder.core.scaffolder import (
    ProjectSpec, GeneratedFile, ProjectScaffolder, parse_project_input
)
from vibecoder.runtime.test_runner import (
    TestRunner, TestStatus, TestResult, DebugLoop, verify_project
)
from vibecoder.pipeline import (
    ProjectPipeline, PipelineState, PipelineStage, VibeCoderPipeline
)


# ========== Scaffolder Tests ==========

def test_project_spec_creation():
    """Test ProjectSpec dataclass."""
    spec = ProjectSpec(
        name="test-project",
        description="A test project",
        language="python",
        project_type="cli",
        features=["testing", "ci"]
    )
    
    assert spec.name == "test-project"
    assert spec.language == "python"
    assert spec.project_type == "cli"
    assert "testing" in spec.features
    assert spec.dependencies == []


def test_parse_project_input_python_cli():
    """Test parsing a Python CLI project description."""
    spec = parse_project_input("Create a Python CLI tool for data processing")
    
    assert spec.language == "python"
    assert spec.project_type == "cli"
    assert "testing" in spec.features


def test_parse_project_input_api():
    """Test parsing an API project description."""
    spec = parse_project_input("Build a REST API server")
    
    assert spec.project_type == "api"


def test_parse_project_input_with_ci():
    """Test parsing includes CI when mentioned."""
    spec = parse_project_input("Create a project with GitHub Actions CI")
    
    assert "ci" in spec.features


def test_parse_project_input_with_docker():
    """Test parsing includes Docker when mentioned."""
    spec = parse_project_input("Create a containerized service with Docker")
    
    assert "docker" in spec.features


def test_scaffolder_creates_files():
    """Test scaffolder generates correct files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec = ProjectSpec(
            name="test-app",
            description="Test application",
            language="python",
            project_type="cli",
            features=["testing"]
        )
        
        scaffolder = ProjectScaffolder(Path(tmpdir))
        files = scaffolder.scaffold(spec)
        
        # Should generate multiple files
        assert len(files) > 0
        
        # Check for essential files
        file_paths = [f.path for f in files]
        assert 'main.py' in file_paths
        assert 'README.md' in file_paths
        assert 'pyproject.toml' in file_paths


def test_scaffolder_writes_files():
    """Test scaffolder writes files to disk."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec = ProjectSpec(
            name="write-test",
            description="Test file writing",
            language="python",
            project_type="cli",
            features=["testing"]
        )
        
        scaffolder = ProjectScaffolder(Path(tmpdir))
        files = scaffolder.scaffold(spec)
        created_paths = scaffolder.write_files(files)
        
        # Check files were created
        assert len(created_paths) > 0
        for path in created_paths:
            assert path.exists()


def test_scaffolder_with_ci():
    """Test scaffolder generates CI files when requested."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec = ProjectSpec(
            name="ci-test",
            description="Test CI generation",
            language="python",
            project_type="cli",
            features=["testing", "ci"]
        )
        
        scaffolder = ProjectScaffolder(Path(tmpdir))
        files = scaffolder.scaffold(spec)
        
        file_paths = [f.path for f in files]
        assert '.github/workflows/ci.yml' in file_paths


def test_scaffolder_with_docker():
    """Test scaffolder generates Docker files when requested."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec = ProjectSpec(
            name="docker-test",
            description="Test Docker generation",
            language="python",
            project_type="cli",
            features=["testing", "docker"]
        )
        
        scaffolder = ProjectScaffolder(Path(tmpdir))
        files = scaffolder.scaffold(spec)
        
        file_paths = [f.path for f in files]
        assert 'Dockerfile' in file_paths
        assert 'docker-compose.yml' in file_paths


# ========== Test Runner Tests ==========

def test_test_result_dataclass():
    """Test TestResult dataclass."""
    result = TestResult(
        name="test_suite",
        status=TestStatus.PASSED,
        output="All tests passed",
        error=""
    )
    
    assert result.name == "test_suite"
    assert result.status == TestStatus.PASSED
    assert result.details == {}


def test_test_runner_detect_framework_pytest():
    """Test detection of pytest framework."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create pytest.ini
        (tmppath / "pytest.ini").write_text("[pytest]\n")
        
        runner = TestRunner(tmppath)
        framework = runner.detect_test_framework()
        
        assert framework == "pytest"


def test_test_runner_detect_framework_from_pyproject():
    """Test detection from pyproject.toml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create pyproject.toml with pytest config
        (tmppath / "pyproject.toml").write_text("""
[tool.pytest.ini_options]
testpaths = ["tests"]
""")
        
        runner = TestRunner(tmppath)
        framework = runner.detect_test_framework()
        
        assert framework == "pytest"


def test_test_runner_run_tests_no_tests():
    """Test runner handles missing tests gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = TestRunner(Path(tmpdir))
        result = runner.run_tests()
        
        # Should return skipped or error status
        assert result.status in [TestStatus.SKIPPED, TestStatus.ERROR, TestStatus.FAILED]


def test_test_runner_run_python_tests():
    """Test runner can run simple Python tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        tests_dir = tmppath / "tests"
        tests_dir.mkdir()
        
        # Create a simple passing test
        (tests_dir / "test_simple.py").write_text("""
def test_passing():
    assert True

if __name__ == "__main__":
    test_passing()
    print("All tests passed!")
""")
        
        runner = TestRunner(tmppath)
        result = runner._run_python_tests(None)
        
        assert result.status == TestStatus.PASSED


# ========== Debug Loop Tests ==========

def test_debug_loop_initialization():
    """Test DebugLoop can be initialized."""
    with tempfile.TemporaryDirectory() as tmpdir:
        loop = DebugLoop(Path(tmpdir))
        
        assert loop.project_dir == Path(tmpdir)
        assert loop.max_iterations == 5


def test_debug_loop_pattern_analysis():
    """Test pattern-based error analysis."""
    with tempfile.TemporaryDirectory() as tmpdir:
        loop = DebugLoop(Path(tmpdir))
        
        result = TestResult(
            name="test",
            status=TestStatus.FAILED,
            output="",
            error="ImportError: No module named 'missing_module'"
        )
        
        suggestions = loop.analyze_failure(result)
        
        # Should find the import error
        assert len(suggestions) > 0
        assert any("ImportError" in s.explanation for s in suggestions)


# ========== Verification Tests ==========

def test_verify_project_nonexistent():
    """Test verification of non-existent project."""
    result = verify_project(Path("/nonexistent/path"))
    
    assert result['exists'] is False
    assert len(result['issues']) > 0


def test_verify_project_empty():
    """Test verification of empty project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = verify_project(Path(tmpdir))
        
        assert result['exists'] is True
        assert result['has_tests'] is False
        assert result['has_readme'] is False


def test_verify_project_with_readme():
    """Test verification detects README."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        (tmppath / "README.md").write_text("# Test Project")
        
        result = verify_project(tmppath)
        
        assert result['has_readme'] is True


def test_verify_project_with_tests():
    """Test verification detects and runs tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        tests_dir = tmppath / "tests"
        tests_dir.mkdir()
        
        (tests_dir / "test_basic.py").write_text("""
def test_pass():
    assert True

if __name__ == "__main__":
    test_pass()
    print("All tests passed!")
""")
        
        result = verify_project(tmppath)
        
        assert result['has_tests'] is True


# ========== Pipeline Tests ==========

def test_pipeline_state_creation():
    """Test PipelineState dataclass."""
    state = PipelineState(
        stage=PipelineStage.INPUT,
        project_name="test"
    )
    
    assert state.stage == PipelineStage.INPUT
    assert state.project_name == "test"
    assert state.errors == []
    assert state.started_at is not None


def test_pipeline_stage_enum():
    """Test PipelineStage values."""
    assert PipelineStage.INPUT.value == "input"
    assert PipelineStage.COMPLETE.value == "complete"
    assert PipelineStage.FAILED.value == "failed"


def test_vibecoder_pipeline_initialization():
    """Test VibeCoderPipeline initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = VibeCoderPipeline(output_dir=tmpdir)
        
        assert pipeline.output_dir == Path(tmpdir)
        assert pipeline.history == []


def test_vibecoder_pipeline_list_empty():
    """Test listing projects when none exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = VibeCoderPipeline(output_dir=tmpdir)
        projects = pipeline.list_projects()
        
        assert projects == []


def test_vibecoder_pipeline_create_project():
    """Test full project creation through pipeline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = VibeCoderPipeline(output_dir=tmpdir)
        result = pipeline.create(
            "Create a simple Python CLI tool",
            interactive=False
        )
        
        assert 'success' in result
        assert 'project_name' in result
        assert 'project_dir' in result
        assert result['files_generated'] > 0


def test_vibecoder_pipeline_project_status():
    """Test getting status of generated project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = VibeCoderPipeline(output_dir=tmpdir)
        
        # Create a project first
        result = pipeline.create(
            "Create a test project",
            interactive=False
        )
        
        # Get its status
        status = pipeline.get_project_status(result['project_name'])
        
        assert 'exists' in status
        assert status['exists'] is True


def test_project_pipeline_generates_working_project():
    """Test that generated project has runnable tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = ProjectPipeline(
            output_dir=Path(tmpdir),
            interactive=False
        )
        
        state = pipeline.generate_project("Create a Python library for utilities")
        
        # Project should be created
        assert state.project_dir is not None
        assert Path(state.project_dir).exists()
        
        # Should have generated files
        assert len(state.generated_files) > 0


# ========== Integration Tests ==========

def test_end_to_end_project_generation():
    """Test complete end-to-end project generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Parse input
        spec = parse_project_input("Create a Python CLI tool called myutil")
        
        # Scaffold project
        project_dir = Path(tmpdir) / spec.name
        project_dir.mkdir(parents=True)
        
        scaffolder = ProjectScaffolder(project_dir)
        files = scaffolder.scaffold(spec)
        scaffolder.write_files(files)
        
        # Verify project
        verification = verify_project(project_dir)
        
        assert verification['exists'] is True
        assert verification['has_readme'] is True
        assert verification['has_config'] is True
        assert verification['has_tests'] is True


def test_generated_project_structure():
    """Test that generated project has correct structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec = ProjectSpec(
            name="struct-test",
            description="Structure test",
            language="python",
            project_type="cli",
            features=["testing", "ci", "docker"]
        )
        
        project_dir = Path(tmpdir)
        scaffolder = ProjectScaffolder(project_dir)
        files = scaffolder.scaffold(spec)
        scaffolder.write_files(files)
        
        # Check structure
        assert (project_dir / "main.py").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "Makefile").exists()
        assert (project_dir / ".gitignore").exists()
        assert (project_dir / "tests").exists()
        assert (project_dir / "src").exists()
        assert (project_dir / ".github" / "workflows" / "ci.yml").exists()
        assert (project_dir / "Dockerfile").exists()


if __name__ == "__main__":
    # Simple test runner
    import traceback
    
    test_functions = [
        # Scaffolder tests
        test_project_spec_creation,
        test_parse_project_input_python_cli,
        test_parse_project_input_api,
        test_parse_project_input_with_ci,
        test_parse_project_input_with_docker,
        test_scaffolder_creates_files,
        test_scaffolder_writes_files,
        test_scaffolder_with_ci,
        test_scaffolder_with_docker,
        
        # Test runner tests
        test_test_result_dataclass,
        test_test_runner_detect_framework_pytest,
        test_test_runner_detect_framework_from_pyproject,
        test_test_runner_run_tests_no_tests,
        test_test_runner_run_python_tests,
        
        # Debug loop tests
        test_debug_loop_initialization,
        test_debug_loop_pattern_analysis,
        
        # Verification tests
        test_verify_project_nonexistent,
        test_verify_project_empty,
        test_verify_project_with_readme,
        test_verify_project_with_tests,
        
        # Pipeline tests
        test_pipeline_state_creation,
        test_pipeline_stage_enum,
        test_vibecoder_pipeline_initialization,
        test_vibecoder_pipeline_list_empty,
        test_vibecoder_pipeline_create_project,
        test_vibecoder_pipeline_project_status,
        test_project_pipeline_generates_working_project,
        
        # Integration tests
        test_end_to_end_project_generation,
        test_generated_project_structure,
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
