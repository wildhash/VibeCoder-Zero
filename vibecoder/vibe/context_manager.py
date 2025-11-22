"""Context management for VibeCoder."""

import json
from pathlib import Path
from typing import Any, Dict

VIBE_DIR = Path(".vibe")
CONTEXT_FILE = VIBE_DIR / "context.json"

DEFAULT_CONTEXT: Dict[str, Any] = {"project_name": None, "intent": None, "stack": [], "preferences": {}, "history": []}


def load_context() -> Dict[str, Any]:
    if not CONTEXT_FILE.exists(): return DEFAULT_CONTEXT.copy()
    with open(CONTEXT_FILE, "r", encoding="utf-8") as f: return json.load(f)


def save_context(ctx: Dict[str, Any]) -> None:
    VIBE_DIR.mkdir(exist_ok=True)
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f: json.dump(ctx, f, indent=2)
