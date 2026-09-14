"""
File handling and security validation utilities for Sentinel-X.
"""
import os
import tempfile
from config.settings import FILE_LIMITS

ALLOWED_EXTENSIONS = {
    'csv': ['csv'],
    'image': ['png', 'jpg', 'jpeg', 'bmp', 'webp'],
    'video': ['mp4', 'mov', 'avi', 'mkv']
}

def get_file_type_category(filename: str) -> str:
    """Determine file category based on extension."""
    if not filename or '.' not in filename:
        return 'unknown'
    ext = filename.rsplit('.', 1)[1].lower()
    for cat, exts in ALLOWED_EXTENSIONS.items():
        if ext in exts:
            return cat
    return 'unknown'

def validate_file_upload(uploaded_file) -> tuple[bool, str]:
    """
    Validate uploaded file extension and size limits.
    Returns (is_valid, error_message).
    """
    if uploaded_file is None:
        return False, "No file uploaded."
    
    filename = uploaded_file.name
    category = get_file_type_category(filename)
    if category == 'unknown':
        return False, f"Unsupported file type for '{filename}'. Allowed: CSV, PNG, JPG, MP4, MOV."
    
    # Size check
    uploaded_file.seek(0, os.SEEK_END)
    size_mb = uploaded_file.tell() / (1024 * 1024)
    uploaded_file.seek(0)
    
    limit_key = f"MAX_{category.upper()}_MB"
    max_limit = FILE_LIMITS.get(limit_key, 50)
    
    if size_mb > max_limit:
        return False, f"File size ({size_mb:.1f} MB) exceeds maximum limit of {max_limit} MB."
    
    return True, "Valid file."

def save_temp_file(uploaded_file, suffix: str = "") -> str:
    """Safely save uploaded Streamlit file to a temporary file path."""
    uploaded_file.seek(0)
    ext = f".{uploaded_file.name.rsplit('.', 1)[1]}" if '.' in uploaded_file.name else suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tf:
        tf.write(uploaded_file.read())
        return tf.name

def remove_temp_file(filepath: str):
    """Safely remove temporary file."""
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass
