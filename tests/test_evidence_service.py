"""
Unit tests for services/evidence_service.py using standard unittest
"""
import unittest
from services.evidence_service import compute_sha256, create_evidence_record, verify_evidence_integrity

class TestEvidenceService(unittest.TestCase):
    def test_compute_sha256(self):
        text = "Sentinel-X Test Payload"
        hash_val = compute_sha256(text)
        self.assertEqual(len(hash_val), 64)
        self.assertTrue(verify_evidence_integrity(text, hash_val))

    def test_create_evidence_record(self):
        rec = create_evidence_record("AN-TEST01", "Payload Text", "http://test.url")
        self.assertTrue(rec.evidence_id.startswith("EV-"))
        self.assertEqual(len(rec.sha256_hash), 64)

if __name__ == "__main__":
    unittest.main()
