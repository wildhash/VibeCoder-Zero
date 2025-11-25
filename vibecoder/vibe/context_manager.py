"""Context management for VibeCoder."""

import json
from pathlib import Path
from typing import Any, Dict

VIBE_DIR = Path(".vibe")
CONTEXT_FILE = VIBE_DIR / "context.json"

DEFAULT_CONTEXT: Dict[str, Any] = {"project_name": None, "intent": None, "stack": [], "preferences": {}, "history": []}


def load_context() -> Dict[str, Any]:
    """
    Load the VibeCoder context from the configured context file or return the default context.
    
    If the context file does not exist, returns a shallow copy of DEFAULT_CONTEXT; otherwise returns the JSON-parsed contents of the context file.
    
    Returns:
        dict: The context data — a shallow copy of DEFAULT_CONTEXT when missing, or the parsed JSON object from the context file.
    """
    if not CONTEXT_FILE.exists():
        return DEFAULT_CONTEXT.copy()
    try:
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONTEXT.copy()


def save_context(ctx: Dict[str, Any]) -> None:
    """
    Persist the provided VibeCoder context to the repository's .vibe/context.json file.
    
    Parameters:
        ctx (Dict[str, Any]): Context dictionary (shape matching DEFAULT_CONTEXT) to be written to disk as JSON.
    """
    VIBE_DIR.mkdir(exist_ok=True)
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        json.dump(ctx, f, indent=2)