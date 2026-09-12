---
schema_version: 1
id: doc-session-phase-wb-08-panel-fixes
code: SESS-2026-09-11-07
title: phase-wb-08 panel rendering fixes — checkpoint
kind: session
status: active
owner: repository-owner
created: '2026-09-11'
updated: '2026-09-11'
systems: [sys-ui, sys-demo-stage]
depends_on: [doc-workbench]
---

# phase-wb-08 panel rendering fixes — checkpoint

## Phase

`phase-wb-08` — Panel rendering fixes — terminal fill, HTML Viewer, File Browser scroll.

## Verification

State at close: the fix is integrated into `dev` (fast-forward to the rebased branch at
`bf1749b`); the worktree and `agent/phase-wb-08` branch are removed. Commands re-run in the
primary checkout `/code/d-system` at close:

- `cd ts && npm run build`: `✓ 55 modules transformed … ✓ built` (the 500 kB chunk-size
  warning is pre-existing, not introduced by this change).
- `uv run python -m src.governance`: `Governance OK: 18 systems, 167 documents, 16 memories,
  122 backlog phases`
- `uv run python tools/check_no_private_content.py` with changes staged:
  `check_no_private_content: OK (502 tracked files, 31 identifiers checked)`
- Adversarial review (`demo-adversary`, pack `W08-A`, coordinator-dispatched): no blocker or
  major findings. Verified live that the fix is structural (`.xterm` 760×570, not 0), generic
  to any multi-panel slot (demonstrated by reassigning the HTML Viewer into layout 2's main
  slot), holds for the CMD/PowerShell unavailable-shell overlays, and that collapse, drop and
  restore render correctly inside the repaired chain. One minor note — command echo not
  visible in its headless rig — reproduced with no layout switch and pre-fix, i.e. a test-rig
  quirk, and was superseded by `W08-W`'s passing visible-echo assertion.
- Playwright browser verification (`demo-validator-web`, pack `W08-W`, coordinator-dispatched):
  passed on REQ-007 W15/W18's stated bar after coordinator-directed re-verification. Pass:
  visible echo round-trip; File Browser internal scroll over an expanded `docs/` tree with and
  without a filter, in both layouts, last entry reachable; zero page scroll and zero region
  overlaps in both layouts at 1280×720, 1366×768, 1920×1080 and 1024×768; HTML Viewer renders
  known overview figures in both layouts. Three literal check failures were resolved with
  measured evidence rather than fixes: (1) the xterm fill-proxy gap of 98.16px decomposes
  exactly into the nested duplicate header (39.84px, idea `000101`, explicitly out of scope) +
  tab bar (36.64px) + padding/borders (21.69px), with the xterm filling 100% of its available
  space and tracking the slot body at every size — W15's stated bar; (2) the layout-1 viewer
  "380px gap" was retracted by the validator as its own unscoped-selector bug (correct
  measurement 47.35px, a pass); (3) the layout-switch persistence failure reproduced
  identically on a `dev` baseline without this phase's diff — proving it was not caused by the
  diff — and the session-close independent review then established the failure itself was a
  measurement artifact: on a clean browser session the guard passes (two initial websockets
  only, zero during switches, MARKER echoed back), and both layout files default the terminal
  slot to bash. The failing runs shared a browser profile in which the `W08-W` validator's own
  earlier fill testing had stored PowerShell as layout 2's visible panel, so each round-trip
  genuinely unmounted bash. Idea `000107` was amended to the corrected diagnosis.
- Pre-fix diagnosis (`demo-validator-web`, pack `W08-M`, coordinator-dispatched after the
  orchestrator's two dispatch attempts hit turn limits): recorded the height-chain break at
  `.stage-workbench-slot__body` (missing `display: flex`) with full per-element measurements,
  and distinguished the HTML Viewer's launch-flag gap (runbook scope, `phase-wb-10`) from the
  height collapse.
- `uv run pytest` (post-rebase, pre-integration, in the worktree): `552 passed, 3 failed` —
  the three failures are the known environmental PTY failures in `test_demo_terminal.py`
  (ideas `000097`/`000099`), unchanged in kind and count.
- `git diff` of the integrated change (`6a42caf..bf1749b`):
  `ts/src/stage/StagePage.css | 17 +++++++++++++++++` — nothing outside `ts/`.

## Acceptance

- Shell panel xterm fill at all four sizes, both layouts, with readable round-trip output
  (REQ-007 W15): Met — `W08-W` measured the `.xterm` container non-zero and tracking its slot
  body in both layouts at all four sizes (the constant 98.16px offset is fully accounted for
  by the nested header, tab bar and padding — see `## Verification`), and the echo round-trip
  output was asserted visible in the rendered area, not merely present in the DOM. The
  CMD/PowerShell unavailable-shell messages render unclipped in the filled chain (`W08-A`,
  `.stage-terminal-sessions` 760×570 with the overlay text).
- Zero page scroll and no overlapping regions at all four sizes, both layouts: Met — `W08-W`
  item 7: document scrollHeight equals viewport height in every combination, zero pairwise
  region-bounding-box intersections.
- Layout-switch persistence guard (MARKER round-trip, no new websocket): Met — the guard
  passes as literally written on a clean browser session against the integrated code,
  verified independently twice: the `W08-A` adversarial run (zero new websockets, MARKER in
  scrollback) and the session-close independent review (two initial websockets only, zero
  during switches, `check-persist12345` echoed back correctly). The `W08-W` validator's
  failing runs — including its `dev` baseline — were a measurement artifact of its own stale
  localStorage (PowerShell stored as layout 2's visible panel from earlier fill testing);
  both layout files default the terminal slot to bash. The coordinator's mid-gate
  classification ("pre-existing product defect, layout 2 defaults to PowerShell") was wrong
  in its diagnosis and is corrected in idea `000107`'s amendment; the residual real behavior
  (a stored visible-panel choice differing between layouts silently kills the hidden shell's
  session) intersects `phase-wb-09`'s W16 obligation, and `W09-W`'s guard should run from a
  clean store.
- HTML Viewer renders a known figure in both layouts with the diagnosis stating the confirmed
  cause (REQ-007 W15, viewer half): Met — `W08-M` confirmed the no-flag blank state is the
  launch-flag gap (runbook scope, `phase-wb-10`, no code change made) and the layout-2
  height collapse is the wrapper defect this phase fixed; `W08-W` asserted the viewer renders
  known overview figures in both layouts including layout 2's multi-panel main slot (layout 1
  fill gap 47.35px after the validator retracted its own mis-scoped 380px measurement).
- File Browser internal scroll, last entry reachable, no page scroll (REQ-007 W18): Met —
  `W08-W` item 6: tree scrollHeight far exceeds clientHeight, scrolling reaches the last
  entry, document scroll unchanged, with and without a text filter, in both layouts.
- Windows confirmations: Not applicable here — explicitly an owner check belonging to
  `phase-wb-07`'s checklist, blocked behind `phase-wb-10`. The coordinator reminded the owner
  at integration per the kick-off record's delta 4.

## Backlog

- `status: complete`, `agent: agent-demo-stage` (kept as the record of who did the work).
- `next_action`: None — phase complete and integrated into `dev` (fast-forward to the rebased
  branch, commit `bf1749b`) under the kick-off record's delta-4 pre-approval. The post-fix
  Windows confirmations remain owner checks in `phase-wb-07`'s checklist.
- `completion_evidence`: `ts/src/stage/StagePage.css` (the integrated fix).
- `result`: the full gate outcome as written to `backlog.yaml` in commit `acdacce` — creator
  fix, `W08-V1` pass, `W08-G` green, `W08-A` no blocker/major findings, `W08-W` passing the
  requirement bar with the three literal-check discrepancies resolved by measurement (chrome
  decomposition, retracted selector bug, pre-existing `dev` baseline), post-rebase validation
  green.
- Removed from `next_up` in the completing change.

## Unresolved

- The post-fix Windows confirmations (terminal and viewer visibly filled on the presentation
  machine, `D_SYSTEM_DEMO_TERMINAL=1` on backend AND frontend) are owner checks in
  `phase-wb-07`'s checklist — outstanding by design, not closable on agent evidence.
- Idea `000107` (amended at close: a stored visible-panel choice differing between layouts
  silently kills the hidden shell's session; the original "layout 2 defaults to PowerShell"
  diagnosis was a stale-localStorage measurement artifact) is open and intersects
  `phase-wb-09`'s W16 obligation that visibility and re-assignment changes never silently
  kill a session; `W09-W`'s persistence guard should run from a clean store.
- The duplicate nested header inside multi-panel slots (idea `000101`, cosmetic, ~40px) is
  unfixed by design — out of this phase's scope per the pack — and is what defeats the
  60px fill-check proxy in `W08-W`/`W09-W` item text; `phase-wb-09`'s gate should expect the
  same chrome-accounted offset.
- Orchestrator tooling gap, recurred throughout this phase: browser-heavy subagent dispatches
  (`W08-M` twice for the orchestrator, then `W08-M`, `W08-A` and `W08-W` once each for the
  coordinator) exceed one turn's budget; only the coordinator holds a resume-capable tool, so
  every such dispatch had to run through the coordinator. Worth an idea/plan entry if it
  should be fixed rather than worked around.

## Review

Independent sub-agent review at close (fresh non-fork agent; commit range `7d278e4..acdacce`;
it ran the verification commands, read the diff, and drove the live app itself on ports
8011/5181). Findings verbatim, condition by condition:

1. "SUPPORTED WITH CAVEAT. xterm fill mechanism and my own measurement corroborate the
   chrome-decomposition argument. I did not sweep all four window sizes myself; I relied on
   one size plus the code-level reasoning, which is solid."
2. "SUPPORTED WITH CAVEAT. I did not independently sweep all four sizes/both layouts for zero
   scroll/no-overlap; relying on the record's W08-W item 7 plus the general soundness of the
   fix."
3. "NOT SUPPORTED as the record frames it — and my own rerun actively contradicts the
   underlying defect claim. The backlog's acceptance text is unconditional: 'the guard
   passes.' The session record itself admits it did not pass on the tested baseline (4 new
   websockets, MARKER lost) and reclassifies that as pre-existing/non-regression to justify
   'Met.' Read literally, condition 3 fails on the record's own evidence. Worse: when I
   reproduced the guard myself, on the actual integrated code, in a clean browser session, it
   passed cleanly — no new websockets, MARKER survived, and layout 2's terminal defaulted to
   bash, not PowerShell as idea 000107 claims. This casts real doubt on whether idea 000107's
   diagnosis is a genuine product defect at all, versus an artifact of stale localStorage
   state accumulated during the validator's own test session."
4. "SUPPORTED WITH CAVEAT. The launch-flag-vs-collapse diagnosis distinction is plausible and
   consistent with the phase-wb-04 history; I did not independently drive the flag-set HTML
   Viewer figure check in both layouts, though the panel rendered correctly in my ad hoc
   check."
5. "SUPPORTED. I directly reproduced the File Browser internal scroll (scrollHeight 611 >
   clientHeight 164, overflow-y auto) myself against the live app."
6. "SUPPORTED. Correctly deferred to phase-wb-07/phase-wb-10 as an owner-only Windows check;
   nothing here closes it on agent evidence."

Overall verdict, verbatim: "The code change (commit bf1749b) is real, minimal,
mechanistically sound, and generically correct — not hard-coded. Conditions 1, 2, 4, 5, 6 are
reasonably supported... Condition 3 is the one that does not hold up: the acceptance text
says the guard passes, the session record's own numbers say it didn't, and my independent
rerun on the identical integrated code found no defect at all — directly conflicting with
idea 000107's stated root cause... status: complete is not fully corroborated: the
persistence-guard acceptance condition was closed by reinterpreting its literal wording
rather than by it actually passing."

Resolution of the review's condition-3 finding: the finding was accepted, not argued down.
The coordinator's original classification was wrong in its diagnosis; the reviewer's own
clean-session run is direct evidence that the guard passes as literally written on the
integrated code (corroborated by the earlier W08-A run and by both layout files defaulting
the terminal slot to bash — re-verified directly at close). The record's Acceptance section
and the backlog result were corrected to rest condition 3 on that clean-run evidence, and
idea 000107 was amended to the corrected diagnosis, before completion was confirmed. With the
record corrected, the reviewer's evidence supports Met on every condition; its verdict
sentence was aimed at the record's prior framing, which no longer stands.

## Decisions

- The owner directed this build via the fix-build prompt in the kick-off record (PROMPT-023
  delta 4): dispatches verbatim from PROMPT-024, integration of phase-wb-08/09 pre-approved
  behind a green gate, no descoping, bounded enhancement lane. All held; the enhancement lane
  found nothing to implement.
- The coordinator took over the W08-M, W08-A and W08-W dispatches (pack convention makes
  W08-A/W08-W coordinator dispatches anyway; W08-M moved up after the orchestrator's two
  dispatch attempts hit turn limits with no resume tool available to it). Truncated agents
  were resumed, never re-run, per idea 000077's convention.
- The three literal W08-W failures were resolved by measurement rather than code: the 60px
  fill proxy is defeated by ~98px of legitimate chrome (the idea-000101 nested duplicate
  header + tab bar + padding) while REQ-007 W15's stated bar (tracking height, readable
  output) is met; W09's gate should expect the same offset until 000101 is fixed.
- The pre-existing-defect classification of the persistence failure was superseded at close
  by the independent review's stronger finding (measurement artifact; guard passes clean) —
  see Corrections.
- Integration proceeded without a pause under delta 4's pre-approval once the gate was green
  on the requirement bar; the owner reviews retroactively via this close.

## Corrections

- The coordinator's mid-gate classification of the W08-W persistence failure — "pre-existing
  product defect: layout 2 defaults its terminal slot to PowerShell" — was wrong. The
  dev-baseline run that grounded it shared the validator's browser profile, whose stored
  visible-panel choice (PowerShell in layout 2, left by the validator's own fill testing) was
  the actual mechanism; both layout files default to bash, and the guard passes on a clean
  session. Caught by the session-close independent review; idea 000107 amended, the record
  and backlog corrected above. The durable lesson is recorded in 000107's amendment: browser
  validators must run persistence-type guards from a clean store, or state left by their own
  earlier checks masquerades as a product defect.
- The W08-W validator itself retracted its layout-1 HTML Viewer finding (380px gap) as an
  unscoped-selector bug during coordinator-directed re-verification; the correct measurement
  (47.35px) passes.
- The orchestrator's first W08-G run failed on a stale catalog caused by its own claim commit;
  it regenerated the catalog on dev (d34ac7a) and re-ran green. Recorded as an ordinary
  in-phase fix, noted here because the claim-then-regenerate ordering could recur.

## Left undone

- The Windows confirmations remain phase-wb-07 owner checks by design. Partial early result,
  reported by the owner on 2026-09-11 after porting to the Windows machine: the HTML Viewer
  was blank until D_SYSTEM_DEMO_TERMINAL=1 was set on BOTH backend and frontend processes,
  and setting it fixed the viewer — confirming the launch-flag gap diagnosis and giving an
  early informal pass on the viewer half of the W15 Windows check. To be recorded formally in
  phase-wb-07's checklist when that phase resumes; the flag-on-both-processes requirement is
  exactly what phase-wb-10's runbook refresh must make impossible to forget.
- Idea 000101 (the nested duplicate header inside multi-panel slots, ~40px of chrome) is
  unfixed by design — out of this phase's scope; it is also what defeats the literal 60px
  fill proxy in the pack's browser checks.
- Idea 000107 (amended) — the hidden-shell-session-kill behavior when stored visible panels
  differ between layouts — is left to phase-wb-09's W16 rework, whose gate re-runs the
  persistence guard; run it from a clean store.
- The orchestrator-cannot-resume-truncated-subagents tooling gap recurred on every
  browser-heavy dispatch this phase; the coordinator worked around it by dispatching and
  resuming those agents itself. Left as an observation for the owner rather than an idea
  entry, since it is a harness/tooling property, not repository behavior.
