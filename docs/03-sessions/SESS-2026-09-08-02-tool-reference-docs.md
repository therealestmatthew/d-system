---
schema_version: 1
id: doc-session-2026-09-08-02
code: SESS-2026-09-08-02
title: Generate per-tool operations documents from a new reference generator
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-delivery, sys-governance]
depends_on: [doc-tooling-documentation]
---

# Generate per-tool operations documents from a new reference generator

## Phase

`phase-tool-01` — Document each tool with a generated reference.

## Verification

`uv run pytest`
```
320 passed, 2 warnings
```

`uv run python -m src.governance`
```
Governance OK: 16 systems, 84 documents, 13 memories, 96 backlog phases
```

## Acceptance

- **Regenerating twice produces identical output.** Met — `test_regenerating_twice_produces_identical_output`
  passes, and two consecutive runs of `uv run python tools/generate_tool_docs.py --check` both report
  all six paired documents current with no working-tree diff between them.
- **The test fails when a generated section is edited by hand.** Met — `test_a_hand_edit_is_detected`
  passes; also confirmed by hand: editing text inside a document's generated block made `--check` exit
  1 and name the file, and regenerating restored it.
- **No document is created for a tool that does not exist yet.** Met — `update_doc` only edits a doc
  that already exists between its markers and raises if the markers are absent; the generator's only
  `write_text` call operates on a path `find_doc` returned, and `find_doc` returns `None` (skipped,
  nothing created) for a tool with no matching `OPS-*` file. Covered by
  `test_a_tool_with_no_document_is_reported_not_created`.

## Backlog

`phase-tool-01` reaches `status: complete` (`agent-tool01`) in this close. All scope items are done,
all three acceptance conditions are met, and the independent review's one substantive discrepancy was
fixed before completion (see Corrections below).

## Unresolved

None. The generator's argument extraction is static (AST-based) and cannot resolve a dynamically
computed `choices=` value — `append_idea.py`'s `status` subcommand builds its `to` choices from
`legal_transitions()` at parse time, so that one cell renders empty rather than listing the values;
the human-written narrative in `OPS-005-append-idea.md` names the actual usage instead. Not a defect
against this phase's acceptance criteria, but worth knowing if a future tool's argument table looks
sparser than expected.

## Review

Independent review by a fresh, non-fork sub-agent, given the phase's `scope`/`acceptance`/
`verification` (pasted from `backlog.yaml`), the commit range `dev...HEAD` (three commits at the time
of review: the commit “Add the tool-reference generator and its tests”, the commit “Write one OPS document per existing tool, using the OPS series ADR-011 settled”, the commit “Checkpoint phase-tool-01: all acceptance conditions met”), and this session record. Instructed to independently
rerun verification and hand-test the three acceptance conditions rather than trust the record's
claims. Reported verbatim:

> ## Independent Acceptance Review: phase-tool-01
>
> **Reviewed in:** `/code/d-system-worktrees/phase-tool-01` (branch `agent/phase-tool-01`, `dev...HEAD`
> = 3 commits: the commit “Add the tool-reference generator and its tests”, the commit “Write one OPS document per existing tool, using the OPS series ADR-011 settled”, the commit “Checkpoint phase-tool-01: all acceptance conditions met”)
>
> ### Acceptance condition 1: Regenerating twice produces identical output
>
> **Verdict: Met.**
>
> - Ran `uv run python tools/generate_tool_docs.py --check` twice in succession: both runs printed `5
> tool document(s) current`, exit 0, and produced no working-tree diff (`git status --short` clean
> after both).
> - `test/test_tool_docs.py::test_regenerating_twice_produces_identical_output` calls `render(tool)`
> twice per tool and asserts equality. This is a real (if narrow) determinism check on the pure
> rendering function — `render()` parses AST, extracts args via `ast.walk` in source order and exit
> codes via a `set` that is `sorted()` before return, so there's no ordering non-determinism to hide.
> It is not a tautology, but it only tests the in-memory `render()` function, not the full
> read-modify-write-to-disk path; the CLI-level `--check` rerun I performed covers that gap directly
> and also came back identical.
> - `test_every_paired_document_matches_regenerated_output` independently confirms all 5 committed OPS
> docs equal fresh regeneration.
>
> ### Acceptance condition 2: The test fails when a generated section is edited by hand
>
> **Verdict: Met.**
>
> - `test_a_hand_edit_is_detected` copies a real doc to `tmp_path`, inserts `\n(tampered)` right after
> the `START` marker, monkeypatches `find_doc`/`discover_tools` to point at the tampered copy, and
> asserts `main(["--check"])` returns 1. This tampers a real file on disk and checks the actual
> `--check` exit code — not a bare string comparison that can't fail.
> - I independently hand-tampered the real committed `docs/08-governance/OPS-002-rebuild-db.md`
> (inserted a line inside the generated block) and reran `uv run python tools/generate_tool_docs.py
> --check`: it printed `stale generated section(s): .../OPS-002-rebuild-db.md` and exited 1. Restored
> with `git checkout -- docs/08-governance/OPS-002-rebuild-db.md`; a subsequent `--check` came back
> clean (`5 tool document(s) current`, exit 0). `git status --short` confirmed no residual diff.
>
> ### Acceptance condition 3: No document is created for a tool that does not exist yet
>
> **Verdict: Met.**
>
> - Read `tools/generate_tool_docs.py`: the only `write_text` call in the file (line 179, inside
> `main()`) writes to `doc`, which comes from `find_doc(tool)` — and `find_doc` returns `None` (skipped
> via `continue`, never creating anything) when no matching `OPS-*-<slug>.md` exists. There is no
> `open(..., 'w')`, `.touch()`, or `mkdir` call anywhere that could fabricate a new document.
> - I independently verified by hand: created `tools/not_yet_built.py` with a docstring, ran `uv run
> python tools/generate_tool_docs.py` (non-`--check` mode). Output: `no OPS document found for:
> not_yet_built.py` / `updated 0 of 5 paired tool document(s)`, exit 0, and no new file appeared under
> `docs/08-governance/`. Removed the fake tool afterward; `git status --short` came back clean.
> - `test/test_tool_docs.py::test_a_tool_with_no_document_is_reported_not_created` covers this too,
> asserting `find_doc(fake_tool) is None`.
>
> ### Verification reruns (actual output)
>
> - `uv run pytest` → **319 passed, 2 warnings** — matches the session record and backlog `result`
> field exactly.
> - `uv run python -m src.governance` → **`Governance OK: 16 systems, 83 documents, 13 memories, 96
> backlog phases`**. This does **not** match the "82 documents" quoted in both the session record's
> Verification section and the backlog.yaml `result` field (see discrepancy below).
>
> ### Pattern-following and coverage checks
>
> - `tools/generate_tool_docs.py` follows `tools/generate_glossary.py`'s shape: module docstring with
> usage examples, a pure `render()` function, a `--check` flag that exits 1 on staleness, `main(argv)`
> with argparse, `raise SystemExit(main())` at the bottom. No structurally different shape was
> invented.
> - `tools/*.py` currently holds 6 files: `append_idea.py`, `generate_glossary.py`,
> `generate_ideas_md.py`, `generate_tool_docs.py`, `load_context.py`, `rebuild_db.py`.
> `discover_tools()` explicitly excludes `generate_tool_docs.py` itself ("itself excluded" per its own
> docstring), leaving 5 tools — matching the 5 new OPS docs (`OPS-002` rebuild-db, `OPS-003`
> load-context, `OPS-004` generate-glossary, `OPS-005` append-idea, `OPS-006` generate-ideas-md).
> `OPS-001-operations.md` is a pre-existing general document, not per-tool.
> - `AGENTS.md` was updated (lines added under the governance section) with the
> new-tool-ships-with-its-OPS-doc convention, naming the `OPS-NNN-<tool-stem>.md` filename pairing
> convention the generator relies on.
> - ADR-011 (`docs/04-decisions/ADR-011-governance-model.md`) was read in full: section 3 explicitly
> settles that per-tool documents use the `OPS` series ("This unblocks `phase-tool-01`... It uses the
> `OPS` series"), and the Consequences section reiterates it. The diff's use of `OPS-002`..`OPS-006`
> matches this decision exactly; no codes were minted ahead of it (phase-gov-02, which produced
> ADR-011, is `status: complete` and is listed as a satisfied `depends_on` for phase-tool-01).
>
> ### Discrepancies found
>
> 1. **Stale document count in the session record and backlog `result` field.** Both
> `docs/03-sessions/SESS-2026-09-08-02-tool-reference-docs.md` and the `result:` field for
> `phase-tool-01` in `docs/09-backlog/backlog.yaml` quote `uv run python -m src.governance` as
> reporting **82 documents**. A fresh rerun today reports **83 documents**. This is explained by
> commit order: the final checkpoint commit (the commit “Checkpoint phase-tool-01: all acceptance conditions met”) added the session-record document itself and
> bumped `catalog.md`'s own footer to "83 documents," but the governance-output text pasted inside
> that same session record was apparently captured before that document existed, so it never got
> updated to reflect its own addition. It's a self-referential off-by-one, not a sign of an
> inconsistent catalog (catalog.md's own count field and a fresh governance run agree at 83; pytest,
> which includes catalog-consistency checks, passes at 319). Still, it means the verification output
> quoted in the permanent session record does not match what a rerun actually produces, which the
> review was asked to flag explicitly.
>
> 2. **`generate_tool_docs.py` has no OPS document of its own.** The scope line reads "Write one OPS
> document per existing tool," and AGENTS.md's newly-added rule states "A new tool under `tools/` ships
> with its own `OPS-*` operations document." `generate_tool_docs.py` is itself a new tool shipped in
> this phase, but it is deliberately excluded from `discover_tools()` (avoiding the tool editing its
> own generated block) and no `OPS-*` document anywhere references it — confirmed by `grep -rl
> "generate_tool_docs\|generate-tool-docs" docs/08-governance/*.md` returning nothing. This doesn't
> violate any of the three stated acceptance conditions (which concern determinism, hand-edit
> detection, and non-creation for nonexistent tools — not coverage completeness for existing tools),
> and the self-exclusion is a reasonable design choice to avoid a self-editing generator. But it is a
> literal gap against the scope bullet and the just-added AGENTS.md convention, and neither the diff
> nor the session record explains or acknowledges the gap — the only trace is a one-line code comment
> ("itself excluded") with no rationale recorded anywhere governance-visible.
>
> No other discrepancies were found. The three acceptance conditions and both named verification
> commands otherwise hold exactly as the diff and session record claim, and the OPS-series usage is
> correctly grounded in ADR-011's actual decision text rather than asserted independently.

## Decisions

- **Included the generator itself in `discover_tools()` rather than leaving it excluded.** The review's
  discrepancy 2 was correct: `generate_tool_docs.py` is a tool this phase shipped, and both the scope
  bullet ("one OPS document per existing tool") and the AGENTS.md convention this same phase added
  apply to it with no stated exception. The original self-exclusion had no functional reason — static
  `ast` parsing of the generator's own source carries no self-execution hazard — so the fix was to stop
  excluding it, write `OPS-007-generate-tool-docs.md` for it, and let the generator document itself the
  same way it documents everything else.
- **That inclusion surfaced a real bug, not just a documentation gap.** Once the generator tried to
  render its own docstring — which quotes the literal `<!-- generated:tool-reference:start/end -->`
  marker text as a usage example — `update_doc`'s first-occurrence split on `END` cut the block off at
  the quoted example instead of the true closing marker, and `--check` reported the freshly-generated
  file as stale against itself. Fixed by splitting on the first `START` and the **last** `END`
  (`str.partition`/`str.rpartition`), which is correct given the repository convention that the
  generated block is always the final thing in these documents. Added
  `test_update_doc_survives_marker_text_quoted_inside_the_rendered_block` as a regression test, since
  this failure mode only appears when rendered content quotes the markers — a case none of the other
  five tools' docstrings happen to hit.
- **Fixed the stale document-count text in place rather than leaving it as a known artifact.** Discrepancy
  1 was a real mismatch between quoted output and a rerun, even though the underlying catalog was
  never actually inconsistent. Re-ran verification after all fixes and replaced the quoted numbers
  with the current, accurate ones (320 tests, 84 documents) rather than annotating the old numbers as
  stale.

## Corrections

Two corrections, both driven directly by the independent review rather than found before it:

1. **Missing OPS document for the generator itself.** The review is correct that this was a real gap
   against this phase's own scope and its own new AGENTS.md rule, not a false positive. Fixed by
   writing `OPS-007-generate-tool-docs.md` and including the tool in `discover_tools()`.
2. **The marker-splitting bug** described above under Decisions. This was not visible before the
   generator was asked to document itself — none of the five original tools' docstrings quote the
   marker syntax, so the bug was latent and untested. It is now fixed and covered by a regression
   test, and would have been a real correctness defect (silent, permanent `--check` staleness for any
   future tool whose docstring happens to mention the marker text) if the review had not prompted the
   self-inclusion that exposed it.

The document-count text (discrepancy 1) was a reporting artifact, not a logic error, and is corrected
above under Decisions rather than listed again here as a substantive fix.

## Left undone

Nothing on this phase's own scope. `phase-gov-03` (PROMPT-003, next in the queue after this phase) was
not started — it is its own phase with its own session budget. The known limitation on dynamically
computed `choices=` values (see Unresolved above) is a documented property of static extraction, not
something left undone.
