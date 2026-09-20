---
schema_version: 1
id: doc-session-taxonomy-rulings-and-req026-amendment
code: SESS-2026-09-20-01
title: Owner rulings on the session-type theory's open questions, and the REQ-026 R02 amendment
kind: session
status: active
owner: repository-owner
created: '2026-09-20'
updated: '2026-09-20'
systems: [sys-governance]
depends_on: [doc-session-taxonomy-investigation]
---

# Owner rulings on the session-type theory's open questions, and the REQ-026 R02 amendment

## Phase

Unclaimed — owner-directed work, no backlog phase. `taxonomy-rulings-req026` — settle the five open
questions the session-type theory (`phase-tax-01`) left for the owner, record the rulings in the
working document, and correct the `REQ-026` R02 wording defect that `phase-tax-01`'s independent
reviewer raised.

Peers hold no lock against this session. It follows `phase-tax-01`'s close and precedes
`phase-tax-02`'s claim; both its deliverables are inputs that phase consumes.

## Verification

The three repository-wide gates, because nothing declared a narrower list.

**1. `uv run python -m src.governance`**

```
Governance OK: 35 systems, 298 documents, 26 memories, 288 backlog phases
```

**2. `uv run pytest`**

```
638 passed, 2 warnings
```

**3. `uv run python tools/check_no_private_content.py` (changes staged)**

```
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (740 tracked files, 0 identifiers checked)
```

**Partial, as it always is in a worktree.** The identifier list derives from gitignored
`_private/portfolio/`, which no worktree carries, so the content half did not run. The conclusive
run belongs in the primary checkout at integration, where the same command checks 31 identifiers.
`phase-tax-01` recorded the identical limitation and its conclusive run passed.

## Acceptance

Self-declared from the owner's instruction; no backlog acceptance list exists for this session.

- **All five of the theory's §8 open questions are answered by the owner and recorded where Part 2
  will find them** — **Met.** Five rulings appended as §11 of
  `docs/00-working/session-types-theory.md`, each naming what was ruled, why, and its consequence
  for scoring.
- **The rulings change how the theory is measured, not what it predicts** — **Met.** §11 opens by
  stating this, and no type, prediction, disconfirming observation or frequency band in §4 was
  edited. Verified by diff: the only change to the theory document is an append after §10.
- **`REQ-026` R02 states whether a dispatched sub-agent counts as "the session"** — **Met.** R02 now
  says it does, in terms, and names the registration boundary as the commit adding the theory
  document.
- **The amendment does not retroactively move the bar `phase-tax-01` was judged against** — **Met.**
  R02 carries a dated amendment note saying so explicitly and citing the evidence the reviewer
  verified independently.
- **Governance and the test suite stay green** — **Met.** See `## Verification`.

## Backlog

Unclaimed — no backlog phase was claimed for this session; no line of `backlog.yaml` was changed.

## Decisions

**The five rulings**, in the owner's words as settled through `AskUserQuestion`:

1. **Unit of analysis — two labels per session.** An entry type from the first prompt and a dominant
   type from activity. Not one label, not full segmentation. This is the ruling Part 2's design most
   depends on: it makes `S3` a direct count, makes `S4` a cross-tabulation, and rescues every
   prediction phrased as "common as a segment, uncommon as a session" without requiring transcript
   segmentation.
2. **Family A is exempt from session records entirely.** Not a cheap one-line append. The accepted
   cost is stated rather than glossed: if `S1` confirms, the repository's records are a minority of
   its sessions.
3. **Governance gets an identification rule, not a protocol.** B6 stays a type; its binding is a
   router rule that recognises "from now on" and refuses, rather than a fourth obligation profile
   in `REQ-023`.
4. **C4 Rehearsal is kept and scored**, knowing disconfirmation by absence is its likely outcome,
   because that absence would itself be the finding.
5. **Frequency bands are scored over both populations, separately.** This one **departs from the
   recommendation put to the owner**, which was transcripts alone. Scoring both makes `S1` a measured
   difference between two columns rather than an inference, at the cost of a two-column scorecard and
   the possibility that a prediction confirms in one population and disconfirms in the other — which
   §11 rules is a result to report, not a conflict to resolve.

**Recording the rulings in the working document rather than in an ADR or `GOV-003`.** The owner's
choice. `PLAN-042` states that nothing under it creates governed policy, so an ADR would cut against
the plan's own framing; and these rulings bind one investigation rather than future sessions
repository-wide, which is what `GOV-003` is for. Keeping them beside the questions they answer also
means they travel with the theory into Part 2.

**Amending `REQ-026` rather than leaving the ambiguity for Part 2 to interpret.** R02 said "the
session" without saying whether a dispatched agent counted, where `R06` addresses sub-agents
explicitly — so the omission could be read either way. `phase-tax-02` dispatches sub-agents by
design, which is exactly where an ambiguous exclusion becomes load-bearing.

**Stating the boundary as a commit rather than a moment.** R02's new paragraph names the commit that
adds the theory document as the point after which the exclusions no longer bind, and points at git
author dates as the independent check — because they survive a rebase where committer dates do not.
That is a fact `phase-tax-01` learned the hard way, and R02 now carries it so the next session does
not have to rediscover it.

## Corrections

None this session.

One from `phase-tax-01` is worth carrying forward rather than restating: a branch-local artifact must
not be identified by a commit hash, because the branch's own integration rewrites it. R02's amendment
identifies the boundary by what the commit *does* — adds the theory document — for that reason.

## Left undone

**`phase-tax-02` is not claimed or started.** It is the next step the owner asked for and runs as its
own session with its own claim and worktree, per `AGENTS.md`. It sits at queue position 3 behind
`phase-conc-03` and `phase-conc-02`.

**`REQ-026` R03–R06 were not reviewed for the same class of defect.** The reviewer raised R02's
ambiguity because that was the condition under examination. R06 already names sub-agents explicitly
and needs nothing; R03, R04 and R05 were not audited for whether they say "the session" where they
mean "the session and its agents". Worth a pass before Part 2 dispatches anything, and deliberately
not done here because it was outside what the owner asked for.

**`dev` is far ahead of `origin/dev`** and this session did not push. Pushing the trunk has not been
authorised and is not covered by the standing permission to push an agent branch.

## Unresolved

- **This session is unclaimed**, so no `backlog.yaml` line records that the work happened. The
  rulings are discoverable only through the working document and this record. That is the correct
  handling under `AGENTS.md`'s provision for owner-directed work — noted because a reader looking for
  a phase will not find one, not because a phase should have been manufactured.
- **The staged private-content check has not had its conclusive run** — see verification 3. Owed in
  the primary checkout at integration.
