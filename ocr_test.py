import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import pytesseract
import cv2

st.set_page_config(page_title="🧠 Sentinel-X OCR Module", layout="centered")
st.title("🧠 Sentinel-X OCR Test Module")

# -------------------------------
# Load EasyOCR Reader (CPU)
# -------------------------------
@st.cache_resource(show_spinner=True)
def load_reader_safe():
    try:
        return easyocr.Reader(['en'], gpu=False)
    except Exception as e:
        st.error(f"Failed to load EasyOCR Reader: {e}")
        return None

reader = load_reader_safe()

# -------------------------------
# OCR extraction function with fallback
# -------------------------------
def extract_text_with_fallback(image_np):
    # Try EasyOCR first
    if reader:
        try:
            results = reader.readtext(image_np)
            if results:
                # Combine all detected text
                return " ".join([text for (_, text, _) in results])
        except Exception:
            st.warning("EasyOCR failed, falling back to pytesseract.")

    # Fallback to pytesseract
    try:
        img_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        text = pytesseract.image_to_string(img_bgr)
        return text if text.strip() else "⚠️ No text extracted by pytesseract."
    except Exception as e:
        return f"❌ OCR failed completely: {e}"

# -------------------------------
# File uploader
# -------------------------------
uploaded_file = st.file_uploader("📤 Upload an Image (JPG / PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Convert image to NumPy array
    image_np = np.array(image)

    # OCR extraction
    st.info("Extracting text... please wait ⏳")
    extracted_text = extract_text_with_fallback(image_np)

    # Display results
    if extracted_text.strip() and "No text" not in extracted_text:
        st.success("✅ Text extracted successfully:")
        st.write(extracted_text)
    else:
        st.warning(extracted_text)
else:
    st.write("Please upload an image to begin.")
