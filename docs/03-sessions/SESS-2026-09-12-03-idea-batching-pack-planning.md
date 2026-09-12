---
schema_version: 1
id: doc-session-idea-batching-pack-planning
code: SESS-2026-09-12-03
title: Idea-batching prompt pack — Prompt A, Prompt B, and the stage 3 adversarial gate
kind: session
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems:
- sys-governance
- sys-backlog
- sys-portfolio
depends_on:
- doc-prompt-pack-protocol
- doc-idea-record-system
---

# Idea-batching prompt pack — Prompt A, Prompt B, and the stage 3 adversarial gate

## Phase

None. This session claimed no backlog phase at any point — not one that closed partway through,
none from the start. It was a planning session under the prompt-pack protocol (`GOV-008`),
producing governed prompt documents rather than advancing a queued phase.

`phase-demo-07` (`agent-demo-glossary`) was `active` throughout and belongs to another session; it
was not touched. `phase-wb-10` was `active` at the session's start and had been released by its
close, by its own holder. `next_up` was not modified.

The handling follows `brain/procedures/session-close-with-no-active-phase.md`, which exists for
this fork in the procedure. That entry's case is a phase closing mid-session and work continuing
unclaimed; this session is the further variant where no phase was ever claimed.

## Verification

No phase means no declared `verification` list. The checks run at close were the `session-close`
mechanical gates:

```
uv run python -m src.governance --catalog > docs/08-governance/catalog.md
uv run python -m src.governance
  -> Governance OK: 19 systems, 179 documents, 19 memories, 129 backlog phases
uv run pytest
  -> 578 passed, 2 warnings in 33.37s
git status --short
  -> (clean)
```

The suite ran four times across this session. The first full run was `2 failed, 576 passed` — both
failures traced to generated output that had drifted, not to product code, and both were fixed
during the session (see `## Corrections`). The last three runs were `578 passed`.

**A green run here must not be read as the environmental PTY problem being fixed.**
`SESS-2026-09-12-01` records four consecutive full-suite runs producing 3, 3, 2 and 0 PTY failures
respectively. The failure is intermittent, so `000099` and `000129` both stand and neither is
closed by this session's green runs.

## Acceptance

No phase, therefore no `acceptance` list to evaluate. Nothing in this session reached, or could
have reached, `status: complete`.

The one gate that did apply is `GOV-008`'s own: stage 3, the adversarial review of Prompt B before
it may run. That gate was run and its findings applied — see `## Review`.

## Backlog

`docs/09-backlog/backlog.yaml` was not modified by this session. No phase was claimed, no
`status` changed, no `next_action` written, and `next_up` was left exactly as found.

The seven `phase-lit-*` entries that appeared in `backlog.yaml` during this session were committed
by a concurrent peer session (`d-system-ff`) building the literature-review research pack, in
`efba8f3`. They are queued only and are not this session's work.

## Unresolved

- **`GOV-008` stage 4 has not run.** `PROMPT-026` exists and is audited, but the pack it
  manufactures — delegation pack, adversary charter, corpus builder, kick-off record — does not.
  The owner has chosen to execute it in a fresh session rather than this one, deliberately, so
  `PROMPT-026` is exercised as the standalone artifact it claims to be.
- **The demo fast lane has not started.** It is the deadline-bound half (demo week of 2026-09-15)
  and it produces the exclusion file `PROMPT-026`'s corpus builder reads.
- **The descope ladder's placement of audit 2 is unratified.** `PROMPT-025` decision 16 orders the
  ladder, but the merge re-audit was added by decision 7 *after* that ladder was ratified. Its
  position — first thing spent after the replicates — is recorded in the document as the drafter's
  proposal, explicitly flagged for the owner to reorder.
- **`dev` is 9 commits ahead of `origin` and unpushed.** Six are this session's, three are the
  peer's. Pushing needs no approval; it simply has not happened.

## Review

`GOV-008` stage 3 requires an adversarial audit of Prompt B against Prompt A and repository
reality before Prompt B runs. That audit was dispatched as an independent, non-fork agent and
returned four confirmed and three plausible findings. Its findings, as reported:

**CONFIRMED 1 — the stop condition never verifies what the pack requires pytest to check.**
`PROMPT-026` hedged that the corpus builder should have an OPS document "if the per-tool
documentation pattern requires one — check before assuming either way." The answer is
unconditional: `test/test_tool_docs.py::test_every_existing_tool_is_paired_with_a_document`
asserts every tool under `tools/` has a paired `OPS-*` document with no exception, and
`test_every_paired_document_matches_regenerated_output` gates its content. The stop condition
required only governance exit 0 and a synced catalog, so an agent could satisfy every named check
and leave the suite red.

**CONFIRMED 2 — "the triage finding" is not a well-defined field.** `fold()` returns `annotations`
as a flat, unfiltered list mixing `note`, `finding` and `assessment` kinds from any author. Eight
triaged ideas carry more than one `finding`-kind annotation, and seven findings were written by
authors other than `agent-idea-triage` — including `agent-demo-factory`,
`agent-workbench-planner`, `agent-coordinator`, `agent-workbench-coordinator`,
`agent-readme-audit`, and the owner directly. The corpus builder could not be written from
`PROMPT-026` alone without inventing a selection rule the owner never ratified.

**CONFIRMED 3 — the section-letter scheme inverted the convention it claimed to follow.**
`PROMPT-018` and `PROMPT-021` fix `C*`/`V*` as creator/validator pairs and `A` as the adversarial
review. `PROMPT-026` had assigned `A1`–`A4` to the four analysts and `V1`/`V2` to the two adversary
audits — both letters carrying the opposite role from the shape the document said it was adapting.

**CONFIRMED 4 — `GOV-006`'s idea-citation form was violated for `000145`.** Named without its
parenthetical gloss.

**PLAUSIBLE 5 — `GOV-008` stage 4's plan-mode requirement was not carried into the prompt block.**
On verification this is confirmed, not plausible: executing `PROMPT-026` *is* stage 4, and the
protocol states "first in plan mode; auto execution only after the owner confirms the plan."
`PROMPT-026`'s prompt block went straight from reading to producing.

**PLAUSIBLE 6 — the control does not cleanly isolate framing bias.** `R4` differs from `R1` in one
variable, which is a sound design, but any divergence is equally explained by "`R4` had less
information and produced a weaker partition" as by "`R1`–`R3` inherited the triage charter's
framing." The audit-1 brief asserted that a 3–1 split with the control dissenting is the expected
shape of finding bias, without requiring the competing explanation to be weighed — so audit 1
could rubber-stamp any such split as validated by design.

**PLAUSIBLE 7 — presentation-order-as-anchoring-control is asserted, not established.** Real
dispatch budget is spent on an effect that is plausible but unverified for these agents, with no
specified handling for the case where all three finding-readers converge regardless of order.

**What the audit reported as holding up:** it attacked decision-by-decision fidelity hardest, and
found all sixteen of `PROMPT-025`'s ratified decisions mapped onto `PROMPT-026` without
contradiction or paraphrase drift — including the batch-record fields, the two-level partition, the
decline-tier stratification, the gate schedule, the stages 6/7 collapse, the exclusion-list
disposition semantics, and the descope ladder with its owner-versus-drafter caveat preserved. Every
command named in the preflight exists and behaves as described.

**Disposition.** All seven findings were verified against the repository before being acted on, and
all seven were applied in `267eb80`. Two of the audit's own numbers were corrected in the process:
it reported nine ideas carrying multiple findings where the real count is eight, and it filed
finding 5 as plausible where it is confirmed.

**Scope limit of this review, stated plainly.** This audit covered `PROMPT-026` against
`PROMPT-025`. No independent agent reviewed `PROMPT-025` itself, the `ask-through-the-tool`
procedure, or the session's commits as a whole. `GOV-008` stage 5 — the audit of the finished pack
— has not run, because the pack does not exist yet.

## Decisions

**The pack drives the analysis, not the plans it produces.** The owner chose to manufacture a
`GOV-008` pack whose build *is* the batching analysis — agent dispatches over a text corpus,
producing an ungoverned staging document — rather than treating the batching as ordinary session
work and reserving packs for the plans it eventually yields.

**The demo work leaves by a separate lane.** Demo-blocking and demo-improving ideas are cut and
handed to the build already in flight, outside the pack entirely. The pack yields to the fast lane
if the two compete, which is intended behaviour rather than a descope. The owner ruled the
governance atlas page (`000093`) out of the demo, and framed the audience as novice practitioners
with skills and agents as the subject.

**Four analysts, after a reversal.** The design went four lenses → two complete partitions → four
complete partitions. The middle step was not wasted: it produced the insight that survived. Two
agents could not be four *lenses* without leaving the corpus uncovered, which forced each into
producing a complete partition — and once they were replicates, asymmetric input became the natural
bias control. Returning to four kept the replication instrument rather than reverting to the
original lens design. The owner closed the reversal explicitly ("settled, no more changing").

**Three read findings, one does not.** `R4` is the control. The drafter added, and the owner
ratified, that the three finding-readers receive different presentation orders — ascending,
descending, shuffled under a recorded seed — because three agents given identical input would
reproduce any anchoring effect identically, and three identical artifacts read as consensus.

**The partition is two-level.** The owner's criterion and a batch-count target pull against each
other: if the corpus holds twenty independent groups, a hard target of 8–12 forces merging what the
criterion says to split. Splitting the output into a fine partition rolled up into 8–12 programmes
separates what is genuinely independent from what the owner wants to read. It also resolved, without
a separate decision, what happens when the demo fast lane shrinks the corpus.

**An agent integrates; the owner rules; the adversary audits both sides.** The owner extended the
adversary to re-audit the merge, taking the build from five dispatches to six. Synthesis was
otherwise the only step in the design that nothing checked.

**A light artifact set, overriding `GOV-008` stage 4's default.** No requirement, no plan, no
backlog phase, no decision record — only the delegation pack, adversary charter, corpus builder and
kick-off record. Stage 4's machinery governs code builds; this build writes none.

**Stages 6 and 7 collapse into the kick-off record.** The owner's reasoning when ratifying it — that
this may be a class of work not meriting a prompt pack at all — was captured as `000145`
(alternative planning methodologies below a full prompt pack) rather than acted on here.

**`R4` is not told it is a control.** A drafter's call, flagged as such: an analyst that knows it is
a control would reason about what it is missing rather than doing the job.

**Merge handling under concurrency.** The owner approved merging, then the merge was blocked by a
peer's uncommitted changes to the generated catalog — precisely what `AGENTS.md` step 6 forbids
forcing. The owner chose to message the peer rather than force or wait. When the peer's commit
landed on this branch rather than `dev`, the owner approved integrating both together, because the
peer's proposed alternative — cherry-picking their commit to `dev` alone — would have put a catalog
on `dev` naming two documents not yet there, turning it red.

**A standing rule, carved at the owner's instruction.** Any question the agent wants answered goes
through `AskUserQuestion`, never prose, at any point in a session. Recorded both in this model's
memory and in `brain/procedures/ask-through-the-tool.md`, model-agnostic, so it reaches whichever
model works here next.

## Corrections

**`catalog.md` was stale and would have turned CI red.** Caught while preparing the walkthrough of
`PROMPT-025`. It is generated output and CI fails on any difference; `PROMPT-025` had been written
without regenerating it. Fixed before the first commit.

**`ideas.md` was not regenerated when `000145` was appended, leaving `dev` red.** Commit `994abac`
added the idea without its projection, breaking
`test_ideas.py::test_the_committed_markdown_matches_regenerated_output`. This was a self-inflicted
red trunk that went unnoticed until the suite was run for an unrelated reason. Fixed on `dev` in
`ed7d0d2`.

**`PROMPT-025` decision 5 asserted something false.** It claimed every triaged idea carries a
finding written by one agent charter. The stage 3 audit established that seven findings come from
other authors, including the owner's own, and eight ideas carry more than one. The decision was
corrected and the owner ratified the selection rule that replaced the assumption.

**Predicted document codes were removed from `PROMPT-026`.** It had named `PROMPT-027` and
`PROMPT-028` as the expected codes for the delegation pack and kick-off record. A peer took both
mid-draft. The codes are gone and the collision is written into the document as the argument for
reading `--next-code` at creation rather than at drafting.

**A caution to the peer was unfounded.** They were advised to re-check `PLAN-023` against a live
allocation on the grounds that codes move under concurrency. Their factory already allocates at
file-creation time — the same discipline this session adopted after being bitten. The concern was
reasonable but did not apply, and they said so.

**An overstated claim about the PTY failures.** During the session the owner was told that
`000099`'s red-trunk claim was "now doubtful" because the suite passed here. That was too strong.
`SESS-2026-09-12-01` records four consecutive runs producing 3, 3, 2 and 0 PTY failures — the
failure is intermittent, and a green run is not evidence of a fix. `000099` and `000129` both
stand.

## Left undone

**`GOV-008` stage 4 — executing `PROMPT-026`.** Deliberately left for a fresh session. `PROMPT-026`
is written to be pasted cold; running it in the session that authored it would mask any gap in it,
and a document that only works when its author runs it is not a working document. Better to find
that at stage 4 than with six dispatches running off it.

**The demo fast lane.** The deadline-bound half, untouched. It needs the `000099` red-trunk claim
verified first — carefully, given the intermittency noted above — then a demo cut drafted for the
owner to ratify, then the exclusion file produced. Until that file exists, the corpus builder
treats it as an empty set, which is why the two workstreams remain genuinely independent.

**The descope ladder's audit-2 placement.** Awaiting the owner's ruling. It is flagged inside
`PROMPT-025` decision 16 rather than held in conversation, so it survives this session.

**`dev` unpushed**, 9 commits ahead of `origin`. No approval needed; simply not done.

**`GOV-008` stage 5**, the audit of the finished pack, cannot run until the pack exists.
