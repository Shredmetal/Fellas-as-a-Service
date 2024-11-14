import os
from dataclasses import dataclass, field
from typing import Optional, List

from dotenv import load_dotenv


@dataclass
class ToolConfiguration:

    google_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None
    reliable_domains: List[str] = field(default_factory=lambda: [
    ])

    @classmethod
    def from_env(cls) -> 'ToolConfiguration':
        """Create configuration from environment variables."""
        load_dotenv()

        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")

        if not api_key or not cse_id:
            raise ValueError(
                "Missing required environment variables. "
                "Please ensure GOOGLE_API_KEY and GOOGLE_CSE_ID are set in .env file."
            )

        return cls(
            google_api_key=api_key,
            google_cse_id=cse_id
        )