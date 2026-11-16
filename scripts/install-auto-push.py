#!/usr/bin/env python3
"""Install an auto-push post-commit hook in a private Git repository (default: the
Mimir home), retaining existing Git hooks. Never install it in this public repo."""

import json
import os
from pathlib import Path
import shlex
import sys
import subprocess


def install(root):
    root = Path(root).resolve()

    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()

    hooks = Path(git("rev-parse", "--path-format=absolute", "--git-path", "mimir-hooks"))
    state = hooks / "previous-hooks.json"
    if state.exists():
        previous = Path(json.loads(state.read_text())["path"])
    else:
        result = subprocess.run(["git", "-C", str(root), "config", "--path", "--get",
                                 "core.hooksPath"], capture_output=True, text=True, check=False)
        if result.returncode not in (0, 1):
            raise RuntimeError(result.stderr.strip())
        previous = Path(result.stdout.strip()) if result.returncode == 0 else Path(
            git("rev-parse", "--path-format=absolute", "--git-path", "hooks"))
        if not previous.is_absolute():
            previous = root / previous
        previous = previous.resolve()
        if previous == hooks.resolve():
            raise RuntimeError("Existing auto-push hook directory lacks its original hook metadata")

    hooks.mkdir(exist_ok=True)
    # Include helper files as well as hooks: existing hooks may resolve siblings.
    if previous.is_dir():
        for source in previous.iterdir():
            if source.name == "post-commit" or not source.is_file():
                continue
            target = hooks / source.name
            if target.is_symlink() and target.resolve() == source.resolve():
                continue
            if target.exists() or target.is_symlink():
                raise RuntimeError(f"Preserved existing file rather than replacing it: {target}")
            target.symlink_to(source)

    old_hook = shlex.quote(str(previous / "post-commit"))
    push_script = shlex.quote(str(Path(__file__).resolve().with_name("auto-push.sh")))
    (hooks / "post-commit").write_text(
        f'#!/bin/sh\nif [ -x {old_hook} ]; then\n    {old_hook} "$@" || exit $?\nfi\n'
        f'exec /bin/sh {push_script} "$@"\n')
    (hooks / "post-commit").chmod(0o755)
    state.write_text(json.dumps({"path": str(previous)}) + "\n")
    git("config", "--local", "core.hooksPath", str(hooks))
    print(f"Installed automatic push hook for {root}; retained hooks from {previous}")


if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1
                  else os.environ.get("MIMIR_HOME", "~/.mimir")).expanduser()
    if target.resolve() == Path(__file__).resolve().parents[1]:
        sys.exit("refusing to auto-push the public mimir repository")
    install(target)
