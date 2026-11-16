# mimir

Agent skills and an orchestrator setup for Claude Code, Codex, or any agent that
reads the `SKILL.md` format.

This repository is public. It holds only how the agents work: skills, agent
types, the orchestrator charter, templates, and scripts. Your data (orchestrator
notes, plans, wiki, rules) lives in the Mimir home, `${MIMIR_HOME:-~/.mimir}`,
which you can make a private Git repository if you want history and sync.

## Layout

| Path | What it is |
| --- | --- |
| [skills/mimir](skills/mimir/SKILL.md) | The orchestrator skill and its [charter](skills/mimir/CHARTER.md): one long-lived session that delegates to managers and workers, keeps compact notes, and asks one high-value question per turn. |
| [skills/mimir/templates](skills/mimir/templates) | Seeds for the Mimir home: notes (`state.md`, `queue.md`, `lessons.md`), `rules.md`, and the Org plan template. |
| [agents](agents) | Claude Code agent types the orchestrator dispatches: `manager`, `worker`, `researcher`, `codex-researcher`. |
| [skills/dump](skills/dump/SKILL.md), [organize-wiki](skills/organize-wiki/SKILL.md), [lint-wiki](skills/lint-wiki/SKILL.md) | Wiki memory: append tagged session learnings to an inbox, file them into topic pages daily, and audit pages for stale claims. |
| [skills/daily-notes](skills/daily-notes/SKILL.md) | Turn a daily recap into Org task updates in `${NOTES_DIR:-~/notes}/refile.org`. |
| [skills/octo-review](skills/octo-review/SKILL.md) | Read PR files from running Neovim Octo buffers, with a GitHub fallback. |
| [scripts](scripts) | Wiki helper and tests, rules sync, and an optional auto-push hook for the Mimir home. |

## Install

```sh
git clone git@github.com:daleyu/mimir.git
cd mimir
./sync.sh                      # skills -> ~/.claude/skills, ~/.codex/skills; agents -> ~/.claude/agents
python3 scripts/sync-rules.py  # first run seeds ~/.mimir/rules.md; edit it, then rerun
```

`sync.sh` symlinks by default, so a `git pull` updates every agent at once. It
never overwrites a skill or agent file it did not install.

```sh
./sync.sh claude          # one target: claude, codex, or agents (~/.agents/skills)
./sync.sh /path/to/skills # any other skills directory
./sync.sh --copy          # copy instead of symlink
./sync.sh --remove        # remove what the script installed
```

`sync-rules.py` writes a marked managed block into `~/.claude/CLAUDE.md` (an `@`
import of `rules.md`) and `~/.codex/AGENTS.md` (the rule text), preserving
everything else. With `--machines <id>...` or `--all-machines` it also writes the
rules over `ssh -o BatchMode=yes` to saved Herdr machines.

## Using Mimir

Start one long-lived session and invoke `/mimir` (Claude Code) or `$mimir`
(Codex). On first use it seeds `~/.mimir/notes/` from the templates. Talk only to
it; it dispatches `manager` agents per objective, which run `worker`,
`researcher`, or `codex-researcher` agents and Herdr agents on other machines.
Non-trivial changes get an Org plan in `~/.mimir/plans/` that you annotate with
`FEEDBACK` headings and mark `APPROVED` before work starts.

## Wiki memory

The wiki lives in `~/.mimir/wiki/` (`index.md`, `feedback.md`, the `refile.md`
inbox) with raw history in `~/.mimir/archive.md`. Run `/dump` at the end of a
session to capture learnings and `/organize-wiki` daily to file them. For Codex,
`python3 scripts/mimir-wiki-hook.py install` adds SessionStart/Stop/SessionEnd
hooks that load feedback and commit the inbox automatically; review them in
Codex `/hooks`. If `~/.mimir` is a Git repository,
`python3 scripts/install-auto-push.py` adds a post-commit hook that pushes it.

Run the helper tests with `python3 scripts/test-mimir-wiki-hook.py`.

## Adding a skill

Create `skills/<name>/SKILL.md` with `name` and `description` frontmatter, then
run `./sync.sh` again. Conventions:

- Resolve paths from the skill's real path (two directories up is this repo),
  so it works through install symlinks.
- Keep personal data out: read and write it under `${MIMIR_HOME:-~/.mimir}` or
  another configurable location, never in this repository.
- Optional: `agents/openai.yaml` for Codex display metadata, `scripts/` for helpers.
