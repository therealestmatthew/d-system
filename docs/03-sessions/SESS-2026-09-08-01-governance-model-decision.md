---
schema_version: 1
id: doc-session-2026-09-08-01
code: SESS-2026-09-08-01
title: Answer PROMPT-005 with one ADR on the governance kind/system split
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-governance]
depends_on: [doc-governance-model-prompt]
---

# Answer PROMPT-005 with one ADR on the governance kind/system split

## Phase

`phase-gov-02` — Decide whether governance is a system, a kind, or both.

## Verification

`uv run python -m src.governance`
```
Governance OK: 16 systems, 77 documents, 13 memories, 96 backlog phases
```

`uv run pytest`
```
313 passed, 2 warnings
```

`uv run python -m src.governance --catalog > docs/08-governance/catalog.md` — regenerated twice: once
after adding `ADR-011` (76 documents), again after adding this session record itself (77 documents).
Both diffs were additive only — the new document's row and an updated count — no manual edits.

## Acceptance

- **One ADR answers all five questions, including any answered leave it alone.** Met —
  [ADR-011](../04-decisions/ADR-011-governance-model.md) has one numbered `## Decision` subsection per
  PROMPT-005 question, including questions 2, 4 and 5, which conclude "leave it alone"/"no new field"
  and say so explicitly rather than by omission.
- **Every claim cites a real document in this repository.** Met — each subsection cites and quotes
  from a real source: `GOV-001`'s taxonomy and enforcement tables, `systems.yaml`'s `sys-governance`
  entry, `GOV-002`/`GOV-003`/`GOV-004`'s `systems` fields, `OPS-001`'s failure table,
  `src/governance/backlog.py`'s `inspect_backlog` (the `decision_record` kind check at line 109), and
  `backlog.yaml`'s live `decision_record: doc-backlog-decisions` value. No claim rests on an
  unattributed "in principle" argument.
- **No schema is written this session; changes become phases.** Met — `document.schema.json`,
  `systems.schema.json` and `backlog.schema.json` are all unchanged; `git status` shows only the new
  ADR, the backlog claim, the regenerated catalog and this session record.

## Backlog

`phase-gov-02` moves from `queued` to `active` (claimed as `agent-gov02`), then this checkpoint
records `session`, `completion_evidence` and `result` while it stays `active` — only the owner-invoked
`/session-close` may set `status: complete`.

## Unresolved

`status` stays `active`. [PLAN-014](../01-plans/PLAN-014-governance-and-complexity-review.md)'s next
step, `PROMPT-003` (`phase-gov-03`), is now unblocked and can treat the governance/operation split as
settled per the plan's stated sequencing.

## Review

Independent review by a fresh, non-fork sub-agent, given the phase's `scope`/`acceptance`/
`verification` (pasted from `backlog.yaml`), the commit range `the commit “Claim phase-gov-02 as agent-gov02”..HEAD` (the two commits after
the claim commit: the commit “Add ADR-011, answering PROMPT-005's governance kind/system question” adding ADR-011, the commit “Checkpoint phase-gov-02 with session record and catalog regen” the checkpoint), and this session record.
Instructed to independently rerun verification and check ADR-011's citations against the real
documents rather than trust the record's claims. Reported verbatim:

> ### Acceptance conditions
>
> **1. One ADR answers all five questions, including "leave it alone" ones — Met.** ADR-011 has five
> numbered `## Decision` subsections mapping 1:1 to PROMPT-005's five questions. Sections 2, 4, and 5
> explicitly conclude "No enforced-vs-convention field," "Subsystems do not get their own governance
> concept," and "No `governed_by` field" — stated outright, not left to silence.
>
> **2. Every claim cites a real document — Met**, based on sampling 7+ claims across all five
> sections; every one checked out against the actual file.
>
> **3. No schema written this session — Met.** `git diff the commit “Claim phase-gov-02 as agent-gov02”..HEAD -- schemas/` is empty;
> confirmed independently by full `git diff --stat` (only ADR-011, the session record, `backlog.yaml`,
> and `catalog.md` changed).
>
> ### Claims verified
>
> - (a) `src/governance/backlog.py` line 108-109: `decision = documents.get(catalog["decision_record"]);
> if not decision or decision["kind"] not in {"governance", "adr"}:` — **True**, matches ADR-011's
> claim about `inspect_backlog` exactly, including that `operation` is rejected.
> - (b) `GOV-003` front matter: `systems: [sys-backlog, sys-projection, sys-html, sys-memory-agents]`
> — **True**, no `sys-governance` present, as ADR-011 claims.
> - (c) GOV-001 taxonomy table: `operation` → "Trigger, command, expected result, failure/recovery
> steps"; `governance` → "Rules, scope, enforcement and exceptions" — **True**, verbatim match to
> ADR-011's quotes.
> - `systems.yaml`'s `sys-governance` entry paths (`src/governance`, `schemas/document.schema.json`,
> `schemas/systems.schema.json`, `schemas/codes.schema.json`, plus the registry files) — **True**,
> matches ADR-011 section 1 exactly.
> - GOV-001's "Enforcement and adoption boundaries" table (mechanism/result columns, CI failure vs.
> warning vs. human decision) — **True**, exists as described and supports ADR-011 section 2's claim.
> - GOV-001's "not a second project portfolio" line — **True**, quoted verbatim in the "Inventory
> without duplicate bookkeeping" section, supports ADR-011 section 5.
> - `phase-tool-01`'s scope bullet: "Use whichever series phase-gov-02 settles on; do not mint OPS
> codes before that decision." — **True**, confirms ADR-011's unblocking claim and the session record's
> claim.
> - PLAN-014's sequencing note that PROMPT-005 decides the merge question before PROMPT-003
> re-litigates it — **True**, present at lines 59-61.
>
> ### Verification commands rerun
>
> - `uv run python -m src.governance` → `Governance OK: 16 systems, 77 documents, 13 memories, 96
> backlog phases` — matches session record exactly.
> - `uv run pytest` → `313 passed, 2 warnings` — matches session record exactly.
> - `uv run python -m src.governance --catalog` regenerated and diffed against the committed
> `docs/08-governance/catalog.md` → **no drift**, diff is empty.
> - `git diff the commit “Claim phase-gov-02 as agent-gov02”..HEAD -- schemas/` → empty, confirming the no-schema claim.
> - Backlog status: `phase-gov-02` is still `status: active` (not `complete`) after the checkpoint
> commit, consistent with the rule that only `/session-close` sets `complete`. `decision_record:
> doc-backlog-decisions` resolves to GOV-003, `kind: governance` — consistent with the passing
> `inspect_backlog` check.
>
> ### Discrepancies found
>
> None. Every sampled claim in ADR-011 and the session record checked out against the actual
> repository state — code, front matter, tables, and command output all matched. The session record's
> own acceptance self-assessment ("Met" on all three conditions) is accurate on independent
> re-verification.
>
> ### Recommendation
>
> **This phase should be marked complete.** All three acceptance conditions hold under independent
> verification, the cited claims are accurate (not just plausible-sounding), the verification commands
> reproduce exactly as claimed, and no schema or code beyond documentation/backlog metadata changed.
> The one soft note: the session record's claim about "regenerated twice: once after adding ADR-011
> (76 documents), again after adding the session record (77 documents)" describes intermediate process
> state that isn't independently reproducible from the final diff alone — but the final state (77
> documents, no catalog drift) is verified, so this doesn't affect the acceptance call.

## Decisions

The five questions, answered in [ADR-011](../04-decisions/ADR-011-governance-model.md):

1. **Kind and system are orthogonal, not redundant.** `kind: governance` fixes a document's body
   shape; `sys-governance` tracks the `src/governance` component's paths/owner/maturity like any other
   implemented system. `GOV-003` proves the independence directly — it is `kind: governance` and
   carries zero `sys-governance` in its `systems` list.
2. **No enforced-vs-convention field.** `GOV-001`'s existing enforcement table already classifies
   every rule category by mechanism and result; a per-document field would duplicate it.
3. **`governance` and `operation` do not merge.** Two independent reasons: `inspect_backlog` only
   accepts `kind` `governance` or `adr` as a valid `decision_record` (`operation` is rejected), and the
   two kinds' real documents are structurally different — GOV-002 is declarative rules, OPS-001 is an
   imperative runbook — matching their different body-requirement contracts in `GOV-001`'s taxonomy
   table. This unblocks `phase-tool-01`, which was waiting on this decision: it uses the `OPS` series.
4. **Subsystems already have their own governance via the `systems` field** — no new per-system
   governance concept is needed. `GOV-002`/`GOV-004` scoping to `sys-backlog` is the mechanism the
   question was asking whether to invent.
5. **No `governed_by` field on `systems.yaml`.** The reverse edge is already answerable by
   cross-referencing existing `systems:` front matter, and `GOV-001`'s own "no second project
   portfolio" rule argues directly against adding a hand-maintained duplicate of it.

**Filed as one ADR against the existing plan**, per PLAN-014's own instruction that the investigation
produce exactly one ADR answering all five questions together, rather than splitting the "leave it
alone" answers out of the record where they would be silently re-litigated later.

## Corrections

None. No mistakes were made and fixed mid-session; the ADR was drafted once from the evidence gathered
during orientation and did not need rework after the independent review.

## Left undone

Nothing on this phase's own scope. `phase-tool-01` and `phase-gov-03`, both previously waiting on this
phase, are now ready but were not started — each is its own phase with its own session budget.
[PLAN-014](../01-plans/PLAN-014-governance-and-complexity-review.md)'s next step is `phase-gov-03`
(PROMPT-003), which can now treat the governance/operation merge question as settled rather than open.
