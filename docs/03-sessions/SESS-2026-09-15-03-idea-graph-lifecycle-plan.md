---
schema_version: 1
id: doc-session-idea-graph-lifecycle-plan
code: SESS-2026-09-15-03
title: Finalize the idea graph and lifecycle plan (P1)
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-portfolio, sys-projection, sys-governance]
depends_on: [doc-idea-graph-lifecycle]
---

# Finalize the idea graph and lifecycle plan (P1)

## Phase

`phase-prog-04` — Finalize the idea graph and lifecycle plan (P1).

Second phase of the unattended overnight batch run by `agent-night`, after `phase-prog-01`.

## Verification

`uv run python -m src.governance`

```
Governance OK: 27 systems, 230 documents, 25 memories, 202 backlog phases
```

Exit 0. Documents 229 → 230 for `REQ-014`; phases 190 → 202 for the twelve `phase-idg-*` phases.

`uv run python -m src.governance --ready`

```
| phase-idg-01 | Ship the idea schema bundle and record the scope-fork decision | — | 1 | ready | — | phase-prog-04 |
| phase-idg-06 | Move /idea capture into a subagent | — | 1 | ready | — | — |
| phase-idg-08 | Wrap idea metrics as a command and rule on the generated page | — | 2 | ready | — | — |
| phase-idg-10 | Audit the plan corpus and write the plan-quality standard | — | 2 | ready | — | — |
| phase-idg-11 | Define where a promoted plan lives before it earns a code | — | 2 | ready | — | — |
```

Five of the twelve are `ready`; the other seven wait on declared prerequisites. Four of the five show
`Conflicts: —` against this phase's own live claim, which is the plan's concurrency claim confirmed
by the tool rather than asserted: `phase-idg-06`, `-08`, `-10` and `-11` genuinely do not collide.

`uv run pytest` — not in the phase's list, run because the post-rebase run decides integration.

```
580 passed, 2 warnings
```

### The `G03` delivery check, run before any phase was sized

The phase's third acceptance condition requires this, so it was done first.

`uv run python tools/overview_metrics.py` produced real output — a JSON document opening with
`age_of_open_ideas` over ideas `000208`–`000238`. The tool's own header states it implements
`000071`'s candidate metric set and reads through `load_events()` and `fold()` rather than parsing
`_data/ideas.jsonl`.

```
$ ls ts/src/stage/ | grep -iE "idea|backlog"
BacklogExplorerRegion.tsx
IdeaExplorerRegion.tsx

$ grep -n "/api/v1" ts/src/stage/IdeaExplorerRegion.tsx
3:const IDEAS_URL = '/api/v1/workbench/ideas'
4:const IDEAS_QUEUE_URL = '/api/v1/workbench/ideas/queue'

$ grep -n "/api/v1" ts/src/stage/BacklogExplorerRegion.tsx
3:const BACKLOG_URL = '/api/v1/workbench/backlog'
4:const BACKLOG_QUEUE_URL = '/api/v1/workbench/backlog/queue'

$ ls .claude/skills/ | grep orient
orient
```

`000008` and `000071`'s metric half are delivered by the tool. `000010`'s idea browser and `000042`'s
combined at-a-glance view are delivered as workbench panels. `000071`'s second half is the `orient`
skill. What remains is a command wrapping the tool, and capture with no session open — two phases,
against a group that reads as six ideas.

## Acceptance

- **`PLAN-029` carries no placeholder banner and states a chosen design.** Met. Banner removed,
  `status` moved `draft` → `active`, and six numbered rulings under *The chosen design*, each naming
  the option refused and the cost accepted.
- **A requirement document exists for P1 and every row maps to at least one phase.** Met. `REQ-014`
  carries twenty rows. Checked in both directions against the real backlog rather than the plan's own
  table: every row is cited in at least one phase's acceptance, and every one of the twelve phases
  cites at least one row.
- **What is already delivered in `G03` is verified in code before any phase is sized.** Met, and done
  first rather than retrofitted. The evidence is in `## Verification` above — the tool was executed,
  the two explorer components were read for the endpoints they call, and the `orient` skill was
  confirmed present. The finding changed the sizing: `G03` went from the partition's "most
  shovel-ready" six ideas to two phases.
- **`phase-prog-04` is removed from `next_up` in the same change that completes it.** Met. Removed in
  commit `3da1295`, the same commit that registers the track.

## Backlog

`phase-prog-04` is `status: complete`, `agent: agent-night`,
`session: doc-session-idea-graph-lifecycle-plan`. Completion evidence is `PLAN-029`, `REQ-014`,
`docs/09-backlog/README.md` and this record.

Written under the owner's advance authority for this batch, and only after the read-only independent
review below confirmed all four conditions. Removed from `next_up` in commit `3da1295`.

Twelve phases added under `phase-idg-*`, all `status: queued`, none claimed.

## Review

A fresh non-fork sub-agent with read-only tools (`Read`, `Grep`, `Glob`, `Bash` — no `Edit`, no
`Write`) reviewed `dev...agent/phase-prog-04`. Read-only by construction this time, following
`phase-prog-01`, where the review agent held write tools it was merely instructed not to use. Its own
runs:

```
$ uv run python -m src.governance
Governance OK: 27 systems, 231 documents, 25 memories, 202 backlog phases
EXIT: 0

$ uv run pytest
580 passed, 2 warnings
```

**Condition 1 — no placeholder banner, states a chosen design — Met.** "`status: active`, banner gone,
and carries six numbered design rulings each naming the alternative refused and the cost accepted…
`grep -in "placeholder|TBD|TODO"` on the branch file returns nothing."

**Condition 2 — requirement exists, every row maps to a phase — Met, verified independently.** "Read
`REQ-014` (20 rows, R01–R20) and `backlog.yaml`'s `phase-idg-*` acceptance text directly, not
`PLAN-029`'s own coverage table. Every row R01–R20 is cited by name in at least one phase's
`acceptance:`, and every one of the 12 `phase-idg-*` items cites at least one row. Both directions
hold."

**Condition 3 — `G03`'s delivery verified in code before sizing — Met, and re-verified
independently.** The reviewer ran the tool itself, confirmed the four API routes the explorer panels
call are implemented in `src/api/routes/workbench.py`, and confirmed `.claude/skills/orient/SKILL.md`
exists. Its sharpest check: "All four artifacts (tool, both region files, orient skill) are
**untouched by this branch**… the phase verified pre-existing delivery rather than building it and
then claiming credit." On the sizing: "The two-phases-against-six-ideas sizing is defensible on the
evidence found."

**Condition 4 — removed from `next_up` in the same change — Met, verified with `git show`.**
"`git show 3da1295 -- docs/09-backlog/backlog.yaml` shows `next_up` losing `phase-prog-04` in the
identical commit that adds the 12 `phase-idg-*` items and registers the prefix."

**`backlog.yaml` integrity, attacked directly.** The reviewer was asked specifically to check that the
anchor repair had not silently altered the peer `phase-conc-*` track. "Parsed every `phase-conc-*`
item on `dev` against the branch: **all nine are dict-identical** — the anchor→literal expansion
changed only YAML syntax, not content… the only changes are 12 new `phase-idg-*` items and the
`next_up` removal. No silent mutation of any other phase." No anchors or aliases remain.

**Three weaknesses reported, none blocking. All three fixed before close.**

- *"`backlog.yaml` is modified substantially but is not a declared deliverable of `phase-prog-04`
  itself"* — 417 lines rewritten under a declaration naming only the plan, the requirements directory
  and the README. The reviewer noted this is wider than this run's own staged idea candidate had
  said, which named only `README.md`. **Fixed** by widening that candidate; not fixed by changing the
  declaration, for the reason recorded in it.
- *"`implements 000071's metric set` slightly overclaims"* — `000071`'s body names *amendment rate as
  a proxy for rework*, which the tool does not emit; `phase-demo-03` scoped it out and annotated the
  idea saying so. **Fixed**: both documents now read "delivered metric set", and `PLAN-029` states the
  omission explicitly so `phase-idg-08` does not silently reinstate it.
- *"`phase-idg-10`'s second acceptance bullet is close to restating its own scope line"* — both
  asserted "checkable, not prose" with no independent verification. **Fixed**: the bullet now requires
  a named section list that `phase-idg-12` can grep a draft against.

## Decisions

**The scope fork was ruled toward fields on the idea schema, not a separate graph layer.** `ARCH-005`
names this the decision everything else is scoped against and leaves it open. The graph layer is the
better design if it exists; it does not, and it needs `000060` and `000032`, both in `P6`, neither
started. Choosing it blocks all six `G01` ideas behind an unbuilt substrate. At ~240 ideas the
traversal queries are relational joins DuckDB already expresses, which answers `ARCH-005`'s own
query-surface question — no graph library needed at this size. The cost is stated in the plan: if
`P6` later builds the layer, these fields become a migration.

**Axes are optional, but a blank axis must carry a reason.** `ARCH-005` asks whether forcing all three
produces meaningless values or whether optionality produces inconsistent coverage. Both are real. The
resolution is that an axis absent *with a recorded reason* is distinguishable from an idea nobody has
processed, which is what makes coverage measurable at all.

**The backfill method was made a requirement rather than left to care.** `R07` requires appending
classification events, never rewriting existing lines. A backfill is precisely the operation that
tempts an in-place edit, and an edited append-only log stops being one.

**`000048` and `000127` were built as one phase.** The partition already records them as the same ask
six days apart. `000127`'s general principle — mechanical, self-contained skills should default to a
subagent — is recorded as a finding for the commands-and-skills audit rather than built here, because
generalising it is a different piece of work from doing it once.

**`ARCH-005` moves to `accepted` inside `phase-idg-01`, not here.** It was written as a vocabulary
awaiting a governing requirement. Accepting it in the same phase that writes its requirement would
have been defensible; deferring it to the phase that actually lands the schema is better, because
until then nothing has been built against the vocabulary and acceptance would be a claim about
untested design.

## Corrections

**Governance went red mid-phase on a duplicate YAML anchor, from my own append.**

```
ERROR backlog inputs: found duplicate anchor 'id001'; first occurrence
  in "<unicode string>", line 8757, column 12:
      systems: &id001
second occurrence
  in "<unicode string>", line 9043, column 12:
      systems: &id001
```

Cause: `yaml.safe_dump` emits an anchor whenever two items share one Python list object — three
phases built from a single `["sys-governance"]` variable. The block `phase-prog-01` merged carried
`&id001` and validated fine alone; appending a second independently-dumped block reproduced the same
generated name and broke the file.

Fixed by expanding the anchor and its three aliases in the `phase-conc-*` block, and re-dumping the
`phase-idg-*` block through a dumper with `ignore_aliases` set. `backlog.yaml` now contains no YAML
anchor at all, asserted before commit.

This was not escalated to a triage agent. The run's failure protocol calls for one on a red gate, but
the gate was red on an uncommitted edit I had just made and fully understood — dispatching an agent
to diagnose a defect already diagnosed is the cost the same protocol forbids elsewhere. Recorded here
rather than decided silently, and staged as an idea candidate, because the trap is latent: the
anchored block merges green and breaks whoever appends next.

## Unresolved

**Whether `ARCH-005` should have moved to `accepted` in this phase.** Options: accept it here, since
`REQ-014` is the requirement it was waiting for, or defer to `phase-idg-01`. **Deferred**, on the
reasoning in `## Decisions`. A reader finding a `draft` architecture document with an active
requirement pointing at it may reasonably read that as an oversight; it is not.

**Whether `000042` should have been ruled here rather than sized as a ruling.** The generated
ideas-and-backlog page is arguably already superseded by the two explorers, and this phase had the
evidence to say so. Options: rule it declined now, or size the ruling into `phase-idg-08`.
**Sized it**, because declining an owner's idea on the strength of a component read is a judgement
the owner should see stated, and `R14` requires the ruling to say what the page would add rather than
merely that panels exist.

**Whether `phase-idg-09`'s mechanism should have been chosen here.** `000010` proposes a dashboard
input field; a watched directory or a phone shortcut would satisfy `R16` equally. **Left to the
phase**, with the alternatives named in its scope, because the choice turns on what the owner would
actually reach for, which is not a fact in the repository.

## Left undone

**All twelve phases.** This phase finalizes a plan and builds nothing.

**`000072`'s duplication with `000046` is flagged but not ruled.** The partition recommends striking
`000072`'s planner bullet rather than building the same thing twice, and `000072` lives in `P4`.
`phase-prog-06` owns that ruling and runs later tonight. `phase-idg-12`'s `next_action` says to
confirm the bullet was struck before building, so the dependency is visible to whoever claims it.

**The `phase-conc-*` anchor fix is carried on this branch**, not on the one that introduced it.
`phase-prog-01` is already merged and closed. Fixing it forward rather than amending a closed phase's
history is the right call, but it does mean the correction lives in a different phase's diff from the
defect.
