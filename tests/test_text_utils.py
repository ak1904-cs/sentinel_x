"""
Unit tests for utils/text_utils.py using standard unittest
"""
import unittest
from utils.text_utils import clean_text, extract_text_signals

class TestTextUtils(unittest.TestCase):
    def test_clean_text_basic(self):
        raw = "Check out https://example.com/test! Join us @user123 #threat."
        cleaned = clean_text(raw)
        self.assertNotIn("https", cleaned)
        self.assertIn("user123", cleaned)
        self.assertIn("#threat", cleaned)

    def test_extract_signals(self):
        raw = "Meeting at https://target.org @agent1 #attack"
        signals = extract_text_signals(raw)
        self.assertEqual(len(signals["urls"]), 1)
        self.assertIn("@agent1", signals["mentions"])
        self.assertIn("#attack", signals["hashtags"])

if __name__ == "__main__":
    unittest.main()
