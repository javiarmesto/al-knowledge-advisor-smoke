import { createHash } from "node:crypto";
import { readFileSync, realpathSync } from "node:fs";
import { join, resolve, relative } from "node:path";
import { execFileSync } from "node:child_process";
import { sha256 } from "./copilot_capture.mjs";

export function git(root, ...args) {
  return execFileSync("git", ["-C", root, ...args], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
}
export function snapshot(root, lock) {
  root = realpathSync(root);
  if (git(root, "rev-parse", "HEAD") !== lock.commit) throw new Error("Plugin HEAD differs from bcquality.lock.json.");
  if (git(root, "status", "--porcelain", "--untracked-files=all")) throw new Error("Plugin checkout must be clean.");
  const corpus = new Map(), hashes = {};
  const files = execFileSync("git", ["-C", root, "ls-files", "--stage", "-z"], { encoding: "utf8" }).split("\0").filter(Boolean);
  for (const record of files) {
    const match = /^(\d+) ([0-9a-f]{40}) 0\t(.+)$/.exec(record);
    if (!match) throw new Error("Unmerged/unsupported git index entry.");
    const [, mode, blob, path] = match;
    if (!["100644", "100755"].includes(mode)) throw new Error("Links/submodules are not accepted: " + path);
    const absolute = join(root, path);
    if (relative(root, realpathSync(absolute)).replaceAll("\\", "/") !== path) throw new Error("Noncanonical file: " + path);
    const body = readFileSync(absolute);
    const observed = createHash("sha1").update(Buffer.from("blob " + body.length + "\0")).update(body).digest("hex");
    if (observed !== blob) throw new Error("File bytes differ from pinned git blob: " + path);
    hashes[path] = sha256(body);
    if (/^(plugin\.json|skills\/|schemas\/|microsoft\/|community\/|custom\/|tools\/|docs\/)/.test(path)
        && /\.(md|json|al|ps1|py|txt|yml|yaml)$/.test(path)) corpus.set(path, body);
  }
  const manifest = JSON.parse(corpus.get("plugin.json").toString("utf8"));
  if (manifest.name !== "bcquality" || manifest.version !== lock.version) throw new Error("Plugin manifest differs from lock.");
  const contentHash = sha256(JSON.stringify(Object.entries(hashes).sort(([a], [b]) => a.localeCompare(b))));
  return { root, corpus, hashes, contentHash, manifest };
}
