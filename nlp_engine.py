# nlp_engine.py
import pandas as pd
from transformers import pipeline

# Initialize transformer pipeline (for demo, using sentiment-analysis)
# You can replace with a fine-tuned model for radicalization detection
nlp_model = pipeline("sentiment-analysis")

def calculate_risk(text):
    """
    Calculate risk score for a given text.
    Returns a float between 0 and 1.
    """
    if not text or not isinstance(text, str):
        return 0.0
    
    try:
        result = nlp_model(text[:512])[0]  # Limit to first 512 tokens
        label = result["label"]
        score = result["score"]
        
        # Simple heuristic for demo
        if label == "NEGATIVE":
            risk_score = score  # negative sentiment -> higher risk
        else:
            risk_score = 1 - score  # positive -> lower risk
        return round(risk_score, 2)
    
    except Exception as e:
        print(f"Error processing text: {e}")
        return 0.0

def process_dataframe(df, text_column="text"):
    """
    Process a DataFrame and add a risk_score column.
    """
    df = df.copy()
    if text_column not in df.columns:
        raise ValueError(f"Column '{text_column}' not found in DataFrame.")
    
    df["risk_score"] = df[text_column].apply(calculate_risk)
    
    # Categorize risk
    def categorize(score):
        if score >= 0.7:
            return "High"
        elif score >= 0.4:
            return "Moderate"
        else:
            return "Low"
    
    df["risk_category"] = df["risk_score"].apply(categorize)
    return df
