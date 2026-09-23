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

The owner's rulings, given in the owner's session and relayed by the Session Manager (recorded on
its gitignored board, `_working/session-manager/board.md`):

- Scout-1 decision 1 (a): "one docs phase now", with `AGENTS.md` changed only on "line-by-line
  approval".
- Mapping Q5: "Test Author in unit graph now (amend GOV-014)". Mapping Q6: "two cycles, amend
  ARCH-006 stage 8 + GOV-018".
- Scout O-3 (a): "builders self-merge until P3 N2".
- Scout-1 decisions 3 (c), 4 (a) and 9 (c): agent ideas "labelled agent-proposed"; the
  "session-close reviewer gets no session record"; the "spot-audit replaced by sampled independent
  re-review".
- Protocol Q8 and Q15: "owner approval for every worktree removal"; "remote branch deletion
  OWNER-ONLY (standing; needs GOV-003 entry on a docs branch)".
- `CLAUDE.md`: "stale lines APPROVED as proposed (~144 tasks are separate files; ~137/141 replace
  counts with pointers to schemas/ and sql/001_schema.sql)".
- Idea `000378`: "GOV-003 governs" for phase completion.

Ideas covered: `000378` (completion authority contradicts itself), `000402` in the one instance
`000378` describes (not the general consistency check `000402` proposes), and the owner's rulings
above. Idea `000377` (governance documents still name `main` as the integration branch) is the same
kind of drift but was not in the task statement; OQ1 asks whether to include it.

## Decisions

**D1. One phase, as ruled.** The phase edits about ten files, all text, plus one regeneration. The
owner named one docs phase; splitting it by document was not considered further, because every
file here depends on the same set of rulings and a split would put half-amended contradictions on
`dev` between merges.

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
existing text already says the rate changes "once G5 sittings give real data". OQ3 asks the owner to
confirm.

**D4. One `GOV-003` entry per standing ruling, plus one for the document changes.** The task
statement lists three `GOV-003` entries (Q15, Q8, the agent-proposed label). This plan adds a
fourth, recording that Q5, Q6, O-3, and Scout-1 decisions 4 (a) and 9 (c) changed `ARCH-006`,
`GOV-014`, `GOV-018` and `REQ-022`. `GOV-003` is where an agent looks for "accepted choices that
resolve older plan conflicts" (`AGENTS.md`, Session backlog), and each of those rulings reverses a
rule a document still states. The cost is one more entry to keep true. The fourth entry records
rulings the owner made; it adds no rule.

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
regenerates both.

## Implementation phases

| Phase | What | Requirements | Depends on |
|---|---|---|---|
| `phase-dam-01` | Amend `ARCH-006`, `GOV-014`, `GOV-018`, `REQ-022` R23, `/session-start`, `/session-close` step 3, `/resume-lit-review`, the orient skill's source; add four `GOV-003` entries; put the `AGENTS.md` and `CLAUDE.md` text to the owner and apply what is confirmed; regenerate the orient skill and the catalog | R01-R11 | none |

## Requirement coverage

| Requirement | Evidence in `phase-dam-01` |
|---|---|
| R01, R02 | The grep and `diff` from `REQ-029`, output in the session record |
| R03, R04 | The changed rows and steps, and the two greps |
| R05 | The Test Author contract and the `nine` grep |
| R06 | The `spot-audit` grep over three files |
| R07 | `session-close.md` step 3 diff |
| R08 | The four `GOV-003` entries |
| R09, R10 | `git diff` of `CLAUDE.md` and `AGENTS.md`, and the owner's confirmation or its absence, recorded |
| R11 | `generate_agent_workflows.py --check`, governance, catalog diff |

Every requirement maps to the one phase.

## Execution order and real concurrency

`phase-dam-01` declares `sys-gov-docs` and `sys-realization`. It does not collide with
`phase-part-03`, which is active and declares `sys-governance` only, so it can be claimed while
`phase-part-03` runs, if its deliverables do not overlap (checked by `--ready` when claimed). It
collides with `phase-grd-01` (`PLAN-045`): both list `AGENTS.md` and `docs/08-governance/`. The
proposed order is `phase-grd-01` first, then `phase-dam-01`, because `phase-grd-01`'s governance
check will then catch a stale catalog in `phase-dam-01`'s own completion edit. If `phase-grd-01`
cannot start (it waits for `phase-part-03`), `phase-dam-01` can go first; the order is the owner's
at G3 (`PLAN-045`, OQ1).

## Out of scope

- **`AGENTS.md` line 284** (step 5 has the agent write `status: complete`), which `000378` also
  cites. It was not in the task statement; it is listed for the owner (OQ4).
- **Building the agent-proposed label** in `schemas/idea.schema.json` and `tools/append_idea.py`
  (OQ2).
- **The reviewer contract and dispatch** (Scout step 2, O-5, O-6): a new agent type and three
  procedure edits, planned separately.
- **Security review in the plan standard** (mapping Q9) and **verdict recording** (mapping Q7).
  Both are owner rulings of 2026-09-23 that change `GOV-010` and the merge gate; neither was in the
  task statement. OQ5 asks where they go.
- **Idea `000377`'s `main`-versus-`dev` drift**, unless the owner adds it (OQ1).

## Open questions

- **OQ1. Include `000377`?** Five documents still name `main` as the integration branch
  (`GOV-001:181`, `GOV-002:168` and `:170`, `OPS-001:132` and `:154`, `GOV-005:88`), and
  `session-close.md:79` and `:165` cite a withdrawn exception. Who: the owner, at G3. Leaning:
  include it; the edits are one line each, and `phase-dam-01` already edits `session-close.md`.
- **OQ2. The agent-proposed label's form.** Scout-1 decision 3 (c) says "a labelled
  'agent-proposed' state". A new idea status or field is a schema and writer change. Who: the owner,
  at G3. Leaning: `GOV-003` records the ruling now, and the idea bodies' existing first line
  ("Proposed by <session>, not the owner") serves as the label until a separate idea-system phase
  adds a field.
- **OQ3. The re-review's parameters** (D3). Who: the owner, at G3. Leaning: keep one in ten plus
  every once-rejected unit.
- **OQ4. `AGENTS.md` line 284.** Who: the owner. Leaning: put its text to the owner in the same
  session as lines 179-180, since both contradict `GOV-003` in the same way.
- **OQ5. Where the Q7 and Q9 rulings go.** Who: the owner, at G3. Leaning: a second docs phase after
  the reviewer contract (Scout step 2), because both change what a reviewer is given and records.
- **OQ6. Partition reconciliation.** As in `PLAN-045` OQ6: reconciled with the `phase-part-03`
  sweep's accepted result before G3.
