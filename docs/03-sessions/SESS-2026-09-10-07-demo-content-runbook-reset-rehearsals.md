---
schema_version: 1
id: doc-session-demo-content-runbook-reset-rehearsals
code: SESS-2026-09-10-07
title: Demo content, runbook, reset tool and rehearsals
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-demo-stage, sys-demo-overview]
depends_on: [doc-live-demo]
---

# Demo content, runbook, reset tool and rehearsals

## Phase

`phase-demo-05` — Demo content, runbook, reset tool and rehearsals.

## Verification

`uv run pytest`
```
495 passed, 2 warnings
```

`uv run ruff check src/ test/`
```
All checks passed!
```

`uv run mypy src/`
```
Success: no issues found in 23 source files
```

`uv run python -m src.governance`
```
Governance OK: 18 systems, 139 documents, 15 memories, 112 backlog phases
```

`uv run python tools/check_no_private_content.py` with the changes staged
```
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (437 tracked files, 0 identifiers checked)
```

Adversarial review (demo-adversary, pack D05-A) — not run this session. Dispatched by the
coordinator at PROMPT-015 step 8, not by this orchestrator, per the demo-track completion gate
(GOV-003).

Playwright rehearsal pass over the runbook's browser-marked steps (demo-validator-web, pack
D05-W) — not run this session, same reason.

Two fresh-eyes rehearsal passes (demo-validator-code, pack D05-R, dispatched by this
orchestrator) were run cold against `docs/00-working/demo-runbook.md`, separated by
`uv run python tools/demo_reset.py prepare`. Both passes' per-step times and findings are
recorded in the runbook itself (Dry-Run 1, Dry-Run 2 and Rehearsal Findings sections). Summary:
CLI-executable steps measured 10s (pass 1, partial) and 14s (pass 2, partial) against their
timeboxes — well inside budget for the steps that could run — but `/idea-triage`'s subagent half
could not be executed by either rehearsal agent (forbidden from dispatching subagents), so no
pass produced a complete, real 15-minute total.

The coordinator resolved the branch's diff-scope mismatch directly on `dev` (commit `9753a88`:
declared `_data/ideas.jsonl`, `docs/00-working/ideas.md` and `_public/overview` as this phase's
deliverables) and cleared the stray dev-server port collision. This orchestrator then applied a
one-commit fix cycle (`e1e3886`, pre-rebase) addressing all four Rehearsal Findings as narrative
and procedure corrections to `docs/00-working/demo-runbook.md` — no tool changed:
- `/orient` gained an explicit port-free precondition (`ss -tlnp | grep -E "8010|5180"`).
- `overview-skill rebuild` no longer references the nonexistent `/overview-build`; it now
  describes the real live-segment action (build/invoke the `d-system-overview` skill live), with
  `uv run python tools/generate_overview.py` as the concrete fallback command.
- `overview-skill rebuild`'s Step Markers entry states the parked-skill design plainly: `prepare`
  parks the pre-built skill on purpose so the live rebuild is real, and `restore` is the named
  fallback.
- `/idea-triage`'s Step Markers entry now states its discovery half is CLI-measurable and its
  subagent-dispatch half runs only in the presenter's own Claude Code session, so a rehearsal
  agent records it as partially measured, not failed.

The branch was then rebased onto `dev` at `9753a88` (`git rebase`, one conflict in
`docs/09-backlog/backlog.yaml` resolved by keeping both sides — the widened deliverables list from
`dev` and this session's record/next_action — no conflict occurred in `_data/ideas.jsonl`; its
append-only invariant was independently confirmed: `dev`'s log had 374 lines, this branch's has
377, and `git diff dev...HEAD -- _data/ideas.jsonl` shows only added lines, never a removed one).
The catalog was checked against a fresh regeneration and found already current (empty diff); no
regeneration commit was needed.

D05-G (phase gate, `demo-validator-check`) was re-dispatched verbatim after the rebase and
returned **all 9 checklist items PASS**, including item 9 (diff scope), which is now green against
the widened deliverables declaration.

### Fix cycle 2/2 — D05-A adversarial review

The D05-A adversarial review raised two blockers and two majors, resolved as follows:

- **Blocker — R09's timing evidence is partial** and **blocker — the dry-runs are agent-driven,
  not owner-driven per PROMPT-017**: both **deferred by owner decision**, not fixed here. Per
  `docs/02-prompts/PROMPT-020-workbench-pre-plan-package.md` decision 7 (commit `4c0acd5` on
  `dev`), the demo now runs next week on a reworked workbench UI, and the workbench track ends
  with a rehearsal-refresh phase that re-times the live segment owner-driven against the final
  UI. `docs/00-working/demo-runbook.md`'s Dry-Run Rehearsals section now carries one sentence
  stating this explicitly. The R09 acceptance line below stays honestly Not met, unchanged in
  substance.
- **Major — the Windows checklist implemented a narrower gate than PROMPT-017 specifies**: fixed.
  `docs/00-working/demo-windows-setup.md` gained a Full Fresh-Eyes Rehearsal Checklist section
  running all 7 of PROMPT-017's fresh-eyes items once on the presentation machine (including the
  half-width viewport check, the determinism check and the side-by-side fallback exercise, each
  with a result line), and the Pre-Demo Git Tag section now requires `demo_reset.py prepare` and
  `restore` to each be verified once against the tagged state, with a result block.
- **Major — `ts/public/talking-points.json` violated D05-O's own length rule**: fixed. All eight
  entries were single dense paragraphs (200-234 characters); each is now a short headline plus
  exactly three brief supporting lines (newline-separated within the string, schema unchanged),
  preserving each entry's message. `cd ts && npm run build` reverified clean.
- **Minor — a stale placeholder comment at `ts/src/stage/TalkingPointsRegion.tsx:31`**
  ("this file ships clearly-placeholder entries," no longer true now that D05-O's real copy is
  shipped): recorded only, not fixed — that file is outside `phase-demo-05`'s deliverables (it
  belongs to `phase-demo-02`), and the workbench rework owns its future per PROMPT-020.

Verification re-run after the fix cycle (real output, in the worktree):

`uv run pytest`
```
495 passed, 2 warnings
```

`cd ts && npm run build`
```
✓ 38 modules transformed.
dist/index.html                   0.39 kB │ gzip:   0.27 kB
dist/assets/index-ZpTiJ9jO.css   12.84 kB │ gzip:   3.62 kB
dist/assets/index-DWqr5BsF.js   495.40 kB │ gzip: 136.12 kB
✓ built in 1.06s
```

`uv run python -m src.governance`
```
Governance OK: 18 systems, 139 documents, 15 memories, 112 backlog phases
```

`uv run python tools/check_no_private_content.py` with the changes staged
```
check_no_private_content: OK (437 tracked files, 0 identifiers checked)
```

### Fix cycle 3/3 (owner-sanctioned, beyond the standard two-cycle cap) — D05-W browser pass

`dev` commit `d4d2610` widened this phase's deliverables to `src/api/routes/demo_stage.py` and
`test/test_demo_terminal.py` for the findings below. The branch was rebased onto `dev` at
`d4d2610` (two conflicts, both in already-encountered files — `docs/08-governance/catalog.md`,
generated, regenerated fresh after the rebase rather than hand-merged, and
`docs/09-backlog/backlog.yaml`, resolved by keeping both sides as in the prior fix cycles;
`_data/ideas.jsonl`'s append-only invariant reconfirmed: 0 removed lines against `dev`, 3 net-new).

- **Fixed** — `src/api/routes/demo_stage.py`'s `DEFAULT_OVERVIEW_PAGE_PATH` was
  `_public/d-system-overview.html`; `tools/generate_overview.py` actually writes
  `_public/overview/index.html`, so after a successful rebuild the stage kept reporting the
  overview absent unless `D_SYSTEM_OVERVIEW_PAGE_PATH` was set by hand — undocumented anywhere.
  Aligned the default; the env-var override is unchanged. The existing default-path test asserted
  only that the path started with `_public/`, loose enough to pass with either the wrong default
  or the corrected one — tightened it to assert the exact expected value
  (`_public/overview/index.html`), computed from `DEFAULT_OVERVIEW_PAGE_PATH` itself. D05-W
  verified live that the panel populates once the path is correct.
- **Fixed** — the runbook's `/orient` step and the Windows checklist's smoke-check frontend start
  command omitted `VITE_API_TARGET`; without it the dev proxy silently targets
  `http://localhost:8000` instead of the demo backend on `8010`, and every stage route 404s if
  anything else holds port 8000 (D05-W reproduced this). Both now state
  `VITE_API_TARGET=http://localhost:8010` alongside the `npm run dev` command, with a one-line
  note on the failure mode.
- **Fixed** — "half-width window" appeared in both documents with no pixel definition. Both now
  say 960×1080, D05-W's own interpretation, which it confirmed passing.
- **Record only, not fixed** — `ts/public/demo-commands.json` still carries placeholder entries
  (labeled `PLACEHOLDER COMMAND 1/2/3`). Its real-copy authoring fell between phases:
  `phase-demo-06` created this file after `phase-demo-05` was already scoped, so no phase's
  delegation pack assigns writing its content. Deferred to the workbench track (PROMPT-020),
  whose terminal rework revises this panel anyway.
- **Record only, not fixed** — D05-W observed a harmless-but-visible websocket startup-race
  console warning at `ts/src/stage/TerminalRegion.tsx:105`. Noted as a known cosmetic item for the
  workbench track; not a `phase-demo-05` deliverable.

Verification re-run after this fix cycle (real output, in the worktree):

`uv run pytest`
```
495 passed, 2 warnings
```

`cd ts && npm run build`
```
✓ 38 modules transformed.
dist/index.html                   0.39 kB │ gzip:   0.27 kB
dist/assets/index-ZpTiJ9jO.css   12.84 kB │ gzip:   3.62 kB
dist/assets/index-DWqr5BsF.js   495.40 kB │ gzip: 136.12 kB
✓ built in 999ms
```

`uv run python -m src.governance`
```
Governance OK: 18 systems, 140 documents, 15 memories, 112 backlog phases
```

`uv run python tools/check_no_private_content.py` with the changes staged
```
check_no_private_content: OK (438 tracked files, 0 identifiers checked)
```

## Acceptance

- Both dry-runs complete within 15 minutes with every step inside its timebox, and their times
  are recorded in the runbook (REQ-006 R09) — **Not met**. Times are recorded for both passes,
  but `/idea-triage`'s subagent-dispatch half was not executed by either rehearsal agent (a
  rehearsal-tooling constraint, not a proven step failure, and now documented as such in the
  runbook's Step Markers section), so neither pass produced a complete, verified 15-minute total.
  See `## Verification` above and the runbook's Rehearsal Findings section. Complete owner-driven
  timing against the final UI is deferred to the workbench track's rehearsal-refresh phase, per
  the owner's PROMPT-020 decision 7 — an owner decision, not a defect left unfixed here.
- The R06 smoke check on the presentation machine is recorded as passing in the runbook —
  **Not met**. The Windows checklist (`docs/00-working/demo-windows-setup.md`) carries the R06
  smoke-check procedure and an owner-fillable result block, but the check itself requires the
  Windows presentation machine and has not been run — outstanding owner-machine work, reported
  plainly per this build's governance protocol, not claimed as done.
- `demo_reset.py prepare` parks the skill, seeds the fallback idea without duplication, and
  regenerates outputs; `demo_reset.py restore` returns the pre-built skill byte-identical; both
  are double-run idempotent and never delete or rewrite idea-log content or governed documents —
  **Met**. Proven by D05-C1's 19-test suite (allowlist refusal, prepare→restore round-trip,
  no-duplicate seed, both idempotences) and D05-V1's independent validation (verdict: PASS, no
  findings), and confirmed live during this session's `prepare`/`restore` cycles and the
  post-rebase append-only check above.

## Backlog

`phase-demo-05` — `status: active`, `agent: agent-demo-content`.

`next_action`: D05-G is green on all 9 items; D05-A's two majors and D05-W's one finding requiring
a code fix are all fixed on `agent/phase-demo-05`; the minors from both reviews are recorded only
(outside this phase's deliverables); the two D05-A blockers are deferred by owner decision
(PROMPT-020 decision 7). `uv run pytest`, `cd ts && npm run build`, governance and the staged
private-content check all pass on the rebased tree (see `## Verification` above). Reported to the
coordinator as green — the phase goes to the owner for integration from here. Still outstanding,
not fixable from this worktree: the REQ-006 R06 Windows smoke check (owner-machine work) and the
deferred owner-driven timing pass.

## Unresolved

- `/idea-triage`'s subagent-dispatch half and the full owner-driven R09 timing are deferred to
  the workbench track's rehearsal-refresh phase per PROMPT-020 decision 7 — not a defect left
  unfixed here.
- The REQ-006 R06 Windows terminal smoke check has not been run — owner-machine work, outstanding.
- The stale placeholder comment at `ts/src/stage/TalkingPointsRegion.tsx:31` is recorded, not
  fixed — outside `phase-demo-05`'s deliverables; the workbench rework owns that file's future.
- `ts/public/demo-commands.json`'s placeholder entries are recorded, not fixed — the file is a
  `phase-demo-06` deliverable created after `phase-demo-05` was scoped; real copy is deferred to
  the workbench track per PROMPT-020.
- D05-W's websocket startup-race console warning at `ts/src/stage/TerminalRegion.tsx:105` is
  recorded as a known cosmetic item for the workbench track.
