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
against a file of 13,278 lines, and the file is the repository's lock table — a broken parse
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

**Step 3 must gate the commit, not merely precede it.** Run the edit-and-verify script as its own
command and read its result before staging anything. A script that ends in an assertion is only a
check if a failed assertion stops what follows — chaining `git add`/`git commit` into the same block
after it means the commit runs regardless, and a broken file reaches history with a green-looking
transcript above it. This is `brain/procedures/a-check-that-cannot-fail-is-not-a-check.md` wearing a
different hat.

## The two ways it broke, 2026-09-22

Both happened while adding three scope lines to one phase. Each produced a `ParserError` at a line
number far from the actual edit, which is the characteristic symptom — YAML reports where the
structure became impossible, not where the mistake was.

**Indentation copied from the wrong source.** The new list items were written at column 0 (`- item`)
because that is how `yaml.safe_dump` had printed the phase when inspecting it. In the file, phase
list items sit at two spaces with four-space continuations (`  - item`). The additions parsed as
children of the previous item rather than siblings, and the block ended in the wrong place.

**A plain multi-line scalar quoted at its first line only.** `next_action` was an unquoted scalar
spanning eight lines — the `next_action:` line plus seven continuations. Replacing just its first
line with a single-quoted string left the seven continuation lines stranded after the closing quote. Two consequences worth remembering: a
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

## Corrected 2026-09-22 by an independent review

Two figures in the first draft of this procedure were wrong, and both were the same kind of mistake
this procedure exists to prevent — a number read off the wrong thing and not checked.

- The file was described as "roughly 9,600 lines". It is **13,278**. 9,600 was the *line number of
  the block being edited*, mistaken for the file's length.
- The broken scalar was described as spanning nine lines with eight continuations. It spans
  **eight** — one `next_action:` line plus **seven** continuations.

Neither error changes the guard, but a procedure that misreports the evidence it was written from
is weaker than one that does not. `wc -l` and `sed -n` settle both in one command each.


## Third instance, 2026-09-22, same day as the first two

A `: ` inside a plain scalar. The sentence "Links are unaffected: the owner approves every edge"
was appended to `next_action`, and a colon-space inside an unquoted scalar starts a mapping — the
exact hazard the **two ways it broke** section above already names in its last line.

Two things made this worse than the first two. The procedure warning against it had been written
four hours earlier by the same agent that then did it. And the verify step ran in a script whose
assertion failed, while the `git add` and `git commit` that followed were separate commands in the
same block — so the broken file was committed with the traceback visible directly above the commit
hash. The fix was a repair commit; nothing was pushed.

The rule that would have caught it, now step 3's second paragraph: the verification has to be able
to stop the commit. Writing the check and then stepping around it is not a check.
