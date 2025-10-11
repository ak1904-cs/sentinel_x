import streamlit as st
import easyocr
from PIL import Image
import numpy as np

st.title("🧠 Sentinel-X OCR Test Module")

# Initialize EasyOCR Reader once
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

# Upload Image
uploaded_file = st.file_uploader("📤 Upload an Image (JPG / PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Convert image to array
    image_np = np.array(image)

    # OCR extraction
    st.info("Extracting text using EasyOCR... please wait ⏳")
    results = reader.readtext(image_np)

    if results:
        st.success("✅ Text extracted successfully:")
        for (bbox, text, prob) in results:
            st.write(f"**{text}** (Confidence: {prob:.2f})")
    else:
        st.warning("⚠️ No readable text found in the image.")
else:
    st.write("Please upload an image to begin.")
