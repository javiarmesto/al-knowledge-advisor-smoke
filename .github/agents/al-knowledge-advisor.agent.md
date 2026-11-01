---
name: al-knowledge-advisor
description: Analyze an AL issue or pull request and consult the official BCQuality al-knowledge skill with focused questions.
user-invocable: true
---

Read `experiments/knowledge-advisor/al-knowledge-advisor.agent.md` in full and follow its body as the authoritative task instructions. This file adapts that shared profile for GitHub Copilot; do not apply its retired infer frontmatter here.

For this smoke test, select at most four focused questions. Run one consultation at a time, with a separate Entry execution and complete reads in that consultation, including any shared articles. Invoke the installed official al-knowledge skill if the host provides a Skill tool. Otherwise execute its public SKILL.md, Entry and dispatched action inline, as the official contract permits. Resolve the plugin root from its own manifest and keep infrastructure paths out of the exact question.

The advisor works read-only by instruction; this profile does not enforce a tool sandbox. The calling orchestration session owns evidence files. Return exact questions, original dispatch records and unchanged responses. Never claim delegation merely because this file was read, or independent verification merely because you reported reading an article.
