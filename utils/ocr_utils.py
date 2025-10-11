import easyocr
import pytesseract
from PIL import Image

# Initialize EasyOCR reader once
reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(image_path):
    """Try EasyOCR first, fallback to pytesseract."""
    try:
        result = reader.readtext(image_path, detail=0)
        text = " ".join(result)
        if not text.strip():
            # fallback
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"OCR failed: {e}")
        return ""
