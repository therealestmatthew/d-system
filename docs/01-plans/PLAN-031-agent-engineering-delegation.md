---
schema_version: 1
id: doc-agent-engineering-delegation
code: PLAN-031
title: Agent engineering and delegation (P4)
kind: plan
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-15'
systems: [sys-delivery, sys-governance]
depends_on: [doc-agent-engineering-delegation-requirements, doc-prompt-pack-protocol]
---

# Agent engineering and delegation (P4)

## Summary

Programme `P4` of the twelve and the largest — nineteen ideas across ten fine groups. How agents in
general are instructed, observed, coordinated and reviewed. `P1`'s agents are one application of
this; `P5` runs it without a person present.

The partition flags this programme specifically: it "carries the most internal near-duplication and
deserves a scoping pass before any phase count is committed", and the finalize phase's scope requires
that pass to run before anything is sized. [It ran first](#the-scoping-pass), and it cut six phases
from a naive reading.

| Group | Ideas | What it covers |
|---|---|---|
| `G14` Framework umbrella | `000078`–`000082` | Guides, sensors, context pipelines, orchestration |
| `G15` Truncation handling | `000077` | Resume a truncated subagent rather than rerunning it |
| `G16` Lifecycle roster | `000072`, `000069` | The agent roster, and whether Claude Code stays a dependency |
| `G17` Deliberation trio | `000073`–`000075` | Expander, minimalist, arbiter |
| `G18` Anti-pattern tracking | `000097`, `000138` | The same ask a day apart at two scales |
| `G19` Delegation methodology | `000139` | Dispatch-cost estimation, model assignment, escalation, retrospective |
| `G20` Commands/skills/agents audit | `000126`, `000013` | What the repository already ships, judged |
| `G21` Shared state model | `000128` | Cross-agent context that a coordinator stops hand-carrying |
| `G22` Runtime-evidence convention | `000136` | Browser smoke dispatch and named runtime instruments |
| `G23` Transcript review | `000009` | Independent transcript extraction and adversarial comparison |

## What was verified in the repository before sizing

The phase's acceptance requires both of these checked rather than assumed.

**`G18`'s capture half is delivered.** `.claude/skills/log-anti-patterns/SKILL.md` exists as a
complete workflow — it takes an anti-pattern, decides which record should hold it, and writes the
ones the owner confirms, with explicit rules against editing `AGENTS.md` and against writing without
confirmation. `000097`'s owner ruling already rescoped it to derivation; this confirms why. What
remains is **recurrence detection and derivation**, not capture.

**`G22`'s substance largely exists as a recorded lesson, and its convention does not.**
`brain/procedures/runtime-behavior-needs-runtime-evidence.md` exists at `confidence: high` and carries
the rule verbatim — runtime requirements need a live check in the loop, and an agent asked to fix
runtime behaviour must receive recorded measurements. It documents the `phase-wb-09` incident: a page
that rendered nothing at all in both dev and production builds, invisible to build, lint, pytest and
the mechanical gate, caught first by the only check that opened a browser. What does not exist is the
**pack-authoring convention** that makes a frontend work item carry its instrument by construction.
So `G22` is not a phase; it is a section of `G19`'s methodology.

## The scoping pass

Six phases removed relative to sizing each idea or group at face value. Each cut is a ruling, not a
deferral.

**1. `000072`'s planner bullet is struck — the acceptance condition's explicit subject.** `000072`
proposes a lifecycle roster whose first role is "a planner that turns a triage into a plan". That is
`000046`, which `phase-prog-04` sized four hours ago as `phase-idg-12` in `P1`, complete with the
`000047` standard and the `000049` location it depends on. Only the control analyst caught the
duplication at partition time.

Ruled: **the roster is built without a planner role, and `phase-idg-12` is the planner.** `R17` makes
this checkable rather than a note — a roster reinstating the role fails the row. The alternative,
building it here and retiring `phase-idg-12`, was rejected because `P1`'s version is the better
specified of the two: it has a quality standard to draft against and a defined location to draft
into, neither of which `000072`'s bullet has.

**2. `000013` does not get a phase; `000126`'s audit answers it.** The partition already observes
that `000126`'s "missing-and-needed" output *is* `000013`'s question, and that `000013`'s candidate
list is partly shipped — `/session-close` and `/backlog` both exist now. One audit, one phase.

**3. `000069` does not get a phase; the audit rules on it.** Whether this repository needs Claude Code
or *an* agent runner is a question about `.claude/`, and the audit is the work that reads every file
in `.claude/` and judges it. Asking the question in the same sitting costs nothing; asking it in a
separate phase means reading all of `.claude/` twice. `R05` makes the ruling an acceptance condition
of the audit phase.

**4. `000136` does not get a phase; it is a section of `G19`.** Verified above: the lesson is
recorded, the convention is not, and a convention for authoring dispatches belongs in the document
that governs authoring dispatches. A standalone phase would produce a second document `G19` then has
to reconcile with.

**5. `G14` is two phases, not four or five, and it runs late.** Two cuts here, which is why the six
above come from five numbered rulings. Sensors and context
pipelines do not each earn a phase: `000080`'s live-monitoring half is `G15` and `G19`'s work, and
`000081` is explicitly a cross-reference to `P6`'s `G25` rather than a merge, so what remains of both
is a boundary statement — one phase, not two.

More consequentially, **the framework is derived from the evidence rather than written before it.**
`000078`'s own framing is that agent construction has recurring concerns worth naming once. The
naming is only worth anything if it comes from what actually recurred here, and this programme's
other groups are what establish that: the audit finds what the repository ships, `G18` finds what
keeps going wrong, `G19` finds what a good dispatch costs. Writing the framework first would produce
four essays illustrated with whatever incidents the author remembered. `R14` requires a citation per
concern for exactly this reason.

## The chosen design

### 1. Truncation handling ships first, because it is cheap and this repository is still paying for it

`G15` is `<1` phase and shippable today — the cap is a number, the rule is resume-not-rerun, and both
fit in guidance. It goes first because every other phase in this programme dispatches agents, and
`000077`'s failure is live: two of six scouts lost on 2026-09-10, seven truncations across two phases
on 2026-09-11.

`R02` adds what `000077` actually asks for and guidance alone cannot give: a truncated dispatch must
be distinguishable from a completed one *without reading the last sentence*. That is the part with
teeth, and it may not be satisfiable from inside this repository — see [what may not be
buildable](#what-may-not-be-buildable-here).

### 2. The audit runs second, because four groups are waiting on what it finds

The partition notes `G20`'s audit informs `G02`, `G19`, `G21` and `G22` without blocking them.
"Without blocking" was true when nothing else was scheduled; here it is scheduled, so the informing
is free if the audit runs early and wasted if it runs late.

### 3. Anti-pattern work is store-then-derive, and the store starts populated

`R07` requires the store to be populated from `brain/procedures/` and the 2026-09-11 starter catalog
at first run, with a count. A recurrence detector with an empty store detects nothing for weeks and
looks broken; the material already exists and is the reason the idea was raised twice in two days.

`R08` requires the path from an accumulated record to the dispatch text it changed to be traceable.
Without it, derivation produces a document that joins the pile of documents nobody reads, which is
the failure `000097` describes about its own subject matter.

### 4. The deliberation trio splits at the arbiter, not down the middle

`000072` instructs that `G17` stays out of the roster — a different family, planned alongside but not
merged — and that instruction is followed.

Within `G17`, the split is expander-plus-minimalist, then arbiter. `000073` and `000074` are only
meaningful against each other: `R18` makes "the two produce genuinely opposed outputs on the same
input" the test, because two agents that agree on everything are one agent with two prompts. The
arbiter is separated because `000075` calls it the most dangerous of the three and the repository has
already drawn this line twice — `idea-triage` scouts but never promotes, `/session-close` is typed by
a person precisely so an agent cannot reach completion. `R19` requires the arbiter's boundary to be at
least as tight, and advisory wherever scope is the owner's.

### 5. The shared state model must not become a second lock table

`000128` proposes extending `_tmpagent/` so established facts reach every agent without a coordinator
re-pasting them. `_tmpagent/` already carries a claims ledger with claim, activate and release
semantics, and `backlog.yaml` is the lock table. `R13` requires the contract to state what may be
written, by whom, and when it is released — and forbids duplicating claim semantics. Two lock tables
disagreeing is worse than one lock table with gaps.

### Which of these need a decision record

**Two.**

- **The `000069` ruling needs one** if the answer is anything other than "Claude Code stays". A
  decision to treat the agent runner as interchangeable reshapes what `.claude/` is for and what
  `PLAN-020` generates, and a future reader finding generated workflows needs to know whether that
  was chosen or inherited. `phase-agx-02` writes it conditionally, which is recorded in its scope.
- **The arbiter's authority boundary needs one.** It sets how close an agent may come to a decision
  reserved to the owner, which is a standing constraint rather than one phase's design.

The other rulings — the struck planner bullet, the folded phases, the framework's late sequencing —
are recorded in this plan and in `REQ-016`'s rows, where the reader meets them.

## Implementation phases

Thirteen phases under `phase-agx-*`, registered in [the backlog index](../09-backlog/README.md).

| Phase | Title | Group | Depends on |
|---|---|---|---|
| `phase-agx-01` | Document the truncation cap and make truncation detectable | `G15` | — |
| `phase-agx-02` | Audit every command, skill and agent, and rule on the Claude Code dependency | `G20`, `G16` | — |
| `phase-agx-03` | Build the anti-pattern store with recurrence detection, populated from what exists | `G18` | — |
| `phase-agx-04` | Derive authoring rules from accumulated anti-patterns, traceably | `G18` | `03` |
| `phase-agx-05` | Write the delegation-scoping methodology, including the runtime-evidence convention | `G19`, `G22` | `01`, `02` |
| `phase-agx-06` | Measure the methodology against outcomes and change at least one rule | `G19` | `05`, `04` |
| `phase-agx-07` | Extend `_tmpagent` into a shared state model without a second lock table | `G21` | `02` |
| `phase-agx-08` | Agent engineering: guides (`000079`), grounded in this repository's incidents | `G14` | `02` |
| `phase-agx-09` | Agent engineering: orchestration (`000082`), with the `000080`/`000081` boundaries | `G14` | `02`, `08` |
| `phase-agx-10` | Build the lifecycle agent roster, without a planner role | `G16` | `02`, `08` |
| `phase-agx-11` | Build the expander and the minimalist, and prove they disagree | `G17` | `10` |
| `phase-agx-12` | Rule the arbiter's authority boundary, then build it | `G17` | `11` |
| `phase-agx-13` | Independent transcript review against the participant's record | `G23` | — |

### Sizing against the partition

Partition-time sizing was **12–15 phases** against 19 ideas, with the explicit caveat that the count
was meaningless until the duplication was cut. This plan lands **thirteen**, inside the range but
reached from the other direction: the scoping pass removed six phases a face-value reading would
have produced — `000046`'s duplicate planner, `000013`'s own phase, `000069`'s own phase, `000136`'s
own phase, and two of `G14`'s four, since `000080` and `000081` were both folded into boundary
sections of `phase-agx-09` rather than given phases.

Two groups land below their partition range as a result. `G14` is 2 against 4–5, and `G16` is 1
against 2–3 because `000069` moved into the audit and the planner bullet was struck. `G19` is 2
against "2–3; scope down first", which is that instruction followed. Every other group lands inside
its range.

## Execution order and real concurrency

Every phase declares `sys-delivery`, and most also touch `.claude/` or `docs/08-governance/`, so the
programme is largely serial. Two phases are genuinely independent of the rest and can run beside any
peer: `phase-agx-01` and `phase-agx-13`, neither of which depends on the audit.

`phase-agx-02` is the bottleneck: six phases depend on it. It is also the phase whose output is most
reused, which is why decision 2 puts it second rather than wherever its group's number fell.

The critical path is five deep: `02` → `08` → `10` → `11` → `12`.

**This programme should not run before `P1`.** `phase-agx-10` is sized on the assumption that
`phase-idg-12` is the planner, and `R17` fails if that phase does not exist. The dependency is on a
ruling rather than an artifact, so it is not expressible in `depends_on`, which is why it is stated
here.

## What may not be buildable here

`R02` asks for a truncated dispatch to be distinguishable from a completed one without reading its
last sentence. Whether that is reachable depends on what the agent harness exposes to a caller, which
is outside this repository. `phase-agx-01` is sized to document the cap and the resume rule
regardless, and to report what the harness actually offers rather than to guarantee the signal. If it
turns out to be unavailable, `R02` is satisfied by recording that finding, and the fallback is the
convention `GOV-008` already carries: resume, never re-run.

This is stated here rather than discovered mid-phase because it is the one row in `REQ-016` whose
feasibility this plan cannot establish from inside the repository.

## Requirement coverage

Every row of `REQ-016` maps to at least one phase, and every phase carries at least one row.

| Requirement | Phases |
|---|---|
| R01 The truncation cap documented with its value | `phase-agx-01` |
| R02 Truncation distinguishable without reading the output | `phase-agx-01` |
| R03 A verdict per shipped command, skill and agent | `phase-agx-02` |
| R04 Each verdict cites scope, tooling, model and context cost | `phase-agx-02` |
| R05 The Claude Code dependency ruled on | `phase-agx-02` |
| R06 Recurrence detected mechanically | `phase-agx-03` |
| R07 The store populated from what exists | `phase-agx-03` |
| R08 Derived rules traceable to authored prompts | `phase-agx-04` |
| R09 A delegation-scoping methodology with inputs | `phase-agx-05` |
| R10 Runtime items carry a named instrument and a live check | `phase-agx-05` |
| R11 The methodology measured and updated | `phase-agx-06` |
| R12 Established facts reach every agent unpasted | `phase-agx-07` |
| R13 The shared state is not a second lock table | `phase-agx-07` |
| R14 A framework with a citation per concern | `phase-agx-08`, `phase-agx-09` |
| R15 Boundaries against `P6` and `P3` stated | `phase-agx-09` |
| R16 A roster whose roles cannot reach the decision above | `phase-agx-10` |
| R17 No planner role — `P1` owns it | `phase-agx-10` |
| R18 Expander and minimalist genuinely disagree | `phase-agx-11` |
| R19 The arbiter's authority boundary | `phase-agx-12` |
| R20 An independent transcript record, compared | `phase-agx-13` |

## Key references

- **The requirement** — [REQ-016](../06-requirements/REQ-016-agent-engineering-delegation.md).
- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P4`, including the scoping-pass instruction this plan executes.
- **The prompt-pack protocol** ([GOV-008](../08-governance/GOV-008-prompt-pack-protocol.md)) — carries the cost protocols and agent hygiene `G19` consolidates rather than replaces.
- **Portable agent workflows** ([PLAN-020](PLAN-020-portable-agent-workflows.md)) — what makes `.claude/` generated output, and therefore what `000069`'s question is about.
- **The recorded lesson `G22` builds on** — `brain/procedures/runtime-behavior-needs-runtime-evidence.md`.
- **Idea graph and lifecycle** ([PLAN-029](PLAN-029-idea-graph-lifecycle.md)) — `phase-idg-12` is the planner `R17` keeps out of the roster.

## Known facts not to rediscover

- **`000072`'s planner bullet is struck.** Ruled in the scoping pass, asserted by `R17`. Do not
  reinstate it.
- **Capture is delivered.** `log-anti-patterns` exists and works. A phase that rebuilds it has spent
  a session re-shipping a skill.
- **The runtime-evidence lesson is recorded.** `brain/procedures/runtime-behavior-needs-runtime-evidence.md`
  carries it at high confidence. What is missing is the authoring convention, not the knowledge.
- **`000081` is a cross-reference to `P6`'s `G25`, not a merge.** `000081`'s deliverable is a
  selection framework; `G25`'s is a query contract. Both touch `tools/load_context.py`, which today
  queries only the `memories` table.
- **`000082` stays in `P4` rather than joining `P3`'s `G09`.** It is an open survey of orchestration;
  `G09` is two diagnosed incidents with a known fix shape.
- **`000009` is the weakest-evidenced placement in the partition** — it carries no recorded links to
  anything and was filed here by subject. `phase-agx-13` depends on nothing, so if the placement is
  wrong it costs nothing to move.
- **`000013`'s candidate list is partly shipped.** `/session-close` and `/backlog` both exist. Check
  before treating any candidate as missing.
