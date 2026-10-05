---
schema_version: 1
id: doc-session-coordinator-dispatched-review
code: SESS-2026-10-05-04
title: 'Coordinator-dispatched build review wired into session-close, PROMPT-036, GOV-017 and PROMPT-037'
kind: session
status: active
owner: repository-owner
created: '2026-10-05'
updated: '2026-10-05'
systems: [sys-governance, sys-gov-docs]
depends_on: [doc-reviewer-contract]
---

# Coordinator-dispatched build review wired into session-close, PROMPT-036, GOV-017 and PROMPT-037

## Phase

`phase-asr-04` — Coordinator-dispatched build review wired into session-close, PROMPT-036, GOV-017
and PROMPT-037. Claimed by agent-standby-3 (Session 3 - Standby Builder) on the Session Manager's
overnight ASSIGN; claim commit `9fe43d8` on `dev`.

## Verification

All run in the worktree on `agent/phase-asr-04` at `d59b026`, rebased onto `dev` `07fe6bb`.

`uv run pytest test/test_review_verdict.py`:

```
44 passed, 1 warning in 0.08s
```

The verdict-record tests include `test_committed_verdict_record_is_valid_and_named_by_its_id`, which
had skipped while `reviews/verdicts/` held no records. It now validates the six records committed
here.

`uv run python -m src.governance --catalog`: exit 0.

`uv run python -m src.governance`:

```
Governance OK: 45 systems, 442 documents, 37 memories, 347 backlog phases
```

`git diff --exit-code docs/08-governance/catalog.md`: exit 0.

The six verdict records at this tip, each `git show <tip>:<path> | sha256sum` compared with the
Session Manager's ledger: all six `OK`.

## Acceptance

- PROMPT-036's Validator and Adversary templates name a dedicated reviewer type and do not inherit
  the shared intro's `general-purpose` charter; the Creator and Blocker resolver templates are
  unchanged — **Met.** The intro now says only the Creator and Blocker resolver name
  `general-purpose`. The Validator names `demo-validator-code` and the Adversary names
  `demo-adversary`. The Creator and Blocker resolver paragraphs have no diff.
- GOV-017 states the dispatch rule and names what the brief may not contain — **Met.** "Build
  reviews" has the rule, the brief's four items, and the list of what it may not hold.
- Demonstrated once: an unchanged record's sha256 matches the recorded value, and a copy with one
  finding edited does not and is refused, naming the file — **Met.** See *Demonstration* below. The
  shadow judge noted (round 3, F02) that this evidence was not among its inputs. It is here in the
  record, which by design reviewers do not read.
- `session-close.md` step 3 lists no input the building session wrote — **Met.** A building session
  sends only the branch and tip. The dispatching path's brief lists the backlog entries, the range
  and its diff, the manifest and a coordinator-made clone, and step 3 bars the session record,
  commit messages and `git log`.
- GOV-017's message table has the two new messages, and its merge gate names the runner, the gating
  reviewer and the shadow judge — **Met.** `REVIEW-REQUEST` and `VERDICT` are in the table. Merge
  gate steps 1-3 name `tools/run_review_checks.py`, the gating reviewer and `review-judge`.
- This phase's own review produces a gating verdict record and a shadow judge verdict record,
  applied by hand by the coordinator — **Met.** Three rounds produced six records, three gating and
  three shadow, all committed unchanged and all matching the ledger.

## Backlog

`status: active`, `agent: agent-standby-3`, `session: doc-session-coordinator-dispatched-review`.
`next_action`: "Built and reviewed on agent/phase-asr-04 (SESS-2026-10-05-04); waits for the
owner-approved merge and the completion edit on dev." `completion_evidence` and `result` are written
in the completion edit on `dev`, after the merge.

## Unresolved

- The merge needs the owner if the classifier refuses it. Earlier tonight the auto-mode permission
  classifier refused a fast-forward of `dev` ("Modify Shared Resources") despite a relayed `GRANTED`.
- Owner ruling P4: the new flow takes effect from the next run's starters. Sessions already running
  keep the flow their starters gave them, and `PROMPT-037` says so.

## Review

This phase's review followed the procedure it writes, applied by hand by the Session Manager as
coordinator. The building session sent `REVIEW-REQUEST` with the branch and tip only. The Session
Manager ran the runner, dispatched `demo-adversary` as the gating reviewer and `review-judge` in
shadow, staged the verdict records, and sent `VERDICT`. Each record is committed unchanged under
`docs/08-governance/reviews/verdicts/`.

Verdict records, all under `docs/08-governance/reviews/verdicts/`:

| Round | Commit | Gating `demo-adversary` | Shadow `review-judge` |
|---|---|---|---|
| 1 | `7fa9a3e` | `2026-10-05-phase-asr-04-demo-adversary.json`: **reject**, F01 blocker, F02 major, F03 major | `2026-10-05-phase-asr-04-review-judge.json`: pass, no findings |
| 2 | `820821e` | `2026-10-05-phase-asr-04-demo-adversary-2.json`: **reject**, F04 blocker; F01-F03 resolved | `2026-10-05-phase-asr-04-review-judge-2.json`: pass, F01 minor |
| 3 | `3b591a8` | `2026-10-05-phase-asr-04-demo-adversary-3.json`: **pass**, F05 minor | `2026-10-05-phase-asr-04-review-judge-3.json`: pass, F01 minor, F02 minor |

The gating findings, as the reviewer titled them:

- **F01 (blocker):** "GOV-017 never says where the Session Manager physically writes a verdict record
  before the builder has it." Fixed: the staging directory
  `_working/session-manager/verdicts-pending/<phase-id>/`, in GOV-017 and `/session-close`.
- **F02 (major):** "The merge-gate verdict-sha check names a checkout that has already been deleted,
  with no disambiguation." Fixed: the check reads the commit with `git show <tip>:<path> | sha256sum`.
- **F03 (major):** "PROMPT-036's Validator template does not carry the coordinator brief the intro
  paragraph says it does, and the scope required both templates to." Fixed: the Validator is
  described as step 4's check, distinct from step 6's build review.
- **F04 (blocker):** "GOV-017's brief and session-close.md's mirror omit a checkout of the branch,
  which both gating reviewer types require, while PROMPT-036's templates add 'the worktree path' and
  call it the GOV-017 brief." Fixed: a fourth brief item, the coordinator-made scratch clone, for
  the gating reviewer only.
- **F05 (minor):** "The bar on reading the builder's session record and git log inside the gating
  reviewer's scratch clone is a prompt instruction, not a technical control." Accepted: GOV-017
  states it as an instruction. The gating record notes that the reviewer read two commit subject
  lines through `git log` against the brief and used neither as evidence.

Shadow findings, which decide nothing:

- Round 2 F01 (minor), scope bullet 4's wording is looser than what was built. Accepted: it concerns
  the backlog phase's own text, not the diff.
- Round 3 F01 (minor), `demo-adversary.md` and `demo-validator-code.md` still say "worktree path".
  Accepted here because `.claude/agents/` is outside the deliverables; recorded as idea `000588`.
- Round 3 F02 (minor), acceptance 3 not evidenced to the judge. Accepted: the demonstration is in
  this record, which reviewers do not read.

## Demonstration: the verdict-record check (`REQ-030` R10)

Run on the round-1 records at the branch commit that held them. Each committed record's
`git show <tip>:<path> | sha256sum` is compared with the Session Manager's recorded value in
`_working/session-manager/verdicts.sha256`. Then a copy of the gating record, with F01's severity
edited from `blocker` to `minor`, is checked the same way and with `sha256sum -c`:

```
--- R10 demonstration on the round-1 records, committed at 7685b1b ---
docs/08-governance/reviews/verdicts/2026-10-05-phase-asr-04-demo-adversary.json recorded=ade51c674076b3075dfe79073249d4e438ccc4b5a198d0b501f8167fd2ff3a38 committed=ade51c674076b3075dfe79073249d4e438ccc4b5a198d0b501f8167fd2ff3a38 OK
docs/08-governance/reviews/verdicts/2026-10-05-phase-asr-04-review-judge.json recorded=3324bedbbf1bac6a11a20474610202f222d684f22076c7d5b6683d52c77ef8be committed=3324bedbbf1bac6a11a20474610202f222d684f22076c7d5b6683d52c77ef8be OK
--- copy with one finding edited ---
docs/08-governance/reviews/verdicts/2026-10-05-phase-asr-04-demo-adversary.json (edited copy: F01 severity blocker->minor) recorded=ade51c674076b3075dfe79073249d4e438ccc4b5a198d0b501f8167fd2ff3a38 copy=2d72126f4d2ed3f7a17ace514fc133454f9137f49fcd83c37aef98acbd65b2aa REFUSED: docs/08-governance/reviews/verdicts/2026-10-05-phase-asr-04-demo-adversary.json differs
docs/08-governance/reviews/verdicts/2026-10-05-phase-asr-04-demo-adversary.json: FAILED
sha256sum: WARNING: 1 computed checksum did NOT match
```

The unchanged records match. The edited copy does not, and the check refuses it, naming the file.

## Decisions

- **Where a verdict record waits before handover (round-1 F01).** The coordinator writes it to
  `_working/session-manager/verdicts-pending/<phase-id>/` in the primary checkout. That path is
  gitignored, so the write needs no turn. The runner's worktree is gone by then, and writing onto
  `dev` would put an unmerged phase's record there. The builder copies the record unchanged onto
  its branch, as `PLAN-047` D4 places it.
- **The merge-gate record check reads the commit, not a checkout (round-1 F02).**
  `git show <tip>:<path> | sha256sum` in the primary checkout reads the committed blob. It needs no
  worktree after the runner removes its own, and it does not bring back the separate
  detached-worktree re-run the runner replaces.
- **PROMPT-036's Validator is not the build review (round-1 F03).** The Validator is step 4's check
  inside the creator's fix cycles. The Adversary is step 6's gating build reviewer under `GOV-017`'s
  brief. Both are dedicated types, and neither gets anything the creator wrote.
- **OVERNIGHT ASSUMPTION: the gating reviewer's checkout (round-2 F04).** It is a scratch clone at
  the reviewed commit, made and removed by the coordinator, never the builder's worktree. The brief
  tells the reviewer not to read the phase's session record or `git log`, because a checkout
  contains both. The shadow judge has no shell and gets no checkout. This follows the Session
  Manager's note and the owner's 2026-09-23 ruling that withheld the record from reviewers.
- **OVERNIGHT ASSUMPTION: claim narrowing.** `docs/08-governance/` was narrowed to `GOV-017` and
  `reviews/verdicts/`, inside the phase's original declaration. `GOV-002`, `GOV-018` and the
  top-level review records stay with parked `phase-grd-04`.
- **Unclaimed work keeps the detached-worktree re-run at the merge gate.** The runner needs a phase
  id to read a `verification` list, and unclaimed work has none.
- **No `OPS-029` or `OPS-030` edit.** Both already describe the runner and the sampler as this text
  uses them. `OPS-030` already states that a sampled re-review is recorded with `gating: false`, and
  `GOV-017` now says the same.

## Corrections

- Adding `doc-reviewer-contract` to `GOV-017`'s `depends_on` made a dependency cycle (`PLAN-047`
  depends on `GOV-017`); reverted at once.
- Two review rounds rejected the first texts (F01-F03, then F04). Each was fixed and re-reviewed,
  not accepted.

## Left undone

Nothing in scope. The completion edit on `dev` follows the owner-approved merge.
