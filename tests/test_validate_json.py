"""Classify original invalid response bytes separately from missing resources."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_json import audit


class JsonAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "response.json"

    def check_bytes(self, body, code, status):
        self.path.write_bytes(body)
        report, actual = audit(self.path)
        self.assertEqual(actual, code)
        self.assertEqual(report["status"], status)
        self.assertEqual(self.path.read_bytes(), body, "Audit must preserve original evidence")

    def test_malformed_response_is_failure(self):
        self.check_bytes(b'{"answer":', 1, "FAIL")

    def test_duplicate_response_keys_are_failure(self):
        self.check_bytes(b'{"answer":"a","answer":"b"}', 1, "FAIL")

    def test_invalid_utf8_is_failure(self):
        self.check_bytes(b'{"answer":"\xff"}', 1, "FAIL")

    def test_nonfinite_constant_is_failure(self):
        self.check_bytes(b'{"answer":NaN}', 1, "FAIL")

    def test_valid_json_is_syntax_pass_only(self):
        self.check_bytes(b'{"answer":"a"}', 0, "PASS")

    def test_missing_input_is_unverified(self):
        report, code = audit(self.path)
        self.assertEqual((report["status"], code), ("NOT VERIFIED", 2))

    def test_cli_exit_code_preserves_violation_resource_distinction(self):
        self.path.write_text('{"answer":', encoding="utf-8")
        command = [sys.executable, str(ROOT / "scripts/validate_json.py"), str(self.path)]
        malformed = subprocess.run(command, capture_output=True)
        self.assertEqual(malformed.returncode, 1)
        self.path.unlink()
        missing = subprocess.run(command, capture_output=True)
        self.assertEqual(missing.returncode, 2)


if __name__ == "__main__":
    unittest.main()
