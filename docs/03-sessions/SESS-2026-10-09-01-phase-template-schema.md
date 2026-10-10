---
schema_version: 1
id: doc-session-phase-template-schema
code: SESS-2026-10-09-01
title: Standalone backlog phase template and schema
kind: session
status: active
owner: repository-owner
created: '2026-10-09'
updated: '2026-10-09'
systems: [sys-fw-templates]
depends_on: [doc-portable-framework-document-templates]
---

# Standalone backlog phase template and schema

## Phase

`phase-fwt-02` — Standalone backlog phase template and schema. First phase of batch-016, assigned by
the Session Manager on 2026-10-09 and claimed with the owner's approval in this session (claim
commit `0143ce11` on dev).

## Verification

`uv run python -m src.governance`

```text
Governance OK: 45 systems, 477 documents, 37 memories, 357 backlog phases
```

A short script extracting one real phase item and validating it against `phase.schema.json`: the
phase cases were added to `docs/00-working/framework/05-schemas/check_schemas.py`.

`uv run python docs/00-working/framework/05-schemas/check_schemas.py` (exit 0)

```text
PASS  governance.valid.md against governance.schema.json: valid (expected valid)
PASS  governance.no-incident.md against governance.schema.json: invalid (expected invalid)
        missing section: 'Incident and rationale'
PASS  protocol.valid.md against protocol.schema.json: valid (expected valid)
PASS  governance.valid.md against protocol.schema.json: invalid (expected invalid)
        'protocol' was expected
        missing section: 'Trigger'
        missing section: 'Steps'
        missing section: 'Exit criteria'
        missing section: 'Failure handling'
PASS  protocol.valid.md against governance.schema.json: invalid (expected invalid)
        'governance' was expected
        missing section: 'Rule'
        missing section: 'Problem'
        missing section: 'Incident and rationale'
PASS  governance-shape-labelled-protocol.md against protocol.schema.json: invalid (expected invalid)
        missing section: 'Trigger'
        missing section: 'Steps'
        missing section: 'Exit criteria'
        missing section: 'Failure handling'
PASS  protocol-shape-labelled-governance.md against governance.schema.json: invalid (expected invalid)
        missing section: 'Rule'
        missing section: 'Problem'
        missing section: 'Incident and rationale'
PASS  governance.template.md headings against governance.schema.json sections
PASS  protocol.template.md headings against protocol.schema.json sections
PASS  phase-conc-01 cut from backlog.yaml as text equals the parsed backlog item
PASS  phase-conc-01 against phase.schema.json: valid (expected valid)
PASS  phase-conc-01 without acceptance (a required field) against phase.schema.json: invalid (expected invalid)
        'acceptance' is a required property
PASS  phase-conc-01 without result (required once status is complete) against phase.schema.json: invalid (expected invalid)
        'result' is a required property
PASS  all 357 phases in backlog.yaml against phase.schema.json: 357 valid (expected all)
PASS  phase.template.md YAML keys against phase.schema.json properties

0 failure(s)
```

The script cuts `phase-conc-01` out of `backlog.yaml` as text — from its `- id:` line to the next
item — removes only the list marker and the two-space list indent, and parses the result as its own
YAML document. The first phase line confirms that this text-extracted item equals the item as
parsed from the whole file, so nothing was lost or altered in the cut.

## Acceptance

- REQ-024 R03 — **Met.** `phase-conc-01`, extracted as its own YAML document, validates against
  `phase.schema.json`. Copies with `acceptance` removed, or with `result` removed (required once
  `status` is `complete`), fail. All 357 phases in today's `backlog.yaml` also validate.
- No edit to `backlog.yaml` — **Met.** `git diff --exit-code 0143ce11 -- docs/09-backlog/backlog.yaml`
  is empty on the branch: the only `backlog.yaml` change in this phase is the claim commit's own
  lines (status, agent, the added deliverable), made before the schema existed.

## Decisions

- **The schema is a portable core** (owner, this session, chosen over mirroring d-system's item
  definition exactly or a closed minimal core). Ten fields are required: `id`, `title`, `plan`,
  `status`, `systems`, `depends_on`, `scope`, `acceptance`, `verification`, `deliverables`.
  d-system's other fields are listed as optional properties so their shape is checked when present.
  Identifiers are generic lowercase hyphenated slugs, not d-system's `phase-xxx-NN` and `doc-...`
  patterns. Fields the schema does not list are allowed, so an adopting repository can add its own.
- **Status-conditional rules follow d-system's validator** (`src/governance/backlog.py`):
  `blocked`, `deferred` and `cancelled` need `blocked_reason`; `blocked` and `deferred` need
  `resume_when`; `complete` needs `session`, `completion_evidence` and `result`; `queued`, `deferred`
  and `cancelled` may not carry `agent`, `completion_evidence` or `result`.
- **`active` requires `agent` unconditionally.** d-system requires an agent only when `max_active`
  is above 1, which a single phase cannot see. Every active phase on dev carries one, and the agent
  is the claim, so the schema requires it.
- **The check covers every phase, not only `phase-conc-01`** (owner, this session). The whole
  backlog is read in memory; `backlog.yaml` is never written.
- **`check_schemas.py` was added to the phase's deliverables** in the claim commit (owner, this
  session), so phase-fwt-03 to phase-fwt-05 keep one check script, as phase-fwt-01 left it.
- **The template is a Markdown page around one fenced YAML item**, because a phase is a backlog
  item, not a document. The check confirms the block's keys are schema properties and include every
  required field; the placeholder values are not validated.

## Unresolved

- `tools/check_no_private_content.py` checked 0 identifiers in the worktree, because
  `_private/portfolio/` exists only in the primary checkout. Its `check_content` function, run on the
  three changed files with the 31 identifiers loaded from the primary checkout, reported no
  violations.
- `mypy` on `check_schemas.py` reports two missing-stub errors (`yaml`, `jsonschema`), the same two
  as before this phase. The repository gate runs mypy on `src/` only. `ruff check` on the file passes.
- The framework `INDEX.md` still lists `phase.schema.json` as "to create". It is not a deliverable of
  this phase.

## Review

Pending: requested from the Session Manager per the coordination contract.
