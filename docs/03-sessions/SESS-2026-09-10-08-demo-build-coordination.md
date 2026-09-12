---
schema_version: 1
id: doc-session-demo-build-coordination
code: SESS-2026-09-10-08
title: Demo build coordination — the six-phase demo track from claim to integration
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-demo-stage, sys-demo-overview, sys-api, sys-ui, sys-backlog, sys-governance]
depends_on: [doc-live-demo, doc-prompt-demo-build-orchestration]
---

# Demo build coordination — the six-phase demo track from claim to integration

## Phase

This record covers the whole demo track, coordinated by one build session running the demo build
orchestration prompt (`PROMPT-014`) — six phases, each with its own orchestrator-written session
record carrying its per-phase detail:

- `phase-demo-01` — Build the demo terminal backend and stage read routes (`SESS-2026-09-10-03`).
- `phase-demo-02` — Build the stage frontend with the zero-scroll layout (`SESS-2026-09-10-04`).
- `phase-demo-03` — Build the deterministic overview tools (`SESS-2026-09-10-02`).
- `phase-demo-04` — Build the overview skill, templates and page generation
  (`SESS-2026-09-10-05`).
- `phase-demo-05` — Demo content, runbook, reset tool and rehearsals (`SESS-2026-09-10-07`).
- `phase-demo-06` — Stage terminal interaction — session tabs, guarded drop, command injection
  (`SESS-2026-09-10-06`; inserted mid-build by the owner, GOV-003).

## Verification

Run at close on `dev` at `038a950`:

```
$ uv run pytest
495 passed, 2 warnings

$ uv run ruff check src/ test/
All checks passed!

$ uv run mypy src/
Success: no issues found in 23 source files

$ uv run python -m src.governance
Governance OK: 18 systems, 140 documents, 15 memories, 112 backlog phases

$ cd ts && npm run build
✓ built (tsc -b && vite build)

$ git add -A && uv run python tools/check_no_private_content.py
check_no_private_content: OK (571 tracked files, 31 identifiers checked)
```

Behavioral checks were performed per phase at each completion gate — adversarial reviews
(`demo-adversary`) and Playwright browser verifications (`demo-validator-web`) — with their
evidence in the per-phase session records listed above.

## Acceptance

Per phase, at each completion under the demo-track gate (`GOV-003`):

- `phase-demo-01` — Met (route absence, loopback fail-fast including the `UVICORN_HOST` bypass
  found and fixed by its adversarial review, shell override, read routes).
- `phase-demo-02` — Met (zero-scroll at all four sizes, terminal round-trip, data-file rotator;
  the clipped-popover blocker found by review was fixed and re-verified 7/7 in the browser).
- `phase-demo-03` — Met (byte-identical double runs including varied hash seeds; independent
  recomputation extended to every metrics section after review; OPS documents green).
- `phase-demo-04` — Met (figures match tool output verbatim in the browser check; identical
  double generation; skill recomputes nothing).
- `phase-demo-05` — Met with two conditions explicitly deferred by owner decision (PROMPT-020
  decision 7): the owner-driven 15-minute timing (R09) and the Windows smoke check (R06) move to
  the workbench track's rehearsal-refresh phase; the reset-tool condition is fully met (allowlist
  held under four direct attacks, byte-identical park/restore, no duplicate seeding).
- `phase-demo-06` — Met (session persistence, guarded termination with process-level evidence,
  injection semantics after the embedded-newline blocker fix, resize reaching the PTY by test).

## Backlog

All six phases are `status: complete` on `dev` with `session`, `completion_evidence` and `result`
recorded; none remain in `next_up`. Peers untouched by this session's close: `phase-port-01`
(`agent-codex-port`, active) and `phase-demo-07` (`agent-demo-glossary`, active in a concurrent
session).

## Unresolved

- The REQ-006 R06 Windows smoke check and the owner-driven R09 timing — deferred to the workbench
  track's rehearsal-refresh phase (PROMPT-020 decision 7).
- `ts/public/demo-commands.json` placeholder copy, a stale comment in
  `TalkingPointsRegion.tsx:31`, and a cosmetic websocket startup-race console warning — recorded
  for the workbench track.
- The recurring catalog-goes-stale-on-claim pattern (regenerated on `dev` three times this
  session) — a candidate governance phase to make the check structural.
- The four-session terminal cap is UI-enforced only; the backend session registry belongs to the
  parked terminal-interaction API idea (`000087`), folded into the workbench planning.

## Review

Independent sub-agent review (fresh, non-fork), pasted verbatim:

> Audited at `dev` HEAD = `038a950` (confirmed). Method: full reruns of the code-level
> verification commands, targeted test-suite runs, double-run determinism diffs, direct source
> reading, and — for browser-behavior conditions — the per-phase records' recorded evidence plus
> the Playwright screenshots left in the working tree, which I inspected myself. I did not do a
> fresh browser run; conditions assessed that way are marked.
>
> **phase-demo-01**: flag-gated route + real shell round-trip (R04/R05) HOLDS; loopback
> fail-fast proven by test (ADR-013, including the `UVICORN_HOST` bypass) HOLDS; shell override
> + POSIX platform detection HOLDS; read routes return file content unchanged HOLDS.
>
> **phase-demo-02**: zero-scroll at four sizes (R02) HOLDS — via recorded evidence and the
> on-disk screenshots; terminal end-to-end HOLDS — via recorded evidence plus screenshot;
> data-file-driven rotator with no page-code change HOLDS. The cross-phase test conflict SESS-04
> flagged was resolved in `26fdb48`; the test now passes.
>
> **phase-demo-03**: byte-identical double runs (R07) HOLDS — reran myself, including a changed
> `PYTHONHASHSEED`; independent recomputation in tests HOLDS — eight per-section tests pass;
> OPS-011/OPS-012 with filled generated blocks and green governance HOLDS.
>
> **phase-demo-04**: skill produces the page with every figure matching tool output HOLDS —
> regenerated to scratch and programmatically confirmed all seven meta figures verbatim;
> identical double generation HOLDS — reran myself; no recomputation in the skill HOLDS. Minor:
> the committed `_public/overview/index.html` is one backlog-transition stale (pre-dates
> phase-demo-05's completion) — cosmetic, a skill rerun fixes it.
>
> **phase-demo-05**: R09 timed dry-runs HOLDS-AS-DEFERRED — the deferral is genuine, not a
> silent pass: PROMPT-020 decision 7 really says the workbench track re-times the live segment,
> the runbook records honest partial-coverage notes, and SESS-07 marks the condition Not met in
> bold. R06 Windows smoke check HOLDS-AS-DEFERRED — the checklist carries an explicitly
> owner-fillable, empty result block. demo_reset.py conditions HOLDS — all 19 tests pass,
> covering allowlist refusal, byte-identical park/restore, seed-exactly-once, and double-run
> idempotence; the only idea-log write path is `append_idea.add()`.
>
> **phase-demo-06**: R10 persistence + fifth-tab cap HOLDS — CSS-only visibility with no
> unmount, `MAX_SESSIONS = 4` at both layers, the collapse fix present and re-check recorded;
> R11 guarded termination with no orphans HOLDS — confirm-only termination paths, idle-timeout
> orphan fix test-covered and passing; R12 injection semantics + live-edit HOLDS — the
> embedded-newline blocker fix genuinely in both layers, runtime fetch with `cache: 'no-store'`;
> resize reaching the PTY HOLDS — reran the test, which reads the real kernel window size back
> via `stty size`.
>
> **Discrepancies**: (1) `uv run pytest` at HEAD does not reproduce the coordinator's 495-passed
> claim — 1 catalog-drift failure caused by the coordinator's own still-uncommitted session
> record; fix by committing it with a regenerated catalog. (2) the committed overview page is
> one backlog-transition stale — cosmetic. Everything else matched. The per-phase records are
> notably honest throughout — each orchestrator recorded its own gate failures, truncated
> dispatches, and unfixed minors rather than smoothing them over. No claim in the records was
> contradicted by the diff or my reruns.

Both discrepancies were fixed at close: this record and the regenerated catalog are committed
together, and the overview page was regenerated against the final backlog state, in the same
closing commit.

## Decisions

- The owner inserted `phase-demo-06` (stage terminal interaction) mid-build after testing the
  integrated stage, returned `phase-demo-05` to queued for it, and extended the demo-track
  completion gate to the new phase (`GOV-003`).
- The owner moved the demo to the week of 2026-09-15 and redirected the project: the stage
  becomes the chartered management UI ("the workbench"), specified in the pre-plan package
  (`PROMPT-020`) with all planning decisions ratified in-session. R09/R06 verification was
  deferred to that track's rehearsal-refresh phase rather than faked here.
- The owner sanctioned a third fix cycle for `phase-demo-05` beyond the guardrails' cap, chose
  to commit the factory session's accumulated idea-log events when they blocked the claim
  protocol, approved each of the six integrations individually, and approved pushing `dev`.
- Playwright MCP connectivity required a session restart with `enabledMcpjsonServers` set in
  `.claude/settings.local.json`; browser gates were sequenced after that.

## Corrections

- The coordinator twice committed backlog changes on `dev` without regenerating the catalog
  (the declaration commit and the claim-time drift), and each time the next gate caught it; the
  recurring pattern is recorded in Unresolved as a governance-phase candidate.
- A link command guessed a fresh idea's id (`000083` instead of `000087`), misdirecting an
  append-only write; retracted and relinked through the sanctioned writer, and recorded as a
  standing memory so ids are always taken from the writer's output.
- An early `git checkout --theirs` during the `phase-demo-06` rebase would have taken the wrong
  side of a catalog conflict; caught immediately and replaced with `git checkout dev --`.
- The coordinator's close-out verification was run before writing this record, making the
  "495 passed" claim non-reproducing at HEAD until this record and the catalog were committed
  together — the review's discrepancy 1, fixed in the closing commit.

## Left undone

- The owner-driven 15-minute timing (R09) and the Windows-machine smoke check (R06) — by
  decision, these belong to the workbench track's rehearsal-refresh phase, since the demo now
  runs on the reworked UI.
- Real command copy for `ts/public/demo-commands.json`, the stale `TalkingPointsRegion.tsx:31`
  comment, and the cosmetic websocket startup-race warning — all deferred to the workbench
  track, which reworks those surfaces.
- A backend session registry bounding the terminal cap — parked as idea `000087`, folded into
  the workbench planning (`PROMPT-020`).
- The catalog-staleness-on-claim pattern — a candidate governance phase to make the check
  structural rather than coordinator vigilance.
