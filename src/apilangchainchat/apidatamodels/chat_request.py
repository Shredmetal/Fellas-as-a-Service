from typing import Optional

from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    message: str
    conversation_id: Optional[str] = None
    model_type: str = "openai"
    flagged_content: Optional[str] = None
