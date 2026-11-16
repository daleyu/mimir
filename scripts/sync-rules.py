#!/usr/bin/env python3
"""Install the user's global rules into Claude Code and Codex config.

Rules live in the Mimir home, never in this public repository:
  ${MIMIR_HOME:-~/.mimir}/rules.md (seeded from skills/mimir/templates/rules.md)

Idempotent; content outside the managed markers is preserved. Skills and agent
types are linked separately by ./sync.sh.

Laptop (always, unless --no-local):
  ~/.claude/CLAUDE.md  managed block with an @-import of rules.md
  ~/.codex/AGENTS.md   managed block with the rule text (Codex has no imports)

Remote machines (--machines ID... or --all-machines; ids from `herdr machine list --json`):
  over non-interactive ssh to the machine's target, write the rule text into a
  managed block in ~/.claude/CLAUDE.md, and ~/.codex/AGENTS.md if ~/.codex exists.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get("MIMIR_HOME", "~/.mimir")).expanduser()
RULES = HOME / "rules.md"
TEMPLATE = ROOT / "skills" / "mimir" / "templates" / "rules.md"
BEGIN = "<!-- BEGIN mimir managed block: edit $MIMIR_HOME/rules.md, then rerun mimir's scripts/sync-rules.py -->"
END = "<!-- END mimir managed block -->"


def with_block(existing: str, body: str) -> str:
    block = f"{BEGIN}\n{body.rstrip()}\n{END}\n"
    start, end = existing.find(BEGIN), existing.find(END)
    if start != -1 and end > start:
        return existing[:start] + block + existing[end + len(END):].lstrip("\n")
    if not existing.strip():
        return block
    return existing.rstrip("\n") + "\n\n" + block


def write_local(path: Path, body: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text() if path.exists() else ""
    new = with_block(old, body)
    if new == old:
        return f"unchanged {path}"
    path.write_text(new)
    return f"updated {path}"


def sync_local(rules: str) -> None:
    home = Path.home()
    print(write_local(home / ".claude" / "CLAUDE.md", f"@{RULES.resolve()}"))
    print(write_local(home / ".codex" / "AGENTS.md", rules))


def ssh(target: str, command: str, stdin: str = "") -> subprocess.CompletedProcess:
    return subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", target, command],
        input=stdin, capture_output=True, text=True, timeout=90,
    )


def sync_remote(target: str, rules: str) -> str:
    probe = ssh(target, "test -d ~/.codex && echo codex; cat ~/.claude/CLAUDE.md 2>/dev/null; echo; echo __SPLIT__; cat ~/.codex/AGENTS.md 2>/dev/null; true")
    if probe.returncode != 0:
        return f"FAILED {target}: {probe.stderr.strip() or probe.returncode}"
    out = probe.stdout
    has_codex = out.startswith("codex\n")
    if has_codex:
        out = out[len("codex\n"):]
    claude_old, _, codex_old = out.partition("\n__SPLIT__\n")
    files = [("~/.claude/CLAUDE.md", claude_old)]
    if has_codex:
        files.append(("~/.codex/AGENTS.md", codex_old))
    results = []
    for path, old in files:
        new = with_block(old, rules)
        if new == old:
            results.append(f"unchanged {path}")
            continue
        quoted = path.replace("~/", "$HOME/")
        cmd = f'mkdir -p "$(dirname "{quoted}")" && cat > "{quoted}.tmp" && mv "{quoted}.tmp" "{quoted}"'
        res = ssh(target, cmd, stdin=new)
        if res.returncode != 0:
            return f"FAILED {target} {path}: {res.stderr.strip()}"
        results.append(f"updated {path}")
    return f"ok {target}: " + ", ".join(results)


def machines() -> list:
    out = subprocess.run(["herdr", "machine", "list", "--json"], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--machines", nargs="*", default=[], help="Herdr machine ids (or labels/targets)")
    ap.add_argument("--all-machines", action="store_true", help="sync every enabled saved Herdr machine")
    ap.add_argument("--no-local", action="store_true", help="skip laptop config")
    args = ap.parse_args()
    if not RULES.exists():
        RULES.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(TEMPLATE, RULES)
        print(f"created {RULES} from the template; edit it, then rerun")
        return 0
    rules = RULES.read_text()
    if not args.no_local:
        sync_local(rules)
    if not (args.machines or args.all_machines):
        return 0
    known = machines()
    if args.all_machines:
        chosen = [m for m in known if m.get("enabled", True)]
    else:
        chosen = []
        for want in args.machines:
            match = [m for m in known if want in (m["id"], m["target"], m.get("label"))]
            if not match:
                print(f"FAILED {want}: unknown Herdr machine")
            chosen += [m for m in match if m not in chosen]
    failed = 0
    for m in chosen:
        try:
            line = sync_remote(m["target"], rules)
        except subprocess.TimeoutExpired:
            line = f"FAILED {m['target']}: ssh timed out (auth needed?)"
        failed += line.startswith("FAILED")
        print(line)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
