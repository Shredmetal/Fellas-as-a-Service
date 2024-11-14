from typing import List, Tuple, Callable, Optional
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import Tool

from src.langchainchat.agentmanagement.agent_state import AgentState
from src.langchainchat.agentmanagement.chat_context import ChatContext
from src.langchainchat.configs.configs import ChatBotConfig
from src.langchainchat.conversationmanagement.conversation_manager import ConversationManager
from src.langchainchat.toolmanagement.tool_executor import ToolExecutor


class ChatHandler:
    """Main orchestrator for chat functionality."""

    def __init__(self):
        self.config = ChatBotConfig()
        self.tool_executor = ToolExecutor()
        self.conversation_manager = ConversationManager(self.config)

    @staticmethod
    def create_chat_handler(
            tools: List[Tool],
            llm: BaseLanguageModel,
            verbose: bool = False,
            flagged_content: Optional[str] = None
    ) -> Tuple[Callable[[AgentState], AgentState], ChatContext]:
        context = ChatContext(
            tools_description=ConversationManager.create_tool_description(tools),
            conversation_history=[],
            verbose=verbose,
            flagged_content=flagged_content
        )

        def handle_chat(state: AgentState) -> AgentState:
            if context.verbose:
                print(f"DEBUG - Handling chat: {state}")

            current_message = state["messages"][-1].lower()
            context.conversation_history.append(("user", current_message))

            conversation_manager = ConversationManager(ChatBotConfig())
            return conversation_manager.handle_normal_conversation(
                current_message=current_message,
                conversation_history=context.conversation_history,
                tools_description=context.tools_description,
                flagged_content=context.flagged_content,
                llm=llm,
                tools=tools,
                state=state
            )

        return handle_chat, context

    @staticmethod
    def should_continue(state: AgentState, verbose: bool = False) -> str:
        if verbose:
            print(f"DEBUG - Should continue check: {state}")
        return "end"
