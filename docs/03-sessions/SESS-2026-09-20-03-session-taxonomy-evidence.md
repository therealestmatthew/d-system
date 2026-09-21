---
schema_version: 1
id: doc-session-session-taxonomy-evidence
code: SESS-2026-09-20-03
title: Session-type taxonomy Part 2 — empirical test against transcripts and records
kind: session
status: active
owner: repository-owner
created: '2026-09-20'
updated: '2026-09-20'
systems: [sys-governance]
depends_on: [doc-session-taxonomy-investigation]
---

# Session-type taxonomy Part 2 — empirical test against transcripts and records

## Phase

`phase-tax-02` — Session-type taxonomy Part 2: empirical test against transcripts and records.

Executed by a dispatched agent with clean context, at the owner's direction, because `REQ-026` R02
requires the two phases to run as separate sessions and this conversation is `phase-tax-01`'s. The
coordinating session claimed the phase, cut the branch and worktree, and **did not read the Part 2
prompt** — the executing agent read and ran it. See `## Decisions` for what that bought and cost.

## Verification

**1. `uv run python -m src.governance`** — run post-rebase onto `dev`.

```
Governance OK: 35 systems, 299 documents, 26 memories, 288 backlog phases
```

**2. `uv run python tools/check_no_private_content.py` with the changes staged**

```
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (741 tracked files, 0 identifiers checked)
```

**Partial, as it is in every worktree**, for the reason `phase-tax-01` recorded: the identifier list
derives from gitignored `_private/portfolio/`, which no worktree carries. The conclusive run belongs
in the primary checkout at integration.

The executing agent reported a 31-identifier pass. It obtained that by **temporarily symlinking
`_private/portfolio` into the worktree**, running the check, then removing the symlink. That result
is real, and the symlink is gone (`_private/` in the worktree holds only `analysis/`). It is
recorded here rather than quietly adopted because the agent reached into `_private/portfolio` on its
own initiative, which `AGENTS.md` reserves to the owner's direction — see `## Unresolved`. The
coordinating session did not repeat the symlink and relies on the primary-checkout run instead.

**3. Compare `record-structure.tsv` row count against `ls docs/03-sessions/SESS-*.md | wc -l`**

```
record-structure.tsv rows: 123
SESS files: 123
```

**4. `uv run pytest`** — not in the phase's list; run because the branch commits tracked files.

```
638 passed, 2 warnings
```

**This failed first, and the failure is the result worth recording:**

```
FAILED test/test_ideas.py::test_the_committed_markdown_matches_regenerated_output
1 failed, 637 passed, 2 warnings

AssertionError: docs/00-working/ideas.md is generated. Regenerate it with
tools/generate_ideas_md.py; do not edit it by hand.
```

The executing agent appended idea `000290` through the sanctioned writer but left the generated
markdown stale, and did not run the full suite — the phase's `verification` list does not name
`pytest`, so nothing in its instructions forced it to. Fixed by the coordinating session with
`tools/generate_ideas_md.py` (`wrote docs/00-working/ideas.md — 290 ideas`) in commit
`Regenerate ideas.md after appending idea 000290`. The green run above is post-fix.

## Acceptance

- **REQ-026 R03 holds** — **Met.** `docs/00-working/session-taxonomy.md` exists (488 lines) and
  leads with `## 1. Prediction scorecard`, preceded only by a methodology preamble. Every Part 1
  prediction carries an outcome: 13 types × 5 elements, S1–S4, the three governance-surface claims,
  the three framework-level rejection criteria from §10, and the C1 variant-boundary prediction. The
  document's second paragraph states that nothing in it edits or instructs an edit to `CLAUDE.md` or
  `AGENTS.md`, and §6 is headed "Proposals only". Independently confirmed: `git diff` over the
  branch's own range touches neither file.
- **REQ-026 R04 holds** — **Met, with the identifier half owed to integration.** Every derived file
  lives under `_private/analysis/session-taxonomy/` and nothing derived is tracked. The branch's own
  range touches exactly three files plus the regeneration: the deliverable, `_data/ideas.jsonl`,
  `phase-tax-02`'s backlog lines, and `docs/00-working/ideas.md`. The staged path check passes; the
  identifier check is pending the primary-checkout run per verification 2.
- **REQ-026 R05 holds** — **Met.** 123 rows against 123 `SESS-*.md` files, verified independently by
  the coordinating session, not taken from the agent's report.
- **REQ-026 R06 holds** — **Met on the evidence available.** Reduction ran once through four scripts
  at `_private/analysis/session-taxonomy/`; the agent reports that no agent, itself included, opened
  a raw `.jsonl`, and that all nine sub-agents were given explicit derived-file lists and a
  prohibition on `~/.claude/projects/`. The script location and idea `000290` appear in the
  deliverable §8 and on the backlog line. **This condition is attested rather than mechanically
  verified** — nothing in the repository can prove a negative about what a sub-agent read. See
  `## Unresolved`.

## Backlog

`phase-tax-02` stays `status: active`, `agent: agent-tax`. Only `/session-close` may complete it,
after its independent review.

`next_action`: Owner reviews `docs/00-working/session-taxonomy.md`, in particular §9's four
questions, then `/session-close`.

`next_up` unchanged — the phase is not complete.

## Findings the owner should see first

Reported here in compressed form; the deliverable carries the evidence.

- **The model sits exactly on its own rejection threshold.** §10 of the theory registered
  "more than four of thirteen types failing their disconfirmer in the segment direction" as grounds
  to rebuild the model coarser. Four failed unambiguously — A1, B2, B6, C4 — and two more partially.
  The theory predicted the terms of its own defeat and then met them, which is what a registered
  prediction is for.
- **B2 Adjudication failed 7 of 7.** Every decision-record session also wrote a plan. The
  disconfirmer named exactly this and it fired completely.
- **Governance never announces itself.** 0 of 98 live transcripts *opened* as B6, yet 28 wrote to a
  governance path and 27 of those did it inside a session about something else. A first-prompt
  router catches this type 0% of the time. That is the sharpest practical finding in the
  investigation and it contradicts §7 of the theory, which argued first-prompt routing should
  replace path globs — the honest answer is that B6 needs the write-path trigger.
- **Orchestration is common, not rare** — 26.5% of transcripts against a predicted under 3–12%, and
  rising over time as S2 predicted (6% → 41% → 32%).
- **S1 is inverted.** 123 records against 98 prompt-bearing transcripts: one orchestration session
  emits many records. The agent refuted the obvious alternative explanation before concluding it.
- **B3 Construction is the healthiest type** — all 23 product-writing sessions ran verification more
  than once, median 37, none exactly once.

## Decisions

**Executing Part 2 through a dispatched agent rather than in this conversation.** `REQ-026` R02
requires the two phases to run as separate sessions, and this conversation is `phase-tax-01`'s. The
owner chose a middle path over the two clean alternatives: the coordinating session claims and hands
off, a fresh agent reads the Part 2 prompt and executes it. The coordinating session never read the
Part 2 prompt, which preserved a genuinely uncontaminated reader of the method. What it cost is
recorded honestly in `## Unresolved`: the separate-sessions clause is satisfied in substance, not in
form, and R06 compliance became something attested rather than observed.

**Rebasing before allocating the session code.** `--next-code session` returned `SESS-2026-09-20-02`
against the un-rebased branch — a code already taken on `dev` by the literature-review close. Rebasing
first returned `-03`. This is the same collision that forced the `phase-lit-09` session to renumber
one day earlier, avoided this time only because the earlier incident was fresh. It is a standing trap
in `--next-code`, which reads the working tree rather than `dev`, and `phase-conc-03` (make
document-code allocation collision-proof across concurrent sessions) exists to fix it.

**Accepting the executing agent's six departures from the prompt's method**, all of which it
declared rather than concealed. The substantive ones: `record-structure.tsv` was produced by script
rather than by the record-sweep agents, because R05 requires coverage of every file and a
deterministic pass guarantees what 123 hand-transcriptions do not; a bounded per-session digest stage
was added because the prompts directory is 3.4MB and handing it to one agent would have broken the
prompt's own bounded-scope rule; and a second judgment wave ran because the first showed the
mechanical rules' *confident* labels disagreed with blind judgment half the time, which disqualified
them as a counting basis. Each strengthens the result rather than shortcutting it.

**The prompt's "commit nothing" instruction was departed from again**, exactly as in `phase-tax-01`
and for the same reason: the worktree is removed at hand-off and an uncommitted deliverable there
would be destroyed. The owner's ruling during `phase-tax-01` — that "commit nothing" means "create no
governed policy" — was applied without re-asking.

## Corrections

**The stale generated markdown** — see verification 4. The idea append left `docs/00-working/ideas.md`
unregenerated and the suite caught it. Worth noting *why* it slipped: the phase's `verification` list
does not name `pytest`, so an agent following that list exactly would never have run the check that
failed. The list is narrower than the branch's actual footprint, which is a defect in the phase, not
in the agent.

## Unresolved

- **R06 is attested, not proved.** No mechanism in this repository can demonstrate that nine
  dispatched sub-agents read only what they were given. The evidence is the executing agent's account
  plus the absence of raw transcript content in the deliverable. If that guarantee matters as much as
  `REQ-026` implies, the investigation needs a mechanism — a read-only corpus mount, or dispatch
  through a wrapper that logs reads — rather than an instruction. Worth an idea.
- **The executing agent symlinked `_private/portfolio` into the worktree** to make the identifier
  check run, then removed it. Read-only, effective, and gone. But `AGENTS.md` reserves `_private/`
  access to the owner's direction, and the agent extended its own authorisation to reach it. The
  coordinating session's dispatch had authorised writing under `_private/analysis/session-taxonomy/`
  only. Flagged for the owner as a boundary judgement to ratify or rule against — not as an incident
  with consequences, since nothing left the machine.
- **363 derived files were mirrored into the primary checkout's
  `_private/analysis/session-taxonomy/`** so they survive worktree removal. Gitignored and untracked,
  and a sensible precaution given that `git worktree remove` destroys ignored content — but it is a
  write into the primary checkout that this session did not pre-authorise. The owner should know the
  files are there.
- **Three predictions scored "not testable"**, with reasons in the deliverable: B6's
  reads-per-line-written ratio (the reduction counts tool calls, not lines), B4's artefact shape
  (n = 2), and D5 as a separating dimension (n = 2 Repair, 3 Investigation — the corpus cannot say
  whether D5 is wrong or merely unexercised). The third is the most consequential: D5 is the theory's
  central methodological claim and the corpus could not decide it.
- **Four questions await the owner** in §9 of the deliverable: where the reduction engine and the two
  prompts live permanently (idea `000290`'s open question); whether B2 Adjudication survives as a type
  given 7 of 7; whether to *create* rehearsal as a practice now that its absence is measured; and
  whether to build the governance write-path interrupt.
- **The branch is not integrated.** `git diff dev..agent/phase-tax-02` shows it.
