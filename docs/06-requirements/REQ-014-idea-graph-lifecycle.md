---
schema_version: 1
id: doc-idea-graph-lifecycle-requirements
code: REQ-014
title: Idea graph and lifecycle requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-25'
systems: [sys-portfolio, sys-projection, sys-governance]
depends_on: [doc-idea-node-classification, doc-idea-record-system, doc-idea-staging]
---

# Idea graph and lifecycle requirements

## Observed problem and scope

The idea log works. `_data/ideas.jsonl` is append-only, `fold()` derives current state from events,
`tools/append_idea.py` is the only sanctioned writer, and the corpus has grown past 230 ideas without
a schema change. What it does not have is structure a query can use, agents that maintain that
structure, or a defined path from a promoted idea to the governed plan it becomes.

Four gaps, each observable today.

1. **The graph is flat.** Ideas carry free-form tags nowhere and typed links only to other ideas.
   `schemas/idea.schema.json`'s link `target` is another idea id, so "this idea relates to `PLAN-001`"
   has no home but prose inside a finding annotation, where it is not queryable (`000053`). There is
   no node classification at all, so the traversal queries `ARCH-005` exists to enable — every
   *Strategic Directive* resting on an *Assumption* rather than an *Axiom* — cannot be run.
   `ARCH-005` defines the vocabulary and explicitly stops before the implementation, naming "write
   the governing REQ/PLAN" as the gate before any schema change lands. This is that requirement.

2. **Nothing maintains the graph after capture.** Links are written by whoever happens to notice a
   relationship during triage. `000055` names the consequence: a sparse or stale relationship graph
   becomes a retrieval quality problem once `P6`'s work lands, not merely a bookkeeping gap. No agent
   owns classification (`000062`) or connection-building, and `000018`'s tagging does not exist, so
   there is nothing to maintain even if an agent existed.

3. **Capture spends the context of whatever session noticed the idea.** `.claude/commands/idea.md`
   drafts the title and body inline, writes a temp file, and calls the writer — in the main session.
   `000048` and `000127` are the same ask six days apart: move the write into a subagent that returns
   only the id. The cost is paid repeatedly in exactly the sessions where context is most scarce.

4. **`promoted` names an outcome with no mechanics.** An idea's status machine ends at *became a
   plan, requirement or phase*, but nothing governed says what happens between the owner deciding an
   idea should become a plan and the coded document existing in `docs/01-plans/`. `ADR-010` covers
   staging and stops at promotion; `PLAN-015`'s `_working/` is for detail deleted when the task ends,
   which is the wrong shape for a document meant to become permanent (`000049`). `000046`'s planner
   agent is blocked on this, and `000047` observes that nothing states what makes a plan good, so
   each new plan is written by pattern-matching whichever existing one the author had open.

**`G03` is largely delivered and was verified in code before this requirement was written**, per the
phase's acceptance condition. `tools/overview_metrics.py` implements `000071`'s delivered metric set — funnel
counts and rates, cycle time between statuses, annotation coverage, link-type distribution and
orphan count, throughput, age of open ideas, and backlog phase counts — reading through `load_events()`
and `fold()` rather than parsing the log by hand. `ts/src/stage/IdeaExplorerRegion.tsx` and
`BacklogExplorerRegion.tsx` render both queues against `/api/v1/workbench/ideas`, `/ideas/queue`,
`/backlog` and `/backlog/queue` with a standard/priority toggle. The `orient` skill answers `000071`'s
second half. What remains of `G03` is small and is stated in rows R13 and R14; the rest of the group
gets no implementation phase, and `000050` is an umbrella that gets none either.

This requirement covers the idea graph and lifecycle programme (`P1`): node classification and the
schema that carries it, the agents that assign and maintain it, tagging, the decomposition procedure,
subagent capture, the remaining reporting gap, and the promoted-idea-to-plan path. It does **not**
cover retrieval over the graph — that is `P6` ([PLAN-033](../01-plans/PLAN-033-retrieval-knowledge-infrastructure.md)).
The boundary is that `P1` produces the structure and `P6` queries it.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | `schemas/idea.schema.json` carries the classification from `ARCH-005` — a record kind and the four axes, ontological, epistemic, lifecycle and temporal — as distinct fields, not as tag values. | Read the schema for a record-kind field and four named axis fields with enumerated values matching `ARCH-005`. Confirm a classification written as a tag is rejected by validation rather than silently accepted. |
| R02 | A classification of a knowledge record carries one value on each of the four axes, and the epistemic axis may be Not Applicable / Agnostic; a `collection`, `fixture` or `reference` record carries its record kind and no axis values; a reason is kept for each axis value (owner ruling C1, 2026-09-24, in `ARCH-005`). | Validate a knowledge-record classification with one axis absent and confirm it is rejected. Validate one with the epistemic axis set to Not Applicable and confirm it passes. Validate a `collection` record carrying an axis value and confirm it is rejected. Confirm every axis value carries a reason. |
| R03 | Classification coverage across the corpus is measurable as a number, per axis. | Run the metrics tool and read a per-axis coverage figure. A taxonomy whose coverage cannot be stated cannot be known to be worth its cost. |
| R04 | A link may target a governed document code as well as another idea, and the two target shapes are distinguishable without parsing the value. | Write a link targeting a `PLAN-` code through the sanctioned writer and read it back through `fold()`. Confirm the target shape is explicit in the record. Confirm a link to a document code that does not exist is rejected. |
| R05 | The `component_of` link type and the `lineage` annotation kind both exist and are written only through `tools/append_idea.py`. | Write one of each and read both back through `fold()`. Confirm `lineage` is restricted to the owner's voice, as `note` and `assessment` already are — an agent author attempting it is rejected, per the writer's existing author rule. |
| R06 | Every schema addition in R01, R04 and R05 lands in one change, and `fold()`, the writer and the schema stay consistent across it. | Confirm one commit touches `schemas/idea.schema.json`, `src/db/ideas.py` and `tools/append_idea.py` together. Run the full suite. `ARCH-005` bundles these precisely to avoid re-touching the same three files four times. |
| R07 | Every idea written before the schema change is readable unchanged, and no existing event is rewritten. | Re-read the pre-change corpus through `fold()` after the change and confirm identical derived state for every idea. Confirm `_data/ideas.jsonl`'s existing lines are byte-identical — the log is append-only, and a backfill that edits history has broken it. |
| R08 | A classification agent assigns a record kind and values on the `ARCH-005` axes for one idea at a time, reading that idea in isolation, and writes neither tags nor links. | Run it against one idea and inspect the events it wrote. Any tag or link event is a defect. Confirm it does not read the idea's neighbours — `000062` makes isolation the point, so a classification biased by what an idea sits next to fails this row. |
| R09 | The existing corpus is backfilled, and the proportion left unclassified is reported rather than assumed to be zero. | Run the backfill and read the coverage figure from R03 before and after. Confirm ideas the agent declined to classify are listed with reasons, not silently skipped. |
| R10 | Tags exist as a registry with a controlled vocabulary, assignable retroactively through the sanctioned writer, and queryable. | Add a tag to an existing idea and query for it. Confirm the vocabulary is a registry file rather than free text, as `_data/tags.json` already is for projects. Confirm an unregistered tag is rejected. |
| R11 | A connection-builder agent maintains links and tags across ideas of every status, including revisiting ideas already past `open`. | Run it and confirm it writes links to at least one `triaged` or `promoted` idea. An agent that only touches `open` ideas is the triage agent, which already exists; this row distinguishes them. |
| R12 | A decomposition procedure exists for a compound idea, and running it leaves the original idea intact with `component_of` links to its parts. | Run it against a compound idea. Confirm each fragment is checked against the existing corpus before a new idea is written, and that an existing matching idea is linked rather than duplicated. |
| R13 | Idea metrics are reachable as a command, not only as a tool invocation. | Run the command and confirm it reports the metric set `tools/overview_metrics.py` already computes. This is the remaining half of `000071`; the tool is delivered and verified. |
| R14 | The question of whether a generated ideas-and-backlog HTML page is still wanted is ruled on, given both explorers now ship in the workbench. | Read the ruling. Confirm it states what the generated page would add over `IdeaExplorerRegion` and `BacklogExplorerRegion`, and either sizes it or declines it. Carrying `000042` forward unruled is the defect. |
| R15 | Capture through `/idea` runs in a subagent, and the main session receives the created ids and nothing else. | Capture an idea and confirm the main session's transcript carries the ids without the file churn or the writer's output. Confirm the subagent still obeys the sanctioned-writer rule and never edits `_data/ideas.jsonl` directly. |
| R16 | An idea can be captured without a session open. | Capture one through whatever mechanism is chosen and confirm it lands in the log with a valid id. `000010` names this as the part that changes behaviour most: today an idea is recorded only if a session happens to be running, which silently filters for ideas that occur at a keyboard. |
| R17 | A written standard states what makes a plan document good — which sections earn their place, what tone, and what distinguishes the dense plans from the thin ones — derived from the existing corpus rather than asserted. | Read the standard for named examples from `docs/01-plans/` on both sides of each judgement. A standard citing no actual plan has not used the corpus it was meant to audit. |
| R18 | Where a promoted plan or requirement lives before it earns a code is defined, and the definition is reachable from `ADR-010`, which currently stops at promotion. | Read the definition for the location, and for what happens if the draft is abandoned. Confirm `ADR-010` or its successor points at it. |
| R19 | A planner agent drafts a governed plan from a promoted idea, and the draft carries what triage already found rather than rediscovering it. | Run it against a promoted idea with existing findings and links. Confirm the draft cites them. Confirm the agent drafts and does not decide — it allocates no code and marks nothing promoted, mirroring the triage agent's boundary. |
| R20 | A plan drafted by R19's agent is measurably conformant to R17's standard. | Check the draft against the standard's own named sections. A standard nothing is checked against is prose; this row is what makes R17 load-bearing. |
| R21 | Ideas whose work demonstrably shipped are closed into `delivered`, `resolved` or `absorbed` by appending events, each close carrying a pointer that resolves, and `000099` and `000129` move from `discarded` to `resolved` through a revisit followed by a status move. | Fold the log and confirm every close written by the backfill carries a pointer to an existing document code, backlog phase id or commit hash. Confirm a close citing a pointer that does not resolve is rejected. Confirm `000099` and `000129` fold to `resolved` through a `revisited` event and then a `status` event, and that `_data/ideas.jsonl`'s existing lines are byte-identical. Scope and reasoning: `GOV-003`, 2026-09-22 lifecycle ruling. |
| R22 | An agent-written terminal-state close is distinguishable from an owner-ratified one through a `proposed_by` field, is verified by a second agent before it counts as ratified, and blocks no downstream work while it waits. | Write an agent-proposed close and read it back through `fold()`. Confirm it is marked as agent-written and pending ratification, and that the pending set is derivable from the log alone. Confirm a close missing the verification step stays marked as agent-written. Scope and reasoning: `GOV-003`, 2026-09-22 lifecycle ruling and the 2026-09-23 batch-003 entry. |
| R23 | The owner can set an idea aside at a partition without discarding it: a non-terminal idea status reachable from `triaged` that can return to `triaged` or `reviewing`, and a hold-out field in the partition record that records the owner's hold-out as such rather than as an unbatched reason. | Move a `triaged` idea to the new status and back through the sanctioned writer, and confirm the writer rejects it from any other status. Validate a partition record carrying a hold-out in the new field, and confirm the accepted 2026-09-23 partition record still validates. Scope: idea `000417`, owner ruling 2026-09-24. |

## What each requirement is not

**R02's Not Applicable is not a default.** Not Applicable / Agnostic is for a record that asserts no
verifiable truth claim, and is available on the epistemic axis only; it is not a value for a record
nobody has examined. R03 and R09 exist so that coverage is a measured number rather than an
impression.

**R07 is not a general backfill rule.** It is specifically the append-only invariant: backfilling
classification means appending classification events, never rewriting the lines already written. A
backfill implemented as a file edit satisfies R09 and breaks the log.

**R14 may be satisfied by declining.** The row requires a ruling, not a page. If the workbench
explorers make the generated page redundant, saying so and closing `000042` satisfies it.

**R16 does not prescribe the mechanism.** `000010` proposes an input field on a dashboard; a watched
directory, an email drop or a phone shortcut would satisfy the observable equally. The row fixes the
behaviour, not the surface.
