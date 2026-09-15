---
schema_version: 1
id: doc-schema-consistency-testing-requirements
code: REQ-020
title: Schema consistency and testing requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-contracts, sys-delivery]
depends_on: [doc-adr-file-based-governance]
---

# Schema consistency and testing requirements

## Observed problem and scope

Making drift between schema, DDL, fixtures and CI mechanically impossible. Eight ideas across four
groups — and **the most important thing this requirement can say is what the repository checked and
found already fixed.**

### What was verified, before anything was sized

**`G36` is delivered.** `schemas/workbench-layout.schema.json` exists and
`test/test_workbench_layout_schema.py` passes 21 tests. Idea `000098` is already `discarded` on the
log, by the owner's ruling of 2026-09-13 ("verified resolved"). It gets no phase.

**`G33`'s concrete drift is mostly closed too, which changes the group's whole shape.** `000024`
reports that `src/db/source_validation.py`'s `ENTITY_DIRECTORIES` maps four entities —
`interactions`, `decisions`, `waiting-on`, `development-events` — with "no DDL table, no data
directory, and no CLAUDE.md mention". Checked:

```
$ grep -in "create table" sql/001_schema.sql
81:CREATE TABLE interactions (      94:CREATE TABLE decisions (
112:CREATE TABLE waiting_on (      128:CREATE TABLE development_events (

$ grep -in "interaction\|decision\|waiting\|development_event" tools/rebuild_db.py
54: "development_events",  55: "waiting_on",  56: "decisions",  57: "interactions",
209: for path in _glob(entities / "interactions", "*.json"):
```

All four tables exist, and `tools/rebuild_db.py` loads all four — so the schema-validated-with-no-
table-behind-it drift is gone.

The data directories, by contrast, **still do not exist**, and that is designed rather than drifted:

```
$ ls _data/
commitments  ideas.jsonl  people  projects  tags.json  tasks  workbench
```

`source_validation.py:170` is `if not source.is_dir(): continue`, and the comment above
`ENTITY_DIRECTORIES` states the intent: *"A directory that does not exist yet is not an error; the
capture pipeline creates them as records appear."* A missing directory and an empty one are handled
identically, so this half of `000024` needs no fix.

**What remains as a real gap is documentation drift in `CLAUDE.md`, and it is wider than the idea
states.** `CLAUDE.md` names four schema files and seven DDL tables. `schemas/` holds twenty
definitions and `sql/001_schema.sql` creates sixteen tables. So the file under-describes the schema
layer by more than the four entities `000024` counted.

That matters for `G33`'s central question, because `000035`'s contract compiler was proposed to
prevent exactly the drift `000024` identified — and that drift closed through ordinary work, without a
compiler.

### What is genuinely open

1. **CI does not test or lint the frontend.** `.github/workflows/ci.yaml`'s frontend job runs `npm ci`
   and `npm run build`, and nothing else. No eslint config exists under `ts/`, no test runner is
   configured in `ts/package.json` (`000026`).

2. **The overview page has no drift test.** `test/test_ideas.py:775`'s
   `test_the_committed_markdown_matches_regenerated_output` asserts `docs/00-working/ideas.md` always
   matches a fresh regeneration. `test/test_generate_overview.py` has determinism tests — two runs
   produce byte-identical output — but **nothing asserts the committed
   `_public/overview/index.html` matches a regeneration**. That gap let a real drift ship silently
   (`000106`).

3. **No stated testing philosophy per layer.** Backend routes, frontend components, generation
   scripts and agent-facing tools like `tools/append_idea.py` have no shared answer to what "tested"
   means (`000057`).

4. **HTML-generation fixtures are undesigned and dormant**, pending `PLAN-003` (`000001`).

This requirement covers the schema consistency and testing programme (`P8`). It does **not** cover
document hygiene — that is `P2`. The boundary is that `P2` governs what a correct governed *document*
is, and `P8` governs code and contract hygiene.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | `000024`'s current state is recorded against the repository: which of its three claims still hold and which closed, each verified by a command whose output distinguishes the cases. | Read the record against `sql/001_schema.sql`, `tools/rebuild_db.py` and `_data/`. Confirm the DDL and loader claims are recorded as closed, and the data-directory claim as still true but not a defect. Confirm the directory check distinguishes *absent* from *empty* — `ls _data/x 2>/dev/null \| wc -l` returns `0` for both and settles neither. |
| R02 | The `CLAUDE.md` correction is written out as proposed text for the owner, and not applied by an agent. | Confirm the phase's diff contains no `CLAUDE.md` edit. `AGENTS.md` and `CLAUDE.md` are owner-only; the deliverable is exact replacement wording. |
| R03 | A check fails when `CLAUDE.md`'s stated tables or schema files diverge from `sql/001_schema.sql` and `schemas/`. | Add a table to the DDL without updating `CLAUDE.md` and confirm the check fails and names the divergence. Confirm it passes once the text matches. This is the mechanism `000024`'s drift went unnoticed for want of. |
| R04 | `000035`'s contract compiler is decided against recorded drift evidence, not against its own proposal. | Read the decision for the drift instances it weighs. Confirm it counts what `R03`'s check has actually caught since shipping. A decision to build made with zero recorded recurrences has not used evidence. |
| R05 | The decision states what would change it, in terms a later reader can evaluate. | Read for a named trigger — a count of drift instances, a new entity type, a second consumer of the schemas. "Revisit later" is not a trigger. |
| R06 | CI runs a linter over `ts/` and fails the build on a lint error. | Introduce a lint violation and confirm CI fails naming it. Confirm a clean tree passes. |
| R07 | CI runs a frontend test suite and fails the build on a failing test. | Add a deliberately failing test and confirm CI fails. Confirm the runner is configured in `ts/package.json` rather than invoked ad hoc. |
| R08 | A committed-output drift test asserts `_public/overview/index.html` matches a fresh regeneration. | Modify the committed page by hand and confirm the test fails. Confirm it mirrors `test_ideas.py`'s existing pattern rather than inventing a second one. |
| R09 | A testing standard states what "tested" means per layer — backend routes, frontend components, generation scripts, and agent-facing tools. | Read for one entry per layer, each naming what is covered and what is deliberately not. A layer with no entry has not been reasoned about. |
| R10 | The standard is derived from what the repository already does, and names where current coverage falls short of its own rule. | Read for citations to existing test files on both sides. A standard that finds the current state already conformant has not been applied. |
| R11 | HTML-generation fixtures state where they live, whether they are generated from `_data/` or hand-authored, and whether a fixture is a governed artifact or a test asset. | Read for all three. `000001` names them as the decisions that get discovered late; this row makes them decided early instead. |
| R12 | `G36` receives no implementation phase, and the reason is recorded with its evidence. | Confirm no phase covers `000098`. Confirm the record cites the shipped schema and the passing test count rather than asserting delivery. |

## What each requirement is not

**R02 is not a `CLAUDE.md` edit.** No agent may make one, for any reason. The deliverable is proposed
wording the owner applies, in the same shape `phase-conc-09` uses for `AGENTS.md`.

**R03 is the small mechanism that replaces a large one.** A check comparing three files is cheap and
catches recurrence at the moment it happens. It is not a contract compiler and does not pretend to
generate anything.

**R04 does not presume the answer.** Building `000035` is a legitimate outcome if the evidence
supports it. What the row forbids is deciding from the proposal's own persuasiveness, which is the
only evidence available today.

**R08 is not a determinism test.** `test/test_generate_overview.py` already proves two runs agree with
each other. This row asks whether the *committed file* agrees with a run — a different assertion, and
the one whose absence let drift ship.
