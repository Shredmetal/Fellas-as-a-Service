from typing import List, Tuple

from langchain_core.tools import Tool

from src.langchainchat.agentmanagement.agent_state import AgentState


class ToolExecutor:
    @staticmethod
    def execute_tool(
            tool_name: str,
            tools: List[Tool],
            conversation_history: List[Tuple[str, str]],
            state: AgentState,
            input_message: str = None
    ) -> AgentState:
        print(f"\nDEBUG: Tool execution attempt - {tool_name}")

        for tool in tools:
            if tool.name == tool_name:
                try:
                    if tool_name == "search_reliable_sources":
                        if input_message and "QUERY:" in input_message:
                            query = input_message.split("QUERY:")[1].strip()
                            print(f"DEBUG: Search query: {query}")
                            result = tool.run(query)
                        else:
                            return AgentState(
                                messages=state["messages"],
                                next_step="end",
                                tool_output=None,
                                final_answer="I need a search query to check for information."
                            )
                    else:
                        result = tool.run(input_message)

                    print(f"DEBUG: Tool result: {result}")
                    return AgentState(
                        messages=state["messages"],
                        next_step="end",
                        tool_output=str(result),
                        final_answer=str(result)
                    )
                except Exception as e:
                    print(f"DEBUG: Tool error: {str(e)}")
                    return AgentState(
                        messages=state["messages"],
                        next_step="end",
                        tool_output=None,
                        final_answer=f"Tool execution error: {str(e)}"
                    )
        return None
