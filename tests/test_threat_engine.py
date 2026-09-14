"""
Unit tests for engines/threat_engine.py using standard unittest
"""
import unittest
from engines.threat_engine import analyze_threat_indicators

class TestThreatEngine(unittest.TestCase):
    def test_threat_keyword_detection(self):
        text = "Terrorists plan a car bomb attack with C4 explosives."
        res = analyze_threat_indicators(text)
        self.assertGreater(res["threat_score"], 0.4)
        self.assertTrue(len(res["threat_matches"]) > 0 or len(res["weapon_matches"]) > 0)

    def test_planning_pattern_detection(self):
        text = "Attack scheduled for tomorrow at 5pm near the embassy."
        res = analyze_threat_indicators(text)
        self.assertTrue(res["planning_detected"])
        self.assertGreater(len(res["planning_details"]["location_signals"]), 0)

if __name__ == "__main__":
    unittest.main()
