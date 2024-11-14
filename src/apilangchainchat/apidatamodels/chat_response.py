from typing import Optional, Any

from pydantic import BaseModel


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    has_used_tools: bool = False
    tool_output: Optional[str] = None
    error: Optional[str] = None
