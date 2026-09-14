"""
Video Threat Analysis Service for Sentinel-X.
Processes uploaded video files: samples video frames, runs OCR text extraction with frame-to-frame
text deduplication, creates timestamped timeline, and evaluates overall risk.
"""
from engines.ocr_engine import extract_text_from_video_file
from engines.risk_engine import calculate_explainable_risk
from utils.file_utils import save_temp_file, remove_temp_file

def process_uploaded_video(uploaded_video) -> dict:
    """Process uploaded video file and execute timeline threat analysis."""
    temp_path = save_temp_file(uploaded_video, suffix=".mp4")
    
    try:
        ocr_result = extract_text_from_video_file(temp_path)
    finally:
        remove_temp_file(temp_path)
        
    combined_text = ocr_result.get("combined_text", "")
    if not combined_text.strip():
        return {
            "status": "no_text_found",
            "frames_analyzed": ocr_result.get("total_frames_analyzed", 0),
            "timeline_segments": [],
            "combined_text": "",
            "risk_analysis": calculate_explainable_risk("")
        }
        
    risk_analysis = calculate_explainable_risk(combined_text)
    
    return {
        "status": "success",
        "frames_analyzed": ocr_result.get("total_frames_analyzed", 0),
        "timeline_segments": ocr_result.get("segments", []),
        "combined_text": combined_text,
        "risk_analysis": risk_analysis
    }
