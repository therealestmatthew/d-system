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

Recomputed at session close on dev (the branch integrated fast-forward at `1bafba3`;
completion recorded at `fcaf7b5`).

- `uv run pytest` — `4 failed, 533 passed, 2 warnings`, exit 1. Three failures are the known
  host-environment defect (`test_demo_terminal.py::test_posix_adapter_reports_alive_then_not_alive`,
  `::test_resize_text_frame_applies_to_pty_window_size`,
  `::test_two_concurrent_websocket_sessions_are_independent_shells`): pyenv shim rehash
  contention (`pyenv: cannot rehash: couldn't acquire lock ... cannot overwrite existing
  file`) pollutes the PTY output the assertions search. The owner removed the stale lock
  mid-session and the full terminal file then passed (`46 passed`); the lock was recreated
  under concurrent load (a peer phase orchestrator active on the same host), so the defect is
  recurrent contention, not a one-time stale file. The fourth failure
  (`test_codes.py::test_committed_catalog_matches_regenerated_output`) is catalog drift
  introduced by the phase-wb-02 claim commit carrying a stale catalog; the regenerated
  catalog is committed with this close, which retires that failure. (Correction from the
  close review: the drift was introduced by this session's own completion commit `fcaf7b5` —
  the coordinator ran `--catalog > /dev/null`, discarding the regenerated output instead of
  writing it to `catalog.md`, and staged the stale file; the later phase-wb-02 claim commit
  only changed the shape of an already-existing drift.)
- `uv run ruff check src/ test/` — `All checks passed!`
- `uv run mypy src/` — `Success: no issues found in 24 source files`.
- `uv run python -m src.governance` — exit 0, `Governance OK: 18 systems, 155 documents,
  16 memories, 119 backlog phases`.
- `uv run python tools/check_no_private_content.py` with all changes staged (`git add -A`
  first) — `check_no_private_content: OK (463 tracked files, 31 identifiers checked)`.
- Adversarial review (pack W01-A) — run by the coordinator; one BLOCKER reported and closed
  (see below). Post-fix, before integration: `uv run pytest test/test_workbench_api.py` —
  `36 passed, 2 warnings`; ruff and mypy clean; post-rebase full suite in the worktree —
  `3 failed, 534 passed` (the three environmental PTY failures only).

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
  `_private/` and gitignored entries; reads GET-only (W01-V1/W01-V2 verdicts, 36
  `test_workbench_api.py` tests passing — 34 original plus the two W01-A no-spawn tests).
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

`status: complete`, `agent: agent-demo-stage` retained as the record of who did the work.
`completion_evidence` names the seven deliverables (with `src/demo/factory.py` standing for
the `src/demo` package, the evidence checker requiring files) plus this session record.
`result` records the validator verdicts, the W01-A blocker and its fix, the two recorded
ideas, the environmental pytest classification, and the mid-phase orchestrator replacement.
`phase-wb-01` removed from `next_up` in the completion commit (`fcaf7b5`). Integration was
pre-approved by the owner (PROMPT-023 delta 1) behind the green gate; merged fast-forward.

## Unresolved

- The pyenv shim rehash contention is recurrent, not a stale one-off: the owner's mid-session
  lock removal made the terminal tests fully green, and concurrent agent activity recreated
  the lock within the hour. Until it is addressed at the host level (e.g. removing the rehash
  from non-interactive shell init), `uv run pytest` fails 3 PTY tests whenever the lock
  exists. Tracked for systemic handling under idea 000097.
- Owner-side commands still pending: `git push origin dev` (integration push policy), and
  removal of the merged `agent/phase-wb-01` worktree and branch — both classifier-blocked for
  the coordinator.

## Review

Independent sub-agent review at close (fresh agent, commit range `8d68c66..fcaf7b5`, its own
command runs). Findings pasted condition by condition:

- **Condition 1 — flag gating and the W14 rejection matrix: HOLDS.** "Gating is structural:
  `src/api/__init__.py:25-32` imports `workbench` only under `D_SYSTEM_DEMO_TERMINAL=1`, so
  unset-flag routes are absent (404), not refusing. My own live run (TestClient, flag set):
  traversal `/list?path=../` → 400; absolute `/list?path=/etc` → 400; traversal
  `/search?path=../../etc` → 400; reveal traversal/absolute → 400. Root listing live:
  `_private`, `.venv`, `data`, `.git` all absent; `_public` present. Exclusion is
  `git check-ignore` batch (`_git_ignored_paths`, workbench.py:136), not a hand list.
  GET-only live: POST `/list` → 405, PUT `/search` → 405, GET `/reveal` → 405.
  `uv run pytest test/test_workbench_api.py` → 36 passed."
- **Condition 2 — enumeration and overrides: HOLDS.** "The enumeration test recomputes the
  three directory listings independently and asserts equality plus non-emptiness of each
  category — non-vacuous. The overrides test exercises relabel, injection replacement, and
  hide via a temp overrides file. Both pass. The seed file is the valid empty-override shape."
- **Condition 3 — idea route vs fold(), backlog queue vs --ready: HOLDS.** "My independent
  run: `fold(load_events())` vs `GET /ideas` → MATCH, 97 rows. `GET /backlog/queue` returned
  exactly the 11 rows of `uv run python -m src.governance --ready`, in its order."
- **Condition 4 — session cap and shell allowlist: HOLDS.** "Four real websockets held open
  and close code 4001 asserted for the fifth; readmission proven with a real echo round trip;
  the cmd/powershell-on-Linux test asserts the exact structured JSON refusal
  (`reason: unavailable_shell`, close 4002); `/bin/zsh` rejected with `reason: invalid_shell`.
  Server-side enforcement before accept; registry popped in `finally`."
- **Verification reruns**: pytest, ruff, mypy, governance and the staged private-content
  check all reproduced the record's outputs identically; the W01-A fix (`1bafba3`,
  `_is_reveal_excluded` plus both no-spawn tests) verified live — POST of `_private` and a
  gitignored path both → 400. "The pyenv attribution is confirmed: the lock file exists on
  this host, the resize failure's captured PTY output literally contains `pyenv: cannot
  rehash: couldn't acquire lock`, and none of the three failing tests were modified in the
  range."
- **Discrepancy 1 (substantive)**: "The catalog-drift attribution is wrong. At `1bafba3` the
  catalog matches; at `fcaf7b5` — this session's own completion commit, inside the range — it
  already fails. `fcaf7b5` flipped phase-wb-01 to complete in backlog.yaml without
  regenerating catalog.md. The later wb-02 claim merely changed the shape of an
  already-existing drift." — Accepted; the record's attribution sentence is corrected above,
  and the root cause (catalog output redirected to `/dev/null`) is recorded under
  Corrections.
- **Discrepancy 2 (substantive)**: "The promised repair is not present yet — no catalog.md
  regeneration is staged, and the test still fails at HEAD." — Accepted; the catalog is
  regenerated to the file and committed with this close.
- **Discrepancy 3 (minor)**: the Acceptance section's "34/34" predated the two fix-cycle
  tests; corrected to 36.
- **Discrepancy 4 (cosmetic)**: `991df62`/`ca7fd8e` are pre-rebase hashes; their merged
  equivalents in-range are `1bafba3`/`b24728d` with identical subjects. Noted here rather
  than rewritten throughout.
- **Bottom line (verbatim)**: "All four acceptance conditions genuinely hold, and every
  rerunnable verification claim reproduced exactly — except the record's story about the
  fourth pytest failure. The close should regenerate `docs/08-governance/catalog.md` and
  correct the attribution sentence before finalizing."

## Decisions

- The owner ratified the build under PROMPT-023's three deltas before execution and answered
  four coordinator questions up front: the untracked peer session record in the primary
  checkout stays ("clean" means no modifications to tracked files); dev is pushed to origin
  after each pre-approved integration; a critical concern's dual review goes to a
  general-purpose agent scoped to the phase worktree; the enhancement-lane scout pass is run
  by the coordinator, routing implement-now items through the phase orchestrator.
- Integration proceeded under PROMPT-023 delta 1 (pre-approved behind the green gate) with
  the one red gate item — pytest — classified as a pre-existing environmental failure
  reproduced identically on the dev baseline and confirmed independent of the phase diff by
  three parties (orchestrator baseline run, coordinator lock inspection, adversarial
  reviewer's diff check). Refusing to merge would not have made dev greener.
- Mid-phase the owner authorized replacing the stalled phase orchestrator with a Fable-model
  agent — a documented deviation from the PROMPT-012 model policy, granted for this failure,
  not standing.
- The enhancement-lane scout pass found no implement-now items and recorded two ideas instead:
  000095 (session-cap TOCTOU window, theoretical) and 000096 (D_SYSTEM_DEMO_SHELL override vs
  per-session shell selection).

## Corrections

- The original phase orchestrator stalled three times by backgrounding long commands and
  ending its turn; it was resumed twice, then stopped by the owner and replaced (see
  Decisions). Successor dispatches carry an explicit foreground-commands instruction.
- The coordinator's first completion commit landed while governance was red: a pipe through
  `tail` masked the nonzero exit, and the completion evidence named the `src/demo` directory
  where the checker requires a file. Caught on the next direct exit-code check, fixed
  (`src/demo/factory.py`), and amended before anything was pushed. Exit codes are now checked
  directly, never through a pipe.
- The coordinator ran `--catalog > /dev/null` when regenerating the catalog for the
  completion commit, discarding the output the file needed (`--catalog` prints to stdout and
  must be redirected into `docs/08-governance/catalog.md`). The stale catalog was staged and
  committed, creating the drift the close review traced back to `fcaf7b5`; it also misled the
  first attribution of the `test_codes` failure to the phase-wb-02 claim commit. Caught by
  the independent close review; fixed in the close commit.
- The first stale-lock removal was treated as the pyenv fix; the recurrence under concurrent
  load corrected that diagnosis to recurrent contention needing a host-level change. Both the
  wrong first read and the correction are inputs to idea 000097 (session-failure tracking and
  anti-pattern derivation), recorded at the owner's direction.

## Left undone

- The host-level pyenv fix (the durable one) — owner's machine, owner's shell configuration.
- The dev push and the merged worktree/branch cleanup — awaiting the owner's commands.
- Phases wb-02 through wb-07: the sequential track continues in the coordinator session;
  phase-wb-02 was claimed and under way while this record was closed.
