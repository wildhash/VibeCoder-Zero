"""Command execution with safety checks."""

import shlex
import subprocess
from typing import List

SAFE_PREFIXES = ["ls", "pwd", "mkdir", "touch", "git init", "git status", "python -m venv"]


def is_safe_command(cmd: str) -> bool:
    stripped = cmd.strip()
    return any(stripped.startswith(prefix) for prefix in SAFE_PREFIXES)


def execute_command(cmd: str, auto: bool = False) -> subprocess.CompletedProcess:
    if auto and is_safe_command(cmd):
        print(f"[AUTO-EXEC] {cmd}")
        return subprocess.run(cmd, shell=True, text=True, capture_output=True)
    else:
        print(f"[MANUAL EXECUTION REQUIRED]\n{cmd}\n")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
