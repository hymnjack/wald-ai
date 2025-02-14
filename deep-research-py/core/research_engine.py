import asyncio
from typing import List, Optional, Callable, Dict, Any
import markdown2
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
import os

from core.schemas import (
    ResearchConfig,
    ResearchProgress,
    ResearchResult,
    SearchQuery
)
from core.query_generator import QueryGenerator
from integrations.firecrawl_client import FirecrawlClient

class ResearchEngine:
    """Core research engine that performs iterative deep research."""
    
    def __init__(
        self,
        firecrawl_client: FirecrawlClient,
        query_generator: Optional[QueryGenerator] = None,
        on_progress: Optional[Callable[[ResearchProgress], None]] = None
    ):
        self.firecrawl = firecrawl_client
        self.query_generator = query_generator or QueryGenerator()
        self.on_progress = on_progress
        
        # Use o3-mini with supported parameters
        model = os.getenv("OPENAI_MODEL", "o3-mini")
        base_url = os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")
        
        # Only use reasoning_effort, specified directly
        self.llm = ChatOpenAI(
            model=model,
            base_url=base_url,
            reasoning_effort="medium"  # Specify directly instead of through model_kwargs
        )
        
    def _update_progress(self, progress: ResearchProgress):
        """Update research progress."""
        if self.on_progress:
            self.on_progress(progress)

    async def _process_content(
        self,
        content: str,
        config: ResearchConfig
    ) -> List[str]:
        """Process and extract learnings from content."""
        # Clean and trim content
        text = BeautifulSoup(
            markdown2.markdown(content),
            features="html.parser"
        ).get_text()
        text = text[:config.content_chunk_size]
        
        # Extract learnings using LLM
        response = await self.llm.ainvoke(
            f"Extract {config.max_learnings_per_query} key learnings from this text. "
            f"Focus on unique and specific insights: {text}"
        )
        
        learnings = []
        for line in response.content.split("\n"):
            if line.strip() and line.strip().startswith("-"):
                learnings.append(line.strip()[2:])
        
        return learnings[:config.max_learnings_per_query]

    async def _process_search_results(
        self,
        query: SearchQuery,
        config: ResearchConfig
    ) -> tuple[List[str], List[str]]:
        """Process search results for a query."""
        search_response = await self.firecrawl.search(query.query)
        learnings = []
        visited_urls = []
        
        # If no results from direct URL, treat query as a search term
        if not search_response.data:
            # For now, skip queries that don't return results
            # In the future, we could integrate with a search engine API here
            return [], []
        
        # Process results with rate limiting
        for result in search_response.data:
            if "url" in result and result["url"] not in visited_urls:
                try:
                    # Add delay between requests to respect rate limits
                    await asyncio.sleep(0.5)  # 500ms delay between requests
                    
                    content = await self.firecrawl.extract_content(result["url"])
                    new_learnings = await self._process_content(content, config)
                    learnings.extend(new_learnings)
                    visited_urls.append(result["url"])
                except Exception as e:
                    if "429" in str(e):  # Rate limit error
                        # Add longer delay and retry once
                        await asyncio.sleep(6)  # 6 second delay as suggested in error
                        try:
                            content = await self.firecrawl.extract_content(result["url"])
                            new_learnings = await self._process_content(content, config)
                            learnings.extend(new_learnings)
                            visited_urls.append(result["url"])
                        except Exception as retry_e:
                            print(f"Error processing {result['url']} after retry: {str(retry_e)}")
                            continue
                    else:
                        print(f"Error processing {result['url']}: {str(e)}")
                        continue
        
        return learnings, visited_urls

    async def _generate_final_report(
        self,
        query: str,
        learnings: List[str],
        visited_urls: List[str]
    ) -> str:
        """Generate a final comprehensive report."""
        learnings_text = "\n".join(f"<learning>\n{learning}\n</learning>" for learning in learnings)
        
        response = await self.llm.ainvoke(
            f"Given the following prompt from the user, write a final report on the topic using the learnings from research. "
            f"Make it as detailed as possible, aim for 3 or more pages, include ALL the learnings from research:\n\n"
            f"<prompt>{query}</prompt>\n\n"
            f"Here are all the learnings from previous research:\n\n"
            f"<learnings>\n{learnings_text}\n</learnings>"
        )
        
        # Add sources section
        urls_section = "\n\n## Sources\n\n" + "\n".join(f"- {url}" for url in visited_urls)
        return response.content + urls_section

    async def research(
        self,
        config: ResearchConfig
    ) -> ResearchResult:
        """Perform deep research based on configuration."""
        all_learnings = []
        all_visited_urls = []
        current_query = config.query
        
        for depth in range(config.depth):
            queries = await self.query_generator.generate_queries(
                current_query,
                num_queries=config.breadth,
                previous_learnings=all_learnings
            )
            
            progress = ResearchProgress(
                current_depth=depth + 1,
                total_depth=config.depth,
                current_breadth=0,
                total_breadth=len(queries),
                total_queries=config.depth * config.breadth,
                completed_queries=depth * config.breadth
            )
            self._update_progress(progress)
            
            # Process queries concurrently with rate limiting
            tasks = []
            sem = asyncio.Semaphore(config.concurrency_limit)
            
            async def process_with_semaphore(query: SearchQuery):
                async with sem:
                    return await self._process_search_results(query, config)
            
            for i, query in enumerate(queries):
                progress.current_breadth = i + 1
                progress.current_query = query.query
                progress.completed_queries += 1
                self._update_progress(progress)
                
                tasks.append(process_with_semaphore(query))
            
            results = await asyncio.gather(*tasks)
            
            for learnings, urls in results:
                all_learnings.extend(learnings)
                all_visited_urls.extend(urls)
            
            # Update query for next iteration based on learnings
            if depth < config.depth - 1:
                response = await self.llm.ainvoke(
                    "Based on these learnings, what should be our next research focus? "
                    f"Previous query: {current_query}\n"
                    f"Learnings:\n{chr(10).join(all_learnings)}"
                )
                current_query = response.content
        
        # Generate final report
        final_report = await self._generate_final_report(
            config.query,
            list(set(all_learnings)),
            list(set(all_visited_urls))
        )
        
        return ResearchResult(
            learnings=list(set(all_learnings)),
            visited_urls=list(set(all_visited_urls)),
            final_report=final_report
        )
