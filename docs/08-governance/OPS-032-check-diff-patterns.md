---
schema_version: 1
id: doc-ops-check-diff-patterns
code: OPS-032
title: Check a branch's added lines for refused patterns before READY
kind: operation
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-governance]
depends_on: [doc-deterministic-guards-requirements, doc-deterministic-guards, doc-multi-session-coordination-protocol]
---

# Check a branch's added lines for refused patterns before READY

## Trigger

A builder runs it after rebasing and before sending `READY`
([GOV-017](GOV-017-multi-session-coordination-protocol.md)'s merge gate, `PROMPT-037` item 4).
It exists because `mypy` and `ruff` pass when a type error is silenced instead of fixed: no ruff
rule refuses a new `# type: ignore[arg-type]` (idea `000408`, `REQ-028` R08, `PLAN-045` D7).

## Command

```bash
uv run python tools/check_diff_patterns.py dev..HEAD
```

Run it from the branch worktree after `git rebase dev`, so `dev..HEAD` is exactly the branch's own
commits.

## Expected result

| Exit | Meaning | What happens |
|---|---|---|
| 0 | No refused pattern on a line the branch adds | `READY` carries the OK line |
| 1 | One or more findings, each `path:line: <pattern>: <the line>` | `READY` carries the list; the merge proceeds only with the owner's recorded sign-off naming the lines it accepts (`REQ-028` R10, `PLAN-045` D9) |
| 2 | The range is malformed, `git` failed, or a changed file does not parse at the head | No result: fix the cause and repeat it |

The three patterns, on added lines of Python files only:

- `type-ignore`: a `# type: ignore` comment whose code list is not exactly `[import-untyped]`;
- `cast-any`: a `cast(Any, ...)` call;
- `except-pass`: an `except` that is bare or catches `Exception` or `BaseException` and whose body
  is only `pass`. The `except` line is the one checked.

Comments and code are read from the file at the head with Python's own tokenizer and parser, so the
same text in a string literal, a docstring or a Markdown file is not reported. Unchanged and
removed lines are never reported, and neither is an `except` naming a specific type, such as
`except FileNotFoundError: pass`. The 25 existing ignores and the existing broad handlers are out of
scope (`PLAN-045`'s non-goals).

## Failure and recovery

- **A justified ignore.** Some stubs are genuinely wrong. The owner's sign-off names the line and
  the reason, and the comment in the code should say the same.
- **`does not parse at head`.** The branch commits a Python file with a syntax error; `pytest` or
  `ruff` would fail on it too.
- **`git diff` failed.** The range names a ref that does not exist in this worktree; check
  `git rev-parse dev`.

<!-- generated:tool-reference:start -->

### Reference: `tools/check_diff_patterns.py`

Refuse three patterns on lines a branch adds (REQ-028 R08).

A builder runs it before `READY` over the branch's own commits (GOV-017's merge gate, PROMPT-037
item 4):

    uv run python tools/check_diff_patterns.py dev..HEAD

For every Python file the range adds or modifies, it reads the file as it stands at `<head>` and
reports each of these whose line is an added line of the diff:

- a `# type: ignore` comment whose code list is not exactly `[import-untyped]` (a bare ignore, a
  different code, or more than one code);
- a `cast(Any, ...)` call (`cast` or `typing.cast`; `Any` or `typing.Any`);
- an `except` clause that is bare or catches `Exception` or `BaseException` (alone or in a tuple)
  and whose body is only `pass`. The line reported is the `except` line, so an `except` that was
  already there is not reported when only its body changes.

Comments are found with `tokenize` and calls and handlers with `ast`, so the same text inside a
string literal, or in a Markdown file, is never reported. Unchanged context lines and removed lines
are never reported. An `except` naming a specific exception type with a `pass` body is not
reported.

- exit 0: none of the three patterns on an added line;
- exit 1: one or more findings, each printed as `path:line: <pattern>: <the line>`;
- exit 2: the range is malformed, `git` failed, or a changed file does not parse at `<head>`.

A nonzero result blocks the merge unless the owner signs off naming the lines it accepts
(REQ-028 R10, PLAN-045 D9).

See PLAN-045 D7 (docs/01-plans/PLAN-045-deterministic-guards.md), phase-grd-03.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `range` | The commit range, as <base>..<head> |  |  |  |
| `--repo` | Repository to read |  |  |  |

Exit codes found in source: 0, 1, 2.

<!-- generated:tool-reference:end -->
