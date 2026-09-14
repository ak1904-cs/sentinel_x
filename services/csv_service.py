"""
CSV Processing Service for Sentinel-X.
Handles multi-encoding loading, gzipped CSV detection, column auto-discovery,
batch risk analysis execution, pagination, filtering, and exports.
"""
import pandas as pd
import io
from utils.text_utils import clean_text
from engines.risk_engine import calculate_explainable_risk
from config.settings import DEFAULT_TEXT_COLUMN, ALTERNATIVE_TEXT_COLUMNS
from utils.logging_utils import get_logger

logger = get_logger("csv_service")

def load_csv_file(uploaded_file) -> pd.DataFrame:
    """
    Safely load CSV file attempting multiple encodings and compression formats.
    """
    encodings = ["utf-8", "iso-8859-1", "latin1", "cp1252"]
    
    # Check if gzip compressed by magic bytes
    uploaded_file.seek(0)
    first_bytes = uploaded_file.read(2)
    uploaded_file.seek(0)
    is_gzip = (first_bytes == b'\x1f\x8b')
    
    for enc in encodings:
        try:
            uploaded_file.seek(0)
            if is_gzip:
                return pd.read_csv(uploaded_file, compression='gzip', encoding=enc, low_memory=False)
            else:
                return pd.read_csv(uploaded_file, encoding=enc, low_memory=False)
        except Exception:
            continue
            
    # Fallback to python engine ignoring bad lines
    uploaded_file.seek(0)
    return pd.read_csv(uploaded_file, engine="python", on_bad_lines="skip")

def detect_text_column(df: pd.DataFrame, user_col: str = None) -> str:
    """Detect or validate text column in DataFrame."""
    if user_col and user_col in df.columns:
        return user_col
    for col in ALTERNATIVE_TEXT_COLUMNS:
        if col in df.columns:
            return col
    # Fallback to first string/object column
    for col in df.columns:
        if df[col].dtype == object:
            return col
    return df.columns[0] if not df.empty else "text"

def process_csv_dataframe(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    """
    Run Sentinel-X NLP & Risk analysis on all rows of the DataFrame.
    Calculates risk_score, risk_category, threat_indicators, and entities.
    """
    if df.empty or text_column not in df.columns:
        return df

    processed_df = df.copy()
    processed_df["clean_text"] = processed_df[text_column].astype(str).apply(clean_text)

    risk_scores = []
    risk_categories = []
    threat_details_list = []
    entities_list = []

    for text in processed_df["clean_text"]:
        res = calculate_explainable_risk(text)
        risk_scores.append(res["risk_score"])
        risk_categories.append(res["risk_category"])
        
        # Summary of threat matches
        t_matches = res["threat_details"].get("threat_matches", []) + res["threat_details"].get("weapon_matches", [])
        threat_details_list.append(", ".join(t_matches) if t_matches else "None")
        
        # Summary of extracted entities
        ents = [e["text"] for e in res["entity_details"].get("entities", [])]
        entities_list.append(", ".join(set(ents)) if ents else "None")

    processed_df["risk_score"] = risk_scores
    processed_df["risk_category"] = risk_categories
    processed_df["threat_indicators"] = threat_details_list
    processed_df["detected_entities"] = entities_list

    return processed_df
