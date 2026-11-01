"""Regression coverage for the acceptance gate, not a live agent evaluation."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_plugin import PLUGIN
from validate_result import evaluate

FIXTURE = ROOT / "tests/fixtures/copilot-q2"
ARTICLE = "microsoft/knowledge/web-services/handle-httpclient-platform-failure-before-response-access.md"
SECOND = "microsoft/knowledge/web-services/check-http-status-before-consuming-response-body.md"

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.response = self.work / "response.json"
        self.question = self.work / "question.txt"
        self.response.write_bytes((FIXTURE / "response.json").read_bytes())
        self.question.write_bytes((FIXTURE / "question.txt").read_bytes())
        self.original = json.loads(self.response.read_text(encoding="utf-8"))

    def synthetic_valid(self):
        value = copy.deepcopy(self.original)
        value["references"][0]["applicability"] = "applicable"
        value["references"].append({"path": SECOND, "applicability": "applicable", "unknown": []})
        self.response.write_text(json.dumps(value), encoding="utf-8")
        return value

    def evidence(self, value, run_id="synthetic-unit-test"):
        records = []
        for ref in value["references"]:
            body = (PLUGIN / ref["path"]).read_bytes()
            records.append({"path": ref["path"], "complete": True,
                            "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
        data = {"runId": run_id,
                "questionSha256": hashlib.sha256(self.question.read_bytes()).hexdigest(),
                "reads": records}
        file = self.work / "reads.json"
        file.write_text(json.dumps(data), encoding="utf-8")
        return file

    def test_observed_q2_fails_without_evidence_and_is_not_repaired(self):
        before = self.response.read_bytes(), self.question.read_bytes()
        result, code = evaluate(self.response, self.question, PLUGIN, "structure")
        self.assertEqual(code, 1)
        self.assertEqual(result["checks"]["schema"]["status"], "FAIL")
        self.assertEqual(result["checks"]["answerCitations"]["status"], "FAIL")
        self.assertEqual(result["checks"]["question"]["status"], "PASS")
        self.assertEqual(result["checks"]["paths"]["status"], "PASS")
        self.assertEqual(result["smokeStatus"], "FAIL")
        self.assertEqual(before, (self.response.read_bytes(), self.question.read_bytes()))

    def test_missing_reference_detected_even_after_schema_rule_is_satisfied(self):
        value = copy.deepcopy(self.original)
        value["references"][0]["applicability"] = "applicable"
        self.response.write_text(json.dumps(value), encoding="utf-8")
        result, code = evaluate(self.response, self.question, PLUGIN, "structure")
        self.assertEqual(code, 1)
        self.assertEqual(result["checks"]["schema"]["status"], "PASS")
        self.assertEqual(result["checks"]["answerCitations"]["status"], "FAIL")

    def test_structural_pass_never_implies_acceptance(self):
        self.synthetic_valid()
        result, code = evaluate(self.response, self.question, PLUGIN, "structure")
        self.assertEqual(code, 0)
        self.assertEqual(result["checks"]["reads"]["status"], "NOT VERIFIED")
        self.assertEqual(result["contractStatus"], "NOT VERIFIED")
        self.assertEqual(result["smokeStatus"], "NOT VERIFIED")

    def test_full_mode_without_evidence_is_inconclusive_not_pass(self):
        self.synthetic_valid()
        result, code = evaluate(self.response, self.question, PLUGIN)
        self.assertEqual(code, 3)
        self.assertEqual(result["contractStatus"], "NOT VERIFIED")

    def test_invalid_response_fails_before_missing_evidence(self):
        result, code = evaluate(self.response, self.question, PLUGIN)
        self.assertEqual(code, 1)
        self.assertEqual(result["contractStatus"], "FAIL")

    def test_exact_question_includes_line_endings(self):
        self.synthetic_valid()
        self.question.write_bytes(self.question.read_bytes() + b"\r\n")
        result, code = evaluate(self.response, self.question, PLUGIN, "structure")
        self.assertEqual(code, 1)
        self.assertEqual(result["checks"]["question"]["status"], "FAIL")

    def test_duplicate_json_key_is_input_error(self):
        self.response.write_text('{"question": "a", "question": "b"}', encoding="utf-8")
        result, code = evaluate(self.response, self.question, PLUGIN, "structure")
        self.assertEqual(code, 2)
        self.assertIn("Duplicate JSON key", result["inputError"])

    def test_nonexistent_article_fails_static_check(self):
        value = self.synthetic_valid()
        value["references"][0]["path"] = "microsoft/knowledge/web-services/does-not-exist.md"
        self.response.write_text(json.dumps(value), encoding="utf-8")
        result, code = evaluate(self.response, self.question, PLUGIN, "structure")
        self.assertEqual(code, 1)
        self.assertEqual(result["checks"]["paths"]["status"], "FAIL")

    def test_official_full_check_with_synthetic_evidence_only_passes_contract(self):
        value = self.synthetic_valid()
        reads = self.evidence(value)
        result, code = evaluate(self.response, self.question, PLUGIN,
                                evidence=reads, run_id="synthetic-unit-test")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["contractStatus"], "PASS")
        self.assertEqual(result["smokeStatus"], "NOT VERIFIED")

    def test_official_validator_rejects_evidence_from_other_run(self):
        reads = self.evidence(self.synthetic_valid(), run_id="another-run")
        result, code = evaluate(self.response, self.question, PLUGIN,
                                evidence=reads, run_id="synthetic-unit-test")
        self.assertEqual(code, 1)
        self.assertEqual(result["checks"]["reads"]["status"], "FAIL")

    def test_official_validator_rejects_changed_article_hash(self):
        reads = self.evidence(self.synthetic_valid())
        data = json.loads(reads.read_text())
        data["reads"][0]["sha256"] = "0" * 64
        reads.write_text(json.dumps(data), encoding="utf-8")
        result, code = evaluate(self.response, self.question, PLUGIN,
                                evidence=reads, run_id="synthetic-unit-test")
        self.assertEqual(code, 1)

    def test_no_knowledge_needs_no_article_read_manifest(self):
        value = copy.deepcopy(self.original)
        value.update(outcome="no-knowledge", answer="No applicable knowledge was found.", references=[])
        self.response.write_text(json.dumps(value), encoding="utf-8")
        result, code = evaluate(self.response, self.question, PLUGIN, run_id="synthetic-unit-test")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["checks"]["reads"]["status"], "NOT REQUIRED")
        self.assertEqual(result["smokeStatus"], "NOT VERIFIED")

    def test_cli_can_reject_q2_without_read_evidence_or_run_id(self):
        run = subprocess.run([sys.executable, str(ROOT / "scripts/validate_result.py"),
                              str(self.response), "--question-file", str(self.question),
                              "--mode", "structure", "--plugin-root", str(PLUGIN)],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(json.loads(run.stdout)["checks"]["schema"]["status"], "FAIL")

if __name__ == "__main__":
    unittest.main()
