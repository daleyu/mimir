---
name: octo-review
description: Read and review PR files from the user's running Neovim Octo review buffers, with a GitHub diff fallback when a requested file is not loaded or accessible. Use when the user is reviewing through Octo or supplies an octo:// URI.
---

# Octo review

The user is doing a code review in Neovim through Octo. Read the files from
their running Neovim server first. An `octo://` URI identifies a virtual buffer,
not a file on disk. Loaded buffers, including hidden ones, can be read through
Neovim RPC. The local checkout may differ from the reviewed PR revision.

## Locate the server and buffer

Discover current sockets; do not reuse session-specific socket paths or buffer
numbers from past conversations. On this user's macOS setup, Neovim sockets
were under `$TMPDIR/nvim.<user>/<directory>/nvim.<pid>.0`. Multiple instances
may be running, and stale sockets may remain.

This read-only example lists buffer IDs, names, and loaded status for each
reachable instance without dumping buffer variables or contents:

```python
import glob
import os
import subprocess
import tempfile

root = os.environ.get("TMPDIR") or tempfile.gettempdir()
expression = '''json_encode(luaeval("vim.tbl_map(function(b) return {id=b, name=vim.api.nvim_buf_get_name(b), loaded=vim.api.nvim_buf_is_loaded(b)} end, vim.api.nvim_list_bufs())"))'''
for socket in glob.glob(os.path.join(root, "nvim.*", "*", "nvim.*")):
    try:
        result = subprocess.run(
            ["nvim", "--server", socket, "--remote-expr", expression],
            capture_output=True, text=True, timeout=10,
        )
    except subprocess.TimeoutExpired:
        continue
    if result.returncode == 0:
        print(socket)
        print(result.stdout)
```

Match the exact requested URI. A review URI includes repository, review ID,
diff side (`LEFT` or `RIGHT`), and repository-relative path. `RIGHT` is the
proposed version; `LEFT` is the base version. Do not silently substitute one
side, a test with a similar filename, or a buffer from another review.

If socket access fails because of sandbox restrictions, request the normal
command escalation for the read-only Neovim connection. Use bounded calls;
skip stale sockets and report an actual access blocker accurately.

## Read the file

Use the socket and buffer ID discovered above. For example, after replacing
`SOCKET` and `BUFFER_ID` with the discovered values:

```sh
nvim --server SOCKET --remote-expr 'json_encode({"name": bufname(BUFFER_ID), "lines": getbufline(BUFFER_ID, 1, "$")})'
```

Verify the returned name still matches the requested URI before using its
contents. JSON encoding returns actual text; printing a Lua table directly
only returns its address. For large files, replace `1, "$"` with a focused
line range. Read both diff sides when available and needed for the review.
An empty result or unloaded buffer is not evidence that the PR file is empty.

Keep the review read-only: do not switch windows, change buffers, write files,
submit review comments, or send keys merely to retrieve text. Review the
retrieved contents under the applicable repository instructions and distinguish
observations from checks you have actually run.

## GitHub fallback

If the requested file is absent, unloaded, or inaccessible after checking the
running instances, it is okay to fetch the file or PR diff from GitHub using
available read tools (such as read-only `gh`). There is no need
to make the user open it in Octo first.

Identify the correct PR from the associated `octo://OWNER/REPO/pull/NUMBER`
buffer, Octo review context, or a supplied PR link. The `PRR_...` review ID is
not a PR number; never guess the number or choose an unrelated open PR.
If the mapping is ambiguous, ask for the PR link or number.

Fetch the requested path and the relevant PR diff at its head/base revisions.
Explain briefly that the file was not available through the Octo buffers and
that GitHub supplied the content. Do not claim GitHub content came from the
live editor or assume it matches a previously loaded buffer after a new push.
