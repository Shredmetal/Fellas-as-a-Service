from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from uuid import uuid4
import uvicorn
from typing import Dict

from starlette.middleware.cors import CORSMiddleware

from src.apilangchainchat.apidatamodels.chat_request import ChatRequest
from src.apilangchainchat.apidatamodels.chat_response import ChatResponse
from src.apilangchainchat.apidatamodels.conversation_state import ConversationState
from src.langchainchat.agentmanagement.chat_handler import ChatHandler
from src.langgraphmanagement.langgraph_manager import LangGraphManager
from src.modelwrappers.model_config import LLMConfig
from src.modelwrappers.model_wrapper_factory import ModelWrapperFactory
from src.tools.tool_factory import ToolFactory

app = FastAPI(title="LangChain Chat API")


# Add CORS middleware configuration
app.add_middleware(       # type: ignore
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# use redis for prod, this is just in local memory LOL
conversations: Dict[str, ConversationState] = {}


def get_llm(model_type: str):
    """Initialize the appropriate LLM based on model type."""
    llm_config = LLMConfig(
        model_type=model_type,
        temperature=0.0,
        verbose=True,
        model_id=None
    )

    return ModelWrapperFactory.create_llm(llm_config)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    print(request)

    try:
        conversation_id = request.conversation_id or str(uuid4())

        # Get or create conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = ConversationState(
                conversation_id=conversation_id,
                messages=[],
                model_type=request.model_type
            )

        conversation = conversations[conversation_id]

        # Add new message as tuple
        conversation.messages.append(("user", request.message))

        # Initialize LLM and tools
        llm = get_llm(request.model_type)
        tool_factory = ToolFactory.from_env()
        tools = tool_factory.create_all_tools()

        # Create chat handler
        handle_chat, chat_context = ChatHandler.create_chat_handler(
            tools=tools,
            llm=llm,
            verbose=False,
            flagged_content=request.flagged_content
        )

        # Restore conversation history
        chat_context.conversation_history = conversation.messages

        # Create LangGraph manager and process message
        lang_graph_manager = LangGraphManager(handle_chat, chat_context)
        result = lang_graph_manager.process_message(request.message)

        # Add assistant response as tuple
        conversation.messages.append(("assistant", result.get("final_answer")))
        conversation.last_updated = datetime.now(timezone.utc)

        # Get tool output if it exists
        tool_output = result.get("tool_output")
        has_used_tools = tool_output is not None

        return ChatResponse(
            message=result.get("final_answer", "No response generated"),
            conversation_id=conversation_id,
            has_used_tools=has_used_tools,
            tool_output=str(tool_output) if tool_output is not None else None
        )

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Retrieve conversation history."""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversations[conversation_id]
