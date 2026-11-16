# Lessons

What makes delegation work, misconceptions that were corrected, and why the
rules changed. One line each; merge similar lessons.

## Delegation (what subagents actually need, where they get stuck)

- Herdr machine labels can carry emoji and match exactly: pass the id from
  `herdr machine list --json`. `agent prompt --wait` then
  `agent read --source recent-unwrapped` returns a clean answer.
- `herdr agent read` can hang or refuse `--lines` while the agent works: wait
  until idle, then read to a file. The Herdr SSH bridge drops occasionally; retry.
- Subagents refuse pushes when approval is only relayed by the orchestrator. Put
  standing authorization in the user-owned `rules.md`; outside its scope,
  have the manager return the exact command for the user.
- Running agents don't reload CLAUDE.md or AGENTS.md: start a new one after rule
  changes.
- Before rewriting a PR body, check its edit history: if the user edited it, keep
  their text and change only what was asked.
- After creating a draft PR, verify draft state (`gh pr view --json isDraft`);
  some tools undraft or reset title and body on push.
- Long-running projects get their own named session (a Herdr agent in a
  workspace of that name), not a subagent; never open TUIs or panes in the
  user's current workspace for testing.
- Squash merges: a merged PR's merge SHA differs from the branch head, so the
  branch is leftover; say so rather than reporting "in sync".
- Verify a split or rewritten history with an independent agent (tree compare,
  e.g. `git merge-tree --write-tree`), not the agent that made it.

## Corrections

## Rule changes
