---
schema_version: 1
id: doc-session-type-taxonomy-requirements
code: REQ-023
title: Session type taxonomy and per-type context requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-governance]
depends_on: [doc-session-lifecycle, doc-governance-protocol]
---

# Session type taxonomy and per-type context requirements

## Observed problem and scope

`AGENTS.md` opens with four steps every session runs regardless of what the session is for. A
planning session, a brainstorming session and an implementation session load the same context and
carry the same obligations today, which is either too strict for exploratory thinking or too loose
for code. [PLAN-008](../01-plans/PLAN-008-session-lifecycle-protocols.md) (`doc-session-lifecycle`)
names this gap and assigns its Phase 1 to define the taxonomy. This document is that taxonomy,
written as observable obligations rather than a description of intent.

Two mechanisms this taxonomy must describe are already built and are treated here as fixed
constraints, not as open questions: the checkpoint skill
(`.claude/skills/checkpoint/SKILL.md`, built by `phase-ses-03`) and the session-close command
(`.claude/commands/session-close.md`, built by `phase-ses-05`). Both are generated or owner-governed
files this document does not modify. Where an obligation below touches session closing, it states
what those two mechanisms already do rather than proposing an alternative.

The decisions this document assumes — whether brainstorming produces a governed artifact, how a
mid-flight type change behaves, and how a type is declared — are recorded in
[ADR-020](../04-decisions/ADR-020-session-type-declaration-and-lifecycle.md) (`doc-session-type-decisions`).
This document states the resulting obligations per type; the ADR states why they were chosen.

## Session types

Three types exist: **planning**, **brainstorming**, and **implementation**. This matches the
owner's stated intent recorded in `PLAN-008`. No fourth type is introduced. A coordinator session
running several backlog phases in a batch (`GOV-003`'s 2026-09-16 entry) is not a fourth type — each
phase it works is still planning or implementation by the rules below, and the coordinator's own
batching behavior is governed by `PROMPT-036`, not by session type.

## R1 — Universal rules apply to every type, without exception

**Statement.** The following rules bind every session regardless of declared or inferred type, and
no type-specific "must never" list below may be read as relaxing them:

- **Confidentiality.** Never write a confidential identifier into a tracked file, in code, a
  document, a commit message, or a session record describing the identifier. Run
  `tools/check_no_private_content.py` with changes staged before any commit that could contain one.
  Never read or write `_private/` unless the owner directs it. (`AGENTS.md`, "Confidentiality and
  publishing".)
- **Code allocation.** Every governed document gets its code from
  `uv run python -m src.governance --next-code <kind>`. Never pick a number by reading a directory.
  (`AGENTS.md`, step 4 of "Read this before doing anything".)
- **The push/integration gate.** Pushing a session's own `agent/<phase-id>` branch to `origin` needs
  no approval. Integrating that branch into `dev` does — ask first, every time. (`AGENTS.md`,
  "Concurrent agents: claim a phase" and "Confidentiality and publishing".)
- **The worktree rule.** Every session works in a worktree; the primary checkout's branch is never
  switched, except for the claim commit and the catalog regeneration it forces. (`AGENTS.md`,
  "Concurrent agents: work in a worktree".)
- **No session decides its own completion.** An agent never sets a phase's `status` to `complete` on
  its own judgement that the work looks finished. Completion happens only through `session-close`
  (`.claude/commands/session-close.md`), or through a coordinator meeting all three conditions in
  `GOV-003`'s 2026-09-16 entry. `checkpoint` (`.claude/skills/checkpoint/SKILL.md`) never writes
  `status: complete`.
- **The session record contract.** Any session that touches a claimed backlog phase writes to the
  one `kind: session` document that phase's `checkpoint`/`session-close` cycle uses, in the shape
  `.claude/skills/checkpoint/SKILL.md` already defines. A brainstorming session working unclaimed
  (no backlog phase — see R4) has no phase to record against and produces no session record; see R2.

**Verification.** `uv run python -m src.governance` exits 0 (checks code allocation and document
shape); `tools/check_no_private_content.py` run with changes staged shows no confidential match;
`git log` for the session's branch shows no commit merged to `dev` without an owner approval message
in the conversation; `.claude/skills/checkpoint/SKILL.md` and `.claude/commands/session-close.md` are
unmodified by any session claiming to be bound by this rule.

## R2 — Brainstorming: obligations

**Must read.** R1's universal rules only. Not the planning methodology, not the repository's code
style and testing conventions (`AGENTS.md`, "Stack" and "Key conventions").

**May skip.** Governed-document front matter, code allocation for anything short-lived, and the
requirement-before-plan sequencing in `AGENTS.md` step 3 — none of that applies until brainstorming
output is promoted out of the session (see R2's "must produce").

**Must produce.** Nothing governed, by default. Per `ADR-020`'s Decision 1: if the session reaches
something worth keeping, it is recorded as one idea per distinct thought through
`tools/append_idea.py` (the sanctioned writer named in `GOV-006`), or carried forward as plain input
to a later planning session. It is never written directly into a REQ, PLAN, or ADR from within the
brainstorming session itself.

**Must never.** Write implementation code. Create or edit a governed document (REQ/PLAN/ADR/GOV).
Claim a backlog phase under `status: active` for brainstorming alone — a brainstorming session that
has nothing to claim runs unclaimed, per `AGENTS.md`'s "Owner-directed work with no backlog phase"
provision, and says so in its first report. Violate any R1 rule.

**Verification.** `git diff` for the session shows no file outside `_data/ideas.jsonl` (via
`append_idea.py`) or files under `docs/00-working/`/`_working/` (ungoverned staging, per `ADR-010`
and `PLAN-015`). `uv run python -m src.governance` shows no new or modified governed-document code
from the session unless it also carried out planning or implementation work per R5.

## R3 — Planning: obligations

**Must read.** `AGENTS.md` in full, including the code-allocation and governed-document rules. The
plan(s) and requirement(s) this session's output depends on or extends. Not the repository's code
style and testing conventions (`AGENTS.md`, "Stack") unless the plan itself concerns code
architecture.

**May skip.** Writing or modifying implementation code, running the test suite, and the code review
skill.

**Must produce.** For any non-trivial change, a `requirement` document stating observable conditions
with verification methods, and/or a `plan` document, each carrying an allocated code from
`uv run python -m src.governance --next-code <kind>` (`AGENTS.md` step 3). Where the plan adds
backlog phases, each phase carries `scope`, `acceptance`, `verification` and `deliverables`
(`AGENTS.md` step 2; an open plan with no phases fails the governance check).

**Must never.** Write implementation code as part of the planning session itself. Mark a phase
`status: complete`. Edit `AGENTS.md` or `CLAUDE.md` without the owner's explicit per-change approval
(both files' own standing rule). Manufacture scope, acceptance or verification content to satisfy the
schema rather than to state a real requirement (the anti-pattern `ADR-010` names by example).

**Verification.** `uv run python -m src.governance` exits 0. Every new governed document's `code`
matches the date `--next-code` returned it on. `uv run python -m src.governance --ready` shows any
new backlog phase this session added, with a non-empty `scope`/`acceptance`/`verification`.

## R4 — Implementation: obligations

**Must read.** `AGENTS.md` in full. The claimed phase's `scope`, `acceptance`, `verification` and
`deliverables` from `docs/09-backlog/backlog.yaml`. The repository's stack conventions
(`AGENTS.md`, "Stack" and "Key conventions"). Any REQ/PLAN the phase implements.

**May skip.** Authoring a new requirement or plan document, if one already exists and is what the
phase implements — implementation does not re-derive planning's output, it consumes it.

**Must produce.** Code, tests and documentation changes that satisfy the phase's `acceptance`
conditions. The literal output of every command in the phase's `verification` list, actually run,
recorded in the session record per `checkpoint`'s contract. A session record via `checkpoint`
(created or updated at least once) before any claim to being done.

**Must never.** Mark its own phase `status: complete` (see R1). Skip `uv run python -m src.governance`
before finishing. Push a merge into `dev` without the owner's approval. Silently retry a failing
check until it passes without recording the failure (`AGENTS.md`'s standing rule, echoed in
`GOV-006`: a failing check is a result to record, not a step to retry until quiet).

**Verification.** Every command in the phase's `verification` list is present, with real captured
output, in the session's `## Verification` section (`checkpoint`'s contract). `uv run pytest` and
`uv run python -m src.governance` both exit 0 before the session reports done.

## R5 — A session's declared type governs what is asked of it; the phase or backlog entry it works governs what type applies

**Statement.** The type an agent is bound by is determined by
`ADR-020`'s Decision 3: inferred by default from the claimed phase's own nature (a
documentation-only phase with `docs/0*` deliverables and no code paths infers planning; a phase with
code or config deliverables infers implementation; an unclaimed session with no phase must be
declared explicitly, defaulting to brainstorming if the owner does not say otherwise), and
overridable by the owner's explicit declaration at any point in the session.

**Verification.** The session's first report states its type and, if inferred, names the phase field
that produced the inference; if declared, names that it was declared and by whom.

## R6 — A session that changes type mid-flight is bound by the new type from the point of change

**Statement.** Per `ADR-020`'s Decision 2, a session is not required to restart or split into two
session records when its type changes. From the moment of the change forward, the new type's "must
produce" and "must never" obligations in R2–R4 apply; obligations already satisfied under the prior
type are not retroactively undone or redone. R1's universal rules apply before, during and after the
change without exception, since they are not type-scoped.

**Verification.** Where a session record exists, its narrative (in `session-close`'s `## Decisions`
section, or a `checkpoint` note) states the type change and the point at which it happened. `git log`
for the session shows no commit that satisfies a looser type's obligations after the point a stricter
type began applying.
