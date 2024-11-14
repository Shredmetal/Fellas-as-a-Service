from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.utils import Input, Output
from typing import Any, Optional
from dotenv import load_dotenv
import sys
import time
import os


class CustomOpenAILLM(Runnable):
    """Simple wrapper class for ChatOpenAI."""

    def __init__(
            self,
            model_id: str = "gpt-4o",
            temperature: float = 0.0,
            verbose: bool = False,
            **kwargs
    ):
        super().__init__()

        # Try to load API key from .env file
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in .env file. "
                "Please create a .env file with your OpenAI API key "
                "in the format: OPENAI_API_KEY=your-key-here"
            )

        self.llm = ChatOpenAI(
            model_name=model_id,
            temperature=temperature,
            verbose=verbose,
            streaming=True,  # Enable streaming
            **kwargs
        )

    def invoke(
            self,
            input: Input,
            config: Optional[RunnableConfig] = None,
            **kwargs: Any
    ) -> Output:
        """Required method for Runnable interface."""
        response = ""
        for chunk in self.llm.stream(input, config, **kwargs):
            # Print chunk content character by character
            chunk_content = chunk.content
            for char in chunk_content:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.01)
            response += chunk_content

        sys.stdout.write("\n")
        sys.stdout.flush()
        return response
