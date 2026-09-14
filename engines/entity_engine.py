"""
Named Entity Recognition (NER) and Normalization Engine for Sentinel-X.
Uses spaCy for actual NER (PERSON, ORG, GPE, LOC, DATE, EVENT) when available,
with graceful regex fallback if spaCy is not installed.
Applies entity normalization rules to standardize aliases for network graphing and risk analysis.
"""
import re
from collections import Counter
from utils.logging_utils import get_logger
from config.settings import SPACY_MODEL

logger = get_logger("entity_engine")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    SPACY_AVAILABLE = False

# Entity Normalization Map (Mapping aliases to standard canonical forms)
ENTITY_NORM_MAP = {
    "isis": "ISIS",
    "is": "ISIS",
    "daesh": "ISIS",
    "islamic state": "ISIS",
    "al-qaeda": "Al-Qaeda",
    "al qaeda": "Al-Qaeda",
    "al qaida": "Al-Qaeda",
    "hezbollah": "Hezbollah",
    "hamas": "Hamas",
    "boko haram": "Boko Haram",
    "taliban": "Taliban",
    "nyc": "New York",
    "new york city": "New York",
    "us": "United States",
    "usa": "United States",
    "united states of america": "United States",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "britain": "United Kingdom",
    "dc": "Washington D.C.",
    "washington dc": "Washington D.C."
}

# High-Risk Known Entity Set
HIGH_RISK_ENTITIES = {
    "ISIS", "Al-Qaeda", "Hezbollah", "Hamas", "Boko Haram", "Taliban",
    "Al-Shabaab", "Tehrik-i-Taliban", "Sinai Province"
}

class EntityNEREngine:
    def __init__(self):
        self.nlp = None
        self._load_spacy_model()

    def _load_spacy_model(self):
        if not SPACY_AVAILABLE:
            logger.warning("spaCy module not installed in environment. Using regex fallback entity extractor.")
            return

        try:
            self.nlp = spacy.load(SPACY_MODEL)
            logger.info(f"Loaded spaCy model '{SPACY_MODEL}' for NER.")
        except Exception:
            logger.warning(f"spaCy model '{SPACY_MODEL}' not found. Downloading via spacy...")
            try:
                spacy.cli.download(SPACY_MODEL)
                self.nlp = spacy.load(SPACY_MODEL)
                logger.info(f"Successfully downloaded and loaded spaCy model '{SPACY_MODEL}'.")
            except Exception as e:
                logger.error(f"Failed to load spaCy model: {e}. Falling back to basic regex entity extractor.")
                self.nlp = None

    def normalize_entity(self, entity_text: str) -> str:
        """Normalize entity text using canonical mapping rules."""
        if not entity_text:
            return ""
        clean_text = entity_text.strip()
        lower_text = clean_text.lower()
        if lower_text in ENTITY_NORM_MAP:
            return ENTITY_NORM_MAP[lower_text]
        return clean_text.title()

    def extract_entities(self, text: str) -> dict:
        """
        Extract named entities using spaCy NER or regex fallback.
        Categorizes entities into PERSON, ORG, GPE, LOC, DATE, EVENT.
        Returns detailed entity dictionary and summary lists.
        """
        if not isinstance(text, str) or not text.strip():
            return {"entities": [], "by_type": {}, "high_risk_entities": [], "entity_signal_score": 0.0}

        entities = []
        by_type = {"PERSON": [], "ORG": [], "GPE": [], "LOC": [], "DATE": [], "EVENT": []}
        high_risk_entities = []

        if self.nlp is not None:
            doc = self.nlp(text[:5000])  # Cap length for performance
            for ent in doc.ents:
                if ent.label_ in by_type:
                    norm_name = self.normalize_entity(ent.text)
                    if len(norm_name) > 1 and not norm_name.isdigit():
                        entities.append({"text": norm_name, "raw": ent.text, "label": ent.label_})
                        by_type[ent.label_].append(norm_name)
                        if norm_name in HIGH_RISK_ENTITIES:
                            high_risk_entities.append(norm_name)

        # Fallback regex extraction if spaCy is uninitialized or extracted nothing
        if not entities:
            # Capitalized words / phrases proxy
            caps = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            for cap in caps:
                norm_name = self.normalize_entity(cap)
                if len(norm_name) > 2 and norm_name.lower() not in {'the', 'this', 'that', 'with', 'from'}:
                    entities.append({"text": norm_name, "raw": cap, "label": "ORG"})
                    by_type["ORG"].append(norm_name)
                    if norm_name in HIGH_RISK_ENTITIES:
                        high_risk_entities.append(norm_name)

        # Deduplicate entity types
        for label in by_type:
            by_type[label] = list(set(by_type[label]))

        high_risk_entities = list(set(high_risk_entities))

        # Calculate Entity Signal Score (0.0 to 1.0)
        base_score = min(0.5, len(entities) * 0.05)
        high_risk_score = min(0.5, len(high_risk_entities) * 0.25)
        entity_signal_score = float(min(1.0, base_score + high_risk_score))

        return {
            "entities": entities,
            "by_type": by_type,
            "high_risk_entities": high_risk_entities,
            "entity_signal_score": entity_signal_score
        }

# Singleton Instance
_entity_engine_instance = None

def get_entity_engine() -> EntityNEREngine:
    global _entity_engine_instance
    if _entity_engine_instance is None:
        _entity_engine_instance = EntityNEREngine()
    return _entity_engine_instance
