# VibeCoder Package Structure

This document describes the modular package structure of VibeCoder.

## Directory Structure

```
vibecoder/
├── __init__.py
├── core/                   # Core analysis and planning logic
│   ├── __init__.py
│   ├── output.py          # DirectiveOutput dataclass
│   ├── analyzer.py        # CodebaseAnalyzer, EnvironmentState, constants
│   └── planner.py         # SelfImprovementPlanner
├── runtime/               # Runtime execution and state management
│   ├── __init__.py
│   ├── cli.py            # VibeCoder class and main() CLI entrypoint
│   ├── executor.py       # Command execution with safety checks
│   └── state.py          # VibeLog state persistence
├── llm/                  # LLM integration
│   ├── __init__.py
│   └── client.py         # LLMClient for OpenAI/Anthropic
├── vibe/                 # Context management
│   ├── __init__.py
│   └── context_manager.py # Project context persistence
└── self_reflector/       # Self-reflection capabilities
    ├── __init__.py
    └── reflector.py      # run_self_reflection()
```

## Usage

### Basic CLI Usage

```bash
# Run analysis on current directory
python3 vibecoder_zero.py

# Run analysis on specific directory
python3 vibecoder_zero.py --work-dir /path/to/project

# Output as JSON
python3 vibecoder_zero.py --json

# Auto-execute safe commands
python3 vibecoder_zero.py --auto-execute

# Run self-reflection (requires API key)
export OPENAI_API_KEY='your-key'
python3 vibecoder_zero.py --self-reflect
```

### Programmatic Usage

```python
from vibecoder.runtime.cli import VibeCoder
from vibecoder.llm.client import LLMClient

# Basic usage
vc = VibeCoder(work_dir=".")
directives = vc.execute()

# With LLM integration
llm = LLMClient(provider="openai", plan_model="gpt-4", code_model="gpt-4")
vc = VibeCoder(work_dir=".", llm_client=llm)
directives = vc.execute()

# With auto-execute
vc = VibeCoder(work_dir=".", auto_execute=True)
directives = vc.execute()
```

## New Features

### LLM Integration

The `LLMClient` class supports both OpenAI and Anthropic providers:

```python
from vibecoder.llm.client import LLMClient

# OpenAI
llm = LLMClient(
    provider="openai",
    plan_model="gpt-4",
    code_model="gpt-4",
    reflect_model="gpt-4"
)

# Anthropic
llm = LLMClient(
    provider="anthropic",
    plan_model="claude-3-5-sonnet-20241022",
    code_model="claude-3-5-sonnet-20241022"
)

# Use the client
code = llm.generate_code("Create a hello world function")
analysis = llm.analyze_error(stderr_output, context={"language": "python"})
next_steps = llm.plan_next_steps("Current state: ...")
```

### Command Execution with Safety

The executor module provides safe command execution:

```python
from vibecoder.runtime.executor import execute_command

# Manual execution (prints command, returns empty result)
result = execute_command("rm -rf /", auto=False)

# Auto execution (only runs safe commands)
result = execute_command("mkdir test", auto=True)  # Executes
result = execute_command("rm -rf /", auto=True)    # Does not execute
```

Safe commands include: `ls`, `pwd`, `mkdir`, `touch`, `git init`, `git status`, `python -m venv`

### Context Management

Store and retrieve project context:

```python
from vibecoder.vibe.context_manager import load_context, save_context

# Load context (returns default if file doesn't exist)
ctx = load_context()

# Modify context
ctx["project_name"] = "MyProject"
ctx["stack"] = ["Python", "FastAPI"]

# Save context
save_context(ctx)
```

Context is stored in `.vibe/context.json`.

### Self-Reflection

Generate a self-reflection report:

```python
from pathlib import Path
from vibecoder.llm.client import LLMClient
from vibecoder.self_reflector.reflector import run_self_reflection

llm = LLMClient(provider="openai", plan_model="gpt-4", code_model="gpt-4")
output_path = run_self_reflection(Path("."), llm)
print(f"Report saved to: {output_path}")
```

Or use the CLI:

```bash
export OPENAI_API_KEY='your-key'
python3 vibecoder_zero.py --self-reflect
```

## Testing

Run all tests:

```bash
make test
```

Or run tests directly:

```bash
python3 tests/test_vibecoder.py
python3 tests/test_new_modules.py
```

## Migration from VibeCoder-Zero

The original `vibecoder_zero.py` has been converted to a simple entrypoint that imports from the new package structure. All functionality remains the same, but is now organized into logical modules.

### Import Changes

Old:
```python
from vibecoder_zero import VibeCoder, CodebaseAnalyzer, DirectiveOutput
```

New:
```python
from vibecoder.runtime.cli import VibeCoder
from vibecoder.core.analyzer import CodebaseAnalyzer
from vibecoder.core.output import DirectiveOutput
```

## API Keys

VibeCoder supports the following API keys:

- `OPENAI_API_KEY` - For OpenAI integration
- `ANTHROPIC_API_KEY` - For Anthropic integration
- `GITHUB_TOKEN` - For GitHub API access

Set them as environment variables:

```bash
export OPENAI_API_KEY='your-key'
export ANTHROPIC_API_KEY='your-key'
export GITHUB_TOKEN='your-key'
```
