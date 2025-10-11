# nlp_engine.py
import pandas as pd
from data_loader import load_hate_speech, load_terrorism, load_uploaded_dataset

# Optional: you can import transformers or other NLP libraries if needed
from transformers import pipeline

# Initialize a sentiment/risk pipeline
# You can replace this with a proper terrorism detection model
risk_pipeline = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

def calculate_risk(df, text_column='clean_text'):
    """Calculate risk scores for each post using a simple NLP model."""
    df = df.copy()
    risk_scores = []

    for text in df[text_column]:
        # For demo purposes, using a sentiment model to simulate risk
        try:
            result = risk_pipeline(text[:512])[0]  # limit text length
            score = result['score']
            if result['label'] == 'NEGATIVE':
                score = score
            else:
                score = 1 - score
        except Exception:
            score = 0.0
        risk_scores.append(score)

    df['risk_score'] = risk_scores
    df['risk_category'] = df['risk_score'].apply(categorize_risk)
    return df

def categorize_risk(score):
    """Categorize risk score into High, Moderate, Low."""
    if score >= 0.7:
        return "High"
    elif score >= 0.4:
        return "Moderate"
    else:
        return "Low"

def process_dataframe(df, text_column='text'):
    """Clean text column and calculate risk scores."""
    df = df.copy()
    if 'clean_text' not in df.columns:
        df['clean_text'] = df[text_column].astype(str).apply(lambda x: re.sub(r"http\S+|www\S+|https\S+", '', x))
        df['clean_text'] = df['clean_text'].str.replace(r'\W', ' ', regex=True).str.lower().str.strip()
    df = calculate_risk(df, text_column='clean_text')
    return df
