---
schema_version: 1
id: doc-systems-review-decision
code: ADR-012
title: Systems review keeps the model as built and retires the unused walkthrough kind
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-governance, sys-backlog, sys-portfolio, sys-contracts, sys-projection, sys-retrieval]
depends_on: [doc-systems-review-prompt, doc-governance-model-decision]
---

# Systems review keeps the model as built and retires the unused walkthrough kind

## Context

[PROMPT-003](../02-prompts/PROMPT-003-systems-review.md) asks this repository to review every system,
document kind, schema and folder for scope creep, biased toward removal, on the standard: what
decision does it make cheaper, what breaks if it is deleted, who is the audience, and what did it
cost against what it has returned. It exists because a git course produced course material that
acquired a project record, a system entry, a plan and two backlog phases inside a repository that
manages consulting work — the schema's insistence on a plan, a systems list and deliverables was
resistance, and the resistance was read as a cost instead of the signal it was. `PROMPT-004`
(terminology and architecture) was meant to run first for shared vocabulary; `phase-term-01` and
`phase-term-02` are both complete, so that prerequisite is satisfied. Per
[PLAN-014](../01-plans/PLAN-014-governance-and-complexity-review.md), question 3 (`governance` versus
`operation`) is inherited from [ADR-011](ADR-011-governance-model.md) rather than reopened: the two
kinds stay split, and `phase-tool-01`'s per-tool documents already use the `OPS` series on that basis.

### Part 1 — the system as it stands, checked against the code rather than assumed

**The content folders.** `_data/` is the git-tracked source of truth `tools/rebuild_db.py` projects
into the gitignored `data/d_system.duckdb`; it currently still holds the owner's real portfolio
(named client engagements, personal finances and health) because [ADR-009](ADR-009-structure-content-boundary.md)'s
relocation to `_private/portfolio/` has not run yet — that is `phase-priv-02`/`-03`, both queued
directly behind this phase. `_public/` holds shareable outputs. `_private/` is gitignored entirely,
read only on direction. `_working/` is gitignored, unscanned by governance, and holds ephemeral plans
that would be *deleted* rather than rewritten once the task ends. `_tmpagent/` is tracked but also
unscanned, and exists only because a gitignored file can never reach a sibling worktree — it holds
claim-contract files agents in worktrees must read.

The one place two folders could plausibly accept the same file is `_data/` versus
`_private/portfolio/` during the current pre-relocation window: real content sits in the tracked path
today, which is exactly the state ADR-009 exists to end. That is not ambiguity in the *rule* — the
destination is decided — it is a known, scheduled, already-queued gap between decision and execution.
`_working/` and `docs/00-working/` look like a second overlap (both are "not ready to be governed
yet" staging) but are not: `_working/` is gitignored and its contents are meant to disappear,
`docs/00-working/` is tracked and its contents (parked ideas, per
[ADR-010](ADR-010-idea-staging.md)) are meant to graduate. Tracked-versus-gitignored is a mechanical,
unambiguous test; the two folders hold different lifecycles by design, not by accident.

**The backlog system.** `docs/09-backlog/backlog.yaml` holds one phase per one-session outcome, with
`plan`, `sources`, `systems`, `status`, `priority`, `session_budget`, `depends_on`, `scope`,
`acceptance`, `verification`, `deliverables` and `next_action` required on every item
([GOV-002](GOV-002-backlog-protocol.md)). Every field does real work: `systems`/`deliverables`
disjointness is what lets `max_active` phases run concurrently without collision
([ADR-003](ADR-003-multi-agent-concurrency.md)); `depends_on` drives derived readiness; `acceptance`
and `verification` are what a session-close review actually checks; `next_up` is the explicit queue
override that lets an agent pick up work with no judgment call. Nothing here is ceremony — each field
is cited by a real mechanism, not merely descriptive.

**The document system.** Nine kinds (`plan`, `adr`, `architecture`, `prompt`, `requirement`,
`session`, `walkthrough`, `operation`, `governance`) are drawn from a per-kind series in
[codes.yaml](codes.yaml), allocated by `--next-code` and never chosen by hand
([GOV-005](GOV-005-document-codes.md)), and rendered into [catalog.md](catalog.md), which CI
regenerates and diffs. 84 documents currently exist. Every kind but one has real, structurally
distinct instances (see question 3 below).

## Decision

### 1. Personal action items: confirmed, and no parent required — already built, not reopened

`SESS-2026-09-06-08` was right that the backlog cannot hold the owner's personal to-dos: a backlog
phase requires a plan, systems and deliverables that a bare action item has no reason to carry.
`schemas/task.schema.json` already covers the case with only `id`, `description`, `status` and
`created` required, and per its own description, "an entity that can exist without a parent cannot be
stored inside one" — `commitment_id` and `project_id` are both nullable, and an unfiled task is
explicitly called out as intended, not an edge case to special-case away. The only gap is
mechanical, not a design question: `_data/tasks/` does not exist yet, because it arrives with
`phase-cap-07`. Nothing is added or changed by this review; the design question PROMPT-003 raised was
already answered when the schema was written.

### 2. What belongs in this repository: the git course was the only violation, and it is already gone

The candidate test — *does this manage the owner's work, or is it work being managed?* — needs one
refinement to survive contact with `_data/`: portfolio content is not "work being managed" in the
sense that made the git course wrong. The git course had its own audience (learners) and its own
deliverable, unrelated to running a consulting practice, and only entered this repository because the
backlog schema demanded a plan for it to exist at all. `_data/`'s projects, by contrast, are the
substrate the system exists to manage — without them there is nothing to track. The sharper test:
*does this have an audience or delivery mechanism of its own that is not "help the owner run their
practice"?* Applying it to everything currently tracked — `src/`, `ts/`, `schemas/`, `sql/`, `tools/`,
every `docs/` series, `_data/`, `PROMPT-001` (a reusable code-generation prompt for this system,
not an external artifact) — nothing else fails it. `sys-course` is already `retired` in
`systems.yaml`, already extracted to its own repository; the mechanism this question worries about
has already fired once, correctly. Nothing further to remove.

### 3. Eight kinds earn their keep; `walkthrough` does not, and is retired

Checked each kind against a real, structurally distinct instance: `plan` (`PLAN-001`–`017`, 28
documents), `adr` (`ADR-001`–`012`, this document included), `architecture` (`ARCH-001`–`004`),
`prompt` (`PROMPT-001`–`005`, reusable session-launch instructions), `requirement` (`REQ-001`–`003`,
observable statements plus verification methods, distinct from a plan's narrative), `session`
(`SESS-*`, 22 dated execution records), `governance` and `operation` (kept split per ADR-011: rules
versus runbooks, and `inspect_backlog` mechanically requires `kind: governance` or `adr` for a
decision record). `walkthrough` has zero instances across 84 documents and four days of continuous
work, despite sharing `docs/03-sessions/`, dated numbering and much of its stated body shape
("reproducible steps, result, verification") with both `session` and `operation`. By this review's own
standard — *a kind with no distinct instance is a candidate for merging* — nothing breaks by removing
it: no `decision_record`, no check, no cross-reference names `kind: walkthrough`. Its function, to the
extent one ever existed, is already covered: `operation` documents are exactly "reproducible steps,
run this, verify that" for anything durable enough to repeat, and `session` already carries verification
output for anything that happened once. **Retired.** Implementation — removing the kind from
`document.schema.json`'s enum, the `WALK` series from `codes.yaml`, and the taxonomy row from
`GOV-001` — is filed as `phase-gov-04`, not done in this session, per PLAN-014's constraint that no
schema is written before the ADR deciding it.

### 4. The requirement-plan-phase chain is not routinely bypassed; leave it alone

Two distinct patterns hide behind PROMPT-003 question 4's one claim of "several recent documents...
recorded that deviation," and pulling them apart matters. **The plan-before-code step itself** was flagged as
skipped exactly **once** across four days and 96 backlog phases —
`SESS-2026-09-06-07-conversation-guidelines.md`, where the owner judged a plan disproportionate for a
single short governance memo, directed it written directly, and the agent recorded the deviation
rather than leaving it implicit. **Owner-directed "unphased" work** is a separate, already-formalized
pattern — small owner-directed edits made outside any claimed phase, required by `OPS-001`'s interim
procedure (added in `SESS-2026-09-06-03`) to produce their own session record — and it recurs, e.g.
`SESS-2026-09-06-08`'s cadence-column rename. That is not a plan-before-code bypass: the rename
decision was already covered by `phase-cap-02`'s governed plan, and only the mechanical SQL/tooling
follow-through was done outside a fresh phase claim, exactly as the sanctioned procedure allows, with
the required record produced. Every remaining recorded "Deviation from AGENTS.md" in the session log
concerns a third matter again — primary-checkout-versus-worktree (already resolved by `phase-ses-03`
per GOV-003) or a rebase-versus-merge choice — not this chain at all. Once separated, the
plan-before-code rule has one genuine instance, and it is a correct application of the rule's own
qualifier: `AGENTS.md` already says "for any **non-trivial** change," and a single short prose memo is
exactly the case that qualifier exists to exclude. The rule is doing its job, and the unphased-work
escape valve next to it is also working as designed. No change.

### 5. Sixteen systems: a live registry, not an aspirational map — leave alone

Of sixteen entries, eight are `implemented`, two `scaffold`, five `planned`, one `retired`. A `planned`
entry is not inert description: it is the thing a not-yet-built phase's `systems:` field points at so
the backlog's concurrency check (`ADR-003`) has something to lock against before the component exists
— without it, two agents could start conflicting work on the same not-yet-built area with no
disjointness check to catch it. `GOV-001` already states this design plainly: the dependency graph is "current
dependencies for implemented components and intended dependencies for planned components." The
pruning mechanism this question asks whether to add already exists and has already fired once:
`sys-course` sits at `status: retired` with an empty `paths` list, the exact outcome a stale planned
entry should reach. No entry today is stale by that standard — all five `planned` systems back an
open plan with active or queued backlog coverage. No change.

### 6. The projection has a real consumer today; it is not ahead of its market

The premise needs correcting before it can be answered: `sys-retrieval` (`tools/load_context.py`,
documented in `OPS-003`) reads `data/d_system.duckdb` directly and is a real, currently-used
consumer — keyword, project, type and tag-filtered retrieval for agent memory context. The FastAPI
app (`sys-api`, `scaffold`: a health check and an empty `/api/v1` router) and the React UI
(`sys-ui`, `scaffold`: a heading and a Vite proxy) are a *second*, not-yet-built consumer, tracked
under their own maturity and their own planned dependents (`sys-html`). `tools/rebuild_db.py` and
`sql/001_schema.sql` are not idle investment awaiting an application; they already justify their
maintenance cost through the CLI that exists today. No change.

### 7. Session records earn their cost specifically because git log will not survive

22 session records span four days. The comparison PROMPT-003 asks for — what does a future reader get
that `git log` does not — undersells the case: `GOV-003` already records that `phase-priv-05` will
**squash all history to a single commit** before the first push, because a single provable tree beats
a filtered-but-unverifiable history for a repository that has held real client and financial content
in nearly every commit. After that squash, `git log` will not be a poorer substitute for the
session-record narrative — it will not exist at all for anything before the squash point. Session
records already carry what a future reader actually needs and `git log` never captured even today:
the owner's stated reasoning for a deviation, verification output actually run rather than assumed,
and citable evidence other governed documents point at (`ADR-011`, `GOV-003` and this document all
cite specific session records for specific claims). No change.

## Alternatives considered

**Fold `walkthrough` into `session` instead of retiring it outright.** Rejected: `session` already
covers "outcomes, evidence, unresolved items" including verification output for one-off work (every
`SESS-*` record already does this), so there is no shape `walkthrough` would add that `session` lacks.
A merge that changes nothing about what gets written is a rename, not a simplification.

**Treat the course-extraction precedent as reason to audit every plan for a hidden external audience.**
Rejected as more work than the evidence supports: the sharpened test in decision 2 was applied to
every currently-tracked plan and document series, and nothing else failed it. Re-running a full audit
without a new candidate would be exactly the "defer to the volume of prior documentation" failure mode
PROMPT-003 itself warns against — in reverse, auditing for the sake of having audited.

**Widen this phase's own deliverables to edit `document.schema.json` and `codes.yaml` directly.**
Rejected: PLAN-014 states no schema is written before the ADR that decides it, and this ADR is that
decision, not the implementation. `phase-gov-04` carries the schema edit as its own reviewable diff.

## Consequences

- `kind: walkthrough` is retired. `phase-gov-04` implements the removal:
  `schemas/document.schema.json`'s kind enum, the `WALK` series entry in `codes.yaml`, and the
  taxonomy row in `GOV-001`. Until that phase runs, the kind remains technically legal but is not to
  be used — this ADR is the record that would flag any new `WALK-*` document as a mistake, not a
  precedent.
- No system, folder or other kind changes maturity or is removed. `_data/` versus
  `_private/portfolio/` stays a known, already-scheduled gap closed by `phase-priv-02`/`-03`, not a
  new finding.
- The requirement-plan-phase chain, the systems registry's four-maturity model, the DuckDB
  projection, and the session-record practice are all confirmed as designed; none is reopened absent
  new evidence.
- `AGENTS.md` is not revised: none of the seven answers changes what an agent must do.

## Revisit trigger

If a second repository-scoped body of external-audience work (a second "git course") appears, apply
decision 2's test to it directly rather than reopening this review. If `kind: walkthrough` is ever
proposed again, cite this ADR and bring a real candidate instance — the "no distinct instance" finding
is what retired it, and a genuine one would be new evidence. If the `_data/`/`_private/portfolio/`
relocation stalls past `phase-priv-03`, that gap stops being "scheduled" and becomes a live finding for
a future review.
