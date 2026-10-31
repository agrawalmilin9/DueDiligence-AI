"""Web research adapters backed by Crustdata's documented live endpoints."""

from typing import Any, Dict, List

from ..config import settings
from .crustdata import crustdata_service


class ResearchService:
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY

    @property
    def has_search_capability(self) -> bool:
        return crustdata_service.is_configured

    @property
    def has_llm_capability(self) -> bool:
        return bool(self.openai_key or self.gemini_key)

    async def search_web(
        self,
        query: str,
        max_results: int = 5,
    ) -> List[Dict[str, Any]]:
        response = await crustdata_service.search_web(query)
        if response.get("success") is not True:
            return []
        results = []
        for result in response.get("results", []):
            if not isinstance(result, dict):
                continue
            url = result.get("url")
            title = result.get("title")
            if not isinstance(url, str) or not url.startswith(("https://", "http://")):
                continue
            results.append(
                {
                    "title": title if isinstance(title, str) and title else url,
                    "url": url,
                    "snippet": result.get("snippet", "")
                    if isinstance(result.get("snippet"), str)
                    else "",
                }
            )
        return results[: max(0, max_results)]

    async def fetch_web_pages(self, urls: List[str]) -> List[Dict[str, Any]]:
        return await crustdata_service.enrich_web_pages(urls[:10])


# Shared singleton instance
research_service = ResearchService()
