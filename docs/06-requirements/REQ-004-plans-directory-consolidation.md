---
schema_version: 1
id: doc-plans-directory-consolidation-requirements
code: REQ-004
title: Plans directory consolidation requirements
kind: requirement
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-governance, sys-memory-agents]
depends_on: [doc-governance-protocol]
---

# Plans directory consolidation requirements

Observable requirements for retiring the root `plans/` directory as a governed concept and
consolidating its two files under the taxonomy `GOV-001-protocol.md` already states as canonical.
Each requirement states what must be true and how to verify it.
[The implementation plan](../01-plans/PLAN-018-plans-directory-consolidation.md) describes how and
when they are met.

## Problem being solved

Root `plans/` holds exactly two files, kept there by two separate prose exceptions rather than by
any structural need: `PLAN-001-agent-memory-system.md` (a governed plan `GOV-001-protocol.md:60`
says "remains at its existing path for link compatibility") and `codex_governance_prompt.md` (the
ungoverned bootstrap prompt, exempted by name in `GOV-001-protocol.md:155` and hardcoded into
`src/governance/__main__.py`'s `EXEMPT` set). The `PLAN` series in `docs/08-governance/codes.yaml`
still lists `plans/` as a second valid location, and the discovery loop in `__main__.py:214` still
scans it as a third root alongside `docs/` and `brain/`. The owner decided the split is not worth
preserving.

## Accepted decisions

| Decision | Choice |
|---|---|
| PLAN-001's destination | `docs/01-plans/PLAN-001-agent-memory-system.md`; `id`/`code` unchanged, only the path moves |
| codex_governance_prompt.md's destination | `docs/02-prompts/codex_governance_prompt.md`; stays ungoverned/exempt, does not become a coded `PROMPT-*` document |
| `plans/` as a concept | Retired entirely — dropped from `codes.yaml`'s `PLAN` locations and from the discovery loop, not just emptied of files |
| Historical documents | `PLAN-005`'s phase-4 rename table and dated session logs are not edited; they describe what was true when written |

## Requirements

### R1 — No governed document lives under root `plans/`

`docs/01-plans/PLAN-001-agent-memory-system.md` is the sole location for `doc-agent-memory`, carrying
the same `id` and `code` it had at its old path.

*Verification:* `uv run python -m src.governance` resolves `doc-agent-memory` at the new path;
`git status` shows no file remaining under `plans/`.

### R2 — The bootstrap prompt is preserved, unchanged, at its new path

`docs/02-prompts/codex_governance_prompt.md` has identical content to the old
`plans/codex_governance_prompt.md`, still carries no front matter, and is still exempt from
metadata scanning.

*Verification:* `diff` between the pre-move and post-move content is empty (the `git mv` is a pure
rename); `uv run python -m src.governance` raises no "missing front matter" error for this file.

### R3 — The `PLAN` series advertises exactly one location

`docs/08-governance/codes.yaml`'s `PLAN` series lists only `docs/01-plans/`.

*Verification:* reading `codes.yaml` shows a single-entry `locations` list for `PLAN`; a document
placed under a hypothetical new `plans/` file would fail `location_error` in `src/governance/codes.py`.

### R4 — The existence-checked system path resolves

`sys-memory-agents`' `paths` entry in `docs/08-governance/systems.yaml` points at the file's new
location.

*Verification:* `uv run python -m src.governance` exits 0 — this system's paths are checked
unconditionally, so a stale entry here is a hard failure, not a warning.

### R5 — Every non-historical inbound reference resolves to the new paths

`README.md`, `docs/09-backlog/README.md`, `docs/09-backlog/backlog.yaml`, `docs/07-architecture/ARCH-002-system-audit.md`,
`docs/06-requirements/REQ-001-document-code-requirements.md`, `docs/02-prompts/PROMPT-004-terminology-and-architecture.md`,
`_tmpagent/AGENTS.md`, and `brain/concepts/terms-documents-and-governance.md` no longer point at or
describe `plans/` as a live location. `docs/01-plans/PLAN-005-document-code-system.md`'s historical
rename table and dated session logs are left as-is.

*Verification:* `grep -rn '\bplans/'` across the repository, excluding `docs/01-plans/` and the two
named historical documents, returns zero hits.

### R6 — The full check suite is green with no test-code edits

`uv run python -m src.governance` exits 0, `docs/08-governance/catalog.md` is regenerated and
committed, and `uv run pytest` passes without modifying any file under `test/`.

*Verification:* run all three commands; `test_current_repository_validates` and
`test_committed_catalog_matches_regenerated_output` pass unmodified.

## Out of scope

This does not change `PLAN-001`'s content, status, or `id`/`code`; does not promote
`codex_governance_prompt.md` to a governed document; and does not touch any other document's
substantive content beyond the path references named above.
