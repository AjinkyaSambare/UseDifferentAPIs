import streamlit as st
import requests
import json
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import time
import os

# Set page configuration
st.set_page_config(
    page_title="Object Detection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API key from Streamlit secrets
API_KEY = st.secrets.get("GOOGLE_CLOUD_VISION_API_KEY", "")

# Custom CSS for a professional look
st.markdown("""
    <style>
        /* Main styling */
        .main {
            background-color: #F8F9FA;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #0A2647;
        }
        
        /* Container for results */
        .results-container {
            padding: 1.5rem;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        /* Progress bar */
        .stProgress > div > div {
            background-color: #144272;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #144272;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
        }
        
        .stButton > button:hover {
            background-color: #0A2647;
        }
        
        /* Info box */
        .info-box {
            background-color: #E5F6FD;
            border-left: 5px solid #144272;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Footer */
        .footer {
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #DEE2E6;
            text-align: center;
            color: #6C757D;
        }
    </style>
""", unsafe_allow_html=True)

def detect_objects_google_vision(image_bytes):
    """
    Detect objects in an image using Google Cloud Vision API
    """
    # Encode image to base64
    encoded_image = base64.b64encode(image_bytes).decode('UTF-8')
    
    # Prepare request to the Vision API
    url = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"
    
    request_data = {
        "requests": [
            {
                "image": {
                    "content": encoded_image
                },
                "features": [
                    {
                        "type": "OBJECT_LOCALIZATION",
                        "maxResults": 20
                    },
                    {
                        "type": "LABEL_DETECTION",
                        "maxResults": 10
                    }
                ]
            }
        ]
    }
    
    response = requests.post(url, json=request_data)
    return response.json()

def draw_bounding_boxes(image, vision_response):
    """
    Draw bounding boxes around detected objects
    """
    # Create a copy of the image to draw on
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    # Try to get a font
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    # Process object localizations if present
    if 'localizedObjectAnnotations' in vision_response['responses'][0]:
        objects = vision_response['responses'][0]['localizedObjectAnnotations']
        
        width, height = img.size
        
        # Color mapping for different object categories
        colors = {
            "Person": "#FF0000",        # Red
            "Vehicle": "#00FF00",       # Green
            "Animal": "#0000FF",        # Blue
            "Food": "#FFFF00",          # Yellow
            "Electronics": "#FF00FF",   # Magenta
            "Furniture": "#00FFFF",     # Cyan
            "Clothing": "#FFA500",      # Orange
            "Sports": "#800080",        # Purple
            "Building": "#A52A2A",      # Brown
        }
        
        default_color = "#FFFFFF"  # White for objects not in categories
        
        for obj in objects:
            # Get object category (or use the name if category not available)
            object_name = obj['name']
            
            # Determine color based on object name
            color = default_color
            for category, cat_color in colors.items():
                if category.lower() in object_name.lower():
                    color = cat_color
                    break
            
            # Get normalized vertices
            vertices = obj['boundingPoly']['normalizedVertices']
            
            # Convert normalized vertices to actual pixel coordinates
            box = [
                (vertices[0]['x'] * width, vertices[0]['y'] * height),
                (vertices[1]['x'] * width, vertices[1]['y'] * height),
                (vertices[2]['x'] * width, vertices[2]['y'] * height),
                (vertices[3]['x'] * width, vertices[3]['y'] * height)
            ]
            
            # Draw bounding box
            draw.line([box[0], box[1], box[2], box[3], box[0]], fill=color, width=3)
            
            # Draw label with confidence
            confidence = obj['score'] * 100
            label = f"{object_name}: {confidence:.1f}%"
            
            # Get text size to position it properly using the newer textbbox method
            left, top, right, bottom = draw.textbbox((0, 0), label, font=font)
            text_width = right - left
            text_height = bottom - top
            text_position = (box[0][0], box[0][1] - text_height - 5)
            
            # Draw label background
            draw.rectangle(
                [
                    text_position[0],
                    text_position[1],
                    text_position[0] + text_width,
                    text_position[1] + text_height
                ],
                fill=color
            )
            
            # Draw label text (white on colored background)
            draw.text(text_position, label, fill="#FFFFFF", font=font)
    
    return img

def main():
    # App title and description
    st.title("Advanced Object Detection System")
    
    # Check if API key is available in secrets
    if not API_KEY:
        st.error("""
            API key is missing! Please set up your secrets.toml file with:
            ```
            GOOGLE_CLOUD_VISION_API_KEY = "your-api-key-here"
            ```
        """)
        st.stop()
    
    # Sidebar with info about the application
    with st.sidebar:
        st.header("About")
        st.markdown("""
            <div class="info-box">
            This application uses Google Cloud Vision API to detect and locate objects in images. 
            It provides real-time analysis and visualization of detected objects with bounding boxes.
            
            <b>Common Use Cases:</b>
            - Autonomous vehicle perception
            - Retail inventory management
            - Manufacturing quality control
            - Security and surveillance
            - Augmented reality applications
            </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    st.header("Image Upload")
    uploaded_file = st.file_uploader("Upload an image for object detection", type=["jpg", "jpeg", "png"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if uploaded_file is not None:
            # Display original image
            image = Image.open(uploaded_file)
            st.image(image, caption="Original Image", use_container_width=True)
    
    # Process the image when user clicks the button
    if uploaded_file is not None and st.button("Detect Objects"):
        # Display spinner during processing
        with st.spinner("Processing image..."):
            # Read image bytes for API
            image_bytes = uploaded_file.getvalue()
            
            # Create a progress bar
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            try:
                # Call Google Vision API
                vision_response = detect_objects_google_vision(image_bytes)
                
                with col2:
                    # Draw bounding boxes on image
                    image = Image.open(uploaded_file)
                    annotated_image = draw_bounding_boxes(image, vision_response)
                    st.image(annotated_image, caption="Detected Objects", use_container_width=True)
                
                # Display detection results
                st.header("Detection Results")
                st.markdown('<div class="results-container">', unsafe_allow_html=True)
                
                if 'localizedObjectAnnotations' in vision_response['responses'][0]:
                    objects = vision_response['responses'][0]['localizedObjectAnnotations']
                    
                    # Create a table of detected objects
                    if objects:
                        data = []
                        for i, obj in enumerate(objects):
                            data.append({
                                "Object": obj['name'],
                                "Confidence": f"{obj['score']*100:.1f}%"
                            })
                        
                        st.table(data)
                        
                        # Show JSON result in expander
                        with st.expander("View Raw API Response"):
                            st.json(vision_response)
                    else:
                        st.warning("No objects were detected in the image.")
                else:
                    st.error("No object detection results returned from the API.")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
    
    # Display instructions when no image is uploaded
    if uploaded_file is None:
        st.info("""
            ### Instructions
            1. Upload an image using the file uploader above
            2. Click "Detect Objects" to analyze the image
            3. View the results with highlighted object bounding boxes
        """)
    
    # Footer
    st.markdown("""
        <div class="footer">
            Object Detection System • Powered by Google Cloud Vision API
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()