from typing import List, Optional
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    """Represents a single search query with its research goal."""
    query: str = Field(..., description="The SERP query")
    research_goal: str = Field(
        ...,
        description="First talk about the goal of the research that this query is meant to accomplish, then go deeper into how to advance the research once the results are found, mention additional research directions. Be as specific as possible, especially for additional research directions."
    )

class ResearchProgress(BaseModel):
    """Tracks the progress of research operation."""
    current_depth: int
    total_depth: int
    current_breadth: int
    total_breadth: int
    current_query: Optional[str] = None
    total_queries: int
    completed_queries: int

class ResearchResult(BaseModel):
    """Contains the results of research operation."""
    learnings: List[str]
    visited_urls: List[str]
    final_report: str

class ResearchConfig(BaseModel):
    """Configuration for research operation."""
    query: str
    breadth: int = Field(default=3, ge=1, le=10)
    depth: int = Field(default=2, ge=1, le=5)
    max_learnings_per_query: int = Field(default=3, ge=1, le=10)
    max_followup_questions: int = Field(default=3, ge=1, le=10)
    content_chunk_size: int = Field(default=25000)
    concurrency_limit: int = Field(default=1, ge=1, le=5)  # Reduced to 1 to avoid rate limits
