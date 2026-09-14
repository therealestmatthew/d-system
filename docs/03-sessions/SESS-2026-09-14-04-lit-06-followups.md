---
schema_version: 1
id: doc-session-lit-06-followups
code: SESS-2026-09-14-04
title: Post-phase-lit-06 follow-ups — a backlog regression guard, a targeted search phase, and one tool defect
kind: session
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems:
- sys-backlog
- sys-governance
- sys-research
depends_on:
- doc-backlog-status-regression-guard
- doc-backlog-status-regression-guard-plan
- doc-lit-campaign
---

# Post-phase-lit-06 follow-ups

**Phaseless session.** Owner-directed work with no backlog phase to claim — all three claim slots
were held (`phase-demo-07`, `phase-kit-02`, `phase-part-01`) when it started, so it ran unclaimed
per `AGENTS.md`, on `agent/lit-06-followups`. Peers held no lock against it. The two phases it
created were created `queued`; neither was claimed or worked.

It follows [SESS-2026-09-14-01](SESS-2026-09-14-01-literature-review-pass-3.md), which closed
`phase-lit-06`, and exists because the owner selected three of that session's proposed next steps.

## Phase

None. See above.

## Verification

`uv run python -m src.governance`

```text
Governance OK: 20 systems, 214 documents, 24 memories, 150 backlog phases
exit 0
```

`uv run pytest`

```text
580 passed, 2 warnings
```

`uv run python tools/check_no_private_content.py`, with changes staged, in the worktree

```text
check_no_private_content: OK (585 tracked files, 0 identifiers checked)
exit 0
```

**Not a verification.** `_private/` is gitignored and absent from a worktree, so the identifier
list is empty. The real run happened in the primary checkout during this session's integration
work — **573 tracked files, 31 identifiers checked**, exit 0 — which is the first time in the
campaign's six sessions that check ran anywhere it could actually see anything.

## Acceptance

No phase, so no acceptance list. What the owner asked for, and whether it was delivered:

- **The `000224` governance fix** — delivered as specification, not implementation. `REQ-010`
  (five requirements, each with a verification method), `PLAN-038`, and `phase-gov-05` queued.
  Implementation is the phase's own work.
- **Push `dev` to `origin`** — found already satisfied at the time it was checked. A peer session
  had pushed `dev` as part of its own integration, and `86baa11` was an ancestor of the published
  `fa60fc4`. `dev` has since moved again and is **8 commits ahead of `origin/dev`**, unpushed;
  three of those commits are peers' work.
- **An eighth search session before synthesis** — delivered as a queued phase, `phase-lit-08`, not
  executed. `phase-lit-07`'s `depends_on` now names it, so synthesis is gated behind it.

## Backlog

Two phases added, both `queued`, neither claimed:

- **`phase-gov-05`** — fail the governance check when a phase silently leaves `complete`.
  Priority 2, no dependencies. `--ready` shows it conflicting with `phase-part-01`, which holds
  `sys-backlog`/`sys-governance`; that resolves when that claim releases.
- **`phase-lit-08`** — Pass 3b, targeted collision search for H1, H4 and H11. Depends on
  `phase-lit-06`.

One existing phase edited: `phase-lit-07` gained `phase-lit-08` in its `depends_on`.

**`phase-lit-08` is numbered 08 but runs before 07.** Ids are allocated in creation order;
execution order is the dependency chain. This is stated in the phase's own `scope` so nobody
reads the numbering as the order.

## Unresolved

- **`REQ-010` leaves one question open for the owner**: whether the guard compares the working
  copy against `HEAD` or against `dev`. `HEAD` is narrow and quiet — it catches the bad edit as it
  is made, which is the case that occurred, and stays silent otherwise. A `dev` comparison also
  catches a regression arriving by merge, but fires on every agent branch that legitimately
  completes a phase, and a check that cries wolf on correct work is one agents learn to ignore.
  `PLAN-038` proceeds on `HEAD` and says plainly that it would **not** have caught `5ecb203` at
  merge time. `phase-gov-05`'s `next_action` carries the same question so it is visible at pickup.
- **`agent/lit-06-followups` is unmerged**, 2 commits. Integration is the owner's call.
- **`dev` is unpushed**, 8 commits, three of them peers'.

## What was done

**`REQ-010` and `PLAN-038`.** The guard specified in response to idea `000224`. The design point
worth carrying forward is the escape hatch: a `complete → queued` transition is permitted when the
same change adds a `GOV-003` entry naming that phase. Reopening a finished phase is legitimate and
has happened; the defect was never that a phase moved backwards, only that it moved backwards
*silently, inside a diff about something else*. A hard prohibition would be worked around; a
prompt to write the reason down routes it through the record that already exists.

**`phase-lit-08`.** Queued on the owner's direction because `phase-lit-06` left H1, H4 and H11 at
`INSUFFICIENT_EVIDENCE` under a rule that distinctness requires search saturation, and the
measured 20.0% duplicate rate does not show it. H1 has never had a dedicated collision search
across six phases; H4 had one; H11 lost its only challenger when `burns-groth` was found to
describe its own future work. Synthesis cannot honestly characterise what remains while those
three rest on searches that never targeted them.

**Idea `000231`** — `tools/generate_glossary.py:119` prints `len(entries)`, the count loaded
before `render()` applies its tag and system filters, so a filtered run reports the same number as
an unfiltered one. Reported by the `phase-demo-07` session, which hit it using the count as
evidence: "9 term(s)" for both a 61-heading unfiltered glossary and an 18-heading filtered one.
Verified from source before recording rather than taken on report.

## Corrections

**A document id was invented rather than looked up.** `REQ-010` and `PLAN-038` were written with
`depends_on: doc-multi-agent-concurrency`; the real id is `doc-adr-multi-agent-concurrency`. The
governance check caught it, twice — once for the documents and once for the phase's `sources`
list. Fixed before commit. `AGENTS.md`'s rule against picking a code by reading a directory has an
obvious sibling that is not written down: do not guess a document id either.

**A peer session was messaged on a wrong premise.** The owner reported `phase-wb-07` as closing in
another session and asked for a conflict check. No such session existed: `phase-wb-07` was never
claimed, sat `blocked` with `agent: None` since 2026-09-11, and cannot be closed by any agent —
its remaining acceptance is owner-machine only (R06 smoke check, CMD/PowerShell round-trips, two
timed dry-runs). It was moved `blocked → queued` today by the `phase-demo-07` session on the
owner's instruction, its resume condition having been met. The message was sent to `d-system-37`,
identified as the only busy interactive session; that session turned out to be `phase-demo-07`,
not `phase-wb-07`. The warnings it carried were used and reported useful, but the targeting was
luck. The session actually named for that work, `w07-w-playwright-verification`, was offline and
received nothing.

## Left undone

**Both new phases are unstarted, deliberately.** `phase-gov-05` and `phase-lit-08` are
specification and queue entries. Neither was claimed — all three slots were full, and claiming a
phase this session could not finish would have locked a slot against peers for no gain.

**The guard is not implemented.** `REQ-010` and `PLAN-038` describe it; `src/governance/` is
untouched. That is `phase-gov-05`'s work and it should not start before the owner answers the
`HEAD`-versus-`dev` question, because the answer changes the acceptance.

**No audit for past regressions.** `PLAN-038` says so explicitly: the
`phase-lit-03`/`04`/`05`/`06` reversal was repaired by hand in `b319b7a`, no other instance is
known, and looking for more is a separate question from preventing the next one.

## Resume state

**Next in the campaign**: `phase-lit-08`, then `phase-lit-07`. `PROMPT-031` carries the dated
pre-synthesis check-in entry, so `phase-lit-07` is unblocked on that condition — but it now also
depends on `phase-lit-08`, which is not done.

**Next outside it**: `phase-gov-05`, once a claim slot frees and the owner has answered
`REQ-010`'s open question.

**The `lit-campaign` worktree must be retained.** `PLAN-023`'s branch model is one long-lived
campaign branch; `phase-lit-08` and `phase-lit-07` both commit to it. `agent/lit-campaign` is 0
ahead of `dev` and fully merged, which makes it look disposable — it is not. Removing the worktree
would also destroy its gitignored `.venv` and `data/`, which no merge carries.

**A fresh session must read**: `AGENTS.md`, `GOV-006`, then
[SESS-2026-09-14-01](SESS-2026-09-14-01-literature-review-pass-3.md) for the campaign's state and
the eight check-in rulings, then this record for what was queued after it.
