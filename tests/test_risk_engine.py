"""
Unit tests for engines/risk_engine.py using standard unittest
"""
import unittest
from engines.risk_engine import calculate_explainable_risk

class TestRiskEngine(unittest.TestCase):
    def test_high_risk_calculation(self):
        text = "ISIS sleeper cell planning an AK-47 attack tomorrow near the embassy in New York."
        res = calculate_explainable_risk(text)
        self.assertGreaterEqual(res["risk_score"], 40.0)
        self.assertIn(res["risk_category"], ["High", "Moderate"])
        self.assertGreater(len(res["reasons"]), 0)

    def test_low_risk_calculation(self):
        text = "Beautiful sunny morning in Central Park having coffee."
        res = calculate_explainable_risk(text)
        self.assertLess(res["risk_score"], 40.0)
        self.assertEqual(res["risk_category"], "Low")

if __name__ == "__main__":
    unittest.main()
