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
| The sanitiser at capture time violates `REQ-002` R1 and R2 (`src/capture/raw.py` stores verbatim) | Changed a row | Applied at structuring time (`phase-mig-02`), raw record untouched (R04) |
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
- **D3. The sanitiser runs at structuring time.** Rejected: at capture time, in
  `src/capture/raw.py` or `tools/capture.py`. Cost: breaks `REQ-002` R1 and R2 (byte-identical raw
  record) and `ADR-007`'s immutable capture. Cost of the chosen option: the hidden characters stay
  on disk in the raw record, and anything that reads raw records other than through the
  structuring path still sees them. Today only `src/capture/structure.py` reads them for an agent.
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
- **D8. Provenance on every ported unit.** Each copied function carries the source repository,
  path and commit in its header (`autoclaude-api` at `c7abe1389cd7593810dee345b5a3e2dd2b332540`,
  2026-06-22; `life` at `1754e3de0bc2ad6a2b4d536d2ccf8796de7c0f8b`, 2026-07-01). Both repositories
  are the owner's and `autoclaude-api` declares itself `Proprietary` (`pyproject.toml` line 7); no
  upstream licence applies. Rejected: a NOTICE file. Cost: one more file to keep in step, for two
  functions.
- **D9. No `next_up` entry.** The owner places phases at the front of the queue. Rejected:
  proposing an order in `next_up`. Cost: `GOV-003` and `PROMPT-036` say agents never add entries,
  and the review gate requires a dispositioned record first. The order this plan proposes is under
  Execution order below.

## Implementation phases

| Phase | Delivers | Requirement rows | Depends on |
|---|---|---|---|
| `phase-mig-01` | `tools/idea_overlap.py` with its OPS document and tests, and the triage driver and role sources updated to run it and cite it, with the generated agent files regenerated | R01, R02, R03, R12 | — |
| `phase-mig-02` | The sanitiser function in `src/capture/`, applied in the structuring read path, with its provenance header and tests | R04, R05, R12 | — |
| `phase-mig-03` | `schemas/timeline.schema.json`, the `timelines` and `timeline_entries` tables, the loader, source validation of `ref`, and one fictional timeline in `_data/timelines/` | R06, R07, R08 | — |
| `phase-mig-04` | The Pydantic response model and the two read routes under `/api/v1/timelines`, registered unconditionally, with tests | R09 | `phase-mig-03` |
| `phase-mig-05` | A draft ADR on workbench write-back to tracked files, with the three alternatives and a revisit trigger; builds nothing | R10 | — |
| `phase-mig-06` | Deferred: the run schema's `model` and cache fields and `tools/run_cost_report.py` | R11 | `phase-irs-04` |

R13 is already met on this branch: the sixteen ideas are recorded and triaged, and the session
record lists them. Each phase's scope, acceptance, verification and deliverables are in
`docs/09-backlog/backlog.yaml`. Five are `queued` and `phase-mig-06` is `deferred`; none is in
`next_up`.

Threat surfaces per phase (`GOV-010` P12): `phase-mig-02` reads untrusted text (the capture) and
exists to reduce what reaches an agent; it adds no network, secret or dependency. `phase-mig-04`
adds two read-only HTTP routes on the existing application binding, with no new port, process,
credential or write. `phase-mig-01`, `phase-mig-03`, `phase-mig-05` and `phase-mig-06` touch
none: no network, no secrets, no new dependency.

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
| R13 | Met on this branch before any phase runs; the session record is the evidence |

Every row maps to a phase or to recorded evidence, and every phase to at least one row.

## Execution order and real concurrency

Proposed order: `phase-mig-01` and `phase-mig-02` first, which may run at the same time;
`phase-mig-03`, then `phase-mig-04`; `phase-mig-05` at any point. `phase-mig-06` waits on its
resume condition.

Measured from declared `systems` and `deliverables`:

- `phase-mig-01` locks `sys-portfolio` (`tools/idea_overlap.py`, the idea log it reads) and the
  two workflow sources under `agent-workflows/`. `phase-mig-02` locks `sys-capture`
  (`src/capture/`). Disjoint, so both may be active together.
- `phase-mig-03` declares `sys-contracts`, `sys-projection` and `sys-portfolio` (it adds
  `_data/timelines/`), so it collides with `phase-mig-01` on `sys-portfolio` and waits for it.
  `phase-mig-04` depends on `phase-mig-03` and locks `sys-api` only.
- `phase-mig-05` locks `sys-gov-docs` and writes only under `docs/04-decisions/` and
  `docs/03-sessions/`. It collides with nothing in this plan.
- Against the rest of the backlog on 2026-10-10: the one active phase, `phase-arch-07`, locks the
  workbench systems and `sys-ui`; none of these phases declares those. `phase-cap-08`, first in
  `next_up`, declares `sys-capture`, so `phase-mig-02` cannot be active at the same time as it.
  `phase-idg-06` (move `/idea` capture into a subagent) and `phase-irs-01` family phases touch
  the idea log; `phase-mig-01` declares `sys-portfolio`, so the validator refuses a concurrent
  claim.

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
