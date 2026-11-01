import { createHash } from "node:crypto";
import { appendFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

export const sha256 = value => createHash("sha256").update(value).digest("hex");
export const ARTICLE = /^(microsoft|community|custom)\/knowledge\/.+\.(md|al)$/;
export const META = ["plugin.json", "skills/al-knowledge/SKILL.md", "skills/entry.md"];
export const ACTION = "microsoft/skills/knowledge/al-knowledge.md";
export const TOOL_NAMES = ["smoke_list", "smoke_search", "smoke_read", "smoke_dispatch", "smoke_response", "smoke_plan"];

export class Capture {
  constructor({ runId, sessionId, directory, corpus, question = null, maxQuestions = 2 }) {
    Object.assign(this, { runId, sessionId, directory, corpus, question, maxQuestions });
    this.calls = new Map();
    this.completions = new Map();
    this.starts = new Map();
    this.events = [];
    this.faults = [];
    this.sequence = 0;
    this.dispatch = null;
    this.response = null;
    this.plan = null;
    mkdirSync(join(directory, "raw"), { recursive: true });
    if (question !== null) writeFileSync(join(directory, "question.txt"), question, { flag: "wx" });
  }
  save(name, value) { writeFileSync(join(this.directory, name), value, { flag: "wx" }); }
  json(name, value) { this.save(name, JSON.stringify(value, null, 2)); }
  fail(message) {
    this.faults.push(message);
    throw new Error(message);
  }
  observe(event) {
    // SDK event object preserved as received. This is not a model-authored transcript.
    appendFileSync(join(this.directory, "raw/events.jsonl"), JSON.stringify(event) + "\n");
    this.events.push(event);
    const d = event.data || {};
    if (event.type === "tool.execution_start") {
      if (this.starts.has(d.toolCallId)) this.faults.push("Duplicate tool start: " + d.toolCallId);
      this.starts.set(d.toolCallId, event);
    }
    if (event.type === "tool.execution_complete") {
      if (this.completions.has(d.toolCallId)) this.faults.push("Duplicate tool completion: " + d.toolCallId);
      this.completions.set(d.toolCallId, event);
    }
    if (event.type === "assistant.message") {
      this.save("raw/message-" + this.events.length + ".json", JSON.stringify(event));
    }
    if (event.type === "session.error" || event.type === "subagent.failed") {
      this.faults.push(event.type + ": " + (d.message || d.error || "unknown error"));
    }
  }
  receipt(invocation, kind, args) {
    const id = invocation.toolCallId;
    if (typeof id !== "string" || this.calls.has(id)) this.fail("Missing or reused runtime toolCallId.");
    if (!invocation.agentId) this.fail("Tool call lacks subagent attribution; root calls cannot count.");
    const r = { id, kind, args, agentId: invocation.agentId, sequence: ++this.sequence };
    this.calls.set(id, r);
    appendFileSync(join(this.directory, "raw/calls.jsonl"), JSON.stringify({
      sessionId: this.sessionId, invocation, questionSha256: this.question === null ? null : sha256(this.question),
      sequence: r.sequence
    }) + "\n");
    return r;
  }
  success(r, text) {
    r.expected = text;
    return { resultType: "success", textResultForLlm: text };
  }
  confirmed(r) {
    const start = this.starts.get(r.id);
    const end = this.completions.get(r.id);
    // detailedContent is a UI payload and is deliberately NOT accepted as proof of model delivery.
    return !!(typeof r.expected === "string" && start && end && start.data.toolName === "smoke_" + r.kind
      && start.agentId === r.agentId && end.agentId === r.agentId
      && end.data.success === true && end.data.result?.content === r.expected);
  }
  hasRead(path) {
    return [...this.calls.values()].some(r => r.kind === "read" && r.path === path && this.confirmed(r));
  }
  requireFiles(paths) {
    const missing = paths.filter(p => !this.hasRead(p));
    if (missing.length) this.fail("Missing confirmed full contract reads: " + missing.join(", "));
  }
  handle(kind, args, invocation) {
    const r = this.receipt(invocation, kind, args);
    if (this.response || (this.question === null && this.plan)) this.fail("Output already captured; no subsequent tools allowed.");
    if (kind === "plan") {
      if (this.question !== null) this.fail("Planning is not allowed inside a bound consultation.");
      this.save("plan.raw.json", args.raw);
      const plan = JSON.parse(args.raw);
      if (!Array.isArray(plan.questions) || plan.questions.length < 1 || plan.questions.length > this.maxQuestions
          || plan.questions.some(q => typeof q.question !== "string" || !q.question.trim()
                                      || typeof q.reason !== "string" || !q.reason.trim())
          || new Set(plan.questions.map(q => q.question)).size !== plan.questions.length) {
        this.fail("Plan must contain distinct exact questions with reasons, within the host limit.");
      }
      this.plan = { value: plan, receipt: r };
      return this.success(r, "Plan captured. Return a concise summary; do not consult the skill in this planning phase.");
    }
    if (this.question === null) this.fail("Only smoke_plan is available in the planning phase.");
    if (kind === "list" || kind === "search") {
      const offset = args.offset ?? 0;
      if (!Number.isInteger(offset) || offset < 0) this.fail("Invalid discovery offset.");
      const prefix = args.prefix ?? "";
      const term = args.term ?? "";
      if (typeof prefix !== "string" || typeof term !== "string" || term.length > 200) this.fail("Invalid discovery input.");
      const all = [...this.corpus.keys()].sort().filter(p => p.startsWith(prefix)
        && (kind === "list" || this.corpus.get(p).toString("utf8").toLowerCase().includes(term.toLowerCase())));
      const paths = all.slice(offset, offset + 100);
      // Discovery returns paths only and never counts as a body read.
      return this.success(r, JSON.stringify({ paths, nextOffset: offset + paths.length < all.length ? offset + paths.length : null }));
    }
    if (kind === "read") {
      const path = args.path;
      if (typeof path !== "string" || !this.corpus.has(path)) this.fail("Unknown canonical corpus path.");
      if (ARTICLE.test(path) && (!this.dispatch || !this.confirmed(this.dispatch.receipt)
            || this.dispatch.value.outcome !== "routed")) this.fail("Article read before a confirmed routed Entry record.");
      const body = this.corpus.get(path);
      if (body.length > 200_000) this.fail("Document exceeds bounded full-read size; no truncated read is accepted.");
      const text = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(body);
      if (!Buffer.from(text, "utf8").equals(body)) this.fail("Document cannot round-trip as exact UTF-8.");
      r.path = path; r.bytes = body.length; r.sha256 = sha256(body);
      this.save("raw/read-" + r.sequence + ".txt", body);
      return this.success(r, text);
    }
    if (kind === "dispatch") {
      // Preserve the first attempted output even if admission fails.
      this.save("dispatch.raw-" + r.sequence + ".json", args.raw);
      if (this.dispatch) this.fail("Entry was already captured; a replacement/reconstructed dispatch is not accepted.");
      this.requireFiles(META);
      if ([...this.calls.values()].some(x => x.kind === "read" && ARTICLE.test(x.path || ""))) {
        this.fail("Entry capture must precede all knowledge body reads.");
      }
      const value = JSON.parse(args.raw);
      if (value.skill?.id !== "entry" || value.skill.version !== 1 || !["routed", "no-match", "failed"].includes(value.outcome)
          || !Array.isArray(value.dispatch) || !Array.isArray(value.skipped)) this.fail("Invalid Entry envelope.");
      if (value.outcome === "routed") {
        if (value.dispatch.length !== 1) this.fail("Knowledge-only fixture requires exactly one dispatched action.");
        const action = value.dispatch[0];
        if (action.skill?.id !== "al-knowledge" || action.skill.path !== ACTION
            || action.skill.version !== 1 || JSON.stringify(action.inputs) !== '["knowledge-query"]'
            || JSON.stringify(action.outputs) !== '["knowledge-response"]') this.fail("Unexpected action dispatch.");
      } else if (value.dispatch.length || !value["outcome-reason"]) this.fail("Unrouted Entry needs an empty dispatch and reason.");
      this.save("dispatch.json", args.raw);
      this.json("task-context.json", { goal: this.question, "inputs-available": ["knowledge-query"],
        "knowledge-query": this.question, technologies: ["al"] });
      this.dispatch = { value, receipt: r };
      return this.success(r, value.outcome === "routed"
        ? "Entry captured before article reads. Execute the dispatched action now."
        : "Entry outcome captured. Stop; do not invent a knowledge response.");
    }
    if (kind === "response") {
      this.save("response.raw-" + r.sequence + ".json", args.raw);
      if (!this.dispatch || !this.confirmed(this.dispatch.receipt)
          || this.dispatch.value.outcome !== "routed") this.fail("Response requires a confirmed routed Entry.");
      this.requireFiles([ACTION, "skills/read.md", "skills/do.md", "schemas/knowledge-response.schema.json"]);
      // Save verbatim, including invalid JSON. Validation runs OUTSIDE the model after capture.
      this.save("response.json", args.raw);
      this.response = { receipt: r };
      return this.success(r, "Original response captured. Do not revise it; the external validator will evaluate it.");
    }
    this.fail("Unknown collector operation.");
  }
  finalize() {
    const starts = this.events.filter(e => e.type === "subagent.started");
    const delegated = starts.length === 1 && starts[0].data?.agentName === "al-knowledge-advisor";
    if (starts.length > 1 || starts.some(e => e.data?.agentName !== "al-knowledge-advisor"))
      this.faults.push("Expected exactly one advisor delegation in this isolated phase.");
    if (new Set([...this.calls.values()].map(r => r.agentId)).size > 1)
      this.faults.push("Tools were attributed to more than one subagent.");
    const cancelled = this.events.some(e => e.type === "subagent.completed" && e.data?.cancelled === true);
    if (cancelled) this.faults.push("Advisor delegation was cancelled.");
    const completed = !cancelled && this.events.some(e => e.type === "subagent.completed" && e.data?.agentName === "al-knowledge-advisor"
      && this.events.some(s => s.type === "subagent.started" && s.data?.toolCallId === e.data.toolCallId
                             && s.data?.agentName === e.data.agentName));
    const allowed = new Set(["task", ...TOOL_NAMES]);
    for (const e of this.events) {
      if (e.type === "tool.execution_start" && !allowed.has(e.data?.toolName))
        this.faults.push("Unexpected runtime tool executed: " + e.data?.toolName);
    }
    const reads = new Map();
    const excluded = [];
    for (const r of this.calls.values()) {
      if (r.kind !== "read" || !ARTICLE.test(r.path || "")) continue;
      const index = e => e ? this.events.indexOf(e) : -1;
      const dispatchEnd = index(this.completions.get(this.dispatch?.receipt.id));
      const readStart = index(this.starts.get(r.id));
      const readEnd = index(this.completions.get(r.id));
      const responseStart = index(this.starts.get(this.response?.receipt.id));
      const timely = this.dispatch && this.response
        && this.dispatch.receipt.sequence < r.sequence && r.sequence < this.response.receipt.sequence
        && dispatchEnd >= 0 && dispatchEnd < readStart && readStart < readEnd && readEnd < responseStart;
      if (timely && this.confirmed(r)) {
        reads.set(r.path, { path: r.path, complete: true, bytes: r.bytes, sha256: r.sha256 });
      } else excluded.push({ toolCallId: r.id, path: r.path, reason: "Unconfirmed, failed, truncated, misattributed or outside consultation boundaries." });
    }
    if (this.question !== null) {
      this.json("reads.json", { runId: this.runId, questionSha256: sha256(this.question), reads: [...reads.values()] });
      this.json("read-exclusions.json", excluded);
    }
    const target = this.question === null ? this.plan?.receipt
      : this.dispatch?.value.outcome === "routed" ? this.response?.receipt : this.dispatch?.receipt;
    const missing = [];
    if (!delegated || !completed) missing.push("Matching native subagent start/completion events.");
    if (!target || !this.confirmed(target)) missing.push("Native successful completion of captured output.");
    if (this.question !== null && (!this.dispatch || !this.confirmed(this.dispatch.receipt)))
      missing.push("Native completion of the per-consultation Entry capture.");
    const result = { status: this.faults.length ? "FAIL" : missing.length ? "NOT VERIFIED" : "PASS",
      delegation: delegated && completed ? "PASS" : "NOT VERIFIED",
      faults: this.faults, missing, excludedReads: excluded.length,
      semanticReview: "NOT VERIFIED",
      note: "Capture proves delivery and chronology, not comprehension or correctness of Entry reasoning." };
    this.json("capture.json", result);
    return result;
  }
}

export function toolDefinitions(capture, planning = false) {
  const specs = planning ? [
    ["plan", "Capture the exact question plan once. raw is a JSON string with questions:[{question,reason}].", { raw: { type: "string" } }, ["raw"]]
  ] : [
    ["list", "Discover canonical plugin-relative paths; does not count as reading bodies.", { prefix: { type: "string" }, offset: { type: "integer" } }, []],
    ["search", "Discover paths whose text contains a term; no article bodies are returned.", { term: { type: "string" }, prefix: { type: "string" }, offset: { type: "integer" } }, ["term"]],
    ["read", "Read one entire pinned UTF-8 document. Use canonical plugin-relative path.", { path: { type: "string" } }, ["path"]],
    ["dispatch", "Capture the original Entry JSON before article reads. Exactly once per consultation.", { raw: { type: "string" } }, ["raw"]],
    ["response", "Capture original knowledge-response JSON verbatim once. Never repair after submission.", { raw: { type: "string" } }, ["raw"]]
  ];
  return specs.map(([kind, description, properties, required]) => ({
    name: "smoke_" + kind, description, defer: "never", skipPermission: true,
    parameters: { type: "object", properties, required, additionalProperties: false },
    handler: (args, invocation) => {
      try { return capture.handle(kind, args, invocation); }
      catch (error) {
        if (!capture.faults.includes(error.message)) capture.faults.push(error.message);
        return { resultType: "failure", textResultForLlm: "Capture failure: " + error.message, error: error.message };
      }
    }
  }));
}
