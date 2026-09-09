---
schema_version: 1
id: doc-ops-append-idea
code: OPS-005
title: Append an event to the idea log
kind: operation
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-portfolio]
depends_on: [doc-governance-operations]
---

# Append an event to the idea log

## Trigger

Use whenever an idea needs to be recorded, moved to a new status, reopened, or corrected. This is
the only sanctioned writer for `_data/ideas.jsonl` — it is an append-only event log, so a malformed
line written any other way is permanent; there is no correction path, only a longer history
containing the mistake. A wrong title or body is fixed the same way: not by editing the line, but
by appending a correction that names it.

## Command

```bash
uv run python tools/append_idea.py add --file idea.md      # title = first line, rest = body
uv run python tools/append_idea.py add                     # same, but reads stdin
uv run python tools/append_idea.py status 000007 reviewing
uv run python tools/append_idea.py status 000007 promoted --promoted-to PLAN-016
uv run python tools/append_idea.py revisit 000007
uv run python tools/append_idea.py amend 000007 --title "corrected title"
uv run python tools/append_idea.py amend 000007 --body "corrected body"
```

Prefer `--file`/stdin over `--title "..." --body "..."` for anything beyond a short, plain-text
title: a quoted `--body` passes prose through the shell, and a backtick or `$(` in it is evaluated
by the shell before this script ever sees the text — that corrupted idea `000019` once. `--file`
and stdin never put prose in a shell argument.

## Expected result

The script generates the identifier and timestamp, validates the result against
`schemas/idea.schema.json`, and appends one line to `_data/ideas.jsonl`. There is deliberately no
flag to supply a timestamp — an override would be one flag away from anyone reading `--help`, and a
log whose times can be chosen is not evidence of anything.

## Failure and recovery

A schema validation failure prints the error and appends nothing — the log is never left with a
malformed line. A `status` transition not in the legal transition table is rejected before writing;
rerun with a legal `to` value. An `amend` targeting an idea with no `created` event, or clearing
title or body (both are required on every idea), is rejected before writing. `_data/ideas.jsonl` is
never hand-edited or corrected in place; a mistaken entry is superseded by a later event, not fixed.

<!-- generated:tool-reference:start -->

### Reference: `tools/append_idea.py`

The only sanctioned writer for `_data/ideas.jsonl`.

Ideas are an append-only event log. Nothing in it is ever edited, so a malformed line is
permanent — there is no correction path, only a longer history containing the mistake.
That is the whole reason this script exists instead of a convention: an agent formatting
its own entries will eventually format one wrongly.

The caller supplies prose. This script generates the identifier, the timestamp and the
event shape, validates the result against `schemas/idea.schema.json`, and appends it.

**There is deliberately no way to supply a timestamp.** The migration that needed one used
a separate tool which was deleted once it had run (see PLAN-016); an override living here
permanently would be one flag away from anyone reading --help, and a log whose times can be
chosen is not evidence of anything. The `at` parameters below are internal, reachable only
by import, and the CLI exposes no option that reaches them.

Usage:
    uv run python tools/append_idea.py add --title "..." --body "..."
    uv run python tools/append_idea.py add --title "..."     # body on stdin
    uv run python tools/append_idea.py add --file idea.md    # title = first line, rest = body
    uv run python tools/append_idea.py add                   # same, but from stdin
    uv run python tools/append_idea.py status 000007 reviewing
    uv run python tools/append_idea.py status 000007 promoted --promoted-to PLAN-016
    uv run python tools/append_idea.py revisit 000007
    uv run python tools/append_idea.py amend 000007 --title "corrected title"
    uv run python tools/append_idea.py amend 000007 --body "corrected body"
    uv run python tools/append_idea.py annotate 000007 --author repository-owner --kind note         --text "..."
    uv run python tools/append_idea.py amend-annotation 000007 <eid> --text "corrected text"
    uv run python tools/append_idea.py link 000007 --type relates_to --target 000003
    uv run python tools/append_idea.py retract-link 000007 <eid>

**`amend` corrects the idea's `created` event rather than rewriting it** — nothing in an
append-only log can be rewritten. It always targets that idea's `created` event by identity,
never a position, so the correction survives a rebase or a merge that interleaves two
branches' appended lines. Amending the same idea twice appends two corrections that both
survive (`src.db.ideas` merges a chain of amendments rather than keeping only the latest).
Title and body are the only amendable fields, and neither can be cleared — every idea must
have both.

**`annotate` adds a note, finding or assessment; it is permitted on every idea, terminal
included** — it extends the record, not the state machine (`PLAN-017.04`). A non-owner
`--author` (an agent) is restricted to `--kind finding`, so the owner's own voice in the log
stays unambiguous. `amend-annotation` corrects one annotation's text by its own `eid`
(printed when it was written); it never touches the others.

**`link` asserts a typed, one-directional edge to another idea** — `extends`, `supersedes` or
`relates_to` — and never mutates it afterward. `retract-link` is the one legal amendment: it
clears the target by the link's own `eid`, so the retraction is recorded rather than the edge
being silently repointed or deleted. An `extends` cycle or a `supersedes` edge whose target is
not `discarded` is flagged to stderr, never refused — capture always wins.

**`--title`/`--body` pass prose through the calling shell as quoted arguments.** Prose
containing a backtick or `$(` is not safe there — idea 000019 was corrupted exactly this
way, by a double-quoted `--body` whose command substitution the shell evaluated before this
script ever saw the text. `--file` (or plain stdin) never puts prose in a shell argument at
all: the first line of the file/stream is the title, everything after it is the body. Prefer
it for anything longer than a short, plain-text title.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--title` | one-line summary; omit to read title and body together (see --file) |  |  |  |
| `--body` | the idea in full; read from stdin when omitted |  |  |  |
| `--file` | read the title (first line) and body (the rest) from a file — bypasses the shell entirely, so it is the safe route for prose that might contain backticks, $(...), quotes or newlines |  |  |  |
| `idea` | six-digit idea id |  |  |  |
| `to` |  |  |  |  |
| `--promoted-to` | one or more governed document codes, required when promoting |  |  |  |
| `idea` | six-digit idea id |  |  |  |
| `idea` | six-digit idea id |  |  |  |
| `--title` | the corrected title |  |  |  |
| `--body` | the corrected body |  |  |  |
| `idea` | six-digit idea id |  |  |  |
| `--author` | repository-owner or an agent name |  |  | yes |
| `--kind` |  |  |  | yes |
| `--text` | the contribution itself |  |  | yes |
| `idea` | six-digit idea id |  |  |  |
| `eid` | identity of the annotation to correct |  |  |  |
| `--text` | the corrected text |  |  | yes |
| `idea` | six-digit idea id |  |  |  |
| `--type` |  |  |  | yes |
| `--target` | six-digit idea id this edge points to |  |  | yes |
| `idea` | six-digit idea id |  |  |  |
| `eid` | identity of the link to retract |  |  |  |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
