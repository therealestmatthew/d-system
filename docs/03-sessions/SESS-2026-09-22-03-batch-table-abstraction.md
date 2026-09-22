---
schema_version: 1
id: doc-session-2026-09-22-batch-tables
code: SESS-2026-09-22-03
title: Abstract the batch table out of the build coordinator and register the orchestration protocol
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-backlog, sys-governance]
depends_on: [doc-build-coordinator, doc-batch-orchestration-protocol, doc-coordinator-protocol]
---

# Abstract the batch table out of the build coordinator and register the orchestration protocol

## Phase

Unclaimed — owner-directed work, no backlog phase. `batch-tables` — abstract the build
coordinator's hard-coded batch table into a schema-backed structure capturing order, dependencies
and parallelism, move the original table into it, compose the next batch as a new table, make
`PROMPT-036` discover and select a table rather than be told one, and register the resulting
batching and orchestration mechanism as a protocol.

## Verification

Self-declared gates; no backlog verification list exists for this session.

```
$ uv run python -m src.governance
Governance OK: 35 systems, 310 documents, 29 memories, 293 backlog phases
```

```
$ uv run pytest
688 passed, 2 warnings
```

```
$ uv run python tools/check_no_private_content.py   # with changes staged
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (778 tracked files, 0 identifiers checked)
```

Beyond the three gates, the six batch compositions were checked by script against
`docs/09-backlog/backlog.yaml`: every phase id resolves; every phase in an unbuilt batch is
`queued` and unclaimed; every `depends_on` edge resolves to an earlier position in the global batch
order or to an external phase confirmed `complete`; every stage boundary follows from a shared
`system` or a prefix-overlapping `deliverable`. Each emitted table was validated against
`schemas/batch.schema.json` with `jsonschema` at write time.

## Acceptance

Self-declared from the owner's instruction; no backlog acceptance list exists for this session.

- **An existing reusable prompt was found rather than a new one written** — Met. `PROMPT-036` was
  located and reported before any file was changed; no competing prompt was created.
- **The batch table is abstracted out of the prompt behind a schema capturing order, dependencies
  and parallelism** — Met. `schemas/batch.schema.json` defines `stages` (order), `after` and
  `external_depends_on` (dependencies) and `parallel` with `conflicts_with` (parallelism);
  `PROMPT-036` contains no phase list.
- **The original batch table is moved into that form** — Met. `batch-001` through `batch-006` carry
  `PROMPT-036`'s original six batches, membership unchanged, with `batch-002` replaced per the next
  condition.
- **The next batch is composed as a new table** — Met. `batch-002` holds the owner's chosen seven
  phases; its composition is verified and recorded in `provenance` and `verified`.
- **The coordinator auto-references the latest unstarted or incomplete table, and asks only when
  several are genuinely ambiguous** — Met. `PROMPT-036` § *Selecting one* states the four-case rule;
  `sequence` exists so that several `queued` tables resolve without a question.
- **The mechanism is registered as a protocol** — Met. `GOV-016` governs composition, verification,
  stages, selection, status and supersession, with pointers from `GOV-013` and `PROMPT-036`.
- **No batch was run** — Met, and intended: the session's scope became the mechanism. `batch-002`
  is `queued` and selectable.

## Backlog

Unclaimed — no backlog phase was claimed for this session; no line of `backlog.yaml` was changed.

## Unresolved

Nothing validates the batch tables mechanically. The selection rule's first case assumes at most one
table is `in_progress`, and nothing prevents two. Idea `000316` holds that check; it is implementation
code and so needs a requirement document, a plan document and backlog phases before it is written.

Every guarantee about a composition therefore rests on the composing session running the check by
hand and recording it in `provenance` — which this session did, and which `GOV-016` requires, but
which no gate enforces.

## Review

Independent sub-agent review (fresh context, not a fork), run at close against `3cc4ea6..HEAD`. Its
findings, condition by condition:

> **Reruns.** `uv run python -m src.governance` → `Governance OK: 35 systems, 310 documents, 29
> memories, 293 backlog phases`. `uv run pytest` → `688 passed, 2 warnings in 58.95s`. Both match
> the record exactly. `check_no_private_content.py` also runs clean in the primary checkout (31
> identifiers checked, differs from the worktree's "0 identifiers" note only because the worktree
> environment lacks `_private/portfolio/` — expected, not a discrepancy).
>
> **Independent re-derivation of every batch table**, via my own script over
> `docs/09-backlog/backlog.yaml` and `docs/09-backlog/batches/*.yaml` (six tables): every phase id
> resolves; every phase in an unbuilt (`queued`/not `complete`) table has backlog `status: queued`
> and no `agent`; every `after` entry sits in a strictly earlier stage; every `depends_on` edge from
> `backlog.yaml` resolves either to an earlier position in the global sequence-then-stage order, or
> to a phase confirmed `status: complete` and listed in that table's `external_depends_on`; every
> `parallel: true` stage's phase-pairs share no `systems` and no prefix-overlapping `deliverables`
> and carry no direct `depends_on` edge between them. **Zero errors, zero warnings.** `batch-002`
> contains exactly the seven phases the owner named, in that order, matching `next_up`'s head
> exactly.
>
> All six tables validate cleanly against `schemas/batch.schema.json` (draft-07, `jsonschema` +
> `FormatChecker`). Stage numbers match their list index in every table; no `parallel: true` stage
> has fewer than two phases.
>
> **`src/governance/__main__.py`**: diff is exactly one line — `"docs/09-backlog/batches/README.md"`
> added to the `EXEMPT` set at line 41, parallel in form to the existing `"docs/09-backlog/README.md"`
> entry two lines above. No other change in the file. Confirmed: a front-matter-scanner exemption, no
> behavior change beyond letting that one README pass.
>
> 1. **An existing reusable prompt was found rather than a new one written — holds.** `PROMPT-036`
>    existed before this session (created 2026-09-16) and was reused; no competing prompt was authored.
> 2. **The batch table is abstracted out of the prompt behind a schema — holds.**
>    `schemas/batch.schema.json` (new, 172 lines) captures `sequence` (order), `after`/
>    `external_depends_on` (dependencies), and `parallel`/`conflicts_with` (parallelism).
>    `PROMPT-036` no longer contains any phase list — its old inline six-batch table (previously at
>    old lines 124–131) is gone.
> 3. **The original batch table is moved into that form — holds.** `batch-001` through `batch-006`
>    reproduce PROMPT-036's original six batches with membership unchanged (verified by diffing the
>    old inline table against the new tables' phase ids), plus retrospective stage decomposition and
>    `phase-lit-09`'s exclusion correctly carried into `batch-002`'s `excluded` block.
> 4. **The next batch is composed as a new table — holds.** `batch-002` replaces the original batch-2
>    composition with the owner's seven-phase list, independently re-verified with zero errors.
> 5. **Auto-reference latest unstarted/incomplete table, ask only when genuinely ambiguous — holds,
>    and is complete as written.** The rule is exhaustive over the only possible states of the
>    `in_progress` count (0, 1, >1) and the `queued` set (empty, unique lowest-sequence, tied
>    lowest-sequence). No gap found. Two pre-existing "batch 1" prose references are historical
>    narrative about the already-built `batch-001`, not operational references by number — the
>    abstraction is not broken by either.
> 6. **Registered as a protocol — holds.** `GOV-016` (new, 159 lines) governs composition,
>    verification, stages, selection, status/lifecycle and supersession; `GOV-013` and `PROMPT-036`
>    both gained pointer prose. The annotated reason for omitting a `PROMPT-036 → GOV-016` metadata
>    edge (it would close a cycle) is accurate.
> 7. **No batch was run — holds.** All seven `batch-002` phases remain `status: queued`,
>    `agent: None`; `next_up` is unchanged in ranking.
>
> **Fairness of the condition set.** The seven conditions are a fair reading of the "Data + prompt
> now" scope. One gap worth flagging: the owner's instruction said the mechanism should let the
> coordinator "run the prompt automatically" — the conditions test that the *rule* is written and
> deterministic, but nothing tests it *end-to-end* against a live selection. That is an inherent
> limit of "mechanism only, no run," not a defect — but it means condition 5's "holds" is a
> static-correctness verdict, not a tested one.
>
> **Other findings.** `GOV-016`'s "What is not yet enforced" section is accurate: no batch validation
> logic exists in `src/governance/` beyond the one `EXEMPT` string, and nothing prevents two tables
> being `in_progress`. Ideas `000316`/`000317` are present and well-formed, and `000317`'s
> `promoted_to` is consistent with `GOV-016` existing. Catalog counts moved `308 → 310` with
> `governance: 12 → 13` and `session: 130 → 131`; arithmetic checks out against the live count, so no
> drift.
>
> **No discrepancies found** between what the session claims and what the diff, schema validation, or
> a fresh rerun of governance/pytest/my own composition script actually show.

The reviewer's one substantive caveat is accepted rather than fixed: condition 5 is verified
statically, and will only be tested when a coordinator actually selects a table. That is the next
session's first act.

## Decisions

**Use the existing prompt rather than write one.** The opening question had a real answer:
`PROMPT-036` already did what was asked, and its companions `PROMPT-034` and `PROMPT-035` cover
partitioning and queued-phase review. What it lacked was a live table. Writing a second coordinator
would have duplicated a pack that had already absorbed an adversarial review.

**Abstract the table rather than refresh it.** The owner's call, against a narrower option to
re-partition inside the prompt. The argument that decided it is now `GOV-016`'s opening: a table
embedded in a prompt is invisible to every check, so it goes stale silently — which is exactly what
had happened, twice over, by batch 1 completing and two phases being ranked ahead of batch 2.

**Data and prompt only; no validator.** The owner scoped the session so that `AGENTS.md`'s
requirement-and-plan-before-code gate would not apply, and the enforcement work went to `000316` to
be planned properly. One line of `src/` was added anyway and is declared below.

**Selection by an explicit `status` field, with `sequence` breaking ties.** Deriving table state
from the phases' own backlog status was considered and rejected: it cannot distinguish "not started"
from "abandoned", and a phase completed outside a batch confuses it. `sequence` exists so that
several `queued` tables do not force a question at every kickoff, which would move the organising
load back onto the owner — `GOV-006`'s rule against blocking on a question that can be answered.

**Its own governance document, not an extension of `GOV-013`.** `GOV-013` is read by a planning
session designing a coordinator; `GOV-016` is read by whoever composes a batch and by the
coordinator running one. Different readers, different moment.

**An empty batch queue is answered with a proposal, not a blank page.** The owner asked what happens
when nothing is queued. The rule as first written stopped and reported, which is too passive: the
coordinator has just read the backlog and the claiming rules, making it the cheapest place to draw a
candidate partition. It now computes one and puts it to the owner as a question. Composition
authority did not move — the coordinator proposes, the owner disposes, and an unanswered proposal is
not a yes.

## Corrections

**The collision rule was wrong on the first pass, and it mattered.** Deliverable paths were compared
by exact set intersection, which reported `phase-conc-02` and `phase-irs-04` disjoint. They are not:
`tools/git-hooks/` sits under `tools/`. Drawn that way, `batch-002` would have declared a parallel
stage the claim validator refuses. Fixed to a prefix comparison before any table was written; the
rule is now recorded in `GOV-016` and is one of the checks `000316` would enforce.

**The session record was first written in free narrative**, not the six-section contract that
`checkpoint` and `session-close` share. Rewritten at close. A record in the wrong shape is not a
cosmetic problem — the contract is what lets a later reader treat one format rather than two.

**A `depends_on` edge from `PROMPT-036` to `GOV-016` closed a dependency cycle** through `GOV-013`
and was rejected by the validator. The prose pointer stays; the metadata edge was dropped.

## Left undone

**`batch-002` was not built.** The session's purpose became the mechanism. The table is `queued`,
verified, and selectable by the next coordinator with nothing to remember.

**Nothing validates the tables.** `000316` holds that work, and it needs a requirement document, a
plan and phases before it is written. Until then the selection rule's first case — at most one table
`in_progress` — is an assumption rather than an invariant.

**Batches 3 through 6 were carried over unchanged and re-verified, but not re-partitioned.** They
were composed before `phase-gov-05` and `phase-conc-02` entered the queue. Nothing in them is
wrong today, and each will be re-verified before it runs, but a re-partition after `batch-002`
completes would be a reasonable thing for the owner to want.

**Parallelism is declared but untested.** No stage with `parallel: true` has ever been run
concurrently — `batch-001` ran serially, and its stage decomposition is retrospective. The first
real test is `batch-002`'s last stage.
