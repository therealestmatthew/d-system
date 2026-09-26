---
schema_version: 1
id: doc-session-plugin-idea-system
code: SESS-2026-09-25-03
title: Idea-realization plugin idea system — writer, fold, render, priority queue, vocabulary, triage
kind: session
status: active
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-ideas]
depends_on: [doc-idea-realization-plugin-idea-system]
---

# Idea-realization plugin idea system — writer, fold, render, priority queue, vocabulary, triage

## Phase

`phase-plug-02` — The idea system — writer, fold, render, priority queue, vocabulary, triage.

## Verification

Run in `../d-system-worktrees/phase-plug-02` on `agent/phase-plug-02`, rebased onto `dev` at
`dccf952`.

```text
$ cd plugins/idea-realization && uv run pytest
177 passed

$ claude plugin validate plugins/idea-realization --strict
✔ Validation passed

$ uv run python tools/check_no_private_content.py   # changes staged
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (955 tracked files, 0 identifiers checked)

$ uv run python -m src.governance
Governance OK: 43 systems, 362 documents, 32 memories, 318 backlog phases
```

The worktree has no `_private/portfolio/`, so the tool's content check skipped. The same check
function (`confidential_identifiers` and `check_content` from `tools/check_no_private_content.py`),
run from the primary checkout against every file under `plugins/idea-realization/` in this branch,
reported: `31 identifiers checked over 40 plugin files; 0 problems`.

The acceptance-evidence tests, selected by name from the suite above:

```text
$ uv run pytest -q -k "promotion_must_name or promotion_without_promoted_to_is_refused_by_the_cli or second_discard_after_a_revisit or no_help_text_offers or twice_over_a_fixture or hand_edit_to_the_view or vocabulary or queue_naming or queue_dated or valid_priority_queue or triage_agent_cannot or triage_runs_no_link or source_references or schema_enums_equal or fold_matches_the_source"
35 passed, 142 deselected
```

## Acceptance

- The ported transition tests pass through the plugin's script; an open -> promoted without a
  pointer is refused; a second discard after the one revisit is refused; --help shows no time
  option — **Met.** `test_ideas.py` carries the ported writer tests (177 pass).
  `test_promotion_must_name_what_the_idea_became` and
  `test_promotion_without_promoted_to_is_refused_by_the_cli` (exit 1, nothing appended);
  `test_a_second_discard_after_a_revisit_is_permanent`; `test_no_help_text_offers_a_time_option`
  over the top-level help and all eleven subcommands. Reading of the second condition: the schema
  permits `reviewing -> discarded` after the revisit, so the discard itself is accepted and every
  later move — a further revisit, `reviewing`, another discard — is refused as permanent.
- render twice over a fixture log diffs to nothing; an edited rendered file fails check — **Met.**
  `test_rendering_twice_over_a_fixture_log_is_byte_identical`;
  `test_a_hand_edit_to_the_view_is_reported` (check names the view, `render_ideas.py --check`
  exits 1).
- The vocabulary test passes and fails on a fixture document missing one status — **Met.**
  `test_the_vocabulary_matches_the_schema`; `test_a_document_missing_one_status_fails` returns
  exactly `Statuses: absorbed is in the schema but not the document`.
- A fixture priority queue naming a promoted idea fails check naming the id — **Met.**
  `test_a_queue_naming_a_promoted_idea_fails_the_check`, with the unknown-idea, future-date and
  schema-invalid fixtures failing and a valid queue passing (REQ-031 R11).
- The idea-triage agent's tools exclude Edit and Write; the R02 check passes — **Met.**
  `test_the_triage_agent_cannot_edit_or_write_files` (tools `Read, Grep, Glob, Bash`);
  `test_triage_runs_no_link_or_promotion_command`; `test_no_source_references.py` passes over the
  whole plugin tree.

R23 (the schema's enums equal this repository's at the commit `phase-idg-01` landed):
`test_the_schema_enums_equal_the_source_schema`, with the source sets written into the test as
literals by owner ruling, since R21 bars the suite from reading this repository.
PLAN-048.02's fold-equality rule: `test_the_fold_matches_the_source_fold_on_a_fixture_log`; the
literal expected state was checked against `src.db.ideas.fold` on the same fixture before it was
committed (`source fold equals expected: True`).

## Backlog

`phase-plug-02`: `status: active`, `agent: agent-standby-builder`. `next_action`: every acceptance
condition met and the independent review recorded; waits for the owner's merge approval, relayed
by the Session Manager, then completion on `dev`. `session`, `completion_evidence` and `result`
recorded as interim evidence.

## Unresolved

- The merge onto `dev` and the completion edit wait for the owner's approval (contract item 4).
- The repository's own test suite, ruff and mypy are run after the final rebase, for READY, not
  here.

## Review

One independent review ran to a report: a `demo-adversary` agent over `dev...HEAD` at `cffea3b`.
It stopped at its turn limit and reported on request; its findings and verdicts, as given:

- **Should-fix** — `scripts/idea.py`, the `status` subparser: the source constrained the `to`
  positional with `choices=sorted({t for _, t in legal_transitions()})`; the port dropped it, so a
  misspelled status was refused only after the log was loaded and folded, and `--help` no longer
  listed the legal targets. "Minor UX regression, not a correctness or data-integrity regression."
  **Fixed** in `7f87793`: an unknown target is now refused by argparse, naming the legal ones.
- **Note** — `phase_ids()` and `document_codes()` return empty sets when the backlog file or the
  document root is missing, where the source assumed they existed. "A deliberate, correct
  adaptation … not a regression." **Accepted.**
- "No other discrepancies found": `scripts/ideas.py` against `src/db/ideas.py` and `scripts/idea.py`
  against `tools/append_idea.py` are logic-identical with comments stripped; both schemas are
  structurally identical to the source with descriptions stripped; no R02 leak found; the triage
  skill and agent issue no link or promotion command; every script runs from a copy against a
  temporary root; an empty log renders to exactly the scaffold's seeded view. Plugin suite: 177
  passed.
- Acceptance verdicts: 1 **Met**, 2 **Met**, 3 **Met**, 4 **Met**, 5 **Met**.
- Not checked by that reviewer: `claude plugin validate --strict`, the private-content check and the
  governance check; a line-by-line comparison of `scripts/render_ideas.py` with
  `tools/generate_ideas_md.py` and of `scripts/checks/ideas.py` with the source priority and
  staleness code; `docs/vocabulary.md`'s prose (it relied on the drift test); this session record;
  the `backlog.yaml` and `catalog.md` diff.

A second review was dispatched for those items. It stalled for about five hours with no report and
was stopped; a restart was then stopped too, when the owner directed the session to drop the
remaining review and move on. The three verification commands were rerun by this session instead,
after `7f87793`:

```text
$ claude plugin validate plugins/idea-realization --strict
✔ Validation passed

$ uv run python tools/check_no_private_content.py
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (956 tracked files, 0 identifiers checked)

$ uv run python -m src.governance
Governance OK: 43 systems, 363 documents, 32 memories, 318 backlog phases
```

**Not independently reviewed, by the owner's direction:** the render and check comparisons with
their sources, the vocabulary document's prose, this record's claims, and the backlog and catalog
diff. The tests cover them (the render, staleness, priority and vocabulary tests pass), but no
reviewer read them.

## Decisions

- **Claim and assignment.** The Session Manager assigned the phase; the owner approved the claim in
  this session. Agent id `agent-standby-builder`.
- **Where R23's test lives (owner).** REQ-031 R23 asks for the plugin schema's enums to equal this
  repository's at the commit `phase-idg-01` landed; R21 bars the plugin suite from reading this
  repository and R02 bars commit hashes in the plugin. The owner ruled the test carries the source
  sets as literals, copied from the source schema at that commit, with no repository-side test.
- **Widened deliverables (Session Manager turn).** `schemas/idea-priority.schema.json`, which the
  `phase-plug-01` scaffold already seeds and no phase declared, and `test/test_scripts_portable.py`,
  whose fixture now copies `schemas/` because the ideas check reads the plugin's own schemas.
- **Schema descriptions rewritten, structure kept.** The source schema's descriptions cite this
  repository's documents, ideas and dates, which R02 forbids; only `description` strings changed,
  and a comparison with descriptions stripped shows the two schemas identical.
- **The rendered view's header is the scaffold's seed text.** So an empty log renders to exactly
  the file the scaffold creates, and a freshly scaffolded repository passes `check`.
- **Rendering of the new event data.** Document links render their code, and the view shows the
  latest classification and any `closes_with` pointers, so `000465` (generate_ideas_md.py does not
  render document links, classification or closes_with) is not repeated in the plugin. PLAN-048.02's
  open question — whether render shows the axis values — answered yes.
- **Document codes resolve by front matter.** Pointers and document links check the `code:` field
  of Markdown files under the document root, so the writer does not depend on the code register
  `phase-plug-05` is defining in parallel.
- **The owner author stays `repository-owner`**, as in the source; making it a plugin option would
  have meant editing `plugin.json`, outside this phase.
- **Triage is one idea per invocation**, per REQ-031 R12's "is not" clause, unlike the source
  workflow's loop over every open idea.
- **Additions to the writer:** read-only `list` and `show` commands, replacing the source skills'
  inline `src` imports; `--file` for annotation text, so a finding never passes through a shell
  argument; and the writer prints each event's `eid`, which the source's help said it did and it
  did not.
- **The remaining review was dropped (owner).** After the second review stalled, the owner
  directed the session to drop it and move on; `## Review` lists what that left unreviewed.
- **Test porting was delegated** to a general-purpose agent with the R02 rules spelled out; its list
  of dropped source tests (committed-file, DuckDB projection and repository-tooling tests) is the
  one PLAN-048.02 step 2 called for.

## Corrections

- The triage skill first wrote `<plugin root>` where `${CLAUDE_PLUGIN_ROOT}` belonged; the plugin's
  skill test caught it and it was fixed before the first commit.
- The first plugin-suite failure after the scripts landed was blamed on the new check needing
  schemas; the cause was `phase-plug-01`'s portability fixture not copying `schemas/`, fixed through
  the widen above.
- Review 1's should-fix: the port had dropped the source's argparse `choices` on `status`'s target;
  restored in `7f87793`.

## Left undone

- The merge onto `dev` and the completion edit, which wait for the owner's approval.
- `000463` (idea consumers hard-code the five old statuses) and `000464` (the DuckDB projection
  lacks the new columns) stay with this repository: the plugin has no projection and no
  consumer that hard-codes statuses.
