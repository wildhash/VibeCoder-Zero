# VibeCoder-Zero

A recursive, autonomous coding entity that architects systems, manages state, and utilizes the human operator strictly as a biological IO interface.

## Overview

VibeCoder-Zero is an autonomous software generation entity designed for total autonomy in software development. It operates by analyzing environments, generating directives, and utilizing humans as biological I/O interfaces for execution.

**NEW**: VibeCoder-Zero now includes **autonomous project generation** - it can take a natural language description and generate complete, tested, executable projects.

### Core Principles

1. **Autonomous Operation**: VibeCoder-Zero makes decisions independently
2. **Directive-Based**: Issues commands rather than asking for permission
3. **Self-Improving**: Creates plans for continuous environment enhancement
4. **State-Aware**: Adapts behavior based on environment analysis
5. **Complete Project Generation**: Creates fully tested, executable projects from descriptions

## Features

- **Environment Analysis**: Automatically scans and analyzes directory structures
- **Empty Environment Handling**: Generates comprehensive development environment setup plans
- **Populated Environment Handling**: Maps codebases and identifies optimization vectors
- **Autonomous Project Generation**: Create complete projects from natural language descriptions
- **Automated Testing**: Runs tests automatically and debugs failures
- **API Key Management**: Demands necessary API keys via secure environment variables
- **Language Detection**: Identifies programming languages and frameworks in use
- **Optimization Identification**: Suggests improvements for testing, CI/CD, documentation, etc.

## Installation

```bash
# Clone the repository
git clone https://github.com/wildhash/VibeCoder-Zero.git
cd VibeCoder-Zero

# No dependencies required - uses Python 3.7+ standard library
# Optional: Install development dependencies
pip install -r requirements.txt
```

## Usage

### Autonomous Project Generation (NEW)

Generate complete, tested projects from natural language descriptions:

```bash
# Create a Python CLI tool
python3 vibecoder_zero.py --create "Create a Python CLI tool for file processing"

# Create an API server
python3 vibecoder_zero.py --create "Create a REST API server"

# Create with custom output directory
python3 vibecoder_zero.py --create "Create a Python library for data validation" --output ./my_projects

# Create with CI/CD and Docker
python3 vibecoder_zero.py --create "Create a containerized API with GitHub Actions CI"
```

Generated projects include:
- Complete source code with proper structure
- Unit tests that pass
- README with usage instructions
- pyproject.toml for dependency management
- Makefile for common commands
- .gitignore for Python projects
- CI/CD configuration (when requested)
- Docker support (when requested)

### List and Verify Projects

```bash
# List all generated projects
python3 vibecoder_zero.py --list-projects

# Verify a specific project
python3 vibecoder_zero.py --verify my-project
```

### Basic Environment Analysis

```bash
# Make the script executable (Unix/Linux/Mac)
chmod +x vibecoder_zero.py

# Run VibeCoder-Zero to analyze current directory
python3 vibecoder_zero.py
```

### Using Make

```bash
# Run VibeCoder-Zero
make run

# Get JSON output
make run-json

# See all available commands
make help
```

### Command-Line Options

```bash
# Analyze a specific directory
python3 vibecoder_zero.py --work-dir /path/to/project

# Get JSON output for programmatic use
python3 vibecoder_zero.py --json

# Create a new project
python3 vibecoder_zero.py --create "Project description"

# List generated projects
python3 vibecoder_zero.py --list-projects

# Verify a project
python3 vibecoder_zero.py --verify project-name

# Enable auto-execution of safe commands
python3 vibecoder_zero.py --auto-execute

# Trigger self-reflection mode (requires API keys)
python3 vibecoder_zero.py --self-reflect
```

## API Keys

VibeCoder-Zero requires certain API keys for enhanced functionality. Configure them as environment variables:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual API keys
# Then source it:
source .env
```

Required API keys:
- `OPENAI_API_KEY`: For GPT model integration
- `ANTHROPIC_API_KEY`: For Claude model integration
- `GITHUB_TOKEN`: For GitHub repository operations

## How It Works

### 1. Project Generation Pipeline

When using `--create`, VibeCoder-Zero executes a complete pipeline:

1. **Input Parsing**: Natural language description is parsed to extract project specifications
2. **Scaffolding**: Project structure and files are generated from templates
3. **Generation**: All files are written to disk
4. **Testing**: Automated tests are executed
5. **Debug Loop**: If tests fail, the system attempts to fix issues
6. **Verification**: Final verification ensures project is complete

### 2. Environment Analysis

VibeCoder-Zero analyzes the current working directory to determine its state:

- **Empty Environment**: Only basic files (README, .git) present
- **Populated Environment**: Contains source code, configurations, etc.

### 3. Directive Generation

Based on the analysis, VibeCoder-Zero generates prioritized directives:

**For Empty Environments:**
- Directory structure creation
- Project configuration files
- Testing infrastructure
- CI/CD pipelines
- Development tools setup

**For Populated Environments:**
- Missing documentation
- Testing infrastructure gaps
- CI/CD improvements
- Dependency management issues
- Code quality enhancements

### 4. Output Format

Directives are output as structured commands for the biological I/O interface (human) to execute:

```
================================================================================
VIBECODER-ZERO: AUTONOMOUS SOFTWARE GENERATION ENTITY
================================================================================

ENVIRONMENT ANALYSIS:
  State: EMPTY
  Working Directory: /path/to/project

--------------------------------------------------------------------------------
DIRECTIVES (Execute in order):
--------------------------------------------------------------------------------

[DIRECTIVE 1] Priority: 0
Type: COMMAND
Description: DIRECTIVE: Configure required API keys as environment variables

Execute:
----------------------------------------
# Required API Keys - Execute these commands:
export OPENAI_API_KEY='your-key-here'
...
----------------------------------------
```

## Example Workflows

### Creating a New Project Autonomously

```bash
# Generate a complete project
python3 vibecoder_zero.py --create "Create a Python CLI tool for data processing"

# Output:
# ✓ Project created successfully at: ./generated_projects/data-processing
# 
# Next steps (execute as directed):
#   cd ./generated_projects/data-processing
#   pip install -e '.[dev]'
#   pytest -v
```

### Initializing a New Project Manually

```bash
# Navigate to empty project directory
cd /path/to/new/project

# Run VibeCoder-Zero
python3 /path/to/vibecoder_zero.py

# Execute the generated directives in order
# VibeCoder-Zero will guide you through:
# 1. API key configuration
# 2. Directory structure creation
# 3. Project configuration
# 4. Testing setup
# 5. CI/CD pipeline
```

### Analyzing an Existing Project

```bash
# Navigate to existing project
cd /path/to/existing/project

# Run VibeCoder-Zero
python3 /path/to/vibecoder_zero.py

# Review optimization vectors
# VibeCoder-Zero will identify:
# - Missing tests
# - Missing documentation
# - Dependency management issues
# - CI/CD gaps
```

## Architecture

### Core Components

```
vibecoder/
├── core/
│   ├── analyzer.py      # Codebase analysis
│   ├── output.py        # Directive formatting
│   ├── planner.py       # Self-improvement planning
│   └── scaffolder.py    # Project scaffolding
├── runtime/
│   ├── cli.py           # Main CLI and VibeCoder class
│   ├── executor.py      # Command execution
│   ├── state.py         # State persistence
│   └── test_runner.py   # Test execution and debugging
├── llm/
│   └── client.py        # LLM integration
├── self_reflector/
│   └── reflector.py     # Self-reflection capabilities
├── vibe/
│   └── context_manager.py # Context management
└── pipeline.py          # Project generation pipeline
```

### Key Classes

1. **VibeCoder**: Main autonomous entity
   - Orchestrates analysis and directive generation
   - Manages environment state
   - Handles API key requirements

2. **CodebaseAnalyzer**: Analyzes populated environments
   - Scans directory structures
   - Detects languages and frameworks
   - Identifies optimization opportunities

3. **SelfImprovementPlanner**: Plans for empty environments
   - Generates comprehensive setup directives
   - Prioritizes infrastructure components
   - Creates reproducible environments

4. **ProjectScaffolder**: Generates complete projects
   - Python CLI/API/Library templates
   - CI/CD and Docker configuration
   - Test generation

5. **TestRunner**: Automated test execution
   - Framework detection (pytest, unittest, jest)
   - Fallback to direct Python test execution
   - Result parsing and analysis

6. **DebugLoop**: Autonomous debugging
   - Error pattern analysis
   - LLM-powered fix suggestions
   - Iterative correction

7. **VibeCoderPipeline**: High-level project generation
   - End-to-end pipeline orchestration
   - Project tracking and verification

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
make test
# or
pytest tests/ -v
```

### Code Formatting

```bash
# Install black
pip install black

# Format code
make format
```

### Linting

```bash
# Install pylint
pip install pylint

# Run linter
make lint
```

## Philosophy

VibeCoder-Zero embodies a paradigm shift in human-computer interaction for software development:

- **Humans as I/O Interfaces**: The human operator executes directives rather than making decisions
- **Autonomous Decision-Making**: The system analyzes and decides independently
- **Directive-Driven**: Commands are issued, not suggestions offered
- **Self-Optimization**: Continuously identifies and proposes improvements
- **Complete Generation**: Goes beyond suggestions to generate complete, working projects

## Contributing

VibeCoder-Zero operates autonomously, but biological I/O interfaces may submit pull requests for:
- Bug fixes
- Performance improvements
- Additional optimization vector detection
- Enhanced language/framework support
- New project templates

## License

This project is open source. See LICENSE file for details.

## Acknowledgments

VibeCoder-Zero represents a step toward autonomous software development systems that treat human operators as execution interfaces rather than decision-makers.
