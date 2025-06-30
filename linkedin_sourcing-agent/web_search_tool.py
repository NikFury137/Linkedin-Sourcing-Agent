"""
Web Search Tool
===============

Provides web search capabilities for the AI agents.
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional
from crewai_tools import BaseTool
import json

class WebSearchTool(BaseTool):
    """
    Custom web search tool that aggregates results from multiple search engines
    """

    name: str = "web_search"
    description: str = "Search the web for information about suppliers, companies, and market data"

    def __init__(self):
        super().__init__()
        self.session = None

    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    def _run(self, query: str, max_results: int = 10) -> str:
        """
        Synchronous search method (required by CrewAI)
        """
        return asyncio.run(self._search_async(query, max_results))

    async def _search_async(self, query: str, max_results: int = 10) -> str:
        """
        Perform asynchronous web search
        """
        try:
            results = []

            # Try DuckDuckGo search first (no API key required)
            ddg_results = await self._search_duckduckgo(query, max_results)
            results.extend(ddg_results)

            # Format results for agent consumption
            formatted_results = []
            for i, result in enumerate(results[:max_results], 1):
                formatted_results.append(f"""
{i}. {result.get('title', 'No title')}
   URL: {result.get('url', 'No URL')}
   Snippet: {result.get('snippet', 'No snippet')}
""")

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Search failed: {str(e)}"

    async def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """
        Search using DuckDuckGo (no API key required)
        """
        try:
            from duckduckgo_search import DDGS

            ddgs = DDGS()
            results = []

            for result in ddgs.text(query, max_results=max_results):
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'snippet': result.get('body', '')
                })

            return results

        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
            return []

    async def search_suppliers(self, product_category: str, location: str = "") -> List[Dict]:
        """
        Specialized method for searching suppliers
        """
        location_filter = f"in {location}" if location else ""
        queries = [
            f"{product_category} suppliers {location_filter}",
            f"{product_category} manufacturers {location_filter}",
            f"{product_category} distributors {location_filter}",
            f"wholesale {product_category} {location_filter}"
        ]

        all_results = []
        for query in queries:
            results = await self._search_async(query, 5)
            all_results.append(results)

        return all_results

    def __del__(self):
        """Cleanup session when object is destroyed"""
        if self.session:
            asyncio.create_task(self.session.close())
