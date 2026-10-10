---
schema_version: 1
id: doc-sibling-repo-feature-migration
code: PLAN-053
title: Sibling-repository feature migration — six phases porting what survived adversarial review from life and autoclaude-api, and sixteen triaged ideas for everything that did not
kind: plan
status: draft
owner: repository-owner
created: '2026-10-10'
updated: '2026-10-10'
systems: [sys-portfolio, sys-capture, sys-contracts, sys-projection, sys-api, sys-gov-docs, sys-auto-ledger]
depends_on: [doc-sibling-repo-feature-migration-requirements, doc-idea-staging, doc-structure-content-boundary, doc-capture-requirements, doc-plan-quality-standard, doc-three-altitude-review-procedure, doc-planning-protocol]
---

# Sibling-repository feature migration

Delivers [REQ-038](../06-requirements/REQ-038-sibling-repo-feature-migration.md). Review record:
[`2026-10-10-plan-053`](../08-governance/reviews/2026-10-10-plan-053.json). The starter prompt
for the session that runs these phases is
[PROMPT-045](../02-prompts/PROMPT-045-sibling-repo-migration-runner.md).

## Context and scope

On 2026-10-10 the owner asked for a review of two sibling repositories, `life` and
`autoclaude-api`, and a proposal of features to integrate into d-system, then for an adversarial
review of that proposal, idea capture and triage, this plan with its phases and reviews, and a
pull request to `dev`. Three read-only surveys ran on Sonnet (one per repository), the proposal
was written as a document outside the repository, and one adversarial agent then checked every
claim in it against the three checkouts. The session record names the surveys and the review.

The adversary's ranked findings, and what this plan did with each:

| Finding | Severity | Disposition in this plan |
|---|---|---|
| The two token-ledger ports have no data: `_data/runs.jsonl` has never been written and `schemas/run.schema.json` has no `model` field (checked: `ls _data/`; the schema's `properties` list) | Blocked two ports | The cost fold is `phase-mig-06`, created `deferred` with a resume condition. The budget cap is idea `000678`, design input for `phase-irs-11` |
| The budget cap contradicts the owner's ruling on `phase-irs-11` (tokens only, per run, fail closed, no cap value; `backlog.yaml`, that phase's scope) | Blocked a port | Not ported. Idea `000678` records the one reusable part, the test pattern of a cap stopping a batch part-way |
| The sanitiser at capture time violates `REQ-002` R1 and R2 (`src/capture/raw.py` stores verbatim) | Changed a row | Applied where the structuring agent reads the capture, with provenance offsets mapped back to the raw record (`phase-mig-02`, R04); raw record untouched |
| The overlap detector is permitted by `ADR-010` but the triage agent already skims titles by reading | Changed a row | Ported as a deterministic pre-pass the driver runs and hands to the role (`phase-mig-01`), not as new judgement |
| "Reverses the single-writer rule": no such rule exists as stated | Changed a row | Restated as the per-log writers (`OPS-005`, `OPS-022`, `OPS-023`), the broker (`ADR-022`) and the backlog lock table; the write-back question is a decision phase (`phase-mig-05`) |
| Three of four design-input targets have deliverables that do not include the proposed work (`phase-ret-05` delivers an ADR revisit; `phase-agx-06` a methodology retrospective; `phase-irs-13` decision assembly) | Changed four rows | None of the design inputs is a phase here. Each is an idea with a finding naming the phase it informs (`000677` to `000684`, `000686`) |
| No upstream licence; `autoclaude-api` `pyproject.toml` line 7 says `Proprietary` | Cosmetic | Recorded under Decisions (D8). Both repositories are the owner's |
| The governance path skipped G2, the `GOV-018` audit, the mapper and G3 | Blocked promotion to a plan | This plan follows `GOV-021`: ideas captured and triaged, the partition proposed below, requirement then plan, `GOV-018` review at plan and phase altitudes, systems and `depends_on` assigned, G3 on the pull request |

Scope: the six phases in the table below. Four build, one decides, one is deferred. Sixteen ideas,
`000673` to `000688`, hold every proposal the surveys made, including the six this plan delivers,
so the owner can decline any of them at G1 without editing this plan.

**Partition proposed for G2.** One track, `phase-mig-*`, because every phase ports from or decides
about the same two external sources, and no phase belongs to an existing plan's deliverables (the
adversary's sixth finding is why: the existing phases that looked like targets do not declare the
work). The ideas that inform existing phases are not in this track; their findings name the
phases. The review record's plan-altitude findings include the adversary's attack on this
partition.

## Decisions

The planner's, open to the adversary and to the owner at G3. None is ruled.

- **D1. Port only what survived adversarial review: the overlap function, the sanitiser function,
  the timeline entity, and a decision on write-back.** Rejected: porting all twelve surveyed
  candidates as phases. Cost of that: two phases with no data to run on, one that contradicts an
  owner ruling, and four that would duplicate deliverables of phases already queued under other
  plans. Cost of the chosen option: eight candidates exist only as ideas until a phase of another
  plan picks them up, and nothing forces that. The findings on each idea name the phase, which is
  the only pointer the idea system offers today.
- **D2. The overlap pre-pass is a tool the triage driver runs, not logic inside the agent's
  prompt.** Rejected: describing Jaccard in the role's contract and letting the model compute it.
  Cost: a non-deterministic number, different per dispatch, that no test can check. Cost of the
  chosen option: one more tool under `tools/` with an OPS document and a drift-checked edit to two
  workflow sources.
- **D3. The sanitiser runs where the structuring agent reads the capture, and quote offsets are
  mapped back to the raw record.** Today no code hands a capture's content to an agent:
  `stage_capture` in `src/capture/structure.py` takes proposals the agent has already built, and
  `load_raw` is called only after that, so an agent reads the raw JSON file itself. The phase adds
  one read surface, `tools/capture.py show <id>`, and resolves quotes against the same sanitised
  view with an index map back to raw offsets, so `REQ-002` R6 provenance still indexes the record
  on disk. Rejected: sanitising at capture time in `src/capture/raw.py`. Cost: breaks `REQ-002` R1
  and R2 and `ADR-007`'s immutable capture. Rejected: sanitising `content` inside `structure()`
  before the quote check with no map. Cost: offsets index text that is not on disk, and a quote
  spanning a removed character raises "does not occur". Cost of the chosen option: the raw record
  keeps the hidden characters, the owner-facing review path (`src/capture/review.py`) still shows
  them, and a session that reads the raw file instead of `show` bypasses the sanitiser; `OPS-008`
  states the rule and nothing enforces it.
- **D3a. The sanitiser is adapted, not copied.** The source function NFC-normalises, collapses
  runs of spaces and tabs, and keeps carriage return (checked by running it: a tab became a
  space). Each of those changes a capture's text in a way `REQ-002`'s verbatim quote rule cannot
  absorb. Rejected: a verbatim copy. Cost: it fails R04's own test. Cost of the chosen option: the
  source's 17 tests no longer describe the function, so d-system writes its own.
- **D4. Timelines are a JSON domain entity under the data root, not markdown with front
  matter as in the source.** Rejected: markdown timelines in a tracked folder. Cost: a second entity
  format beside the JSON entities `tools/rebuild_db.py` and `src/db/source_validation.py` already
  load and validate, and no way to honour `ADR-009`'s data root without new code. Cost of the chosen
  option: the source's `routers/timelines.py` does not transfer; the entity follows `AGENTS.md`'s
  six-step recipe instead, split across two phases.
- **D5. Write-back is a decision phase that produces a draft ADR and builds nothing.** Rejected:
  porting `web/apps/api/writes/` as a phase. Cost: a writer beside the sanctioned per-log writers
  and the broker, with no owner ruling that one is wanted; `audit.py` also imports SQLAlchemy, so
  the code would be a rewrite anyway. Cost of the chosen option: one more owner decision before
  any workbench editing exists.
- **D6. The cost fold is a deferred phase, not a cancelled one.** Rejected: cancelling it. Cost:
  `phase-irs-12` still needs a cost report and the source's fold is the nearest tested design.
  Rejected: building it now. Cost: no ledger has events, two ledgers compete for the role
  (idea `000349`, `phase-irs-04` and `phase-auto-04`), and the schema would gain fields for a file
  nobody writes. The phase carries `resume_when` naming both conditions.
- **D7. A new track, `phase-mig-*`.** Rejected: attaching these phases to the plans that own the
  nearest systems (`PLAN-009` for capture, `PLAN-016` for ideas). Cost: a plan's phases must name
  that plan, and each of those plans is complete or owns a different problem; the pairing check
  in `src/governance/plan_phases.py` would also require this plan's phases to appear in this
  plan's text. Cost of the chosen option: one more track row in the backlog README.
- **D8. Provenance on every ported or adapted unit.** Each unit carries the source repository,
  path and commit in its header (`autoclaude-api` at `c7abe1389cd7593810dee345b5a3e2dd2b332540`,
  2026-06-22; `life` at `1754e3de0bc2ad6a2b4d536d2ccf8796de7c0f8b`, 2026-07-01). Both repositories
  are the owner's and `autoclaude-api` declares itself `Proprietary` (`pyproject.toml` line 7); no
  upstream licence applies. Rejected: a NOTICE file. Cost: one more file to keep in step, for two
  functions.
- **D10. The timeline routes mount behind the workbench gate.** `ADR-015` decision 1 mounts every
  workbench route only under `D_SYSTEM_DEMO_TERMINAL=1` and the loopback-only binding, and its
  rejected alternatives name ungated read routes. The DuckDB projection holds the owner's real
  portfolio when `D_SYSTEM_DATA_ROOT=_private/portfolio`, so a timeline route is portfolio data,
  not public talking points like the demo stage routes. Rejected: unconditional registration.
  Cost: a database-backed route over real milestones on the default binding, reversing a recorded
  decision. Cost of the chosen option: the route is absent unless the workbench is on.
- **D11. No phase declares `docs/03-sessions/` as a deliverable.** The containment check exempts a
  phase's own session record, and declaring the directory made every pair of phases collide at
  claim time. Rejected: keeping it, as `phase-plfx-*` did. Cost: no two phases of this plan could
  ever be active together, which the execution order below relies on.
- **D9. No `next_up` entry.** The owner places phases at the front of the queue. Rejected:
  proposing an order in `next_up`. Cost: `GOV-003` and `PROMPT-036` say agents never add entries,
  and the review gate requires a dispositioned record first. The order this plan proposes is under
  Execution order below.

## Implementation phases

| Phase | Delivers | Requirement rows | Depends on |
|---|---|---|---|
| `phase-mig-01` | `tools/idea_overlap.py` with its OPS document and tests, and the triage driver and role sources updated to run it and cite it, with the generated agent files regenerated | R01, R02, R03, R12 | — |
| `phase-mig-02` | `src/capture/sanitize.py` with its map back to raw offsets, the `show` read surface in `tools/capture.py`, quote resolution in `src/capture/structure.py` against the sanitised view, the `OPS-008` rule, and tests | R04, R05, R12 | — |
| `phase-mig-03` | `schemas/timeline.schema.json`, the `timelines` and `timeline_entries` tables, the loader, source validation of `ref`, and one fictional timeline in `_data/timelines/` | R06, R07, R08 | — |
| `phase-mig-04` | The Pydantic response model and the two read routes under `/api/v1/timelines`, mounted behind the workbench gate (D10), with the unbuilt-projection response and tests | R09 | `phase-mig-03` |
| `phase-mig-05` | A draft ADR on workbench write-back to tracked files, with the three alternatives and a revisit trigger; builds nothing | R10 | — |
| `phase-mig-06` | Deferred: the run schema's `model` and cache fields and `tools/run_cost_report.py` | R11 | `phase-irs-04` |

R13 is met on this branch before any phase runs: the sixteen ideas are recorded and triaged, and
the session record `SESS-2026-10-10-01` lists them. Each phase's scope, acceptance, verification and deliverables are in
`docs/09-backlog/backlog.yaml`. Five are `queued` and `phase-mig-06` is `deferred`; none is in
`next_up`.

Threat surfaces per phase (`GOV-010` P12): `phase-mig-02` reads untrusted text (the capture) and
exists to reduce what reaches an agent; it adds no network, secret or dependency. `phase-mig-04`
adds two read-only HTTP routes over the projection, which holds the owner's real portfolio under
the data root, so they mount only under `ADR-015`'s gate and loopback binding (D10); no new
port, process, credential or write. `phase-mig-01`, `phase-mig-03`, `phase-mig-05` and
`phase-mig-06` touch none: no network, no secrets, no new dependency.

## Requirement coverage

| Requirement | Phase |
|---|---|
| R01, R02, R03 | `phase-mig-01` |
| R04, R05 | `phase-mig-02` |
| R06, R07, R08 | `phase-mig-03` |
| R09 | `phase-mig-04` |
| R10 | `phase-mig-05` |
| R11 | `phase-mig-06` (deferred) |
| R12 | `phase-mig-01` and `phase-mig-02`, the two phases that copy code |
| R13 | Met on this branch before any phase runs; `SESS-2026-10-10-01` is the evidence |

Every row maps to a phase or to recorded evidence, and every phase to at least one row.

## Execution order and real concurrency

Proposed order: `phase-mig-01` first, then `phase-mig-03`, then `phase-mig-04`. `phase-mig-02`
and `phase-mig-05` may each run beside any of those three. `phase-mig-06` waits on its resume
condition.

Measured with `src.governance.backlog.collisions` over `backlog.yaml` on 2026-10-10, after D11
removed `docs/03-sessions/` from every phase. The claim-time validator is the authority; this
section records what it said then.

Within the plan:

- `phase-mig-01` and `phase-mig-03` share `sys-portfolio` and `docs/08-governance/systems.yaml`,
  so they serialise. `phase-mig-01` and `phase-mig-05` share `sys-gov-docs` (the OPS document and
  the ADR both live under governance), so they serialise. `phase-mig-01` and `phase-mig-02` share
  `docs/08-governance/OPS-008-capture.md` through `phase-mig-01`'s directory deliverable, so they
  serialise.
- `phase-mig-02` collides with none of `phase-mig-03`, `phase-mig-04` and `phase-mig-05`.
  `phase-mig-04` collides with none of `phase-mig-01`, `phase-mig-02` and `phase-mig-05`.
  `phase-mig-03` and `phase-mig-05` are disjoint.
- `phase-mig-06` collides with `phase-mig-01`, `phase-mig-02`, `phase-mig-03` and `phase-mig-05`
  through `docs/08-governance/`, `OPS-008`, `systems.yaml`, `test/test_schemas.py` and
  `sys-gov-docs`; it is deferred, so this binds nothing today.

Against the rest of the backlog (queued and active phases only):

- The one active phase, `phase-arch-07`, locks the workbench systems and `sys-ui` and collides
  with none of the six.
- `phase-cap-08`, first in `next_up`, declares `sys-portfolio`, so it blocks `phase-mig-01` and
  `phase-mig-03` while active, and nothing else here.
- `phase-mig-01` collides with 22 queued phases on `sys-portfolio`, 17 on the generated
  `.claude/agents/idea-triage.md` (among them `phase-ses-02`, `phase-idg-02`, `phase-idg-06`,
  `phase-port-03`), and 27 on `docs/08-governance/`, because those phases declare the directory
  or the generated file. `phase-port-03` shares every workflow source and generated target.
- `phase-mig-02` collides with the 11 phases that declare `tools/` (`phase-tool-02` among them)
  and the 12 that declare `src/`.
- `phase-mig-03` collides with the `sys-contracts`, `sys-projection` and `sys-portfolio` phases
  (`phase-rel-04`, `phase-mem-08`, `phase-sig-01` among them), with `phase-mem-09` and
  `phase-auto-04` on `sql/001_schema.sql`, and with `phase-expl-04` and `phase-idg-04` on
  `_data/`.
- `phase-mig-04` collides with the 10 `sys-api` phases, which are the `phase-arch-*` and
  `phase-rel-07` work.
- `phase-mig-05` collides with the 10 phases that declare `docs/04-decisions/` and the 4 that
  declare `sys-gov-docs` (`phase-idg-08`, `phase-mode-01` to `-03`).

Most of these collisions come from other phases declaring a whole directory (`tools/`, `test/`,
`src/`, `docs/08-governance/`), not from shared files; the validator counts them anyway, so the
owner sequences on the report, not on this list.

## Acceptance and verification

Common to every phase, beside the phase's own acceptance in the backlog:

- The phase's new tests are written against d-system's fixtures and pass; the source tests are
  read for coverage, not copied (`REQ-038`, "What each requirement is not").
- Each copied function's header names the source repository, path and the commit in D8.
- After rebasing onto `dev`: `uv run python -m src.governance`, `uv run pytest`,
  `uv run ruff check src/ test/ tools/` and `uv run mypy src/` are clean.
- `uv run python tools/check_no_private_content.py`, with changes staged, reports OK.
- A new tool ships with its `OPS-NNN` document and the generated reference block
  (`tools/generate_tool_docs.py`).
- An independent review from a validator or adversary agent type finds no unresolved blocker or
  major before READY.

## Linked ideas

All sixteen were recorded and triaged on this branch by the Ideation role. No status beyond
`triaged` is moved by this plan.

| Idea | Relation to this plan |
|---|---|
| `000673` (idea overlap pre-pass) | Delivered by `phase-mig-01` |
| `000674` (sanitiser at structuring time) | Delivered by `phase-mig-02` |
| `000675` (timelines as a domain entity) | Delivered by `phase-mig-03` and `phase-mig-04` |
| `000676` (decision on workbench write-back) | Decided by `phase-mig-05` |
| `000677` (run-ledger cost fold) | `phase-mig-06`, deferred on `000349` |
| `000678` (budget-cap acceptance pattern) | Not a phase here; design input for `phase-irs-11` |
| `000679` (proposal state machine) | Not a phase here; design input for `phase-irs-13` |
| `000680` (golden-set evaluation harness) | Not a phase here; relates to `REQ-030`'s shadow judge |
| `000681` (hash-diff incremental rebuild) | Not a phase here; input to `phase-ret-05`'s `ADR-001` revisit |
| `000682` (memory promotion ladder) | Not a phase here; input to `phase-mem-03` to `phase-mem-06` |
| `000683` (bootstrap prompt with a proceed gate) | Not a phase here; input to the plugin's install workflow |
| `000684` (read-when column for GOV-007) | Not a phase here; a documentation change the owner can direct |
| `000685` (engagement templates) | Not a phase here; placement is open question 3 |
| `000686` (static-export profiles) | Not a phase here; input to `phase-syn-05` |
| `000687` (front-matter validation in a pre-commit hook) | Not a phase here; the hook exists, `core.hooksPath` is not set in a fresh clone |
| `000688` (voice capture pipeline sketch) | Not a phase here; relates to `000561` |

## Out of scope

- Scout extractors, per-source cursors and the per-clone Docker sandbox: domain-specific, and
  d-system has no external discovery source.
- Brands, bundles, the PPTX and DOCX export pipeline and the rename guardrail: unbuilt in the
  source (only `Client` and `BusinessProcess` tables, stub templates and one brand folder exist).
- The Next.js operator UI, the SQLAlchemy and Alembic index: d-system's stack is React, Vite and
  DuckDB.
- `life`'s Postgres, Celery and speech-to-text note application, its git workflow and its
  decision-log format: d-system has its own session, worktree and ADR conventions.
- Any workbench view of timelines. The entity and its read route ship; a panel is later work.
- Any change to `AGENTS.md` or `CLAUDE.md`.
- Moving any idea past `triaged`. The owner rules at G1.

## Open questions

1. **Does the owner want the timeline entity?** Owner, at G3 on the pull request. It is the only
   proposal that serves the consulting half, and the surveys found no dated view over
   commitments; the author leans yes. If no, `phase-mig-03` and `phase-mig-04` are cancelled with a
   reason and R06 to R09 are marked withdrawn in `REQ-038`.
2. **Is 0.6 the right overlap threshold for idea titles?** Owner, after `phase-mig-01` prints
   scores over the real log in its session record. The author leans to keeping the source's
   constant and printing the score, so the number is judged on evidence rather than guessed.
3. **Where do engagement templates live (`000685`)?** Owner, at idea review. The author leans to
   structure under the data root per `ADR-009` with no tracked prose, because a scoping document
   names a client.
4. **Idea ids were allocated on a feature branch.** If `dev` gains an idea before this branch
   merges, the fold fails at merge on a duplicate id. Owner, at G4. The author leans to merging
   this branch before the next idea is recorded on `dev`, or renumbering here if `dev` moved.
