"""Audit original JSON syntax: exit 0 valid, 1 contract violation, 2 unavailable input."""
import json
from pathlib import Path
import sys
from validate_result import strict_json


def audit(path):
    try:
        strict_json(path)
    except OSError as error:
        return {"status": "NOT VERIFIED", "error": str(error)}, 2
    except ValueError as error:
        # JSONDecodeError, duplicate keys, nonfinite constants and invalid UTF-8.
        return {"status": "FAIL", "error": str(error)}, 1
    return {"status": "PASS"}, 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"status": "NOT VERIFIED", "error": "Expected an original JSON file."}))
        sys.exit(2)
    report, code = audit(Path(sys.argv[1]))
    print(json.dumps(report))
    sys.exit(code)
