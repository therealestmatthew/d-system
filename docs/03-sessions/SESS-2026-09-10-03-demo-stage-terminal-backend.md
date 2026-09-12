---
schema_version: 1
id: doc-session-demo-stage-terminal-backend
code: SESS-2026-09-10-03
title: Demo stage orchestration — terminal backend and stage read routes (phase-demo-01)
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-api, sys-demo-stage]
depends_on: [doc-live-demo, doc-prompt-demo-build-delegation-pack]
---

# Demo stage orchestration — terminal backend and stage read routes (phase-demo-01)

## Phase

`phase-demo-01` — Build the demo terminal backend and stage read routes.

## Verification

- `uv run pytest` — `452 passed, 2 warnings`.
- `uv run ruff check src/ test/` — `All checks passed!`.
- `uv run mypy src/` — `Success: no issues found in 23 source files`.
- `uv run python -m src.governance` — `Governance OK: 18 systems, 131 documents, 15 memories,
  110 backlog phases`, exit 0.
- `uv run python tools/check_no_private_content.py`, run with all changes staged —
  `check_no_private_content: OK (404 tracked files, 0 identifiers checked)`.
- Adversarial review (D01-A) — not yet dispatched. Per `PROMPT-018`'s completion-gate convention
  and `GOV-003`'s demo-track completion decision, D01-A is dispatched by the build coordinator at
  `PROMPT-015` step 8, not by this orchestrator.

Item-level dispatch history (creator/validator pairs from `PROMPT-018`):

- D01-C1 (PTY adapter, `src/demo`) — first pass touched `pyproject.toml`/`uv.lock` outside its
  declared scope; D01-V1 failed it on that boundary violation. One fix cycle reverted those two
  files, keeping the diff to `src/demo` and `test/test_demo_terminal.py`. D01-V1 re-run: pass —
  `12 passed`, ruff clean, mypy clean.
- D01-C2 (websocket route, gating, `pywinpty` dependency) — first pass left debug code
  (`open("/tmp/argv_probe_result.txt", ...)`) in `src/main.py` and was uncommitted when its turn
  was cut off by a session limit; resumed and the debug code removed in a fix cycle. D01-V2: pass
  — full suite `416 passed, 1 pre-existing unrelated failure` at the time (a catalog/backlog
  drift check, confirmed by the validator to reproduce identically on `dev` itself), ruff clean,
  mypy clean.
- D01-C3 (stage read routes, `src/api/routes/demo_stage.py`) — the creator's turn was cut off by
  a session limit before running verification or committing; resumed, found the routes and tests
  already complete, fixed one `ruff` I001 import-order finding, committed. D01-V3: pass — `28`
  tests covering this diff pass, ruff clean, mypy clean.
- Mid-build, the coordinator reported `phase-demo-03` integrated into `dev` (tip `a572fb3`) and
  directed a rebase now rather than at the end. `git rebase dev` in the worktree replayed all
  three commits with no conflicts; the pre-existing `test_committed_catalog_matches_regenerated_output`
  failure resolved itself (the rebased `dev` already carried the regenerated catalog from
  phase-demo-03's integration) — full suite went from `422 passed, 1 failed` to `452 passed, 0
  failed`.
- D01-G (phase gate) — dispatched three times. First attempt's final report was truncated before
  stating a verdict. Second (post-rebase) attempt reported FAIL on three items: (a) `pyproject.toml`
  declares `pywinpty` via a `sys_platform == 'win32'` marker rather than a PEP 621
  `[project.optional-dependencies]` extras table — this is the exact mechanism D01-C2's own
  dispatch prompt specified ("Declare pywinpty as a Windows-only optional dependency ... (sys_platform
  == 'win32')"), so not a real violation; (b) `src/api/routes/__init__.py` (an empty package-init
  file) flagged as out-of-scope — necessary scaffolding implied by the two named route-file
  deliverables, not a real violation; (c) the diff against `dev` allegedly included 28 unrelated
  files (agent specs, docs, other phases' tools). This orchestrator independently ran
  `git diff dev...agent/phase-demo-01 --name-only` after the rebase and got exactly the 12
  expected deliverable files — the dispatch's own output carried a harness warning that its
  content "matched instruction-shaped pattern(s): settings-json," flagged and neutralized as a
  possible prompt-injection artifact, so its item-5 finding is not trusted. This orchestrator's
  own verification (pasted above) is the basis for treating the phase gate as green; a clean,
  unqualified D01-G dispatch has not yet returned a verdict this orchestrator trusts without
  reservation, so this is recorded as a genuine open item, not swept under a passing gate.

## Acceptance

- With `D_SYSTEM_DEMO_TERMINAL` unset the terminal route does not exist; with it set, a websocket
  client on 127.0.0.1 reaches a real shell and receives command output (REQ-006 R04 and R05) —
  Met. `src/api/__init__.py` imports and registers `demo_terminal.router` only inside
  `if os.environ.get("D_SYSTEM_DEMO_TERMINAL") == "1"`; `test_route_absent_with_flag_unset` and
  `test_websocket_command_round_trip_with_flag_set` in `test/test_demo_terminal.py` exercise both
  states end to end through a real PTY.
- With the flag set, startup on a non-loopback bind host fails fast, proven by a test — Met.
  `src/api/routes/demo_terminal.py`'s `enforce_loopback_bind()` runs as an import-time side
  effect (not a comment), covered by
  `test_registration_fails_fast_for_non_loopback_bind_with_flag_set`.
- The shell override selects the configured shell; platform detection picks the POSIX adapter on
  Linux without pywinpty installed — Met. `src/demo/factory.py`'s `resolve_shell()` /
  `create_adapter()`, covered by `test_shell_override_via_explicit_argument_is_honored`,
  `test_shell_override_via_env_var_is_honored`, and
  `test_module_imports_cleanly_without_pywinpty_installed` (a genuine subprocess import with
  `winpty` absent from the environment).
- Stage read routes return the talking-points data file content unchanged — Met.
  `src/api/routes/demo_stage.py`'s `get_talking_points` streams the file via `FileResponse` with
  no re-serialization; `test_get_talking_points_returns_file_content_unchanged` asserts
  byte-for-byte equality.
- Adversarial review (D01-A) — Not met / not yet run. Owned by the build coordinator per
  `GOV-003`'s demo-track completion gate, not this orchestrator.

## Backlog

- `phase-demo-01`: `status: active`, `agent: agent-demo-stage`.
- `next_action`: Dispatch D01-A (adversarial review, coordinator-owned) and obtain one D01-G
  phase-gate report whose item-5 diff-scope finding is not itself flagged as a possible
  prompt-injection artifact; then request the owner's approval to integrate
  `agent/phase-demo-01` into `dev`.

## Unresolved

- D01-G has not yet produced a phase-gate report this orchestrator both trusts and reads as an
  unqualified PASS — the last (third) attempt's PASS/FAIL items 3 and 5 required this
  orchestrator's own correction against the pack's own D01-C2 wording and its own independently
  re-run diff; a fourth dispatch was not made to stay within a sane number of gate attempts, so
  this is reported up rather than resolved silently.
- One dispatch's tool output (the second D01-G attempt) was flagged by the harness as matching an
  instruction-shaped pattern ("settings-json") and neutralized — worth the coordinator's or
  owner's attention as a possible prompt-injection attempt inside the live-demo build's own
  tooling or worktree content, not just a validator error.
- D01-A (adversarial review) and integration into `dev` are both outstanding, and both require
  the coordinator/owner, not this orchestrator, to proceed.
