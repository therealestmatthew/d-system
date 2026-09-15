---
schema_version: 1
id: doc-session-agent-engineering-delegation-plan
code: SESS-2026-09-15-05
title: Finalize the agent engineering and delegation plan (P4)
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-delivery, sys-governance]
depends_on: [doc-agent-engineering-delegation]
---

# Finalize the agent engineering and delegation plan (P4)

## Phase

`phase-prog-06` — Finalize the agent engineering and delegation plan (P4).

Fourth phase of the unattended overnight batch run by `agent-night`. The largest programme in the
partition, and the one whose finalize phase requires a scoping pass before any count is committed.

## Verification

`uv run python -m src.governance`

```
Governance OK: 27 systems, 235 documents, 25 memories, 222 backlog phases
```

Exit 0. Documents 233 → 235: `REQ-016`, and this record. Phases 209 → 222 for the thirteen
`phase-agx-*` phases. An earlier run during the session reported `234 documents`, correctly — this
record did not exist yet. The final figure is the one recorded here.

`uv run python -m src.governance --ready`

```
| phase-agx-01 | Document the truncation cap and make truncation detectable | — | 1 | ready | — | phase-prog-06 |
| phase-agx-02 | Audit every command, skill and agent, and rule on the Claude Code dependency | — | 1 | ready | — | phase-prog-06 |
| phase-agx-03 | Build the anti-pattern store with recurrence detection, populated from what exists | — | 2 | ready | — | phase-prog-06 |
| phase-agx-13 | Independent transcript review against the participant's record | — | 3 | ready | — | phase-prog-06 |
```

Four of thirteen are `ready` — exactly the four declaring `depends_on: []`. The other nine wait on
prerequisites, six of them on `phase-agx-02`, which the plan names as the bottleneck.

`uv run pytest`

```
580 passed, 2 warnings
```

### The two repository checks the acceptance requires, run before any sizing

**`G18`'s capture half — delivered.**

```
$ ls .claude/skills/log-anti-patterns/
SKILL.md
```

Read in full. It is a complete workflow: it takes an anti-pattern someone has described, decides
which record should hold it, and writes the ones the owner confirms. It carries its own rules against
editing `AGENTS.md` and against writing without confirmation. `000097`'s owner ruling had already
rescoped it to derivation; this is why. **What remains is recurrence detection and derivation, not
capture.**

**`G22`'s substance — the lesson exists, the convention does not.**

```
$ ls brain/procedures/ | grep runtime
runtime-behavior-needs-runtime-evidence.md
```

Read in full. `confidence: high`, created 2026-09-11, and it carries the rule verbatim: any work item
whose requirement is runtime behaviour must have a live check in its loop, and an agent asked to fix
runtime behaviour must receive recorded measurements rather than verify by assumption. It documents
`phase-wb-09`: a page that rendered nothing in dev and production builds alike, invisible to build,
pytest and the mechanical gate because the bug was runtime-only, caught first by the only check that
opened a browser; and two fix cycles burned patching from a React batching assumption instead of a
websocket-lifecycle measurement.

**So `G22` is not a phase.** The knowledge is recorded; what is missing is the pack-authoring
convention that makes a work item carry its instrument by construction. That is a section of `G19`'s
methodology, and `phase-agx-05` carries it.

## Acceptance

- **`PLAN-031` carries no placeholder banner and states a chosen design.** Met. Banner removed,
  `status` `draft` → `active`, five numbered design decisions plus a scoping pass with five numbered
  rulings, each naming what was cut and why.
- **The `000072`-to-`000046` duplication is ruled on explicitly.** Met. Scoping-pass ruling 1: the
  planner bullet is struck, `phase-idg-12` in `P1` is the planner, and `REQ-016` `R17` makes it a
  checkable condition rather than a note — a roster reinstating the role fails the row. The reason is
  stated rather than asserted: `P1`'s version has a quality standard to draft against and a defined
  location to draft into, neither of which the bullet has.
- **`G18`'s delivered capture half and `G22`'s possible existing procedure are both verified in the
  repository before either is sized.** Met, and done first. Both files were read in full, not listed;
  the evidence is in `## Verification` above. Both findings changed the sizing — `G18` lost its
  capture phase and `G22` lost its phase entirely.
- **`phase-prog-06` is removed from `next_up` in the same change that completes it.** Met, in the
  same commit that registers the track.

## Backlog

`phase-prog-06` is `status: complete`, `agent: agent-night`,
`session: doc-session-agent-engineering-delegation-plan`. Completion evidence is `PLAN-031`,
`REQ-016`, `docs/09-backlog/README.md` and this record. Written under the owner's advance authority
for this batch, after the read-only independent review below confirmed all four conditions.

Thirteen phases added under `phase-agx-*`, all `status: queued`, none claimed.

## Review

A fresh non-fork sub-agent with read-only tools reviewed `dev...agent/phase-prog-06`. Its own runs:

```
$ uv run python -m src.governance
Governance OK: 27 systems, 235 documents, 25 memories, 222 backlog phases
EXIT=0

$ uv run pytest -q
580 passed, 2 warnings
```

**Condition 1 — no placeholder banner, states a chosen design — Met.** "`dev`'s copy opens with
`> **Placeholder. Not a finalized plan.**`; the branch copy has no such banner, `status: draft` →
`active`… and a 'The chosen design' section with five numbered decisions plus a five-ruling scoping
pass."

**Condition 2 — the `000072`-to-`000046` duplication ruled on — Met, and independently verified.**
The reviewer read the ideas through `fold()` rather than taking the claim: "`000072` does contain the
planner bullet ('A **planner** that turns a triaged idea into a requirement, plan and phases');
`000046` is the separately-filed idea-planner-agent idea. `phase-idg-12` … exists in
`backlog.yaml:9426`, depends on `phase-idg-10` … and `phase-idg-11` … — exactly the 'quality standard
to draft against and a defined location to draft into' the plan claims, and this text predates the
branch." It also confirmed `R17` exists, is cited by `phase-agx-10`, and that no roster role is a
planner under another name.

**Condition 3 — `G18`'s capture half and `G22`'s procedure verified in the repository before sizing —
Met.** "`.claude/skills/log-anti-patterns/SKILL.md` exists (10.5KB) and is a real, complete
routing/capture workflow… the plan's characterization holds.
`brain/procedures/runtime-behavior-needs-runtime-evidence.md` exists at `confidence: high`, documents
the `phase-wb-09` incident verbatim as claimed, and does *not* contain a pack-authoring convention —
also as claimed. Sizing genuinely follows."

**Condition 4 — removed from `next_up` in the same change — Met, verified by `git show`.** It also
noted correctly that the phase was still `active` at review time, "correct, since marking a phase
complete is owner-only."

**Integrity and coverage.** All 20 rows cited in exactly the phases claimed, checked against the
backlog rather than the plan's table; all thirteen phases carry acceptance, verification and
`session_budget: 1`; all 19 ideas accounted for, read through `fold()` and cross-checked against the
partition's `P4` table; `backlog.yaml` parses at 222 items with no anchors, and "diffed every
pre-existing phase's parsed dict between `dev` and the branch — zero changed, zero removed."

**One major finding, and it was a real error of mine.**

> "the plan's own 'Sizing against the partition' arithmetic doesn't match its own implementation
> table… the implementation table directly above tags only **two** phases with `G14`… Both `000080`
> (sensors) and `000081` (context pipelines) were folded out of standalone phases, not just one — the
> scoping-pass narrative undercounts its own cut by one."

Correct. `G14` is two phases, not three, and the pass therefore cut six phases, not five. **Fixed** in
`PLAN-031` and in this record: the headline, the scoping-pass heading, ruling 5, the sizing paragraph
and the `G14` figure all now read two and six. The reviewer's own diagnosis — that both thin concerns
were folded, not one — is what makes the corrected number six rather than five.

**Two minor findings, both fixed.**

- *The session record's pasted governance output was stale* — `234 documents` against an actual 235,
  because the record was not yet in the catalog when the command ran. Corrected, with the reason
  stated.
- *`phase-agx-02`'s remit is large for one session* — roughly 37 files under `.claude/` on four
  dimensions each, plus the `000069` ruling, while also being the bottleneck six phases wait on.
  **Not resized**, because the plan is explicit that the bottleneck is deliberate; instead its
  `next_action` now tells whoever claims it to judge at claim time whether to split the audit from the
  ruling.

## Decisions

**The scoping pass cut six phases, and each cut is a ruling rather than a deferral.** The planner
bullet struck (ruling 1); `000013` folded into the audit, since the partition already observes that
`000126`'s missing-and-needed output *is* `000013`'s question; `000069` folded into the audit, because
the question is about `.claude/` and the audit is the work that reads every file in `.claude/`;
`000136` folded into `G19`, because a convention for authoring dispatches belongs in the document
governing authoring dispatches; and two of `G14`'s four sub-topic phases removed, since `000080` and
`000081` both became boundary sections of `phase-agx-09` rather than phases.

**The framework is derived from evidence rather than written before it, which is the most consequential
ruling here.** `G14` is `P4`'s headline group and the obvious thing to schedule first. It runs late
instead — `phase-agx-08` and `-09` both depend on the audit. `000078`'s premise is that agent
construction has recurring concerns worth naming once, and the naming is only worth something if it
comes from what actually recurred. Writing it first produces four essays illustrated with whatever
incidents the author happened to remember. `R14` requires a citation per concern precisely so this is
checkable.

**Truncation handling ships first.** `G15` is under a phase and shippable today, and every other
phase in this programme dispatches agents. The failure is live: two of six scouts lost on 2026-09-10,
seven truncations across two phases on 2026-09-11. This run has been following the resume-not-rerun
rule from `GOV-008` all night; `phase-agx-01` is what makes it documented rather than conventional.

**The deliberation trio splits at the arbiter, not down the middle.** `000073` and `000074` are only
meaningful against each other, so they ship together and `R18` makes their disagreement the test. The
arbiter is separated because `000075` itself calls it the most dangerous of the three, and the
repository has drawn this line twice already — `idea-triage` scouts but never promotes,
`/session-close` is typed by a person so an agent cannot reach completion.

**Two decision records are required, one of them conditionally.** The `000069` ruling needs an ADR
only if the answer is anything other than "Claude Code stays", because a decision to treat the runner
as interchangeable reshapes what `PLAN-020` generates. The arbiter's authority boundary needs one
unconditionally, because it is a standing constraint on how close any agent may come to an owner
decision rather than one phase's design.

## Corrections

None this phase.

## Unresolved

**Whether `R02` is buildable at all.** It asks for a truncated dispatch to be distinguishable from a
completed one without reading the output's last sentence. Whether that is reachable depends on what
the agent harness exposes to a caller, which is outside this repository. Options: drop the row, or
size the phase to find out. **Sized it to find out**, and stated in `PLAN-031` under *What may not be
buildable here* that the row is satisfied by recording the finding if no signal exists. This is the
one row whose feasibility the plan cannot establish from inside the repository, and saying so up
front seemed better than letting a future phase discover it.

**Whether `G14` should have been three phases or one.** Having ruled that the framework is derived
from evidence, a case exists for one document with four sections rather than three phases. Options:
one framework phase, or three. **Kept three**, because `000078` records the four sub-topics as
separate ideas and collapsing them to one document would discard the owner's own structure to save a
session. The two thin concerns are handled by boundary statements inside `phase-agx-09` rather than
by silence.

**Whether `phase-agx-13` belongs in this programme at all.** The partition calls `000009` its
weakest-evidenced placement — no recorded links, filed here by subject. Options: move it, or leave it.
**Left it**, and gave it `depends_on: []` so moving it later costs nothing. Recorded in the plan's
known-facts section so the next reader does not have to re-derive that it is loosely attached.

**Whether `000128`'s shared state model conflicts with the `000020` decline nomination.** `000128` is
described as the light alternative to `000020`, which the control analyst nominated for decline in its
favour — and `000020` sits in `P5`, which `phase-prog-07` finalizes later tonight. **Proceeded by
sizing `phase-agx-07` independently** and writing the cross-reference into its `next_action`, so
whoever claims it checks `P5`'s ruling first.

## Left undone

**All thirteen phases.** This phase finalizes a plan and builds nothing.

**`P4` should not run before `P1`, and this is not expressible in `depends_on`.** `phase-agx-10` is
sized on the assumption that `phase-idg-12` is the planner, and `R17` fails if that phase does not
exist. The dependency is on a ruling rather than an artifact, so it is stated in the plan's execution
section instead. This is the second cross-programme ordering constraint this run has produced, after
`phase-dgov-02`'s.

**The `000020` ruling is `phase-prog-07`'s**, later tonight. `phase-agx-07` is sized as though
`000128` proceeds, which is the direction the control analyst's nomination points, but the ruling has
not been made.
