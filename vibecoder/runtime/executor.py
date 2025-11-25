"""Command execution with safety checks."""

import shlex
import subprocess
from typing import List

SAFE_PREFIXES = ["ls", "pwd", "mkdir", "touch", "git init", "git status", "python -m venv"]


def is_safe_command(cmd: str) -> bool:
    """
    Determine whether a shell command may be automatically executed according to the module's safety rules.
    
    Performs validation against a set of dangerous shell operators and ensures the command begins with one of the approved SAFE_PREFIXES.
    
    Returns:
        True if the command contains none of the defined dangerous shell operators and begins with one of the approved SAFE_PREFIXES, False otherwise.
    """
    stripped = cmd.strip()
    
    # Check for command chaining operators
    dangerous_chars = [';', '&', '|', '>', '<', '`', '$', '(', ')']
    if any(char in stripped for char in dangerous_chars):
        return False
    
    # Check if command starts with a safe prefix
    return any(stripped.startswith(prefix) for prefix in SAFE_PREFIXES)


def execute_command(cmd: str, auto: bool = False) -> subprocess.CompletedProcess:
    """
    Execute a shell command when permitted by safety checks or return a benign CompletedProcess indicating manual execution is required.
    
    Parameters:
        cmd (str): The shell command to evaluate and potentially run.
        auto (bool): If True, attempt automatic execution; if False, do not run the command.
    
    Returns:
        subprocess.CompletedProcess: If `auto` is True and the command passes safety checks, the actual CompletedProcess returned by subprocess.run with stdout and stderr captured. Otherwise, a CompletedProcess with `args` set to `cmd`, `returncode` 0, and empty `stdout` and `stderr`.
    """
    if auto and is_safe_command(cmd):
        print(f"[AUTO-EXEC] {cmd}")
        return subprocess.run(cmd, shell=True, text=True, capture_output=True)
    else:
        print(f"[MANUAL EXECUTION REQUIRED]\n{cmd}\n")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")