---
schema_version: 1
id: doc-schema-consistency-testing
code: PLAN-035
title: Schema consistency and testing (P8)
kind: plan
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-15'
systems: [sys-contracts, sys-delivery]
depends_on: [doc-schema-consistency-testing-requirements, doc-adr-file-based-governance]
---

# Schema consistency and testing (P8)

## Summary

Programme `P8` of the twelve. Eight ideas across four groups: making drift between schema, DDL,
fixtures and CI mechanically impossible. Distinct from `P2`, which is document hygiene where this is
code and contract hygiene.

| Group | Ideas | What it covers |
|---|---|---|
| `G33` Schema/DDL drift and contract compiler | `000024`, `000035`, `000052` | The concrete drift, and the general compiler proposed to fix it |
| `G34` Testing strategy | `000001`, `000026`, `000057` | The missing `ts/` gate, HTML-generation fixtures, and what "tested" means per layer |
| `G35` Overview drift test | `000106` | One pytest mirroring the `ideas.md` pattern |
| `G36` Layout-schema test | `000098` | **Already shipped. No work remains.** |

Partition-time sizing was 4–5 phases. This plan lands **six**, and two groups came out very
differently from their descriptions — because both were checked against the repository first.

## What was checked before anything was sized

### `G36` is delivered, and that is the phase's third acceptance condition

```
$ ls schemas/workbench-layout.schema.json
schemas/workbench-layout.schema.json

$ uv run pytest test/test_workbench_layout_schema.py -q
21 passed, 2 warnings
```

`000098` asked for the layout-schema test `ADR-016` promised, observing that "no `schemas/*layout*`
definition, no `test/` reference" existed. Both exist now. The idea is already `discarded` on the log
under the owner's ruling of 2026-09-13 — "verified resolved", one of three ideas that ruling names as
having misled three analysts in the partition sweep itself.

**`G36` gets no implementation phase**, and the reason is recorded with the evidence above rather than
asserted.

### `G33`'s drift is closed; two other halves of `000024` survive

`000024` reports four entities mapped in `ENTITY_DIRECTORIES` with "no DDL table, no data directory,
and no CLAUDE.md mention". Checked, claim by claim:

```
$ grep -in "create table" sql/001_schema.sql
81:CREATE TABLE interactions (    94:CREATE TABLE decisions (
112:CREATE TABLE waiting_on (    128:CREATE TABLE development_events (

$ grep -in "interaction\|decision\|waiting\|development_event" tools/rebuild_db.py
54: "development_events",  55: "waiting_on",  56: "decisions",  57: "interactions",
209: for path in _glob(entities / "interactions", "*.json"):
```

- **No DDL table — now false.** All four exist, and `tools/rebuild_db.py` loads all four.
- **No data directory — still true, and deliberately not a defect.** None of `_data/interactions`,
  `_data/decisions`, `_data/waiting-on` or `_data/development-events` exists:

  ```
  $ ls _data/
  commitments  ideas.jsonl  people  projects  tags.json  tasks  workbench
  ```

  `source_validation.py:170` reads `if not source.is_dir(): continue`, and the comment above
  `ENTITY_DIRECTORIES` states the intent: *"A directory that does not exist yet is not an error; the
  capture pipeline creates them as records appear."* A missing directory and an empty one are
  treated identically, so this half of `000024` describes designed behaviour rather than drift.
- **No `CLAUDE.md` mention — still true, and wider than stated.** `CLAUDE.md` names four schema files
  and seven DDL tables. `schemas/` holds twenty definitions; `sql/001_schema.sql` creates sixteen
  tables.

**So one of `000024`'s three claims closed, one is designed behaviour, and one is a real remaining
gap.** The claim that closed is the one `000035`'s compiler was proposed to prevent.

So the *drift* `000024` identified — schema validated with no table behind it — closed through
ordinary work. What survives is one benign absence and one real documentation gap, the latter in a
file no agent may edit.

## The chosen design

### 1. `G33` commits to `000024`, and `000035` is decided later on evidence

The phase's scope requires choosing between them before sizing either. **Ruled: `000024`.**

`000035` proposes making JSON Schema the single executable contract source — generating Python
models, TypeScript types, OpenAPI fragments and valid/invalid fixture factories, with mutation-based
checks. It is a substantial build, and its stated motivation is the drift `000024` found.

That motivation has largely evaporated. The schema/DDL/loader drift closed without a compiler, by
someone adding the tables and loaders in the course of other work. Committing to build a contract
compiler now would be building a machine to prevent a class of defect whose only recorded instance
has already healed.

So `phase-sch-01` fixes what remains of `000024` — the documentation half — and adds the small
mechanism whose absence let the drift go unnoticed: a check comparing the schema layer's consumers
against `schemas/`.

**That check has to span the boundaries `000035` targets, or the deferral is circular.** A check
covering only `CLAUDE.md`, `schemas/` and the DDL would report clean indefinitely while drift between
schemas and Pydantic models, or schemas and TypeScript types, went unmeasured — and `phase-sch-02`
would then read "zero recurrences" from a check that never looked. So `R03` spans `CLAUDE.md`, the
DDL **and** `src/models/`, and `R04` requires the decision to state which boundaries its evidence
covers.

This is the correction to the first draft of this ruling, which specified the narrow check. "The
drift closed on its own" is also weaker than it first sounds: it closed because someone noticed and
fixed it, which is exactly the manual vigilance `000035` proposes to replace. The deferral is
defensible only if what replaces the compiler is actually measuring the right thing.

`R04` forbids deciding from the proposal's own persuasiveness, and `R05` requires a named trigger.
Building `000035` remains a legitimate outcome — the row asks for evidence, not for a particular
answer.

The cost accepted: if drift is in fact systemic and the check only catches one facet of it, the
compiler arrives later than it might have. That is the right way round, because the reverse error —
a generation framework nobody needed, sitting between every schema change and its consumers — is much
harder to undo.

### 2. The remaining `000024` work is owner-executed, like `phase-conc-09`

The surviving gap is in `CLAUDE.md`, and `AGENTS.md`'s standing rule is absolute: no agent modifies
`CLAUDE.md` for any reason without the owner's explicit approval for that specific change.

`phase-sch-01` therefore writes the correction out as **proposed replacement text** and stops. `R02`
makes the absence of a `CLAUDE.md` edit in the phase's diff a checkable condition, so an agent that
"helpfully" applies it fails the row rather than merely breaking a rule.

This is the second owner-executed phase this batch has produced, after `phase-conc-09`'s `AGENTS.md`
rewrite. Both exist because the repository's two governing files are deliberately outside agent
reach, and both are sized so an agent can verify the result without being able to produce it.

### 3. `G34` is three phases, not two, because `000001` is genuinely dormant

The partition sizes `G34` at two and notes `000026` is "actionable today" while `000001` is "dormant
until `PLAN-003` builds". Both observations hold. `000026` is confirmed open:

```
$ grep -n "npm\|ts/" .github/workflows/ci.yaml
40:      - run: npm ci
41:      - run: npm run build
```

Build and nothing else — no lint, no test runner. So `phase-sch-03` is claimable now.

`000001` gets a **`deferred`** phase with a gate naming `PLAN-003`, rather than being folded into
`000057`'s strategy or omitted. Folding it would bury three specific decisions — where fixtures live,
generated versus hand-authored, governed artifact versus test asset — inside a document about
philosophy. Omitting it would lose them. The backlog's `deferred` plus `resume_when` is the mechanism
for exactly this, and `P7` used it the same way earlier tonight.

### 4. `G35` mirrors the existing pattern rather than inventing one

`000106`'s gap is real and narrow:

```
$ grep -rn "def test_" test/test_generate_overview.py
54: test_two_generations_via_generate_produce_byte_identical_output
61: test_two_cli_runs_write_byte_identical_files
...
$ grep -rn "committed_markdown_matches_regenerated" test/test_ideas.py
775: def test_the_committed_markdown_matches_regenerated_output() -> None:
```

The overview has **determinism** tests — two runs agree with each other — and no **drift** test. The
distinction is the whole idea: determinism proves the generator is a pure function; drift proves the
committed artifact is what the generator currently produces. `000106` records a real case where that
gap let a stale page ship.

`R08` requires the new test to mirror `test_ideas.py`'s pattern rather than invent a second one, so
the repository has one shape for this assertion and not two.

### Which of these need a decision record

**One.** `phase-sch-02`'s ruling on `000035` needs an ADR whichever way it goes: building a contract
compiler commits every future schema change to a generation pipeline, and declining it commits the
repository to hand-maintained consistency with a check. A future reader needs to know which was
chosen and on what evidence.

`G33`'s commitment to `000024` (decision 1) needs none — it is recorded here and in `REQ-020`'s rows,
and it is a sequencing choice rather than an architectural commitment. Decisions 2, 3 and 4 are
recorded where the reader meets them.

## Implementation phases

Six phases under `phase-sch-*`, registered in [the backlog index](../09-backlog/README.md).

| Phase | Title | Group | Status | Depends on |
|---|---|---|---|---|
| `phase-sch-01` | Record `000024`'s real state, propose the `CLAUDE.md` text, and add the drift check | `G33` | `queued` | — |
| `phase-sch-02` | Decide `000035`'s contract compiler against recorded drift evidence | `G33` | `queued` | `01` |
| `phase-sch-03` | Add a lint and test gate for `ts/` to CI | `G34` | `queued` | — |
| `phase-sch-04` | Write the per-layer testing standard | `G34` | `queued` | `03` |
| `phase-sch-05` | Add the committed-output drift test for the overview page | `G35` | `queued` | — |
| `phase-sch-06` | Design HTML-generation fixtures | `G34` | `deferred` | gated on `PLAN-003` |

### Sizing against the partition

Group ranges were `G33` 2–3, `G34` 2, `G35` `<1`, `G36` 0 — 4–5 total. This plan lands **six**: `G33`
at 2, `G34` at **3**, `G35` at 1, `G36` at 0.

`G34`'s extra phase is decision 3 — `000001` gets its own `deferred` phase rather than being folded or
dropped. `G33` lands at the bottom of its range because the drift half of `000024` turned out to be done.
`G36` at zero is the acceptance condition, and is the only group in this programme whose partition
sizing was already correct.

## Execution order and real concurrency

Three phases declare `depends_on: []` — `phase-sch-01`, `-03` and `-05` — and they touch genuinely
different surfaces: governance documentation and a check, CI configuration and `ts/`, and one pytest
over `_public/`. **This is the widest real concurrency in any programme this batch has planned.** All
three can run at once, which is unusual here and worth using.

`phase-sch-05` is also the cheapest phase in the whole batch: one test mirroring an existing one.

The critical path is two deep, twice over: `01` → `02`, and `03` → `04`.

## Requirement coverage

Every row of `REQ-020` maps to at least one phase, and every phase carries at least one row.

| Requirement | Phases |
|---|---|
| R01 `000024`'s current state recorded against the repository | `phase-sch-01` |
| R02 The `CLAUDE.md` correction proposed, never applied | `phase-sch-01` |
| R03 A check catches `CLAUDE.md`/DDL/schema divergence | `phase-sch-01` |
| R04 `000035` decided on recorded drift evidence | `phase-sch-02` |
| R05 The decision names what would change it | `phase-sch-02` |
| R06 CI lints `ts/` and fails on a violation | `phase-sch-03` |
| R07 CI runs a frontend suite and fails on a failing test | `phase-sch-03` |
| R08 A committed-output drift test for the overview | `phase-sch-05` |
| R09 A per-layer testing standard | `phase-sch-04` |
| R10 The standard names where coverage falls short | `phase-sch-04` |
| R11 Fixture location, provenance and governance decided | `phase-sch-06` |
| R12 `G36` gets no phase, with evidence | `phase-sch-01` |

## Key references

- **The requirement** — [REQ-020](../06-requirements/REQ-020-schema-consistency-testing.md).
- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P8`, including its `G36` "[RESOLVED]" marking, which this plan verified rather than trusted.
- **`AGENTS.md`** — the standing rule that puts `CLAUDE.md` outside agent reach, and the "Adding a domain entity" sequence `000035` proposes to automate.
- **The HTML generation plan** ([PLAN-003](PLAN-003-dynamic-html-generation/PLAN-003-overview.md)) — what `phase-sch-06` is gated on.
- **Concurrency, git safety and enforcement** ([PLAN-026](PLAN-026-concurrency-git-safety.md)) — `phase-conc-08`'s enforcement-placement rule should govern where `R03`'s check lives, if it has landed first.

## Known facts not to rediscover

- **`G36` is shipped.** Schema present, 21 tests passing, idea already `discarded`. Do not re-verify
  from scratch and do not size it.
- **`000024`'s DDL and loader gaps are closed.** All four tables exist and `rebuild_db.py` loads them.
  Only the `CLAUDE.md` half survives.
- **The four entity directories do not exist, and that is not a defect.** `source_validation.py:170`
  skips a directory that is not there, and the comment above `ENTITY_DIRECTORIES` says so explicitly.
  Do not "fix" this by creating empty directories; the capture pipeline creates them as records
  appear.
- **`CLAUDE.md` under-describes the schema layer by more than `000024` counted** — four schema files
  named against twenty present, seven tables named against sixteen created.
- **`phase-sch-02`'s evidence is only as good as `phase-sch-01`'s span.** If the check ships covering
  `CLAUDE.md` alone, a zero count means nothing was looking rather than nothing drifted. `R03` names
  the model boundary for that reason.
- **The overview has determinism tests but no drift test.** They are different assertions; do not read
  `test_two_generations_..._byte_identical_output` as covering `000106`.
- **`CLAUDE.md` is owner-only.** `phase-sch-01` proposes text and stops, exactly as `phase-conc-09`
  does for `AGENTS.md`.
- **`000098` is one of three ideas the owner's 2026-09-13 ruling names as having misled three
  analysts** during the partition sweep, because resolved work had not been marked resolved. That is
  `000204`'s systemic finding, and `P2`'s `phase-dgov-06` is the nearest mechanism to it.
