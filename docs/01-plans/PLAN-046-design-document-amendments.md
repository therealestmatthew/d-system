---
schema_version: 1
id: doc-design-document-amendments
code: PLAN-046
title: Design-document amendments — the 2026-09-23 rulings applied to the realization design, role contracts, review procedure and session commands
kind: plan
status: draft
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-gov-docs, sys-realization]
depends_on: [doc-design-document-amendments-requirements, doc-idea-realization-system, doc-realization-role-contracts, doc-three-altitude-review-procedure]
---

# Design-document amendments

Delivers [REQ-029](../06-requirements/REQ-029-design-document-amendments.md) in one phase,
`phase-dam-01`.

## Context and scope

`REQ-029`'s problem section lists eight places where the governing documents contradict each other
or the owner's rulings of 2026-09-23, each with its source. An agent that reads `ARCH-006`,
`GOV-014` or `/session-start` today is told that phase completion is owner-only, that a broker
enforces G4, that one revision cycle is allowed and that the owner spot-audits validations. None of
those is the current rule.

The owner's rulings, given in the owner's session and relayed by the Session Manager, are recorded
on its board (`_working/session-manager/board.md`, gitignored). Most answer the numbered list "Owner
decisions needed" in the Scout's report `_working/session-manager/scout/orchestration-1-evidence.md`
(items 1-9, each with lettered options), cited below as "Scout-1 item N (x)". The board records the
answers unnumbered, so each is given here with the board's words and the item it answers:

| Ruling as the board records it | Answers |
|---|---|
| "OWNER Scout-1 rulings: docs amendments = one docs phase now (AGENTS.md line-by-line approval)" | Scout-1 item 1 (a) |
| "agent ideas labelled agent-proposed" (same line) | Scout-1 item 3 (c) |
| "session-close reviewer gets no session record" (same line) | Scout-1 item 4 (a) |
| "OWNER rulings: ... spot-audit replaced by sampled independent re-review" (a separate board line) | Scout-1 item 9 (c) |
| "OWNER mapping rulings: ... Q5 Test Author in unit graph now (amend GOV-014); Q6 two cycles, amend ARCH-006 stage 8 + GOV-018" | Builder A's mapping (`reports/owner-design-mapping.md`), section 8, Q5 and Q6 |
| "OWNER Scout rulings: ... O-3 builders self-merge until P3 N2" | `orchestration-3-architecture.md`, "Owner decisions", O-3 (a) |
| "OWNER protocol rulings: Q8 owner approval for every worktree removal" and "Q15 remote branch deletion OWNER-ONLY (standing; needs GOV-003 entry on a docs branch)" | The board/state protocol draft's questions Q8 and Q15 |
| "CLAUDE.md stale lines APPROVED as proposed (~144 tasks are separate files; ~137/141 replace counts with pointers to schemas/ and sql/001_schema.sql)" | The restart file's open owner item on `CLAUDE.md` |
| "OWNER: ... OQ8 STANDING rule: never reuse a phase id for different content (GOV-003 via dam-01)" | `PLAN-045` OQ8 |
| Idea `000378`'s annotation: "Owner ruling, 2026-09-23 ... GOV-003 governs" | Phase-completion authority |

Ideas covered: `000378` (completion authority contradicts itself), `000381` (`CLAUDE.md`'s three
stale lines), `000402` in the one instance
`000378` describes (not the general consistency check `000402` proposes), and the owner's rulings
above, and `000377` (governance documents still name `main` as the integration branch), included by
the owner's ruling of 2026-09-23 (answer to OQ1). The work sits under the owner's framing in
`000411`: agents with defined contracts, and the orchestration systems that manage them, are
designed in parallel; the Test Author contract and the Validator and close-reviewer input rules here
are agent-contract changes.

**Partition placement.** In the partition the owner accepted at GATE 3 on 2026-09-23
(`docs/00-working/idea-partition-2026-09-23.md`, on `agent/phase-part-03` at `6051dad`), this
plan's ideas sit in the track "Governance checks, document hygiene and the portable framework":
`000377` and `000378` in the group "Cross-document textual drift", and `000402` in "Delivery-safety
gates in governance and CI". `000411` postdates the corpus. The drift group also holds `000381`
(`CLAUDE.md` has three stale lines; the owner must approve any edit), which is the `CLAUDE.md`
correction in D5 and is covered by this plan; `000298` (`PLAN-005` states a retired workaround as
live) and `000383` (`REQ-003` R11 names an idea status that does not exist) are in the same group
and not covered (OQ8). None of this plan's ideas is declined or held out.

## Decisions

**D1. One phase, as ruled, judged to fit one session.** The phase edits about fifteen files; the
five that `000377` adds each need a one-line change. It fits
one session because none of the work is design: every ruling is settled, the exact
`AGENTS.md` and `CLAUDE.md` text is fixed below, the Test Author's placement is fixed in D7, and the
one new contract (the Test Author) follows the shape of the nine existing ones in `GOV-014`. There
is no code; the verification is greps, a regeneration and the test suite. Splitting by document was
rejected because every file depends on the same rulings, and a split would put half-amended
contradictions on `dev` between merges (for example, `GOV-014` saying ten roles while `ARCH-006`
still names two at stage 8). If the session nevertheless runs short, `GOV-002`'s rule applies: the
remaining edits become new phase ids, with the half-done state recorded, rather than an oversized
phase left labelled as one session.

**D2. Stage 5 changes with stage 8.** Q6 names `ARCH-006` stage 8 and `GOV-018`. `GOV-018` step 5
says "`ARCH-006` stage 5 allows one revision cycle"; it implements stage 5, not stage 8. Changing
`GOV-018` alone would leave it contradicting the stage it cites. This plan therefore changes stage
5 as well, and reports this reading at G3. Stage 3 (partition) also says one revision cycle; it is
left alone because Q6 was about review of plans and builds, and nothing ties it to `GOV-018`.

**D3. The sampled re-review keeps the spot-audit's sampling rule and changes who reviews.** The
ruling names the mechanism, not its parameters. The existing rule (`GOV-014` Validator: at least one
in ten passed validations per G5 sitting, chosen at random, plus every unit that was rejected once
before it passed) is kept. What changes: the sample is re-reviewed by a dedicated reviewer type
(owner ruling of 2026-09-23 that reviews backing a merge come from a validator or adversary type,
never general-purpose), which is not the reviewer that passed it, with the requirement and the diff
only; its result goes to the owner at G5. The alternative, a new rate, has no data behind it; the
existing text already says the rate changes "once G5 sittings give real data". Ruled by the owner on
2026-09-23 (answer to OQ3): "re-review 1 in 10, plus every once-rejected unit".

**D4. One `GOV-003` entry per standing ruling, plus one for the document changes.** The task
statement lists three `GOV-003` entries (Q15, Q8, the agent-proposed label). The owner added a
fourth standing ruling on 2026-09-23, answering `PLAN-045` OQ8: "a STANDING rule that a phase id is
never reused for different content, recorded in GOV-003 through dam-01". This plan adds a fifth, recording that Q5, Q6, O-3, and Scout-1 items 4 (a) and 9 (c) changed `ARCH-006`,
`GOV-014`, `GOV-018` and `REQ-022`. `GOV-003` is where an agent looks for "accepted choices that
resolve older plan conflicts" (`AGENTS.md`, Session backlog), and each of those rulings reverses a
rule a document still states. The alternative, only the three entries named in the task, would
leave a reader of `GOV-003` with no record of why `ARCH-006`, `GOV-014` and `GOV-018` changed, and
the next session that finds the old text in a session record or a plan would not know which is
current. The cost is one more entry to keep true. The fifth entry records rulings the owner made;
it adds no rule. The agent-proposed entry records the form the owner ruled on 2026-09-23 (answer to
OQ2): "GOV-003 records the ruling, and the body's first line is the label until an idea-system field
exists".

**D5. `AGENTS.md` and `CLAUDE.md` changes are proposals the executing session puts to the owner.**
`CLAUDE.md` and `AGENTS.md` each forbid editing either without the owner's explicit approval of the
specific change. The owner's `CLAUDE.md` approval, as relayed, gives the substance, not the exact
text. The executing session therefore shows the owner the exact old and new text below, in its own
session, and applies only what the owner confirms there. The text is fixed here so G3 can see it.

`AGENTS.md` lines 179-180. The task statement also names lines 155-156; that change belongs to
`phase-grd-01` in `PLAN-045`, because its new text is true only after that phase's check exists.

Old:

```text
  an available checkpoint skill). It is safe to record progress any number of times, but do not mark a phase complete;
  only the owner-invoked review (e.g., `/session-close`) does that. An agent must never invoke final closure itself.
```

New:

```text
  an available checkpoint skill). It is safe to record progress any number of times, but a checkpoint never marks a
  phase complete. A phase is completed by `/session-close`, or by a coordinator under the three conditions in
  GOV-003's entry "Coordinator completion replaces owner-invoked /session-close" - never on an agent's own judgement
  that the work looks done.
```

`AGENTS.md` lines 284-286 (hand-off step 5), put to the owner in the same session as 179-180 (owner's
answer to OQ4, 2026-09-23). Old:

```text
5. Update your phase: `status: complete`, `session:`, `completion_evidence:` (files that exist now),
   and `result:` summarizing the actual verification output. Keep the `agent` field as the record of
   who did the work.
```

New:

```text
5. Update your phase: `session:`, `completion_evidence:` (files that exist now), and `result:`
   summarizing the actual verification output. Keep the `agent` field as the record of who did the
   work. Do not set `status: complete` here: `/session-close` sets it, or a coordinator does under the
   three conditions in GOV-003's entry "Coordinator completion replaces owner-invoked /session-close".
```

`CLAUDE.md` lines 137, 141 and 144. Old:

```text
`project.schema.json`, `commitment.schema.json`, `person.schema.json`, `tag.schema.json`
Tables: `projects`, `people`, `project_people`, `tags`, `project_tags`, `commitments`, `tasks`
- Tasks are embedded in commitment JSON but get their own `tasks` table in DuckDB (unpacked by rebuild)
```

New:

```text
One JSON Schema per entity and record type; the current set is the contents of `schemas/`.
Tables: see `sql/001_schema.sql` for the current set.
- Tasks are separate files under `_data/tasks/`, not embedded in commitment JSON, and load into their own `tasks` table
```

**D6. The orient skill is changed at its source.** `.claude/skills/orient/SKILL.md` and
`.agents/skills/orient/SKILL.md` are generated from `agent-workflows/orient.md` by
`tools/generate_agent_workflows.py` and carry a "do not edit" notice. The phase edits the source and
regenerates both. Editing the generated files directly was rejected: the next regeneration would
overwrite the change, and `generate_agent_workflows.py --check` would fail until it did.

**D7. Where the Test Author sits in stage 8.** Q5 adds the role to the `unit` graph; `ARCH-006`'s
stage table says a stage with no failure path is a defect, so stage 8 must name the role and its
failure path, not only `GOV-014`. Proposed text, taken from the owner's design (`docs/00-working/agentic-sdlc-2026-09/agentic-sdlc-design.md`,
section 3.6, "Runs
**before** the Task Dev agent and commits red tests"), which mapping Q1 made an input to the `unit`
graph: the Test Author writes failing tests from the phase's acceptance before the Developer starts;
the Developer may not change them; a Developer who holds that a test is wrong records a finding,
the Validator rules on it, and only the Test Author changes the test; this follows the stage's
two-cycle path and then parks the unit, like any other finding. The alternative, leaving stage 8
unchanged until the `unit` graph is built, would leave `GOV-014` and `ARCH-006` disagreeing about
who works in stage 8. Ruled by the owner on 2026-09-23 (answer to OQ7): "Test Author stage-8 text as proposed".

## Implementation phases

| Phase | What | Requirements | Depends on |
|---|---|---|---|
| `phase-dam-01` | Amend `ARCH-006`, `GOV-014`, `GOV-018`, `REQ-022` R23, `/session-start`, `/session-close` step 3, `/resume-lit-review`, the orient skill's source, and the `main`-branch passages from `000377`; add five `GOV-003` entries; put the `AGENTS.md` and `CLAUDE.md` text to the owner and apply what is confirmed; regenerate the orient skill and the catalog | R01-R12 | none |

## Requirement coverage

| Requirement | Evidence in `phase-dam-01` |
|---|---|
| R01, R02 | The grep and `diff` from `REQ-029`, output in the session record |
| R03, R04 | The changed rows and steps, and the two greps |
| R05 | The Test Author contract and the `nine` grep |
| R06 | The `spot-audit` grep over three files |
| R07 | `session-close.md` step 3 diff |
| R08 | The five `GOV-003` entries |
| R09, R10 | `git diff` of `CLAUDE.md` and `AGENTS.md`, and the owner's confirmation or its absence, recorded |
| R11 | `generate_agent_workflows.py --check`, governance, catalog diff |
| R12 | The `main` grep, with each remaining line explained |

Every requirement maps to the one phase.

## Execution order and real concurrency

`phase-dam-01` declares `sys-governance`, `sys-gov-docs` and `sys-realization`. `sys-governance`
is declared because no system registers `.claude/`, `agent-workflows/`, `AGENTS.md` or `CLAUDE.md`,
and every phase that edits them declares it (for example `phase-ses-02`, `phase-idea-06`,
`phase-part-03`). So `phase-dam-01` cannot be claimed while `phase-part-03` is active: both change
the agent-workflow sources. It also collides with every `PLAN-045` phase through `sys-governance`,
and with `phase-grd-01` on `AGENTS.md` and `docs/08-governance/`. The proposed order is
`phase-grd-01`, `phase-grd-02`, `phase-dam-01`, so the staleness check from `phase-grd-01` catches a
stale catalog in `phase-dam-01`'s own commits; the order is the owner's at G3 (`PLAN-045`, OQ1).

## Out of scope

- **Building the agent-proposed label** in `schemas/idea.schema.json` and `tools/append_idea.py`.
  Until then the body's first line is the label (OQ2).
- **The reviewer contract and dispatch** (Scout step 2, O-5, O-6): a new agent type and three
  procedure edits, planned separately.
- **Security review in the plan standard** (mapping Q9) and **verdict recording** (mapping Q7).
  Ruled by the owner on 2026-09-23 (answer to OQ5): "Q7/Q9 go in a second docs phase, after the
  reviewer contract". That phase is not planned here.

## Open questions

Closed on 2026-09-23: owner rulings relayed by the Session Manager, and items the planner resolved
(OQ5 by Ideation's records, OQ6 against the accepted partition):

- **OQ1. Include `000377`?** Ruled: "include 000377". Applied: `REQ-029` problem 9 and R12.
- **OQ2. The agent-proposed label's form.** Ruled: "GOV-003 records the ruling, and the body's first
  line is the label until an idea-system field exists". Applied: D4, `REQ-029` R08.
- **OQ3. The re-review's parameters.** Ruled: "re-review 1 in 10, plus every once-rejected unit".
  Applied: D3.
- **OQ4. `AGENTS.md` line 284.** Ruled: "AGENTS.md 284 is put to the owner in the same session as
  179-180". Applied: D5, `REQ-029` R10.
- **OQ5. Where the Q7 and Q9 rulings go.** Ruled: "Q7/Q9 go in a second docs phase, after the
  reviewer contract". Recorded under Out of scope.
- **OQ7. The Test Author's stage 8 text.** Ruled: "Test Author stage-8 text as proposed". Applied:
  D7.

- **OQ6. Partition reconciliation.** Done against the accepted partition (`6051dad`); see
  "Partition placement" in Context and scope.

Still open:

- **OQ8. The rest of the drift group.** `000298` and `000383` are one-passage text corrections of the
  same kind as `000377`. Who: the owner, at G3. Leaning: add both to `phase-dam-01`, since the
  partition grouped them with work this phase already does and each is a single passage.
