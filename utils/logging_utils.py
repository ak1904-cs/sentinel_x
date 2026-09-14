"""
Structured logging module for Sentinel-X.
Logs operation audits, performance metrics, and technical errors without storing sensitive user text payloads.
"""
import os
import logging
from config.settings import LOG_FILE, LOG_DIR, LOG_LEVEL

def get_logger(name: str = "sentinel_x") -> logging.Logger:
    """Return a configured Logger instance."""
    os.makedirs(LOG_DIR, exist_ok=True)
    
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Already configured
    
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # File Handler
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Stream Handler (console)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(file_formatter)
    logger.addHandler(stream_handler)
    
    return logger
