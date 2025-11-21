# VibeCoder-Zero

A recursive, autonomous coding entity that architects systems, manages state, and utilizes the human operator strictly as a biological IO interface.

## Overview

VibeCoder-Zero is an autonomous software generation entity designed for total autonomy in software development. It operates by analyzing environments, generating directives, and utilizing humans as biological I/O interfaces for execution.

### Core Principles

1. **Autonomous Operation**: VibeCoder-Zero makes decisions independently
2. **Directive-Based**: Issues commands rather than asking for permission
3. **Self-Improving**: Creates plans for continuous environment enhancement
4. **State-Aware**: Adapts behavior based on environment analysis

## Features

- **Environment Analysis**: Automatically scans and analyzes directory structures
- **Empty Environment Handling**: Generates comprehensive development environment setup plans
- **Populated Environment Handling**: Maps codebases and identifies optimization vectors
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

### Basic Execution

```bash
# Make the script executable (Unix/Linux/Mac)
chmod +x vibecoder_zero.py

# Run VibeCoder-Zero
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

### 1. Environment Analysis

VibeCoder-Zero first analyzes the current working directory to determine its state:

- **Empty Environment**: Only basic files (README, .git) present
- **Populated Environment**: Contains source code, configurations, etc.

### 2. Directive Generation

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

### 3. Output Format

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

### Initializing a New Project

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

4. **DirectiveOutput**: Structured directive format
   - Type-based classification
   - Priority-based ordering
   - API key dependency tracking

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

## Contributing

VibeCoder-Zero operates autonomously, but biological I/O interfaces may submit pull requests for:
- Bug fixes
- Performance improvements
- Additional optimization vector detection
- Enhanced language/framework support

## License

This project is open source. See LICENSE file for details.

## Acknowledgments

VibeCoder-Zero represents a step toward autonomous software development systems that treat human operators as execution interfaces rather than decision-makers.
