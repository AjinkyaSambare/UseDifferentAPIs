import streamlit as st
import requests
import os
from typing import Dict, Any
class AzureOpenAIChat:
    def __init__(self):
        self.API_ENDPOINT = st.secrets.get("AZURE_OPENAI_API_ENDPOINT", "")
        self.API_KEY = st.secrets.get("AZURE_OPENAI_API_KEY", "")

    def generate_response(self, query: str, max_tokens: int = 300) -> Dict[str, Any]:
        """Generate response from Azure OpenAI"""
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
        response = requests.post(self.API_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()  # Automatically raises an error for HTTP issues
        return response.json()

def main():
    st.set_page_config(page_title="Azure OpenAI Chat", page_icon="💬")
    st.title("Azure OpenAI GPT-4o Chat")

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat input
    if prompt := st.chat_input("Enter your message"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display "Generating response..." message
        with st.spinner("Generating response..."):
            # Generate AI response
            chat_client = AzureOpenAIChat()
            response = chat_client.generate_response(prompt)
            
            # Process and display the assistant's response
            if response and "choices" in response:
                full_response = response["choices"][0]["message"]["content"]
                with st.chat_message("assistant"):
                    st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                with st.chat_message("assistant"):
                    st.markdown("Sorry, I couldn't generate a response.")

if __name__ == "__main__":
    main()