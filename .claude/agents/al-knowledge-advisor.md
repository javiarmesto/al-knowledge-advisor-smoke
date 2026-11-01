---
name: al-knowledge-advisor
description: Analyze an AL issue or pull request and consult the official BCQuality al-knowledge skill with focused questions.
tools: Read, Glob, Grep, Skill
---

Read `experiments/knowledge-advisor/al-knowledge-advisor.agent.md` in full and follow its body as the authoritative task instructions. Its YAML frontmatter belongs to another host.

Use the installed official `bcquality:al-knowledge` Skill. Resolve the plugin root from its manifest; never put PLUGIN_ROOT into Skill args. Make one consultation at a time: exact question -> Skill -> Entry -> action and complete article reads -> unchanged response, then the next question. A separate question needs a separate Entry execution and complete reads in its own consultation, including shared articles.

For this smoke test, select at most four focused questions. Do not invent project context. Return the report, exact questions, original dispatch records and original knowledge responses to the caller. The caller owns evidence files. Do not write files or publish anything. If the plugin is unavailable, report the blocker. Use the documented path discovery fallback when PowerShell/index helpers are unavailable. Your own read claims are self-attestation, never independent verification.
