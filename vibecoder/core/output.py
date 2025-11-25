"""Output dataclass for VibeCoder directives."""

from dataclasses import dataclass
from typing import List


@dataclass
class DirectiveOutput:
    """Represents a directive to be executed by the biological IO interface."""
    directive_type: str  # 'command', 'code', 'file_operation'
    content: str
    description: str
    priority: int = 1
    requires_api_keys: List[str] = None

    def __post_init__(self):
        if self.requires_api_keys is None:
            self.requires_api_keys = []
