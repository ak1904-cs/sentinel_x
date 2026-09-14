"""
Video Threat Analysis Service for Sentinel-X.
Processes uploaded video files: samples video frames, runs OCR text extraction with frame-to-frame
text deduplication, creates timestamped timeline, and routes through central Analysis Service.
"""
from engines.ocr_engine import extract_text_from_video_file
from models.analysis_models import AnalysisInput
from services.analysis_service import analyze_input_payload
from utils.file_utils import save_temp_file, remove_temp_file

def process_uploaded_video(uploaded_video) -> dict:
    """Process uploaded video file and execute timeline threat analysis."""
    temp_path = save_temp_file(uploaded_video, suffix=".mp4")
    
    try:
        ocr_result = extract_text_from_video_file(temp_path)
    finally:
        remove_temp_file(temp_path)
        
    combined_text = ocr_result.get("combined_text", "")
    
    input_payload = AnalysisInput(
        source_type="video",
        content=combined_text,
        url_or_reference=uploaded_video.name,
        media_type="video/mp4",
        metadata={"frames_analyzed": ocr_result.get("total_frames_analyzed", 0)}
    )
    
    analysis_res = analyze_input_payload(input_payload)
    
    return {
        "status": "success" if combined_text.strip() else "no_text_found",
        "frames_analyzed": ocr_result.get("total_frames_analyzed", 0),
        "timeline_segments": ocr_result.get("segments", []),
        "combined_text": combined_text,
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
