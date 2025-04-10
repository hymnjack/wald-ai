import streamlit as st
import sys
import os
import pandas as pd

# Add the path to the yoastevals.py file
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'yoastEvalsFinal', 'mainyoastfiles'))

# Import the evaluate_article function
from yoastevals import evaluate_article

# Set page config
st.set_page_config(
    page_title="Yoast SEO Evaluator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTextArea textarea {
        height: 400px;
    }
    .result-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .green-card {
        background-color: rgba(0, 128, 0, 0.1);
        border-left: 5px solid green;
    }
    .orange-card {
        background-color: rgba(255, 165, 0, 0.1);
        border-left: 5px solid orange;
    }
    .red-card {
        background-color: rgba(255, 0, 0, 0.1);
        border-left: 5px solid red;
    }
    .result-title {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .green-dot {
        color: green;
        font-size: 1.5rem;
    }
    .orange-dot {
        color: orange;
        font-size: 1.5rem;
    }
    .red-dot {
        color: red;
        font-size: 1.5rem;
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
    
    # Evaluate button
    evaluate_button = st.button("Evaluate Content", type="primary")

# Function to display results
def display_results(results):
    st.subheader("Evaluation Results")
    
    # Count scores for summary
    green_count = 0
    orange_count = 0
    red_count = 0
    
    # Display each criterion with colored text
    for criterion, score in results.items():
        # Count for summary
        if score == "Green":
            green_count += 1
            color = "green"
            emoji = "✅"
        elif score == "Orange":
            orange_count += 1
            color = "orange"
            emoji = "⚠️"
        elif score == "Red":
            red_count += 1
            color = "red"
            emoji = "❌"
        else:
            color = "black"
            emoji = "ℹ️"
        
        # Display criterion with colored text
        st.markdown(f"### {emoji} {criterion}")
        st.markdown(f"<span style='color:{color};font-weight:bold;'>{score}</span>", unsafe_allow_html=True)
        st.markdown("---")
    
    # Display score summary
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<p style="color:green; font-size:24px;">✅ Green: {green_count}</p>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<p style="color:orange; font-size:24px;">⚠️ Orange: {orange_count}</p>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<p style="color:red; font-size:24px;">❌ Red: {red_count}</p>', unsafe_allow_html=True)

# Run evaluation when button is clicked
if evaluate_button and article_content and focus_keyword:
    with st.spinner("Evaluating your content..."):
        # Run the evaluation
        results = evaluate_article(article_content, focus_keyword)
        
        # Display results in the second column
        with col2:
            display_results(results)
            
            # No additional table needed as results are already displayed as colored text
elif evaluate_button:
    st.error("Please provide both article content and a focus keyword.")

# Add a sidebar with information
with st.sidebar:
    st.header("About SEO Content Evaluator")
    st.markdown("""
    This tool evaluates your content based on Yoast SEO criteria, including:
    
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
    st.markdown("Made with ❤️ using Streamlit")
