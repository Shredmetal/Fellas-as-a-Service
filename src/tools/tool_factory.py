from langchain.tools import Tool
from typing import List

from src.tools.individualtools.news_checker import ReliableSourceSearcher
from src.tools.tool_config import ToolConfiguration


class ToolFactory:
    def __init__(self, config: ToolConfiguration):
        self.config = config
        self._db_reader = None
        self._source_searcher = None

    @classmethod
    def from_env(cls) -> 'ToolFactory':
        """Create factory from environment configuration."""
        return cls(ToolConfiguration.from_env())

    @property
    def source_searcher(self) -> ReliableSourceSearcher:
        if self._source_searcher is None:
            if not (self.config.google_api_key and self.config.google_cse_id):
                raise ValueError("Google API key and CSE ID required for source searching")
            self._source_searcher = ReliableSourceSearcher(
                self.config.google_api_key,
                self.config.google_cse_id,
                self.config.reliable_domains
            )
        return self._source_searcher

    def create_source_search_tool(self) -> Tool:
        return Tool(
            name="search_reliable_sources",
            func=self.source_searcher.search_reliable_sources,
            description="Searches the internet using Google. "
                        "Returns google search results based on the the search query."
        )

    def create_all_tools(self) -> List[Tool]:
        tools = [
            self.create_source_search_tool()
        ]

        return tools
