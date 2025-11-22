"""Self-reflection module for VibeCoder."""

from pathlib import Path
from typing import List
from vibecoder.llm.client import LLMClient

TARGET_FILES = ["vibecoder_zero.py", "IMPLEMENTATION_SUMMARY.md"]


def read_files(base_dir: Path, filenames: List[str]) -> str:
    chunks = []
    for name in filenames:
        p = base_dir / name
        if p.exists():
            chunks.append(f"=== {name} ===\n{p.read_text(encoding='utf-8')}\n")
    return "\n".join(chunks)


def run_self_reflection(base_dir: Path, llm: LLMClient) -> Path:
    code_snapshot = read_files(base_dir, TARGET_FILES)
    prompt = f"You are the SelfReflector module of VibeCoder.\n\nHere is a snapshot of key files:\n{code_snapshot}\n\n1. Analyze strengths and weaknesses.\n2. Propose improvements.\n3. Draft a PR body.\n\nOutput ONLY the PR body markdown."
    pr_body = llm.plan_next_steps(prompt)
    out_path = base_dir / "SELF_REFLECTION_PR.md"
    out_path.write_text(pr_body, encoding="utf-8")
    return out_path
