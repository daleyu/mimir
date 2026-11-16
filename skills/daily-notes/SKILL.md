---
name: daily-notes
description: Turn a spoken or written daily recap into Org task updates in the user's notes inbox (refile.org under $NOTES_DIR, default ~/notes), capture next steps and tomorrow's tasks, and tidy notes formatting without deleting content. Use for daily debriefs and planning against this personal notes directory.
---

# Daily notes

Use `${NOTES_DIR:-$HOME/notes}` as the notes root and `refile.org` as the default task inbox. Accept conversational, unstructured recaps of what the user finished, what is in progress, and what comes next. Act on the recap rather than merely suggesting edits.

## Listen and inspect

- If the user says they are about to talk or will send several parts, acknowledge briefly and wait for the recap. Do not finalize edits until they indicate they are finished. A complete recap in one message can be processed immediately.
- Read applicable `AGENTS.md` instructions, `refile.org`, and relevant task or topic notes. Inspect local changes before editing so existing user work is preserved. Use local file discovery and search for this local notes workflow.
- Determine the recap date in the user's timezone. Resolve “today” and “tomorrow” against that date; use the date the user supplies when recounting a different day. Do not invent a completion time.
- Inspect file-local TODO keywords and existing task, heading, tag, drawer, and timestamp conventions. This inbox currently uses `TODO`, `DONE`, and `CLOSED: [YYYY-MM-DD Day HH:MM]`; inspect it each time rather than assuming conventions never change.

## Update tasks

- Distinguish completed work, partial progress, future actions, blockers, and contextual notes. Only mark a task done when the recap clearly says it was completed. Progress or an intention to finish is not completion.
- Match tasks by their meaning, project context, and subtasks rather than exact wording alone. Read the matched subtree before editing. Update the smallest matching task; do not complete a parent merely because one child is done.
- Preserve task titles, links, tags, priorities, properties, IDs, drawers, scheduling, and historical notes. Change the state to the configured done keyword and add a valid inactive `CLOSED` timestamp immediately below the heading. Use a date-only timestamp when the completion time is unknown; preserve an existing `CLOSED` timestamp on tasks already done.
- Record partial progress and blockers as concise notes under the relevant task, using its existing log convention where practical. Preserve uncertainty and the user's intended meaning.
- Add concrete future actions as Org TODO headings in `refile.org`, under an existing project/task when appropriate or as top-level entries matching the inbox. Retain actionable details, dependencies, and supplied references. Leave general reflections as notes rather than manufacturing tasks.
- If an equivalent open task exists, update it instead of creating a duplicate. Repeated processing of the same recap should not duplicate tasks, completion timestamps, or progress notes.
- For work explicitly planned for tomorrow or another date, use `SCHEDULED: <YYYY-MM-DD Day>`. Use `DEADLINE` only for an actual due date stated by the user. Do not schedule every future action for tomorrow or change existing dates from a vague “next.”
- Preserve independently stated accomplishments even if no existing task matches: add a DONE entry in the inbox with a completion date and useful context.
- If the recap is ambiguous about which task was completed, leave candidate task states unchanged, capture clear information, and ask a focused clarification. Continue any independent edits supported by the recap.

Example syntax (replace the example dates with the recap's actual dates):

```org
* TODO Improve retry handling
** DONE Add regression coverage
CLOSED: [2026-11-04 Wed]
** TODO Deploy and check error rates
SCHEDULED: <2026-11-05 Thu>
Deploy after the parent change merges.
```

## Format without deleting content

Review human-authored `.org` and `.md` files in the notes directory for formatting improvements. Prioritize `refile.org` and notes related to the recap, then review the remaining notes in manageable batches. Skip hidden configuration, generated exports, logs, and binary assets. Apply only clear, lossless improvements; already well-formatted files need no edits.

- Tidy redundant blank lines, ordinary prose whitespace, list indentation, and table alignment. Preserve Markdown hard breaks and Org line-break syntax. Keep headings and list nesting semantically equivalent.
- Use Org syntax in Org files. When converting Markdown-style links or fenced blocks found in Org prose, preserve exact URLs, labels, block contents, and language names; leave ambiguous cases intact. In Markdown files, retain Markdown conventions.
- Preserve all substantive text, repeated notes, completed tasks, quotations, links, table cell values, and ordering. Do not summarize, rewrite prose, correct technical claims, deduplicate existing notes, archive tasks, move notes between files, or delete anything as a formatting operation.
- Preserve source/example block contents, commands, embedded data, and whitespace-sensitive material exactly. Preserve Org metadata and drawers, including `:PROPERTIES:` and `:LOGBOOK:`. New context may be appended; original notes stay intact.
- Do not run a whole-directory formatter blindly. Make focused patches and inspect the diff against the state read at the start, including files with pre-existing edits. If a file changed concurrently, re-read and merge the intended patch instead of overwriting it.

## Verify and report

Check that headings, drawers, blocks, links, and timestamps remain valid, and that every removed or replaced line is accounted for by a supported task-state change or lossless formatting. Confirm existing content is retained and new tasks are not duplicates. Recheck the working tree to distinguish your edits from pre-existing work.

Finish with a concise summary of tasks completed, tasks added or scheduled (including tomorrow's date), files formatted, and any unresolved matches or files not reviewed. Do not claim full-directory formatting if review was incomplete. Leave changes uncommitted unless asked to commit. Invoking this workflow authorizes the described notes edits; do not add a separate approval round when the recap and task matches are clear. Follow actual filesystem permission requirements if access is restricted.
