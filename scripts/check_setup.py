"""Static readiness checks. This does not run or validate an agent smoke test."""
import ast
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
required = [
    "README.md", "AGENTS.md", "CLAUDE.md", "docs/CLAUDE.md", "docs/ACCEPTANCE.md",
    "prompts/claude-smoke.txt", "prompts/copilot-smoke.md",
    ".claude/agents/al-knowledge-advisor.md", ".github/agents/al-knowledge-advisor.agent.md",
    "experiments/knowledge-advisor/al-knowledge-advisor.agent.md",
    "experiments/knowledge-advisor/smoke-issue.md",
    "scripts/prepare_plugin.py", "scripts/run_claude.py", "scripts/validate_result.py",
]
for name in required:
    if not (ROOT / name).is_file():
        raise SystemExit("Missing: " + name)
lock = json.loads((ROOT / "bcquality.lock.json").read_text(encoding="utf-8"))
if not re.fullmatch(r"[a-f0-9]{40}", lock["commit"]):
    raise SystemExit("Plugin lock must contain a full commit SHA.")
if lock["repository"] != "https://github.com/microsoft/BCQuality.git":
    raise SystemExit("Unexpected plugin source.")
settings = json.loads((ROOT / ".github/copilot/settings.json").read_text(encoding="utf-8"))
if settings["extraKnownMarketplaces"]["bcquality"]["source"]["repo"] != "microsoft/BCQuality":
    raise SystemExit("Unexpected Copilot marketplace.")
if settings["enabledPlugins"].get("bcquality@bcquality") is not True:
    raise SystemExit("Copilot plugin is not enabled.")
for path in (ROOT / "scripts").glob("*.py"):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
for name in [".github/agents/al-knowledge-advisor.agent.md", ".claude/agents/al-knowledge-advisor.md"]:
    text = (ROOT / name).read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise SystemExit("Missing agent frontmatter: " + name)
    if "experiments/knowledge-advisor/al-knowledge-advisor.agent.md" not in text:
        raise SystemExit("Adapter does not reference the canonical profile: " + name)
print("SETUP PASS: required files, configuration and Python syntax. Live smoke: NOT RUN.")
