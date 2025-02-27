import streamlit as st
import time
import requests
import json
import os

class AzureOpenAISummarizer:
    def __init__(self):
        # Get the API endpoint and key from Streamlit secrets - exactly like your chat app
        self.API_ENDPOINT = st.secrets.get("AZURE_OPENAI_API_ENDPOINT", "")
        self.API_KEY = st.secrets.get("AZURE_OPENAI_API_KEY", "")
    
    def generate_response(self, query, max_tokens=1000, max_retries=3):
        """Generate response from Azure OpenAI with retry logic"""
        headers = {
            "Content-Type": "application/json",
            "api-key": self.API_KEY,
        }
        data = {
            "messages": [{"role": "user", "content": query}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.API_ENDPOINT, 
                    headers=headers, 
                    json=data,
                    timeout=60  # Increase timeout to 60 seconds
                )
                response.raise_for_status()
                return response.json()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries - 1:
                    # Wait with exponential backoff before retrying
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise Exception(f"Failed after {max_retries} attempts: {str(e)}")
    
    def summarize_text(self, text, length_option, audience, target_reduction=None):
        # Create the prompt for summarization with improved reduction guidance
        length_map = {
            "Very Brief": {
                "description": "1 paragraph (3-4 sentences)",
                "target_reduction": 85
            },
            "Brief": {
                "description": "1-2 paragraphs",
                "target_reduction": 75
            },
            "Moderate": {
                "description": "2-3 paragraphs",
                "target_reduction": 60
            },
            "Detailed": {
                "description": "3-4 paragraphs",
                "target_reduction": 50
            }
        }
        
        # Use custom target reduction if provided, otherwise use default
        reduction_target = target_reduction if target_reduction else length_map[length_option]["target_reduction"]
        
        # Build the summarization prompt with specific reduction targets
        prompt = f"""You are an expert summarizer. Create a highly concise {length_map[length_option]["description"]} summary of the following text.
        Your summary should be approximately {reduction_target}% shorter than the original text.
        Target the summary for a {audience.lower()} audience.
        Focus ONLY on the most essential ideas and key findings.
        Eliminate all redundancy and unnecessary details.
        Use concise language and efficient phrasing.
        Maintain factual accuracy while being extremely selective about what to include.
        
        Here is the text to summarize:
        {text}
        """
        
        # Use the same method as your chat app to get a response
        response = self.generate_response(prompt)
        
        # Extract the summary from the response
        if response and "choices" in response:
            summary = response["choices"][0]["message"]["content"]
            return summary
        else:
            raise Exception("Failed to generate a summary")


# Page configuration
st.set_page_config(
    page_title="Document Summarization System",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            background-color: #f5f7f9;
        }
        
        .stTextArea textarea {
            border-radius: 4px;
            border: 1px solid #E0E5EC;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #1E3A8A;
        }
        
        /* Progress bar */
        .stProgress > div > div {
            background-color: #1E3A8A;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #1E3A8A;
            color: white;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            border: none;
        }
        
        .stButton > button:hover {
            background-color: #152b63;
        }
        
        /* Info box */
        .info-container {
            background-color: #EFF6FF;
            padding: 1.5rem;
            border-radius: 4px;
            border-left: 5px solid #1E3A8A;
            margin: 1rem 0;
        }
        
        /* Results container */
        .results-container {
            background-color: white;
            padding: 1.5rem;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        /* Select boxes */
        .stSelectbox div[data-baseweb="select"] div:first-child {
            background-color: white;
            border-radius: 4px;
        }
    </style>
""", unsafe_allow_html=True)

# Application title
st.title("Document Summarization System")
st.markdown("Transform lengthy documents into concise summaries for faster comprehension")

# Sidebar options
with st.sidebar:
    st.header("Summary Options")
    summary_length = st.select_slider(
        "Summary Length",
        options=["Very Brief", "Brief", "Moderate", "Detailed"],
        value="Brief"
    )
    
    audience = st.selectbox(
        "Target Audience",
        ["General", "Academic", "Technical", "Business"],
        index=0
    )
    
    # Add custom reduction target slider
    custom_reduction = st.slider(
        "Target Reduction Percentage",
        min_value=30,
        max_value=90,
        value=75,
        step=5,
        help="Higher values produce more concise summaries"
    )
    
    st.markdown("""
    <div class="info-container">
        <h4>About this tool</h4>
        <p>This application uses Azure OpenAI to generate concise summaries of long documents or articles. 
        Ideal for students, researchers, and professionals who need to quickly understand key information from extensive texts.</p>
    </div>
    """, unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([3, 2])

with col1:
    text_input = st.text_area("Paste your document or article here:", height=300)
    
    # Add a unique key to each button
    if st.button("Generate Summary", key="generate_summary_btn") and text_input:
        try:
            # Initialize summarizer
            summarizer = AzureOpenAISummarizer()
            
            # Create a progress bar
            with st.spinner("Analyzing document content..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                # Get summary with the custom reduction target
                summary = summarizer.summarize_text(text_input, summary_length, audience, custom_reduction)
                
                # Display summary
                with col2:
                    st.markdown('<div class="results-container">', unsafe_allow_html=True)
                    st.subheader("Summary")
                    st.write(summary)
                    
                    # Metadata
                    st.markdown("---")
                    mcol1, mcol2, mcol3 = st.columns(3)
                    with mcol1:
                        st.metric("Original Length", f"{len(text_input)} chars")
                    with mcol2:
                        st.metric("Summary Length", f"{len(summary)} chars")
                    with mcol3:
                        reduction = int((1 - len(summary)/len(text_input)) * 100)
                        st.metric("Reduction", f"{reduction}%")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
        except ValueError as ve:
            st.error(f"Configuration Error: {str(ve)}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    # Use a different key for this button
    elif st.button("Generate Summary", key="empty_text_btn") and not text_input:
        st.warning("Please enter some text to summarize")

# Display instructions when no text is entered
if not text_input:
    with col2:
        st.markdown("""
        <div class="info-container">
            <h3>How to use</h3>
            <ol>
                <li>Paste the document you want to summarize in the text area</li>
                <li>Adjust summary preferences in the sidebar</li>
                <li>Set your desired reduction percentage</li>
                <li>Click "Generate Summary" to process your document</li>
            </ol>
            
            <h4>Best Practices</h4>
            <ul>
                <li>For optimal results, ensure text is well-formatted</li>
                <li>Documents with clear structure yield better summaries</li>
                <li>Higher reduction rates work best with longer documents</li>
                <li>Specialized technical content works best with the "Technical" audience setting</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6B7280; padding: 1rem 0;">
        Powered by Azure OpenAI • Document Summarization System
    </div>
""", unsafe_allow_html=True)