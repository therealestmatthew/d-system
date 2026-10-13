---
schema_version: 1
id: doc-session-requirement-plan-schemas
code: SESS-2026-10-12-01
title: Requirement and plan document schemas
kind: session
status: active
owner: repository-owner
created: '2026-10-12'
updated: '2026-10-13'
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
carry none of the forms the four `--document` templates use (`REQ-NNN`, `YYYY-MM-DD`, a bracketed name
in the title, an HTML comment, an `Example:` lead-in). Run against the templates instead, the same
pattern finds every one of those forms, so the check is not passing by matching nothing.

`--document <path> --kind <kind>` (added for review finding F01, extended in round 2) runs the
schema check, the placeholder check and the retained-sample check on any one document and exits 1
if any fails, or if the path does not exist. The suite runs it on ten examples, under
DOCUMENT_CASES above. Run directly:

```text
requirement.boilerplate.md --kind requirement: exit=1
plan.boilerplate.md --kind plan: exit=1
requirement.stripped-sample.md --kind requirement: exit=1
plan.stripped-sample.md --kind plan: exit=1
requirement.bom.md --kind requirement: exit=0
requirement.valid.md --kind requirement: exit=0
plan.valid.md --kind plan: exit=0
plan.valid.md --kind requirement: exit=1
governance.valid.md --kind governance: exit=0
protocol.valid.md --kind protocol: exit=0
file.md --kind requirement: exit=1
--document without --kind: exit=2
```

The two boilerplate fixtures are the templates with only `code`, `created` and the title line
filled in (and the plan's `depends_on`, so the plan fixture is not failed by its schema instead).
Validated against the schema alone, both return no errors, so the placeholder check is what fails
them.

The retained-sample check compares the front-matter `title` with the template's sample title, and
each section body with the sentences of the template's sample text. The sample is read from the
kind's own template, with comments and `Example:` lead-ins removed, split into paragraphs, list
items and bold-led lines, then into sentences. Both sides are normalized before comparing: case
folded, punctuation removed, whitespace collapsed (round 3). Sentences shorter than 30 characters
after normalizing are not compared, so a short generic phrase cannot fail a real document.
`req-case-only.md`, the reviewer's round-3 probe copied unchanged, lowercases the title and the
first Overview sentence and must fail.

**Known limit (owner ruling, round 3): reworded sample text passes.** The comparison is exact after
normalizing, so a sample sentence with a word or two changed is not caught. The check is a lint aid
for an author who forgot to replace the sample, not a guarantee that none remains; fuzzy matching
was ruled out. The reviewer's two full-rewording probes now exit 1, but only because normalizing
made a few sentences they left untouched match (the R02 heading, the verification command, the
first phase line). Their reworded sentences still pass. The two stripped-sample fixtures are the
reviewer's round-2 probes, copied unchanged: the boilerplate copies with every comment and
`Example:` lead-in removed. `requirement.bom.md` is `requirement.valid.md` with a UTF-8 byte-order
mark, also the reviewer's probe. A missing path:

```text
FAIL  /no/such/file.md as a requirement document
        no such file: /no/such/file.md
```

Two further reviewer probes were run directly and fail as they should (exit 1): a requirement with
one section rewritten and the rest of the sample kept, and one with comments removed but the
`Example:` lead-ins kept.

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

- **The angle-bracket form was removed from the placeholder pattern** (review round 1, while fixing
  F01). The first `--document` run failed `protocol.valid.md`, a filled document, on
  `` `agent/<phase-id>` `` in a code span. Of the Markdown templates only `phase.template.md` uses
  an angle-bracket slot, and phase is not a `--document` kind, so the form was dropped rather than
  special-cased. **Correction:** the round-1 fix commit's message says no Markdown template uses the
  form. That is wrong: `phase.template.md` does. The commit message is left as pushed; this record
  and the code comment carry the correct statement. The governance and protocol examples were added as
  passing `--document` cases so a false positive of this kind fails the suite.
- **Retained template sample text fails `--document`** (owner ruling, 2026-10-13, review round 2).
  A document fails if its front-matter title is its template's sample title, or if any section
  keeps a sentence of the template's sample text. Round 3 (owner ruling): both comparisons ignore
  case and punctuation; reworded text is a stated known limit, with no fuzzy matching.
- **`governance.valid.md` and `protocol.valid.md` were rewritten** (owner, this session, chosen over
  replacing the two templates' sample text, which are `phase-fwt-01` files outside this phase's
  deliverables, and over limiting the sample check to requirement and plan). Both restated the
  same rules their templates use as samples, so the new check failed them. They now restate
  different rules: owner approval before integrating a branch (in the "rationale adopted before
  any incident" form the template allows) and removing a finished worktree. The three fixtures
  derived from them (`governance.no-incident.md`, `governance-shape-labelled-protocol.md`,
  `protocol-shape-labelled-governance.md`) were regenerated from the new text by the same edits
  as before. The round-1 cross-validation cases still pass. The example codes, GOV-001 and GOV-002,
  are the adopting repository's own numbering, not d-system's documents of those codes.

## Unresolved

- `tools/check_no_private_content.py` checked 0 identifiers in the worktree, because
  `_private/portfolio/` exists only in the primary checkout. Its `check_content` function, run on every
  file the branch changes against dev (25, after the round-2 fixes) with the 31 identifiers loaded
  from the primary checkout, reported no violations.
- The framework `INDEX.md` still lists `requirement.schema.json` and `plan.schema.json` as "to
  create". It is not a deliverable of this phase.

## Review

Round 1, at `547b3154`, run by the Session Manager. Verdict records, committed unchanged in
`31fbfd17` (`7e3d4a1b` before the rebase onto dev `9df2ae34`):

- `docs/08-governance/reviews/verdicts/2026-10-13-phase-fwt-03-demo-adversary.json`
  (sha256 `f197a5872c1436d9de5c1139c74cf92dc528967471dffa25b3c0bdda2193eb22`): gating pass with one
  finding.
  - **F01 major — fixed** (owner ruling, 2026-10-13: fix in this phase). The placeholder check ran
    only on the two shipped examples, so a real document that was still template boilerplate
    validated. `check_schemas.py` now has a `--document <path> --kind <kind>` mode that runs the
    schema and the placeholder check on any document and exits 1 if either fails. Two boilerplate
    fixtures, `examples/requirement.boilerplate.md` and `examples/plan.boilerplate.md`, must fail it.
    The existing cases are kept.
- `docs/08-governance/reviews/verdicts/2026-10-13-phase-fwt-03-review-judge.json`
  (sha256 `594d4f42a1c51a19621887c9dfdb3c25c83ca845b4f9bf9225f038c4c0c275b8`): shadow pass with one
  finding.
  - **F01 minor — accepted.** The phase's second verification entry is prose, so the review runner
    does not execute `check_schemas.py`. Changing it is a `backlog.yaml` edit outside this phase's
    deliverables, mid-review; `phase-fwt-02` accepted the same finding for the same reason. The
    literal command and its output are in this record's Verification section.

The reviewers found the status values (`draft`, `approved`, `active`, `complete`, `deprecated`,
`superseded`) consistent with d-system's real plans; no change.

Round 2, at `9c3d3c61`, run by the Session Manager: gating **reject**. The round-2 shadow review was
not dispatched; it runs on the next tip. Verdict record, committed unchanged in `828ebd48`:

- `docs/08-governance/reviews/verdicts/2026-10-13-phase-fwt-03-demo-adversary-2.json`
  (sha256 `6127a77de1082b0bb193d6d1ad9a4a051cfb53a73a4729443a4a1a7b4cc1eba1`): four findings.
  - **F01 major — fixed** (owner ruling, 2026-10-13: detect retained sample text). Round 1's fix
    matched only literal markers, so a copied template with its comments and `Example:` lead-ins
    removed but its sample text kept passed `--document`. `--document` now also compares the
    front-matter title and each section body with the template's own sample text. The reviewer's
    two stripped probes are failing fixtures.
  - **F02 minor — fixed** by the same check: a front-matter title equal to the template's sample
    title fails.
  - **F03 minor — fixed.** `--document` on a missing path printed a `FileNotFoundError` traceback. It
    now prints a FAIL line naming the path and exits 1.
  - **F04 minor — fixed.** A UTF-8 byte-order mark hid the front matter. `split_document` drops a
    leading mark first; `requirement.bom.md` is a passing case.
  - The reviewer also flagged the round-1 claim that no Markdown template uses the angle-bracket
    form; corrected under Decisions.

Round 3, at `70646557`, run by the Session Manager: gating reject, which the owner ruled **accept
after a small fix** (2026-10-13). Round-2 F02 to F04 were found resolved. The round-3 verdict record
follows once the round-3 shadow review returns.

- **Blocker — accepted as a known limit, per the owner's ruling.** Light rewording of every sample
  sentence passed `--document`, because the comparison is an exact substring match. Both sides are
  now normalized, and the limit is stated in `retained_sample`'s docstring and above. No fuzzy
  matching. The Session Manager is sending the rewording gap to Ideation as an idea.
- **Minor — fixed.** The title comparison was case-sensitive. It now uses the same normalization,
  and `req-case-only.md` is a failing fixture.
