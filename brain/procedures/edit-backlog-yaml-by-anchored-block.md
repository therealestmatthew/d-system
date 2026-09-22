---
id: mem-proc-edit-backlog-yaml-by-anchored-block
title: Edit backlog.yaml By Anchored Block, And Parse Before You Trust It
type: procedure
tags: [agentic-systems, automation, knowledge-base]
source_model: anthropic/claude-opus-5
project: d-system
created: 2026-09-22
updated: 2026-09-22
confidence: high
related: [mem-proc-check-that-cannot-fail, mem-proc-runtime-behavior-needs-runtime-evidence]
scope: project
---

## The rule

`docs/09-backlog/backlog.yaml` has **no sanctioned writer**. Every edit is hand-rolled text surgery
against a file of roughly 9,600 lines, and the file is the repository's lock table — a broken parse
blocks every agent, not just the one that broke it.

So: **edit by anchored block replacement, then parse the result before believing the edit worked.**
Never rewrite the whole file, and never assume a string replacement produced valid YAML because it
produced no error.

Four steps, in order:

1. **Read the real indentation first.** `sed -n '<start>,<end>p' docs/09-backlog/backlog.yaml | cat -A`
   shows it literally. Do not infer indentation from `yaml.safe_dump` output of the parsed item —
   the dump reformats, and its shape is not the file's shape.
2. **Anchor on an exact existing line, and assert the anchor is unique** (`s.count(anchor) == 1`)
   before replacing. A non-unique anchor silently edits the wrong phase.
3. **Parse, then diff item by item.** `yaml.safe_load` both the before and after text, assert the
   item count is unchanged, and list which ids actually differ. The expected output is exactly the
   phase you meant to touch. This is the step that catches a mangled edit while it is still cheap.
4. **Run `uv run python -m src.governance` and `uv run pytest`** afterwards, because a file can parse
   and still be wrong.

## The two ways it broke, 2026-09-22

Both happened while adding three scope lines to one phase. Each produced a `ParserError` at a line
number far from the actual edit, which is the characteristic symptom — YAML reports where the
structure became impossible, not where the mistake was.

**Indentation copied from the wrong source.** The new list items were written at column 0 (`- item`)
because that is how `yaml.safe_dump` had printed the phase when inspecting it. In the file, phase
list items sit at two spaces with four-space continuations (`  - item`). The additions parsed as
children of the previous item rather than siblings, and the block ended in the wrong place.

**A plain multi-line scalar quoted at its first line only.** `next_action` was an unquoted scalar
spanning nine lines. Replacing just its first line with a single-quoted string left the remaining
eight continuation lines stranded after the closing quote. Two consequences worth remembering: a
multi-line plain scalar must be replaced **whole**, and a plain scalar cannot contain `: ` — write
` - ` or restructure the sentence instead of reaching for a colon.

## Why this is a procedure and not just a fix

Nothing about either mistake was situational; both are reflexes any agent would reach for under the
same conditions — inspect a YAML item by dumping it, then edit the line you care about. The file's
absence of a writer is the standing condition that makes those reflexes dangerous.

The durable fix is a sanctioned writer, and it is already captured: idea `000240` (yaml.safe_dump
writes anchors into backlog.yaml) proposes `tools/append_backlog.py` doing block replacement with
alias validation, and idea `000224` records the whole-file write that silently reverted four
completed phases while the governance check still exited zero. Until one of those ships, this
procedure is the guard.
