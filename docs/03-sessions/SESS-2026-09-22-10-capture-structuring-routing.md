---
schema_version: 1
id: doc-session-capture-structuring-routing
code: SESS-2026-09-22-10
title: Capture structuring, evidence scoring and routing
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-capture]
depends_on: [doc-capture-build]
---

# Capture structuring, evidence scoring and routing

## Phase

`phase-cap-05` — Implement structuring, evidence scoring and routing.

## Verification

`uv run pytest test/test_capture_routing.py`

```text
73 passed, 2 warnings
```

`uv run mypy src/`

```text
Success: no issues found in 28 source files
```

## Acceptance

- Stakes-by-evidence matrix — **Met.** `test_each_matrix_cell_produces_the_stated_route` runs 33
  cases: each of the 11 entity types in `routing.STAKES` against explicit, inferred and guessed
  evidence. That covers all four stakes tiers, and each case asserts ADR-007's route.
  `test_an_unresolved_reference_holds_an_otherwise_clean_record` adds 7 cases showing that an
  unknown person, project or tag holds the record.
- Ambiguous capture completes non-interactively and is flagged — **Met.**
  `test_an_ambiguous_inbox_capture_completes_without_prompting_and_is_flagged` puts a vague note
  through `scan_inbox` and then `stage_capture`, with `input()` replaced by a function that fails
  the test and `sys.stdin` set to None. It completes, and the result is one staged record routed
  `flagged`.
- Unknown person creates no person record anywhere — **Met.**
  `test_a_capture_naming_an_unknown_person_creates_no_person_record` compares byte snapshots of a
  temporary data root and of the repository's `_data/` before and after, checks that staging holds
  only the commitment, and checks that the name is kept as written with the route `held`.
- Same fixture through all three channels — **Met.**
  `test_the_same_fixture_through_all_three_channels_routes_identically` captures one text through
  the session writer, the inbox scanner and the CLI's `main()`, then stages the same three
  proposals from each capture. The routes and evidence are identical once each record's own
  `capture_id` is removed.

## Backlog

`status: active`, `agent: agent-builder-b`, `session: doc-session-capture-structuring-routing`.
`next_action`: All acceptance conditions are met on agent/phase-cap-05; waiting for the
owner-approved merge onto dev, after which the completion edit is made.

## Unresolved

- REQ-002 R11: a new tag inside an existing category is held rather than created with an alert,
  as the owner ruled for this phase. The alert-and-create path is left to review and promotion
  (`phase-cap-06`).
- REQ-002's opening paragraph still says only R1, R2 and R5 are implemented. That document is not
  a deliverable of this phase.

## Review

Independent adversarial review (a fresh `demo-adversary` subagent) of `dev...agent/phase-cap-05`
at commits `2987bde` and `26745b1`. The reviewer ran both verification commands itself
(`62 passed, 2 warnings`; mypy `Success: no issues found in 28 source files`), and ruff on the new
files was clean. Its findings, as reported:

- **Acceptance 1, the matrix — Holds.** Reversing the check order so `flagged` is tested before
  `held` broke 8 matrix cases, so the test enforces that held outranks flagged. No fixture covered
  a high-stakes record with an unresolved reference, although the code routed it correctly.
- **Acceptance 2, ambiguous capture — Holds.** No prompt path exists in either module.
- **Acceptance 3, unknown person — Holds.** A search confirmed that neither module writes to
  `_data/`; they only read it.
- **Acceptance 4, three channels — Holds.**
- **HIGH:** a non-list value in a list field (`participants`, `decided_by`, `participant_names`,
  `decided_by_names`, `tags`) raised an unhandled `TypeError` instead of a `StructuringError`. A
  bare string was read one character at a time.
- **MEDIUM:** the id-collision check sat inside the write loop, so a collision could leave some
  of one capture's records staged. That contradicted the docstring's promise that staging is left
  unchanged.
- **MEDIUM:** no test covered a truthy non-boolean `review_flag` such as `"true"`. The code
  rejected it, but a mutation that accepted `"true"` still passed all 62 tests.
- **LOW:** a quote that appears twice always resolves to its first occurrence.
- **No discrepancies found** in the never-invent field list, the completion statuses (checked
  against the task, commitment and waiting-on schemas), empty or missing quotes at `explicit`,
  `D_SYSTEM_DATA_ROOT` handling, or `_data/` writes.

**What was done about each finding** (in `structure.py` and `test_capture_routing.py`, commit
following `26745b1`):

- HIGH — fixed. Reference fields are checked before use: person and project fields must be a
  string or null, and list fields a list of strings. Anything else is refused with the field named.
  Six parametrised cases cover this.
- MEDIUM, partial write — fixed. `stage_capture` now confirms every id is free, both on disk and
  within the batch, before writing anything. A test with a pinned id shows staging is unchanged
  after a collision in either form.
- MEDIUM, truthy flag — test added: `"true"`, `1` and `"yes"` are each refused, naming the field.
  Re-applying the reviewer's mutation still left the suite green. The staged-record schema itself
  requires `review_flag` to be a boolean, so the record is refused by schema validation even when
  the code check is weakened. The new test pins that observable result rather than the mechanism.
- Coverage gap — test added: a `decision` with an unresolved reference is held, not flagged.
- LOW — accepted. A proposal carries no offset to choose between occurrences, and the quote is
  verbatim either way. A comment at the `find` call records this.

## Decisions

- **The interpretation is an agent's proposal, not code in this phase.** The phase did not say
  what reads a capture for meaning. The owner chose a deterministic validator over an LLM call or
  a rule-based extractor: `structure.py` checks and stages a proposal but never interprets text.
  This keeps every acceptance condition testable with fixtures.
- **Every new tag is held.** The phase scope, REQ-002 R8 and ADR-007 section 5 say to hold new
  tags; R11 and section 9 say a new tag in an existing category is created with an alert. The owner
  ruled for this phase to hold all new tags and to leave R11 for phase-cap-06.
- **A completion status is protected like a completion date.** ADR-007 forbids inventing
  "completion of anything", and `evidence.schema.json` lists only the `completed` and `received`
  fields. A `status` of `complete` or `received` is therefore also treated as protected. These are
  the only completion values in the task, commitment and waiting-on enums.
- **A person reference resolves only by id.** A name that matches a known person's name, but not
  their id, is kept as written and held. Matching a name to a person is the identity call ADR-007
  reserves for the owner.
- **`note` is the raw-note tier.** ADR-007's low-stakes "raw note" has no schema, so the staged
  `entity_type` for it is `note`. `tag-category` names the structural new-category case.

## Corrections

- One test sorted a list of dicts directly and failed on the first run. It was fixed to sort by id
  before the first commit.
- The first version of the collision regression test forced a shared random suffix, so it only
  collided when both records were staged in the same second. It was changed to pin `_new_id`
  itself before commit.

## Left undone

- REQ-002 R11's alert-and-create path for a new tag inside an existing category — phase-cap-06.
- REQ-002's opening paragraph still lists only R1, R2 and R5 as implemented. It is not a
  deliverable here and should be updated by whoever next amends that document.
- Nothing yet produces proposals. A conversational agent or a later phase has to write them in the
  shape documented in `structure.py`'s module docstring.
