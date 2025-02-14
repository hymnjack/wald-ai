from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from src.core.schemas import SearchQuery

class QueryList(BaseModel):
    """List of search queries."""
    queries: List[SearchQuery] = Field(..., description="List of SERP queries")
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            SearchQuery: lambda v: v.dict()
        }

SYSTEM_PROMPT = """You are an expert researcher. Follow these instructions when responding:
- Be highly organized and thorough in your research approach
- Generate diverse and unique search queries that explore different aspects
- Make sure each query has a clear research goal
- Consider both broad and specific angles of the topic
- Avoid redundant or overlapping queries"""

QUERY_TEMPLATE = """Given the following prompt from the user, generate a list of SERP queries to research the topic.
Return a maximum of {num_queries} queries, but feel free to return less if the original prompt is clear.
Make sure each query is unique and not similar to each other.

User Prompt: {query}

{context}

Return the response in this format:
{{
    "queries": [
        {{
            "query": "your search query here",
            "research_goal": "detailed research goal and future directions"
        }},
        // more queries...
    ]
}}"""

class QueryGenerator:
    """Generates search queries using LLM."""
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7
    ):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        self.parser = PydanticOutputParser(pydantic_object=QueryList)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", QUERY_TEMPLATE)
        ])

    async def generate_queries(
        self,
        query: str,
        num_queries: int = 3,
        previous_learnings: Optional[List[str]] = None
    ) -> List[SearchQuery]:
        """Generate search queries based on the input query."""
        context = ""
        if previous_learnings:
            context = "Previous learnings:\n" + "\n".join(
                f"- {learning}" for learning in previous_learnings
            )

        formatted_prompt = self.prompt.format(
            query=query,
            num_queries=num_queries,
            context=context
        )

        response = await self.llm.ainvoke(formatted_prompt)
        
        try:
            query_list = self.parser.parse(response.content)
            return query_list.queries[:num_queries]
        except Exception as e:
            raise Exception(f"Failed to parse LLM response: {str(e)}")
