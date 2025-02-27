import streamlit as st
import requests

# Streamlit Page Config
st.set_page_config(
    page_title="Speech-to-Text Using Whisper",
    page_icon="🎙️",
    layout="centered",
)

# App Header
st.title("Speech to Text using Whisper")
st.write("Upload an audio file to get its transcription using the Whisper API.")

# Sidebar explanation
with st.sidebar:
    st.header("📖 What is Whisper?")
    st.write("""
    Whisper is an automatic speech recognition (ASR) system developed by OpenAI. 
    It can transcribe audio into text and detect the spoken language in various audio formats.
    """)

    st.subheader("⚙️ How Whisper Works:")
    st.write("""
    - **Audio Input:** The model takes an audio file (e.g., .mp3, .wav) as input.
    - **Encoding:** The audio is converted into features using deep neural networks.
    - **Decoding:** Whisper predicts the most likely sequence of words by analyzing the audio features.
    - **Output:** It provides a transcribed text representation of the speech in the audio.
    """)

    st.info("Whisper is widely used for podcasts, meetings, and real-time speech-to-text conversion.")

# Input fields for the API endpoint and API key
api_url = st.secrets["api_url"]
api_key = st.secrets["api_key"]

# Upload audio file
uploaded_file = st.file_uploader("🎧 Upload an audio file (e.g., .mp3, .wav, .m4a)", type=["mp3", "wav", "m4a"])

if uploaded_file and api_key and api_url:
    st.write("### 🎵 Uploaded Audio Preview:")
    st.audio(uploaded_file, format="audio/wav")
    
    # Sending file to API
    with st.spinner("⏳ Transcribing audio... Please wait."):
        # API headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "api-key": api_key,
        }
        
        # Uploading the file to the API as a form-data POST request
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

        response = requests.post(api_url, headers=headers, files=files)

        # Display result
        if response.status_code == 200:
            result = response.json()
            st.success("✅ Transcription completed successfully!")
            st.write("### 📝 Transcribed Text:")
            st.text_area("Transcription Output", result.get("text", "No transcription available"), height=200)
        else:
            st.error(f"❌ Failed to transcribe. Status Code: {response.status_code}")
            st.write("**Error Details:**", response.text)