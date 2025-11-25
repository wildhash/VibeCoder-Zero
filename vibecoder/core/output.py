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
        """
        Ensure the instance's `requires_api_keys` attribute is an empty list when not provided.
        
        If `requires_api_keys` was set to `None` during initialization, this method replaces it with an empty list so callers can safely append or iterate without checking for `None`.
        """
        if self.requires_api_keys is None:
            self.requires_api_keys = []