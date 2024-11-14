from typing import List, Tuple, Optional

from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import HumanMessage
from langchain_core.tools import Tool

from src.langchainchat.agentmanagement.agent_state import AgentState
from src.langchainchat.configs.configs import ChatBotConfig
from src.langchainchat.toolmanagement.tool_executor import ToolExecutor


class ConversationManager:

    def __init__(self, config: ChatBotConfig):
        self.config = config
        self.tool_executor = ToolExecutor()

    @staticmethod
    def create_tool_description(tools: List[Tool]) -> str:
        """Create a description of available tools."""
        return "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in tools
        ])

    def handle_normal_conversation(
            self,
            current_message: str,
            conversation_history: List[Tuple[str, str]],
            tools_description: str,
            flagged_content: Optional[str],
            llm: BaseLanguageModel,
            tools: List[Tool],
            state: AgentState
    ) -> AgentState:
        try:
            context = "\n".join([
                f"{'User' if role == 'user' else 'Assistant'}: {msg}"
                for role, msg in conversation_history[-4:]
            ])

            full_prompt = self.config.get_full_prompt(
                tools_description=tools_description,
                context=context,
                current_message=current_message,
                flagged_content=flagged_content
            )

            response = llm.invoke([HumanMessage(content=full_prompt)])

            # Handle response content
            if isinstance(response, dict):
                response_content = response.get('content', '')
            elif hasattr(response, 'content'):
                if isinstance(response.content, list):
                    response_content = ''.join(
                        item.get('text', '')
                        for item in response.content
                        if isinstance(item, dict) and item.get('type') == 'text'
                    )
                else:
                    response_content = response.content
            else:
                response_content = str(response)

            # Check for tool execution
            if "EXECUTE_TOOL:" in response_content:
                command_part = response_content[response_content.index("EXECUTE_TOOL:"):]
                print(f"DEBUG: Command: {command_part}")
                tool_name = command_part.split()[1]

                query_start = command_part.index("QUERY:") + 6
                query_end = command_part.find("\n", query_start) if "\n" in command_part[query_start:] else len(
                    command_part)
                clean_query = command_part[query_start:query_end].strip()

                tool_input = f"EXECUTE_TOOL: {tool_name} QUERY: {clean_query}"
                print(f"DEBUG: Tool input: {tool_input}")

                tool_result = self.tool_executor.execute_tool(
                    tool_name,
                    tools,
                    conversation_history,
                    state,
                    tool_input
                )

                print(f"DEBUG: Tool Result: {tool_result}")

                if tool_result and tool_result['tool_output']:
                    analysis_prompt = self.config.get_tool_analysis_prompt(
                        user_message=current_message,
                        tool_output=tool_result['tool_output'],
                        flagged_content=flagged_content
                    )

                    explanation_response = llm.invoke([
                        HumanMessage(content=analysis_prompt)
                    ])

                    explanation = explanation_response.content if hasattr(explanation_response, 'content') else str(
                        explanation_response)

                    conversation_history.append(("assistant", explanation))
                    return AgentState(
                        messages=state["messages"],
                        next_step="end",
                        tool_output=tool_result['tool_output'],
                        final_answer=explanation
                    )
                else:
                    error_msg = "No results were returned from the tool."
                    conversation_history.append(("assistant", error_msg))
                    return AgentState(
                        messages=state["messages"],
                        next_step="end",
                        tool_output=None,
                        final_answer=error_msg
                    )

            # Handle normal conversation response
            conversation_history.append(("assistant", response_content))
            return AgentState(
                messages=state["messages"],
                next_step="end",
                tool_output=None,
                final_answer=response_content
            )

        except Exception as e:
            error_msg = f"Error during conversation: {str(e)}"
            print(f"DEBUG: {error_msg}")
            return AgentState(
                messages=state["messages"],
                next_step="end",
                tool_output=None,
                final_answer=error_msg
            )


        except Exception as e:
            error_msg = f"Error during conversation: {str(e)}"
            print(f"DEBUG: {error_msg}")
            return AgentState(
                messages=state["messages"],
                next_step="end",
                tool_output=None,
                final_answer=error_msg
            )
