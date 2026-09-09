---
schema_version: 1
id: doc-plans-directory-consolidation
code: PLAN-018
title: Plans directory consolidation
kind: plan
status: approved
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-governance, sys-memory-agents]
depends_on: [doc-governance-protocol]
---

# Plans directory consolidation

## Outcome and scope

Retire root `plans/` as a governed concept. It currently holds two files kept there by deliberate
prose exceptions rather than any structural need: `PLAN-001-agent-memory-system.md` (governed,
"remains at its existing path for link compatibility" per `GOV-001-protocol.md:60`) and
`codex_governance_prompt.md` (ungoverned, exempt by name). The owner decided the split is not worth
preserving. [The requirements](../06-requirements/REQ-004-plans-directory-consolidation.md) state
the observable contract this satisfies.

## Ordered work and acceptance

| Step | Change | Acceptance evidence required |
|---|---|---|
| 1 | `git mv plans/PLAN-001-agent-memory-system.md docs/01-plans/PLAN-001-agent-memory-system.md`; fix its two internal relative links (`../docs/...` → `../...`) | File resolves at new path with unchanged `id`/`code`; both links still resolve |
| 2 | `git mv plans/codex_governance_prompt.md docs/02-prompts/codex_governance_prompt.md` | File resolves at new path, byte-identical content |
| 3 | Update `src/governance/__main__.py`: `EXEMPT` entry to the new prompt path; drop `"plans"` from the discovery tuple | `uv run python -m src.governance` still exempts the prompt file; no file under a nonexistent `plans/` is scanned |
| 4 | Drop `plans/` from `codes.yaml`'s `PLAN` series `locations`; update `GOV-005-document-codes.md`'s matching table row | `codes.yaml` lists one location; `GOV-005` matches it |
| 5 | Update `GOV-001-protocol.md` (drop the link-compatibility sentence at line 60, drop "and `plans/`" at line 64, update the exempted path at line 155) | No remaining `GOV-001` sentence describes `plans/` as scanned or as PLAN-001's home |
| 6 | Add a reversal entry to `GOV-003-backlog-decisions.md` recording the old rule, the new rule, and why | Entry present, dated, naming this plan |
| 7 | Fix inbound references: `README.md`, `docs/09-backlog/README.md`, `docs/09-backlog/backlog.yaml` (`phase-mem-01` deliverable), `docs/08-governance/systems.yaml` (`sys-memory-agents` path — existence-checked), `docs/07-architecture/ARCH-002-system-audit.md`, `docs/06-requirements/REQ-001-document-code-requirements.md`, `docs/02-prompts/PROMPT-004-terminology-and-architecture.md`, `brain/concepts/terms-documents-and-governance.md`, `_tmpagent/AGENTS.md` | `grep -rn '\bplans/'` outside `docs/01-plans/` and the historical documents named below returns nothing |
| 8 | Regenerate `docs/08-governance/GLOSSARY.md` (`uv run python tools/generate_glossary.py`) and `docs/08-governance/catalog.md` (`--catalog`) | Both match their generators; no hand edits |

**Not edited** — historical records describing what was true when written: `PLAN-005`'s Phase 4
rename table, `SESS-2026-09-05-01-document-code-system.md`, `ADR-012-systems-review.md` (cites
`PLAN-001–017` as a numeric range only).

## Dependencies and review

Steps 3–6 (governance machinery) must land before or with steps 1–2 (the actual `git mv`), since the
`EXEMPT` path and the `codes.yaml` location list are what let the moved files keep validating in
their new spots. Step 7's `systems.yaml` edit is the one hard existence-check landmine — missing it
fails `uv run python -m src.governance` outright, not just a link check. Mark this plan complete only
after `uv run python -m src.governance` and `uv run pytest` both pass and are recorded in
`completion_evidence`.

## Open questions

None outstanding — `codex_governance_prompt.md`'s destination (`docs/02-prompts/`) was confirmed with
the owner before this plan was written.
