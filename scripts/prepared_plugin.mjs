import { readdirSync, readFileSync, realpathSync, lstatSync } from "node:fs";
import { join } from "node:path";
import { sha256 } from "./copilot_capture.mjs";

const json = b => JSON.parse(b.toString("utf8").replace(/^\uFEFF/, ""));
const required = ["plugin.json","skills/al-knowledge/SKILL.md","skills/entry.md","skills/read.md","skills/do.md",
  "microsoft/skills/knowledge/al-knowledge.md","schemas/knowledge-response.schema.json","tools/validate_knowledge_response.py",
  "_filter-report.json","knowledge-index.json"];

// The caller supplies trusted SetupBCQuality outputs, never paths from a GitHub issue or diff.
export function preparedSnapshot(directory, expectedActionHash) {
  if (!/^[a-f0-9]{64}$/.test(expectedActionHash || "")) throw Error("Missing trusted SetupBCQuality contentHash.");
  const root = realpathSync(directory);
  const hashes = {}, corpus = new Map();
  function walk(prefix) {
    for (const entry of readdirSync(join(root,prefix), {withFileTypes:true})) {
      if (entry.name === ".git") continue;
      const path = prefix ? prefix + "/" + entry.name : entry.name;
      if (entry.isSymbolicLink()) throw Error("Link in prepared plugin: " + path);
      if (entry.isDirectory()) { walk(path); continue; }
      if (!entry.isFile()) throw Error("Unexpected prepared plugin entry: " + path);
      const bytes = readFileSync(join(root,path));
      hashes[path] = sha256(bytes);
      if ((/^(plugin\.json$|knowledge-index\.json$|skills\/|schemas\/|microsoft\/|community\/|custom\/|tools\/|docs\/)/).test(path)
          && /\.(md|json|al|ps1|py|txt|ya?ml)$/.test(path)) corpus.set(path,bytes);
    }
  }
  walk("");
  for (const path of required) if (!Object.hasOwn(hashes,path)) throw Error("Unavailable in prepared plugin: " + path);
  const manifest = json(corpus.get("plugin.json"));
  const policy = json(readFileSync(join(root,"_filter-report.json")));
  if (manifest.name !== "bcquality" || manifest.version !== policy.pluginVersion || policy.marketplace !== "microsoft/BCQuality"
      || policy.contentHash !== expectedActionHash) throw Error("Prepared plugin and trusted action outputs disagree.");
  if (!Array.isArray(policy.removed) || policy.removed.length !== policy.removedCount) throw Error("Invalid filter report.");
  for (const {path} of policy.removed) if (Object.hasOwn(hashes,path)) throw Error("Excluded content still present: " + path);
  for (const {path} of json(corpus.get("knowledge-index.json")).articles) {
    if (!corpus.has(path)) throw Error("Missing indexed article: " + path);
  }
  // Includes generated indices + filter report; AL-Go computes its own hash before writing these.
  const contentHash = sha256(JSON.stringify(Object.keys(hashes).sort().map(p=>[p,hashes[p]])));
  return {root,hashes,corpus,contentHash,manifest,policy};
}

export function readTaskContext(file) {
  if (!lstatSync(file).isFile() || lstatSync(file).size > 160000) throw Error("Invalid or oversized context.");
  const raw = readFileSync(file);
  const t = json(raw);
  if (!["issue","pull_request"].includes(t.kind) || !/^[\w.-]+\/[\w.-]+$/.test(t.repository) ||
      !Number.isSafeInteger(t.number) || t.number < 1 || typeof t.title !== "string" || typeof t.body !== "string")
    throw Error("Invalid GitHub task context.");
  if (t.kind === "pull_request" && (!/^[0-9a-f]{40}$/.test(t.headSha || "") || !/^[0-9a-f]{40}$/.test(t.baseSha || "")
    || !Array.isArray(t.files) || !t.files.length || t.files.some(f=>typeof f.path !== "string" || !f.path.endsWith(".al") || typeof f.patch !== "string" || !f.patch)))
    throw Error("PR requires authoritative base, head and AL patches.");
  return {text:raw.toString("utf8"),source:{kind:t.kind,repository:t.repository,number:t.number,host:t.host ?? null,
    ...(t.kind==="pull_request"?{headSha:t.headSha,baseSha:t.baseSha}:{}),contextSha256:sha256(raw)}};
}
