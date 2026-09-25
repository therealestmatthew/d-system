---
name: idea
description: Record a new idea in the append-only idea log, or move an existing one along — status, revisit, amend, annotate, link, classify — through the plugin's writer, then re-render the idea view. Use whenever someone names an idea to capture or asks to change an idea's status, text, annotations or links.
---

# Record or move an idea

The writer, `scripts/idea.py`, is the only sanctioned way to change the idea log. **Never write to
the log directly and never hand-edit the rendered view.** The log is append-only, so a malformed
line is permanent: there is no correction path, only a longer history containing the mistake.

Every command below starts with the same option assignments, so the person's saved plugin options
reach the script. Run them from the repository root, assignments included. An option the person
never saved appears as its `${user_config.…}` text; the script treats that as unset and uses the
documented default. The values are single-quoted so the shell leaves that text alone.

## Recording a new idea

Read the request as the idea. Distil a **title** — one line, specific enough to recognise in a list
of a hundred — and write the **body** as the idea in full: what it is, why it came up, what it would
touch, and what is unresolved. An idea recorded as one sentence usually cannot be judged later
without reconstructing the conversation it came from.

**Write the title and body to a temporary file with the file-writing tool, then pass that file.**
Never put the prose in a shell argument and never build the file with a shell heredoc: a backtick,
`$(...)`, a quote or a newline in the prose is evaluated or mangled by the shell before the writer
sees it, and the log keeps whatever the shell produced. The file's first line is the title; everything
after it is the body.

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" add --file <path to the file>
```

The writer generates the identifier and the timestamp. You supply the title and body and nothing
else; there is no way to supply a time.

**Record the idea as given.** Do not decline it for overlapping something that already exists, do
not merge it into a neighbouring entry, and do not judge it. If it overlaps, say so inside the body
and record it anyway: triage is a later pass, not a gate at the door.

## Moving an idea along

Use the same option assignments as above, then one of:

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" status <id> reviewing
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" status <id> promoted --promoted-to <document code>
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" status <id> delivered --doc <code> --commit <hash>
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" revisit <id>
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" amend <id> --title "corrected title"
```

Statuses move forward only; `docs/vocabulary.md` in the plugin lists every legal move. Promoting
names what the idea became. `delivered`, `resolved` and `absorbed` each need at least one pointer —
`--doc`, `--phase` or `--commit` — naming where the delivery happened, and the writer refuses a
pointer that does not resolve. A discarded idea may be revisited **once**; a second discard after
that is permanent, because something worth a third look is a new idea.

**Do not work around a refusal.** If the writer rejects a transition, the transition is illegal;
the fix is a different transition or a new idea, never a hand-edited line.

## Annotating, linking and classifying

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" annotate <id> --author repository-owner --kind note --file <path>
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" amend-annotation <id> <eid> --file <path>
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" link <id> --type relates_to --target <other id>
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" link <id> --type extends --target-code <document code>
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" retract-link <id> <eid>
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" classify <id> --author <name> --file <classification.json>
```

Annotations accumulate and are permitted on any idea, terminal included. `repository-owner` is the
owner's author name; **an agent writing under its own name may only use `--kind finding`**, so
`note`, `assessment` and `lineage` stay the owner's own voice. Write annotation text to a file and
pass `--file`, as for a new idea. `amend-annotation` corrects one annotation by the `eid` the writer
printed when it was written.

Links are typed and one-directional; the rendered view shows the inverse, which is never stored.
A link never changes its target: `retract-link` clears it, and there is no way to repoint one. An
`extends` cycle or a `supersedes` edge whose target is not discarded prints a warning and still
succeeds — capture wins over graph correctness.

A classification is a JSON object of the fields `docs/vocabulary.md` lists under Classification;
the latest one wins.

To read an idea's current state, amendments applied, use `idea.py list` or `idea.py show <id>` —
never the raw log, whose `created` line still holds any text an amendment corrected.

## Afterwards

Re-render the view and check the feature:

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/render_ideas.py"

CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/check.py" --feature ideas
```

Then tell the person the identifier and title of what was recorded or changed, and the writer's
output line. A bare "done" makes them open a file to find out what was written.
