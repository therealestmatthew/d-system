---
schema_version: 1
id: doc-session-close-2026-09-06
code: SESS-2026-09-06-03
title: Session close, protocol gaps and unphased work
kind: session
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-backlog]
depends_on: [doc-session-lifecycle, doc-code-reservation-enforcement]
---

# Session close, protocol gaps and unphased work

Covers the work in this session that belongs to **no claimed phase**. The two phases executed have
their own records: [SESS-2026-09-06-01](SESS-2026-09-06-01-capture-definition.md) for `phase-cap-01`
and [SESS-2026-09-06-02](SESS-2026-09-06-02-structure-content-boundary.md) for `phase-priv-01`. This
record exists because unphased work is otherwise invisible to the backlog, and the owner directed all
of it.

## Why this work was unphased

The owner asked, at session end, whether anything decided in conversation remained undocumented. The
audit that followed found three gaps. Fixing them meant editing governed documents outside any
phase's declared `deliverables` — which `AGENTS.md` forbids without widening the declarations first.
Two of the three were resolved by creating or widening a phase rather than by editing outside one;
the third was recorded rather than fixed.

## What was done

**1. The primary-checkout deviation was recorded.** Both phases today ran in the primary checkout on
`dev`, which `AGENTS.md` prohibits unconditionally. The owner approved it, but only in conversation,
and `SESS-2026-09-05-02` shows the same deviation happening previously — a pattern nobody had written
down. The reasoning and its limits are now in
[GOV-003](../08-governance/GOV-003-backlog-decisions.md): a worktree is required whenever a peer holds
an active claim or the phase touches `src/`, `ts/`, `schemas/`, `sql/`, `tools/` or `test/`, and a
solo agent on a documentation-only phase has nothing to isolate.

**2. The code reservation rule became enforceable.** `GOV-005` already required reserving a code when
a backlog phase names it as a deliverable. `PLAN-006` claimed `ADR-007` in prose without reserving it,
so `--next-code` issued the code elsewhere and the collision only surfaced when the boundary ADR was
written. [PLAN-010](../01-plans/PLAN-010-code-reservation-enforcement.md) and `phase-gov-01` add the
check. It was given its own plan rather than attached to `PLAN-004`, whose scope is source integrity
and projection reliability — filing a governance check there would have been misattribution.

**3. `phase-ses-03` was widened.** It already owned rescoping the worktree and rebase steps in the
hand-off section. The blanket primary-checkout prohibition in the *worktree* section has the same root
cause — rules written for a worktree-and-remote setup that does not exist — so splitting it across two
phases would have left `AGENTS.md` contradicting practice whichever ran first. `GOV-001` was added to
its deliverables.

**4. The closing procedure was written down.** Closing had been done from memory every session, which
is how both `AGENTS.md` and `docs/03-sessions/README.md` came to prescribe a session filename format
the validator rejects. The procedure actually followed is now a section in
[OPS-001](../08-governance/OPS-001-operations.md), marked **interim**: `phase-ses-03` replaces it and
`phase-ses-01` decides the session-type taxonomy, so it documents observed practice rather than
pre-empting either decision. It covers the incomplete-session path and owner-directed unphased work,
both of which still produce a record. The sessions README was corrected to the code-prefixed name.

## Verification

```
uv run python -m src.governance
Governance OK: 15 systems, 40 documents, 7 memories, 78 backlog phases

uv run pytest
110 passed, 2 warnings
```

Checked directly rather than assumed: `git status` clean, `--ready` reports 0 active claims, and
`grep -rn "source of truth"`, `grep -rn "primary checkout"` and a search for codes claimed in prose
were each run to confirm no further instance existed. No other code is claimed in prose anywhere in
`docs/`.

## Deviation from AGENTS.md

This work ran in the primary checkout on `dev` under no phase claim, at the owner's direction. Both
facts are stated here rather than left implicit. The procedure added to OPS-001 now says explicitly
that owner-directed unphased work produces a session record, so the next occurrence has a rule to
follow instead of a precedent to infer.

## Unresolved

- **`AGENTS.md` still contradicts practice** until `phase-ses-03` runs. A fresh agent reading it will
  believe a worktree is mandatory. `GOV-003` is the only thing currently recording otherwise.
- **`PLAN-010`'s open question**: whether the reservation check should also scan plan *prose*, which
  is where the actual failure occurred. Deferred until the deliverables check is in place and it is
  known whether prose claims recur.
- **`phase-ses-01` gates the session work.** Both `phase-ses-02` and `phase-ses-03` wait on it, so the
  interim procedure stands until the taxonomy is decided.
