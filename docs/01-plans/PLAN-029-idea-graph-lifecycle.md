---
schema_version: 1
id: doc-idea-graph-lifecycle
code: PLAN-029
title: Idea graph and lifecycle (P1)
kind: plan
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-25'
systems: [sys-portfolio, sys-projection, sys-governance]
depends_on: [doc-idea-graph-lifecycle-requirements, doc-idea-node-classification]
---

# Idea graph and lifecycle (P1)

## Summary

Programme `P1` of the twelve, fourth in the owner's delivery order. Nineteen ideas across four fine
groups, from the accepted partition of 2026-09-13. Every member changes, agentifies, or reports on the
append-only idea log and the schema it folds through.

Two of the nineteen are already ruled out of implementation: `000063`'s forking half was resolved into
`component_of` plus `000064`'s lineage annotation, and `000070` was delivered by the live-demo pack.
Both are `discarded` on the log. Seventeen remain.

| Group | Ideas | What it covers |
|---|---|---|
| `G01` `ARCH-005` schema bundle | `000018`, `000053`, `000061`, `000062`, `000064`, `000065` | Tagging, doc-code link targets, the three-axis classification, its agent, the lineage annotation and the decomposition procedure |
| `G02` Idea-system agents | `000048`, `000055`, `000127` | `000048` and `000127` are the same ask six days apart; `000055` maintains the link graph those writes create |
| `G03` Idea and backlog reporting | `000008`, `000010`, `000042`, `000050`, `000071` | Largely delivered — see the verification below |
| `G04` Idea-to-plan drafting | `000046`, `000047`, `000049` | `000046` names `000047` its own prerequisite; `000049` surfaced from triaging `000046` and blocks its design |

Partition-time sizing was 10–13 phases if built in full. This plan landed **twelve**; later splits
took it to nineteen (see the phase table).

## What `G03` already ships, verified in code

The phase's acceptance requires this before any phase is sized, so it was done first and is recorded
here rather than left in the session record.

- **`tools/overview_metrics.py` implements `000071`'s delivered metric set.** It emits funnel counts and rates
  by status, cycle time between statuses, annotation coverage, link-type distribution and orphan
  count, throughput by day, age of open ideas, and backlog phase counts. It reads through
  `load_events()` and `fold()` rather than parsing `_data/ideas.jsonl` by hand, and is deterministic
  by construction — no wall clock, sorted keys, byte-identical across runs. Executed during this
  phase and produced real output. **`000008` is delivered by this tool.**
  One metric from `000071`'s candidate list is deliberately absent: *amendment rate as a proxy for
  rework*. `phase-demo-03` scoped it out and annotated the idea saying so. The tool implements what
  was accepted, not the full candidate list, and `phase-idg-08` should not silently reinstate it.
- **Both explorers ship in the workbench.** `ts/src/stage/IdeaExplorerRegion.tsx` and
  `BacklogExplorerRegion.tsx` render the two queues against `/api/v1/workbench/ideas`,
  `/ideas/queue`, `/backlog` and `/backlog/queue`, each with a standard/priority-queue toggle.
  **`000010`'s idea browser is delivered**, and `000042`'s combined at-a-glance view is delivered as
  panels rather than as a generated page.
- **The `orient` skill answers `000071`'s second half** — the command that shows what commands can do.

What is genuinely left in `G03` is two things: no command wraps the metrics tool, and nothing captures
an idea without a session open. Those are `phase-idg-08` and `phase-idg-09`. `000050` is an umbrella
and gets no phase; `000042` gets a ruling rather than a build, under `R14`.

This is the partition's own warning confirmed: the group reads as six ideas and is worth two phases.

## The chosen design

### 1. Classification lands as fields on the idea schema, not as a separate graph layer

`ARCH-005`'s recommended build order names this the scope fork that everything else is scoped
against, and leaves it open. **Ruled: three fields on `schemas/idea.schema.json`.**

The alternative — a typed-node graph layer that ideas, memories and documents all become nodes
within — is the more general design and is genuinely better if it exists. It does not exist. It
requires `000060` and `000032`, both of which sit in `P6`, neither of which has started. Choosing it
now blocks all six `G01` ideas behind an unbuilt substrate, and `G01` is the group everything else in
this programme depends on.

The corpus is also small enough that the general design buys nothing yet. At roughly 240 ideas the
traversal queries `ARCH-005` wants — every *Strategic Directive* resting on an *Assumption* — are
relational joins the existing DuckDB derived layer expresses adequately. `ARCH-005` raises exactly
this as its query-surface question and names NetworkX as the alternative; at this size the answer is
that no graph library is needed.

**The cost accepted, stated plainly:** if `P6` later builds the graph layer, these fields become a
migration rather than a design already fitted to it. That is a real cost and it is the right one to
take, because the migration is bounded and the blockage is not.

### 2. Every knowledge record carries a value on every axis, with a reason for each

**Amended 2026-09-25, superseding the 2026-09-14 ruling.** This decision first ruled each axis
optional, with the classification agent required to say why it left an axis blank. The owner's
2026-09-24 ruling on the revised `ARCH-005` replaced that:

- The epistemic axis is never blank. Not Applicable / Agnostic replaces a blank on a record that
  asserts no verifiable truth claim.
- The ontological, lifecycle and temporal axes are required on every knowledge record.
- Records that are not knowledge records (`collection`, `fixture`, `reference`) carry a record kind
  instead of axis values.
- A reason is kept for each axis value.

The failure the first ruling guarded against still holds, and the amendment meets it without
blanks. An absent axis is indistinguishable from an idea the agent never processed, which makes
coverage unmeasurable and makes `R03`'s number meaningless. With no blanks allowed, an absent value
on a knowledge record now always means an unprocessed record.

### 3. The schema additions ship as one phase, because they touch the same three files

`ARCH-005` item 3 bundles the classification fields, the `component_of` link type, the `lineage`
annotation kind and `000053`'s document-code link targets. **Kept bundled.** All four touch
`schemas/idea.schema.json`, `src/db/ideas.py`'s `fold()` and `tools/append_idea.py` together, and
splitting them means re-touching the same three files four times, with four rounds of the same test
surface.

`ARCH-005` notes `000053` is genuinely independent — a different axis, the link *target* shape rather
than node classification — and could split if sequencing demanded. Nothing here demands it.

### 4. Backfill is an append, never an edit

The taxonomy's value is entirely coverage-dependent, so the backfill is not optional. But `R07` makes
the method a requirement rather than a matter of care: classification is backfilled by appending
classification events, never by rewriting the lines already in `_data/ideas.jsonl`.

This is worth stating because a backfill is exactly the operation that tempts an in-place edit — the
data is already there and the events feel like ceremony. An edited log is no longer an append-only
log, and every derived guarantee `fold()` provides goes with it.

### 5. `000048` and `000127` are one phase, because they are one ask

The partition already observes they are the same request six days apart. **Built once**, as
`phase-idg-06`. `000127` adds the general principle worth extracting — any skill whose work is
mechanical and self-contained should run in a subagent by default — which is recorded in the phase's
scope as a finding for the commands-and-skills audit rather than built here.

### 6. `G04` is sequenced by its own stated dependencies, not by idea number

`000046` names `000047` its own prerequisite, and `000049` surfaced from triaging `000046` and blocks
its design. So the planner agent is last: the standard for a good plan and the location a draft lives
in both have to exist before an agent can draft into them.

`R20` is what stops this being three unrelated phases. It requires a plan the agent drafts to be
checked against the standard — otherwise `000047` produces prose nothing is measured against, which
is the failure mode `000047` itself describes about the existing corpus.

The partition records `G04` as contested 2–2 and ruled on the one-directional dependency rather than
by counting. That ruling stands, and this sequencing is what it implies.

### Which of these need a decision record

**One of the six needs an ADR; the rest do not.**

- **Decision 1 (the scope fork) needs one**, and `phase-idg-01` writes it. It is a choice between two
  architectures with a stated migration cost, made against an alternative that may later be built —
  exactly the shape a decision record exists to preserve. Without it, a future reader finding fields
  on the idea schema cannot tell whether the graph layer was rejected or never considered.
- **Decisions 2, 3, 4, 5 and 6 need none.** Each is recorded where the reader meets it: decision 2 in
  the schema and the agent's own contract, 3 and 4 in `REQ-014`'s rows, 5 in `phase-idg-06`'s scope,
  6 in this plan's phase table. `ARCH-005` already carries the vocabulary these reason from.

`ARCH-005` was accepted on 2026-09-25, before `phase-idg-01`, with the owner's revisions to the
vocabulary. It was written as a vocabulary awaiting a governing requirement; `REQ-014` is that
requirement and existed by then, so accepting it did not invert the repository's plan-before-code
rule. `phase-idg-01` builds the schema, writer and code against the accepted vocabulary.

## Implementation phases

Nineteen phases under `phase-idg-*`, registered in [the backlog index](../09-backlog/README.md).
`phase-idg-13` and `phase-idg-14` were split out of `phase-idg-01` after this plan was written, on
2026-09-22 and 2026-09-23 (`GOV-003`), and belong to no partition group. On 2026-09-24 the backfill
in `phase-idg-13` was split again into five batches by the date each idea was created, `phase-idg-13`
and `phase-idg-15` through `phase-idg-18`, so each holds about 100 ideas inside `session_budget: 1`
(review finding F11, [the review record](../08-governance/reviews/2026-09-24-plan-029-idg-split.json)).
`phase-idg-19` was split out of `phase-idg-01` the same day, after idea `000417` was folded into it
and took it past one session.

| Phase | Title | Group | Depends on |
|---|---|---|---|
| `phase-idg-01` | Ship the idea schema bundle and record the scope-fork decision | `G01` | — |
| `phase-idg-02` | Build the pure classification agent | `G01` | `01` |
| `phase-idg-03` | Backfill classification across the corpus and report coverage | `G01` | `02` |
| `phase-idg-04` | Build the tagging registry and retroactive tag assignment | `G01` | `01` |
| `phase-idg-05` | Write the decomposition procedure for compound ideas | `G01` | `01`, `02` |
| `phase-idg-06` | Move `/idea` capture into a subagent | `G02` | — |
| `phase-idg-07` | Build the connection-builder agent across all idea statuses | `G02` | `01`, `04` |
| `phase-idg-08` | Wrap idea metrics as a command and rule on the generated page | `G03` | — |
| `phase-idg-09` | Capture an idea with no session open | `G03` | `06` |
| `phase-idg-10` | Audit the plan corpus and write the plan-quality standard | `G04` | — |
| `phase-idg-11` | Define where a promoted plan lives before it earns a code | `G04` | — |
| `phase-idg-12` | Build the idea planner agent and check it against the standard | `G04` | `10`, `11` |
| `phase-idg-13` | Backfill the idea log into the new terminal states - ideas created 2026-09-06 to 2026-09-10 | — | `01`, `14` |
| `phase-idg-14` | Build the terminal-state authority process - propose, verify, ratify | — | `01` |
| `phase-idg-15` | Backfill the idea log into the new terminal states - ideas created 2026-09-11 to 2026-09-12 | — | `01`, `14` |
| `phase-idg-16` | Backfill the idea log into the new terminal states - ideas created 2026-09-13 to 2026-09-21 | — | `01`, `14` |
| `phase-idg-17` | Backfill the idea log into the new terminal states - ideas created 2026-09-22 to 2026-09-23 | — | `01`, `14` |
| `phase-idg-18` | Backfill the idea log into the new terminal states - ideas created 2026-09-24 onward | — | `01`, `14` |
| `phase-idg-19` | Add the set-aside status and the partition hold-out field | — | `01` |

### Sizing against the partition

Partition-time sizing was **10–13 phases** against 19 ideas. This plan lands **twelve**, inside the
range, and the internal distribution is where the interest is.

- `G01` was called the group needing a governing requirement and lands at **five**, matching the
  `ARCH-005` build order's items 3 through 9 with the tagging item pulled alongside.
- `G03` was called "most shovel-ready" at partition time and lands at **two**, because it turned out
  to be most shovel-*ed* — the verification above found the metrics, both explorers and the `orient`
  skill already shipped. This is the largest delta from partition-time expectation in the programme.
- `G02` lands at two rather than three, because `000048` and `000127` are one ask.
- `G04` lands at three, one per idea, which its own dependency chain forces.

The later splits take the plan to **nineteen**, above the partition-time range. None adds a
partition idea: `phase-idg-13` to `phase-idg-18` carry the owner's 2026-09-22 lifecycle ruling on idea `000236`, which arrived
after the partition and was first folded into `phase-idg-01`, then split out because it doubled that
phase's scope while its `session_budget` stayed at one. Five of the six are the backfill, divided
by date because one session cannot read the findings of roughly 420 ideas. `phase-idg-19` carries
idea `000417`, folded in by owner ruling on 2026-09-24 and split out for the same sizing reason.

## Execution order and real concurrency

`phase-idg-01` is a genuine bottleneck: twelve phases depend on it directly or transitively, and
every other phase touching `schemas/idea.schema.json` (`phase-idg-04`, `phase-idg-14`, `phase-idg-19`) depends on it.
Nothing in `G01` can start beside it.

Five phases declare `depends_on: []`, but not all five clear each other. `phase-idg-08`,
`phase-idg-10` and `phase-idg-11` all declare `sys-gov-docs` and collide with each other on that
shared system; `phase-idg-08`'s bare `.claude/commands/` deliverable also collides with
`phase-idg-06`'s `.claude/commands/idea.md`; and `phase-idg-01`'s bare `docs/04-decisions/`
deliverable collides with `phase-idg-11`'s `docs/04-decisions/ADR-019-promoted-plan-staging.md`.

**Corrected 2026-09-24: `phase-idg-01` and `phase-idg-06` collide.** This section first named
`phase-idg-01`, `phase-idg-06` and `phase-idg-10` as a mutually disjoint trio. That was true only
because `phase-idg-01` under-declared its systems: its `src/governance/` deliverable, added on
2026-09-23, belongs to `sys-governance`, which `phase-idg-06` also declares. With `sys-governance`
now declared on `phase-idg-01`, no three of the five clear each other. The disjoint pairs are
`phase-idg-01` with `phase-idg-08` or `phase-idg-10`, and `phase-idg-06` with `phase-idg-10` or
`phase-idg-11`. `phase-idg-10` is complete, so of the four still queued the widest parallel front is
two: `phase-idg-01` with `phase-idg-08`, or `phase-idg-06` with `phase-idg-11`.

After `phase-idg-01` lands, `G01` serialises hard: `-02` before `-03`, `-02` before `-05`, and `-04`
before `-07`, and `-14` before each backfill batch (`-13`, `-15` to `-18`). The five batches share
`_data/ideas.jsonl`, so they run one at a time, in any order. The critical path is four deep: `01` →
`02` → `03`, with `01` → `04` → `07` the same length.

## Requirement coverage

Every row of `REQ-014` maps to at least one phase, and every phase carries at least one row.

| Requirement | Phases |
|---|---|
| R01 Three classification axes as schema fields | `phase-idg-01` |
| R02 Axes independently optional, blanks carry a reason | `phase-idg-01`, `phase-idg-02` |
| R03 Coverage measurable per axis | `phase-idg-03` |
| R04 Links may target a document code | `phase-idg-01` |
| R05 `component_of` and `lineage` exist, writer-restricted | `phase-idg-01` |
| R06 The schema additions land in one change | `phase-idg-01` |
| R07 Pre-change ideas readable, log never rewritten | `phase-idg-01`, `phase-idg-03` |
| R08 Classification agent reads one idea in isolation | `phase-idg-02` |
| R09 Corpus backfilled, unclassified proportion reported | `phase-idg-03` |
| R10 Tag registry with controlled vocabulary | `phase-idg-04` |
| R11 Connection-builder works across all statuses | `phase-idg-07` |
| R12 Decomposition leaves the original intact | `phase-idg-05` |
| R13 Idea metrics reachable as a command | `phase-idg-08` |
| R14 The generated-page question is ruled on | `phase-idg-08` |
| R15 `/idea` capture runs in a subagent | `phase-idg-06` |
| R16 An idea can be captured with no session open | `phase-idg-09` |
| R17 A plan-quality standard derived from the corpus | `phase-idg-10` |
| R18 Where a promoted draft lives before it earns a code | `phase-idg-11` |
| R19 A planner agent that drafts and does not decide | `phase-idg-12` |
| R20 A drafted plan is conformant to the standard | `phase-idg-12` |
| R21 Shipped ideas backfilled into terminal states, `000099`/`000129` reversed | `phase-idg-13`, `phase-idg-15`, `phase-idg-16`, `phase-idg-17`, `phase-idg-18` |
| R22 Agent-written closes marked, verified and ratified | `phase-idg-14` |
| R23 An idea can be set aside at a partition without being discarded | `phase-idg-19` |

## Key references

- **The requirement** — [REQ-014](../06-requirements/REQ-014-idea-graph-lifecycle.md).
- **Idea node classification** ([ARCH-005](../07-architecture/ARCH-005-idea-node-classification.md)) — the owner's own document, which bundles `G01` and names the scope fork decision 1 resolves.
- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P1`, including the disagreement table behind `G04`'s 2–2 ruling.
- **Idea record system** ([PLAN-016](PLAN-016-idea-record-system.md)) and the **idea/plan lifecycle** ([PLAN-017](PLAN-017-idea-plan-lifecycle)) — the existing substrate.
- **Idea staging** ([ADR-010](../04-decisions/ADR-010-idea-staging.md)) — the record-as-given rule, and the document that stops at promotion where `R18` picks up.
- **Document and backlog governance** ([PLAN-030](PLAN-030-document-backlog-governance.md)) — `G05`'s requirement-vs-plan rule informs `G04`.

## Known facts not to rediscover

- **`G01` is not internally separable by design.** `ARCH-005` names those ideas as one unit; splitting
  them re-opens a decision the owner already made. The five phases here split by *deliverable*
  (schema, agent, backfill, tagging, procedure), not by idea, which is why the bundle holds.
- **`G03` is largely delivered**, and this plan records exactly what, verified by running the tool and
  reading the components. Do not re-verify from scratch; do check whether anything has moved.
- **`G04` was contested 2–2** and was ruled on the one-directional dependency, not by counting. Read
  the partition's disagreement table before revisiting it.
- **`000072`'s planner bullet duplicates `000046`.** `000072` lives in `P4` (`G16`); only the control
  analyst caught the duplication. The partition recommends striking the bullet rather than building
  the same thing twice. `phase-prog-06` finalizes `P4` and owns that ruling — `phase-idg-12` should
  not be sized as if `000072` might also deliver it.
- **`G02`'s `000055` depends on `G01`**; the rest of `G02` does not, which is why `phase-idg-06` has
  no prerequisites and `phase-idg-07` has two.
- **`lineage` is the owner's voice.** `tools/append_idea.py` already restricts agent authors to
  `kind: finding`; `000064` places `lineage` alongside `note` and `assessment` deliberately. An agent
  writing a lineage annotation is a defect, not a convenience.
- **`000004` is a live candidate compound idea** to test `phase-idg-05`'s procedure against —
  `ARCH-005` names it as already reading like one.
