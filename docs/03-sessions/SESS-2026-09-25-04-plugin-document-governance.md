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
200 passed
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
Governance OK: 43 systems, 363 documents, 32 memories, 318 backlog phases
```

Also run for the Session Manager's merge gate: `uv run pytest` → `1115 passed, 1 warning`;
`uv run ruff check src/ test/` → `All checks passed!`; `uv run mypy src/` → `Success: no issues
found in 46 source files`. Within the plugin, `uv run ruff check .` → clean. Plugin mypy is not a
gate and is not clean without help: run from inside `scripts/` as
`uv run mypy --ignore-missing-imports --explicit-package-bases *.py checks/*.py` it reports no
issues, but only because `--ignore-missing-imports` silences the missing `yaml` and `jsonschema`
stubs, which the scripts do not declare. Plain `uv run mypy scripts/` reports import errors
throughout the plugin's flat-package layout, plug-01's scripts included.

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
  plan-check names `plan_check.py`), `test_a_skill_runs_nothing_but_its_script` (every command in
  each skill's code blocks is its one script, with no redirection or chaining), and
  `test_the_next_code_skill_names_the_register_only_to_forbid_editing_it`.
- The R02 check passes — **Met.** `test/test_no_source_references.py` passes in the 200.

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

## Review

Independent adversarial review by a `demo-adversary` sub-agent (the owner chose the type), over
`dev...HEAD` at `c93943d`. It stopped at its turn limit once and was asked to report from what it had
established. It re-ran all four verification commands (197 passed at that commit, validation passed,
private-content check OK, governance OK) and the repo gates (1115 passed, ruff and mypy clean). Its
verdicts and findings, as reported:

- **Unknown kind, two worktrees, hand-edited catalog — Met.** Reproduced in fresh scratch git
  repositories with the scripts run by `uv run --no-project --script` from an unrelated directory:
  the unknown-kind error, `PLAN-001` then `PLAN-002` from two linked worktrees, and the
  catalog-differs error, each with the expected exit code.
- **plan-check — Met.** The template gives `OK`, exit 0; a fixture without Boundaries gives
  `missing: Boundaries`, exit 1. Fence handling matches the shell script's; the table and both
  conditional sections match. Resolving `depends_on` through a recursive scan is a superset of the
  shell's `docs/*/*.md` glob, not a loss.
- **Skills — Met**, with Finding 2.
- **R02 — Met.**

1. **[Should-fix] The record's plugin-mypy claim did not reproduce as stated.** Plain `uv run mypy
   scripts/` reports missing `yaml` and `jsonschema` stubs, which the scripts do not declare. With
   stubs installed, the `type: ignore[misc]` on `MetadataLoader` becomes unused. Not one of the
   phase's verification commands.
2. **[Note] The "no other write" clause of the skills condition was untested.** The test counted
   only `codes.yaml` paragraphs; the reviewer confirmed by reading that no skill instructs a write.
3. **[Note] Nothing outside the declared deliverables was touched**, and neither dispatcher was
   edited.
4. **Held, with no finding:** the reservation mutual exclusion and path-escape guards, the
   agreement between each skill's option exports and its script's flags, portability from a
   foreign working directory, the template placement against the scaffold's seed table, the
   owner's nine-series layout, the catalog's conditional phase table, and the `Scan` contract in
   `documents.py`'s docstring.

Left unconfirmed by the reviewer: a test-by-test diff of the ported tests against the source's, a
live symlink probe (covered by `test_a_symlink_is_reported_and_not_read`, which creates one), and
individual review of every assertion.

**Disposition.** Finding 1 is a correction to this record: `## Verification` now states the exact
mypy invocation and its limit instead of "no issues". The `type: ignore[misc]` stays, because the
plugin declares no stub packages and without them the ignore is needed. Finding 2 is fixed:
`test_a_skill_runs_nothing_but_its_script` checks that every command in each skill's code blocks,
after option assignments, is its one script, with no redirection or chaining. Finding 3 needs no
action.

## Decisions

- **The template register holds the nine source kinds in plain folders** under the document root
  (owner ruling). Series locations are relative to the document root, so a copied template
  follows a configured `docs_root`.
- **The plugin's codes schema makes `updated` optional, and its systems schema allows an empty
  systems list.** The scaffold copies templates verbatim, and a date in a template would breach
  R02, so the source's required date and non-empty list could not stand.
- **The documents check is silent when neither register exists.** The pre-existing dispatcher and
  portability tests run `check` on unscaffolded roots and require it clean. With one register or
  both present, every problem is reported, a missing catalog included.
- **Each module is also its command:** `codes.py` is `next-code`, `reservations.py` is
  `release-code` (and lists reservations), `documents.py` is `catalog`. `checks/documents.py`
  registers them, so `cli.py` stays unedited and every script's `--help` describes a real command
  for the tools reference.
- **The catalog shows plan phase counts only when a backlog file exists**, which settles
  PLAN-048.05's open question the way it leaned.
- **Scripts validate against the plugin's own `schemas/`**, not the scaffolded copies.
- **The reviewer type was `demo-adversary`**, chosen by the owner.

## Corrections

- The first code docstring carried a literal counter code, and a test fixture carried a literal
  operation code; the R02 check caught both and they were rewritten.
- The documents check first failed on unscaffolded roots; the rule above replaced it.
- The record's mypy statement overstated what was run (review Finding 1).

## Left undone

- The scaffold writes no catalog, so a freshly scaffolded repository fails the check until
  `catalog` runs once. The scaffold belongs to phase-plug-01's files.
- Plugin-wide mypy needs the scripts directory on the path and stub packages; making it a gate is
  a decision for the plugin as a whole, not this phase.

