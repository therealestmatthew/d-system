---
schema_version: 1
id: doc-portable-framework-document-templates-requirements
code: REQ-024
title: Portable framework document template and schema requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-19'
updated: '2026-09-19'
systems: [sys-fw-templates]
depends_on: [doc-governance-protocol, doc-document-code-protocol, doc-idea-staging]
---

# Portable framework document template and schema requirements

## Observed problem and scope

Thirteen ideas captured on 2026-09-19 (`000269`-`000281`) describe a portable, generalized
multi-developer agentic workflow framework meant to let a new repository adopt d-system's
governance model — plan before phase before claim, worktree isolation, code allocation — without
re-deriving it from scratch. `000281` is the batch anchor: a starter kit that a new repository can
copy and customize in one pass.

Before there is a kit there has to be a stable set of document shapes for it to carry. `000269`,
`000270`, `000271`, `000277`, `000278` and `000279` each name one shape that is either missing or
present only as an unvalidated draft under `docs/00-working/framework/05-schemas/`:

- Governance-rule documents (what problem a standing rule solves, the rule, the incident that
  motivated it, current status) — `000269`.
- Protocol documents (a trigger, an ordered procedure, exit criteria, failure handling) — distinct
  from a governance document because a protocol states *what to do*, not *why a rule exists* —
  `000270`.
- A standalone backlog phase shape, today only implicit in `backlog.yaml` entries and never stated
  on its own — `000271`.
- Session records — `000277`.
- Requirements and plans — drafted as Markdown templates already, with no schema to check a document
  against them — `000278`.
- GitHub issue and pull request templates, with more than one issue type — `000279`.

The drafts at `docs/00-working/framework/05-schemas/` are the raw material for this work, not its
authority. They were written before these ideas existed, are ungoverned per
[ADR-010](../04-decisions/ADR-010-idea-staging.md), and this requirement is free to contradict them
where they do not hold up.

`000272` asks a design question this requirement must also answer: whether a "workstream" — a layer
above plans and phases, one per developer or machine, holding several plans and cross-referencing
many requirements — earns a place in this template family. **R06** below states the answer and its
test.

## Requirements

**R01 — Governance-rule template and schema are distinguishable from protocol by structure, not
just by name.**
A governance-rule template (`docs/00-working/framework/05-schemas/governance.template.md`) and its
schema (`governance.schema.json`) require a stated rule, the problem it solves, and an
incident/rationale section. A filled-in example that states a rule but omits the incident/rationale
section fails schema validation.
*Verification:* `uv run python -c "..."` loading `governance.schema.json` with `jsonschema`, validated
against (a) a filled example that passes and (b) the same example with the incident section removed,
which must fail.

**R02 — Protocol template and schema require procedure, not rationale.**
A protocol template (`protocol.template.md`) and schema (`protocol.schema.json`) require a trigger
condition, an ordered step list, verification/exit criteria and failure handling. A document that
states only a rule and its justification (the shape R01 validates) fails the protocol schema, and a
document that states only ordered steps fails the governance schema — the two schemas reject each
other's shape.
*Verification:* same jsonschema check, cross-validating one governance-shaped example against
`protocol.schema.json` and one protocol-shaped example against `governance.schema.json`; both must
fail.

**R03 — The phase schema matches a phase already in use, not an invented shape.**
`phase.schema.json` validates an existing, unmodified `backlog.yaml` phase item (e.g. `phase-conc-01`)
extracted as its own YAML document, without editing `backlog.yaml` to fit the schema.
*Verification:* a short script extracts one real phase item and validates it against
`phase.schema.json`; it passes without modification to the source phase.

**R04 — Requirement and plan schemas validate their own templates.**
`requirement.schema.json` and `plan.schema.json` each validate a filled, placeholder-free instance of
their respective templates (`requirement.template.md`, `plan.template.md`), and each rejects an
instance missing a required section (acceptance criteria for a requirement; scope and phases for a
plan).
*Verification:* jsonschema validation of a passing and a deliberately incomplete instance of each.

**R05 — At least two GitHub issue types are distinguishable without reading the body, and the PR
template carries completion evidence.**
Beyond the existing idea-capture issue template, at least one more issue type (a defect report) has
its own template with front matter or labels that differ from the idea-capture template. The PR
template requires fields for acceptance criteria, verification output, scope confirmation and a
session-record link.
*Verification:* diff the two issue templates' front matter/label blocks and confirm they differ; grep
the PR template for the four required fields.

**R06 — The workstream question is answered and the answer is testable.**
The plan states explicitly whether a workstream document kind is adopted. If adopted, the plan states
which field on a workstream document constrains or relates to the `systems`/`deliverables`
declarations that `ADR-003`'s concurrency check actually locks on, and that relationship is stated
precisely enough that a reader could implement the constraint. If not adopted, the plan names the
existing structure (or structures) that already cover the need `000272` describes, and why a new
document kind is not required to get that coverage.
*Verification:* read the plan body; the design section either names the constraining field or names
the substitute structure. No code verification applies — this is a design-record requirement.

## Out of scope

- Writing `01-overview/`, `02-workflows/`, `03-governance/` or `04-templates/` content described in
  the `docs/00-working/framework/README.md` draft. Those are unstarted and not the subject of any of
  the thirteen ideas; inventing them now would repeat the 2026-09-06 incident `ADR-010` records.
- Packaging the finished template family into the starter kit `000281` describes. That depends on
  this requirement's deliverables existing first and is not itself ready to plan.
- Any change to `src/governance/`, `schemas/document.schema.json` or `docs/09-backlog/backlog.yaml`'s
  validator behavior. The templates and schemas produced here describe documents for a *future*
  repository's own governance engine; they do not extend d-system's.
