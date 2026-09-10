---
schema_version: 1
id: doc-session-demo-data-overview-skill
code: SESS-2026-09-10-03
title: Demo data orchestration — overview skill, templates and page generation (phase-demo-04)
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-html, sys-demo-overview]
depends_on: [doc-live-demo, doc-prompt-demo-build-delegation-pack]
---

# Demo data orchestration — overview skill, templates and page generation (phase-demo-04)

## Phase

`phase-demo-04` — Build the overview skill, templates and page generation.

## Verification

- `uv run pytest` — `436 passed, 2 warnings`.
- `uv run ruff check src/ test/` — `All checks passed!`.
- `uv run mypy src/` — `Success: no issues found in 15 source files`.
- `uv run python -m src.governance` — `Governance OK: 18 systems, 132 documents, 15 memories,
  110 backlog phases`, exit 0.
- `uv run python tools/check_no_private_content.py`, run with all changes staged (`git add -A`
  staged nothing new — the worktree was already fully committed) —
  `check_no_private_content: OK (407 tracked files, 0 identifiers checked)`.
- Double-generation determinism (REQ-006 R08): `tools/generate_overview.py` run twice against the
  unchanged tree to two scratch paths, `diff` between the two outputs — empty (byte-identical);
  `git status --short` after both runs — clean (the tracked `_public/overview/index.html` was
  unchanged by regeneration).
- Adversarial review (D04-A) and Playwright verification (D04-W) — not yet dispatched. Per
  `PROMPT-018`'s completion-gate convention and `GOV-003`'s demo-track completion decision, both
  are dispatched by the build coordinator at `PROMPT-015` step 8, not by this orchestrator.

## Acceptance

- Invoking the skill produces the overview page under `_public/` and every figure on it matches
  the corresponding tool output — Met (D04-V2 and D04-G both cross-checked page figures against
  `overview_metrics.py`/`overview_inventory.py`'s own JSON; `test_generate_overview.py` asserts
  this directly).
- Two generations against an unchanged repository produce an identical page — Met (empty diff
  recorded above, both in D04-V2's independent check and this orchestrator's own run).
- The skill definition contains no recomputation of tool-owned numbers — Met (D04-V3 quoted the
  skill's explicit prohibitions on recomputing, restating from memory, or hand-editing the
  generated page; verified against `.claude/skills/d-system-overview/SKILL.md`).

## Backlog

`phase-demo-04`: `status: active`, `agent: agent-demo-data`. All four work items (D04-C1/V1,
D04-C2/V2, D04-C3/V3, D04-C4) and the D04-G phase gate are green on `agent/phase-demo-04`,
committed but not yet integrated into `dev`. Remaining is the coordinator's D04-A adversarial
review, D04-W Playwright verification, and the completion/integration decision (`GOV-003`
demo-track gate) — none of this is this orchestrator's to perform. `completion_evidence` and
`result` are recorded in `backlog.yaml` while the phase stays `active`.

## Unresolved

- D04-A (adversarial review) and D04-W (Playwright verification of the generated page) belong to
  the build coordinator, not this orchestrator — not performed here by design.
- `agent/phase-demo-04` is not integrated into `dev` and not pushed; no push was requested.
- One observation for the coordinator, not a blocker for this phase: `test/test_codes.py::test_committed_catalog_matches_regenerated_output`
  was reported by the D04-C2 dispatch as failing on a pre-existing basis (confirmed via `git
  stash` before that dispatch's changes) — this orchestrator's own full `uv run pytest` run above
  shows `436 passed`, so it is not currently failing on `agent/phase-demo-04` after D04-C4's
  catalog regeneration; flagging in case it resurfaces on `dev` or during integration.
