from typing import TypedDict, Sequence


class AgentState(TypedDict):
    messages: Sequence[str]
    next_step: str
    tool_output: str | None
    final_answer: str | None
