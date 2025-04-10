import streamlit as st
import sys
import os
import pandas as pd

# Add the path to the yoastevals.py file
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'yoastEvalsFinal', 'mainyoastfiles'))

# Import the evaluate_article function
from yoastevals import evaluate_article

# Import the GPT correction function
from gpt_correction import generate_correction

# Set page config
st.set_page_config(
    page_title="SEO Content Evaluator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'article_content' not in st.session_state:
    st.session_state.article_content = None

if 'focus_keyword' not in st.session_state:
    st.session_state.focus_keyword = None
    
if 'results' not in st.session_state:
    st.session_state.results = None
    
if 'rewritten_content' not in st.session_state:
    st.session_state.rewritten_content = None

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTextArea textarea {
        height: 400px;
    }
    .green-text {
        color: green;
        font-weight: bold;
    }
    .orange-text {
        color: orange;
        font-weight: bold;
    }
    .red-text {
        color: red;
        font-weight: bold;
    }
    .rewritten-content {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 20px;
        background-color: #f9f9f9;
        margin-top: 10px;
        margin-bottom: 20px;
        white-space: pre-wrap;
        overflow-wrap: break-word;
    }
    .rewritten-content-container {
        margin-top: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.title("SEO Content Evaluator")
st.markdown("Analyze your content for SEO optimization using SEO criteria.")

# Create a two-column layout
col1, col2 = st.columns([3, 2])

with col1:
    # Input fields
    st.subheader("Content Input")
    article_content = st.text_area("Paste your article content here (Markdown format supported)", height=400)
    focus_keyword = st.text_input("Enter your focus keyword or keyphrase")
    
    # Optimize button (evaluates and rewrites content)
    optimize_button = st.button("Optimize", type="primary")

# Run evaluation when button is clicked
# Import dotenv to load environment variables from .env file
import dotenv
from pathlib import Path

# Load environment variables from .env file in the agents/yoast_seo directory
dotenv_path = Path(os.path.dirname(__file__)).parent / '.env'
dotenv.load_dotenv(dotenv_path)

# Check if OpenAI API key is set
if 'OPENAI_API_KEY' not in os.environ:
    st.sidebar.warning("⚠️ OpenAI API key not set. Please check the .env file in the agents/yoast_seo directory.")

if optimize_button and article_content and focus_keyword:
    with st.spinner("Evaluating your content..."):
        # Run the evaluation
        results = evaluate_article(article_content, focus_keyword)
        
        # Store results in session state for later use with GPT
        st.session_state.article_content = article_content
        st.session_state.focus_keyword = focus_keyword
        st.session_state.results = results
        
        # Display results in the second column
        with col2:
            st.subheader("Evaluation Results")
            
            # Count scores for summary
            green_count = 0
            orange_count = 0
            red_count = 0
            
            # Create a DataFrame for better visualization
            results_data = []
            
            # Process each criterion
            for criterion, score in results.items():
                # Count for summary
                if score == "Green":
                    green_count += 1
                    color_class = "green-text"
                    emoji = "✅"
                elif score == "Orange":
                    orange_count += 1
                    color_class = "orange-text"
                    emoji = "⚠️"
                elif score == "Red":
                    red_count += 1
                    color_class = "red-text"
                    emoji = "❌"
                else:
                    color_class = ""
                    emoji = "ℹ️"
                
                # Add to results data
                results_data.append({
                    "Criterion": criterion,
                    "Score": score,
                    "Emoji": emoji
                })
                
                # Display criterion with colored text
                st.markdown(f"### {emoji} {criterion}")
                st.markdown(f'<span class="{color_class}">{score}</span>', unsafe_allow_html=True)
                st.markdown("---")
            
            # Display summary
            st.subheader("Summary")
            col1_summary, col2_summary, col3_summary = st.columns(3)
            with col1_summary:
                st.markdown(f'<p class="green-text">✅ Green: {green_count}</p>', unsafe_allow_html=True)
            with col2_summary:
                st.markdown(f'<p class="orange-text">⚠️ Orange: {orange_count}</p>', unsafe_allow_html=True)
            with col3_summary:
                st.markdown(f'<p class="red-text">❌ Red: {red_count}</p>', unsafe_allow_html=True)
            
            # Display results as a table
            st.subheader("Results Table")
            results_df = pd.DataFrame(results_data)
            st.dataframe(results_df)
            
                        # Now automatically generate rewritten content
            with st.spinner("Generating AI-rewritten content..."):
                # Call GPT API to get rewritten content
                st.session_state.rewritten_content = generate_correction(article_content, focus_keyword, results)
                
            # Display rewritten content
            st.markdown("---")
            st.subheader("AI-Rewritten Content")
            
            # Create a container with a border for the rewritten content
            rewritten_container = st.container()
            with rewritten_container:
                st.markdown("""
                <style>
                .rewritten-content {
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 20px;
                    background-color: #f9f9f9;
                    margin-top: 10px;
                    margin-bottom: 20px;
                }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown(f'<div class="rewritten-content">{st.session_state.rewritten_content}</div>', unsafe_allow_html=True)
            
            # Add a download button for rewritten content
            st.download_button(
                label="Download Rewritten Content",
                data=st.session_state.rewritten_content,
                file_name="seo_optimized_content.md",
                mime="text/markdown",
                key="download_button"
            )
            
elif optimize_button:
    st.error("Please provide both article content and a focus keyword.")



# Add a sidebar with information
with st.sidebar:
    st.header("About SEO Content Evaluator")
    st.markdown("""
    This tool evaluates your content based on SEO criteria, including:
    
    - Content length
    - Keyword density
    - Keyword distribution
    - Transition words
    - Sentence structure
    - Paragraph length
    - Internal/external links
    - Image usage
    - And more!
    
    The evaluation results are color-coded:
    - 🟢 **Green**: Good - meets the criteria
    - 🟠 **Orange**: Needs improvement
    - 🔴 **Red**: Poor - needs significant improvement
    
    Enter your content in the text area, provide a focus keyword, and click "Evaluate Content" to get started.
    """)
    
    st.markdown("---")
    
    st.header("AI Content Optimization")
    st.markdown("""
    This tool evaluates your content based on Yoast SEO criteria and automatically rewrites it to improve its SEO performance.
    
    The AI will analyze your content and generate a rewritten version that addresses any SEO issues while maintaining the original meaning and information.
    
    **How it works:**
    1. Enter your content and focus keyword
    2. Click the "Optimize" button
    3. Review the evaluation results and rewritten content
    4. Download the optimized content if needed
    
    This feature uses OpenAI's o3-mini model to provide high-quality SEO-optimized content.
    """)
    
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit and OpenAI's o3-mini model")
