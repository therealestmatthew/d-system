---
schema_version: 1
id: doc-session-2026-09-06-08
code: SESS-2026-09-06-08
title: Complete the cadence rename and track the new course project
kind: session
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-projection, sys-backlog, sys-course, sys-portfolio, sys-brain]
depends_on: [doc-record-types, doc-ephemeral-working-plans, doc-terminology-system,
  doc-tooling-documentation, doc-governance-model]
---

# Complete the cadence rename and track the new course project

## What happened

A long conversational session on git internals produced course material, which then had to be tracked
like any other work. Doing that surfaced an unfinished rename and a structural limit in the backlog.

## The cadence rename — correcting my own account

The owner said the `commitment_cadence` → `review_cadence` change was mine and should have been
documented. **Half of that is right, and the half that is wrong is worth stating precisely, because
the record is better than my summary of it suggested.**

The change was decided and documented, in more places than one:

- [ADR-008](../04-decisions/ADR-008-record-types.md) §4 records the rename, its vocabulary, the
  retirement of `ongoing`, and — under alternatives — that *dropping the field entirely was
  **rejected***, because without a declared rhythm staleness has no threshold.
- `phase-cap-02` carried the rename in scope and is complete. Its scope ends with the explicit line
  **"No DDL, loader or application code changes in this phase."** The DDL was left alone by design,
  not by oversight.
- Three session records ([-02](SESS-2026-09-06-02-structure-content-boundary.md),
  [-04](SESS-2026-09-06-04-entity-contracts.md), [-05](SESS-2026-09-06-05-source-preflight.md))
  discuss it, and [-06](SESS-2026-09-06-06-session-close.md) carried the column divergence forward
  explicitly.

So the decision was recorded, and the phrase "remove `commitment_cadence` entirely" is accurate about
the **name** but not the **field** — the concept survives as `review_cadence`, and ADR-008 rejected
removing it.

**What was actually wrong was mine.** The commit message introducing the divergence described it as
"already carried forward from an earlier session, unchanged by this commit and still owed a fix" —
vague, uncited, and it implied an orphaned defect rather than a deliberate scope boundary with an ADR
behind it. Had that message named ADR-008 and `phase-cap-02`, the question would not have arisen.

### The real defect

`tools/rebuild_db.py` carried the comment *"Column is still named commitment_cadence; phase-cap-07
renames it."* **`phase-cap-07`'s scope contains no such bullet.** The comment pointed at a phase that
did not own the work, so the DDL rename was genuinely unowned — findable only by reading a code
comment that was wrong.

### What was changed

- `sql/001_schema.sql` — column renamed to `review_cadence`.
- `tools/rebuild_db.py` — stale comment removed; the read was already correct.

Verified by rebuild: `commitment_cadence` is absent from `information_schema`, and the new course project reads
back `weekly`. Full suite: **265 passed**. Governance exits 0.

Two references to the old name remain and are **correct to keep**:

- `test/test_schemas.py:171` — `test_old_cadence_field_name_is_rejected` asserts the old name fails
  validation. It is the guard for the rename.
- `backlog.yaml:2112` — inside completed `phase-cap-02`, a historical record of what that phase did.
  Its own scope says historical records keep the name they were written with.

Done at the owner's direction outside queue order. No phase owned it.

## The course is now tracked

The new project's record captures it — category `personal`, type `project`, cadence weekly.

Backlog entry required more. Every item must carry `plan`, `sources`, `systems`, `verification` and
`deliverables`, so queueing course work meant creating the governance around it:

- `sys-course` added to `systems.yaml`, domain `delivery`. It is a **separate product sharing this
  repository** — the application's React UI and the course's animation components have nothing in
  common but the language.
- PLAN-011 written as a course *production* plan.
- `phase-course-01` (animation primitives) and `phase-course-02` (reachability lessons) queued at
  priority 4, deliberately **not** added to `next_up`.

## Finding: the backlog cannot hold personal action items

The owner asked whether the backlog should cover personal to-dos or whether a separate object is
needed. The schema answers it.

`schemas/backlog.schema.json` requires `plan`, `sources`, `systems`, `session_budget`, `verification`
and `deliverables` on **every** item. A personal action — "book a microphone", "review the lesson 4
script" — can satisfy none of those without inventing a plan and a system to hang it from. Adding the
course took a new system entry and a new plan document precisely because of this.

**The backlog is for agent work against governed plans. It is the wrong instrument for personal
work.**

The right instrument is already designed and not yet built. `schemas/task.schema.json` exists and
requires only `id`, `description`, `status` and `created`, with `commitment_id`, `project_id`,
`due_date`, `priority` and `tags` optional — a task needs no plan and no system. But `_data/tasks/`
does not exist; `phase-cap-07` scope carries *"Load tasks from `_data/tasks/` instead of unpacking
them from commitment JSON."*

So personal action items belong in `_data/tasks/`, parented to a project where one applies, and the
store arrives with `phase-cap-07`. **No new object type is needed.** Recorded as a finding rather than
an ADR because the owner has not decided, and the decision may not be needed — the existing design
already covers it.

## Carried forward

- `_data/tasks/` does not exist yet, so personal action items have nowhere to live until
  `phase-cap-07` lands. That phase is queued at priority 2 and not in `next_up`.
- `phase-cap-07`'s scope should gain an explicit bullet for anything else the removed code comment
  implied it owned. This session removed the comment; nobody has audited what else pointed at that
  phase incorrectly.
- Course distribution, narration and the interactive inspector are all undecided, per PLAN-011.
- `next_up` changed repeatedly during this session. The final order is recorded in the fourth
  amendment below; do not trust this section's earlier statement of it.

## Amendment — 2026-09-06, same day

The owner identified this session's course tracking as scope creep, and was right.
`docs/01-plans/` holds plans for building *this* system; a plan for producing a separate product
does not belong here, and neither do its build phases.

This record already noted that queueing course work forced a system entry and a plan document into
existence. It read that as a cost. It was a signal — the schema resisted because the work was not
repository work.

`PLAN-011` became an extraction plan and then, on a second correction, the governed policy for
[ephemeral working plans](../01-plans/PLAN-015-ephemeral-working-plans.md) — the extraction detail
moved to `_working/`, since it describes a one-off task rather than how the system works.
`phase-course-01` and
`phase-course-02` are removed, and `phase-scope-01` now sits at the front of `next_up`. The
generalised version of the failure is
[PROMPT-003](../02-prompts/PROMPT-003-systems-review.md).

## Second amendment — vocabulary as the root cause

Three scope-creep corrections happened in one day: a course production plan, then a course extraction
plan, then the plan/ephemeral distinction. The owner's read is that they share a root cause, and the
evidence supports it — **no shared definition of what a plan is**, so each judgement was re-derived
from scratch and reached a different answer. Vocabulary is not documentation overhead here; its
absence has a measured cost.

[PLAN-012](../01-plans/PLAN-012-terminology-system.md) establishes the system:
definitions canonical in `brain/`, glossaries **generated** by a deterministic script so there is one
source of truth rather than two copies that drift, and stated rules for when a term enters, retires
and is reviewed. [PROMPT-004](../02-prompts/PROMPT-004-terminology-and-architecture.md) writes the
content. `phase-term-01` and `phase-term-02` head `next_up`, ahead of the course extraction.

### Two findings that redirected the brain proposal

The owner proposed reorganising `brain/` into a folder per subsystem for agent queryability. Both
halves turned out not to hold:

- **Governance enforces type-first.** `src/governance/__main__.py:226` computes
  `brain/{MEMORY_DIRS[type]}/` and errors on anything elsewhere. Subsystem folders would require
  rewriting that rule.
- **Folders do nothing for retrieval.** `tools/load_context.py` filters on query, project, type, tags
  and limit, and **never reads the path**. The restructure would have broken a rule to gain nothing.

The want behind it was real and is genuinely unsupported: `project` validates against project IDs and
`tags` against `_data/tags.json`, so neither can hold a `sys-*` identifier. The fix is a `systems`
field on the memory schema plus a `--system` filter — surgical, and it delivers what the folder move
was reaching for. That is `phase-term-01`.

### Sequencing

Documentation precedes the systems review. The apparent circularity resolves once the two mandates
are separated: PROMPT-004 describes what **is**, PROMPT-003 decides what **should be**. The review is
expected to prune or consolidate some of what gets documented, and that is the sequence working.

### Ordering left for the owner

`phase-term-01` and `-02` now sit ahead of `phase-scope-01`, so the course extraction has moved
back one place. Both were called top priority at different points in the same session; the terminology
work was named more recently and blocks less. Reorderable in one edit if that reads wrong.

## Third amendment — governance, tooling, and the fourth instance

The owner asked for governance and tooling to be documented alongside vocabulary and architecture,
and asked whether governance merits its own schema.

**Governance already scopes to subsystems.** `GOV-002` and `GOV-004` carry `sys-backlog`;
`GOV-001`, `GOV-005` and `GOV-006` carry `sys-governance`. The general-versus-subsystem distinction
the question was reaching for exists and is in use, so no schema is needed to express it. Whether
governance needs fields the other kinds lack is a separate and open question —
[PROMPT-005](../02-prompts/PROMPT-005-governance-model-review.md) investigates it, hosted by
[PLAN-014](../01-plans/PLAN-014-governance-and-complexity-review.md).

**Tooling gets one operations document per tool**, not one shared document. The single-document
recommendation was made without knowing the tool count is about to multiply — front-matter
validation, drift detection and a family of generators are designed and unintegrated. At three tools
a shared document is lighter; at eight to ten it becomes a file everyone edits and nobody owns.
[PLAN-013](../01-plans/PLAN-013-tooling-documentation.md) records the decision, generates the
mechanical reference from docstrings, and **defers drift enforcement** at the owner's direction, with
the signature-hash approach noted for later and the whole-file hash rejected in advance as a check
that would always fire.

**Prompts describe; plans build.** `PROMPT-004` gains Parts 3b and 3c documenting governance and
tooling **as they exist**, explicitly barred from redesigning either. Redesign belongs to `PROMPT-005`
and `PLAN-013`.

### The fourth instance of the same pressure

`phase-gov-02` could not enter the backlog without a plan document, because every phase must name a
document of kind `plan`. `PLAN-014` was therefore written to satisfy a schema rather than to record a
decision — its own text says so.

This is the fourth time in one day that the plan requirement manufactured a document: course
production, course extraction, the governed/ephemeral split, and now this. The first three were
foreign work pushing in from outside. This one is internal and arguably legitimate, which makes it
the cleanest data point — the requirement is simultaneously keeping the backlog anchored and
generating paperwork. `PROMPT-003` should weigh both with these four instances in hand.

### Queue

`phase-scope-01` moves to first at the owner's direction: it is small, blocks nothing, and shrinks
the repository before the documentation sessions describe it. Full order is
`scope-01`, `term-01`, `term-02`, `tool-01`, `gov-02`, then the pre-existing queue.

## Fourth amendment — adversarial review, and what it found

A third-party agent reviewed this work with no knowledge of the conversation. It returned 21
findings. Every claim below was re-verified before acting on it.

### Three defects that would have broken the next session

**`phase-scope-01` ordered the deletion of its own parent plan.** The phase text was written when
`PLAN-011` was the course extraction plan. When that document was rewritten as the ephemeral-plan
policy, the phase's `plan:` field was re-anchored and its **scope and acceptance text were not**. The
first phase in the queue instructed a fresh agent to delete the standing policy, and its acceptance —
"governance exits 0 with PLAN-011 removed" — was unsatisfiable, because `backlog.py:119-125` errors
on any phase whose plan is missing. Fixed.

**A document code was reused three times in one day.** `PLAN-011` was issued to the course production
plan, then the extraction plan, then the ephemeral-plan policy, with `retired: []` throughout.
[GOV-005](../08-governance/GOV-005-document-codes.md) lines 72 and 77 forbid exactly this: a code
reaching `dev` is never reused, and a deleted document's code is recorded under `retired`. The
violation was narrated in this very record and never checked against the protocol. `PLAN-011` is now
retired with its reason, and the policy document carries `PLAN-015`.

**`phase-term-01` could not meet its own acceptance.** It promised a `--system` filter on
`load_context.py`, which queries DuckDB — and `sql/001_schema.sql` has no `systems` column on
`memories`, while `rebuild_db.py` inserts thirteen positional values. It also promised validation
against `systems.yaml`, which JSON Schema cannot reach. Four required files sat outside its
deliverables, which under `AGENTS.md:166-168` would have forced the boundary violation the
concurrency protocol exists to prevent. Scope, systems and deliverables corrected.

### A claim of mine that was simply wrong

I told the owner that reorganising `brain/` into per-subsystem folders would break governance, citing
`__main__.py:226`, and hardened that into a prohibition in `PROMPT-004`. **It is a `startswith`
prefix test and `markdown_paths` recurses.** `brain/concepts/sys-backlog/terms.md` passes today —
verified by creating that file and running the check, which exited 0.

The owner's proposal was viable and was overridden on a false claim. The decision to prefer a
`systems` field still stands, but on the second reason alone: folders answer subsystem retrieval by
convention while a field answers it directly. The prohibition is withdrawn.

### The irony finding, which is fair

The review observed that work whose purpose is preventing scope creep added 1,207 lines across 13
documents, 4 plans, 3 prompts and 5 phases, and changed **zero lines of executable code** — while
`PROMPT-003`, the review that would prune all of it, had **no plan, no phase and no queue slot**. A
plan had been manufactured to schedule the *narrow* governance review and not the broad one.

`PLAN-014` now hosts both and is broadened accordingly, which removes the circularity the review
identified in its first draft. `phase-gov-03` schedules `PROMPT-003`.

### Other corrections

- `PROMPT-003` said fifteen systems (there are 16), named six tracks (there are 13), and attached
  "derived and gitignored" to `rebuild_db.py` rather than the database.
- The governance-scoping table omitted `GOV-003` — a governance document carrying four systems and
  no `sys-governance` scope, which is the case any proposal must handle — and misdescribed `GOV-002`
  as scoping to `sys-backlog` when it carries both.
- `phase-tool-01` would have minted permanent `OPS-*` codes before `phase-gov-02` decides whether
  that series should exist. It now depends on `phase-gov-02`, which runs first.
- The `_working/` policy existed only in its own plan. `AGENTS.md` never mentioned the directory and
  `CLAUDE.md` still called it a scratchpad — so the next agent facing "governed or ephemeral?" would
  have re-derived the answer, the exact failure the policy was written to stop. Both now carry it.
- Two tests asserted exact allocator arithmetic while reading the live `codes.yaml`, so retiring any
  `PLAN-*` code broke them. A hermetic fixture was added; live-register coverage is unchanged.

### Deferred, not fixed

Findings 12, 16, 17, 18, 19, 20 and 21 — directory-level deliverables weakening the concurrency lock,
the absence of requirement documents and ADRs for this work, unverifiable acceptance criteria, and
the undecided glossary series — are recorded here and left for `phase-gov-03`. They are real. Fixing
them in the same session that produced them would repeat the pattern the review criticised.

### Final queue

`scope-01`, `term-01`, `term-02`, `gov-02`, `tool-01`, `gov-03`, then `cap-03`, `rel-11`, `cap-07`,
`priv-02`, `ses-01`. `phase-tool-02` — generalising the tooling for reuse across repositories — is
queued at priority 4 and deliberately not in `next_up`.

## Fifth amendment — a staging area for ideas

The owner asked whether anywhere holds one-off to-dos and plan ideas that are not ready to become
plans — "the plans for the plans". The answer was almost yes.

`docs/00-working/` already existed and already held `codex-answers.md`, exempted from the audit **by
exact filename**. So it was a staging area for exactly one file; any second file would have failed
the check. The exemption is now directory-level via `EXEMPT_DIRS`, recorded in
[ADR-010](../04-decisions/ADR-010-idea-staging.md).

This is not new structure so much as an escape valve for the pressure that has been generating it.
Four documents were manufactured on 2026-09-06 because there was nowhere to put an idea that was not
yet a plan: the course production plan, the course extraction plan, and the first drafts of
`PLAN-015` and `PLAN-014` — the last of which admitted in its own text that it existed only to
satisfy a schema. Parking an idea now costs nothing and commits to nothing.

Alternatives were rejected for stated reasons. `status: deferred` phases defer scheduling but not the
schema. `brain/` holds knowledge that is true and retrieved as agent context; speculation there
degrades retrieval. A new top-level folder to hold things that prevent unnecessary structure would
have been its own joke.

The one rule is that an entry graduates into a plan, requirement or phase, or is deleted. Pruning
happens during the systems review. `test_idea_staging_directory_is_ungoverned` asserts the directory
stays exempt so a later refactor cannot quietly re-govern it, and both `AGENTS.md` and `CLAUDE.md`
now point at it — the propagation step whose absence the adversarial review called the most
consequential omission last time.

**First entry parked:** test fixtures for the HTML generation system. Fixtures have to be created,
kept in step with the templates and data shapes they stand for, and pruned when those change — the
maintenance cost that gets discovered late. Open questions noted: whether fixtures are generated from
`_data/` or hand-authored, whether a fixture is a governed artifact or a test asset, and how a schema
change invalidates one. Related to [PLAN-003](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003-overview.md),
which is approved and unbuilt. Nothing to do until it is.

## Sixth amendment — session close

### The staging list is append-only

At the owner's direction, `docs/00-working/ideas.md` is **append-only**. New entries go at the
bottom; the only permitted edit to an existing entry is its `Status` line — `open`, `investigating`,
`promoted`, `discarded`.

The reasoning, recorded in [ADR-010](../04-decisions/ADR-010-idea-staging.md): a deletable list
cannot answer the question it exists for. If an idea can be quietly removed, its absence means
nothing — it may never have been raised, or it may have been raised and rejected for good reason.
Someone re-proposes it and the work of having judged it once is lost. Discarded entries stay visible
with their reasons, so the list answers *"has this been considered?"*. Same principle `GOV-005`
applies to codes: a record that can be rewritten stops being evidence.

This also corrected a contradiction introduced an hour earlier — ADR-010 originally said an entry
"graduates or is deleted", which the append-only rule contradicts. Now it ends in a status, never in
deletion.

### Final-pass checks

| Check | Result |
|---|---|
| Test suite | 266 passed |
| Governance | exit 0 — 16 systems, 55 documents, 8 memories, 86 phases |
| Queue executable in `next_up` order | Yes — every phase's `depends_on` is satisfied by something earlier or already complete |
| Internal document links | One dangling reference found and fixed (`PLAN-014` was renamed when it broadened to host both reviews) |
| The course material's cross-links | All resolve |
| Working tree | Clean |
| Remote | None, per `AGENTS.md` until `phase-priv-05` |

### What this session produced

No phase was claimed; all work was owner-directed, which `OPS-001` says still requires this record.
Outputs: the course material and its production design in `_public/`, the cadence rename
finished in the DDL, the terminology and tooling systems planned, the governance-model and
complexity reviews scheduled, an ungoverned staging area, and eleven commits.

### What is deliberately unresolved

- **Seven adversarial-review findings** — directory-level deliverables weakening the concurrency
  lock, no requirement documents or ADRs for this session's own work, unverifiable acceptance
  criteria, and the undecided glossary series. Assigned to `phase-gov-03`.
- **`_data/tasks/` does not exist**, so personal action items still have nowhere to live until
  `phase-cap-07`.
- **The plan-requirement pressure** — four manufactured documents in one day — is evidence for
  `phase-gov-03`, not a decision made here.
- **This record has six amendments**, and the owner corrected my reading of that. I called it a
  finding — a session long enough to need six should have been closed and reopened. The better
  argument is theirs: the alternative to amending is writing the whole record at the end from
  degraded memory. Amendments are **contemporaneous**, written while the context that produced each
  decision is still loaded, and revised as later work changes what earlier work meant. For a long
  session that is more accurate, not less. What `phase-ses-01` should take from this is not "cap the
  amendments" but "long sessions document in passes" — see the seventh amendment.

### Queue at close

`phase-scope-01`, `phase-term-01`, `phase-term-02`, `phase-gov-02`, `phase-tool-01`, `phase-gov-03`,
`phase-cap-03`, `phase-rel-11`, `phase-cap-07`, `phase-priv-02`, `phase-ses-01`.

`phase-tool-02` — generalising the tooling for reuse across repositories — sits at priority 4 outside
`next_up`.

## Seventh amendment — the amendment pattern itself, and one more parked idea

### Amending as you go beats writing at the end

I recorded six amendments as a defect. The owner disagreed, and their reasoning is better than mine.

Writing a session record at the close means reconstructing decisions from memory that has already
degraded — the reasoning behind an early choice is thinnest exactly when the session has been long
enough to need the record most. Amending as the session progresses captures each decision while its
context is still loaded, and lets later work revise what earlier work meant rather than silently
overwriting it. The amendment trail in this document is a fair example: three separate corrections to
the `brain/` folder claim, the plan-code reuse, and the queue order are all legible as corrections
because they were written when they happened.

**The practice worth extracting for `phase-ses-01`:** long sessions should document in passes —
pause, write while fresh, revise as the work moves — rather than treating the record as a closing
task. Amendment count is a signal of session length, not of session quality, and conflating the two
would push toward exactly the worse practice.

This session ran far longer than intended, which the owner noted. The reason was that each extension
carried context that would have been lost across a clear — architectural decisions building on
earlier ones. That is a real trade-off between session hygiene and context continuity, and it belongs
in the session taxonomy rather than being resolved by a rule about length.

### Idea 002 parked

A prioritised **search order for agentic knowledge retrieval**: which source an agent consults first
when answering a question, given that developed code, plans, ADRs, session records and parked ideas
all have different relationships to truth. The ordering principle is the real question — an agent
that reads a plan describing unbuilt work and treats it as reality will be confidently wrong, which
is not hypothetical here, since several `systems.yaml` entries describe aspiration and `PROMPT-003`
already asks whether that file is a registry or a map.

Recorded in [ideas.md](../00-working/ideas.md) as entry 002, `open`. Order to be decided later;
related to `sys-retrieval` and to `phase-term-01`'s `--system` filter, which adds a retrieval axis
any ordering would have to account for.

## Eighth amendment — capture discipline, and six more ideas

### Ideas are recorded as given

The owner corrected a real mistake: I proposed consolidating three of their ideas because the work
already existed as deferred phases. They accepted the consolidation once and stated the principle —
*"my ideas are my ideas, whether they conflict or already exist in some form. Let the data be, and
the processes that are or will be handle it."*

They are right, and the reason is stronger than preference. **Filtering at capture destroys the data
the list exists to produce.** An idea raised is a fact about what the owner was thinking and when,
and it stays a fact even when the work is scoped elsewhere. Collapsing it at the door erases the
signal that the thought recurred — which is exactly what idea `000008` proposes to measure. This is
the same routing principle [ADR-007](../04-decisions/ADR-007-capture-routing.md) applies to captured
notes: ambiguity is flagged, not interrupted for. Recorded in
[ADR-010](../04-decisions/ADR-010-idea-staging.md) as rule 0, ahead of the append-only rule, because
it governs the earlier moment.

Idea `000007` — an agent that triages this list and scouts for related plans — is what makes
capture-as-given safe. Overlap detection moves downstream, where it belongs.

### A skill, not a command

The owner asked why offering both a skill and a slash command was even an option, since they would
have the same result. It was a false choice and the option was wrong. A **skill** is invokable by the
owner as `/name` *and* by the model when its description matches; a **command** is user-triggered
only. The skill strictly dominates, and the only reason to prefer a command is to deliberately
prevent model invocation. Recorded in idea `000003`.

### Six-digit identifiers

Entries `001` and `002` are renumbered `000001` and `000002`. This edits existing entries, which the
append-only rule forbids, so ADR-010 gains an explicit carve-out: a format migration changing no
content is permitted and must be recorded. The rule protects the record of *what was judged and why*;
an identifier width carries no judgement.

The owner drew the general lesson: three digits was chosen without a horizon, and other indexes may
share the defect. **Document codes are three digits** —
`^[A-Z]+-(?:[0-9]{3}(?:\.[0-9]{2})?|...)$` caps each series at 999, sub-codes at `.99`, and dated
session codes at 99 per day, while `GOV-005` forbids reuse so retirements consume the space
permanently. Idea `000006` audits every index against a realistic horizon. The asymmetry is the
point: widening a pattern early is cheap, renumbering issued codes is forbidden.

### Ideas parked

`000003` mid-session notes skill · `000004` vector databases, agentic RAG and semantic-plus-
deterministic search, cross-referenced to the deferred `phase-mem-15` through `-19` · `000005` graph
databases and GitNexus · `000006` index-width audit · `000007` idea-triage agent · `000008` metrics
over the ideas data.

`000005` is the one that is genuinely uncovered. GitNexus is a real MIT tool that builds a client-side
knowledge graph of a repository using an embedded KuzuDB, with a Graph RAG agent exposed to Claude
Code over MCP, and it argues explicitly for Cypher over code relationships instead of vector
embeddings. The entire `phase-mem-*` line is vector-based, so nothing here has considered graph
retrieval at all.

One finding surfaced while cross-referencing `000004`: all five `phase-mem-*` phases gate on
**recorded retrieval failures** — `phase-mem-15` requires them to choose a provider, `phase-mem-19`
requires them to justify query refinement. Nothing in this repository currently records a retrieval
failure, so the gate cannot be met by waiting. That is noted in the entry rather than acted on.

## Ninth amendment — final two ideas and close

`000009` — an agent that reads the session transcript directly as an independent third party and
writes its own session record, then an adversarial review between that account and the working
agent's. The premise has evidence from this session: a reviewer with no conversational context
returned 21 findings, three of them session-breaking. Reading the raw transcript is a stronger
version, because a participant's record inherits the participant's blind spots. Includes a
deterministic extraction script and a diff against the previous extract so each pass analyses only
new material rather than re-reading a monotonically growing file.

`000010` — an ideation dashboard: an input field wired to an idea-manager agent that captures and
triages without a session being open, an idea browser, and the metrics from `000008`. The capture
path matters most: today an idea is only recorded if a session happens to be running, which silently
filters for ideas that occur at a keyboard. Noted as a candidate first real consumer of `sys-html`,
which `PROMPT-003` asks whether anything consumes.

Both were recorded as given under ADR-010 rule 0, with their overlaps against `000003`, `000007` and
`000008` noted inside the entries rather than used to decline or merge them.

The list closes this session at ten entries, all `open`.

## Tenth amendment — the idea record system becomes first priority

The owner identified a missing component that invalidates the list's stated purpose: **no
timestamps**. Without them, none of the intended analysis — idea density over time, actualisation
rate, fizzle rate, time to resolution — is computable. This is time-sensitive in a way most backlog
work is not: every idea captured before the system exists is captured without structure, and a
timestamp reconstructed later is a guess.

The ten existing entries carry timestamps at two-minute intervals from `2026-09-06T14:45:00-04:00`,
recorded by the owner against a clock as the ideas arrived. Note the offset: 6 September is daylight
time in US Eastern, so the literal "EST" would be `-05:00` and would place every entry an hour off in
any time series. `phase-idea-01` preserves them exactly, since restamping them would destroy real
recorded times.

### The event-log design, and why it resolves the owner's objection

The owner accepted JSONL with a real reservation: *some fields must change — status and dates — while
the entry stays immutable.* That is a genuine tension in a line-per-entity file.

An **event log** dissolves it. Each line is an event rather than an entity: `created`, `status`,
`revisited`. Nothing is ever edited, so a status change appends a line, and "immutable except status"
stops being a rule to police and becomes structurally true. Current state is a fold over events, done
once at rebuild into `ideas` and `idea_events`, which makes the time-series metrics SQL rather than a
parsing job — every transition already carries its own timestamp.

File count was investigated and is **not** the constraint the question assumed: ext4 with `dir_index`
degrades in the hundreds of thousands, git carries ~80k files in the kernel tree, and at three ideas
a day it would take a century to reach 100k. One-file-per-idea was rejected for a different reason —
a status change rewrites a file, so immutability becomes a claim about content rather than a fact
about bytes.

### States

`open` → `triaged` → `reviewing` → `promoted` | `discarded`, forward-only, with `discarded` reachable
from any working state. `revisited` is an **attribute with its own timestamp, not a status**, at the
owner's direction; a revisit returns status to `reviewing`, and a second discard is permanent. The
owner's reasoning: something worth revisiting twice needs a profoundly new but related idea recorded
separately, which keeps the second thought legible as its own entry.

`triaging` was proposed and deliberately omitted. It would separate "the agent has not started" from
"the agent is working" — different problems with different fixes — but only pays if triage is slow
enough to be observed in. The event log makes adding it later free, since a new event type does not
invalidate old events, so the decision is deferred rather than guessed.

### Consequences for ADR-010

`docs/00-working/ideas.md` becomes a **generated artifact**, same rule as `catalog.md` and the
glossary. The staging *concept* survives untouched — capture as given, never filtered at entry — but
the storage moves to `_data/`, which partly supersedes ADR-010. `phase-idea-01` carries amending it
as an explicit deliverable rather than leaving a governed decision contradicting reality.

### Queue

`phase-idea-01` takes first position, ahead of the course extraction. `phase-idea-02` — the triage
agent — is priority 3 and outside `next_up`, per the owner: the schema and tools are essential, the
agent is secondary, and the tool is usable by hand the moment it exists.

## Eleventh amendment — the /backlog command

`.claude/commands/backlog.md` — the first entry in `.claude/` beyond `settings.local.json`, so it
sets the pattern for commands in this repository.

**A command, not a skill**, and this is consistent with the earlier reasoning rather than a reversal.
A skill dominates a command *except* when model invocation should be prevented, and claiming a
backlog phase is exactly that case: it writes `status: active` and an `agent` field that the
concurrency protocol treats as a lock, so it must follow the owner's decision rather than an agent's
inference.

Named `/backlog` because Claude Code already owns `/resume`.

**What it does:** preflight with governance and the full suite, stopping dead if either fails; print
the top five ready phases with titles rather than bare codes, per `GOV-006`; recommend the first and
say why; orient on it by reading the phase, its plan and `AGENTS.md`, with sources and
`systems.yaml` entries loaded **conditionally** rather than always; then summarise and stop.

**Modes.** `$ARGUMENTS` takes an optional phase id and an optional mode flag. Bare `/backlog` orients
and stops — the default. `--claim` claims the phase and stops. `--go` claims and begins the first
action. An unrecognised argument falls back to the default, and `--go` is never inferred from urgency,
from a phase looking obvious, or from it having been used last time: it is typed or it does not
happen.

Every mode runs the preflight and stops dead on failure, `--go` most of all — starting work
automatically on a repository already red produces failures tangled with someone else's. And under
every mode, defects noticed while orienting are surfaced *before* work begins; `--go` means the owner
skipped the confirmation, not that judgement was waived.

**What it deliberately does not do:** claim the phase by default, or read session records. The
owner excluded session records — they are narrative and long, and their carried-forward content
belongs in phases. The stated exception is an adversarial review after work is done, where the record
of what was decided is the point.

The preflight is a direct response to this session's own history: it opened on a governance failure
inherited from a previous session. Finding that before any edits is a fix; finding it three edits in
is a debugging session where someone else's breakage is entangled with yours.

The summary step asks the agent to flag defects it notices while orienting — an acceptance condition
no verification can observe, a deliverable list missing a file the scope requires, an undeclared
dependency. Those are exactly the three defect classes the adversarial review found in phases written
this session, and catching them at orientation costs far less than catching them at close.

### Two ideas parked from the design

`000011` — a backlog review and re-prioritisation recipe. The command's empty-queue branch says a
review is needed without saying how; that is deliberate, since defining a prioritisation process
before it has ever been needed is building ahead of demand, and 88 phases means the case is not
close.

`000012` — skipping the test preflight when the tree is provably clean. Free at 266 tests in under
two seconds; not free later. Once CI gates exist and a commit has a green result, re-running locally
proves nothing new, and the preflight could check provenance instead. Blocked on infrastructure that
does not exist until `phase-priv-05`.

The list closes at twelve entries, all `open`.

## Twelfth amendment — timestamp scope corrected, and idea 000013

### The timestamp scope covers all thirteen entries, not just the first ten

The owner asked me to confirm the timestamps were present. All thirteen entries carry one, and
checking surfaced a scope error in `PLAN-016` that I introduced: it described only the first ten.

Entries `000011` through `000013` were created later in the same session and carry recorded times of
their own, so the migration has to cover every entry rather than a fixed count. `PLAN-016` now scopes
it to "every entry created before the writer exists". After `phase-idea-01` the writer is the only
thing that stamps a timestamp, so the set is closed.

### The migration override the owner anticipated

The owner flagged that a one-time exception would be needed to carry the backfilled timestamps
through migration. Correct, and it is now a decision in `PLAN-016` rather than something discovered
mid-migration and worked around.

`tools/append_idea.py` generates the timestamp itself — that is the whole point, and letting a caller
supply one is how the log stops being trustworthy. But the migration must **preserve** the existing
recorded values rather than restamp everything with the migration's clock, which would collapse
thirteen entries into one instant and destroy the only history the list has.

So the writer gets an `--at` override that is deliberately awkward: refused unless an explicit
migration flag accompanies it, recorded in the event itself so the log states that an override
happened, and covered by a test asserting normal invocation cannot reach it. An escape hatch that
looks like an ordinary argument will be used as one.

### Idea 000013 parked

Investigate other commands worth encoding. `/backlog` exists because a repeated manual routine was
worth capturing; the same test — *is this a routine done from memory where doing it differently each
time causes real problems* — points at several others observed today. Closing a session is the
strongest candidate, since `OPS-001` documents the procedure in prose **precisely because** closing
was being done from memory. Also: allocate-a-code-and-stub-a-document, the verify sequence run
roughly fifteen times by hand today, and adversarial review, which found three session-breaking
defects and should not depend on remembering to ask for it.

The list closes at thirteen entries, all `open`.
