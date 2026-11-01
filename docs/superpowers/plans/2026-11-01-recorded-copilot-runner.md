# Recorded Copilot Runner Implementation Plan

**Goal:** Prepare an externally recorded Copilot test that can produce trustworthy per-query read manifests.
**Architecture:** A pinned official plugin snapshot, one SDK planning phase and isolated consultation sessions. Host-owned read/capture tools preserve raw outputs and match successful model-visible tool results before forming read evidence.
**Tech stack:** Node.js 22, Copilot SDK 1.0.28, Python official BCQuality validator.
**Spec:** docs/RECORDED-COPILOT.md; approved preparation scope in the conversation.

## Constraints and choices

- Preserve the canonical advisor; the SDK transport is explicitly a new adapter, not the mobile runtime.
- Keep PR #1 and #3 evidence immutable. Do not merge branches or change credentials.
- No shell/edit/web tools for the model. Only the host writes evidence.
- No model calls in default CI. Live execution needs explicit --run and an available model.
- Refuse incomplete, replayed, cross-agent, or late read evidence.

## Tasks

- [x] Pin SDK and verify typed API against its published package.
- [x] Implement snapshot verification against exact Git blobs, plus native event capture.
- [x] Enforce Entry -> full reads -> original response boundaries and bind manifests to each question.
- [x] Add synthetic rejection tests and retain existing Python regression tests.
- [x] Run offline and runtime preflight; report credentials blockers separately from test results.
- [ ] Publish a draft PR with runnable instructions and optional manually triggered workflow.
- [ ] A live model run is pending until an authenticated runtime is available; never claim that synthetic CI proves it.

## Verification focus

Truncated model output despite full display content; async results arriving after response;
cross-question/cross-agent replay; raw output replacement; native tool surface drift.

Validation: Actions run 41335659409 passed 18 collector tests, 13 consumer tests, upstream regressions, SDK type check and offline preflight. Runtime startup succeeded; authentication was unavailable (exit 3). No model calls were made.
