# data_loader.py
import pandas as pd
import re

def clean_text(text):
    """Clean text by removing URLs, non-alphanumeric characters, and converting to lowercase."""
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    text = re.sub(r'\W', ' ', text)
    return text.lower().strip()

def load_hate_speech():
    """Load and clean hate speech dataset."""
    df = pd.read_csv("data/hate_speech.csv")
    df['clean_text'] = df['tweet'].astype(str).apply(clean_text)
    return df

def load_terrorism():
    """Load and clean terrorism dataset."""
    df = pd.read_csv("data/terrorism_small.csv")
    df['clean_text'] = df['summary'].astype(str).apply(clean_text)
    return df

def load_uploaded_dataset(uploaded_file, text_column):
    """Load a user-uploaded CSV and clean the specified text column."""
    try:
        df = pd.read_csv(uploaded_file)
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in uploaded dataset.")
        df['clean_text'] = df[text_column].astype(str).apply(clean_text)
        return df
    except Exception as e:
        raise e
