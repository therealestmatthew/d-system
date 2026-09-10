---
schema_version: 1
id: doc-backlog-decisions
code: GOV-003
title: Accepted choices for phased backlog delivery
kind: governance
status: active
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-10'
systems: [sys-backlog, sys-projection, sys-html, sys-memory-agents]
depends_on: [doc-governance-protocol]
---

# Accepted choices for phased backlog delivery

Authority: the user's [saved questionnaire answers](../00-working/codex-answers.md), plus the subsequent instruction: “All of the above for the ones I left more than one answer - you figure out the right blend from there.” The raw answers are preserved without editing. This record translates those choices into actionable constraints; it does not mark any feature implemented.

| Question | Accepted choice | Backlog coverage |
|---|---|---|
| Delivery scope | Capture all remaining plans, then deliver them in session-sized phases | Every phase; current turn creates the tracker and captures scope only |
| Project/person membership | `project.stakeholders` is authoritative; derive person membership | `phase-rel-04` |
| Global memory retrieval | Include `scope: global` alongside project memories, including `project: d-system` | `phase-rel-08`, `phase-mem-07` |
| Page data authority | Commit authored YAML; generate ignored JSON during builds | `phase-html-01`, `phase-html-02`, `phase-html-09` |
| Runtime block validation | Validate every block type against a shared runtime contract | `phase-html-01`, `phase-html-03`, `phase-html-04` |
| Memory writers | Keep direct human and authorized-agent edits with validation | `phase-mem-01`, `phase-mem-02`, `phase-mem-06` |
| Chronicle trigger | Manual invocation for an explicitly selected session | `phase-mem-03`; periodic review never silently changes this |
| Embeddings | Defer until measured keyword/tag retrieval is insufficient | `phase-mem-10`, deferred `phase-mem-15` through `phase-mem-18` |
| Retrieval hints | Blend all three approaches as described below | `phase-mem-08`, `phase-mem-09` |
| Conflicts and memory promotion | Agents propose; owner resolves conflicts and approves promotion | `phase-mem-05`, `phase-mem-06` |

## Blended hint design

Infer useful defaults from memory type. Keep explicit hint IDs in the existing tag registry so there is one vocabulary. Add an optional `retrieval_hints` field for routing-specific additions that do not belong among ordinary classification tags. Combine inferred defaults and explicit hints as a deduplicated set. Existing memories need no metadata change to obtain inferred defaults. Registered explicit hints remain available where ordinary tags already carry the intended meaning.

The hint contract phase will define schema/category details and compatibility examples before changing DDL, ingestion or retrieval. There is no unresolved selection between the three approaches.

## Delegated implementation choices

Use Chronicle as the working role name from the existing proposal. Choose the failure-safe projection mechanism through a small experiment and ADR. Define snapshot ownership before writing observations. Use model-independent, manually invoked synthesis prompts and deterministic data collection for the first portfolio workflows, fitting the repository's current model-agnostic operation without inventing a provider commitment.

For `--all`, implement all matches by default while honoring an explicitly supplied limit. Keep the ordinary query default bounded. These are concrete interpretations of the existing functionality and scope, recorded so they are reviewable.

## Concurrency collisions

This record is also the ledger for collisions between concurrent agents. Most merge conflicts need no
entry: two agents editing different items of `backlog.yaml` is mechanical, and the resolution is
always to keep both sides. Record an entry when resolving a collision required an actual choice —
which phase yielded, whether a system boundary moved, whether a phase was split or its declared
`systems`/`deliverables` were widened, or which of two incompatible implementations was kept.

| Date | Phases | Collision | Resolution |
|---|---|---|---|
| 2026-09-06 | `phase-cap-01`, `phase-priv-01` | Both claimed ADR-007. PLAN-006 stated in prose that ADR-007 was allocated to the structure/content boundary, but never reserved it in `codes.yaml`, so `--next-code` issued it to the capture routing decision | The merged document keeps the code, per the rule that the second to integrate renumbers. The boundary ADR became ADR-009; `phase-priv-01`'s deliverable path and PLAN-006's prose were corrected to match. Root cause was the reservation step being skipped, not the allocator |

Append rows in the same diff as the resolution; a commit message is not a governed record. A conflict
under `src/`, `ts/`, `schemas/` or `sql/` between phases declared disjoint always warrants an entry,
because it means the declarations the concurrency check relies on were wrong. [ADR-003](../04-decisions/ADR-003-multi-agent-concurrency.md)
states the rules; this table states what was actually decided when they were tested.

## Choices made after the capture definition session

The capture definition session (`phase-cap-01`,
[SESS-2026-09-06-01](../03-sessions/SESS-2026-09-06-01-capture-definition.md)) produced two ordering
choices that change existing phases. Both were the owner's decision, not an agent's.

**The signal track now depends on capture.** Nine `phase-sig-*` and five `phase-syn-*` phases were
written against commitment, task and interaction data that has never existed. Rather than annotate
all fourteen, the dependency was added at the four earliest points in each chain, and the rest
inherit it transitively:

| Phase | Added dependency | Why |
|---|---|---|
| `phase-sig-02` Stale Radar | `phase-cap-07` | Needs `review_cadence` and derived `last_touched`; its six thresholds changed when `ongoing` was retired |
| `phase-sig-03` Accountability Ledger | `phase-cap-08` | Joins commitments to people; neither exists until capture seeds them |
| `phase-sig-05` Cognitive Load Estimator | `phase-cap-07` | Reads open commitments and tasks in their final shape, including unfiled ones |
| `phase-sig-06` Commitment Velocity | `phase-cap-08` | Counts commitments closing over time; requires real rows, then accumulation |

`phase-sig-01` (view installation boundary) and `phase-sig-09` (tag clusters) were deliberately left
alone: the first needs no data and the second reads projects and tags, which are already populated.

**A solo agent on a documentation-only phase works in the primary checkout.** `AGENTS.md` says never
to work in the primary checkout, and both phases of 2026-09-06 did exactly that, with the owner's
approval. The reasoning: the worktree rule exists so that tests, rebuilds and dev servers cannot
corrupt a peer's run, and with no peer claim and no deliverable outside `docs/`, there is nothing to
isolate — a Markdown edit cannot corrupt a run that is not happening, and a second virtualenv buys
nothing. A worktree remains required whenever a peer holds an active claim or the phase touches
`src/`, `ts/`, `schemas/`, `sql/`, `tools/` or `test/`.

`phase-ses-03` already owned repairing the hand-off section, whose worktree and rebase steps assume a
remote that does not exist. Its scope was widened in the same diff to replace the blanket prohibition
in the *worktree* section of `AGENTS.md`, `GOV-001` and `GOV-002` with the conditions above, rather
than leaving the same root cause split across two phases. Until it runs, practice and protocol
diverge; this entry is what keeps that visible.

**Resolved 2026-09-07.** `phase-ses-03` replaced the blanket prohibition in the worktree section of
`AGENTS.md`, `GOV-001` and `GOV-002` with the conditions stated above. Practice and protocol now
agree; this entry stays as the record of why the exception exists.

**Promoted records keep a source reference and the list of assumed fields.** Full per-field evidence
scoring lives on the staged record and does not travel into `_data/`. A promoted record carries a
pointer to its raw capture plus the names of the fields that were non-explicit at promotion time.
The reasoning: keeping every field's evidence level forever roughly doubles the field count on every
entity, while keeping nothing means a bulk-approved record has no memory of what was assumed and a
systematic misreading could never be found afterwards. `phase-cap-02` implements this shape.

**`phase-cap-02` owns the source data and the instructions that name the renamed field.** The phase
was declared as schemas and tests only, but renaming `project.commitment_cadence` to `review_cadence`
invalidates all 33 files in `_data/projects/`, and no phase declared that directory. `phase-cap-07`
owns the loader and `phase-cap-08` owns the owner's cadence reassignments; neither owns the mechanical
key rename. Leaving it undone would have left the portfolio failing the contract it is validated
against, and `phase-rel-02` — the next item in the queue, whose acceptance requires valid current
source files to pass — would have tripped on all 33 immediately.

The same reasoning extends to `README.md`, `brain/procedures/add-new-project.md` and `PROMPT-001`,
which instructed a reader or an agent to write the old field name, PROMPT-001 offering the retired
`ongoing` value as a valid choice. `SESS-2026-09-06-02` had already assigned the README correction to
`phase-cap-02`. Historical records — ADR-008, PLAN-009, PROMPT-002 and the session logs — keep the old
name, because they describe what was true when they were written.

Both widenings were committed to `backlog.yaml` on `main` before the work, so the wider lock was
visible first. The owner chose this over filing a separate migration phase; the alternative would
have split one rename across two sessions with the data invalid in between. The owner also supplied
the three replacement cadence values in the same session, which satisfies `phase-cap-08`'s cadence
scope item ahead of that phase.

**Contracts precede the source preflight.** `phase-rel-02` builds a preflight validating every source
shape against the existing schemas, and `phase-cap-02` rewrites those schemas. `phase-cap-02` was
moved to the front of `next_up` so the preflight is written once, against final shapes, rather than
written and then extended in the following phase.

**`waiting_on.owed_by` stays unprotected.** It is the structural mirror of `commitment.promised_to`,
which ADR-007 protects, and the surface argument — an agent should not decide who owes the owner
something — reads the same. The owner chose not to widen the protected set anyway. The stakes are
not symmetric: `promised_to` guards the owner's first priority, zero *broken promises*, where a
wrong name means a promise made to nobody. An inbound item is the second priority, and `waiting_on`
is already a medium-stakes type, so under ADR-007's routing table every one of these records reaches
flagged review regardless of evidence level. The protected-field rule would add a second flag on a
record the owner is going to read anyway. ADR-007's set stays at four things.

**`tools/` joins the documented lint gate.** `ruff check src/ test/` is the gate AGENTS.md and OPS-001
name, so `tools/rebuild_db.py` and `tools/load_context.py` have never been covered by it —
`tools/load_context.py` currently fails `ruff check tools/` on a pre-existing F541. These are the
loader and the retrieval CLI, not scratch scripts, and the projection depends on them. `phase-rel-09`
already owned resolving the script lint issues and pulling this tooling into CI; its scope now also
covers updating the documented command in `AGENTS.md` and `OPS-001`, so the gate agents run by hand
matches the gate CI runs. No separate phase was filed for something an existing phase already owns.

**Contract tests and the source preflight must agree about dates.** `test/test_schemas.py` validates
without a format checker and `src/db/source_validation.py` validates with one, so `2026-13-45` passes
the contract tests and fails the rebuild. Nothing is broken today, but every schema phase that adds a
date field widens the gap — `phase-cap-03` adds a capture timestamp next. Filed as `phase-rel-11`
rather than fixed in passing, because it changes a completed phase's deliverable. It is placed ahead
of `phase-cap-07` in `next_up` for that reason.

## Session close splits into a skill and a command

**`phase-ses-03` no longer depends on `phase-ses-01`.** The closing work was queued behind the
session-type taxonomy, but nothing in a close varies by session type and `PLAN-008` describes it as
"a single closing procedure". The dependency was plan ordering rather than a real prerequisite, so it
was dropped and the phase moved to the front of `next_up`. If a later session type turns out to need
a different close, the dependency can be reintroduced deliberately.

**One phase became two, because invocation rights differ.** `phase-ses-03` now builds `checkpoint` as
a **skill** — invocable by the owner *or* the agent, safe to run repeatedly, and never claiming a
completion that is not there. `phase-ses-05` builds `session-close` as a **command**, reachable only
by the owner, adding third-party sub-agent review and the depth worth doing once.

The split is not about size. **An agent must never decide that a session is over.** Checkpointing
records and concludes nothing, so an agent noticing that much has happened should just run it;
declaring the work done is a judgement that belongs to the owner. A command cannot be reached by an
agent deciding on its own that it has finished, and that is the property being bought.

Both write **the same session record** — the checkpoint creates it and updates it, the close
finalises it — so a session has one output product rather than a trail of partial ones, and the close
never starts from a blank page. `checkpoint` must be referenced from `CLAUDE.md` and `AGENTS.md`, or
the agent-invoked half never happens: an agent unaware of the skill will not choose to run it.

`phase-ses-04` (dogfooding) now depends on both.

## History is squashed, not filtered

`phase-priv-05` offered two routes: squash to a single commit, or keep history and scrub it with
`git-filter-repo`. **The squash is now the decision, and the fallback is withdrawn.**

The argument is about what is provable rather than what is tidy. The phase has to establish that *no
commit anywhere* names a confidential identifier, and real portfolio records sit in `_data/` across
nearly the whole history. Filtering makes that a check which must hold across every commit, with a
failure mode that is silent — `git-filter-repo` reports success while leaving a blob reachable from a
tag or the reflog. A single tree is provable by inspection. Since a missed identifier that reaches a
remote is unrecoverable, the provable option wins over the merely careful one.

Little is given up. This repository records its own evolution in ADRs, this document, session records
and backlog phases carrying `result` and `completion_evidence` — git history is a derivative and
poorer copy of a narrative the governed documents already hold deliberately. At the time of the
decision it was 91 commits over two days by a single author, and the only deleted files were three
manufactured plans that [ADR-010](../04-decisions/ADR-010-idea-staging.md) already cites as a
cautionary example, plus a one-time migration tool whose work is described in `PLAN-016`.

**Two consequences travel with this.** Nothing can be "kept in history" — preserving something means
keeping it in the tree, and `PLAN-016` was corrected where it claimed otherwise. And no tracked
document may cite a commit hash, because none will resolve afterwards; four such references were
swept when the decision was made, and `phase-priv-05` now carries the sweep and an acceptance
condition against their return.

## Root plans/ is retired

**GOV-001's link-compatibility exception for PLAN-001 is withdrawn.** GOV-001-protocol.md previously
stated `plans/PLAN-001-agent-memory-system.md` "remains at its existing path for link compatibility,"
the one file the original `docs/01-plans/` migration (PLAN-005) chose not to move. `plans/` also held
`codex_governance_prompt.md`, the ungoverned bootstrap prompt, exempted by name rather than moved.

The owner judged the two-location split not worth preserving, on 2026-09-08. `PLAN-001` moved to
`docs/01-plans/PLAN-001-agent-memory-system.md` with its `id`/`code` unchanged; `codex_governance_prompt.md`
moved to `docs/02-prompts/`, keeping its ungoverned, exempt status rather than becoming a coded
`PROMPT-*` document. `plans/` was dropped from `codes.yaml`'s `PLAN` locations and from the
governance discovery loop, not merely emptied of files — the same cost ADR-006 already paid once for
the original code-system migration. See [PLAN-018](../01-plans/PLAN-018-plans-directory-consolidation.md)
and [REQ-004](../06-requirements/REQ-004-plans-directory-consolidation.md), delivered by `phase-plc-01`.

## The demo track completes through its testing gate, not through /session-close

Owner decision, 2026-09-10, for the five `phase-demo-*` phases only. The backlog validator rejects
an active phase whose prerequisite is not `status: complete`, and the demo build (PROMPT-014)
cannot pause for an owner-run `/session-close` at every phase boundary on demo day. The owner
substituted the completion authority for this track: a demo phase is marked `complete` by the
build coordinator once its gate has passed — every verification command green with output
captured, the phase's adversarial review (`demo-adversary`) with findings fixed or explicitly
reported, and, for phases with a browser-facing deliverable, the Playwright-driven web checks
(`demo-validator-web`) — and the branch is integrated onto `dev` with the owner's approval. The
completion edit is one small commit on `dev` immediately after that integration.

What is bought and what is conceded. The section above this one records why an agent must never
decide a session is over; this decision consciously narrows that rule for one track, trading the
owner's synchronous judgment for an adversarial gate plus **retroactive** owner review — the owner
reads the session records and may run `/session-close` afterwards as an audit of phases already
complete. The integration ask is unchanged: merging onto `dev` still requires the owner each time,
so a human remains in the loop at every boundary; what moved is only which authority flips the
status field. Everywhere outside `phase-demo-*`, `/session-close` remains the only path to
`status: complete`, and the checkpoint skill's never-complete rule stands unmodified (its text is
currently a `phase-port-01` deliverable and was deliberately not edited for this exception).

## phase-demo-06 inserted ahead of the rehearsal phase

Owner decision, 2026-09-10, after testing the integrated stage (phases 01–04): the stage terminal
interaction upgrade (`phase-demo-06` — session tabs that survive collapse, a confirmation-guarded
drop control, in-page command injection from a data file, resize wiring; REQ-006 rows R10–R12)
folds into the demo track ahead of the rehearsals rather than waiting for a post-demo phase.
`phase-demo-05` was returned to `queued` — its claim released with zero commits on its branch,
its worktree kept — and gained `phase-demo-06` as a dependency so the runbook and rehearsals
describe the final UI. The demo-track completion decision above extends to `phase-demo-06` on the
same terms ("five phases" reads as the track's phases). A backend inject/read API for driving the
terminal from outside the page was considered and parked as an idea: per ADR-013's closing
consequence, that capability starts from its own decision record.

## The demo-track completion gate extends to the workbench track

Owner decision, 2026-09-10, ratified through the workbench pre-plan package (`PROMPT-020`, item
5 of its production list). The completion-authority substitution recorded above for
`phase-demo-*` extends on identical terms to the seven `phase-wb-*` phases of the workbench
build ([PLAN-022](../01-plans/PLAN-022-workbench.md)): a workbench phase is marked
`status: complete` by the build coordinator (`PROMPT-022`) once its gate has passed — every
verification command green with output captured, the phase's adversarial review
(`demo-adversary`, pack `WNN-A`) with findings fixed or explicitly reported, and, for phases
with a browser-facing deliverable, the Playwright-driven checks (`demo-validator-web`, pack
`WNN-W`) — and the branch is integrated onto `dev` with the owner's approval. The completion
edit is one small commit on `dev` immediately after that integration.

The same trade and the same limits apply: the owner's synchronous judgment is substituted by
the adversarial gate plus retroactive review, integration onto `dev` still requires the owner
each time, and everywhere outside `phase-demo-*` and `phase-wb-*`, `/session-close` remains the
only path to `status: complete`. One addition specific to this track: `phase-wb-07`'s
owner-machine conditions — the REQ-006 R06 Windows smoke check, the REQ-007 W12 Windows shell
round-trips, and the owner-driven R09 timing — close only on the owner's recorded results; the
coordinator may not mark that phase complete on agent evidence alone.

Semantic provider, private/cloud data boundary, storage and quality targets belong to deferred `phase-mem-15`. No provider was selected or memory transmission authorized by the questionnaire. Agentic refinement additionally requires evidence that the simpler retrieval stages leave useful work unresolved. The optional periodic memory-review phase packages an opt-in trigger; it does not activate a scheduler or automate approval/deletion.

These are tracked gates with resume conditions, not missing backlog coverage. All feature plans remain open until their mapped phases are completed or explicitly cancelled with rationale.
