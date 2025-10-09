import pandas as pd
import re

def clean_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    text = re.sub(r'\W', ' ', text)
    return text.lower().strip()

def load_hate_speech():
    df = pd.read_csv("data/hate_speech.csv")
    df['clean_text'] = df['tweet'].astype(str).apply(clean_text)
    return df

def load_terrorism():
    df = pd.read_csv("data/terrorism.csv")
    df['clean_text'] = df['summary'].astype(str).apply(clean_text)
    return df
