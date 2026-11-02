"""Copy the pinned workshop AL sources into a fresh AL-Go PTE checkout."""
import argparse
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", required=True, type=Path)
    parser.add_argument("--consumer", required=True, type=Path)
    args = parser.parse_args()
    lock = json.loads(Path(__file__).with_name("seed.lock.json").read_text(encoding="utf-8"))
    root = args.consumer.resolve(strict=True)
    seed = args.seed.resolve(strict=True)
    settings = json.loads((root / ".github/AL-Go-Settings.json").read_text(encoding="utf-8-sig"))
    project = json.loads((root / ".AL-Go/settings.json").read_text(encoding="utf-8-sig"))
    if settings.get("type") != "PTE" or project.get("appFolders") not in ([], ["App"]):
        parser.error("Use a fresh single-project AL-Go PTE with appFolders [] or [App].")
    dest = root / "App"
    if dest.exists():
        parser.error("App already exists; select a fresh consumer checkout.")
    with TemporaryDirectory(dir=root) as staging:
        app = Path(staging) / "App"
        for relative, expected in lock["files"].items():
            source = (seed / relative).resolve(strict=True)
            source.relative_to(seed)
            data = source.read_bytes()
            if git_blob(data) != expected:
                data = data.replace(b"\r\n", b"\n")
            if git_blob(data) != expected:
                parser.error(f"{relative} differs from the pinned workshop seed")
            target = app / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        app.rename(dest)
    print(f"Prepared {len(lock['files'])} verified files under {dest}")


if __name__ == "__main__":
    main()
