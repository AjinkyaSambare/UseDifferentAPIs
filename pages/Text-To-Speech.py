import requests
import streamlit as st
import tempfile
import os

def generate_speech(text, voice="alloy", response_format="mp3", speed=1.0):
    """
    Convert text to speech using Azure OpenAI's TTS endpoint
    """
    # Endpoint and key
    api_endpoint = "https://access-01.openai.azure.com/openai/deployments/tts/audio/speech?api-version=2024-05-01-preview"
    api_key = st.secrets.get("AZURE_OPENAI_API_KEY", "your-api-key-here")
    
    # Request headers and body
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": text,
        "voice": voice,
        "response_format": response_format,
        "speed": speed
    }
    
    # Create a temporary file to store the audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{response_format}")
    file_name = temp_file.name
    temp_file.close()
    
    try:
        # Make the API request
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=payload,
            stream=True,
            timeout=60
        )
        
        # Check for errors
        if response.status_code != 200:
            try:
                error_detail = response.json()
                error_message = error_detail.get('error', {}).get('message', f"Error {response.status_code}")
            except:
                error_message = f"Error {response.status_code}: {response.text}"
            raise Exception(error_message)
        
        # Write the audio data to the file
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        return file_name
    except Exception as e:
        # Clean up the temporary file if there's an error
        if os.path.exists(file_name):
            os.unlink(file_name)
        raise Exception(f"Speech generation failed: {str(e)}")

# Streamlit app
st.title("Text-to-Speech Generator")

# Text input
text_input = st.text_area(
    "Enter text to convert to speech",
    value="Hello, this is a test of the Azure OpenAI text-to-speech service.",
    height=150
)

# Voice options
col1, col2 = st.columns(2)

with col1:
    voice = st.selectbox(
        "Select voice",
        options=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        index=0
    )

with col2:
    speed = st.slider(
        "Speech speed",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1
    )

# Generate button
if st.button("Generate Speech"):
    with st.spinner("Generating speech..."):
        try:
            audio_path = generate_speech(
                text_input,
                voice=voice,
                speed=speed
            )
            
            # Read and display the audio
            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
            
            st.audio(audio_bytes, format="audio/mp3")
            
            # Option to download
            st.download_button(
                "Download Audio",
                data=audio_bytes,
                file_name=f"speech_{voice}.mp3",
                mime="audio/mp3"
            )
            
            # Clean up
            os.unlink(audio_path)
            
        except Exception as e:
            st.error(f"Error generating speech: {str(e)}")

# Voice descriptions
with st.expander("Voice Descriptions"):
    st.markdown("""
    * **Alloy** - Versatile, balanced voice
    * **Echo** - Clear, measured tone
    * **Fable** - Expressive storytelling voice
    * **Onyx** - Deep, authoritative voice
    * **Nova** - Warm, friendly female voice
    * **Shimmer** - Bright, enthusiastic voice
    """)