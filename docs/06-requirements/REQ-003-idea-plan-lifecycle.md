---
schema_version: 1
id: doc-idea-plan-lifecycle-requirements
code: REQ-003
title: Idea and plan lifecycle integrity requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-portfolio, sys-projection, sys-governance, sys-backlog]
depends_on: [doc-idea-staging, doc-governance-protocol]
---

# Idea and plan lifecycle integrity requirements

This is a proposed implementation contract. This session delivers architecture and verification
criteria; it does not claim these behaviors exist. The unified lifecycle plan owns implementation.
The authoritative audit synthesis supplied for this task corrects the original brief's factual
inventory. The [transcript report](../00-working/idea-plan-architecture/transcript-analysis.md)
separates direct owner statements from brief-supplied decisions. All examples in the plan are synthetic.

## Observed problem and scope

The supplied audit snapshot reports 19 creation events and zero transitions; zero historical plan
activations; 2 of 21 plans complete and none of five plans with eight or more phases complete.
These are pre-task measurements, not a census of the expanded document set. The writer exposes
shell-sensitive prose arguments. Replay is repeated in three places; semantic history validation
is missing. Plan-phase coverage and complete-plan evidence checks already exist. Six HTML children
are covered through sources, with counts 3/3/2/3/1/2. No zero-phase repair project is warranted.

## Observable requirements and verification

| ID | Required observable behavior | Verification method | Delivery |
|---|---|---|---|
| R01 | Existing log bytes, identifiers and writer-issued timestamps remain unchanged; the known corrupted record remains evidence | Compare byte prefix against pre-change source; inspect scoped diff; no live repair/capture in this architecture session | Every phase |
| R02 | Supported prose input preserves backticks, dollar substitutions, quotes, newlines and Unicode as data | Run the real CLI in an isolated synthetic fixture with a quoted-heredoc/file input, compare decoded prose with input and assert no sentinel command executed | First fix |
| R03 | Writer, renderer, rebuild and projection tests consume one validating replay implementation and one schema transition table | Trace imports/call sites; synthetic corpus includes every existing transition/revisit branch and refusal; no production replay copied into tests | First fix |
| R04 | Duplicate creation, unknown idea, mismatched from, illegal transition and second revisit fail before append or database mutation | Negative fixtures bypass high-level writer then call replay/preflight directly; assert unchanged log/database and absent data directory on failed first rebuild | First fix |
| R05 | Every event resolves to a unique identity — a written `eid`, or a digest of a legacy line's own bytes — and an amendment names its target by that identity; direct amendments compose without reverting earlier unrelated fields | Synthetic sibling title/body corrections; nested chain; absent, forward and foreign target refusal; two events resolving to one identity fail the fold; a merge fixture interleaving two worktrees' appends leaves every pointer resolvable | Amendments |
| R06 | Flags obey replace/clear/inherit exactly; an amendment changes one record's contribution, never the accumulated collection | Exhaustive truth-table and event-field fixtures; required clears fail, optional contribution clears succeed; siblings survive | Amendments |
| R07 | Effective replay rechecks the whole corrected history, including from and revisit invariants | Correct an early transition into one inconsistent with a later from; refuse proposal before append, reject imported bad history before rebuild writes | Amendments |
| R08 | Raw history and effective current state remain separately queryable; past knowledge excludes later amendments | Synthetic cutoff before/after correction gives different known states; raw row count equals log event count, including retracted contributions | Amendments |
| R09 | Annotations carry owner or agent-name author, minimal kind and text; terminal states admit notes; assessments remain timestamped notes | Every author/kind fixture, promoted/discarded notes, text replacement/clear, status unchanged | Notes |
| R10 | Agent findings ship with collapsed rendering and complete accessible details; current prose displays final values without amendment badges | Golden render with 100 findings, owner note, corrected title; reload/refold in different processes/hash seeds; --check detects stale output | Notes/amendments |
| R11 | Triage enters triaging, writes findings through the sanctioned writer, and ends at triaged; promotion remains owner judgment | Synthetic end-to-end execution of existing triage phase; interrupted run remains observable; no automatic reviewing/promotion/discard | Existing triage phase |
| R12 | Three link types are stored once, inverses derived, contributors retained, and directional cycles flagged at fold time without rejecting capture | Reciprocal relates_to accepted; extends/supersedes cycle flagged; duplicate contributors and selective retraction tested | Relationships |
| R13 | Promotion supports one idea to several governed documents and several ideas to one; unresolved current targets fail validation, historical closures remain auditable | Code-to-document lookup fixtures for multiplicity, missing/reserved/retired codes, renamed paths and later deprecated targets; reverse lookup | Relationships |
| R14 | Plan attribution is plan OR sources, deduplicated; every plan has at least one historical phase and open plans retain noncancelled coverage | Coverage fixtures and existing six HTML child counts; zero/all-cancelled cases across every plan status | First fix/matrix |
| R15 | Work cannot begin under draft/approved affected plans; activation precedes the claim, and approval is never fabricated | Command-mode review and fixtures; draft/approved plus active/completed phases fail; first fix reconciles actual affected plans | First fix |
| R16 | All plans receive consistency reports; active/all-complete passes pending review, complete/unfinished fails, and complete with complete-or-cancelled phases warns unless completion evidence explains the cancellations | Full disjoint distribution matrix; existing evidence-path tests retained; owner-intent review separate from counts | First fix/matrix |
| R17 | Supported metrics declare population, cutoff, time axis and missing-data treatment; corrections/notes do not create new capture counts | Synthetic SQL results with known durations and denominators; skew flagged; no inferred duplication or session count reported as measured | Integrated verification |
| R18 | Architecture is one parent plus category children in the four requested folders; each category has six sections, coverage, open choices and conflicts | Document review, allocator output, catalog byte comparison and governance exit 0 | This session |

R02 promises the sanctioned input path, not recovery of prose already altered by an arbitrary caller's
shell. R05–R08 use the nested precedence recommendation in the event contract, whose decision is
visible before implementation. R16's cancelled-phase cell is decided: `complete` with a mix of
complete and cancelled phases **warns**, and the warning clears when `completion_evidence` states why
those phases were dropped. `GOV-002`'s complete-or-cancelled closure is unchanged, so this requirement
adds a check without reversing a standing policy.

## Boundaries and open questions

Tags and classification remain deferred until at least 60 captured ideas or a documented failed
retrieval, followed by a boundary decision against links. No vocabulary, registry or schema is designed
now. Mandatory idea provenance for plans is excluded: record genuine promotion and never fabricate
captures. A future proposal would need prospective evidence of lost provenance and a capture process
that adds no synthetic history; it is not an automatic evidence-triggered hard gate.

Duplication rate, ideas per session, complete machine-readable plan transition history, undoing a
revisit, moving a creation between identities and multi-record historical repair are not delivered by
the minimal model. They require explicit decisions/data. A final-state plan report does not reconstruct
past plan states, and the planned history squash makes Git an insufficient archival fallback.

The first implementation phase must deliver the four live repairs before any schema extension.
Subsequent phases remain proposals, subject to the recorded complexity review and unresolved choices.
