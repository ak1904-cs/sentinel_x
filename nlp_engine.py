from transformers import pipeline

# Load a sentiment / text classification pipeline
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

# Example lexicon for radicalization keywords
radical_keywords = ["attack", "bomb", "kill", "terror"]

def calculate_risk(text):
    """
    Calculate risk score for a given text.
    Returns a dictionary: risk_score (0-1), matched_keywords, label
    """
    # NLP classification
    result = classifier(text)[0]
    label = result['label']  # POSITIVE / NEGATIVE
    score = result['score']

    # Keyword matching
    matches = [word for word in radical_keywords if word in text.lower()]

    # Risk calculation (example)
    risk_score = min(1.0, score + 0.2 * len(matches))  # simple formula

    return {
        "risk_score": round(risk_score, 2),
        "keywords": matches,
        "label": label
    }
