from src.modelwrappers.anthropic.custom_anthropic_wrapper import CustomAnthropicLLM
from src.modelwrappers.model_config import LLMConfig
from src.modelwrappers.openai.custom_openai_wrapper import CustomOpenAILLM


class ModelWrapperFactory:
    """Factory for creating LLM instances."""

    @staticmethod
    def create_llm(config: LLMConfig):
        """Create an LLM instance based on configuration."""
        if config.model_type == "anthropic":
            return CustomAnthropicLLM(
                model_id=config.model_id or "claude-3-5-sonnet-latest",
                temperature=config.temperature,
                verbose=config.verbose,
                max_tokens=4096
            )
        elif config.model_type == "openai":
            return CustomOpenAILLM(
                model_id=config.model_id or "gpt-4o",
                temperature=config.temperature,
                verbose=config.verbose
            )
        else:
            raise ValueError(f"Unsupported model type: {config.model_type}")
