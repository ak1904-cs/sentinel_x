"""
Unit tests for engines/entity_engine.py using standard unittest
"""
import unittest
from engines.entity_engine import get_entity_engine

class TestEntityEngine(unittest.TestCase):
    def test_entity_extraction_and_normalization(self):
        engine = get_entity_engine()
        text = "ISIS leaders met in New York City with members of Al-Qaeda."
        res = engine.extract_entities(text)
        self.assertTrue(len(res["high_risk_entities"]) > 0 or len(res["entities"]) > 0)
        self.assertGreater(res["entity_signal_score"], 0.0)

if __name__ == "__main__":
    unittest.main()
