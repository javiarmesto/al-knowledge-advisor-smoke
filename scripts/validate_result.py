"""Check response structure even without read evidence; never repair raw results.

Exit 0: requested checks passed (structure mode is NOT full acceptance).
Exit 1: observed contract violation. Exit 2: input/resource error.
Exit 3: structure passed but full verification lacks read evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError
from prepare_plugin import PLUGIN

CITATION = re.compile(r"(?:microsoft|community|custom)/knowledge/[A-Za-z0-9_./-]+\.md")

def strict_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("Invalid JSON constant: " + value)
    return json.loads(Path(path).read_bytes().decode("utf-8-sig"),
                      object_pairs_hook=pairs, parse_constant=invalid)

def check(status, errors=None):
    return {"status": status, "errors": errors or []}

def structural_checks(response, question, root, schema):
    checks = {}
    errors = ["/" + "/".join(map(str, e.absolute_path)) + ": " + e.message
              for e in Draft7Validator(schema).iter_errors(response)]
    checks["schema"] = check("FAIL" if errors else "PASS", errors)
    exact = isinstance(response, dict) and response.get("question") == question
    checks["question"] = check("PASS" if exact else "FAIL",
                              [] if exact else ["Question differs from the exact bound UTF-8 input."])
    # Inspect well-shaped references even when another schema rule failed (q2).
    refs = response.get("references") if isinstance(response, dict) else None
    suppressed = response.get("suppressed") if isinstance(response, dict) else None
    if (not isinstance(refs, list) or not isinstance(suppressed, list)
            or not all(isinstance(r, dict) and isinstance(r.get("path"), str)
                       for r in refs + suppressed)):
        checks["paths"] = check("NOT VERIFIED", ["Reference structure is invalid."])
        checks["answerCitations"] = check("NOT VERIFIED", ["Reference structure is invalid."])
        return checks
    path_errors = []
    for item in refs + suppressed:
        name = item["path"]
        parts = name.split("/")
        candidate = (root / name).resolve()
        if ("\\" in name or any(p in ("", ".", "..") for p in parts)
                or not candidate.is_relative_to(root)):
            path_errors.append("Noncanonical corpus path: " + name)
        elif candidate.relative_to(root).as_posix() != name:
            path_errors.append("Corpus identity differs from claimed path: " + name)
        elif not candidate.is_file():
            path_errors.append("Corpus path does not exist: " + name)
    checks["paths"] = check("FAIL" if path_errors else "PASS", path_errors)
    answer = response.get("answer")
    if not isinstance(answer, str):
        checks["answerCitations"] = check("NOT VERIFIED", ["Answer is not a string."])
    else:
        declared = {r["path"] for r in refs}
        missing = sorted(set(CITATION.findall(answer)) - declared)
        errors = ["Explicit answer citation absent from references: " + p for p in missing]
        checks["answerCitations"] = check("FAIL" if errors else "PASS", errors)
    return checks

def evaluate(response_file, question_file, root, mode="full", evidence=None, run_id=None):
    root = Path(root).resolve()
    report = {
        "mode": mode,
        "contractStatus": "NOT VERIFIED",
        "smokeStatus": "NOT VERIFIED",
        "checks": {},
        "limits": [
            "Structure checks do not prove article reads, provenance, delegation or semantic support.",
            "Answer citation check only recognizes explicit canonical paths; it is not a prose audit.",
            "Read evidence must come from a trusted host collector, never from the answering model.",
            "The schema hash identifies the schema used for this audit, not the plugin loaded by the agent."
        ],
    }
    try:
        schema_file = root / "schemas/knowledge-response.schema.json"
        schema = strict_json(schema_file)
        Draft7Validator.check_schema(schema)
        report["schemaSha256"] = hashlib.sha256(schema_file.read_bytes()).hexdigest()
        report["pluginRootUsedForValidation"] = str(root)
        response = strict_json(response_file)
        question = Path(question_file).read_bytes().decode("utf-8-sig")
        report["responseSha256"] = hashlib.sha256(Path(response_file).read_bytes()).hexdigest()
        report["questionSha256"] = hashlib.sha256(question.encode("utf-8")).hexdigest()
        report["checks"] = structural_checks(response, question, root, schema)
        report["checks"]["reads"] = check("NOT VERIFIED")
        if any(c["status"] == "FAIL" for c in report["checks"].values()):
            report["contractStatus"] = report["smokeStatus"] = "FAIL"
            return report, 1
        if mode == "structure":
            return report, 0
        # Nothing is accepted merely because the deterministic structure checks passed.
        if evidence is None and response["references"]:
            report["checks"]["reads"] = check("NOT VERIFIED", ["No trusted read-evidence file supplied."])
            return report, 3
        if not run_id:
            raise ValueError("--run-id is required for the official full validator.")
        if evidence is not None:
            strict_json(evidence)  # Reject malformed input before invoking the upstream consumer.
        validator = root / "tools/validate_knowledge_response.py"
        if not validator.is_file():
            raise FileNotFoundError(validator)
        command = [sys.executable, str(validator), str(Path(response_file).resolve()),
                   "--root", str(root), "--question-file", str(Path(question_file).resolve()),
                   "--run-id", run_id]
        if evidence is not None:
            command += ["--read-evidence", str(Path(evidence).resolve())]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        report["officialValidator"] = {
            "exitCode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        if result.returncode not in (0, 1, 2):
            raise ValueError("Unexpected official validator exit code: " + str(result.returncode))
        if result.returncode == 2:
            report["checks"]["reads"] = check("NOT VERIFIED", ["Official validator input/resource error."])
            return report, 2
        report["checks"]["reads"] = check(("PASS" if response["references"] else "NOT REQUIRED")
                                         if result.returncode == 0 else "FAIL")
        report["contractStatus"] = "PASS" if result.returncode == 0 else "FAIL"
        # A contract PASS is never a global smoke PASS: other acceptance criteria remain separate.
        if result.returncode == 1:
            report["smokeStatus"] = "FAIL"
        return report, result.returncode
    except (OSError, ValueError, TypeError, SchemaError) as error:
        report["inputError"] = str(error)
        return report, 2

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response", type=Path)
    parser.add_argument("--question-file", required=True, type=Path)
    parser.add_argument("--mode", choices=["structure", "full"], default="full")
    parser.add_argument("--read-evidence", type=Path, help="Trusted collector output; never model-authored.")
    parser.add_argument("--run-id")
    parser.add_argument("--plugin-root", type=Path, default=PLUGIN,
                        help="Corpus/schema for validation; record if it differs from the run's loaded plugin.")
    args = parser.parse_args()
    if args.mode == "structure" and args.read_evidence is not None:
        parser.error("--read-evidence requires --mode full.")
    report, code = evaluate(args.response, args.question_file, args.plugin_root,
                            args.mode, args.read_evidence, args.run_id)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code

if __name__ == "__main__":
    sys.exit(main())
