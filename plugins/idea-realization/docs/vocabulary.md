# Idea vocabulary

Every value the idea log accepts, and what each one means. The schema
(`schemas/idea.schema.json`) is the machine statement; this document is the readable one.
`test/test_vocabulary.py` compares every table below with the schema, so a value added to one
and not the other fails the plugin's tests.

In each table, the first column holds the value exactly as the log stores it.

## Statuses

An idea is created `open`. Status moves only forward, by a `status` event the writer appends.

| Status | Meaning | Terminal |
|---|---|---|
| `open` | Captured; nothing has looked at it. | no |
| `triaged` | Scouting finished, a finding is attached; awaiting the owner. | no |
| `reviewing` | The owner is actively considering it. | no |
| `promoted` | Became a plan, requirement or phase, named in `promoted_to`. In flight, not finished: it moves on to `delivered` when that work ships. | no |
| `discarded` | Rejected. Terminal unless revisited, which is permitted once. | yes, except for one revisit |
| `delivered` | A working capability exists and was verified. Needs a `closes_with` pointer. | yes |
| `resolved` | The ask was satisfied without building anything. Needs a `closes_with` pointer. | yes |
| `absorbed` | The substance was folded into another document that now carries it. Needs a `closes_with` pointer. | yes |

## Transitions

Every legal `status` move. Anything not listed is refused by the writer and by the fold.
`discarded`, `delivered`, `resolved` and `absorbed` are never a `from`. The one way out of
`discarded` is a `revisited` event, which returns the idea to `reviewing` and is permitted once per
idea; a second discard after that revisit is permanent.

| From | To | Requires |
|---|---|---|
| `open` | `triaged` | — |
| `open` | `reviewing` | — |
| `open` | `promoted` | `promoted_to` |
| `open` | `discarded` | — |
| `open` | `delivered` | `closes_with` |
| `open` | `resolved` | `closes_with` |
| `open` | `absorbed` | `closes_with` |
| `triaged` | `reviewing` | — |
| `triaged` | `promoted` | `promoted_to` |
| `triaged` | `discarded` | — |
| `triaged` | `delivered` | `closes_with` |
| `triaged` | `resolved` | `closes_with` |
| `triaged` | `absorbed` | `closes_with` |
| `reviewing` | `promoted` | `promoted_to` |
| `reviewing` | `discarded` | — |
| `reviewing` | `delivered` | `closes_with` |
| `reviewing` | `resolved` | `closes_with` |
| `reviewing` | `absorbed` | `closes_with` |
| `promoted` | `delivered` | `closes_with` |

A `closes_with` pointer names where the delivery happened: exactly one of `doc` (a governed
document code), `phase` (a backlog phase id) or `commit` (a commit hash). The writer refuses a
pointer that does not resolve.

## Event kinds

Each line of the log is one event. Nothing is ever edited or removed.

| Event | Meaning |
|---|---|
| `created` | The idea was captured, with its title and body. |
| `status` | Its status moved, from the status it had reached to a legal next one. |
| `revisited` | A discarded idea was reopened, returning it to `reviewing`. Once per idea. |
| `amended` | A prior event's field was corrected without rewriting it: a title, a body, an annotation's text, or a link's target retracted. |
| `annotated` | A note, finding, assessment or lineage was added. Permitted on every idea, terminal included. |
| `linked` | A typed edge to another idea, or to a governed document, was asserted. |
| `classified` | The idea's record kind and axis values were assigned. The latest one wins. |

## Annotation kinds

The owner is the author `repository-owner`. Every other author is an agent, and an agent may
write only a `finding`, so the owner's own voice in the log stays unambiguous.

| Kind | Meaning | Who may write it |
|---|---|---|
| `note` | The owner thinking aloud. | owner only |
| `finding` | What a triage agent found. | owner or agent |
| `assessment` | A judgement, itself correctable by a later assessment without either being deleted. | owner only |
| `lineage` | How the owner arrived at this idea, such as the compound idea it was pulled out of. Structurally inert, never a link. | owner only |

## Link types

A link is stored once, on the idea that asserts it. Its inverse is derived when the log is folded
and never stored, so the two halves cannot disagree. A link never changes its target; the one
legal amendment retracts it.

| Type | Inverse | Meaning | May point at a document |
|---|---|---|---|
| `extends` | `extended_by` | This idea builds on the target. | yes |
| `supersedes` | `superseded_by` | This idea replaces the target. It does not discard the target; that is a separate status event. | no |
| `relates_to` | `relates_to` | A symmetric relationship, its own inverse. | yes |
| `component_of` | `has_component` | This atomic idea functions within the target compound idea. Many-to-many. | no |

Two link shapes are reported when the log is folded, never refused: an `extends` cycle, and a
`supersedes` edge whose target is not `discarded`.

## Classification

A `classified` event records what kind of record an idea is and, for a knowledge record, one
value on each of four independent axes. Each axis value carries a reason and a confidence from 0
to 1. Discarding and superseding are dispositions of the idea, not axis values: a discarded or
superseded idea keeps its own axis values.

### Record kinds

Decided before any axis. Only a `knowledge` record carries axis values; the others carry none,
because their job is to group, test or point at other records rather than to state a claim.

| Record kind | Meaning |
|---|---|
| `knowledge` | States, asks for, or records something about the domain. |
| `collection` | Exists to group other records: an anchor, umbrella or shared parent, or a body that is mainly a list of other records. A record that bundles several findings of its own is `knowledge` with `decompose` set, not a collection. |
| `fixture` | Test or rehearsal data with no domain content. |
| `reference` | A pointer to an external source kept for later, with no claim or ask of its own. |

### Ontological axis

What kind of thing the record's subject is: the thing its observation is about, or that its ask
would change.

| Value | Meaning |
|---|---|
| `concept` | Concept / Mental Model: a theoretical construct, principle, paradigm or classification. |
| `artifact` | Artifact / Entity: a concrete output or entity — a file, schema, tool, system, dataset or commit. |
| `process` | Process / Workflow: a sequence of steps — how something is done, who does what, in what order. |
| `event` | Event: a distinct occurrence in time, as the subject itself. |
| `actor` | Actor / Agent: who acts — a human role, stakeholder group or autonomous agent, with its remit and authority. An agent type is an actor, not an artifact. |
| `metric` | Metric / Standard: a quantitative measure or threshold that governs something — a service level, indicator, benchmark, budget or cap. |

### Epistemic axis

How far what the record asserts can currently be relied on.

| Value | Meaning |
|---|---|
| `axiom` | Axiom / Ground Truth: a claim accepted as verified within its stated scope. |
| `hypothesis` | Hypothesis / Assumption: an untested theory, prediction or premise that needs validation before anything is built on it. |
| `anti_pattern` | Anti-Pattern / Falsified Concept: a disproven theory, failed approach or known dead end, kept so the mistake is not repeated. |
| `not_applicable` | Not Applicable / Agnostic: the record asserts no verifiable claim — an ask, a proposal, an instruction, a question, or a named thing with nothing claimed about it. Never a stand-in for an unexamined record. |

### Lifecycle axis

Where the record sits between raw thought and executed, reviewed work, or outside that arc.

| Value | Meaning |
|---|---|
| `generative_seed` | Generative Seed: a raw or developing idea, before owner commitment. |
| `strategic_directive` | Strategic Directive: a committed goal or plan that sets a direction. |
| `operational_task` | Operational Task: one executable action with a clear done-state. |
| `retrospective_insight` | Retrospective Insight: a post-execution observation — a gap, technical debt, or newly realised context. Carries a lifecycle remedy. |
| `active` | Active / Evergreen: a standing record in force outside execution — a policy, principle, master data or reference kept current. |
| `deprecated` | Deprecated / Archived: the record's subject has been retired or superseded, and the record is kept for audit. Describes the subject, never the idea record's own disposition. |

### Lifecycle remedy

Present exactly when the lifecycle value is `retrospective_insight`. It marks how the record could
be split, not a second lifecycle value.

| Value | Meaning |
|---|---|
| `operational_task` | The record names one concrete fix. |
| `generative_seed` | The remedy is left open. |

### Temporal axis

Whether what the record states is bound to a time.

| Value | Meaning |
|---|---|
| `as_of` | True of a point or interval: a state at a commit, a count on a date, a condition later work changes. A later change makes it untrue without falsifying it. |
| `standing` | True or relevant without a time bound: a principle, a want, a standing rule. |

### Decompose

`decompose: true` marks a knowledge record that bundles several unrelated findings of its own
(rule O6). It is still classified as one record; the marker flags it for decomposition rather than
splitting it at classification time. Absent reads as false.

### Tie-break rules

Applied when more than one value seems to fit, and recorded by id in the classification's
`tie_breaks`. Order: the record kind is decided first; L3 is applied before L1; E4 overrides E1.

| Rule | Axis | Rule text |
|---|---|---|
| `O1` | ontological | Artifact vs Process. Editing a file, schema, code or data is Artifact. Changing steps, their order or who performs them is Process, even when the steps live in a file. If the title names both, pick the thing the record's observation measures or counts; if nothing is measured, Process. |
| `O2` | ontological | Actor vs Artifact. An agent type and its remit or definition are Actor / Agent. Tooling that generates, indexes or lists agent files is Artifact. |
| `O3` | ontological | Metric vs Artifact or Process. Metric / Standard only when the number or threshold is the subject. The tool that computes it, or the step that checks it, is Artifact or Process. |
| `O4` | ontological | Event. An incident that evidences a lasting defect is evidence, not the subject. Classify the defective thing. |
| `O5` | ontological | Actor vs Process. Adding, removing or re-scoping a role is Actor / Agent. Changing an existing role's steps is Process. |
| `O6` | ontological | A bundle of unrelated findings. The record is `knowledge` with `decompose` set. Its ontological value is the value its parts share, otherwise the value of the first finding named in the title. |
| `E1` | epistemic | The record's point. Classify what the record asks or asserts as its point, using the title as the proxy. A defect, count or fact in the title is Axiom. An imperative, proposal or question is Not Applicable. |
| `E2` | epistemic | A verified symptom with a guessed cause. Axiom; the reason names the guessed part. |
| `E3` | epistemic | Scope and time. An Axiom verified at a point in time stays an Axiom, and the temporal axis carries its time bound. A fixed defect was never falsified. |
| `E4` | epistemic | An Insight asserts its observation. If the lifecycle value is Retrospective Insight, the epistemic value is Axiom, or Hypothesis when the observation itself is hedged. Overrides E1. |
| `L1` | lifecycle | Seed vs Directive. Strategic Directive requires evidence of owner commitment in the record: a ruling, a promotion, "we will", "must", or a relayed owner imperative to produce a named deliverable. An imperative to investigate or explore is not commitment. |
| `L2` | lifecycle | Seed vs Task. Operational Task is one action with a checkable done-state and no open choice. If the record lists options or questions, it is a Generative Seed. |
| `L3` | lifecycle | Directive vs Evergreen, applied before L1. A standing rule ("every", "always", "from now on", "must" applied to all future cases) is Active / Evergreen. "Build X" is a Strategic Directive. |
| `L4` | lifecycle | An observation with a remedy. The lifecycle value is Retrospective Insight, and the lifecycle remedy is Operational Task or Generative Seed. |
| `L5` | lifecycle | Deprecated. Only when the record's subject is retired or superseded. A record about something stale that is still in use is a Retrospective Insight. |
