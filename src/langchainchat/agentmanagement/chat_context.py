from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class ChatContext:
    """Container for chat context and configuration."""
    tools_description: str
    conversation_history: List[Tuple[str, str]]
    verbose: bool = False
    flagged_content: Optional[str] = None
