---
schema_version: 1
id: doc-session-workbench-backend-api
code: SESS-2026-09-10-11
title: Demo stage orchestration — workbench backend API (phase-wb-01)
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-api]
depends_on: [doc-workbench, doc-prompt-workbench-delegation-pack]
---

# Demo stage orchestration — workbench backend API (phase-wb-01)

## Phase

`phase-wb-01` — Workbench backend API: enumeration, filesystem, explorers, reveal, session
registry.

## Verification

All commands run in the worktree at `/code/d-system-worktrees/phase-wb-01` on branch
`agent/phase-wb-01`, which sits on current dev (`0b3f899`).

- `uv run pytest` — `3 failed, 532 passed, 2 warnings`. The three failures
  (`test_demo_terminal.py::test_posix_adapter_reports_alive_then_not_alive`,
  `::test_resize_text_frame_applies_to_pty_window_size`,
  `::test_two_concurrent_websocket_sessions_are_independent_shells`) fail identically on dev
  (`3 failed, 37 passed` for the same file at dev's tip): the host's pyenv shim rehash fails
  inside the spawned PTY shell (`pyenv: cannot rehash: couldn't acquire lock ... cannot
  overwrite existing file`) and pollutes the output the assertions search. Pre-existing
  host-environment defect, not introduced by this phase; none of the failing tests touch this
  phase's diff.
- `uv run ruff check src/ test/` — `All checks passed!`
- `uv run mypy src/` — `Success: no issues found in 24 source files`.
- `uv run python -m src.governance` — `Governance OK: 18 systems, 154 documents, 16 memories,
  119 backlog phases`, exit 0.
- `uv run python tools/check_no_private_content.py` with all changes staged (`git add -A`
  first) — `check_no_private_content: OK (462 tracked files, 0 identifiers checked)`.
- Adversarial review (pack W01-A) — run by the coordinator; one BLOCKER reported and closed
  (see below). Post-fix, in the worktree: `uv run pytest test/test_workbench_api.py` —
  `36 passed, 2 warnings`; `uv run ruff check src/ test/` — `All checks passed!`;
  `uv run mypy src/` — `Success: no issues found in 24 source files`.

W01-A blocker and closure: `/reveal` could be pointed at `_private/` or any gitignored path
and would spawn a real opener — only the path-escape check (`resolve_repo_relative_path`)
ran on the reveal path; the listings' private/gitignored exclusion was never applied. Fixed
in W01-C2 fix cycle 1 (`991df62`): `reveal_in_explorer` now passes the resolved path through
`_is_reveal_excluded` (the same `git check-ignore` mechanism the listing routes use) before
any spawn, refusing with 400; two new tests assert no spawn for a `_private/` path and for a
gitignored fixture path. W01-V2 was re-dispatched after the fix and returned PASS with no
findings.

Work-item validators: W01-V1 ran and produced one fix cycle (`ca7fd8e`, proving the
`_private/` exclusion with a real fixture dir); W01-V2 passed (re-validated green after the
W01-A fix cycle, `991df62`) and W01-V3 passed with no findings against the diff. The phase
gate (W01-G) recorded 5 of 6 items green; its single red item is the mechanical `pytest`
exit code, caused solely by the three pre-existing dev failures above.

## Acceptance

- Flag gating and the W14 rejection matrix — **Met**: with the flag unset every workbench
  route is 404; traversal, absolute-path and symlink-escape requests refused; listings free of
  `_private/` and gitignored entries; reads GET-only (W01-V1/W01-V2 verdicts, 34/34
  `test_workbench_api.py` tests passing).
- Enumeration matches the three directories minus hidden overrides, relabel and text
  replacement reflected — **Met**: verified by W01-V1 after the fix cycle; covered by passing
  tests.
- Idea route matches an independent `fold()` run; backlog route matches `--ready` ordering —
  **Met**: W01-V2 confirmed the test recomputes independently via `queue_order()`/`readiness()`
  and that no direct read of `_data/ideas.jsonl` exists in the diff.
- Fifth session refused server-side; cmd/powershell on Linux return the structured
  unavailable-shell refusal; non-allowlisted shell rejected — **Met**: W01-V3 confirmed all
  three non-vacuously (four real sessions opened before the fifth's refusal; readmission
  proven with a real echo round trip).

## Backlog

`status: active`, `agent: agent-demo-stage`. `next_action`: adversarial review (pack W01-A,
coordinator-dispatched) per the phase's verification list, then owner-approved integration;
the three pre-existing `test_demo_terminal.py` PTY failures on dev (host pyenv shim
contention) are reported up as a finding, not fixed in this phase.

## Unresolved

- The three pre-existing PTY test failures fail identically on dev and block a mechanically
  green `uv run pytest` anywhere until the host pyenv shim contention is addressed — a
  host-environment finding for the owner/coordinator, outside this phase's scope.
- W01-A (adversarial review) has not run; it is the coordinator's dispatch and part of the
  GOV-003 completion gate.
