import re
import numpy as np
from transformers import pipeline

# Load a pre-trained model (zero-shot classification)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Simple keyword list
keywords = ["attack", "bomb", "kill", "revenge", "terror", "martyr", "war", "explode"]

def calculate_risk(text):
    # 1. Check keyword hits
    keyword_hits = sum([1 for k in keywords if k.lower() in text.lower()])
    keyword_score = min(keyword_hits / 5, 1.0)

    # 2. Use ML model for intent
    labels = ["hate_speech", "terrorism_intent", "neutral"]
    result = classifier(text, labels)
    ml_score = 1 - result["scores"][2]  # higher if not 'neutral'

    # 3. Combine
    risk_score = round(0.6 * ml_score + 0.4 * keyword_score, 2)
    return risk_score
