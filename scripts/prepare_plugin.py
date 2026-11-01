"""Fetch the pinned official plugin without modifying an existing checkout."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "bcquality.lock.json").read_text(encoding="utf-8"))
PLUGIN = ROOT / ".deps" / "bcquality"

def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True, encoding="utf-8").strip()

def verify():
    if git("rev-parse", "HEAD", cwd=PLUGIN) != LOCK["commit"]:
        raise RuntimeError("Existing plugin has another revision; use a fresh workspace.")
    if git("status", "--porcelain", "--untracked-files=all", cwd=PLUGIN):
        raise RuntimeError("Plugin checkout is not clean; use a fresh workspace.")
    manifest = json.loads((PLUGIN / "plugin.json").read_text(encoding="utf-8"))
    if manifest.get("name") != "bcquality" or manifest.get("version") != LOCK["version"]:
        raise RuntimeError("Pinned manifest does not match lock.")
    return manifest

def main():
    if not PLUGIN.exists():
        PLUGIN.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "-c", "core.autocrlf=false", "clone", "--no-checkout",
                        LOCK["repository"], str(PLUGIN)], check=True, cwd=ROOT)
        subprocess.run(["git", "-C", str(PLUGIN), "config", "core.autocrlf", "false"], check=True)
        subprocess.run(["git", "-C", str(PLUGIN), "checkout", "--detach", LOCK["commit"]], check=True)
    manifest = verify()
    print(json.dumps({"root": str(PLUGIN), "commit": LOCK["commit"], "version": manifest["version"]}))

if __name__ == "__main__":
    main()
