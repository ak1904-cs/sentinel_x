"""
Text processing and cleaning utilities for Sentinel-X.
Preserves important OSINT signals such as URLs, mentions, hashtags, and numbers.
"""
import re
import unicodedata

# Regex patterns for signal extraction
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')
MENTION_PATTERN = re.compile(r'@\w+')
HASHTAG_PATTERN = re.compile(r'#\w+')
NUMBER_PATTERN = re.compile(r'\b\d+\b')

def normalize_unicode(text: str) -> str:
    """Normalize Unicode characters to standard NFKD form."""
    if not isinstance(text, str):
        return ""
    return unicodedata.normalize("NFKD", text)

def extract_text_signals(text: str) -> dict:
    """
    Extract OSINT signals (URLs, mentions, hashtags) from raw text before cleaning.
    """
    if not isinstance(text, str):
        return {"urls": [], "mentions": [], "hashtags": [], "clean_text": ""}
    
    text_norm = normalize_unicode(text)
    urls = URL_PATTERN.findall(text_norm)
    mentions = MENTION_PATTERN.findall(text_norm)
    hashtags = HASHTAG_PATTERN.findall(text_norm)
    
    return {
        "urls": urls,
        "mentions": mentions,
        "hashtags": hashtags,
        "raw_length": len(text_norm)
    }

def clean_text(text: str, preserve_signals: bool = True) -> str:
    """
    Clean and normalize raw text for NLP and threat engines.
    
    Args:
        text: Raw text string.
        preserve_signals: If True, keep hashtags and mentions in cleaned text.
    
    Returns:
        Cleaned lowercase string.
    """
    if not isinstance(text, str):
        return ""
    
    cleaned = normalize_unicode(text)
    # Remove URLs
    cleaned = URL_PATTERN.sub(' ', cleaned)
    
    if not preserve_signals:
        cleaned = MENTION_PATTERN.sub(' ', cleaned)
        cleaned = HASHTAG_PATTERN.sub(' ', cleaned)
    
    # Remove non-alphanumeric characters except spaces and @ #
    cleaned = re.sub(r'[^a-zA-Z0-9\s@#]', ' ', cleaned)
    
    # Collapse multiple whitespace characters
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()
    return cleaned

def tokenize_text(text: str) -> list:
    """Basic whitespace and punctuation tokenizer."""
    cleaned = clean_text(text)
    return [t for t in cleaned.split() if len(t) > 1]
