---
schema_version: 1
id: doc-session-workbench-planning
code: SESS-2026-09-10-09
title: Workbench planning — requirement, decisions, phases and delegation pack
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-ui, sys-demo-stage, sys-api, sys-backlog, sys-governance]
depends_on: [doc-prompt-workbench-pre-plan-package, doc-workbench]
---

# Workbench planning — requirement, decisions, phases and delegation pack

## Phase

None claimed. This session executed the workbench pre-plan package's planner prompt
(`PROMPT-020`) — a documentation-and-`.claude/`-only session run directly on `dev` per
`GOV-003` — and *produced* the seven `phase-wb-*` phases rather than working one. Active claims
throughout, untouched: the portable-workflows phase (`phase-port-01`, `agent-codex-port`) and
the glossary phase (`phase-demo-07`, `agent-demo-glossary`).

## Verification

- `uv run python -m src.governance` — `Governance OK: 18 systems, 148 documents, 15 memories,
  119 backlog phases`, exit 0 (also confirmed exit 0 before any change was made).
- `uv run python -m src.governance --ready` — the seven `phase-wb-*` phases render at queue
  positions 1–7, `phase-wb-01` ready with an empty Conflicts column and the rest waiting on
  the sequential dependency chain; the two peer claims unchanged. (A Conflicts column of `—`
  says nothing about the `max_active` budget — the pack audit below corrected an earlier
  over-reading of this report.)
- `uv run pytest` — 495 passed, 2 warnings.
- `uv run python tools/check_no_private_content.py`, run with all changes staged —
  `check_no_private_content: OK (447 tracked files, 31 identifiers checked)`.
- `uv run python -m src.governance --catalog` — catalog regenerated and committed;
  `docs/00-working/ideas.md` regenerated after the idea `000087` annotation (90 ideas).

## Produced

- **Requirement** — the workbench requirements (`REQ-007`): rows W01–W14 with mechanical
  browser-verification methods, plus the descope ladder.
- **Decisions** — the workbench terminal capability (`ADR-014`, supersedes and narrows the demo
  terminal decision `ADR-013`; session registry and shell allowlist; flag and loopback binding
  kept), the workbench read/action API surface (`ADR-015`), and layout persistence (`ADR-016`).
- **Plan** — the workbench plan (`PLAN-022`), seven `phase-wb-*` phases in
  `docs/09-backlog/backlog.yaml` at the front of `next_up`, the `phase-wb-*` prefix gloss in the
  backlog README, and `systems.yaml` updates (sys-ui carries the workbench charter;
  sys-demo-stage marked implemented and evolving into it).
- **Agent-roster deltas** — all ten demo agents' charters extended to the workbench track
  (`.claude/agents/`), no new agents, fences in `.claude/settings.json` untouched, model policy
  (`PROMPT-012`) unchanged.
- **Delegation pack** — the workbench delegation pack (`PROMPT-021`), one verbatim-dispatchable
  idempotent prompt per dispatch in the `PROMPT-018` conventions; the completion-gate decision
  in `GOV-003` extended to `phase-wb-*` in that document.
- **Build coordinator prompt** — the workbench build orchestration prompt (`PROMPT-022`), the
  `PROMPT-014` shape.
- **Idea log** — idea `000087` (terminal interaction API) annotated via the sanctioned writer:
  its session-registry half is adopted by `ADR-014`/`phase-wb-01`; the inject/read API remains
  its open scope.

## Owner inputs recorded

All seven of `PROMPT-020`'s open questions were resolved with the owner in this session
(2026-09-10) and are recorded in `REQ-007` and the ADRs: two shipped layouts; assignment-only
configuration surface; viewer + one explorer slot on the right; `.html`+`.svg` viewer
compatibility; in-app directory dialogs; five context-menu actions; gated both-platform
reveal-in-explorer; `next_up`+priority queue views; slash/natural injection texts; one
overrides file; notes-file picker in the strip dropdown.

## Post-pack audits (2026-09-10, owner-directed)

Two independent audits ran after the pack was committed. A haiku coverage audit against
`PROMPT-020` found no missing or partial item. An adversarial audit (`demo-adversary`, in a
scratch worktree, changing nothing) surfaced five findings, all fixed in this session with the
owner's direction:

1. **Blocker** — the coordinator's `phase-wb-01` ∥ `phase-wb-02` parallel dispatch was
   mechanically rejected by the validator (one claim id, one active phase; reproduced). Owner
   chose strictly sequential: the whole track now runs one phase at a time, `phase-wb-02`
   depends on `phase-wb-01`, and `PROMPT-021`/`PROMPT-022`/`PLAN-022`/backlog were aligned.
2. **Blocker** — the same parallel claim exceeded `max_active: 3` with the two peers active
   (reproduced: "4 found"). `PROMPT-022`'s preflight and both stage kickoffs now carry an
   explicit numeric budget check, separate from the Conflicts column.
3. **Major** — `ADR-015` described the notes-file picker (W01) as API-fed while `phase-wb-02`
   had no `phase-wb-01` dependency and its creator prompt hardcoded `ts/public/`. Owner chose
   the API-fed picker: `phase-wb-02` now depends on `phase-wb-01`, `W02-C2`/`W02-V2`/`W02-A`
   and REQ-007 W01 name the listing route, and `W02-A`'s specification list gained `ADR-015`.
4. **Major** — the `ADR-013` supersession was prose-only, so the governance supersession check
   never fired. `ADR-014` now carries `supersedes: [doc-demo-terminal-decision]`, `ADR-013` is
   `status: superseded` with a banner pointing forward.
5. **Major** — REQ-007 W09's clipboard assertions were not mechanically checkable under the
   Playwright MCP toolset. W09 and `W05-W` now verify copies by stubbing
   `navigator.clipboard.writeText` via script injection and asserting the passed string.

## Unresolved

- The build has not started — by design. The owner reviews this pack, then starts a fresh
  session with `PROMPT-022`.
- `phase-wb-07`'s owner-machine conditions (REQ-006 R06, owner-driven R09, REQ-007 W12 Windows
  half) are deferred owner work carried from the demo track, closable only by the owner's
  recorded results (GOV-003 workbench extension).
- `phase-demo-07` remains active with its concurrent session; nothing here touches it.
