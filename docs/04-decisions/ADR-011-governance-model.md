---
schema_version: 1
id: doc-governance-model-decision
code: ADR-011
title: Governance stays a kind and a system, unmerged from operation, with no new fields
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-governance, sys-backlog]
depends_on: [doc-governance-protocol, doc-governance-model-prompt]
---

# Governance stays a kind and a system, unmerged from operation, with no new fields

## Context

[PROMPT-005](../02-prompts/PROMPT-005-governance-model-review.md) asked whether `governance` is a
document kind, a system (`sys-governance`), or both, and posed four follow-on questions: an
enforced-vs-convention field, merging `governance` with `operation`, subsystem-owned governance, and
a `governed_by` field on `systems.yaml`. [PLAN-014](../01-plans/PLAN-014-governance-and-complexity-review.md)
holds this investigation and required one ADR answering all five, with no schema written until this
ADR calls for one.

`phase-tool-01` is already blocked on question 3: it needs to know whether new per-tool documentation
uses the `operation` series before it can start.

## Decision

### 1. Kind and system are orthogonal, and the overlap costs nothing

`kind: governance` describes a document's **body shape** — rules, scope, enforcement and exceptions,
per the taxonomy table in [GOV-001](../08-governance/GOV-001-protocol.md#taxonomy-and-placement).
`sys-governance` describes an **implementation component** — the code and schemas at `src/governance`,
`schemas/document.schema.json`, `schemas/systems.schema.json`, `schemas/codes.schema.json` and the
registry files themselves, per its entry in
[systems.yaml](../08-governance/systems.yaml).

They name the same English word but answer different questions, and neither implies the other:
`GOV-003` carries `systems: [sys-backlog, sys-projection, sys-html, sys-memory-agents]` and no
`sys-governance` at all, while `GOV-001`, `GOV-005` and `GOV-006` do carry it because those documents'
rules are actually about the governance component. A `governance`-kind document is not required to
name `sys-governance`, any more than a `plan`-kind document about `sys-governance` would be required
to use `kind: governance`. Removing either the kind or the system would break something real: the
kind supplies the body-shape contract and the `decision_record` mechanism (below); the system supplies
the paths, owner and maturity tracking every other implemented component gets. Neither is redundant
with the other, so nothing is removed. The confusion this investigation was asked to test for is a
naming coincidence, not a structural one, and this ADR is the record that resolves it without a
schema change.

### 2. No enforced-vs-convention field

The question — can a reader tell whether violating a rule fails a check or only disappoints someone —
already has an answer that predates this investigation:
[GOV-001's "Enforcement and adoption boundaries" table](../08-governance/GOV-001-protocol.md#enforcement-and-adoption-boundaries)
classifies every rule category across the governance corpus into a mechanism (schema, validator,
graph check, human diff review) and a result (CI failure, warning, human decision). Individual
protocol documents already cite the actual check inline rather than asserting enforcement in prose —
GOV-002's concurrency table names `inspect_backlog` directly, OPS-001's failure table names the exact
diagnostic string a command produces. A per-document field would duplicate a distinction the corpus
already makes centrally and inline, which is exactly the "second project portfolio" GOV-001 already
warns against for `systems.yaml`. Per PROMPT-005's bias toward removal, no field is added. This is a
**leave it alone**, not an oversight — it is one of the five answers that must not be re-litigated.

### 3. `governance` and `operation` do not merge

Two independent reasons hold, and either alone would be sufficient:

**They already carry different mechanical weight.** `src/governance/backlog.py`'s
`inspect_backlog` requires `catalog["decision_record"]` to resolve to a document whose `kind` is
`governance` or `adr` — `operation` is not accepted. `GOV-003` is the live example: it is not an ADR
in form (no Context/Decision/Alternatives/Consequences structure), it is a table of accepted
questionnaire answers, but it qualifies as the backlog's decision record specifically because its
`kind` is `governance`. Merging the two kinds would either break this check or require it to accept
`operation` too, silently widening what counts as a decision record.

**They serve different readers doing different things.** Comparing the two real documents: GOV-002 is
declarative — state diagrams, field-meaning tables, `must`/`is`/`requires` language, no numbered steps
to execute. OPS-001 is imperative — numbered command blocks, a failure-diagnostic lookup table, "do
this next." A reader who wants to know *whether* something is a rule reaches for `GOV-*`; a reader who
wants to know *how* to run the check reaches for `OPS-*`. GOV-001's taxonomy table already encodes
this as two different body-requirement contracts ("Rules, scope, enforcement and exceptions" versus
"Trigger, command, expected result, failure/recovery steps"). Nothing would have been lost by using
one series for the counter and location — both already share `docs/08-governance/`, a plain counter,
and no sub-codes — but something would be lost from the body contract and from the decision-record
check, so the two-kind, two-prefix split stays.

This unblocks `phase-tool-01`: the per-tool documents it produces are trigger/command/result/recovery
shaped, which is `operation`'s existing contract exactly. It uses the `OPS` series.

### 4. Subsystems do not get their own governance concept; the existing `systems` field already is one

Tested against the concrete case PROMPT-005 names: does `sys-backlog` need rules that are not already
in `GOV-002` and `GOV-004`? No — and the reason is that `sys-backlog` **already has its own
governance**, expressed the same way every scoped document expresses it: `GOV-002` and `GOV-004` both
carry `systems: [sys-backlog, ...]` in front matter. `GOV-003` shows the same mechanism covering four
systems in one document when a decision cuts across them, and `OPS-001` shows it covering two
(`sys-governance`, `sys-delivery`) for the same reason. The `systems` field is already the
subsystem-governance concept the question is asking whether to invent. No new structure — a
per-system governance file, a new kind, a new directory — answers a question the existing field does
not already answer.

### 5. No `governed_by` field on `systems.yaml`

The reverse query — "what governs this system?" — is answerable today by reading a `systems.yaml`
entry's `paths` and cross-referencing `systems:` front matter across `docs/08-governance/`, or via
`--inventory`. A stored `governed_by` field would duplicate that direction of the same edge GOV-001
already carries the other way, and GOV-001's "Inventory without duplicate bookkeeping" section states
the standing rule directly: `systems.yaml` "is not a second project portfolio," and a generated file
may exist only when a check regenerates and diffs it. Nobody has asked the reverse question often
enough to justify a hand-maintained, driftable second copy of an edge the front matter already states.
If the query becomes common, the answer is a derived column in `--inventory` or `--catalog` output —
computed from existing `systems:` fields, never a new source-of-truth field — consistent with how the
inventory is already generated rather than committed. Per the bias toward removal, nothing is added
now.

## Alternatives considered

**Merge `governance` and `operation` into one kind with a `mode: rule|runbook` field.** Rejected: this
recreates the exact field the investigation already declined to add for a different axis
(enforced/convention), for the same reason — the split is already legible from which series a
document is in, and a field would encode in metadata what the prefix already encodes in the
filename.

**Add `governed_by` to `systems.yaml` and require it to stay in sync with front matter via a new
check.** Rejected: this is real code (a new bidirectional-consistency check) to answer a question
nobody has asked yet, which is the pattern [PLAN-014](../01-plans/PLAN-014-governance-and-complexity-review.md)
was itself opened to catch — three same-day corrections came from building structure ahead of
demonstrated need, and this would be a fourth.

**Drop `sys-governance` as a system, since governance is "just" a kind.** Rejected: `src/governance`
is real implementation code with real paths, an owner and a maturity state, identical in shape to
every other implemented component in the registry. Removing its entry would stop tracking that
component the way every other one is tracked, for a naming-coincidence reason that section 1 shows
does not hold up.

## Consequences

- `phase-tool-01` is unblocked: it uses the `OPS` series for per-tool documents, as its own scope
  bullet anticipated ("use whichever series phase-gov-02 settles on").
- No schema, field or check changes as a result of this ADR. `document.schema.json`,
  `systems.schema.json` and `backlog.schema.json` are all unchanged.
- The five questions are now on record as answered, including the three answered "leave it alone" —
  re-raising any of them should point here first rather than reopening the investigation.
- [PLAN-014](../01-plans/PLAN-014-governance-and-complexity-review.md)'s next step, PROMPT-003, can
  proceed treating the governance/operation split as settled rather than open, per the plan's own
  sequencing note.

## Revisit trigger

If a second `operation` document is written and turns out to share no structural pattern with
OPS-001 (i.e., the trigger/command/result/recovery shape does not generalize), reopen question 3 with
two real examples instead of one. If a future rule genuinely cannot be classified as CI-enforced or
human-reviewed using GOV-001's existing table, reopen question 2 with that rule as the concrete case
PROMPT-005's bias-toward-removal test requires.
