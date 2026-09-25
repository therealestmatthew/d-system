---
schema_version: 1
id: doc-session-plugin-document-governance
code: SESS-2026-09-25-04
title: The plugin's document-governance engine
kind: session
status: active
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-documents]
depends_on: [doc-idea-realization-plugin-document-governance]
---

# The plugin's document-governance engine

## Phase

`phase-plug-05` — Document-governance engine: check, next-code with reservations, catalog,
plan-check.

## Verification

Run in `/code/d-system-worktrees/phase-plug-05` on `agent/phase-plug-05`, rebased onto dev
`dccf952`.

```
$ cd plugins/idea-realization && uv run pytest
197 passed
```

```
$ claude plugin validate plugins/idea-realization --strict
✔ Validation passed
```

```
$ uv run python tools/check_no_private_content.py
check_no_private_content: OK (961 tracked files, 0 identifiers checked)
```

The worktree has no `_private/portfolio/`, so the content half of that check had no identifiers to
look for; the path half ran. The same check ran with 31 identifiers in the primary checkout at the
claim commit.

```
$ uv run python -m src.governance
Governance OK: 43 systems, 362 documents, 32 memories, 318 backlog phases
```

Also run for the Session Manager's merge gate: `uv run pytest` → `1115 passed, 1 warning`;
`uv run ruff check src/ test/` → `All checks passed!`; `uv run mypy src/` → `Success: no issues
found in 46 source files`. Within the plugin, `uv run ruff check .` → clean, and mypy over
`scripts/` with that directory on the path → no issues.

## Acceptance

- A fixture document with an unknown kind fails check; two next-code calls from two worktrees of a
  temporary repository return different codes; a hand-edited catalog fails check — **Met.**
  `test_a_document_with_an_unknown_kind_fails_check`,
  `test_two_next_code_commands_from_two_worktrees_return_different_codes` (runs `cli.py next-code
  plan` as a subprocess in each worktree: `PLAN-001`, then `PLAN-002`), and
  `test_a_hand_edited_catalog_fails_check`.
- plan-check exits 0 on the plan template and 1 on a fixture missing the boundaries section — **Met.**
  `test_the_plan_template_passes`, and
  `test_a_draft_missing_its_boundaries_section_fails_and_names_it` (stdout is exactly
  `<draft>: missing: Boundaries`).
- Each of the three skills names exactly one script and no other write; a grep of the next-code
  skill for `codes.yaml` finds only the statement that the register is never edited by hand —
  **Met.** `test_each_skill_runs_exactly_one_script` (next-code and catalog name `cli.py`;
  plan-check names `plan_check.py`) and
  `test_the_next_code_skill_names_the_register_only_to_forbid_editing_it`.
- The R02 check passes — **Met.** `test/test_no_source_references.py` passes in the 197.

## Backlog

`status: active`, `agent: agent-builder-a`, `session: doc-session-plugin-document-governance`.
`next_action`: every acceptance condition is met on `agent/phase-plug-05`; awaiting the independent
review's findings and the owner's merge approval, after which the completion edit is made on dev.

## Unresolved

- A freshly scaffolded repository fails the documents check until the `catalog` command runs once,
  because the scaffold does not write a catalog. The failure names the command to run.
- The scaffold's `.idea-realization/schemas/` copies are not what the check reads: every script
  validates against the plugin's own `schemas/`. The copies are for people and other tools, and the
  doctor reports drift in them.
