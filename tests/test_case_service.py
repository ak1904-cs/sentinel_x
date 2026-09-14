"""
Unit tests for services/case_service.py using standard unittest
"""
import unittest
import uuid
from models.case_models import CaseRecord, CasePriority, CaseStatus
from storage.repository import save_case
from services.case_service import get_all_cases, escalate_case, dismiss_case, add_case_note

class TestCaseService(unittest.TestCase):
    def setUp(self):
        self.case_id = f"SX-TEST-{uuid.uuid4().hex[:4]}"
        self.case = CaseRecord(
            case_id=self.case_id,
            analysis_id="AN-123",
            title="Test Case",
            source_type="text",
            risk_score=85.0,
            priority=CasePriority.HIGH,
            status=CaseStatus.NEW,
            assigned_analyst="TestAnalyst",
            reasons=["Threat keyword matched"],
            evidence_hash="1234567890abcdef",
            content_snippet="Threat text snippet"
        )
        save_case(self.case)

    def test_case_lifecycle(self):
        escalate_case(self.case_id, "Analyst1", "Escalating suspicious threat")
        cases = get_all_cases("ESCALATED")
        escalated_ids = [c.case_id for c in cases]
        self.assertIn(self.case_id, escalated_ids)

        dismiss_case(self.case_id, "Analyst1", "Dismissing false positive")
        cases_dism = get_all_cases("DISMISSED")
        dismissed_ids = [c.case_id for c in cases_dism]
        self.assertIn(self.case_id, dismissed_ids)

if __name__ == "__main__":
    unittest.main()
