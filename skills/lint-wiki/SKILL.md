---
name: lint-wiki
description: Review the shared wiki to verify it is current and internally consistent. Use when the user asks to lint, audit, validate, or check the wiki for stale or contradictory information.
---

The wiki is private user data at `${MIMIR_HOME:-$HOME/.mimir}/wiki/`, never in
this skill's public repository. Review its `logs.md` (create it if missing),
then inspect wiki notes that could be wrong or outdated.

Find gaps, unsupported claims, and contradictions between notes, and report
them to the user. Put the strongest and most actionable findings first. Cite
the relevant note and its source when available, and distinguish verified
errors from items that merely need confirmation.

Pay attention to the dates in `logs.md` and any dated sources. Newer information
is usually, but not always, more accurate; prefer authoritative current code or
documentation over recency alone.

Move or group topics under a new subdirectory only when there is a clear
retrieval or maintenance benefit. When reorganizing, update `wiki/index.md` and
all affected relative links, avoid duplicating content, and append a compact
`YY-MM-DD ...` entry to `wiki/logs.md`.
