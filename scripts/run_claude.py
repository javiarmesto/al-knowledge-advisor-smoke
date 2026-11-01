"""Run the real project adapter; capture host output without claiming a smoke PASS."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

from prepare_plugin import ROOT, PLUGIN, LOCK, verify, git

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="Optional explicit model; otherwise the host chooses.")
    parser.add_argument("--max-budget-usd", type=float, default=10.0)
    parser.add_argument("--max-turns", type=int, default=40)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    if args.max_budget_usd <= 0 or args.max_turns <= 0 or args.timeout <= 0:
        parser.error("Budget, turns and timeout must be positive.")
    verify()
    executable = shutil.which("claude")
    if not executable:
        raise RuntimeError("Claude Code is missing from PATH. See docs/CLAUDE.md.")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    out = ROOT / "output" / "claude" / run_id
    raw = out / "raw"
    raw.mkdir(parents=True)
    prompt = (ROOT / "prompts/claude-smoke.txt").read_bytes()
    (raw / "prompt.txt").write_bytes(prompt)
    command = [executable, "-p", "--output-format", "stream-json", "--verbose",
               "--plugin-dir", str(PLUGIN), "--permission-mode", "dontAsk",
               "--tools", "Agent,Read,Glob,Grep,Skill",
               "--allowedTools", "Agent,Read,Glob,Grep,Skill",
               "--max-turns", str(args.max_turns), "--max-budget-usd", str(args.max_budget_usd)]
    if args.model:
        command += ["--model", args.model]
    env = os.environ.copy()
    env.pop("CLAUDE_AUTO_BACKGROUND_TASKS", None)
    env["CLAUDE_CODE_DISABLE_BACKGROUND_TASKS"] = "1"
    # Do not bypass nested-session protection. Launch this runner from an outer terminal.
    paths = ["plugin.json", "skills/al-knowledge/SKILL.md", "skills/entry.md",
             "skills/read.md", "skills/do.md", "schemas/knowledge-response.schema.json",
             "microsoft/skills/knowledge/al-knowledge.md"]
    hashes = {p: hashlib.sha256((PLUGIN / p).read_bytes()).hexdigest() for p in paths}
    profile_paths = ["experiments/knowledge-advisor/al-knowledge-advisor.agent.md",
                     ".claude/agents/al-knowledge-advisor.md",
                     "experiments/knowledge-advisor/smoke-issue.md"]
    version = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=30)
    manifest = {"runId": run_id, "repositoryCommit": git("rev-parse", "HEAD"),
                "repositoryStatus": git("status", "--porcelain"),
                "claudeVersion": version.stdout.strip(), "requestedModel": args.model,
                "pluginCommit": LOCK["commit"], "pluginVersion": LOCK["version"],
                "pluginRoot": str(PLUGIN), "pluginContractSha256": hashes,
                "projectSha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in profile_paths},
                "command": command, "verification": "NOT VERIFIED",
                "note": "Host capture only; no independent read collector has run."}
    def save():
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    save()
    print("Evidence:", out, flush=True)
    try:
        with (raw / "stream.jsonl").open("wb") as stdout, (raw / "stderr.txt").open("wb") as stderr:
            result = subprocess.run(command, input=prompt, stdout=stdout, stderr=stderr,
                                    cwd=ROOT, env=env, timeout=args.timeout)
        manifest["processExitCode"] = result.returncode
    except subprocess.TimeoutExpired:
        manifest["processExitCode"] = 124
        manifest["error"] = "Host exceeded the configured timeout; preserve partial transcript."
    except OSError as error:
        manifest["processExitCode"] = 2
        manifest["error"] = str(error)
    finally:
        save()
    print("Process exit:", manifest["processExitCode"], "Smoke acceptance: NOT VERIFIED")
    return manifest["processExitCode"]

if __name__ == "__main__":
    sys.exit(main())
