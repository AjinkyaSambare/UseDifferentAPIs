import streamlit as st
import requests
import json

# Hardcoded API key - replace with your actual Google Translate API key
API_KEY = st.secrets.get("Google_Translation_Key", "")

def translate_text(text, target_language, source_language='auto'):
    url = "https://translation.googleapis.com/language/translate/v2"
    # Only include source if not auto-detect
    payload = {
        'q': text,
        'target': target_language,
        'key': API_KEY
    }
    # Only add source parameter if not set to auto
    if source_language != 'auto':
        payload['source'] = source_language
    
    response = requests.post(url, params=payload)
    if response.status_code == 200:
        return response.json()['data']['translations'][0]['translatedText']
    else:
        return f"Error: {response.text}"

def main():
    st.title("Real-Time Language Translator")
    
    input_text = st.text_area("Input text:", height=150)
    
    languages = {
        'English': 'en', 'Spanish': 'es', 'French': 'fr', 'German': 'de',
        'Italian': 'it', 'Portuguese': 'pt', 'Russian': 'ru', 'Japanese': 'ja',
        'Korean': 'ko', 'Chinese (Simplified)': 'zh', 'Arabic': 'ar'
    }
    
    source_lang = st.selectbox("Source Language (or auto-detect):", ['Auto-detect'] + list(languages.keys()))
    target_lang = st.selectbox("Target Language:", list(languages.keys()))
    
    if st.button("Translate"):
        if not input_text:
            st.warning("Please enter text to translate")
        else:
            with st.spinner("Translating..."):
                source_code = 'auto' if source_lang == 'Auto-detect' else languages[source_lang]
                translated_text = translate_text(
                    input_text,
                    target_language=languages[target_lang],
                    source_language=source_code
                )
                
                st.success("Translation Complete!")
                st.write("### Translated Text:")
                st.write(translated_text)

if __name__ == "__main__":
    main()