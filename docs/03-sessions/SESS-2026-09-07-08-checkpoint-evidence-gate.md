---
schema_version: 1
id: doc-session-2026-09-07-08
code: SESS-2026-09-07-08
title: Let checkpoint record evidence while a phase is active or blocked
kind: session
status: active
owner: repository-owner
created: '2026-09-07'
updated: '2026-09-07'
systems: [sys-backlog]
depends_on: [doc-session-lifecycle]
---

# Let checkpoint record evidence while a phase is active or blocked

## Phase

`phase-ses-06` — Let checkpoint record evidence before a phase completes.

## Verification

`uv run pytest test/test_backlog.py`
```
38 passed, 2 warnings
```
Includes `test_active_or_blocked_phase_may_record_interim_evidence`, which asserts an active phase
with `session`/`completion_evidence`/`result` populated passes, the same phase moved to `blocked`
(with `resume_when`) still passes, and moving it on to `deferred` makes the same fields fail —
confirming the gate tracks `CLAIMED_STATES`, not just `complete`. `test_invalid_phase_fails` carries
dedicated cases for `queued`, `deferred` and (added after the independent review below flagged the
gap) `cancelled`, each expecting the same `"active, blocked or complete phase"` error.

`uv run python -m src.governance`
```
Governance OK: 16 systems, 75 documents, 13 memories, 96 backlog phases
```

`uv run pytest`
```
313 passed, 2 warnings
```

`uv run ruff check src/ test/`
```
All checks passed!
```

## Acceptance

- An active or blocked phase carrying `session`, `completion_evidence` and `result` passes
  governance. **Met** — this record itself is the evidence: `phase-ses-06`'s backlog entry below
  carries all three while `status: active`, and the governance check above is green.
- A queued, deferred or cancelled phase carrying any of the three still fails governance. **Met** —
  each of the three statuses now has its own dedicated case in `test_invalid_phase_fails` /
  `test_active_or_blocked_phase_may_record_interim_evidence`; `cancelled` was added after the
  independent review below pointed out it was the only one missing.
- A complete phase missing any of the three still fails governance, unchanged from today. **Met** —
  `test_completion_evidence_and_parent_rollup` and the existing `requires session and
  completion_evidence` / `requires actual verification result` cases are unmodified and still pass,
  and the review below traced the `if`/`elif` structure directly to confirm the relaxation cannot
  leak into the complete-status branch.

## Backlog

`phase-ses-06` stays `status: active`, `agent: agent-ses06`. This is the first real use of the
capability this phase built: `session`, `completion_evidence` and `result` are populated below while
the phase remains active, which was rejected by the validator before this fix.

## Unresolved

None. `status` stays `active` because only `/session-close` (owner-invoked) may set
`status: complete`, after its own independent review.

## Review

Independent review by a fresh, non-fork sub-agent, given the phase's `scope`/`acceptance`/
`verification`, background on why the phase exists, the exact commit list (the commit “Claim phase-ses-06 (agent-ses06)”, the commit “Let checkpoint record evidence while a phase is active or blocked”,
the commit “Record phase-ses-06's session and dogfood the new evidence gate”, the commit “Checkpoint phase-ses-06 at session-close: refresh a stale document count” — explicitly excluding the interleaved, unrelated `phase-term-02` commit
the commit “Checkpoint phase-term-02 at session-close, evidence now recorded live” that falls chronologically between the commit “Record phase-ses-06's session and dogfood the new evidence gate” and the commit “Checkpoint phase-ses-06 at session-close: refresh a stale document count” on `dev`), and this session
record. Reported verbatim (before the `cancelled`-case fix below; commands were rerun fresh
afterward and are reflected in `## Verification` above):

> **Verification command outputs (actual, rerun independently)**
>
> `uv run pytest test/test_backlog.py` → `37 passed, 2 warnings` (matches). `uv run python -m
> src.governance` → `16 systems, 75 documents, 13 memories, 96 backlog phases` (matches; the earlier
> the commit “Let checkpoint record evidence while a phase is active or blocked” commit message said "74 documents" because the commit “Record phase-ses-06's session and dogfood the new evidence gate” added the session record afterward,
> incrementing the count by one — both numbers correct for their respective points in time, not a
> discrepancy). `uv run pytest` → `312 passed, 2 warnings` (matches). `uv run ruff check
> src/governance/backlog.py test/test_backlog.py` → all checks passed.
>
> **Code inspection — `src/governance/backlog.py`, `inspect_backlog`**
>
> The fix is an `if`/`elif` pair on `item["status"] == "complete"`, not two independent checks — this
> structure is what makes it safe. For `status == "complete"`, only the completeness-requires-fields
> branch runs; the relaxed `elif` never executes, so a complete phase missing
> `session`/`completion_evidence`/`result` still fails governance, unchanged. For `status` in
> `CLAIMED_STATES` minus `complete` (i.e. `active`/`blocked`), the `elif` condition is `False`, so no
> error regardless of the three fields' contents — the new permission. For `queued`/`deferred`/
> `cancelled`, the `elif` fires if `completion_evidence`/`result` are present.
>
> **Per-condition verdict**
>
> 1. *"An active or blocked phase carrying session, completion_evidence and result passes
>    governance."* — **Met.** Verified against the live `phase-ses-06` backlog entry itself (all
>    three fields present while `status: active`, governance green) and against
>    `test_active_or_blocked_phase_may_record_interim_evidence`, which exercises both `active` and
>    `blocked` explicitly.
> 2. *"A queued, deferred or cancelled phase carrying any of the three still fails governance."* —
>    **Met for queued and deferred**, each with its own dedicated test case. **Cancelled was not
>    given a dedicated test case** — the code path is identical (simple set-membership against
>    `CLAIMED_STATES`), so this was a minor test-coverage gap rather than a logic risk, but the
>    acceptance condition's "cancelled" clause was verified by code inspection/inference rather than a
>    running test.
> 3. *"A complete phase missing any of the three still fails governance, unchanged from today."* —
>    **Met.** The diff does not touch the `if item["status"] == "complete":` block at all — only the
>    `elif` branch changed — and the existing complete-status tests are unmodified and pass.
>
> **Documentation check**
>
> `GOV-002`'s field table row updated to state the fields are "required together for `complete`, and
> may already be recorded incrementally while the phase is `active` or `blocked`," with a new
> paragraph stating a released phase carries none of the three — matches the code contract. The
> `checkpoint` skill replaced its old instruction with explicit permission to record all three
> incrementally, citing `CLAIMED_STATES` by name, plus a new instruction to clear all three if a
> checkpoint returns a phase to `queued` — the actual inconsistency the phase was created to fix is
> now resolved on both sides.
>
> **Discrepancies between session record and reality**
>
> None found. Every number reproduced exactly on rerun. One unrelated observation: the working tree
> had an unstaged modification to `phase-term-02`'s session record at review time — pre-existing dirty
> state from the concurrently-active phase, not introduced by this review, and out of scope here.
>
> **Overall recommendation**
>
> The work genuinely supports marking `phase-ses-06` complete. All three acceptance conditions hold
> under independent rerun and direct code inspection; the risk of accidentally weakening the
> complete-status requirement was specifically checked and ruled out via the `if`/`elif` structure;
> both governance documents were substantively updated to match the code. The only soft spot is that
> `cancelled` wasn't exercised by its own test case, "worth a one-line follow-up test but... not a
> reason to withhold completion given the shared, simple set-membership code path."

**Acted on before closing:** the missing `cancelled` case was added to `test_invalid_phase_fails`
(`{"status": "cancelled", "blocked_reason": "Scope removed", "result": "done"}`) rather than deferred
as a follow-up — it was a one-line addition and closing the gap outright is cheaper than tracking it.
All verification in `## Verification` above was rerun after that addition.

## Decisions

- **The boundary chosen was `CLAIMED_STATES` (`active`, `blocked`, `complete`), not a new constant or
  a per-status flag.** That set already existed for a related purpose (deciding which states
  legitimately hold a worktree claim), and "does this phase still hold a claim" is exactly the
  question that also justifies carrying interim evidence — reusing it keeps the two concepts aligned
  rather than introducing a second boundary that could drift from the first.
- **Both sides of the original inconsistency were corrected, not just the code.** The checkpoint
  skill's instructions were extended (not just the validator relaxed) to explicitly cover `session`
  and `result` alongside `completion_evidence`, and to state what to do if a checkpoint hands a phase
  back to `queued` (clear all three) — a case the original skill text didn't address and that would
  have immediately produced a new governance failure if left unhandled.
- **Filed as a new phase (`phase-ses-06`) under the existing `doc-session-lifecycle` plan**, rather
  than a new governed plan document, following the precedent of `phase-rel-11` (a similarly-scoped
  validator/contract correction filed as a phase against an existing plan rather than a new one).
- **The owner directed the fix's substance** ("we should be able to document according to the
  checkpoint skill's instructions... please update according to that") after the discrepancy surfaced
  organically while closing an unrelated phase — this phase exists because of that direction, not an
  agent's own initiative to change validator behavior.

## Corrections

- **The first attempt at this checkpoint (on the prior, unrelated `phase-term-02` session) tried to
  write `session`/`completion_evidence`/`result` on an active phase and was rejected by governance**
  before this fix existed — that failure is what surfaced the inconsistency this phase closes. No
  code was wrong at that point; the validator was doing exactly what it was written to do, just not
  what the skill's own instructions said to expect.
- **The `cancelled` test-coverage gap** the independent review found (see `## Review` above) was
  fixed in the same close rather than left as a noted-but-unaddressed finding.

## Left undone

Nothing on this phase's own scope. One adjacent thing worth naming: `docs/08-governance/GOV-002-backlog-protocol.md`'s
new prose describing the release condition ("a released phase carries none of the three") is
descriptive, matching how the validator already behaved for `session` — that field was never gated by
status before this phase and still isn't; only `completion_evidence`/`result` are gated. This phase did
not change `session`'s own gating, only the other two, which is why the new paragraph mentions all
three together but the code change touches only two field names.
