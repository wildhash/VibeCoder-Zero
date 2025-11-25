"""Self-reflection module for VibeCoder."""

from pathlib import Path
from typing import List
from vibecoder.llm.client import LLMClient

TARGET_FILES = ["vibecoder_zero.py", "IMPLEMENTATION_SUMMARY.md"]


def read_files(base_dir: Path, filenames: List[str]) -> str:
    """
    Concatenate the contents of existing files from a base directory into a single snapshot with headings.
    
    Parameters:
    	base_dir (Path): Directory to look up the files in.
    	filenames (List[str]): Filenames to attempt to read from base_dir; missing files are skipped.
    
    Returns:
    	snapshot (str): A single string with one chunk per existing file in the format
    	"=== {filename} ===\n{file_contents}\n", joined by blank lines.
    """
    chunks = []
    for name in filenames:
        p = base_dir / name
        if p.exists():
            chunks.append(f"=== {name} ===\n{p.read_text(encoding='utf-8')}\n")
    return "\n".join(chunks)


def run_self_reflection(base_dir: Path, llm: LLMClient) -> Path:
    """
    Generate a self-reflection PR body for the repository and write it to disk.
    
    Builds a snapshot of selected target files, asks the provided LLM client to produce a PR body (containing analysis, improvements, and a draft PR), writes that markdown to SELF_REFLECTION_PR.md in base_dir, and returns the written file path.
    
    Parameters:
        base_dir (Path): Directory containing the target files and the location to write SELF_REFLECTION_PR.md.
        llm (LLMClient): Language model client used to generate the PR body; must implement plan_next_steps(prompt) -> str.
    
    Returns:
        Path: Path to the written SELF_REFLECTION_PR.md file.
    """
    code_snapshot = read_files(base_dir, TARGET_FILES)
    prompt = f"You are the SelfReflector module of VibeCoder.\n\nHere is a snapshot of key files:\n{code_snapshot}\n\n1. Analyze strengths and weaknesses.\n2. Propose improvements.\n3. Draft a PR body.\n\nOutput ONLY the PR body markdown."
    pr_body = llm.plan_next_steps(prompt)
    out_path = base_dir / "SELF_REFLECTION_PR.md"
    out_path.write_text(pr_body, encoding="utf-8")
    return out_path