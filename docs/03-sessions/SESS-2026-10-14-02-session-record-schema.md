---
schema_version: 1
id: doc-session-session-record-schema
code: SESS-2026-10-14-02
title: Session-record document schema
kind: session
status: active
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: [sys-fw-templates]
depends_on: [doc-portable-framework-document-templates]
---

# Session-record document schema

## Phase

`phase-fwt-04` — Session-record document schema. Batch-016 stage 3, assigned by the Session Manager
on 2026-10-14 with the owner's approval and claimed in claim commit `665050cc` on dev. The claim
added `05-schemas/examples` and `05-schemas/check_schemas.py` to the phase's deliverables (owner,
this session).

## Verification

`uv run python -m src.governance`

```text
Governance OK: 46 systems, 484 documents, 38 memories, 364 backlog phases
```

A short jsonschema script validating a passing and a deliberately incomplete instance: the cases
were added to `docs/00-working/framework/05-schemas/check_schemas.py`.

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
PASS  session.valid.md against session-record.schema.json: valid (expected valid)
PASS  governance.template.md headings against governance.schema.json sections
PASS  protocol.template.md headings against protocol.schema.json sections
PASS  requirement.template.md headings against requirement.schema.json sections
PASS  plan.template.md headings against plan.schema.json sections
PASS  session-record.template.md headings against session-record.schema.json sections
PASS  requirement.valid.md has no template placeholders
PASS  plan.valid.md has no template placeholders
PASS  session.valid.md has no template placeholders
PASS  governance.valid.md as a governance document (--document): passes (expected pass)
PASS  protocol.valid.md as a protocol document (--document): passes (expected pass)
PASS  requirement.valid.md as a requirement document (--document): passes (expected pass)
PASS  plan.valid.md as a plan document (--document): passes (expected pass)
PASS  requirement.boilerplate.md as a requirement document (--document): fails (expected fail)
        placeholder: '<!--'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        front-matter title is the template's sample: 'short name of the feature or subsystem'
        section 'Overview' keeps the template's sample text: 'route planners need a multi stop route ordered to minimise d'
        section 'Overview' keeps the template's sample text: 'today they order stops by hand which takes several minutes p'
        section 'Requirements' keeps the template's sample text: 'r01 an optimised route visits every stop given a start an en'
        section 'Requirements' keeps the template's sample text: 'verification uv run pytest test test route optimizer py k vi'
        section 'Requirements' keeps the template's sample text: 'r02 the response arrives within two seconds'
        section 'Requirements' keeps the template's sample text: 'verification a load test of ten concurrent requests reports '
        section 'Scope' keeps the template's sample text: 'the ordering algorithm and the http endpoint that returns th'
        section 'Scope' keeps the template's sample text: 'a user interface for viewing routes and storing routes betwe'
        section 'Acceptance criteria' keeps the template's sample text: 'r01 and r02 each pass their stated verification'
        section 'Acceptance criteria' keeps the template's sample text: 'an invalid coordinate returns an error that names the offend'
PASS  plan.boilerplate.md as a plan document (--document): fails (expected fail)
        placeholder: '<!--'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        front-matter title is the template's sample: 'short name of what will be built'
        section 'Overview' keeps the template's sample text: 'build the route optimiser as a nearest neighbour ordering be'
        section 'Overview' keeps the template's sample text: 'nearest neighbour is fast enough for ten stops and simple en'
        section 'Overview' keeps the template's sample text: 'an exact solver is deferred unless the latency target is mis'
        section 'Scope' keeps the template's sample text: 'the ordering module the endpoint and their tests'
        section 'Scope' keeps the template's sample text: 'caching distances between requests and any user interface'
        section 'Phases' keeps the template's sample text: 'phase route 01 ordering module'
        section 'Phases' keeps the template's sample text: 'orders stops by nearest neighbour and returns the total dist'
        section 'Phases' keeps the template's sample text: 'src route order py test test route optimizer py'
        section 'Phases' keeps the template's sample text: 'exposes the ordering over http and returns an error that nam'
        section 'Phases' keeps the template's sample text: 'src api routes route py test test route api py'
PASS  requirement.stripped-sample.md as a requirement document (--document): fails (expected fail)
        front-matter title is the template's sample: 'short name of the feature or subsystem'
        section 'Overview' keeps the template's sample text: 'route planners need a multi stop route ordered to minimise d'
        section 'Overview' keeps the template's sample text: 'today they order stops by hand which takes several minutes p'
        section 'Requirements' keeps the template's sample text: 'r01 an optimised route visits every stop given a start an en'
        section 'Requirements' keeps the template's sample text: 'verification uv run pytest test test route optimizer py k vi'
        section 'Requirements' keeps the template's sample text: 'r02 the response arrives within two seconds'
        section 'Requirements' keeps the template's sample text: 'verification a load test of ten concurrent requests reports '
        section 'Scope' keeps the template's sample text: 'the ordering algorithm and the http endpoint that returns th'
        section 'Scope' keeps the template's sample text: 'a user interface for viewing routes and storing routes betwe'
        section 'Acceptance criteria' keeps the template's sample text: 'r01 and r02 each pass their stated verification'
        section 'Acceptance criteria' keeps the template's sample text: 'an invalid coordinate returns an error that names the offend'
PASS  plan.stripped-sample.md as a plan document (--document): fails (expected fail)
        front-matter title is the template's sample: 'short name of what will be built'
        section 'Overview' keeps the template's sample text: 'build the route optimiser as a nearest neighbour ordering be'
        section 'Overview' keeps the template's sample text: 'nearest neighbour is fast enough for ten stops and simple en'
        section 'Overview' keeps the template's sample text: 'an exact solver is deferred unless the latency target is mis'
        section 'Scope' keeps the template's sample text: 'the ordering module the endpoint and their tests'
        section 'Scope' keeps the template's sample text: 'caching distances between requests and any user interface'
        section 'Phases' keeps the template's sample text: 'phase route 01 ordering module'
        section 'Phases' keeps the template's sample text: 'orders stops by nearest neighbour and returns the total dist'
        section 'Phases' keeps the template's sample text: 'src route order py test test route optimizer py'
        section 'Phases' keeps the template's sample text: 'exposes the ordering over http and returns an error that nam'
        section 'Phases' keeps the template's sample text: 'src api routes route py test test route api py'
PASS  req-case-only.md as a requirement document (--document): fails (expected fail)
        front-matter title is the template's sample: 'short name of the feature or subsystem'
        section 'Overview' keeps the template's sample text: 'route planners need a multi stop route ordered to minimise d'
        section 'Overview' keeps the template's sample text: 'today they order stops by hand which takes several minutes p'
        section 'Requirements' keeps the template's sample text: 'r01 an optimised route visits every stop given a start an en'
        section 'Requirements' keeps the template's sample text: 'verification uv run pytest test test route optimizer py k vi'
        section 'Requirements' keeps the template's sample text: 'r02 the response arrives within two seconds'
        section 'Requirements' keeps the template's sample text: 'verification a load test of ten concurrent requests reports '
        section 'Scope' keeps the template's sample text: 'the ordering algorithm and the http endpoint that returns th'
        section 'Scope' keeps the template's sample text: 'a user interface for viewing routes and storing routes betwe'
        section 'Acceptance criteria' keeps the template's sample text: 'r01 and r02 each pass their stated verification'
        section 'Acceptance criteria' keeps the template's sample text: 'an invalid coordinate returns an error that names the offend'
PASS  requirement.bom.md as a requirement document (--document): passes (expected pass)
PASS  session.valid.md as a session document (--document): passes (expected pass)
PASS  session.boilerplate.md as a session document (--document): fails (expected fail)
        placeholder: '<!--'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        placeholder: '<!--'
        placeholder: 'Example:'
        front-matter title is the template's sample: 'short name of the session s work'
        section 'Summary' keeps the template's sample text: 'built the route ordering module for phase route 01'
        section 'Summary' keeps the template's sample text: 'stops are ordered by nearest neighbour and the module return'
        section 'Acceptance' keeps the template's sample text: 'req 012 r01 every stop visited exactly once met the visits e'
        section 'Decisions' keeps the template's sample text: 'nearest neighbour not an exact solver owner this session'
        section 'Decisions' keeps the template's sample text: 'ten stops is small enough that the simpler ordering meets th'
        section 'New requirements' keeps the template's sample text: 'routes need a maximum stop count so an oversized request is '
        section 'Deferred and out of scope' keeps the template's sample text: 'caching distances between requests was left out of scope by '
        section 'Open investigations' keeps the template's sample text: 'whether stops closer than ten metres should be merged before'
        section 'Outstanding actions' keeps the template's sample text: 'the owner provisions the routing service s credentials befor'
        section 'Verification' keeps the template's sample text: 'text uv run pytest test test route optimizer py 6 passed in '
PASS  session.stripped-sample.md as a session document (--document): fails (expected fail)
        front-matter title is the template's sample: 'short name of the session s work'
        section 'Summary' keeps the template's sample text: 'built the route ordering module for phase route 01'
        section 'Summary' keeps the template's sample text: 'stops are ordered by nearest neighbour and the module return'
        section 'Acceptance' keeps the template's sample text: 'req 012 r01 every stop visited exactly once met the visits e'
        section 'Decisions' keeps the template's sample text: 'nearest neighbour not an exact solver owner this session'
        section 'Decisions' keeps the template's sample text: 'ten stops is small enough that the simpler ordering meets th'
        section 'New requirements' keeps the template's sample text: 'routes need a maximum stop count so an oversized request is '
        section 'Deferred and out of scope' keeps the template's sample text: 'caching distances between requests was left out of scope by '
        section 'Open investigations' keeps the template's sample text: 'whether stops closer than ten metres should be merged before'
        section 'Outstanding actions' keeps the template's sample text: 'the owner provisions the routing service s credentials befor'
        section 'Verification' keeps the template's sample text: 'text uv run pytest test test route optimizer py 6 passed in '
PASS  session.valid.md without 'Summary' against session-record.schema.json: invalid (expected invalid)
        missing section: 'Summary'
PASS  session.valid.md without 'Acceptance' against session-record.schema.json: invalid (expected invalid)
        missing section: 'Acceptance'
PASS  session.valid.md without 'Decisions' against session-record.schema.json: invalid (expected invalid)
        missing section: 'Decisions'
PASS  session.valid.md without 'New requirements' against session-record.schema.json: invalid (expected invalid)
        missing section: 'New requirements'
PASS  session.valid.md without 'Deferred and out of scope' against session-record.schema.json: invalid (expected invalid)
        missing section: 'Deferred and out of scope'
PASS  session.valid.md without 'Open investigations' against session-record.schema.json: invalid (expected invalid)
        missing section: 'Open investigations'
PASS  session.valid.md without 'Outstanding actions' against session-record.schema.json: invalid (expected invalid)
        missing section: 'Outstanding actions'
PASS  session.valid.md without 'Verification' against session-record.schema.json: invalid (expected invalid)
        missing section: 'Verification'
PASS  session.valid.md without 'Completion evidence' against session-record.schema.json: invalid (expected invalid)
        missing section: 'Completion evidence'
PASS  phase-conc-01 cut from backlog.yaml as text equals the parsed backlog item
PASS  phase-conc-01 against phase.schema.json: valid (expected valid)
PASS  phase-conc-01 without acceptance (a required field) against phase.schema.json: invalid (expected invalid)
        'acceptance' is a required property
PASS  phase-conc-01 without result (required once status is complete) against phase.schema.json: invalid (expected invalid)
        'result' is a required property
PASS  phase-conc-01 as active with no agent against phase.schema.json: valid (expected valid)
PASS  all 364 phases in backlog.yaml against phase.schema.json: 364 valid (expected all)
PASS  phase.template.md YAML keys against phase.schema.json properties

0 failure(s)
```

The nine "without" cases remove one required section at a time from `examples/session.valid.md`,
heading and body, and each copy fails naming that section. The list of sections is read from
`session-record.schema.json`, so a section added to the schema is covered without editing the
script.

`--document <path> --kind session`, run directly:

```text
session.valid.md --kind session: exit=0
session.boilerplate.md --kind session: exit=1
session.stripped-sample.md --kind session: exit=1
requirement.valid.md --kind session: exit=1
```

## Acceptance

- A filled, placeholder-free instance validates; an instance missing any field listed in scope
  fails — **Met.** `session.valid.md` validates and has no template placeholders. Removing any one
  of the seven scope fields (Decisions, New requirements, Deferred and out of scope, Open
  investigations, Outstanding actions, Verification, Completion evidence) fails, and so does
  removing Summary or Acceptance.
- The required-field list is legible without cross-referencing PLAN-041 — **Met.** Each required
  section in `session-record.schema.json` carries a `description` saying what it must contain, and
  the schema's top-level description says what a session record is and that an empty section stays
  and says None. Nothing in the schema names PLAN-041.

## Decisions

- **The field list comes from REQ-025 R02 and the phase scope** (this session, following the
  phase's `next_action`). The three analysis phases of PLAN-041 (`phase-fwa-01` to `-03`) are still
  queued, so no extraction output exists to derive fields from. REQ-025 R02 states what the
  session-extraction pass must find for every record: decisions, new requirements,
  deferred/out-of-scope items, open investigation items and outstanding action items, each allowed
  to be empty. The phase scope adds verification output and completion evidence.
- **Nine required sections** (owner, this session): Summary, Acceptance, Decisions, New
  requirements, Deferred and out of scope, Open investigations, Outstanding actions, Verification,
  Completion evidence. Summary and Acceptance are required beyond the seven scope fields because a
  record without them cannot show what the session was for or whether the phase finished.
- **An empty section stays and says None** (this session), so a reader can tell "nothing found"
  from "not recorded", as REQ-025 R02 allows a category to be empty but requires its heading.
- **The draft was rewritten in the family style** (owner, this session). Where its shape changed:
  - Kept and renamed: "Summary" stays; "Acceptance Verification" becomes Acceptance; "Verification
    Results" becomes Verification; "Completion Evidence" becomes Completion evidence; "Key
    Decisions Made" (under Work Summary) becomes Decisions; "New Requirements Discovered" becomes
    New requirements; "Out-of-Scope / Deferred Items" becomes Deferred and out of scope;
    "Blockers / Unresolved Issues" is split between Open investigations and Outstanding actions.
  - New: Open investigations and Outstanding actions had no section of their own.
  - Removed: Work Summary's other parts (What Was Built, Scope Compliance), Testing Notes, Session
    Timeline, Session Notes, Dependencies & Handoff, Recommendations for Next Agent and the close
    checklist. The template's comment names Review, Timeline and Notes for the next agent as
    optional sections a record may still add.
  - Front matter now uses the family's keys and order (`code`, `title`, `kind`, `status`,
    `created`), with `phase` and `agent` optional. `schema_version` is dropped, as in the other
    framework templates. The code form is `SESS-YYYY-MM-DD-NN`, the form d-system's own records use,
    instead of the draft's `SESS-YYYY-MM-DD-agent-NN`; the schema's `code` pattern is therefore not
    the family's `PREFIX-NNN`.
- **Status values** are `draft`, `active`, `complete`, `superseded`. This was not asked about; it is
  stated here for the review.
- **`--document` accepts a `session` kind** (owner, this session). The kind's template is found from
  its schema's file name (`session-record.schema.json` to `session-record.template.md`) instead of
  from the kind name, because the two differ for this kind.
- **The filled example restates `SESS-2026-10-12-01`** (the requirement and plan schemas session) in
  short form, as the other examples restate real documents.

## Unresolved

- `tools/check_no_private_content.py` checked 0 identifiers in the worktree, because
  `_private/portfolio/` exists only in the primary checkout. Its `check_content` function, run on the
  8 files the branch changes with the 31 identifiers loaded from the primary checkout, reported no
  violations.
- The framework `INDEX.md` still lists `session-record.schema.json` as "to create". It is not a
  deliverable of this phase.
- Real d-system session records do not use this shape. Of the 235 records in `docs/03-sessions/`,
  the most common level-2 headings are Unresolved (195), Phase (194), Verification (189), Acceptance
  (170), Review (158), Backlog (157) and Decisions (146), so `--document --kind session` fails them
  (both records dated from 2026-10-10 on fail). The
  template describes the portable framework's records, not d-system's; changing d-system's own
  session-writing commands is outside this phase.
