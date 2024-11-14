from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.utils import Input, Output
from typing import Any, Optional
from dotenv import load_dotenv
import sys
import time
import os


class CustomAnthropicLLM(Runnable):
    def __init__(
            self,
            model_id: str = "claude-3-5-sonnet-latest",
            temperature: float = 0.0,
            verbose: bool = False,
            max_tokens: int = 4096,  # Add this
            **kwargs
    ):
        super().__init__()
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file...")

        self.llm = ChatAnthropic(
            model_name=model_id,
            temperature=temperature,
            verbose=verbose,
            streaming=True,
            max_tokens=max_tokens,  # Add this
            **kwargs
        )

    def invoke(
            self,
            input: Input,
            config: Optional[RunnableConfig] = None,
            **kwargs: Any
    ) -> Output:
        response = ""
        for chunk in self.llm.stream(input, config, **kwargs):
            chunk_content = chunk.content
            for char in chunk_content:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.01)
            response += chunk_content

        sys.stdout.write("\n")
        sys.stdout.flush()
        return response
