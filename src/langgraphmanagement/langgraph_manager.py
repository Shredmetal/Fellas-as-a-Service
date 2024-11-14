from langgraph.constants import END
from langgraph.graph import StateGraph
from typing import Optional, Any, Dict

from src.langchainchat.agentmanagement.agent_state import AgentState
from src.langchainchat.agentmanagement.chat_handler import ChatHandler


class LangGraphManager:
    
    def __init__(self, handle_chat, chat_context):
        self.handle_chat = handle_chat
        self.chat_context = chat_context
        self._compiled_workflow = None

    def compile_workflow(self):
        """Compiles the workflow if not already compiled."""
        if self._compiled_workflow is None:
            workflow = StateGraph(AgentState)
            workflow.add_node("process", self.handle_chat)
            workflow.set_entry_point("process")
            workflow.add_conditional_edges(
                "process",
                lambda x: ChatHandler.should_continue(x, self.chat_context.verbose),
                {"end": END}
            )
            self._compiled_workflow = workflow.compile()
        return self._compiled_workflow

    def create_initial_state(self, message: str) -> AgentState:
        """Creates an initial state object for the workflow."""
        return AgentState(
            messages=[message],
            next_step="start",
            tool_output=None,
            final_answer=None
        )

    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Processes a message through the workflow.

        Args:
            message: The input message to process

        Returns:
            Dict containing the workflow results
        """
        # Ensure workflow is compiled
        workflow = self.compile_workflow()

        # Create initial state
        initial_state = self.create_initial_state(message)

        # Process the message
        result = workflow.invoke(initial_state)

        return result

