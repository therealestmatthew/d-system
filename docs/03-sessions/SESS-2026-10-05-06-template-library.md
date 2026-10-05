---
schema_version: 1
id: doc-session-template-library
code: SESS-2026-10-05-06
title: The template library with declared population methods
kind: session
status: active
owner: repository-owner
created: '2026-10-05'
updated: '2026-10-05'
systems: [sys-html]
depends_on: [doc-html-generation-design-system]
---

# The template library with declared population methods

## Phase

`phase-des-03`: Make the template layer a growing library with declared population methods
(`REQ-021` R04-R06; `PLAN-036`, amendment decision A). Run overnight on 2026-10-05 as Session 5
(Batch Runner, `agent-batch-runner`). The Session Manager assigned it, and the owner
pre-approved the assignment.

The claim narrowed the phase's deliverables from `templates/html/`, `templates/styles/` and
`tools/` to the files actually built, and excluded every `phase-lrr-03` file. The parked
`agent/phase-lrr-03` branch holds those. A later turn widened the deliverables to the tool's
operations document and its `codes.yaml` reservation. Both edits were Session Manager grants;
see Decisions.

## Verification

`uv run python -m src.governance`

```text
Governance OK: 45 systems, 444 documents, 37 memories, 347 backlog phases
```

`uv run pytest`: see the post-rebase gate in this record's READY message. The run on the first
commit (`74e8397`), before the operations document existed, gave:

```text
2 failed, 1536 passed, 1 skipped, 1 warning
FAILED test/test_tool_docs.py::test_every_existing_tool_is_paired_with_a_document
FAILED test/test_tool_docs.py::test_every_paired_document_matches_regenerated_output
```

Both failed because `tools/template_library.py` had no paired `OPS-*` document. `OPS-033` fixes
that:

`uv run pytest -q test/test_template_library.py test/test_tool_docs.py`

```text
34 passed, 1 warning
```

`uv run ruff check src/ test/ tools/template_library.py` and
`uv run mypy src/ tools/template_library.py`

```text
All checks passed!
Success: no issues found in 49 source files
```

`uv run python tools/generate_tool_docs.py --check`

```text
28 tool document(s) current
```

Private-content check with the real portfolio identifiers: the tool's functions were run from
the worktree, as in `SESS-2026-10-05-05`.

```text
files 1327 identifiers 31 violations 0
```

Two mutation checks show the tests depend on the behaviour:

- Making `fill()` strip each value fails 3 tests: both byte-identity replays and the new-family
  CLI render.
- Making `render()` treat every template as `slot-fill` fails 4 tests: the dispatch tests and the
  brief tests.

## Acceptance

- `REQ-021` R05 holds — a template added without touching a generator renders, and both existing
  families still render byte-identically: Met.
  - `test_a_new_file_in_an_existing_family_renders_without_any_change` adds
    `overview-callout.html`, which the family's pattern already covers.
  - `test_a_new_family_is_a_manifest_entry_and_renders_through_the_cli` adds a family and
    renders it through the CLI. Neither touches a generator.
  - Overview: `test_every_overview_fill_replays_byte_identically_through_the_library` records
    every fill `generate_overview.generate()` makes on the real repository and replays each one
    through `render()`. All eight overview templates are exercised, and the bytes are equal.
  - House: the same replay runs for the engine pages and for the `--specimen`.
  - Atlas: no code has ever rendered its pages, so there is no artifact to replay; see Review.
  - `test_adding_templates_leaves_existing_renders_byte_identical` shows that adding a template
    and a family changes neither family's render.
- `REQ-021` R06 holds — the population method is machine-readable and a generator dispatches on
  it: Met.
  - `templates/html/library.yaml` declares the method, and `template_library.py list` and
    `show` print it as JSON.
  - `render()` dispatches on it. `test_dispatch_follows_the_declaration_not_the_caller` changes
    only the manifest and gets a brief instead of a page for the same call.
- `REQ-021` R04 holds — the phase cites the audit's findings for its scope: Met.
  `library.yaml`'s header cites `ADR-027` and `SESS-2026-10-04-08`: `PLAN-003` contributes no
  template, and its YAML-to-JSON population model is retired. The methods declared start from
  the generators that exist, as `ADR-027` directs.

## Backlog

`status: active`, `agent: agent-batch-runner`. `next_action`: all acceptance met and reviewed;
awaiting the owner's merge approval through the Session Manager.
`completion_evidence`: the six deliverables and this record.

## Unresolved

- R06 is met by the new library dispatching; the four existing generators still load their
  templates directly and do not consult the manifest. See Review finding 2 and Decisions.

## Review

The reviewer was a fresh `demo-adversary` sub-agent. It reviewed `dev...HEAD` at `74e8397` and
was given the phase's scope, acceptance, verification and narrowed deliverables, and no session
record. Its findings, in substance:

- R04 Met: the citation matches `ADR-027` exactly.
- The house-and-engine-pages extraction and the no-code-change scope bullet: Met.
- `load()`'s validation and determinism: no discrepancy. No model, subprocess or network call
  anywhere in the tool.
- R05 Met for overview, with real replay evidence.
  - Atlas (should-fix): its evidence is weaker. Atlas pages were never produced by code, so
    "renders byte-identically" holds only in the sense that nothing in its pipeline changed.
    The documentation says so honestly.
- R06 Met literally: the new library dispatches.
  - Note: the existing generators do not consult the manifest, so a caller of
    `generate_engine_pages.py` learns nothing new. Flagged for the coordinator.
- Finding 1 (should-fix): governance failed in the worktree. The cause was the then-untracked
  `OPS-033` draft, which was not yet a declared deliverable.
- Finding 2 (note): the house family named only `generate_engine_pages.py`, though
  `generate_house_css.py --specimen` also fills `house-page.html`.

Dispositions:

- Finding 1: fixed. `OPS-033` became a declared deliverable on `dev` (`1a2ab05`) and was
  committed with the regenerated catalog in `473305c`.
- Finding 2: fixed. `generator` became a `generators` list, the house family names both tools,
  and `test_house_specimen_replays_byte_identically_through_the_library` replays the specimen
  fill.
- Atlas evidence: accepted. There is no deterministic atlas renderer to replay. The library
  fills atlas's shell slots, and `test_adding_templates_leaves_existing_renders_byte_identical`
  pins that output across library growth. The committed atlas pages and templates are not
  touched by this phase.
- R06 scope: accepted as R06's own verification text reads ("confirm a generator can dispatch
  on it"). Moving the existing generators onto the library is a change to four shipped,
  byte-pinned tools, which the phase's `next_action` warns against ("treat them as the
  regression surface, not as examples to rewrite").

## Decisions

- OVERNIGHT ASSUMPTION: the deliverables were narrowed at the claim to
  `templates/html/library.yaml`, `tools/template_library.py`, `test/test_template_library.py`
  and `templates/README.md`. The new test file was declared at claim time, under `test/`, which
  containment maps to `sys-delivery`. The Session Manager granted this as the AGENTS.md route,
  following the `phase-lrr-03` precedent.
- OVERNIGHT ASSUMPTION: the deliverables were widened to `docs/08-governance/OPS-033-template-library.md`
  and `docs/08-governance/codes.yaml`. The repository requires each `tools/*.py` to have a paired
  `OPS-*` document (`test_tool_docs.py`), and governance requires a reserved code for a planned
  deliverable. Both follow `phase-des-09`'s precedent. The reservation was removed when the
  document landed.
- OVERNIGHT ASSUMPTION: each family states its population method once, in one manifest, by file
  pattern. A per-file declaration inside each template would have meant editing
  `phase-lrr-03`'s templates, which this claim excluded, and would have changed every template's
  bytes. With patterns, `phase-lrr-03`'s new `lit-report-table.html` is declared already, which
  `test_a_future_lit_report_file_is_declared_by_its_family_pattern` checks. That branch needs no
  manifest edit when it merges.
- OVERNIGHT ASSUMPTION: the methods declared are:
  - overview, house page, lit-report: `slot-fill` — each has a deterministic generator;
  - `atlas-page.html`: `both` — its shell slots are mechanical, and its token contract leaves
    `MASTHEAD`, `SECTIONS` and `PAGE_SCRIPT` to an author adapting `atlas-components.html`;
  - `house-components.html` and `atlas-components.html`: `ai-adaptation` with
    `reference: true` — they are canonical-markup catalogues an author copies from, and are
    never rendered.
- AI adaptation returns a brief and never calls a model. That keeps the library deterministic
  and leaves the agent that fills the brief to the designer-agent phase (`phase-des-06`).
- The existing generators are untouched. Equivalence is shown by replaying their fills through
  the library, not by rewiring them.

## Corrections

- Two test bugs were found on the first run and fixed before commit:
  - the "every overview template exercised" check compared template names to template bodies;
  - the atlas brief check did not allow for `atlas.css` naming `{{INLINE_STYLES}}` in its own
    comment.
- The first widening attempt added only the deliverable line, and the pre-commit governance run
  rejected it for an unreserved code. Nothing was committed. The change was reverted, and the
  Session Manager granted the `codes.yaml` reservation in the same turn.

## Left undone

Nothing in scope. Wiring the existing generators onto the library, if the owner wants that, is
a separate change to four byte-pinned tools. The agent that consumes adaptation briefs is
`phase-des-06`.
