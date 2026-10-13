---
schema_version: 1
id: doc-session-requirement-plan-schemas
code: SESS-2026-10-12-01
title: Requirement and plan document schemas
kind: session
status: active
owner: repository-owner
created: '2026-10-12'
updated: '2026-10-12'
systems: [sys-fw-templates]
depends_on: [doc-portable-framework-document-templates]
---

# Requirement and plan document schemas

## Phase

`phase-fwt-03` — Requirement and plan document schemas. Batch-016 stage 2, assigned by the Session
Manager on 2026-10-12 with the owner's approval and claimed in claim commit `fb1a87fc` on dev. The
claim added `05-schemas/examples` and `05-schemas/check_schemas.py` to the phase's deliverables
(owner ruling).

## Verification

`uv run python -m src.governance`

```text
Governance OK: 45 systems, 481 documents, 38 memories, 357 backlog phases
```

A short jsonschema script validating a passing and a deliberately incomplete instance of each
template: the cases were added to `docs/00-working/framework/05-schemas/check_schemas.py`.

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
PASS  requirement.valid.md against requirement.schema.json: valid (expected valid)
PASS  requirement.no-acceptance.md against requirement.schema.json: invalid (expected invalid)
        missing section: 'Acceptance criteria'
PASS  plan.valid.md against plan.schema.json: valid (expected valid)
PASS  plan.no-scope.md against plan.schema.json: invalid (expected invalid)
        missing section: 'Scope'
PASS  plan.no-phases.md against plan.schema.json: invalid (expected invalid)
        missing section: 'Phases'
PASS  governance.template.md headings against governance.schema.json sections
PASS  protocol.template.md headings against protocol.schema.json sections
PASS  requirement.template.md headings against requirement.schema.json sections
PASS  plan.template.md headings against plan.schema.json sections
PASS  requirement.valid.md has no template placeholders
PASS  plan.valid.md has no template placeholders
PASS  phase-conc-01 cut from backlog.yaml as text equals the parsed backlog item
PASS  phase-conc-01 against phase.schema.json: valid (expected valid)
PASS  phase-conc-01 without acceptance (a required field) against phase.schema.json: invalid (expected invalid)
        'acceptance' is a required property
PASS  phase-conc-01 without result (required once status is complete) against phase.schema.json: invalid (expected invalid)
        'result' is a required property
PASS  phase-conc-01 as active with no agent against phase.schema.json: valid (expected valid)
PASS  all 357 phases in backlog.yaml against phase.schema.json: 357 valid (expected all)
PASS  phase.template.md YAML keys against phase.schema.json properties

0 failure(s)
```

The two filled examples are `examples/requirement.valid.md` and `examples/plan.valid.md`. The
incomplete ones are the same files with one section cut: `requirement.no-acceptance.md`,
`plan.no-scope.md` and `plan.no-phases.md`. The placeholder check confirms the filled examples
carry none of the forms the templates use (`REQ-NNN`, `YYYY-MM-DD`, a bracketed name in the title,
an angle-bracket slot, an HTML comment, an `Example:` lead-in). Run against the two templates
instead, the same pattern finds every one of those forms, so the check is not passing by matching
nothing.

## Acceptance

- REQ-024 R04 for `requirement.schema.json` — **Met.** `requirement.valid.md`, a filled,
  placeholder-free instance of `requirement.template.md`, validates; `requirement.no-acceptance.md`
  fails with `missing section: 'Acceptance criteria'`.
- REQ-024 R04 for `plan.schema.json` — **Met.** `plan.valid.md` validates; `plan.no-scope.md`
  fails with `missing section: 'Scope'` and `plan.no-phases.md` with `missing section: 'Phases'`.

## Decisions

- **Required sections** (owner ruling relayed in the Session Manager's ASSIGN): a requirement
  requires Overview, Requirements, Scope and Acceptance criteria; a plan requires Overview, Scope
  and Phases. Other level-2 sections are allowed and unchecked, as in the governance and protocol
  schemas.
- **Both drafts were rewritten in the family style** (owner ruling). Where the drafts' shape had to
  change, as the phase's `next_action` asks this record to note:
  - The requirement draft had no section named Requirements, Scope or Acceptance criteria as
    such. Its "Functional Requirements" and "Non-Functional Requirements" become one Requirements
    section of numbered R01, R02, ... entries, each with its own verification line, following
    REQ-024's own form; its separate "Verification Method" section is folded into those lines.
    "Scope / Boundaries" becomes Scope; "Acceptance Criteria" becomes Acceptance criteria.
  - The plan draft had no Scope section and called its phases "Phase Breakdown". Scope is new;
    Phases replaces Phase Breakdown with one entry per phase (id, outcome, dependency, files)
    instead of a full sub-document per phase, since the backlog item carries acceptance and
    verification.
  - Removed from the requirement draft: User/System Needs (folded into Overview), Dependencies,
    Risks & Mitigations, Related Documents, Review Notes and "How to Use This Template". Removed from
    the plan draft: Architecture, Interdependencies, Tech Decisions & Rationale, Risks & Mitigations,
    Success Criteria, External Dependencies, Open Questions, Approval and "How to Use This
    Template". Each template's comment names some of these as optional sections a document may
    still add. The route-optimiser example content is cut to one short example per section, as in
    the governance and protocol templates.
  - Front matter now uses the family's key order (`code`, `title`, `kind`, `status`, `created`);
    the plan keeps `depends_on`, which its schema checks as a list of document codes when present.
- **Status values** are `draft`, `approved`, `active`, `complete`, `deprecated`, `superseded`: the
  governance and protocol schemas' four plus `approved` and `complete`, which d-system's own
  requirements and plans use. This was not asked about; it is stated here for the review.
- **The filled examples restate REQ-024 and PLAN-040 in short form**, as the governance example
  restates GOV-001, so the examples describe real documents rather than invented ones.

## Unresolved

- `tools/check_no_private_content.py` checked 0 identifiers in the worktree, because
  `_private/portfolio/` exists only in the primary checkout. Its `check_content` function, run on the
  ten changed files with the 31 identifiers loaded from the primary checkout, reported no
  violations.
- The framework `INDEX.md` still lists `requirement.schema.json` and `plan.schema.json` as "to
  create". It is not a deliverable of this phase.
