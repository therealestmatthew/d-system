---
schema_version: 1
id: doc-session-per-idea-trace-pages
code: SESS-2026-10-04-03
title: Build the per-idea trace pages
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-html]
depends_on: [doc-html-generation-design-system]
---

# Build the per-idea trace pages

## Phase

`phase-des-11` — Build the per-idea trace pages.

## Verification

`uv run pytest`

```text
1412 passed, 1 skipped, 1 warning
```

`uv run python -m src.governance`

```text
Governance OK: 43 systems, 425 documents, 36 memories, 347 backlog phases
```

`uv run python tools/check_no_private_content.py`

```text
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (1280 tracked files, 0 identifiers checked)
```

The worktree cannot see `_private/portfolio/`, so the content half of that check read no
identifiers. It was rerun from the worktree with the 140 trace pages staged, taking the identifier
list from the primary checkout through the script's own `confidential_identifiers()` and
`check_content()`: `1288 tracked files (pages staged), 31 identifiers, 0 violations`.

Behavioural checks done by hand:

- The trace page for `000236` was rendered in headless Chrome with JavaScript disabled. Capture,
  plan, phases, delivery and the gate table all render (R12).
- The two dated entries on that page were checked against `git log` by hand. `PLAN-029` reads
  `draft` at `c7b2f62` and `active` at `3da1295` (2026-09-15), the date and commit the page gives
  for G3. `phase-idg-01` reads `active` at `ea3635a` and `complete` at `4a95e12` (2026-09-25), the
  date and commit the page gives for G4 and G5.
- Three mutations of the generator were run against the new tests, and each made a test fail:
  dating a phase by its latest `complete` commit instead of its earliest, accepting any plan status
  at G3, and dropping `promoted_to` from the traced set.

## Acceptance

- REQ-036 R19 (the set of trace pages equals the set of linked ideas): Met.
  `test_trace_pages_are_exactly_the_linked_ideas` compares the rendered `trace/` set with the
  ideas that carry `promoted_to` or appear in a phase's `ideas` field, read without the generator.
  `test_ledger_links_each_traced_idea_and_no_other` checks the ledger column for all of them.
  `main` removes a trace page whose idea lost its last link (`test_a_stale_trace_page_is_removed`).
  140 pages are committed.
- REQ-036 R20 (each gate entry for a known idea matches the git log and the fold): Met.
  `test_a_known_idea_traces_to_the_git_log_and_the_fold` covers `000236`. It checks G1 against
  `fold()`, G2 as not recorded, and G3 against a separate walk of `PLAN-029`'s file history. It
  checks G4 and G5 against a separate walk of every first-parent version of `backlog.yaml`, not
  only the generator's candidates, and the owner rulings against the fold's `assessment`
  annotations. The hand check above agrees.
- REQ-036 R07 to R13 still hold: Met. The byte-identical two-run test now compares every page,
  traces included. The colour-literal, house-family and no-script tests run over every page from
  `render_all`. The fold-only source test still passes. The private-content result is above.

## Backlog

`status: active`. The phase stays active until the branch is merged onto `dev` with the owner's
approval (the Session Manager's contract). The completion edit is made on `dev` after that merge.

## Unresolved

- A historical `dev` commit, `5ec45ea`, holds a `backlog.yaml` that does not parse as YAML. The
  generator's line scan reads it; a full YAML parse of that version fails. Nothing else in this
  phase depends on it.
