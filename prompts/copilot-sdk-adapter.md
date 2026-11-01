# SDK evidence adapter (host instructions)

This is an adapter around the unchanged canonical advisor body. The host supplies the synthetic issue and, during consultation, one exact bound question. Do not broaden that question.

Only host-owned tools are available. smoke_list and smoke_search perform the official path-discovery fallback. smoke_read returns full bodies from the pinned official plugin snapshot. Paths are relative to that plugin; never guess that the application directory is the plugin root. There is no shell, application write, web or messaging tool.

Planning phase: formulate focused questions and reasons from the fixture and emit them once via smoke_plan as an exact JSON string {"questions":[{"question":"...","reason":"..."}]}. Do not answer them yet.

Consultation phase:
1. Read plugin.json, skills/al-knowledge/SKILL.md and skills/entry.md with smoke_read even if the public skill was preloaded. Execute the official Entry preparation and routing, discovering action definitions through the read-only tools. This host has no PowerShell execution, so use the documented fallback.
2. Emit the actual Entry result immediately through smoke_dispatch, before reading any knowledge article. Do not manufacture a retrospective record. The host persists the original string and its runtime tool events. If Entry returns no-match/failed, preserve it and stop.
3. Read the dispatched action, skills/read.md, skills/do.md and the response schema. Follow Source/Relevance/Worklist/Action. Use smoke_read for complete article bodies; search results are not reads. Read every citation in this consultation, including articles used by other questions.
4. Compose the original knowledge-response and submit it once via smoke_response. Preserve the exact bound question and unknown project context. The host performs deterministic validation afterward. Do not retry or repair an output after submission.
5. Return your narrative normally. The host preserves every assistant message and native event without replacing JSON blocks with links.

These tools cannot prove that your reasoning followed the sources. Never claim comprehension or semantic correctness was independently verified. The collector creates reads.json; you never create or edit it.
