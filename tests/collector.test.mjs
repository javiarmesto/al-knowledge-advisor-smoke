import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { Capture, META, ACTION, sha256 } from "../scripts/copilot_capture.mjs";

const ARTICLE = "microsoft/knowledge/security/example.md";
const JSON_RESPONSE = '{"original": "preserve even invalid knowledge-response"}';
const entry = JSON.stringify({ skill: { id: "entry", version: 1 }, outcome: "routed", skipped: [],
  dispatch: [{ skill: { id: "al-knowledge", version: 1, path: ACTION },
               inputs: ["knowledge-query"], outputs: ["knowledge-response"] }] });
let id = 0;
function setup(t, question = "Exact question?\r\n") {
  const dir = mkdtempSync(join(tmpdir(), "bcq-collector-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  const corpus = new Map([...META, ACTION, "skills/read.md", "skills/do.md", "schemas/knowledge-response.schema.json"]
    .map(p => [p, Buffer.from("Full contract: " + p)]));
  corpus.set(ARTICLE, Buffer.from("Full article with accents: información.\r\nLast line.\r\n"));
  const c = new Capture({ runId: "test/q1", sessionId: "session-1", directory: dir, corpus, question });
  c.observe({ type: "subagent.started", data: { toolCallId: "delegate", agentName: "al-knowledge-advisor" } });
  return c;
}
function begin(c, kind, args, agentId = "advisor-1") {
  const toolCallId = "tool-" + ++id;
  c.observe({ type: "tool.execution_start", agentId, data: { toolCallId, toolName: "smoke_" + kind, arguments: args } });
  const result = c.handle(kind, args, { sessionId: "child", agentId, toolCallId, toolName: "smoke_" + kind, arguments: args });
  return { toolCallId, result, agentId };
}
function complete(c, call, content = call.result.textResultForLlm, success = true, agentId = call.agentId) {
  c.observe({ type: "tool.execution_complete", agentId, data: { toolCallId: call.toolCallId,
    success, result: { content, detailedContent: call.result.textResultForLlm } } });
}
function call(c, kind, args) { const r = begin(c, kind, args); complete(c, r); return r; }
function route(c) {
  for (const path of META) call(c, "read", { path });
  call(c, "dispatch", { raw: entry });
  for (const path of [ACTION, "skills/read.md", "skills/do.md", "schemas/knowledge-response.schema.json"])
    call(c, "read", { path });
}
function finish(c) {
  call(c, "response", { raw: JSON_RESPONSE });
  c.observe({ type: "subagent.completed", data: { toolCallId: "delegate", agentName: "al-knowledge-advisor" } });
  return c.finalize();
}
function reads(c) { return JSON.parse(readFileSync(join(c.directory, "reads.json"), "utf8")); }

test("full model-visible delivery yields byte-exact current-question evidence", t => {
  const c = setup(t); route(c); call(c, "read", { path: ARTICLE });
  assert.equal(finish(c).status, "PASS");
  const m = reads(c);
  assert.equal(m.questionSha256, sha256("Exact question?\r\n"));
  assert.equal(m.runId, "test/q1");
  assert.deepEqual(m.reads, [{ path: ARTICLE, complete: true, bytes: c.corpus.get(ARTICLE).length,
    sha256: sha256(c.corpus.get(ARTICLE)) }]);
  assert.equal(readFileSync(join(c.directory, "response.json"), "utf8"), JSON_RESPONSE);
});
test("display-only full content cannot hide model-facing truncation", t => {
  const c = setup(t); route(c);
  complete(c, begin(c, "read", { path: ARTICLE }), "truncated");
  finish(c); assert.equal(reads(c).reads.length, 0);
});
test("failed tool delivery never counts as complete", t => {
  const c = setup(t); route(c);
  complete(c, begin(c, "read", { path: ARTICLE }), c.corpus.get(ARTICLE).toString(), false);
  finish(c); assert.equal(reads(c).reads.length, 0);
});
test("cross-agent completions never count", t => {
  const c = setup(t); route(c);
  const r = begin(c, "read", { path: ARTICLE }); complete(c, r, r.result.textResultForLlm, true, "other-agent");
  finish(c); assert.equal(reads(c).reads.length, 0);
});
test("discovery is not a full body read", t => {
  const c = setup(t); route(c);
  call(c, "search", { term: "Full article" });
  finish(c); assert.equal(reads(c).reads.length, 0);
});
test("article read before Entry capture fails and is not retroactively accepted", t => {
  const c = setup(t);
  assert.throws(() => call(c, "read", { path: ARTICLE }), /before a confirmed/);
  assert.equal(c.finalize().status, "FAIL");
});
test("Entry requires confirmed complete contract reads", t => {
  const c = setup(t);
  assert.throws(() => call(c, "dispatch", { raw: entry }), /Missing confirmed/);
  assert.equal(c.finalize().status, "FAIL");
});
test("Entry replacement is rejected; first raw dispatch remains unchanged", t => {
  const c = setup(t); route(c);
  assert.throws(() => call(c, "dispatch", { raw: entry }), /already captured/);
  assert.equal(readFileSync(join(c.directory, "dispatch.json"), "utf8"), entry);
});
test("read completion after response starts is excluded", t => {
  const c = setup(t); route(c);
  const pending = begin(c, "read", { path: ARTICLE });
  const response = begin(c, "response", { raw: JSON_RESPONSE });
  complete(c, pending); complete(c, response);
  c.finalize(); assert.equal(reads(c).reads.length, 0);
});
test("fresh consultation cannot reuse previous question's read events", t => {
  const a = setup(t, "Q1"); route(a);
  const old = call(a, "read", { path: ARTICLE }); finish(a);
  const b = setup(t, "Q2"); route(b);
  complete(b, old); finish(b);
  assert.equal(reads(b).reads.length, 0);
  assert.notEqual(reads(a).questionSha256, reads(b).questionSha256);
});
test("unknown or traversal paths are rejected", t => {
  const c = setup(t); route(c);
  assert.throws(() => call(c, "read", { path: "../secret" }), /Unknown canonical/);
});
test("unattributed root tool calls are rejected", t => {
  const c = setup(t);
  assert.throws(() => begin(c, "read", { path: "plugin.json" }, null), /./);
});
test("missing native delegation cannot be replaced by model narration", t => {
  const c = setup(t); route(c); call(c, "read", { path: ARTICLE });
  c.events = c.events.filter(e => e.type !== "subagent.started");
  assert.equal(finish(c).status, "NOT VERIFIED");
});
test("extra native shell tool is an effects failure", t => {
  const c = setup(t); route(c);
  c.observe({ type: "tool.execution_start", data: { toolCallId: "shell", toolName: "bash" } });
  assert.equal(finish(c).status, "FAIL");
});
test("duplicate completion event prevents PASS", t => {
  const c = setup(t); route(c);
  const r = call(c, "read", { path: ARTICLE }); complete(c, r);
  assert.equal(finish(c).status, "FAIL");
});
test("planning captures original string and enforces question limit", t => {
  const c = setup(t, null);
  const raw = '{ "questions": [{"question":"A?","reason":"Source says A"}] }';
  call(c, "plan", { raw });
  assert.equal(readFileSync(join(c.directory, "plan.raw.json"), "utf8"), raw);
  assert.equal(c.plan.value.questions[0].question, "A?");
});
test("oversized documents fail instead of silently truncating", t => {
  const c = setup(t); route(c); c.corpus.set(ARTICLE, Buffer.alloc(200001, "x"));
  assert.throws(() => call(c, "read", { path: ARTICLE }), /bounded full-read/);
});
test("duplicate response cannot overwrite preserved original", t => {
  const c = setup(t); route(c); call(c, "response", { raw: JSON_RESPONSE });
  assert.throws(() => call(c, "response", { raw: "{}" }), /already captured/);
  assert.equal(readFileSync(join(c.directory, "response.json"), "utf8"), JSON_RESPONSE);
});
