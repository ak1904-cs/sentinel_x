"""
Image Threat Analysis Service for Sentinel-X.
Processes uploaded images: runs OCR text extraction, routes through central Analysis Service,
and returns packaged analytical results.
"""
from engines.ocr_engine import extract_text_from_image_bytes
from models.analysis_models import AnalysisInput
from services.analysis_service import analyze_input_payload

def process_uploaded_image(uploaded_image) -> dict:
    """Process uploaded image file and execute threat analysis."""
    uploaded_image.seek(0)
    image_bytes = uploaded_image.read()
    
    ocr_result = extract_text_from_image_bytes(image_bytes)
    extracted_text = ocr_result["extracted_text"]
    
    input_payload = AnalysisInput(
        source_type="image",
        content=extracted_text,
        url_or_reference=uploaded_image.name,
        media_type="image/png",
        metadata={"ocr_confidence": ocr_result["confidence"], "ocr_engine": ocr_result["engine"]}
    )
    
    analysis_res = analyze_input_payload(input_payload)
    
    return {
        "status": "success" if extracted_text.strip() else "no_text_found",
        "ocr_confidence": ocr_result["confidence"],
        "ocr_engine": ocr_result["engine"],
        "extracted_text": extracted_text,
        "analysis_result": analysis_res,
        "risk_analysis": {
            "risk_score": analysis_res.risk_score,
            "risk_category": analysis_res.risk_category,
            "components": analysis_res.components,
            "reasons": analysis_res.reasons,
            "threat_details": analysis_res.threat_details,
            "entity_details": analysis_res.entity_details
        }
    }
