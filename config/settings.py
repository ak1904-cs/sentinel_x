"""
Sentinel-X Configuration Settings
Centralized project configuration and configurable risk scoring weights.
"""
import os

# Project Root Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Text Processing & Limits
MAX_TEXT_LENGTH = 5000
DEFAULT_TEXT_COLUMN = "text"
ALTERNATIVE_TEXT_COLUMNS = ["clean_text", "text", "tweet", "summary", "body", "content", "message"]

# Video & Image OCR Settings
VIDEO_FRAME_INTERVAL = 30  # Analyze every Nth frame
MAX_VIDEO_FRAMES = 60      # Maximum frames per video
OCR_CONFIDENCE_THRESHOLD = 0.35
OCR_LANGUAGES = ['en']

# Configurable Risk Engine Weights (Sum should equal 1.0)
# These engineering weights can be tuned based on empirical testing.
RISK_WEIGHTS = {
    'THREAT_INDICATORS': 0.30,       # Keyword, lexicon, weapon indicator matches
    'CONTEXT_CLASSIFICATION': 0.30,  # ML signal probability (Hate Speech & Threat Classifiers)
    'ENTITY_SIGNALS': 0.20,         # High-risk named entities (Person, Org, Location)
    'PLANNING_INDICATORS': 0.20,     # Time + Location + Action planning pattern matches
}

# Risk Categories & Thresholds (Score 0-100)
RISK_THRESHOLDS = {
    'HIGH': 70.0,
    'MODERATE': 40.0,
}

# File Upload Limits (in MB)
FILE_LIMITS = {
    'MAX_CSV_MB': 50,
    'MAX_IMAGE_MB': 15,
    'MAX_VIDEO_MB': 100,
}

# NLP & Entity Recognition Settings
SPACY_MODEL = "en_core_web_sm"

# Logging Settings
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "sentinel_x.log")
LOG_LEVEL = "INFO"

# Data paths
DATA_DIR = os.path.join(BASE_DIR, "data")
HATE_SPEECH_CSV = os.path.join(DATA_DIR, "hate_speech.csv")
TERRORISM_CSV = os.path.join(DATA_DIR, "terrorism_small.csv")
