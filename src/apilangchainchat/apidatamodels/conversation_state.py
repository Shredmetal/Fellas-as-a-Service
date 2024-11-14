from datetime import datetime, timezone
from typing import List, Tuple, Optional
from pydantic import BaseModel, ConfigDict, Field


class ConversationState(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    conversation_id: str
    messages: List[Tuple[str, str]]  # (role, content)
    model_type: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    flagged_content: Optional[str] = None
