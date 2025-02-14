import os
from typing import List, Optional, Dict, Any
from firecrawl import FirecrawlApp
from pydantic import BaseModel

class SearchResponse(BaseModel):
    """Response from Firecrawl search API."""
    data: List[Dict[str, Any]]

class FirecrawlClient:
    """Async client for Firecrawl API."""
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30
    ):
        self.api_key = api_key or os.getenv("FIRECRAWL_KEY")
        if not self.api_key:
            raise ValueError("Firecrawl API key is required")
        
        # Make sure API key has fc- prefix
        if not self.api_key.startswith("fc-"):
            self.api_key = f"fc-{self.api_key}"
        
        # Initialize the official SDK client
        self.client = FirecrawlApp(api_key=self.api_key)

    async def search(self, query: str) -> SearchResponse:
        """Search using Firecrawl's search endpoint."""
        try:
            result = self.client.search(
                query,
                params={
                    "limit": 5,
                    "timeout": 15000,
                    "scrapeOptions": {
                        "formats": ["markdown"]
                    }
                }
            )
            return SearchResponse(data=result.get("data", []))
        except Exception as e:
            raise Exception(f"Firecrawl API error: {str(e)}")

    async def extract_content(self, url: str) -> str:
        """Extract content from a URL using scrape endpoint."""
        try:
            result = self.client.scrape_url(
                url,
                params={'formats': ['markdown']}
            )
            return result.get("markdown", "")
        except Exception as e:
            raise Exception(f"Content extraction error: {str(e)}")

    async def close(self):
        """Close the client (no-op since SDK handles this)."""
        pass
