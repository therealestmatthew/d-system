---
schema_version: 1
id: doc-session-demo-data-overview-tools
code: SESS-2026-09-10-02
title: Demo data orchestration — deterministic overview tools (phase-demo-03)
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-demo-overview]
depends_on: [doc-live-demo, doc-prompt-demo-build-delegation-pack]
---

# Demo data orchestration — deterministic overview tools (phase-demo-03)

## Phase

`phase-demo-03` — Build the deterministic overview tools.

## Verification

- `uv run pytest` — `417 passed, 2 warnings`.
- `uv run ruff check src/ test/` — `All checks passed!`.
- `uv run mypy src/` — `Success: no issues found in 15 source files`.
- `uv run python -m src.governance` — `Governance OK: 18 systems, 131 documents, 15 memories,
  110 backlog phases`, exit 0.
- `uv run python tools/check_no_private_content.py`, run with all changes staged (the worktree
  was already fully committed, so `git add -A` staged nothing) —
  `check_no_private_content: OK (394 tracked files, 0 identifiers checked)`.
- Determinism (REQ-006 R07): `tools/overview_metrics.py` run twice against the unchanged tree,
  `diff` between the two outputs — empty (byte-identical). `tools/overview_inventory.py` run
  twice, `diff` — empty (byte-identical).
- Adversarial review (D03-A) — not yet dispatched. Per `PROMPT-018`'s completion-gate convention
  and `GOV-003`'s demo-track completion decision, D03-A is dispatched by the build coordinator at
  `PROMPT-015` step 8, not by this orchestrator.

## Acceptance

- Running each tool twice against an unchanged repository produces byte-identical output
  (REQ-006 R07) — Met (empty diffs recorded above).
- Reported idea metrics match an independent recomputation over the same log in the tests — Met
  (`test_funnel_counts_match_independent_recomputation_over_the_real_log` recomputes via a fresh
  `fold()` + `Counter` and passes).
- OPS-011 and OPS-012 exist with filled generated blocks and the governance check passes — Met
  (both documents carry non-empty `<!-- generated:tool-reference:start/end -->` blocks; their
  `codes.yaml` reservations are removed in the same branch; `catalog.md` is regenerated and
  committed; governance exits 0).

## Backlog

`phase-demo-03`: `status: active`, `agent: agent-demo-data`. All three work items (D03-C1/V1,
D03-C2/V2, D03-C3) and the D03-G phase gate are green on `agent/phase-demo-03`, committed but not
yet integrated into `dev`. Remaining is the coordinator's D03-A adversarial review and the
completion/integration decision (`GOV-003` demo-track gate) — neither is this orchestrator's to
perform. `completion_evidence` and `result` are recorded below per the checkpoint contract while
the phase stays `active`.

## Unresolved

- D03-A (adversarial review) and the phase's completion/integration decision belong to the build
  coordinator, not this orchestrator — not performed here by design.
- `agent/phase-demo-03` is not integrated into `dev` and not pushed; no push was requested.
- `phase-demo-04` (the next phase this orchestrator drives, `agent-demo-data`) depends on
  `phase-demo-03` being integrated into `dev` AND marked `status: complete` by the coordinator —
  it cannot be claimed yet.
