"""
NLP Classifier Engine for Sentinel-X.
Implements TF-IDF + Logistic Regression classifiers for specialized text signals:
1. Hate Speech / Abusive Content Classifier (trained on data/hate_speech.csv)
2. Threat / Radicalization Signal Estimator
"""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

from utils.text_utils import clean_text
from config.settings import HATE_SPEECH_CSV, TERRORISM_CSV, BASE_DIR
from utils.logging_utils import get_logger

logger = get_logger("nlp_engine")

MODEL_DIR = os.path.join(BASE_DIR, "data", "models")

class ThreatNLPEngine:
    def __init__(self):
        self.hate_vectorizer = None
        self.hate_classifier = None
        self.is_trained = False
        os.makedirs(MODEL_DIR, exist_ok=True)
        self.model_path = os.path.join(MODEL_DIR, "hate_speech_tfidf_logreg.joblib")
    
    def train_hate_speech_model(self, data_path: str = HATE_SPEECH_CSV) -> dict:
        """
        Train TF-IDF + Logistic Regression model on hate_speech.csv.
        Class 0: Hate speech, Class 1: Offensive, Class 2: Neither
        Returns performance evaluation metrics (Accuracy, Precision, Recall, F1).
        """
        if not os.path.exists(data_path):
            logger.warning(f"Dataset path {data_path} not found. Skipping offline training.")
            return {}
        
        logger.info(f"Loading hate speech dataset from {data_path}...")
        df = pd.read_csv(data_path)
        
        if 'tweet' not in df.columns or 'class' not in df.columns:
            raise ValueError("Invalid hate speech dataset format. Missing 'tweet' or 'class' columns.")
        
        df['clean_text'] = df['tweet'].astype(str).apply(clean_text)
        
        X = df['clean_text']
        y = df['class']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        logger.info("Extracting TF-IDF features...")
        self.hate_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')
        X_train_vec = self.hate_vectorizer.fit_transform(X_train)
        X_test_vec = self.hate_vectorizer.transform(X_test)
        
        logger.info("Training Logistic Regression classifier...")
        self.hate_classifier = LogisticRegression(max_iter=1000, C=1.0, class_weight='balanced')
        self.hate_classifier.fit(X_train_vec, y_train)
        
        # Evaluation
        y_pred = self.hate_classifier.predict(X_test_vec)
        acc = accuracy_score(y_test, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
        
        metrics = {
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1_score": float(f1),
            "total_samples": len(df),
            "test_samples": len(y_test)
        }
        
        logger.info(f"Model trained successfully. Accuracy: {acc:.4f}, F1-Score: {f1:.4f}")
        
        # Save model artifacts
        joblib.dump({"vectorizer": self.hate_vectorizer, "classifier": self.hate_classifier, "metrics": metrics}, self.model_path)
        self.is_trained = True
        return metrics

    def load_or_train(self) -> dict:
        """Load trained model from disk or train if missing."""
        if os.path.exists(self.model_path):
            try:
                data = joblib.load(self.model_path)
                self.hate_vectorizer = data["vectorizer"]
                self.hate_classifier = data["classifier"]
                self.is_trained = True
                logger.info("Loaded pre-trained TF-IDF model from disk.")
                return data.get("metrics", {})
            except Exception as e:
                logger.error(f"Failed to load cached model: {e}. Retraining...")
        
        return self.train_hate_speech_model()

    def predict_hate_probability(self, text: str) -> float:
        """
        Predict probability of hate speech / abusive signal (0.0 to 1.0).
        """
        if not self.is_trained or not self.hate_vectorizer or not self.hate_classifier:
            self.load_or_train()
            if not self.is_trained:
                return 0.0
        
        cleaned = clean_text(text)
        if not cleaned:
            return 0.0
        
        vec = self.hate_vectorizer.transform([cleaned])
        probs = self.hate_classifier.predict_proba(vec)[0]
        # Classes: 0=Hate, 1=Offensive, 2=Neither
        # Higher weight on Class 0 (Hate) + partial on Class 1 (Offensive)
        hate_prob = probs[0] + 0.4 * probs[1]
        return float(np.clip(hate_prob, 0.0, 1.0))

# Global Engine Singleton
_nlp_engine_instance = None

def get_nlp_engine() -> ThreatNLPEngine:
    global _nlp_engine_instance
    if _nlp_engine_instance is None:
        _nlp_engine_instance = ThreatNLPEngine()
        _nlp_engine_instance.load_or_train()
    return _nlp_engine_instance
