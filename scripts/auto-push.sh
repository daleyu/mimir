#!/bin/sh
# Invoked after commits in the Mimir home, including background inbox commits.
if ! git rev-parse --verify '@{upstream}' >/dev/null 2>&1; then
    echo 'mimir: automatic push skipped: current branch has no upstream.' >&2
    exit 0
fi

export GIT_TERMINAL_PROMPT=0
if [ -z "${GIT_SSH_COMMAND:-}" ]; then
    export GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=5'
fi

# Name both upstream remote and branch so push.default cannot redirect the push.
branch=$(git symbolic-ref --quiet --short HEAD) || exit 0
remote=$(git config --get "branch.$branch.remote") || exit 0
destination=$(git config --get "branch.$branch.merge") || exit 0
if ! git push -- "$remote" "HEAD:$destination"; then
    echo 'mimir: automatic push failed; local commit retained. Retry git push when resolved.' >&2
fi
# A remote failure must not turn a successful local commit into a failed commit.
exit 0
