"""Test runner and debug loop for VibeCoder-Zero.

This module provides autonomous test execution and debugging capabilities,
enabling the system to verify generated code and fix issues automatically.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class TestStatus(Enum):
    """Status of test execution."""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TestResult:
    """Result of a single test or test suite."""
    name: str
    status: TestStatus
    output: str
    error: str = ""
    duration: float = 0.0
    details: Dict = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class DebugSuggestion:
    """Suggested fix for a test failure."""
    file_path: str
    line_number: Optional[int]
    original_code: str
    suggested_code: str
    explanation: str
    confidence: float  # 0.0 to 1.0


class TestRunner:
    """Executes tests and captures results."""
    
    def __init__(self, project_dir: Path):
        """Initialize test runner.
        
        Args:
            project_dir: Root directory of the project to test
        """
        self.project_dir = Path(project_dir)
    
    def detect_test_framework(self) -> Optional[str]:
        """Detect which test framework the project uses.
        
        Returns:
            Test framework name or None if not detected
        """
        # Check for pytest
        if (self.project_dir / 'pytest.ini').exists():
            return 'pytest'
        if (self.project_dir / 'pyproject.toml').exists():
            content = (self.project_dir / 'pyproject.toml').read_text()
            if '[tool.pytest' in content:
                return 'pytest'
        
        # Check for unittest-style tests
        tests_dir = self.project_dir / 'tests'
        if tests_dir.exists():
            for test_file in tests_dir.glob('test_*.py'):
                content = test_file.read_text()
                if 'import unittest' in content:
                    return 'unittest'
                if 'import pytest' in content or 'def test_' in content:
                    return 'pytest'
        
        # Check for JavaScript test frameworks
        if (self.project_dir / 'package.json').exists():
            content = (self.project_dir / 'package.json').read_text()
            if '"jest"' in content:
                return 'jest'
            if '"mocha"' in content:
                return 'mocha'
        
        # Default to pytest for Python projects
        if any(self.project_dir.glob('*.py')) or (self.project_dir / 'tests').exists():
            return 'pytest'
        
        return None
    
    def run_tests(self, test_path: Optional[str] = None, verbose: bool = True) -> TestResult:
        """Run tests and return results.
        
        Args:
            test_path: Specific test file or directory (optional)
            verbose: Include verbose output
            
        Returns:
            TestResult with overall status and details
        """
        framework = self.detect_test_framework()
        
        if framework == 'pytest':
            result = self._run_pytest(test_path, verbose)
            # If pytest is not installed, fall back to running tests directly
            if 'No module named pytest' in (result.error or '') or 'No module named pytest' in (result.output or ''):
                return self._run_python_tests(test_path)
            return result
        elif framework == 'unittest':
            return self._run_unittest(test_path, verbose)
        elif framework == 'jest':
            return self._run_jest(test_path, verbose)
        else:
            # Try running test files directly
            return self._run_python_tests(test_path)
    
    def _run_pytest(self, test_path: Optional[str], verbose: bool) -> TestResult:
        """Run pytest and capture results."""
        cmd = [sys.executable, '-m', 'pytest']
        
        if verbose:
            cmd.append('-v')
        
        if test_path:
            cmd.append(test_path)
        else:
            cmd.append('tests/')
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            status = TestStatus.PASSED if result.returncode == 0 else TestStatus.FAILED
            
            return TestResult(
                name="pytest",
                status=status,
                output=result.stdout,
                error=result.stderr,
                details=self._parse_pytest_output(result.stdout)
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                name="pytest",
                status=TestStatus.ERROR,
                output="",
                error="Test execution timed out after 5 minutes"
            )
        except Exception as e:
            return TestResult(
                name="pytest",
                status=TestStatus.ERROR,
                output="",
                error=str(e)
            )
    
    def _run_unittest(self, test_path: Optional[str], verbose: bool) -> TestResult:
        """Run unittest and capture results."""
        cmd = [sys.executable, '-m', 'unittest']
        
        if verbose:
            cmd.append('-v')
        
        if test_path:
            cmd.append(test_path)
        else:
            cmd.append('discover')
            cmd.extend(['-s', 'tests'])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            status = TestStatus.PASSED if result.returncode == 0 else TestStatus.FAILED
            
            return TestResult(
                name="unittest",
                status=status,
                output=result.stdout + result.stderr,
                error="" if result.returncode == 0 else result.stderr
            )
        except Exception as e:
            return TestResult(
                name="unittest",
                status=TestStatus.ERROR,
                output="",
                error=str(e)
            )
    
    def _run_jest(self, test_path: Optional[str], verbose: bool) -> TestResult:
        """Run jest and capture results."""
        cmd = ['npx', 'jest']
        
        if verbose:
            cmd.append('--verbose')
        
        if test_path:
            cmd.append(test_path)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            status = TestStatus.PASSED if result.returncode == 0 else TestStatus.FAILED
            
            return TestResult(
                name="jest",
                status=status,
                output=result.stdout,
                error=result.stderr
            )
        except Exception as e:
            return TestResult(
                name="jest",
                status=TestStatus.ERROR,
                output="",
                error=str(e)
            )
    
    def _run_python_tests(self, test_path: Optional[str]) -> TestResult:
        """Run Python test files directly."""
        tests_dir = self.project_dir / 'tests'
        
        if not tests_dir.exists():
            return TestResult(
                name="python",
                status=TestStatus.SKIPPED,
                output="",
                error="No tests directory found"
            )
        
        all_output = []
        all_errors = []
        overall_status = TestStatus.PASSED
        
        test_files = list(tests_dir.glob('test_*.py'))
        
        if not test_files:
            return TestResult(
                name="python",
                status=TestStatus.SKIPPED,
                output="",
                error="No test files found"
            )
        
        for test_file in test_files:
            try:
                result = subprocess.run(
                    [sys.executable, str(test_file)],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                all_output.append(f"=== {test_file.name} ===\n{result.stdout}")
                
                if result.returncode != 0:
                    overall_status = TestStatus.FAILED
                    all_errors.append(f"{test_file.name}:\n{result.stderr}")
                    
            except Exception as e:
                overall_status = TestStatus.ERROR
                all_errors.append(f"{test_file.name}: {e}")
        
        return TestResult(
            name="python",
            status=overall_status,
            output="\n".join(all_output),
            error="\n".join(all_errors)
        )
    
    def _parse_pytest_output(self, output: str) -> Dict:
        """Parse pytest output for details."""
        details = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Look for summary line like "10 passed, 2 failed"
        for line in output.split('\n'):
            if 'passed' in line.lower() and ('failed' in line.lower() or 'error' in line.lower() or '=' in line):
                parts = line.split(',')
                for part in parts:
                    part = part.strip().lower()
                    for status in ['passed', 'failed', 'skipped', 'error']:
                        if status in part:
                            try:
                                count = int(part.split()[0])
                                details[status if status != 'error' else 'errors'] = count
                            except (ValueError, IndexError):
                                pass
        
        return details


class DebugLoop:
    """Autonomous debugging system that analyzes failures and suggests fixes."""
    
    COMMON_ERRORS = {
        'ImportError': {
            'pattern': r"ImportError: No module named '(\w+)'",
            'fix': 'Add missing import or install package',
        },
        'AttributeError': {
            'pattern': r"AttributeError: '(\w+)' object has no attribute '(\w+)'",
            'fix': 'Check attribute name or add missing method/property',
        },
        'TypeError': {
            'pattern': r"TypeError: (\w+)\(\) takes (\d+) positional arguments but (\d+) were given",
            'fix': 'Adjust function arguments',
        },
        'AssertionError': {
            'pattern': r"AssertionError",
            'fix': 'Review assertion logic or expected values',
        },
        'SyntaxError': {
            'pattern': r"SyntaxError: (.+)",
            'fix': 'Fix syntax error in code',
        },
        'IndentationError': {
            'pattern': r"IndentationError: (.+)",
            'fix': 'Fix indentation',
        },
        'NameError': {
            'pattern': r"NameError: name '(\w+)' is not defined",
            'fix': 'Define the variable or fix typo',
        },
    }
    
    def __init__(self, project_dir: Path, llm_client=None):
        """Initialize debug loop.
        
        Args:
            project_dir: Project directory
            llm_client: Optional LLM client for intelligent suggestions
        """
        self.project_dir = Path(project_dir)
        self.llm_client = llm_client
        self.test_runner = TestRunner(project_dir)
        self.max_iterations = 5
    
    def analyze_failure(self, test_result: TestResult) -> List[DebugSuggestion]:
        """Analyze test failure and generate fix suggestions.
        
        Args:
            test_result: Failed test result
            
        Returns:
            List of suggested fixes
        """
        suggestions = []
        error_text = test_result.error or test_result.output
        
        # Try pattern-based analysis first
        suggestions.extend(self._pattern_analysis(error_text))
        
        # If LLM is available, get more sophisticated suggestions
        if self.llm_client:
            suggestions.extend(self._llm_analysis(test_result))
        
        return suggestions
    
    def run_debug_loop(self) -> Tuple[bool, List[TestResult]]:
        """Run autonomous debug loop until tests pass or max iterations reached.
        
        Returns:
            Tuple of (success, list of test results from each iteration)
        """
        results = []
        
        for iteration in range(self.max_iterations):
            # Run tests
            result = self.test_runner.run_tests()
            results.append(result)
            
            if result.status == TestStatus.PASSED:
                return True, results
            
            if result.status == TestStatus.ERROR:
                # Cannot proceed if there's a fundamental error
                break
            
            # Analyze failure and get suggestions
            suggestions = self.analyze_failure(result)
            
            if not suggestions:
                # No suggestions, cannot auto-fix
                break
            
            # Apply first high-confidence suggestion
            applied = False
            for suggestion in sorted(suggestions, key=lambda s: -s.confidence):
                if suggestion.confidence >= 0.7:
                    if self._apply_suggestion(suggestion):
                        applied = True
                        break
            
            if not applied:
                # Could not apply any fixes
                break
        
        return False, results
    
    def _pattern_analysis(self, error_text: str) -> List[DebugSuggestion]:
        """Analyze errors using pattern matching."""
        import re
        suggestions = []
        
        for error_type, info in self.COMMON_ERRORS.items():
            match = re.search(info['pattern'], error_text)
            if match:
                # Extract file and line info if present
                file_match = re.search(r'File "([^"]+)", line (\d+)', error_text)
                file_path = file_match.group(1) if file_match else ""
                line_num = int(file_match.group(2)) if file_match else None
                
                suggestions.append(DebugSuggestion(
                    file_path=file_path,
                    line_number=line_num,
                    original_code="",  # Would need to read file
                    suggested_code="",  # Pattern-based can't provide this
                    explanation=f"{error_type}: {info['fix']}",
                    confidence=0.5  # Medium confidence for pattern-based
                ))
        
        return suggestions
    
    def _llm_analysis(self, test_result: TestResult) -> List[DebugSuggestion]:
        """Use LLM to analyze errors and suggest fixes."""
        if not self.llm_client:
            return []
        
        try:
            # Get relevant source code context
            error_context = self._get_error_context(test_result)
            
            response = self.llm_client.analyze_error(
                stderr=test_result.error or test_result.output,
                context=error_context
            )
            
            # Parse LLM response into suggestions
            return self._parse_llm_suggestions(response)
        except Exception:
            return []
    
    def _get_error_context(self, test_result: TestResult) -> Dict:
        """Extract relevant source code context for error analysis."""
        import re
        
        context = {
            'test_output': test_result.output[:2000],  # Limit size
            'error': test_result.error[:1000],
        }
        
        # Try to find mentioned files
        file_pattern = r'File "([^"]+\.py)", line (\d+)'
        matches = re.findall(file_pattern, test_result.error or test_result.output)
        
        files_content = {}
        for file_path, line_num in matches[:3]:  # Limit to 3 files
            try:
                path = Path(file_path)
                if path.exists() and path.is_file():
                    content = path.read_text()
                    # Get context around the error line
                    lines = content.split('\n')
                    line_idx = int(line_num) - 1
                    start = max(0, line_idx - 5)
                    end = min(len(lines), line_idx + 5)
                    files_content[file_path] = '\n'.join(lines[start:end])
            except Exception:
                pass
        
        context['relevant_code'] = files_content
        return context
    
    def _parse_llm_suggestions(self, llm_response: str) -> List[DebugSuggestion]:
        """Parse LLM response into DebugSuggestion objects."""
        # Simple parsing - LLM response should contain fix suggestions
        suggestions = []
        
        if llm_response and len(llm_response) > 10:
            suggestions.append(DebugSuggestion(
                file_path="",
                line_number=None,
                original_code="",
                suggested_code=llm_response,
                explanation="AI-suggested fix",
                confidence=0.6
            ))
        
        return suggestions
    
    def _apply_suggestion(self, suggestion: DebugSuggestion) -> bool:
        """Apply a debug suggestion to fix the code.
        
        Returns:
            True if suggestion was applied successfully
        """
        if not suggestion.file_path or not suggestion.suggested_code:
            return False
        
        try:
            file_path = Path(suggestion.file_path)
            if not file_path.exists():
                return False
            
            # Read current content
            content = file_path.read_text()
            
            # Apply fix (simple replacement for now)
            if suggestion.original_code and suggestion.original_code in content:
                new_content = content.replace(
                    suggestion.original_code,
                    suggestion.suggested_code,
                    1  # Only replace first occurrence
                )
                file_path.write_text(new_content)
                return True
            
            return False
        except Exception:
            return False


def verify_project(project_dir: Path) -> Dict:
    """Verify a generated project is complete and working.
    
    Args:
        project_dir: Path to the project
        
    Returns:
        Verification report
    """
    report = {
        'exists': project_dir.exists(),
        'has_tests': False,
        'tests_pass': False,
        'has_readme': False,
        'has_config': False,
        'issues': [],
    }
    
    if not report['exists']:
        report['issues'].append('Project directory does not exist')
        return report
    
    # Check for essential files
    report['has_readme'] = (project_dir / 'README.md').exists()
    report['has_config'] = any([
        (project_dir / 'pyproject.toml').exists(),
        (project_dir / 'setup.py').exists(),
        (project_dir / 'package.json').exists(),
    ])
    
    # Check for tests
    tests_dir = project_dir / 'tests'
    report['has_tests'] = tests_dir.exists() and any(tests_dir.glob('test_*.py'))
    
    # Run tests if they exist
    if report['has_tests']:
        runner = TestRunner(project_dir)
        result = runner.run_tests()
        report['tests_pass'] = result.status == TestStatus.PASSED
        report['test_details'] = {
            'status': result.status.value,
            'output': result.output[:500],  # Limit output
        }
        
        if not report['tests_pass']:
            report['issues'].append(f'Tests failed: {result.error[:200]}')
    else:
        report['issues'].append('No tests found')
    
    # Check for missing essentials
    if not report['has_readme']:
        report['issues'].append('Missing README.md')
    if not report['has_config']:
        report['issues'].append('Missing project configuration (pyproject.toml)')
    
    return report
