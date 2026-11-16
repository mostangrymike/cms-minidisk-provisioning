import json
import os
import sys
import unittest

# Ensure the evidence modules are importable from this tests directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import evidence_schema
class CmsEvidenceTests(unittest.TestCase):
    def test_validate_valid_evidence(self):
        evidence = {
            "id": "ev1",
            "timestamp": "2026-11-15T12:00:00Z",
            "type": "test",
            "source": "cms-tooling",
            "payload": {"a": 1}
        }
        self.assertTrue(evidence_schema.validate_evidence(evidence))

    def test_validate_missing_key(self):
        with self.assertRaises(ValueError):
            evidence_schema.validate_evidence({"id": "ev2"})

if __name__ == "__main__":
    unittest.main()
