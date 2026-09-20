---
schema_version: 1
id: doc-session-taxonomy-investigation-requirements
code: REQ-026
title: Session-type taxonomy investigation requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-19'
updated: '2026-09-20'
systems: [sys-governance]
depends_on: [doc-session-type-taxonomy-requirements, doc-session-type-decisions]
---

# Session-type taxonomy investigation requirements

Observable requirements for the two-session investigation
([PLAN-042](../01-plans/PLAN-042-session-taxonomy-investigation.md)) that proposes a theoretical
taxonomy of Claude Code session types and then tests it against this repository's raw transcripts
and session records. The existing governed taxonomy — the per-type obligations requirement
(`REQ-023`) and the type-declaration decision (`ADR-020`), both from `phase-ses-01` — is prior
art the investigation builds on and evidence-tests; this document does not amend either.

## R01 — Registered theory with falsifiable predictions

`docs/00-working/session-types-theory.md` exists and proposes a taxonomy in two layers: a
portable core (types defined without naming any d-system artifact) and an expected d-system
binding per type. Every proposed type carries predictions bound to observables — first-prompt
signature, activity signature, artifact produced, an expected frequency band — and at least one
observation that would count against the type as defined. Where the proposal departs from
`REQ-023`'s type set, the departure and its reason are stated explicitly.

**Verification:** read the document; every type carries all five prediction elements, and a
REQ-023 reconciliation section exists.

## R02 — Theory precedes evidence

The theory is registered before any evidence is examined: the session that writes it reads no
raw transcript and no session-record contents (record titles for orientation only), and does not
read the Part 2 prompt. **"The session" includes every agent it dispatches** — a sub-agent reading
what the session may not read is the session reading it, and its report reaching the session's
context is the same exclusion breached at one remove. The two phases run as separate sessions with
the owner's explicit go between them.

The boundary is the **commit that adds `docs/00-working/session-types-theory.md`**. Before it, the
exclusions bind absolutely. After it the theory is frozen and cannot be shaped by anything read
later, so a post-registration read does not breach this requirement — but it is disclosed in the
session record, naming what was read and whether any of it entered the session's context.

**Verification:** `phase-tax-01`'s session record names its inputs and attests the exclusions, and
discloses any post-registration read with its position relative to the boundary commit; the
ordering is independently checkable from git author dates, which survive a rebase where committer
dates do not. `phase-tax-02`'s session record cites `session-types-theory.md` as a pre-existing
input.

**Amendment, 2026-09-20.** The sub-agent clause and the boundary paragraph were added after
`phase-tax-01` completed, on a defect its independent reviewer raised: R02 as first written said
"the session" without saying whether a dispatched agent counted, where `R06` addresses sub-agents
explicitly — so the omission could be read either way. **This amendment does not move the bar
`phase-tax-01` was judged against.** That phase satisfied both readings on evidence the reviewer
verified independently: its theory commit precedes any session-record read by 82 minutes, its one
dispatched scout ran after the boundary, and that scout's findings were written to a gitignored path
and never entered the session's context. The clause is stated for `phase-tax-02`, which dispatches
sub-agents by design and where the ambiguity would otherwise be load-bearing.

## R03 — Evidence-tested taxonomy with a prediction scorecard

`docs/00-working/session-taxonomy.md` exists and leads with a scorecard giving every Part 1
prediction an outcome (confirmed / disconfirmed / not testable, with the deciding evidence),
followed by: the portable taxonomy with its external-validity caveat (existence is the portable
claim; frequency is local), the d-system binding per type with evidence counts and governance
obligations, orchestrator variants with boundary criteria, undocumented and proposed types, and
proposal-only inputs to the CLAUDE.md / AGENTS.md revamp including an evaluation of the owner's
design notes (Appendix A of the Part 1 prompt).

**Verification:** read the document; every prediction from R01 appears in the scorecard with an
outcome; no section edits or instructs edits to CLAUDE.md or AGENTS.md.

## R04 — Private content stays private

All derived transcript reductions (`manifest.tsv`, `prompts/`, `signatures/`,
`record-structure.tsv`) exist only under `_private/analysis/session-taxonomy/`, and no tracked
file written by the investigation quotes a confidential identifier — transcript content appears
in tracked deliverables only paraphrased or with identifiers removed.

**Verification:** the derived files exist at that path and nowhere trackable;
`uv run python tools/check_no_private_content.py` passes with the investigation's changes staged.

## R05 — Record-structure table ready for the record critique

`_private/analysis/session-taxonomy/record-structure.tsv` covers every `docs/03-sessions/SESS-*`
file with sections-present-versus-contract, line count, front-matter completeness, and
non-contract sections — the input `phase-fwa-03` (PLAN-041, idea `000276`) consumes.

**Verification:** the table's row count equals the SESS file count at run time.

## R06 — No agent reads a raw transcript

Reduction is done once by a deterministic script; every sub-agent and the orchestrator read only
derived files. The script's location is recorded in the Part 2 deliverable, and an idea
proposing its promotion to `tools/` is captured through `tools/append_idea.py` with the id
confirmed to the owner.

**Verification:** `phase-tax-02`'s session record names the script location and the captured
idea id; the id appears in the idea fold.
