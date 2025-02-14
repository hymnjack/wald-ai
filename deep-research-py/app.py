import streamlit as st
import asyncio
import os

# Local imports
from core.schemas import ResearchConfig
from core.research_engine import ResearchEngine
from core.feedback import generate_feedback
from integrations.firecrawl_client import FirecrawlClient

# Get config from environment or streamlit secrets
def get_config(key: str) -> str:
    # Try streamlit secrets first, then environment variables
    if hasattr(st, "secrets"):
        return st.secrets.get(key, "")
    return os.getenv(key, "")

# Initialize components
@st.cache_resource
def init_components():
    client = FirecrawlClient(api_key=get_config("FIRECRAWL_KEY"))
    engine = ResearchEngine(firecrawl_client=client)
    return client, engine

def main():
    st.title("Wald Deep Research")
    
    # Initialize
    client, engine = init_components()
    
    # Get query from user
    query = st.text_input("What would you like to research?")
    
    # Initialize session state for questions and answers if not exists
    if 'questions' not in st.session_state:
        st.session_state.questions = None
        st.session_state.answers = []
    
    if query:
        # Generate questions only if we don't have them or if query changed
        if st.session_state.questions is None:
            with st.spinner("Generating questions..."):
                st.session_state.questions = asyncio.run(generate_feedback(query))
                st.session_state.answers = [""] * len(st.session_state.questions)
        
        # Display questions and get answers
        st.write('Follow-up Questions:')
        for i, question in enumerate(st.session_state.questions):
            st.session_state.answers[i] = st.text_input(f"Q{i+1}: {question}", key=f"answer_{i}")
        
        # Only show the research button when all questions are answered
        all_answered = all(st.session_state.answers)
        if all_answered and st.button("Start Research"):
            with st.spinner("Researching..."):
                # Create progress bar and callback
                progress = st.progress(0)
                
                def update_progress(p):
                    total = p.total_depth * p.total_breadth
                    current = (p.current_depth - 1) * p.total_breadth + p.current_breadth
                    progress.progress(current / total)
                
                # Set the progress callback on the engine
                engine.on_progress = update_progress
                
                # Run research
                async def run_research():
                    try:
                        # Combine all information
                        combined_query = (
                            f"Initial Query: {query}\n"
                            "Follow-up Questions and Answers:\n" +
                            "\n".join(f"Q: {q}\nA: {a}" for q, a in zip(st.session_state.questions, st.session_state.answers))
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