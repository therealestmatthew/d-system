---
schema_version: 1
id: doc-idea-plan-lifecycle
code: PLAN-017
title: Unified idea and plan lifecycle architecture
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-portfolio, sys-projection, sys-governance, sys-backlog]
depends_on: [doc-idea-plan-lifecycle-requirements, doc-idea-record-system]
---

# Unified idea and plan lifecycle architecture

The outcome is a trustworthy path from captured thought through reviewed work to evidence of a
functioning result. Ideas keep immutable history and an intelligible current view; plans cannot claim
states their phases contradict. This is the synthesized proposed architecture, not implemented
capability or approval to execute the implementation phases.

The [requirements](../../06-requirements/REQ-003-idea-plan-lifecycle.md) define observable outcomes.
The [transcript analysis](../../00-working/idea-plan-architecture/transcript-analysis.md) is part of
this handoff. The dedicated reader read the entire export before category work. The export directly
confirms L1–L4 and ends there. L5–L11, detailed flags and folder instructions remain constraints from
the current brief, not quotations independently confirmed in that transcript.

## Design and evidence

The supplied authoritative synthesis corrects eight errors in the original brief. Preserve its
three governing pre-task observations: 19 creation events, zero status transitions; no historical plan
activation; only 2 of 21 plans complete and no completion among five plans with at least eight phases.
The snapshot dates to 2026-09-06 before this architecture adds documents and phases.

Code review confirms the relevant corrections: open-plan coverage and complete-plan evidence are
already enforced; HTML children have 3/3/2/3/1/2 phases through sources; replay is repeated in writer,
rebuild and the projection test fixture; the command lives at `.claude/commands/idea.md`.
The idea-to-idea prose-reference count is 7 of 19, not 16. The supplied whole-Python ratio is 47%,
not 75%. Those counts justify restrained scope, not a new portfolio-data analysis during this task.

The original brief also overstates the identity problem: the owner explicitly requested the first
two related ideas separately. The demonstrated gap is a later requested update captured as a new
idea. Preserve all IDs and all prose. Relationships and corrections do not retrospectively turn
separate captures into one concept or rewrite metric denominators.

An amendment is its own event, and it names its target by **identity rather than by position**.
The secondary identifier and the deliberate key collision are both dropped, and so is the sequence
pointer that first replaced them: `seq` exists nowhere in the log — the rebuild derives it from a
line's ordinal — so an `amends: <seq>` pointer would address a number that concurrent appends are
free to change. Every new event instead carries a writer-generated `eid`, and the 19 historical
events resolve to the digest of their own permanent bytes, so no existing line is rewritten.

Amendments resolve recursively and merge in append order, then the base events replay once. The
boolean replace/clear/inherit truth table is kept exactly as the owner specified. Required fields
cannot be cleared; correcting one contribution never wipes its siblings. Replay validates the whole
effective state history before any write and before any destructive projection.

This retains append-only correction, composes unrelated field corrections, and rejects retroactive
state-machine breaks. Because identity is not positional, an `amends` pointer survives a git merge
that interleaves two worktrees' appended lines — the independent-worktree race becomes a property of
the data rather than a serialisation rule the write contract has to uphold. The DuckDB primary key
moves from `(idea, seq)` to the resolved identity, which removes the constraint violation rather than
routing around it. `PLAN-017.03` holds the full specification.

## Category architecture

Six category children occupy the four requested folders. Their durable content is governed only
after reconciliation; exploratory source analysis remains ungoverned under `docs/00-working/`.
No new document kind, system registration, tag registry or application is created.

| Folder | Child | Category | Original categories absorbed |
|---|---|---|---|
| The Idea Lifecycle | `PLAN-017.01` | Capture, triage, resolution and promotion bridge | G, I; capture boundary from M |
| The Plan Lifecycle | `PLAN-017.02` | State consistency, activation and closure | H |
| Idea Architecture | `PLAN-017.03` | Event contract, identity and validating amendment fold | A, B, C |
| Idea Architecture | `PLAN-017.04` | Annotations and relationship contributions | D, E |
| Idea Architecture | `PLAN-017.05` | Safe writing, projection, rendering and analysis | J, K, L, historical compatibility from M |
| Plan Architecture | `PLAN-017.06` | Governance integration and phase delivery | N; shared compatibility/decision gates |

The four folders required relaxing `src/governance/codes.py`, which rejected any plan document
nested inside a plan folder. One area-folder level is now permitted, for sub-coded children only,
and the rule is documented in `GOV-005` where it had never been stated. `PLAN-017.06` records this
as a finding for the complexity review rather than leaving it for that review to discover.

F (tags/classification) becomes a deferral row. B loses the secondary ID. M loses the nonexistent
child-plan migration and unauthorized historical repair. K loses speculative tag tables and
unsupported metric promises. Shared implementation phases cover several children through `sources`;
six category documents do not imply six independent projects.

## What ships and what waits

| Scope | Disposition and evidence gate |
|---|---|
| Safe input, shared fold, from-check, plan activation consistency | First implementation phase; no event/document schema change |
| Typed annotations, triaging and collapsed agent rendering | Minimal second phase; existing triage phase consumes it |
| Corrected amendments | Build with flags, backward pointers, chain merge and semantic preflight |
| Links and validated promotion arrays | Build extends/supersedes/relates_to only; derive inverse and reverse promotion lookup |
| Tags and classification | Deferred: 60 captured ideas or a recorded failed retrieval; then decide tags/links boundary and namespace before design |
| Mandatory idea-to-plan provenance | Do not build. Reconsider only as a separate prospective proposal supported by observed provenance loss; never fabricate historical captures |
| Additional edge types/graph engine/dashboard | No current implementation. Revisit only when an actual relationship/query cannot be represented or Markdown prevents a documented decision |
| Duplication rate, ideas per session, complete plan history | Deferred for definitions/source evidence; no proxy claims |

First-phase value is independently testable even if the rest never ships. Five new implementation
phases are proposed, plus reuse of the existing triage phase. Each is one session; an overrun releases
an exact remainder rather than expanding indefinitely. The detailed acceptance, verification and
path locks live in the delivery child and backlog. Architecture authorship is a separate completed
work item under the existing ephemeral-task policy; it is not implementation completion here.

## Complexity review recommendation

The systems complexity review (`phase-gov-03`) cannot in fact run alongside this work: it is queued
behind the governance review (`phase-gov-02`), which is queued behind its terminology prerequisites.
"Alongside" was not an available option. What is available is a split — the live repairs (phases 1-3)
need no schema change and can proceed now; the schema extensions (phases 4-5) wait on the review.

Whether to promote the review chain in `next_up` so it stops blocking those extensions is the
owner's call and the most consequential open item in this plan set. The recommendation is to promote
it: a review whose stated bias is removal should see a schema extension before it ships, not after.
This session neither claims nor executes that review, and does not reorder `next_up`.

The systems review prompt (PROMPT-003) prohibits new systems, kinds, folders and schemas **in that
review session**. This separately authorized architecture introduces the requested documentation
folders within existing kinds/systems and proposes changes to an existing schema. It does not evade
the review: its removal findings must be reconciled before extensions ship. Live repairs can land
first without waiting on that schema decision. Existing lock overlap precludes simultaneous writes
by this architecture phase and the review, even when their deliberation is described as alongside.

## Cross-category conflicts and disposition

| ID | Contradiction or gap | Disposition; decision owner and stage |
|---|---|---|
| C01 | Latest record selection loses inherited corrections; repeated keys violate SQL | Resolved by task synthesis: backward pointer plus merge chain, unique seq |
| C02 | Nested amendment corrected later versus later direct sibling at base | Recommend nested correction stays at target amendment's slot; event child gives worked counterexample; confirm before amendments |
| C03 | Clear any field versus required creation/state fields and NOT NULL | Clear only optional contributions; required clears refused; optional note/link payload permits retraction |
| C04 | Final-state-only display versus visible-correction convention | Preserve clean current view as brief instructs; raw/history access stays available without a per-idea amendment badge; do not re-ask a locked display decision |
| C05 | Terminal status versus later notes/links/corrections | Terminal governs state transitions; non-state events permitted; corrected full history must remain legal |
| C06 | Supersedes relation versus discarded status and later revisit | No implicit state mutation by a link. Separate explicit discard; legal revisit may retain historical relationship and show a diagnostic |
| C07 | Ordinal pointers versus independently appended worktrees | **Resolved by identity.** An `amends` pointer names an event id, not a position, so interleaved appends from sibling worktrees still resolve. No serialisation rule is load-bearing |
| C08 | Derived plan status versus human approval and intent review | Derive consistency/eligibility; never derive consent or automatic completion |
| C09 | Activation enforcement versus claim-only commit | Authorized activation commit precedes claim commit; update existing command and protocols together |
| C10 | Complete/cancelled closure currently allowed versus literal all-complete | **Decided: warn, not fail.** A plan whose phases are complete-or-cancelled may be complete if its `completion_evidence` says why the cancelled phases were dropped. `GOV-002` is unchanged |
| C11 | Historical valid promotion versus target later deprecated/superseded | Preserve raw reference; new/effective target validation and current lifecycle diagnostics are distinct |
| C12 | Prior PLAN-016 omits triaging; brief L7 requires it | Add triaging with minimal annotations; preserve old legal transitions; amend conflicting documentation when implemented |
| C13 | Existing triage phase is ready before its new annotation contract | Reuse it, propose exact dependency/scope update before execution; no duplicate triage implementation phase |
| C14 | Rich metrics versus zero observed transitions and absent session IDs | Test with synthetic transitions; report observation limits; defer undefined duplication/session metrics |
| C15 | Complete machine-readable plan history versus mutable metadata and planned history squash | Narrow current promise to consistent state plus retained session evidence; historical plan timing remains open, no invented plan-event schema |
| C16 | Architecture authoring completed under draft ephemeral policy versus future upstream status rule | Preserve honest draft status of new proposals. First repair rescans all plans, including policy plan now gaining completed documentation work; do not freeze the four-case baseline as an exhaustive migration list |
| C17 | New idea versus correction, and prose references versus graph identity | Default to capture as given; correct only an explicitly identified mistake/update; no automatic identity merge or prose-extracted authoritative edge |
| C18 | Mandatory amendment reason recommendation versus brief's owner preference against ceremony | Recommend optional reason pending Q-A3; raw pointer/field delta remains auditable; do not claim mandatory reason was approved |
| C19 | Accepted ADR reversal rule versus open amendment/successor choice | Recommend narrowly scoped successor per GOV-001, preserving all old text; decide before amendment implementation |
| C20 | Historical scalar promotion compatibility versus new array-only writer | Read legacy scalar as singleton without rewriting; new writes use validated arrays; retain raw form |
| C21 | Claimed owner quotations versus truncated exported conversation | Transcript report is authoritative on attribution; current task remains authoritative on requested design |

## Acceptance and review

The architecture is complete when all categories carry known/proposed/open/touches/verified/conflicts,
requirements map to genuine session-sized phases, the transcript discrepancies and every conflict
above have visible dispositions, and catalog/governance checks pass. Implementation acceptance is
R01–R17, with owner review of actual behavior and evidence before parent completion. This draft's
existence cannot mark any implementation phase complete.

Remaining choices are collected in their owning children: nested precedence, reasons, correction
scope limits, cancellation semantics, ADR handling, promotion target breadth, triage bypass, supported
metric cutoffs and deferred tag boundaries. Recommendations are concrete enough to review; they do
not manufacture consent. Closed questions Q-H3/H4 and Q-A2's basic permissibility are removed.
