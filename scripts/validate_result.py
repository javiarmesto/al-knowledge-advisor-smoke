"""Invoke the official validator with externally collected evidence; never repair results."""
import argparse
from pathlib import Path
import subprocess
import sys

from prepare_plugin import ROOT, PLUGIN

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response", type=Path)
    parser.add_argument("--question-file", required=True, type=Path)
    parser.add_argument("--read-evidence", required=True, type=Path,
                        help="Trusted host collector output, never model-authored.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--plugin-root", type=Path, default=PLUGIN,
                        help="Actual plugin root used in the recorded run.")
    args = parser.parse_args()
    validator = args.plugin_root.resolve() / "tools/validate_knowledge_response.py"
    for path in [validator, args.response, args.question_file, args.read_evidence]:
        if not path.is_file():
            parser.error("Missing input: " + str(path))
    return subprocess.run([sys.executable, str(validator), str(args.response.resolve()),
                           "--root", str(args.plugin_root.resolve()),
                           "--question-file", str(args.question_file.resolve()),
                           "--read-evidence", str(args.read_evidence.resolve()),
                           "--run-id", args.run_id], cwd=ROOT).returncode

if __name__ == "__main__":
    sys.exit(main())
