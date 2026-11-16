# Agent instructions

This repository is public. It defines how the agents work: skills, agent types,
the orchestrator charter, templates, and scripts.

- Never write personal data here: no notes, plans, wiki pages, rules, session
  output, usernames, hostnames, internal URLs, employer-specific tools, or
  absolute home-directory paths. That data belongs in `${MIMIR_HOME:-~/.mimir}`.
- A session here is not the orchestrator unless the user invokes the `mimir`
  skill. Subagents and delegated agents never take that role; they do their task
  and return `BLOCKED: <question>` instead of guessing.
- Do not commit or push in this repository unless the user asks; the user
  reviews changes here before publishing.
- Keep skills portable: resolve paths from the skill's real path, keep
  `name`/`description` frontmatter, and match the style of existing skills.
- Validate changes: `bash -n sync.sh` and `python3 scripts/test-mimir-wiki-hook.py`.

## Communication

Always be concise but specific.
