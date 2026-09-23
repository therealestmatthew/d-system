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

`status: complete`, `agent: agent-builder-b`, `session: doc-session-governance-protocol-templates`.
`completion_evidence` lists the four template and schema files, the five fixtures, `check_schemas.py`
and this record. The phase was not in `next_up`. It was completed after the owner-approved
fast-forward merge onto dev at `cf56de8`.

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

## Review

Independent adversarial review (a fresh `demo-adversary` subagent) of `dev...agent/phase-fwt-01`
at commits `05a084f` and `d11c4aa`. The reviewer ran both verification commands itself. Its
findings, condition by condition:

- **REQ-024 R01 — Holds.** `governance.no-incident.md` differs from `governance.valid.md` only by
  the removed `## Incident and rationale` section. A heading changed only in case
  (`## Incident and Rationale`) also fails, so the negative check catches that typo too.
- **REQ-024 R02 — Holds.** Each relabelled fixture differs from its original only in the `kind:`
  line, yet it still fails on missing sections, so the rejection comes from structure, not the
  label.
- **Converter edge cases:** headings in code fences and HTML comments are ignored; `###` headings
  are excluded; missing or empty front matter fails validation; trailing whitespace is stripped;
  CRLF files parse correctly when read the way the script reads them.
- **Scope:** the diff touches only the declared deliverables, the session record, the catalog and
  phase-fwt-01's own backlog entry.
- **Findings:** none blocking or major. One observation, not a finding: as the owner decided,
  `## Steps` is enforced as a required heading only, so an empty or prose Steps section still
  validates. "No discrepancies found" between the record and the diff or runs.

## Decisions

- **The schemas validate front matter and level-2 headings.** JSON Schema cannot read Markdown
  directly, and the phase did not say what the schemas should validate. The owner chose to convert
  each document to `{front_matter, sections}` over two alternatives: front matter only, or headings
  plus section bodies.
- **The fixtures and the check script are committed deliverables.** The phase listed only the four
  template and schema files. The owner approved adding `05-schemas/examples/` and
  `05-schemas/check_schemas.py` to the deliverables in the claim commit. A test under `test/` was
  not used because `test/` was claimed by phase-conc-02 and lies outside `sys-fw-templates`.
- **Governance documents have no required Status section.** Idea `000269` mentions status, but
  REQ-024 R01 requires only the rule, the problem and the incident or rationale. The front-matter
  `status` field already records the state, so a Status section would duplicate it.
- **Both templates use the code placeholder `GOV-NNN`.** In d-system, protocols carry GOV codes too
  (GOV-001 is the documentation protocol). The schemas accept any `PREFIX-NNN`, so this phase does
  not fix a code prefix for the portable framework.
- **The check script also confirms that each template's headings satisfy its schema.** This keeps a
  template and its schema from drifting apart.

## Corrections

- The first protocol template draft used a `PROT-NNN` code prefix, and the first governance
  template draft required a fourth section, Status. Both were conventions the owner had not asked
  for, and both were removed before the first commit.
- An early pytest run in the primary checkout overlapped with another session's run. The Session
  Manager reported that `test/test_codes.py` temporarily rewrites the tracked catalog. The run had
  already finished and the catalog was intact. Every later check ran in the worktree.

## Left undone

- The framework `README.md` and `INDEX.md` still describe these schemas as "to create". They are
  not deliverables of this phase.
- phase-fwt-02 to phase-fwt-04 can add their cases to `check_schemas.py`'s `CASES` and `TEMPLATES`
  lists instead of writing new scripts.
