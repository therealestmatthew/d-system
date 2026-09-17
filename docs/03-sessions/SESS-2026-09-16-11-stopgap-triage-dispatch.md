---
schema_version: 1
id: doc-session-stopgap-triage-dispatch
code: SESS-2026-09-16-11
title: Stopgap triage dispatch shipped with watch, sweep and claim guard
kind: session
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-realization, sys-portfolio]
depends_on: [doc-idea-realization-system-plan, doc-idea-realization-system-requirements, doc-idea-realization-system, doc-irs-orchestrator-design, doc-build-coordinator]
---

# Stopgap triage dispatch shipped with watch, sweep and claim guard

Fifth and final phase of [PROMPT-036](../02-prompts/PROMPT-036-build-coordinator.md) batch 1,
built by dispatched agents under the coordinator (`agent-build`), executing **phase-irs-01** —
stopgap triage dispatch on append, with the reconciling sweep — per PLAN-039.01 §10's ruled
mechanism.

## Outcome

`tools/idea_dispatch.py` is a self-contained interim dispatcher: a `watch` command polls the idea
log for new `created` events past an install-time watermark and dispatches one triage agent per
idea (`claude -p "/idea-triage <id>"`, encapsulated behind a stubbing seam); `dispatch` is the
manual fallback and `sweep` re-dispatches post-watermark ideas still open, so failure degrades to
batch, never to loss. Per the owner's ruling, `append_idea.py` is untouched. Dispatch is bounded
by atomic per-idea claim files (stale claims taken over after 1 hour, preserving crash recovery),
and every command re-checks the `_working/orchestrator-halt` kill switch before each dispatch.
The operations document (`OPS-016`) marks the tool interim — `phase-irs-04`'s daemon retires it,
`phase-auto-01` rules the external-gateway question — and states that GOV-014's 300k token
ceiling is a contract obligation on the dispatched agent, not host-enforced. 30 tests.

## Evidence

- `uv run pytest`: 629 passed (30 in `test/test_idea_dispatch.py`). Governance OK. Re-run by the
  coordinator directly.
- First validator run FAILED R06 — dispatch was manual-only. Fix cycle 1 added `watch`/
  `poll_once` and an end-to-end trigger test (real `append_idea.add` detected by the poll, no
  human action). The validator's other verdicts (R07 real mid-run kill and sweep recovery; halt
  flag block/restore; OPS-016 interim statement) passed.
- Adversarial review then found one major — a double-dispatch race between concurrent watch/sweep,
  reproduced with a threaded script — and three minors (halt-check claim mismatch, cold-start
  watermark exclusion invisible, decorative budget parameter). All four fixed in cycle 2
  (`809bd2a`) with 11 new tests, including a two-path single-dispatch assertion and a
  stale-claim takeover test.

## Unresolved

- Both fix cycles were spent; no findings remain open. The real `claude -p` invocation is
  deliberately untested end-to-end (tests stub the dispatch seam); first live use is the
  remaining exposure and OPS-016 says so.

Full evidence trail in `_working/build-b1/phase-irs-01.md` (gitignored).
