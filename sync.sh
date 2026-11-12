#!/usr/bin/env bash
# Sync the skills in this repo into agent skill directories.
#
#   ./sync.sh                  link into Claude Code and Codex
#   ./sync.sh claude           link into one target (claude, codex, agents)
#   ./sync.sh /some/skills     link into an arbitrary skills directory
#   ./sync.sh --copy ...       copy instead of symlink
#   ./sync.sh --remove ...     remove what this script installed
#
# Symlinks are the default, so `git pull` updates every agent at once.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mode=link
targets=()

for arg in "$@"; do
  case "$arg" in
    --copy) mode=copy ;;
    --remove) mode=remove ;;
    -h | --help)
      sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    claude) targets+=("${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills") ;;
    codex) targets+=("${CODEX_HOME:-$HOME/.codex}/skills") ;;
    agents) targets+=("$HOME/.agents/skills") ;;
    -*)
      echo "unknown option: $arg" >&2
      exit 2
      ;;
    *) targets+=("$arg") ;;
  esac
done

if [ ${#targets[@]} -eq 0 ]; then
  targets=("${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills" "${CODEX_HOME:-$HOME/.codex}/skills")
fi

status=0
for target in "${targets[@]}"; do
  mkdir -p "$target"
  for skill in "$repo"/skills/*/; do
    skill="${skill%/}"
    [ -f "$skill/SKILL.md" ] || continue
    name="$(basename "$skill")"
    dest="$target/$name"

    # Only ever replace something this script put there: a symlink into this
    # repo, or a copy carrying our marker file.
    ours=no
    if [ -L "$dest" ]; then
      [ "$(readlink "$dest")" = "$skill" ] && ours=yes
    elif [ -f "$dest/.mimir-synced" ]; then
      ours=yes
    fi

    if [ -e "$dest" ] || [ -L "$dest" ]; then
      if [ "$ours" = no ]; then
        echo "skip    $dest (exists and was not installed by this script)" >&2
        status=1
        continue
      fi
      rm -rf "$dest"
      [ "$mode" = remove ] && echo "removed $dest"
    fi

    case "$mode" in
      link)
        ln -s "$skill" "$dest"
        echo "linked  $dest -> $skill"
        ;;
      copy)
        cp -R "$skill" "$dest"
        touch "$dest/.mimir-synced"
        echo "copied  $dest"
        ;;
    esac
  done
done
exit $status
