import requests
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def research(query):
    url = "https://chat-api.you.com/research"
    
    # Get API key from environment variable
    api_key = os.getenv('YOU_API_KEY', st.secrets["YOU_API_KEY"])
    chat_id = os.getenv('CHAT_ID', st.secrets["CHAT_ID"])

    payload = {
        "query": query,
        "chat_id": chat_id
    }
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    return response.json()

# Streamlit UI with some styling
st.set_page_config(
    page_title="You.com Research API",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 You.com Research API Tester")
st.write("Enter your query below to test the You.com Research API")

# Create input field for query
user_query = st.text_input("Enter your research query:", placeholder="Type your query here...")

# Create columns for better layout
col1, col2, col3 = st.columns([1, 2, 1])

# Center the button using columns
with col2:
    if st.button("🚀 Search", use_container_width=True):
        if user_query:
            with st.spinner('Searching...'):
                try:
                    result = research(user_query)
                    st.json(result)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("⚠️ Please enter a query first!")