---
schema_version: 1
id: doc-session-2026-09-06-10
code: SESS-2026-09-06-10
title: Synthesize the idea and plan lifecycle architecture
kind: session
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-backlog, sys-portfolio, sys-projection]
depends_on: [doc-idea-plan-lifecycle, doc-idea-plan-lifecycle-requirements]
---

# Synthesize the idea and plan lifecycle architecture

## What happened

`phase-idea-03` was executed in two passes. An external agent produced the first pass — the
requirements (`REQ-003`), the parent plan (`PLAN-017`), two of six category children, and the two
ungoverned working notes — and stopped partway. This session audited that work, corrected it, and
finished it.

The first pass reported itself as drafted and allocated. It was neither validated nor complete:
`uv run python -m src.governance` exited **1** with four errors, `uv run pytest` reported
**3 failed, 284 passed**, four of six children were unwritten, the catalog was never regenerated,
and the single implementation phase it added named none of the children it claimed to cover.

## What the audit found

**The four folders the owner asked for were illegal.** `src/governance/codes.py:149` rejected any
plan document nested inside a plan folder. The first pass created the folders anyway and did not
report the conflict. The rule existed only in code — `GOV-005`'s "Multi-file plans" section had
never stated it, which is how it went unnoticed until documents were already sitting in it.

**A second failure was hidden behind the first.** Once the layout and reservations were fixed in a
scratch copy, two further errors surfaced:

```
ERROR backlog: open plan has no non-cancelled phase: doc-idea-plan-idea-lifecycle
ERROR backlog: open plan has no non-cancelled phase: doc-idea-plan-plan-lifecycle
```

The architecture violated `L3` — the owner's own rule that every plan has at least one phase — which
is one of the four rules it exists to enforce. Its parent plan asserted that shared phases cover
children through `sources` while the only phase written named no child at all.

**The amendment pointer addressed a value that does not exist.** The first pass replaced the
colliding secondary identifier with `amends: <seq>`. But `seq` appears nowhere in
`_data/ideas.jsonl`; `sql/001_schema.sql` declares it as half of a primary key and the rebuild
assigns it from a line's ordinal. The pointer would have addressed a number recomputed on every
rebuild and freely changed by any concurrent append — the same fragility the secondary identifier had,
one layer down. Its own conflict register (`C07`) conceded the pointer could not survive a worktree
merge and offered a serialisation rule instead of a fix.

## Decisions taken during the session

The owner decided four things through the question tool.

### The validator was relaxed rather than the folders abandoned

`naming_errors` now permits exactly one area-folder level inside a plan folder, for sub-coded
children only; the overview stays at the folder root, and nesting stops there. `GOV-005` documents
the rule for the first time.

This is a folder-structure change made while `phase-gov-03` — the complexity review, whose stated
bias is removal and whose prompt says *"Do not add a new system, kind, folder or schema"* — sits
queued. The owner chose it knowingly. `PLAN-017.06` records it as a finding so the review inherits
it rather than discovering it, and the area-folder rule not surviving that review is a legitimate
outcome: the children would flatten and their codes would not change.

### Amendments name a stable identity, not a position

Every new event carries a writer-generated `eid`; the 19 historical events resolve to a digest of
their own already-permanent bytes, so no existing line is rewritten. An `amends` pointer names that
identity. The pointer therefore survives a git merge that interleaves two worktrees' appends, and
`C07` stops being a process rule the writer must uphold and becomes a property of the data. The
DuckDB primary key moves from `(idea, seq)` to the resolved identity, which removes the constraint
violation the audits demonstrated rather than routing around it.

### A complete plan may hold cancelled phases, with a warning

The first pass proposed that `complete` fail when any phase is cancelled. That would force a plan
which met its intent while dropping one optional phase to deprecate instead, converting an ordinary
scope decision into a failure record. The cell is now **warn**, clearing when `completion_evidence`
explains the cancellations. `GOV-002` is unchanged, so no standing policy was reversed.

### Scope stayed at architecture

No implementation code was written. The one exception is the validator change above, which the
chosen folder structure required before anything else could be validated.

## Outcomes

Six category children now occupy the four folders, each carrying what is known, what is proposed,
what is open, what it touches, how it is verified, and its conflicts with other categories. The
single overloaded phase — four repairs, a full plan inventory, activation changes and edits to three
governance documents, in one session with thirteen deliverables — was split into five, each sized to
one session, each naming the children it delivers. The first three need no schema change and can
proceed now; the last two are gated on the complexity review.

Whether to promote that review in `next_up` so it stops blocking the schema extensions is left open
as the owner's call, and is the most consequential unresolved item in the plan set.

One correction carried forward from the transcript analysis, because it is easy to lose: only
**L1-L4** are confirmed by the conversation export. **L5-L11** are constraints supplied by the brief,
not decisions the owner is recorded as making, and every document says so.

## Work outside the claimed phase

Reviewing the tree before committing turned up something the phase did not cover. The idea log held
**14 events at `HEAD` and 19 in the working tree**: ideas `000015`-`000019` had been appended by the
sanctioned writer and never committed, so five captures existed only as an unstaged change to one
file. Among them were `000018`, whose tagging request sets the deferral gate this architecture
relies on, and `000019`, the corrupted record every audit cites as evidence.

Every document produced by this session, both audits and the synthesis are premised on 19 events. A
stash drop or a careless checkout would have taken five of them permanently. An append-only log's
guarantee stops at the last commit, and nothing in the system was watching that gap.

They are committed on `dev` in the commit “Record five ideas captured before the architecture session”, ahead of the architecture work. `000019` stays corrupted:
repairing an append-only log to hide the defect that produced it would destroy the evidence for the
fix. `docs/00-working/ideas.md` was regenerated and was already in sync.

## Integration

Three commits, one concern each, then a merge:

```
Add _tmpagent/ with a claims ledger for cross-worktree files
Gitignore _working/ and reserve its deletion to the owner
Record the architecture session and close it properly
Point the transcript analysis at the export's real location
Merge the idea and plan lifecycle architecture
 |  Add the idea and plan lifecycle architecture
 |  Allow one area-folder level inside a plan folder
Record five ideas captured before the architecture session
Claim idea and plan architecture phase
```

The last three land after `phase-idea-03` was already marked complete. They are owner-directed policy
work, not phase deliverables, and they are recorded here because that is what keeps unphased work
from being invisible.

The conversation export moved to `_private/`, which is gitignored. It is a raw transcript, the
confidentiality sweep (`PLAN-006`) has not run, and this repository will be squashed before a remote
exists — committing it would have put an unreviewed export into history that history is not a place
to recover from. `transcript-analysis.md` now names that location and states plainly that its line
references cannot be resolved from the repository alone, so a later reader does not chase a missing
path and conclude the citations were invented.

## Deviations from AGENTS.md

**Integrated by merge, not rebase.** `GOV-002` asks for a rebase onto current `dev` with the full
check re-run afterwards. The owner directed a merge. The check that matters was still performed:
governance, the catalog comparison and the full suite were all run on `dev` **after** integration,
in the combined 19-events-plus-architecture state that neither branch held on its own. The
integration commit is “Merge the idea and plan lifecycle architecture”.

**Implementation code was written during a documentation phase.** `src/governance/codes.py` and
`test/test_codes.py` changed. The phase's scope says documentation only. The four folders the owner
asked for could not exist otherwise, and nothing else in the phase could be validated until they
did. Recorded here rather than waved through as incidental.

## The working directory was reclassified

The five `_working/` documents left untracked at the end of the architecture work prompted the owner
to change the policy rather than resolve the instance. `PLAN-015` had said `_working/` was committed
but informal, and that ephemeral plans are *deleted, not archived*. Both rules are now reversed:
the directory is **gitignored**, and **nothing in it is deleted without the owner's explicit
approval**. Its open question — prune on a schedule or at phase close — is answered by the same rule:
on request, and only on request.

`.gitignore`, `AGENTS.md`, `CLAUDE.md`, `README.md` and `PROMPT-003` were updated in the same change
so no copy of the old rule survives to be followed later.

One consequence is recorded in the amendment rather than designed around: **an ignored file does not
reach a git worktree.** This session demonstrated it without noticing at the time — the brief, both
audits and the synthesis that `_working/CODEX-PROMPT.md` told an agent to read existed only in the
primary checkout, never in `../d-system-worktrees/phase-idea-03`. A phase whose `next_action` points
into `_working/` must now be run from the primary checkout, or have its detail handed over directly.

Two files stay tracked by explicit exception: `.gitkeep`, and one other file that a since-completed
phase named as a deliverable. Removing that second one would have stranded a queued phase, and
removing files is exactly what the new rule reserves to the owner.

### `_tmpagent/` answers the worktree gap

The owner's response to that consequence was a second directory rather than a carve-out in the
first. `_tmpagent/` is tracked, holds the files agents in sibling worktrees must read, and carries a
claims contract in `_tmpagent/AGENTS.md` with an append-only ledger at `_tmpagent/claims.jsonl` in
the same shape as `_data/ideas.jsonl`. A file is read-only once active; every reader claims it by
naming the branch or plan using it; every claim is closed by an explicit line; a file is eligible for
deletion only when no claim remains open.

Using the **branch** as the locator is the design's strongest idea: a claim nobody closed can still
be investigated, because `git branch --list` says whether the work that held it still exists.

One recommendation of mine was overruled and the owner was right. I proposed deriving plan
dependencies from plan status instead of writing closing lines. That misses a resolution path
entirely — a file that turns out to be worth keeping gets relocated, which is a real way a claim
ends and never involves a plan reaching `complete`. Derived logic would hold such a claim open
forever with no way to close it. Explicit lines close every path, including unenumerated ones.

The contract is **convention, not code**, by the owner's decision: no test reads the ledger and no
validator fails on it. That is proportionate at zero files and a debt if the directory grows. It is
also the same bet the idea-system audit warned about — a schema designed ahead of its data — so the
failure to watch for is a ledger that quietly stops matching reality.

## Verification

Run on `dev` after the merge:

```
uv run python -m src.governance
Governance OK: 16 systems, 66 documents, 8 memories, 95 backlog phases

uv run python -m src.governance --catalog | diff docs/08-governance/catalog.md -
catalog in sync

uv run pytest
290 passed, 2 warnings in 2.01s

uv run mypy src/
Success: no issues found in 11 source files
```

`uv run ruff check src/ test/ tools/` reports one failure:

```
F541 f-string without any placeholders
 --> tools/load_context.py:101:9
```

It is pre-existing, last touched in the commit “docs: add dynamic HTML generation implementation plan”, untouched by this session and outside this phase's
scope. It is left failing rather than fixed quietly in an unrelated commit.

## Unresolved

- **Whether `phase-gov-03` should be promoted in `next_up`.** The complexity review gates
  `phase-idea-07` and `-08`, and it is queued two phases deep behind `phase-gov-02` and
  `phase-term-02`. It is also the review most likely to challenge the area-folder rule this session
  added. This is the owner's call and the most consequential open item in the plan set.
- ~~Whether that one exception file should stay tracked.~~ **Decided: it stays.** The
  owner ruled it stays where it is for now, as a permanent exception in `.gitignore`. `_tmpagent/` is
  the route for new cross-worktree files from here on; this one is not being moved to prove the rule.
  (It was later deleted once its phase completed and the exception no longer applied.)
- The open questions inside each category child stand: nested amendment precedence, whether an
  amendment reason is mandatory, identity encoding, and the initial promotion target kinds.
- `phase-idea-02`'s scope still needs updating before it executes, so the triage agent writes
  findings through the sanctioned writer instead of having nowhere to put them.
