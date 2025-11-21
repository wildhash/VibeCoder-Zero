# VibeCoder-Zero Demo

This document demonstrates the autonomous operation of VibeCoder-Zero.

## Example 1: Empty Directory (Self-Improvement Mode)

When run in an empty directory, VibeCoder-Zero generates a comprehensive plan for establishing a development environment:

```bash
$ python3 vibecoder_zero.py
```

Output:
```
================================================================================
VIBECODER-ZERO: AUTONOMOUS SOFTWARE GENERATION ENTITY
================================================================================

ENVIRONMENT ANALYSIS:
  State: EMPTY
  Working Directory: /path/to/empty/project

DIRECTIVES (Execute in order):
[DIRECTIVE 1] Priority: 0 - Configure required API keys
[DIRECTIVE 2] Priority: 1 - Create directory structure (src, tests, docs, config)
[DIRECTIVE 3] Priority: 2 - Initialize Python project configuration
[DIRECTIVE 4] Priority: 2 - Establish pytest testing infrastructure
[DIRECTIVE 5] Priority: 3 - Implement CI/CD pipeline
[DIRECTIVE 6] Priority: 3 - Configure development environment standards
...
```

## Example 2: Populated Directory (Analysis Mode)

When run in a directory with existing code, VibeCoder-Zero analyzes the codebase and identifies optimization vectors:

```bash
$ cd /path/to/existing/project
$ python3 vibecoder_zero.py
```

Output:
```
================================================================================
VIBECODER-ZERO: AUTONOMOUS SOFTWARE GENERATION ENTITY
================================================================================

ENVIRONMENT ANALYSIS:
  State: POPULATED
  Working Directory: /path/to/existing/project
  Files: 42
  Directories: 8
  Languages Detected:
    - Python: 15 files
    - JavaScript: 12 files
    - HTML: 5 files
  Frameworks/Tools:
    - Python
    - pip
    - Node.js
    - npm

DIRECTIVES (Execute in order):
[DIRECTIVE 1] Priority: 0 - Configure 3 required API keys
[DIRECTIVE 2] Priority: 1 - HIGH: No test directory found - implement testing
[DIRECTIVE 3] Priority: 1 - HIGH: No CI/CD configuration - add automated pipelines
...
```

## Example 3: JSON Output for Programmatic Use

```bash
$ python3 vibecoder_zero.py --json
```

Returns structured JSON with:
- Environment state
- Analysis results (languages, frameworks, file counts)
- Prioritized directives array
- API key requirements

## Example 4: Analyzing a Specific Directory

```bash
$ python3 vibecoder_zero.py --work-dir /path/to/project
```

## Philosophy in Action

VibeCoder-Zero demonstrates:

1. **Autonomous Decision-Making**: Analyzes and decides without asking
2. **Directive-Based**: Issues commands, not suggestions
3. **Human as I/O Interface**: Treats operator as execution interface
4. **Context-Aware**: Adapts behavior based on environment state

## Use Cases

- **Greenfield Projects**: Complete environment setup plan
- **Legacy Codebases**: Identify technical debt and improvement opportunities
- **Code Audits**: Automated quality and completeness checks
- **Development Standards**: Enforce best practices across projects
