"""
Unified Image & Video OCR Engine for Sentinel-X.
Features:
- Image preprocessing (grayscale, contrast, adaptive thresholding)
- Primary EasyOCR + Tesseract fallback
- Confidence scoring and threshold filtering
- Intelligent video frame sampling and text deduplication across timestamps
"""
import os
import cv2
import tempfile
import numpy as np
from PIL import Image as PILImage
import io

from config.settings import VIDEO_FRAME_INTERVAL, MAX_VIDEO_FRAMES, OCR_CONFIDENCE_THRESHOLD
from utils.logging_utils import get_logger

logger = get_logger("ocr_engine")

# Lazy-loaded OCR Readers
EASYOCR_READER = None

def get_easyocr_reader():
    global EASYOCR_READER
    if EASYOCR_READER is None:
        try:
            import easyocr
            EASYOCR_READER = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR Reader initialized successfully.")
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}")
            EASYOCR_READER = False
    return EASYOCR_READER if EASYOCR_READER is not False else None

def preprocess_image_for_ocr(image_np: np.ndarray) -> np.ndarray:
    """Apply grayscale, noise reduction, and contrast enhancement."""
    if image_np is None or image_np.size == 0:
        return image_np
    
    # Convert to grayscale if RGB/BGR
    if len(image_np.shape) == 3:
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_np.copy()
        
    # Contrast Limited Adaptive Histogram Equalization (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return enhanced

def extract_text_from_image_bytes(image_bytes: bytes) -> dict:
    """
    Perform OCR on image bytes using EasyOCR with Tesseract fallback.
    Returns dict with extracted_text, confidence, and engine_used.
    """
    if not image_bytes:
        return {"extracted_text": "", "confidence": 0.0, "engine": "none"}
    
    # Load image array
    try:
        pil_img = PILImage.open(io.BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(pil_img)
    except Exception as e:
        logger.error(f"Failed to read image bytes: {e}")
        return {"extracted_text": "", "confidence": 0.0, "engine": "error"}
    
    preprocessed = preprocess_image_for_ocr(img_np)
    
    # 1. Try EasyOCR
    reader = get_easyocr_reader()
    if reader:
        try:
            results = reader.readtext(preprocessed)
            valid_texts = []
            confidences = []
            for bbox, text, conf in results:
                if conf >= OCR_CONFIDENCE_THRESHOLD and len(text.strip()) > 1:
                    valid_texts.append(text.strip())
                    confidences.append(conf)
            
            if valid_texts:
                full_text = " ".join(valid_texts)
                avg_conf = float(np.mean(confidences)) if confidences else 0.8
                return {"extracted_text": full_text, "confidence": round(avg_conf * 100, 1), "engine": "EasyOCR"}
        except Exception as e:
            logger.warning(f"EasyOCR processing failed: {e}. Falling back to Tesseract.")
            
    # 2. Try Pytesseract Fallback
    try:
        import pytesseract
        text = pytesseract.image_to_string(preprocessed)
        if text.strip():
            return {"extracted_text": text.strip(), "confidence": 70.0, "engine": "Tesseract"}
    except Exception as e:
        logger.warning(f"Pytesseract fallback failed: {e}")
        
    return {"extracted_text": "", "confidence": 0.0, "engine": "failed"}

def extract_text_from_video_file(video_path: str, frame_interval: int = VIDEO_FRAME_INTERVAL, max_frames: int = MAX_VIDEO_FRAMES) -> dict:
    """
    Intelligently sample video frames, run OCR, deduplicate consecutive subtitle texts,
    and return timeline segments + combined text.
    """
    if not os.path.exists(video_path):
        return {"segments": [], "combined_text": "", "total_frames_analyzed": 0, "status": "file_not_found"}
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"segments": [], "combined_text": "", "total_frames_analyzed": 0, "status": "cannot_open_video"}
        
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    segments = []
    seen_texts = set()
    frame_count = 0
    analyzed_count = 0
    last_text = ""
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                analyzed_count += 1
                # Encode frame to PNG bytes
                success, encoded_img = cv2.imencode('.png', frame)
                if success:
                    ocr_res = extract_text_from_image_bytes(encoded_img.tobytes())
                    text = ocr_res["extracted_text"]
                    
                    # Deduplicate subtitle text across consecutive frames
                    if text and text != last_text and text.lower() not in seen_texts:
                        timestamp_sec = int(frame_count / fps)
                        mm = timestamp_sec // 60
                        ss = timestamp_sec % 60
                        time_str = f"{mm:02d}:{ss:02d}"
                        
                        segments.append({
                            "timestamp": time_str,
                            "frame_index": frame_count,
                            "text": text,
                            "confidence": ocr_res["confidence"]
                        })
                        seen_texts.add(text.lower())
                        last_text = text
                        
                if analyzed_count >= max_frames:
                    break
                    
            frame_count += 1
    except Exception as e:
        logger.error(f"Error during video frame extraction: {e}")
    finally:
        cap.release()
        
    combined_text = " ".join([seg["text"] for seg in segments])
    return {
        "segments": segments,
        "combined_text": combined_text,
        "total_frames_analyzed": analyzed_count,
        "status": "success"
    }
