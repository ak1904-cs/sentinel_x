"""
Image Threat Analysis Service for Sentinel-X.
Processes uploaded images: runs OCR text extraction, executes unified threat and risk engine,
and returns packaged analytical results.
"""
from engines.ocr_engine import extract_text_from_image_bytes
from engines.risk_engine import calculate_explainable_risk
from utils.file_utils import save_temp_file, remove_temp_file

def process_uploaded_image(uploaded_image) -> dict:
    """Process uploaded image file and execute threat analysis."""
    uploaded_image.seek(0)
    image_bytes = uploaded_image.read()
    
    ocr_result = extract_text_from_image_bytes(image_bytes)
    extracted_text = ocr_result["extracted_text"]
    
    if not extracted_text.strip():
        return {
            "status": "no_text_found",
            "ocr_confidence": 0.0,
            "ocr_engine": ocr_result.get("engine", "none"),
            "extracted_text": "",
            "risk_analysis": calculate_explainable_risk("")
        }
        
    risk_analysis = calculate_explainable_risk(extracted_text)
    
    return {
        "status": "success",
        "ocr_confidence": ocr_result["confidence"],
        "ocr_engine": ocr_result["engine"],
        "extracted_text": extracted_text,
        "risk_analysis": risk_analysis
    }
