#!/usr/bin/env bash
# Sync the skills and agent types in this repo into agent config directories.
#
#   ./sync.sh                  link into Claude Code and Codex
#   ./sync.sh claude           link into one target (claude, codex, agents)
#   ./sync.sh /some/skills     link into an arbitrary skills directory
#   ./sync.sh --copy ...       copy instead of symlink
#   ./sync.sh --remove ...     remove what this script installed
#
# Symlinks are the default, so `git pull` updates every agent at once.
# Agent types (agents/*.md) go to ~/.claude/agents whenever claude is a target.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mode=link
targets=()
agent_dirs=()
claude_home="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

for arg in "$@"; do
  case "$arg" in
    --copy) mode=copy ;;
    --remove) mode=remove ;;
    -h | --help)
      sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    claude)
      targets+=("$claude_home/skills")
      agent_dirs+=("$claude_home/agents")
      ;;
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
  targets=("$claude_home/skills" "${CODEX_HOME:-$HOME/.codex}/skills")
  agent_dirs=("$claude_home/agents")
fi

# Emit "<target> <source>" pairs: every skill into each skills target, every
# agent type into each agents target.
pairs() {
  local target src
  for target in "${targets[@]}"; do
    for src in "$repo"/skills/*/; do
      src="${src%/}"
      [ -f "$src/SKILL.md" ] && printf '%s\t%s\n' "$target" "$src"
    done
  done
  for target in ${agent_dirs[@]+"${agent_dirs[@]}"}; do
    for src in "$repo"/agents/*.md; do
      [ -f "$src" ] && printf '%s\t%s\n' "$target" "$src"
    done
  done
}

status=0
while IFS=$'\t' read -r target src; do
  mkdir -p "$target"
  dest="$target/$(basename "$src")"

  # Only ever replace something this script put there: a symlink into this
  # repo, or a copy carrying our marker.
  ours=no
  if [ -L "$dest" ]; then
    [ "$(readlink "$dest")" = "$src" ] && ours=yes
  elif [ -f "$dest/.mimir-synced" ]; then
    ours=yes
  elif [ -f "$dest" ] && [ "$(tail -n 1 "$dest")" = "<!-- mimir-synced -->" ]; then
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
      ln -s "$src" "$dest"
      echo "linked  $dest -> $src"
      ;;
    copy)
      if [ -d "$src" ]; then
        cp -R "$src" "$dest"
        touch "$dest/.mimir-synced"
      else
        # Agent files must start with frontmatter, so mark copies at the end.
        { cat "$src"; printf '\n<!-- mimir-synced -->\n'; } >"$dest"
      fi
      echo "copied  $dest"
      ;;
  esac
done < <(pairs)
exit $status
