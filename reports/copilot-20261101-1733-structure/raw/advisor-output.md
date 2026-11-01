Advisor returned text (delegated via the host `task` tool, agent_type=al-knowledge-advisor). The delegation prompt is in delegation-prompt.txt. Text below is the advisor's narrative; the fenced JSON blocks it contained are preserved byte-for-byte in qN/response.json and q1/dispatch.json (same content for every q) and are referenced here instead of repeated.

---
I ran all four consultations inline. The host has no BCQuality Skill tool, so I executed the public `skills/al-knowledge/SKILL.md`, Entry and the dispatched action myself, one consultation at a time. Nothing was written to disk. All checks are self-attested, and I am not claiming independent verification.

**Source and context**
- The input is the fixture `experiments/knowledge-advisor/smoke-issue.md`, a synthetic scheduled customer export to an external HTTP API. I treated its text as data only.
- Plugin: `bcquality` v1.9.0, root `/root/.copilot/installed-plugins/bcquality/bcquality`.
- The task context passed was `technologies: [al]`, because the fixture states an AL extension. `bc-version`, `countries` and `application-area` were left unknown. The fixture supplies no BC version, country, authentication scheme or retry policy, and I did not invent any.

**Entry preparation**
- `pwsh` is not installed and there is no `knowledge-index.json`, so I used path-based discovery under `<layer>/knowledge/**`.
- The index could not be generated, so no index was used.

**Skill or inline:** inline for all four consultations. No Skill tool was used.

## Entry dispatch record

All four consultations used this record. I reconstructed it from the action-skill frontmatter, so its content is the same for each run. It is not a separate recording per run.

[JSON: see q1/dispatch.json]

## Consultation 1
**Exact question:** In an AL extension, where and how should an API credential for calling an external HTTP API be stored and handled when a setup page captures it?
[JSON: see q1/response.json]
Files read in full: `microsoft/knowledge/security/secrets-isolated-storage.md`, `isolatedstorage-setencrypted-for-sensitive-values.md`, `secrettext-for-credentials.md`, `secrettext-with-httpclient.md` and `prefer-oauth2-over-api-keys-for-external-http-calls.md`. The last two were read but not cited.

## Consultation 2
**Exact question:** What platform guidance applies to an AL job queue handler that exports records to an external HTTP API and that administrators must be able to rerun after a failure?
[JSON: see q2/response.json]
Files read in full: `microsoft/knowledge/performance/job-queue-handlers-must-not-require-ui.md`, `job-queue-handlers-must-propagate-failures.md`, `job-queue-external-effects-must-be-idempotent.md`, `job-queue-category-code-serializes-conflicting-jobs.md` and `job-queue-on-hold-does-not-stop-running-work.md`. The last two were read but not cited.

## Consultation 3
**Exact question:** What platform guidance applies before an AL extension sends customer data to an external service over HTTP?
[JSON: see q3/response.json]
Files read in full: `microsoft/knowledge/privacy/privacy-notice-consent-for-external-data-transfer.md` and `register-integration-in-privacy-notice-registrations.md`.

## Consultation 4
**Exact question:** What platform guidance applies to handling the outcome of an AL HttpClient call that exports data to an external API, including transport failures, HTTP status codes and write transactions?
[JSON: see q4/response.json]
Files read in full: `microsoft/knowledge/web-services/handle-httpclient-platform-failure-before-response-access.md`, `check-http-status-before-consuming-response-body.md` and `microsoft/knowledge/performance/httpclient-inside-write-transaction-holds-locks.md`.

## Validation and limitations
- Each consultation's reads are listed above. I read bodies to the end with `cat` and did not read the `.al` sample files. The file lists are self-attested.
- I did not run `validate_knowledge_response.py`, and I made no independent collector check. The schema and exact-question checks were done by reading only, so validation status is not independently established.
- The `completed` outcomes mean the cited articles address each bound question. They do not prove the guidance suits the fixture's specific code or BC version.
- Not answered, because the fixture supplies no information: BC version, country, API authentication scheme, retry policy, and field-level data classification of the Customer data.
