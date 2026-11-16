---
name: dump
description: Append tagged durable feedback and verified learnings from the current session to the Mimir wiki inbox when the user asks to save or capture session learnings.
---

The wiki is private user data in the Mimir home, `${MIMIR_HOME:-$HOME/.mimir}`
(call it HOME below), never in this skill's public repository. The helper is
`scripts/mimir-wiki-hook.py` in that repository: resolve this skill's real path
through any install symlink; the repository is two directories above the skill
folder.

Read `HOME/wiki/index.md` and `HOME/wiki/feedback.md` for context, then append
only new durable user corrections/preferences and verified reusable knowledge to
`HOME/wiki/refile.md`. Do not reorganize curated pages; use `$organize-wiki` for that.

Use the helper's `append --wiki HOME --session ID` command with a JSON array on
stdin. Each entry has `kind` (`feedback` or `learning`),
`tags` (nonempty lowercase kebab-case topics), `note`, and `source` (single lines).
Use the active session ID; retrying an identical entry in that session is safe.
Ground preferences in explicit user input and technical claims in observed
results or source links. Exclude secrets, dumps, transcripts, and task status.
Preserve all existing inbox bytes. Skip appending if nothing new is useful.

If HOME is a Git repository, after capture delegate one subagent working in HOME
to run the helper's `commit --wiki HOME` command and report its result. Its sole
task is the capture-only inbox commit: no editing, organization, further capture,
or delegation. A post-commit hook, if installed, pushes. If delegation is
unavailable, let SessionEnd perform the same commit. Preserve notes if
permissions block capture or committing and report briefly without requesting
additional access solely for memory capture.
