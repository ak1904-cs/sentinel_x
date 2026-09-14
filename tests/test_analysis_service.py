"""
Unit tests for services/analysis_service.py using standard unittest
"""
import unittest
from models.analysis_models import AnalysisInput
from services.analysis_service import analyze_input_payload
from services.case_service import get_all_cases

class TestAnalysisService(unittest.TestCase):
    def test_high_risk_auto_case_creation(self):
        payload = AnalysisInput(
            source_type="text",
            content="URGENT: Cell meeting tomorrow at 22:00 near embassy with AK-47 rifles and C4 explosives."
        )
        res = analyze_input_payload(payload)
        self.assertGreaterEqual(res.risk_score, 40.0)
        self.assertIn(res.risk_category, ["High", "Moderate"])
        
        # Verify auto-case generation
        cases = get_all_cases()
        matched = [c for c in cases if c.analysis_id == res.analysis_id]
        self.assertEqual(len(matched), 1)

if __name__ == "__main__":
    unittest.main()
