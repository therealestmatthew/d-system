---
schema_version: 1
id: doc-session-demo-agent-factory
code: SESS-2026-09-10-01
title: Demo agent factory — roster, governance pack and delegation prompts
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-backlog, sys-demo-stage, sys-demo-overview]
depends_on: [doc-live-demo, doc-prompt-demo-agent-factory]
---

# Demo agent factory — roster, governance pack and delegation prompts

## Phase

None claimed. This session executed the agent factory prompt (`PROMPT-010`) — a
documentation-and-`.claude/`-only session run directly on `dev` per `GOV-003` — and *produced* the
five `phase-demo-*` phases rather than working one. The only active claim throughout was the
peer's portable-workflows phase (`phase-port-01`, `agent-codex-port`), untouched.

## Verification

- `uv run python -m src.governance` — `Governance OK: 18 systems, 127 documents, 15 memories,
  110 backlog phases`, exit 0 (also confirmed exit 0 before any change was made).
- `uv run python tools/check_no_private_content.py`, run with all changes staged (staging
  excluded the peer's untracked `.agents/` and `.codex/`) —
  `check_no_private_content: OK (385 tracked files, 31 identifiers checked)`.
- `uv run python -m src.governance --catalog` — catalog regenerated; a subsequent regeneration
  produced no diff.
- Validation gate (`PROMPT-013` section 3), dispatched to a checklist validator: all six items
  green — agent frontmatter/model/tool policy; all 39 delegation-pack blocks carry the
  idempotency clause, agent, absolute worktree path, branch, ports and stop condition; the five
  phases are consistent and disjoint from the peer's systems; governed front matter and clean
  catalog; staged private-content check; descope ladder / 15-minute timebox / Windows R06
  cross-document consistency.
- Smoke tests: all eight roster agents exercised once with trivial in-character tasks; all
  passed, writing only to the scratch directory. Seven ran as general-purpose agents following
  the definition files (the types were not yet registered mid-session); after registration, a
  real-type dispatch of `demo-validator-check` loaded and ran under its own definition, exit 0.

## Acceptance

Against `PROMPT-010`'s completion conditions: governance exit 0 — Met. Staged private-content
check — Met. No `src/`, `ts/`, `templates/` or `tools/` code written — Met (deliverables are
documents, backlog/registry entries, agent definitions and `.claude/settings.json` only).
Validator findings fixed or reported — Met (none outstanding). Checkpoint skill — run;
its own contract stops it when no phase is active for the session, which is this case.

## Backlog

Five new phases under the live demo plan (`PLAN-021`): `phase-demo-01` (terminal backend),
`phase-demo-03` (deterministic overview tools) — both `queued`, ready, Conflicts `—`;
`phase-demo-02` (stage frontend), `phase-demo-04` (overview generation), `phase-demo-05`
(content and readiness) — `queued`, waiting on their dependencies. `next_up` is now
`phase-demo-01, phase-demo-03, phase-demo-02, phase-demo-04, phase-demo-05, phase-port-01,
phase-ses-01`. Codes `OPS-011`–`OPS-014` reserved for the phases' tool documents.

## Permission fences

`.claude/settings.json` was created with deny rules (`PROMPT-013` section 2), each fencing a
standing limit that was previously instructional only:

- `Edit`/`Write` on `AGENTS.md` and `CLAUDE.md` — no agent edits the governing files without
  explicit per-change approval (`AGENTS.md`'s own first rule).
- `Edit`/`Write` under `_private/` — gitignored confidential portfolio; agents never write there.
- `Edit`/`Write` under `.agents/` and `.codex/` — the peer's active-phase files
  (`phase-port-01`); no other agent may touch them.
- `Edit`/`Write` on `_data/ideas.jsonl` — the append-only idea log accepts writes only through
  `tools/append_idea.py`, which runs via Bash and is unaffected by the fence.

## Unresolved

- The live demo plan (`PLAN-021`) carries `status: draft`; the owner's review flips it to
  approved — the factory does not self-approve a plan.
- The Windows terminal smoke check (`REQ-006` R06) can only run on the presentation machine; the
  delegation pack has `phase-demo-05` report it as outstanding owner-machine work.
- The live-segment runbook and Windows checklist are specified as ungoverned documents under
  `docs/00-working/` so the demo machine's clone carries them; the owner may prefer a governed
  home after the demo.
