import requests
import base64
import io
from PIL import Image
import streamlit as st

class ImageGenerator:
    def __init__(self):
        self.API_ENDPOINT = "https://access-01.openai.azure.com/openai/deployments/dall-e-3/images/generations?api-version=2024-02-01"
        self.API_KEY = st.secrets.get("AZURE_DALLE_API_KEY", "")
    
    def generate_image(self, prompt, size="1024x1024", quality="standard", n=1):
        """
        Generate an image using DALL-E 3 API
        
        Args:
            prompt: Text description of the desired image
            size: Size of the generated image (1024x1024, 1792x1024, or 1024x1792)
            quality: Image quality ("standard" or "hd")
            n: Number of images to generate (1-10)
            
        Returns:
            List of image URLs or base64 data depending on response format
        """
        headers = {
            "Content-Type": "application/json",
            "api-key": self.API_KEY
        }
        
        payload = {
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n
        }
        
        try:
            response = requests.post(
                self.API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=60  # DALL-E generation can take time
            )
            response.raise_for_status()
            result = response.json()
            
            # Process response data
            # The exact structure depends on the API, but usually returns
            # either URLs or base64 encoded image data
            if "data" in result:
                return result["data"]
            return result
        except Exception as e:
            raise Exception(f"Image generation request failed: {str(e)}")

# Example usage in Streamlit
def add_image_generation_tab():
    st.header("Image Generation")
    st.markdown("Generate images based on text descriptions using DALL-E 3")
    
    # Text input for the image prompt
    prompt = st.text_area(
        "Describe the image you want to generate",
        height=100,
        placeholder="A serene landscape with mountains and a lake at sunset"
    )
    
    # Configuration options
    col1, col2 = st.columns(2)
    with col1:
        size = st.select_slider(
            "Image size",
            options=["1024x1024", "1792x1024", "1024x1792"],
            value="1024x1024"
        )
    with col2:
        quality = st.select_slider(
            "Image quality",
            options=["standard", "hd"],
            value="standard"
        )
    
    # Generate button
    if st.button("Generate Image") and prompt:
        with st.spinner("Generating your image..."):
            try:
                generator = ImageGenerator()
                result = generator.generate_image(prompt, size, quality)
                
                # Display the generated image(s)
                if result:
                    for i, img_data in enumerate(result):
                        if "url" in img_data:
                            st.image(img_data["url"], caption=f"Generated Image {i+1}")
                        elif "b64_json" in img_data:
                            # If response is base64 encoded
                            image_bytes = base64.b64decode(img_data["b64_json"])
                            image = Image.open(io.BytesIO(image_bytes))
                            st.image(image, caption=f"Generated Image {i+1}")
                        else:
                            st.warning("Unexpected response format")
                else:
                    st.warning("No images were generated")
            except Exception as e:
                st.error(f"Error generating image: {str(e)}")

# Example of how to add this to your Streamlit app
if __name__ == "__main__":
    st.title("AI Image Generator")
    add_image_generation_tab()