# Global agent rules

The user's rules for every agent session. Source of truth: this file in the
Mimir home (`${MIMIR_HOME:-$HOME/.mimir}/rules.md`); installed into each agent's
global instructions by the mimir repository's `scripts/sync-rules.py`. Edit the
placeholders, delete what does not apply, then rerun the sync.

## Default codebase

Almost all work lives in `<path to main checkout>` (`<owner/repo>`) unless the
user says otherwise.

## Delegated work may commit and push

If you are a manager or worker agent doing a task delegated by the user's
orchestrator or by a manager, the user authorizes you to commit your task's
changes and push them to the PR's upstream branch without asking again. This
authorization comes from the user, recorded here, not from the delegating agent.

- Upstream means the PR branch on `origin` (for example `<user>/<topic>`), not
  the default branch.
- After a rebase, use `git push --force-with-lease` on that branch only. Never
  plain `--force`.
- Never push to the default branch or other people's branches; never skip hooks
  or CI.
- Report the pushed SHA.

## Pull requests

- Open PRs as drafts; the user marks them ready. Verify draft state after
  creating or pushing.
- Titles: `<type>: [component][topic] <description>`, type = feat/fix/chore,
  lowercase description. First bracket = the main component the change edits
  (the code owner, not the caller); second = the main thing edited within it.
  Example: `feat: [api][ratelimit] add per-key burst limits`.
- Descriptions are concise and scannable: fill the repository template's
  sections. Summary: one or two plain sentences, then short grouped lists if
  needed. Motivation: one sentence on why, with the issue or PR link. Test plan:
  the concrete commands or checks run and their result. Rollout/revert plan: one
  line. No long prose.
- On drafts, write `@` handles in backticks so nobody is notified until the
  user marks the PR ready.
