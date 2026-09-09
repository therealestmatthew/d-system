---
schema_version: 1
id: doc-session-2026-09-07-07
code: SESS-2026-09-07-07
title: Terminology content — vocabulary and architecture overview
kind: session
status: active
owner: repository-owner
created: '2026-09-07'
updated: '2026-09-07'
systems: [sys-brain, sys-governance]
depends_on: [doc-terminology-system]
---

# Terminology content — vocabulary and architecture overview

## Phase

`phase-term-02` — Define the vocabulary and document the architecture.

## Verification

`uv run python -m src.governance`
```
Governance OK: 16 systems, 75 documents, 13 memories, 96 backlog phases
```

`uv run pytest`
```
312 passed, 2 warnings
```

`uv run python tools/load_context.py --query "ephemeral plan"`
```
Retrieved: 2 memories
```
Both matches are the new grouped concept memories (Plans and Work; Data and Storage), each containing
a definition whose body includes the term "ephemeral plan".

`uv run python tools/load_context.py --system sys-backlog`
```
Retrieved: 1 memory
```
The match is the new "Plans and Work" concept memory, tagged `systems: [sys-backlog, sys-governance]`
— confirming the `--system` filter (built in `phase-term-01`) actually selects content by subsystem.
Both commands required `tools/rebuild_db.py` to be re-run first, since the five new memories had not
yet been projected into DuckDB; that rebuild is recorded here as part of verification, not as a
separate deliverable.

## Acceptance

- Every term listed in PROMPT-004 is defined or explicitly deferred with a reason. **Met** — all 43
  terms across the five domain groups in PROMPT-004 (Plans and work; Documents and governance; Data
  and storage; Memory and retrieval; Systems) are defined in `brain/concepts/terms-*.md`, none
  deferred.
- The architecture overview names every subsystem and how they depend on each other. **Met** —
  `docs/07-architecture/ARCH-004-architecture-overview.md` §3 tables all 16 `systems.yaml` entries
  with their `depends_on` edges, matching the "16 systems" count the governance check reports.
- No per-subsystem architecture document is created. **Met** — the only new file under
  `docs/07-architecture/` is the one overview, `ARCH-004`.

## Backlog

`phase-term-02` remains `status: active`, `agent: agent-term02`. `next_action` unchanged: "All scope
items complete and verification passes (SESS-2026-09-07-07); ready for `/session-close` review."

`session`, `completion_evidence` and `result` are now populated on the phase while it stays `active` —
`phase-ses-06` (see `SESS-2026-09-07-08`) fixed the validator gate that previously rejected these
fields outside `status: complete`, so they are written here rather than deferred to close:

- `session: doc-session-2026-09-07-07` (this record)
- `completion_evidence`:
  - `brain/concepts/terms-plans-and-work.md`
  - `brain/concepts/terms-documents-and-governance.md`
  - `brain/concepts/terms-data-and-storage.md`
  - `brain/concepts/terms-memory-and-retrieval.md`
  - `brain/concepts/terms-systems-vocabulary.md`
  - `docs/08-governance/GLOSSARY.md`
  - `docs/07-architecture/ARCH-004-architecture-overview.md`
  - `docs/08-governance/systems.yaml`
- `result`: all three acceptance conditions met — see `## Acceptance` above.

## Unresolved

None. The process gap noted in an earlier version of this record — the checkpoint skill's
instructions and the governance validator disagreeing about whether evidence could be recorded before
completion — was resolved by `phase-ses-06`; see `SESS-2026-09-07-08`. `status` stays `active` because
only `/session-close` (owner-invoked) may set `status: complete`, after its own independent review.

## Review

Independent review by a fresh, non-fork sub-agent, given the phase's `scope`/`acceptance`/
`verification`, the exact commit list (“Define the shared vocabulary in brain/concepts and regenerate the glossary”, the commit “Write the architecture overview and enrich systems.yaml”, the commit “Record the phase-term-02 session and update next_action”, the commit “Checkpoint phase-term-02 at session-close, evidence now recorded live” — explicitly
excluding the interleaved, unrelated `phase-ses-06` commits “Claim phase-ses-06 (agent-ses06)”/“Let checkpoint record evidence while a phase is active or blocked”/the commit “Record phase-ses-06's session and dogfood the new evidence gate” that fall
chronologically between them on `dev`), and this session record. Reported verbatim:

> **Verification command outputs (actual, fresh reruns)**
>
> All four commands rerun independently: `uv run python -m src.governance` → `Governance OK: 16
> systems, 75 documents, 13 memories, 96 backlog phases` (exit 0); `uv run pytest -q` → `312 passed, 2
> warnings` (exit 0); `uv run python tools/load_context.py --query "ephemeral plan"` → 2 memories
> (Data and Storage, Plans and Work, both containing "ephemeral plan"); `uv run python
> tools/load_context.py --system sys-backlog` → 1 memory (Plans and Work, tagged `systems:
> [sys-backlog, sys-governance]`). All four match this record's claimed output exactly, including
> exact counts. No discrepancy. Additionally ran `uv run python tools/generate_glossary.py --check`
> (not one of the four listed, but relevant to PROMPT-004 Part 4's "no hand edits") — passes.
>
> **Per-condition verdict**
>
> 1. *"Every term listed in PROMPT-004 is defined or explicitly deferred with a reason."* — **Met.**
>    Independently enumerated PROMPT-004's Part 2 term list (5 groups, 43 terms total) and checked
>    each against `brain/concepts/terms-*.md`: Plans and work (11/11), Documents and governance
>    (9/9), Data and storage (9/9), Memory and retrieval (10/10), Systems (4/4). Total 43/43, none
>    deferred, no missing term found. Each entry follows the "what it is / what it is not / governing
>    pointer" format PLAN-012 requires.
> 2. *"The architecture overview names every subsystem and how they depend on each other."* —
>    **Met.** Independently parsed `systems.yaml` and diffed it against `ARCH-004`'s §3 table: domain,
>    status and `depends_on` match row-for-row for all 16 systems, including the retired `sys-course`
>    (empty deps, correctly shown). No system omitted, no dependency misstated.
> 3. *"No per-subsystem architecture document is created."* — **Met.** The log from “Claim phase-term-02
>    (agent-term02)” to “Checkpoint phase-term-02 at session-close, evidence now recorded live” over
>    `docs/07-architecture/`, and a directory listing at that same commit, show only
>    `ARCH-004-architecture-overview.md` was added; `ARCH-001`/`002`/`003` pre-date this phase.
>
> **Discrepancies between session record and reality**
>
> None found. Every specific claim in this record (term count of 43, verification outputs, ARCH-004's
> coverage of "16 systems.yaml entries," the single new architecture file, the `completion_evidence`
> file list) checked out against the diff and fresh command runs. The five `systems.yaml` descriptions
> the commit message says gained a "does not yet" clause (`sys-contracts`, `sys-brain`,
> `sys-delivery`, `sys-governance`, `sys-backlog`) are indeed the exact five changed by the commit “Write the architecture overview and enrich
> systems.yaml”.
>
> **Overall recommendation**
>
> The work genuinely supports marking `phase-term-02` complete. All three acceptance conditions hold
> under independent inspection, all four verification commands reproduce cleanly, term coverage is
> exhaustive against the actual PROMPT-004 list (not just the session record's count), and the
> architecture table is verifiably accurate against `systems.yaml`. The interleaved `phase-ses-06`
> commits were correctly excluded from this phase's own diff and did not contaminate the review — no
> cross-contamination found.

## Decisions

- **Scope was interpreted as content-only**, since `phase-term-01` (a separate, already-complete
  phase) had already built the scaffolding (the `systems` field on `schemas/memory.schema.json`, the
  `--system` filter on `tools/load_context.py`, `tools/generate_glossary.py`, and the glossary
  regression test). This session verified that scaffolding was actually present before treating
  `PROMPT-004`'s Part 1 as satisfied, rather than re-deriving it from the plan alone.
- **Grouped concept memories, not one file per term**, per `PLAN-012`'s explicit design: one memory
  per domain group (five files), each containing all of that group's terms as `###` subsections. This
  is what the glossary generator (`tools/generate_glossary.py`) expects — it renders one memory's
  whole content under one glossary heading, so per-term files would have produced 43 separate glossary
  sections instead of five coherent ones.
- **The architecture overview absorbed Parts 3, 3b and 3c of PROMPT-004** (subsystem topology,
  governance-document description, tooling description) into one document rather than three, since the
  phase's own acceptance condition forbids new per-subsystem documents and no separate deliverable was
  named for the governance/tooling descriptions — they read naturally as sections of the same
  reader-first entry point.
- **Only 5 of 16 `systems.yaml` descriptions were edited**, not all 16, because most already stated
  what the subsystem does *and* does not yet do; editing prose that already met the bar would have
  been churn. The five picked (`sys-contracts`, `sys-brain`, `sys-delivery`, `sys-governance`,
  `sys-backlog`) were the ones a direct read found missing that clause.
- **The owner directed that `phase-term-02`'s own declared `verification` list be corrected** at claim
  time (adding `uv run pytest` and the `--system sys-backlog` check), since it was thinner than
  PROMPT-004's own Part 4 verification section — this overrode the phase as originally filed rather
  than working around the gap silently.

## Corrections

- **`sys-brain`'s description named a stale, hardcoded memory count** ("Seven initial memories") that
  had already drifted before this session started (13 memories exist). Replaced with a qualitative
  description (memory types, the new `systems` field) specifically so it can't go stale the same way
  again — a count in prose is exactly the kind of fact this session's own vocabulary work argues
  should live in a query, not a sentence.
- **DuckDB was stale mid-session.** The two `load_context.py` verification commands initially failed
  (`No memories matched`; a `BinderException` on the `systems` column) because `tools/rebuild_db.py`
  had not been re-run after the five new memories were written. This is expected projection behavior,
  not a bug — recorded here because it is the kind of thing a reader of this record would otherwise
  reasonably wonder about, given the commands are listed as straightforward verification.

## Left undone

Nothing on this phase's own scope. Two things surfaced during the session that belong to other, not
-yet-started phases and were deliberately not pulled in:

- The `sys-contracts` enrichment this session added notes that JSON Schemas don't check that
  references resolve (no foreign keys in the DDL) — a known, already-tracked gap, not something this
  phase was scoped to fix.
- `sys-delivery`'s enrichment notes `tools/` isn't yet covered by the documented lint gate — already
  owned by `phase-rel-09`, not duplicated here.
