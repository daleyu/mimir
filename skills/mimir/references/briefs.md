# Briefing managers and workers

An agent you start knows nothing about your conversation with the user. The brief is everything it has. Write it as you would for a capable colleague who just walked in: what is wanted, why, what done looks like, and what you already know.

Send the brief as one prompt. If it is long, write it to a file under `${MIMIR_HOME:-$HOME/.mimir}/briefs/` and prompt the agent to read that file, which also leaves a record of what was asked.

## What every brief contains

- **The goal and what it is for.** The purpose lets the agent make sensible calls on things you did not anticipate.
- **What done looks like.** A concrete end state: tests pass, a PR is open, three candidates are ranked. Without it the agent stops early or never stops.
- **What is already known.** Things you or the user have ruled out, where the relevant code lives, the user's preferences that apply. Quote the user's own words when the wording matters.
- **Constraints.** What not to touch, what needs approval first, which branch or worktree to stay in.
- **Where to report.** The report file path, and what to put in it.

## Manager brief

A manager owns one goal end to end and runs its own workers through Herdr. On top of the common parts, tell it:

- Its name and role: it is `mgr-<project>`, a manager working for Mimir, the orchestrator the user talks to.
- That it may split the work and start workers in panes or tabs of its own workspace, naming them `wkr-<project>-<task>`, and that it should run `herdr --skill` and `herdr --help` to learn the commands. It should stay inside its workspace and leave other workspaces alone.
- That it is responsible for its workers: briefing them with the same care, checking their output before relying on it, and closing their panes when they finish.
- To keep its report file current as milestones land, so a check at any time shows real progress, and to finish with a final report and then stop.
- To stop and write its question in the report when it needs a decision that belongs to the user, rather than guessing or prompting Mimir's pane.

Example:

```text
You are mgr-billing, a manager agent working for Mimir, the orchestrator the user talks to.

Goal: move invoice tax calculation from the legacy TaxTable to the new tax-engine
service, so finance can add regions without a deploy. Done means every invoice path
uses the tax engine, the existing invoice tests pass, and a PR is open against main.

Context: the code is in services/billing. The user wants the legacy table left in
place behind a flag for one release, not deleted. Rounding must stay half-even; a
previous attempt broke this.

You are in your own Herdr workspace on a worktree of the repo. Split the work as you
see fit and start worker agents in panes or tabs of this workspace, named
wkr-billing-<task>. Run `herdr --skill` and `herdr --help` to learn the commands. You
own your workers: brief them fully, verify what they hand back, and close their panes
when they are done. Stay inside this workspace.

Do not push to main, deploy, or change anything outside services/billing without
asking. If you need a decision from the user, write the question in your report and
stop.

Keep ~/.mimir/reports/mgr-billing.md current: status, what is done, what is in
progress, open questions. End with what you verified and how, and the PR link.
```

## Worker brief

A worker does one bounded task and hands back a result. Keep the brief tight:

- Its name, and who it works for.
- The single task, its purpose, and what done looks like.
- The context it needs and the constraints that apply.
- What to return and where: the report file, with verified facts marked apart from guesses.
- That it does not start further agents unless told it may.

## Report files

Ask for reports in a shape you can read quickly and relay honestly:

```markdown
# mgr-billing
status: working | blocked | done
updated: <time>

## Done
## In progress
## Needs a decision
## Evidence
```

"Evidence" is what lets you verify before telling the user something is finished: commands run and their results, the diff or PR, and anything that was not checked.
