---
schema_version: 1
id: doc-ops-check-no-private-content
code: OPS-009
title: Enforce the no-private-content boundary
kind: operation
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-delivery]
depends_on: [doc-governance-operations, doc-confidentiality-sweep]
---

# Enforce the no-private-content boundary

## Trigger

Run before every commit — via the pre-commit hook installed from
`tools/git-hooks/pre-commit` (`git config core.hooksPath tools/git-hooks` or copy the file into
`.git/hooks/pre-commit`) — and in CI, ahead of the governance gate. `phase-priv-04` added this as
the enforceable half of [ADR-009](../04-decisions/ADR-009-structure-content-boundary.md): a rule
that lives only in `.gitignore` protects against accident, not against `git add -f`.

## Command

```bash
uv run python tools/check_no_private_content.py
```

## Expected result

Exit 0 and a one-line `OK` summary. Two checks run:

1. **Path check**, always: no file `git ls-files` reports may live under `_private/`,
   `_private/portfolio/` or `_private/portfolio/projects/` — catches a forced add regardless of
   `.gitignore`.
2. **Content check**, only when `_private/portfolio/` exists on disk (the owner's machine; never a
   fresh clone or CI, so CI only ever runs the path check). The confidential-identifier list is
   derived at runtime from the real portfolio's project filenames and is never written to a tracked
   file — see the script's own docstring for the derivation rule and why a shared filename prefix
   is treated as a client identifier only when it is not also a tag kept on purpose in
   `_data/tags.json`.

`EXEMPT_IDENTIFIERS` in the script silences specific known non-leaks (a coincidental name
collision, or a real but lower-sensitivity leak deliberately deferred to a follow-up phase) — each
entry carries a one-line reason. It never silences the path check.

## Failure and recovery

A failure prints each violation as `<file>: matches confidential identifier '<id>'` or
`tracked file under a private path: <file>`. Remove the real content or path from the tracked tree
(move it under `_private/portfolio/`, or generalize the tracked doc) rather than adding an
exemption — an exemption is for a verified false positive or an explicitly deferred, named
exception, not a way to make the check pass.

<!-- generated:tool-reference:start -->

### Reference: `tools/check_no_private_content.py`

Fail when a tracked file leaks private portfolio content or paths.

Run before committing, or as a gate in CI / a pre-commit hook:
    uv run python tools/check_no_private_content.py

Two independent checks:

1. **Path check** (always runs). No file `git ls-files` reports may live under a
   private path (see PRIVATE_PATH_PREFIXES below). This catches `git add -f` of a
   private file, which `.gitignore` alone cannot: ignore rules only stop an
   unqualified `git add`.

2. **Content check** (runs only when `_private/portfolio/` exists on disk, i.e. on
   the owner's machine — never in a fresh clone or CI, so CI only ever runs the path
   check). The confidential-identifier list is derived at runtime from the real
   portfolio itself and is never written to a tracked file, since a tracked list of
   real client names and project IDs would be exactly the leak this script exists to
   prevent. Two kinds of identifier:

   - Every hyphenated project filename stem (a compound real project ID is content
     per ADR-009).
   - Any filename prefix shared by two or more projects, *unless* that token (or a
     tag id/label containing it) already appears in the tracked `_data/tags.json` —
     a repeated prefix that is also a deliberately-kept public tag (e.g. a platform
     name) is vocabulary, not a client identifier; one that is not is folded out of
     the tag registry on purpose, which is the signal that it is one.

   Matches use word boundaries against tracked file paths and content (case
   insensitive).

   EXEMPT_IDENTIFIERS silences specific known non-leaks: an identifier that
   coincidentally matches a structural document's own name (same string, different
   referent). It does not silence a path-check violation.

See PLAN-006 (docs/01-plans/PLAN-006-confidentiality-sweep.md) and phase-priv-04.

No CLI arguments.

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
