"""Audit saved question/response pairs; never claim a live smoke PASS."""
import argparse
import json
from pathlib import Path
import sys

from prepare_plugin import ROOT, PLUGIN
from validate_result import evaluate

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports-root", type=Path, default=ROOT / "reports")
    parser.add_argument("--plugin-root", type=Path, default=PLUGIN)
    args = parser.parse_args()
    results = []
    for response in sorted(args.reports_root.glob("**/q*/response.json")):
        result, code = evaluate(response, response.with_name("question.txt"),
                                args.plugin_root, mode="structure")
        results.append({"response": str(response), "exitCode": code, "validation": result})
    has_failure = any(r["exitCode"] != 0 for r in results)
    output = {"artifactChecks": "FAIL" if has_failure else ("PASS" if results else "NOT RUN"),
              "smokeStatus": "FAIL" if any(r["exitCode"] == 1 for r in results) else "NOT VERIFIED",
              "note": "Retrospective checks against the chosen corpus. Loaded plugin identity and reads are unverified.",
              "results": results}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if has_failure else 0

if __name__ == "__main__":
    sys.exit(main())
