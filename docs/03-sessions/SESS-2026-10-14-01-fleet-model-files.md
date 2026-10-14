---
schema_version: 1
id: doc-session-fleet-model-files
code: SESS-2026-10-14-01
title: Fleet model governance document, fleet schemas, fleet.yaml and definitions.yaml, and their tests (phase-rep-01)
kind: session
status: active
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: [sys-fleet, sys-gov-docs]
depends_on: [doc-agent-replicator, doc-agent-replicator-requirements]
---

# Fleet model governance document, fleet schemas, fleet.yaml and definitions.yaml, and their tests (phase-rep-01)

## Phase

`phase-rep-01` — Fleet model governance document GOV-023, three fleet schemas, fleet.yaml and
definitions.yaml, and the schema, integrity and enum-agreement tests. Built by Session 3 - Standby
Builder as `agent-standby-3` on `agent/phase-rep-01`, under the Session Manager's owner-approved
`ASSIGN` of 2026-10-13.

## Verification

Run in `../d-system-worktrees/phase-rep-01` on 2026-10-14, after the rebase onto `dev` `bf39e7c1`.

```
$ uv run pytest test/test_fleet_files.py
41 passed, 1 warning in 1.21s

$ ! grep -n "Session Manager\|GOV-017" test/test_fleet_files.py
(no output; exit 0)

$ uv run ruff check src/ test/ tools/
All checks passed!

$ uv run python -m src.governance --catalog
(exit 0; git diff --stat afterwards is empty, so the committed catalog is current)

$ uv run python -m src.governance
Governance OK: 46 systems, 485 documents, 38 memories, 364 backlog phases
```

Beyond the list: the full suite passed in the worktree before the rebase (`2308 passed, 1 warning
in 630.67s`). `uv run python -m src.governance --containment phase-rep-01` reported
`phase-rep-01: no undeclared changes (dev...agent/phase-rep-01)`.

## Acceptance

- GOV-023 exists and the enum-agreement test fails on a fixture with an extra edge type — **Met.**
  `docs/08-governance/GOV-023-fleet-model.md` exists.
  `test_enum_agreement_fails_on_a_fixture_list_with_an_extra_edge_type` substitutes
  `test/fixtures/fleet/enum-extra-edge-type.json` for the schema's edge-type list and asserts the
  single disagreement `Edge types: supervises is in the schema only`. The fixture is the value list,
  not a whole schema file, so it cannot drift from the real schema's other lists. A second test
  checks the other direction.
- fleet.yaml and definitions.yaml pass their schemas; a bypass-mode fixture fails, and a definition
  fixture without launcher fails — **Met.** `test_tracked_fleet_files_pass_their_schemas` passes.
  `invalid/definitions-bypass-mode.yaml` and `invalid/definitions-session-without-launcher.yaml`
  fail, among 11 invalid fixtures.
- The integrity test fails on one fixture per broken reference kind and passes on the tracked files —
  **Met.** `test_tracked_fleet_references_resolve` passes. Each of the 17 `broken/<case>/` fixtures
  passes its schema and gives exactly one reference error, matching its expected text in `EXPECTED`.
  `test_every_broken_case_has_an_expected_error` keeps that table complete.
- The test code names no session, role, system or document — **Met.** The negated grep exits 0. The
  model document is found through `fleet.yaml`'s `model_document`, and each value list through its
  schema `$comment`. `test_this_test_names_nothing_the_fleet_files_supply` makes the same check
  inside the suite, against every name the tracked fleet files supply. A probe copy with
  `# Owner Terminal` appended failed it with `AssertionError: assert ['Owner Terminal'] == []`, and
  the probe was deleted.

## Backlog

`phase-rep-01`: `status: active`, `agent: agent-standby-3`. `session`, `completion_evidence` and
`result` are recorded on the branch. `next_action`: `READY`; completion at the merge, under
`GOV-017`.

## Unresolved

- The phase's deliverables first omitted `docs/08-governance/codes.yaml`. Governance requires
  `GOV-023`'s reservation to be released in the same change. The Session Manager granted a
  declaration amendment, owner-approved 2026-10-14, at `dev` `bf39e7c1`, which also covers
  `phase-rep-02` for `OPS-034`.
- `fleet.yaml` enables no system yet. `phase-rep-07` adds the three system files and enables them.

## Review

Dispatched by the Session Manager at `c864d660`; the runner passed (`_working/review-checks/phase-rep-01/c864d660cea8/`).

- `docs/08-governance/reviews/verdicts/2026-10-14-phase-rep-01-demo-adversary.json` — gating,
  verdict `pass`, no findings.
- `docs/08-governance/reviews/verdicts/2026-10-14-phase-rep-01-review-judge.json` — shadow, verdict
  `pass`, two minor findings:
  - **F01** "sys-fleet's paths in systems.yaml omit test/fixtures/fleet/." **Fixed:**
    `test/fixtures/fleet/` added to `sys-fleet`'s paths.
  - **F02** "The review runner did not run the phase's negated-grep verification." The runner's
    `is_command` (`tools/run_review_checks.py`) skips a line that starts with `!`. The Session
    Manager confirmed it and is sending the runner defect to Ideation, since it also affects the
    `! grep` lines in `phase-rep-02`, `-03` and `-04`. **Fixed for this phase:** the same check
    is now `test_this_test_names_nothing_the_fleet_files_supply`, which the runner does run through
    `uv run pytest test/test_fleet_files.py`. The probe above showed it fails on a planted name.

The owner confirmed on 2026-10-14 the permission-mode order in GOV-023's overlay section (`plan`,
`dontAsk`, `manual`, `auto`); no change.

## Decisions

- **One shared definition for the interactive sessions** (`repo-session`), rather than one per
  session. A definition says how to start an agent (GOV-023). The eight auto-mode sessions of the
  interim roster start the same way. Their names and positions belong to roles, which `phase-rep-07`
  writes.
- **The GOV-014 roles with no agent file are `planned` definitions.** `phase-rep-07` can then
  reference them without editing `definitions.yaml`, which is outside its deliverables. The schema
  requires an `agent_file` once a subagent is `available`.
- **Every value list lives once, in `schemas/fleet.schema.json`.** The other two schemas `$ref` it,
  and each list's `$comment` names its GOV-023 section. A test fails if a list has no section.
- **`cwd` is relative to the host's `repo_root`.** The Owner Terminal's `..` is the directory above
  the repository, so no definition carries an absolute path.
- **`sys-fleet` is `scaffold`.** `in-progress` is not in `schemas/systems.schema.json`'s enum. The
  schemas and data exist; the core does not.

## Corrections

- `sys-fleet` was first set to `in-progress`, which the systems schema does not allow; it is now
  `scaffold`.
- A fixture's `kickoff_template` with unquoted braces broke YAML parsing for every fixture case. It
  is now quoted.
- The first test import of `yaml` carried a `type: ignore`, which the diff-pattern check flags and
  other tests do not use. It was removed.
