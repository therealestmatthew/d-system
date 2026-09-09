---
description: Record a parked idea, or move an existing one along, through the sanctioned writer
argument-hint: "<the idea in prose> | status <id> <state> | revisit <id>"
---

# Record an idea

Wraps `tools/append_idea.py`, which is the only sanctioned writer for `_data/ideas.jsonl`.
**Never write to that file directly and never hand-edit `docs/00-working/ideas.md`.** The log is
append-only, so a malformed line is permanent — there is no correction path, only a longer history
containing the mistake. That is the whole reason the writer exists rather than a convention.

## Recording a new idea

Read `$ARGUMENTS` as the idea. Distil a **title** — one line, specific enough to be recognisable in a
list of a hundred — and write the **body** as the idea in full.

**Write the title and body to a temporary file, then pass that file — never inline the prose into a
shell command.** Prose containing a backtick, `$(...)`, a quote or a newline is not safe as a quoted
shell argument: idea `000019` was permanently corrupted exactly this way, when a double-quoted
`--body` let the shell evaluate a command substitution before the writer ever saw the text. Use the
Write tool (not a shell heredoc, which has the same quoting problem) to create the file with the
title as its first line and the body as everything after it:

```
<title, one line>
<body, the idea in full>
```

Then invoke the writer with that file and nothing else:

```bash
uv run python tools/append_idea.py add --file /path/to/the/file
```

The script generates the identifier and the timestamp. You supply the title and body and nothing
else; there is no way to supply a time and you should not look for one.

(`--title "..."` and `--body "..."` still exist for a short, plain-text title typed by hand, but
never use them for prose you did not write yourself character-by-character.)

**Record the idea as given.** Do not decline it for overlapping something that already exists, do not
merge it into a neighbouring entry, and do not judge it. If it overlaps, say so *inside the body* and
record it anyway — triage is a downstream pass, not a gate at the door ([ADR-010](../../docs/04-decisions/ADR-010-idea-staging.md)).

Write the body as the owner would want to read it in six months: what the idea is, why it came up,
what it would touch, and what is unresolved. An idea recorded as one sentence usually cannot be
judged later without reconstructing the conversation it came from.

## Moving an idea along

```bash
uv run python tools/append_idea.py status 000007 reviewing
uv run python tools/append_idea.py status 000007 promoted --promoted-to PLAN-016
uv run python tools/append_idea.py revisit 000007
```

Statuses move forward only: `open` → `triaged` → `reviewing` → `promoted`, with `discarded` reachable
from any of them. Promoting requires naming what the idea became. A discarded idea may be revisited
**once**; after that a second discard is permanent, because something worth a third look is a new
idea that deserves its own entry rather than a footnote in this one's history.

**Do not work around a refusal.** If the writer rejects a transition it is because the transition is
illegal, and the fix is a different transition or a new idea — never a hand-edited line.

## Annotating and linking

```bash
uv run python tools/append_idea.py annotate 000007 --author repository-owner --kind note --text "..."
uv run python tools/append_idea.py amend-annotation 000007 <eid> --text "corrected text"
uv run python tools/append_idea.py link 000007 --type relates_to --target 000003
uv run python tools/append_idea.py retract-link 000007 <eid>
```

Annotations accumulate and are permitted on any idea, terminal included — they extend the record,
not the state machine. **An agent writing `--author` for itself may only use `--kind finding`**;
`note` and `assessment` stay the owner's own voice. `amend-annotation` corrects one annotation's
text by the `eid` printed when it was written; it never touches the others.

Links are typed and one-directional (`extends`, `supersedes`, `relates_to`); the inverse is shown
in the rendered view but never stored. **A link never mutates its target.** The only legal amendment
is `retract-link`, which clears it — there is no way to repoint one. An `extends` cycle or a
`supersedes` edge whose target is not `discarded` prints a warning to stderr and still succeeds;
capture always wins over graph correctness.

## Afterwards

Regenerate the markdown view and leave the tree green:

```bash
uv run python tools/generate_ideas_md.py
uv run python -m src.governance
```

Then tell the owner the identifier and title of what was recorded. A bare "done" makes them open a
file to find out what you wrote.
