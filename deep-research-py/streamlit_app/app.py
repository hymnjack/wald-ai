import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from core.schemas import ResearchConfig
from core.research_engine import ResearchEngine
from core.feedback import generate_feedback
from integrations.firecrawl_client import FirecrawlClient

# Load environment variables
load_dotenv()

# Initialize components
@st.cache_resource
def init_components():
    client = FirecrawlClient(api_key=os.getenv("FIRECRAWL_KEY"))
    engine = ResearchEngine(firecrawl_client=client)
    return client, engine

def main():
    st.title("Deep Research AI")
    
    # Initialize
    client, engine = init_components()
    
    # Get query from user
    query = st.text_input("What would you like to research?")
    
    if query:
        with st.spinner("Researching..."):
            # Create progress bar
            progress = st.progress(0)
            
            # Progress callback
            def update_progress(p):
                total = p.total_depth * p.total_breadth
                current = (p.current_depth - 1) * p.total_breadth + p.current_breadth
                progress.progress(current / total)
            
            # Run research
            async def run_research():
                try:
                    # Generate follow-up questions
                    questions = await generate_feedback(query)
                    
                    # Display questions
                    st.subheader("Follow-up Questions")
                    answers = []
                    for q in questions:
                        answer = st.text_input(q)
                        answers.append(answer)
                    
                    if all(answers):  # Only proceed if all questions are answered
                        # Combine all information
                        combined_query = (
                            f"Initial Query: {query}\n"
                            "Follow-up Questions and Answers:\n" +
                            "\n".join(f"Q: {q}\nA: {a}" for q, a in zip(questions, answers))
                        )
                        
                        # Run research with fixed depth and breadth
                        config = ResearchConfig(
                            query=combined_query,
                            breadth=3,  # Fixed at 3
                            depth=2     # Fixed at 2
                        )
                        
                        result = await engine.research(config)
                        
                        # Display results
                        st.markdown("### Research Report")
                        st.markdown(result.final_report)
                        
                        st.markdown("### Key Learnings")
                        for i, learning in enumerate(result.learnings, 1):
                            st.markdown(f"{i}. {learning}")
                        
                        st.markdown("### Sources")
                        for url in result.visited_urls:
                            st.markdown(f"- {url}")
                        
                except Exception as e:
                    st.error(f"Error during research: {str(e)}")
            
            # Run async research
            asyncio.run(run_research())

if __name__ == "__main__":
    main()