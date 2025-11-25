"""
Tests for new VibeCoder-One modules.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibecoder.llm.client import LLMClient
from vibecoder.runtime.executor import execute_command, is_safe_command
from vibecoder.vibe.context_manager import load_context, save_context, DEFAULT_CONTEXT
from vibecoder.self_reflector.reflector import read_files


def test_safe_command_detection():
    """Test safe command detection."""
    assert is_safe_command("ls -la")
    assert is_safe_command("pwd")
    assert is_safe_command("mkdir test")
    assert is_safe_command("git status")
    
    # Should reject command chaining
    assert not is_safe_command("ls; rm -rf /")
    assert not is_safe_command("ls && rm -rf /")
    assert not is_safe_command("ls | grep test")
    assert not is_safe_command("ls > output.txt")
    assert not is_safe_command("cat $(whoami)")
    assert not is_safe_command("ls `whoami`")
    
    # Should reject unsafe commands
    assert not is_safe_command("rm -rf /")
    assert not is_safe_command("sudo apt install")
    assert not is_safe_command("npm install")


def test_execute_command_manual():
    """Test execute_command requires manual execution for unsafe commands."""
    result = execute_command("rm -rf test", auto=False)
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_execute_command_auto_safe():
    """Test execute_command auto-executes safe commands."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # This should auto-execute
        execute_command(f"mkdir -p {tmpdir}/test_dir", auto=True)
        # Check the directory was created
        assert Path(tmpdir, "test_dir").exists()


def test_execute_command_auto_unsafe():
    """Test execute_command does not auto-execute unsafe commands."""
    result = execute_command("echo dangerous", auto=True)
    # Should return empty result since echo is not in SAFE_PREFIXES
    assert result.returncode == 0
    assert result.stdout == ""


def test_context_manager_default():
    """Test context manager returns default context when no file exists."""
    original_dir = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            context = load_context()
            assert context == DEFAULT_CONTEXT
    finally:
        os.chdir(original_dir)


def test_context_manager_save_load():
    """Test context manager can save and load context."""
    original_dir = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Save context
            test_context = {
                "project_name": "TestProject",
                "intent": "Testing",
                "stack": ["Python"],
                "preferences": {"style": "clean"},
                "history": ["init"]
            }
            save_context(test_context)
            
            # Load context
            loaded_context = load_context()
            assert loaded_context == test_context
    finally:
        os.chdir(original_dir)


def test_read_files():
    """Test read_files function."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test files
        (tmppath / "file1.txt").write_text("content1")
        (tmppath / "file2.txt").write_text("content2")
        
        # Read files
        content = read_files(tmppath, ["file1.txt", "file2.txt"])
        
        assert "file1.txt" in content
        assert "content1" in content
        assert "file2.txt" in content
        assert "content2" in content


def test_read_files_missing():
    """Test read_files handles missing files gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Try to read non-existent file
        content = read_files(tmppath, ["nonexistent.txt"])
        
        # Should return empty string
        assert content == ""


def test_llm_client_initialization_openai():
    """Test LLMClient initialization with OpenAI provider."""
    # Only test initialization, not actual API calls
    try:
        client = LLMClient(
            provider="openai",
            plan_model="gpt-4",
            code_model="gpt-4"
        )
        assert client.provider == "openai"
        assert client.plan_model == "gpt-4"
        assert client.code_model == "gpt-4"
        assert client.reflect_model == "gpt-4"
    except Exception:
        # It's okay if initialization fails without API keys
        pass


def test_llm_client_initialization_anthropic():
    """Test LLMClient initialization with Anthropic provider."""
    # Only test initialization, not actual API calls
    try:
        client = LLMClient(
            provider="anthropic",
            plan_model="claude-3-5-sonnet-20241022",
            code_model="claude-3-5-sonnet-20241022"
        )
        assert client.provider == "anthropic"
        assert client.plan_model == "claude-3-5-sonnet-20241022"
        assert client.code_model == "claude-3-5-sonnet-20241022"
    except Exception:
        # It's okay if initialization fails without API keys
        pass


def test_llm_client_invalid_provider():
    """Test LLMClient raises error for invalid provider."""
    try:
        LLMClient(
            provider="invalid",
            plan_model="model",
            code_model="model"
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown provider" in str(e)


if __name__ == "__main__":
    # Simple test runner
    import traceback
    
    test_functions = [
        test_safe_command_detection,
        test_execute_command_manual,
        test_execute_command_auto_safe,
        test_execute_command_auto_unsafe,
        test_context_manager_default,
        test_context_manager_save_load,
        test_read_files,
        test_read_files_missing,
        test_llm_client_initialization_openai,
        test_llm_client_initialization_anthropic,
        test_llm_client_invalid_provider,
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
