---
schema_version: 1
id: doc-session-governance-protocol-templates
code: SESS-2026-09-22-07
title: Governance and protocol document templates and schemas
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-fw-templates]
depends_on: [doc-portable-framework-document-templates]
---

# Governance and protocol document templates and schemas

## Phase

`phase-fwt-01` — Governance and protocol document templates and schemas.

## Verification

`uv run python -m src.governance`

```text
Governance OK: 35 systems, 315 documents, 30 memories, 293 backlog phases
```

A short jsonschema script validating the passing and failing examples named in the acceptance
conditions: the script is `docs/00-working/framework/05-schemas/check_schemas.py`, and its fixtures
are in `05-schemas/examples/`.

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

0 failure(s)
```

## Acceptance

- REQ-024 R01 — **Met.** `governance.valid.md` validates against `governance.schema.json`;
  `governance.no-incident.md` (the same document with its `## Incident and rationale` section
  removed) fails with `missing section: 'Incident and rationale'`.
- REQ-024 R02 — **Met.** `protocol.valid.md` validates against `protocol.schema.json`. The
  governance-shaped example fails the protocol schema and the protocol-shaped example fails the
  governance schema. The relabelled fixtures show that the rejection comes from the sections, not
  only from `kind`: a governance body labelled `kind: protocol` still fails the protocol schema on
  four missing sections, and the reverse fails on three.

## Backlog

`status: active`, `agent: agent-builder-b`. `next_action`: All acceptance conditions are met on
agent/phase-fwt-01; waiting for the owner-approved merge onto dev, after which session-close
completes the phase.

## Unresolved

- The protocol schema checks that a `## Steps` section exists, not that its body is a numbered
  list. That limit follows from the owner's choice that the schemas validate front matter and
  headings only. The template and the schema's `description` both say so.
- `tools/check_no_private_content.py` checked 0 identifiers in the worktree, because
  `_private/portfolio/` exists only in the primary checkout. The same tool checked 31 identifiers
  there when the claim commit was pushed. All content added in this session is invented example
  text.
- The framework `README.md` and `INDEX.md` still list the schemas as "to create". Neither file is
  a deliverable of this phase, so this session did not change them.
