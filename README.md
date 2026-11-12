# mimir

A collection of agent skills that sync to Claude Code, Codex, or any agent that reads the `SKILL.md` format.

## Skills

| Skill | What it does |
| --- | --- |
| [mimir](skills/mimir/SKILL.md) | A single persistent orchestrator. Mimir stays available to talk to you while it starts managers, which start workers, and it tracks every session, agent, and machine through [Herdr](https://herdr.dev). |

## Install

```sh
git clone git@github.com:daleyu/mimir.git
cd mimir
./sync.sh
```

`sync.sh` symlinks each skill into `~/.claude/skills` and `~/.codex/skills`, so a `git pull` updates every agent at once.

```sh
./sync.sh claude          # one target: claude, codex, or agents (~/.agents/skills)
./sync.sh /path/to/skills # any other skills directory
./sync.sh --copy          # copy instead of symlink
./sync.sh --remove        # remove what the script installed
```

The script never overwrites a skill it did not install.

## Using Mimir

Mimir needs the `herdr` CLI and must run inside a Herdr pane. Start an agent in a pane and invoke the skill (`/mimir` in Claude Code, `$mimir` in Codex), then hand it work:

> Mimir, get the billing migration going and have someone look into the flaky checkout test.

Mimir starts a manager per goal in its own workspace, briefs it, and returns to you. Managers start their own workers. Ask Mimir at any point what is running, what is blocked, and what has finished.

State lives in `~/.mimir` (override with `MIMIR_HOME`): a ledger of who is working on what, and the report files agents write back.

## Adding a skill

Create `skills/<name>/SKILL.md` with `name` and `description` frontmatter, then run `./sync.sh` again.
