from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMConfig:
    """Enhanced configuration for LLM initialization."""
    model_type: str
    temperature: float = 0.0
    verbose: bool = False
    cache_dir: Optional[str] = None
    num_ctx: Optional[int] = None
    model_id: Optional[str] = None
    max_tokens: Optional[int] = 409
