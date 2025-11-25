"""Command execution with safety checks."""

import shlex
import subprocess

SAFE_PREFIXES = ["ls", "pwd", "mkdir", "touch", "git init", "git status", "python -m venv"]


def is_safe_command(cmd: str) -> bool:
    """Check if a command is safe to auto-execute.
    
    Prevents command chaining by checking for shell operators.
    """
    stripped = cmd.strip()
    
    # Check for command chaining operators
    dangerous_chars = [';', '&', '|', '>', '<', '`', '$', '(', ')']
    if any(char in stripped for char in dangerous_chars):
        return False
    
    # Check if command starts with a safe prefix
    return any(stripped.startswith(prefix) for prefix in SAFE_PREFIXES)


def execute_command(cmd: str, auto: bool = False) -> subprocess.CompletedProcess:
    if auto and is_safe_command(cmd):
        print(f"[AUTO-EXEC] {cmd}")
        return subprocess.run(shlex.split(cmd), text=True, capture_output=True)
    else:
        print(f"[MANUAL EXECUTION REQUIRED]\n{cmd}\n")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
