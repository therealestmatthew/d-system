---
schema_version: 1
id: doc-session-capture-intake
code: SESS-2026-09-08-05
title: Build raw intake through the CLI and inbox
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-capture]
depends_on: [doc-capture-build]
---

# Build raw intake through the CLI and inbox

## Phase

`phase-cap-04` — Build raw intake through the CLI and inbox.

## Verification

```
$ uv run pytest test/test_capture_intake.py
19 passed, 2 warnings
```

```
$ uv run ruff check src/ test/ tools/
All checks passed!
```

Also ran, since the phase touched `docs/06-requirements/REQ-002-capture-requirements.md` and
`docs/08-governance/systems.yaml` alongside its own deliverables:

```
$ uv run mypy src/
Success: no issues found in 14 source files
$ uv run python -m src.governance
Governance OK: 16 systems, 88 documents, 13 memories, 97 backlog phases
$ uv run pytest
365 passed, 2 warnings
```

Also ran the actual documented command from `docs/08-governance/OPS-008-capture.md` by hand, once,
against the real (gitignored) `_capture/` tree in this worktree, then removed the resulting files:

```
$ uv run python tools/capture.py "Call John about the Q3 deliverable by Friday."
captured raw-20260908T100014Z-9e7b08
$ echo "A pasted note from a meeting." > _capture/inbox/meeting-note.txt
$ uv run python tools/capture.py --inbox
captured raw-20260908T100019Z-d72433 from meeting-note.txt
$ uv run python tools/capture.py --inbox
inbox empty — nothing to capture
```

Both raw files matched `schemas/capture.schema.json` and held their input byte-identical; the inbox
file moved to `_capture/inbox/processed/meeting-note.txt`; the second `--inbox` run confirmed no
recapture. `git status --short` before and after this manual run was identical (clean).

## Acceptance

- Captured text is stored byte-identical to the input through both paths. — Met:
  `test_write_raw_capture_stores_content_byte_identical` and
  `test_write_raw_capture_preserves_special_characters_unchanged` cover the CLI/writer path;
  `test_scan_inbox_converts_every_file_and_records_relative_source_path` covers the inbox path.
  Confirmed again by the manual run above against the real schema and real files.
- No code path in this phase edits or deletes an existing raw record. — Met:
  `test_two_captures_never_collide_and_never_rewrite_each_other` writes two records and asserts the
  first file's bytes are unchanged after the second write; `write_raw_capture` refuses to overwrite
  an existing id (`raw capture id collision`) rather than silently replacing it.
- Nothing is written to `_data/` or to staging. — Met:
  `test_write_raw_capture_touches_only_the_raw_directory` asserts the only path created under a
  fresh root is `raw/`, and neither `write_raw_capture` nor `scan_inbox` in `src/capture/raw.py`
  references `_data/` or `_capture/staging/` anywhere. The manual run's `git status --short` stayed
  empty before and after, and `_capture/` never appeared even as an ignored path.

## Backlog

- `phase-cap-04` status: `active` (owner runs `/session-close` to move it to `complete`).
- `next_action`: All three acceptance conditions are met and the three declared deliverables exist,
  plus the OPS documentation R5 requires. Nothing further is planned for this phase; it is ready for
  `/session-close` review.
- `completion_evidence`: `src/capture/raw.py`, `tools/capture.py`, `test/test_capture_intake.py`,
  `docs/08-governance/OPS-008-capture.md`.
- `result`: Built `src/capture/raw.py` (`write_raw_capture`, the only writer for `_capture/raw/`, and
  `scan_inbox`, shared by both intake channels) and `tools/capture.py` (the CLI: a single positional
  text argument or stdin, plus `--inbox` to drain the inbox directory). Both write raw records only —
  no structuring, no evidence, no routing — validated against `schemas/capture.schema.json` before
  every write, so a rejected capture costs nothing. A converted inbox file moves to
  `_capture/inbox/processed/` so a later scan never recaptures it; a file that fails to convert
  (empty content, unreadable bytes) is left in place and the scan continues with the rest, so one bad
  file never blocks its neighbours. Added 19 tests in `test/test_capture_intake.py`. Also added
  `docs/08-governance/OPS-008-capture.md` (a new `OPS-*` document, per `AGENTS.md`'s
  tool-documentation pairing convention — a new `tools/*.py` ships with its own paired doc, enforced
  by `test/test_tool_docs.py`) and corrected `REQ-002` R5's verification pointer, which had named
  `OPS-001-operations.md` before that convention existed; also updated REQ-002's "nothing here is
  implemented yet" line, now stale for R1/R2/R5. Updated `sys-capture` in `systems.yaml` with the new
  paths and a description reflecting that raw intake exists but structuring/routing/promotion do not,
  and regenerated `catalog.md`.

## Unresolved

None for this phase's own scope. `phase-cap-05` (structuring and routing) is the next phase in
`PLAN-009` and depends on this one; nothing here blocks it beyond what the plan already expects.

## Review

Independent sub-agent review, run fresh against `the commit “Claim phase-cap-04”..HEAD` (the three commits this session
produced: the commit “Build raw-only CLI and inbox intake (phase-cap-04)”, the commit “Document capture intake and fix REQ-002's stale pointers”, the commit “Checkpoint phase-cap-04: acceptance met, ready for session-close”), with the reviewer running every verification command
itself rather than trusting this record:

> ### Acceptance condition 1 — "Captured text is stored byte-identical to the input through both paths"
>
> **Met.** Evidence:
> - `write_raw_capture` (`src/capture/raw.py:63-87`) never transforms `content` — it's placed
>   directly into the record dict and serialized with `json.dumps(record, ensure_ascii=False, ...)`,
>   which does not alter string content.
> - Tests: `test_write_raw_capture_stores_content_byte_identical`,
>   `test_write_raw_capture_preserves_special_characters_unchanged`,
>   `test_scan_inbox_converts_every_file_and_records_relative_source_path`,
>   `test_cli_reads_dangerous_text_from_stdin_unchanged` all pass (19/19).
> - I independently verified with harder inputs than the test suite covers: leading/trailing
>   whitespace, unicode/emoji, embedded newlines+tabs, and a whitespace-only single-space string —
>   all round-tripped byte-identical through `write_raw_capture` directly. I also ran the actual CLI
>   (`uv run python tools/capture.py`) via both stdin and a positional argument, and the inbox path
>   (`--inbox`) with the same tricky whitespace input, against the real gitignored `_capture/` tree —
>   all three stored the content unchanged (verified by `repr()` diff against source).
> - One caveat, not a violation: the CLI itself refuses whitespace-only input at the entry point
>   (`if not content.strip(): error`, `tools/capture.py:69`) before it ever reaches the writer — so
>   it's rejected, never corrupted. If `write_raw_capture` is called directly (as `scan_inbox` does,
>   and as tests do) with whitespace-only content, it passes through unchanged (schema only requires
>   `minLength: 1`).
>
> ### Acceptance condition 2 — "No code path in this phase edits or deletes an existing raw record"
>
> **Met.** Evidence:
> - `write_raw_capture` (`src/capture/raw.py:84-85`) checks `if path.exists(): raise CaptureError(...)`
>   before ever calling `write_text` — this is a hard refusal, not a silent overwrite.
> - Nowhere in `src/capture/raw.py` or `tools/capture.py` does any code open an existing file under
>   `_capture/raw/` for writing, or call `.unlink()`/`os.remove()` on one. `scan_inbox` only moves
>   (`path.rename`) *inbox* files to `processed/` and appends new files under `raw_dir` — it never
>   touches an existing raw record.
> - I went beyond the existing test suite (which only shows two *different* ids never collide) and
>   forced a genuine id collision by monkeypatching `_new_id` to return the same id twice: the second
>   write was refused (`CaptureError: raw capture id collision`), the first file's bytes were
>   byte-for-byte unchanged afterward, and the directory still held exactly one record.
>
> ### Acceptance condition 3 — "Nothing is written to _data/ or to staging"
>
> **Met.** Evidence:
> - `grep -n "_data\|staging" src/capture/raw.py tools/capture.py` returns no matches — neither path
>   is referenced anywhere in this phase's code.
> - `test_write_raw_capture_touches_only_the_raw_directory` passes, asserting only `raw/` is created
>   under a fresh root.
> - My manual end-to-end run against the real repo (`git status --short -- _data/` before/after)
>   showed no changes to the tracked `_data/` tree; `_capture/` itself is fully gitignored (confirmed:
>   `git status --short` stayed clean throughout, matching the session record's claim).
>
> ### Verification commands (rerun independently)
>
> ```
> $ uv run pytest test/test_capture_intake.py
> 19 passed, 2 warnings
> $ uv run ruff check src/ test/ tools/
> All checks passed!
> ```
> Both match the session record exactly. Also reran the extras the record claims:
> `uv run mypy src/` → clean (14 files), `uv run python -m src.governance` → OK, `uv run pytest`
> (full suite) → 365 passed, matching the record.
>
> ### Scope check on the extra deliverables
>
> Not scope creep. `AGENTS.md` (line 122-124) mandates that any new file under `tools/` ships with a
> paired `OPS-*` document, and this is machine-enforced:
> `test/test_tool_docs.py::test_every_existing_tool_is_paired_with_a_document` would fail without
> `docs/08-governance/OPS-008-capture.md` — I reran that file alone (7 passed) to confirm it's a
> real, currently-passing gate, not an aspirational one. The `REQ-002` pointer fix (from a
> nonexistent `OPS-001-operations.md` reference to the real `OPS-008-capture.md`) and its "nothing
> implemented" line update are necessary corollaries of that doc landing, not unrelated additions.
> `systems.yaml`, `backlog.yaml`, and `catalog.md` updates are the routine bookkeeping this repo's
> governance system requires when new paths/docs are added — consistent with what phase-cap-03's
> session did per the commit log.
>
> ### One discrepancy worth flagging (minor, non-blocking)
>
> The session record's governance-check transcript shows `Governance OK: 16 systems, 88 documents,
> ...`, but rerunning `uv run python -m src.governance` now on the final committed state
> (`the commit “Claim phase-cap-04”..“Checkpoint phase-cap-04: acceptance met, ready for session-close”`) gives **89 documents** — matching `catalog.md`'s own footer count ("89
> documents"). This is almost certainly just the record capturing that command's output before the
> final commit (the commit “Checkpoint phase-cap-04: acceptance met, ready for session-close”, the checkpoint commit) landed, rather than a real inconsistency in the
> current state — the committed `catalog.md` and a fresh governance run agree with each other right
> now. Not a blocker, but the record's pasted transcript doesn't reflect the final state exactly.
>
> ### Test suite quality
>
> `test/test_capture_intake.py`'s 19 tests genuinely exercise the acceptance conditions rather than
> just validating fixtures: they check actual byte-equality of stored content against source strings
> (not just schema validity), force a real second-write to prove the first file's bytes don't change,
> assert the *only* directory created is `raw/`, and cover the CLI entry point end-to-end via
> `capture_cli.main(...)` with monkeypatched paths rather than only testing the library function.
>
> ### Overall verdict
>
> All three acceptance conditions: **Met**, independently confirmed by code inspection, rerunning
> both verification commands, running the full suite/mypy/governance check, and original manual
> testing (tricky-input byte-identity, forced collision, real end-to-end CLI/inbox run against the
> gitignored `_capture/` tree) that went beyond what the session record or existing tests cover. No
> discrepancies found beyond the minor stale document-count in the record's pasted transcript, and no
> scope creep — the extra doc/registry edits are required by existing enforced conventions.

(Note added after the review, not part of it: the "88 vs 89 documents" point above is the same
sequencing artifact phase-cap-03's own session record noted — the `## Verification` section's
pasted transcript was captured before the final checkpoint commit landed. `catalog.md`'s committed
footer and a fresh `governance` run both already agree on 89.)

## Decisions

- **A dedicated `OPS-008-capture.md`, not a new section in `OPS-001-operations.md`.** REQ-002 R5's
  verification text named `OPS-001-operations.md` literally, but `AGENTS.md` requires any new
  `tools/*.py` to ship with its own paired `OPS-*` document, enforced by `test_tool_docs.py`. My
  first attempt added a section to OPS-001; `test_every_existing_tool_is_paired_with_a_document`
  failed, which is what surfaced the actual convention. Reverted that addition, created OPS-008
  instead, and corrected REQ-002 R5's now-stale pointer and its "nothing implemented yet" line in
  the same change rather than leaving a document pointing at the wrong file.
- **Inbox dedup: move converted files to `_capture/inbox/processed/`.** Put to the owner via
  `AskUserQuestion` before writing any inbox code, since ADR-007 doesn't specify a mechanism and it
  changes visible behavior (files disappearing from the inbox as they're processed). The owner asked
  for a plain-language explanation of what the inbox channel actually does before confirming; gave
  that, then proceeded with the recommended option over deleting the source file or tracking a
  separate sidecar index.
- **Add the OPS documentation now, not defer it.** Also put to the owner via `AskUserQuestion`,
  since the phase's declared deliverables didn't include it but REQ-002 R5's verification depends on
  it existing. Owner chose to add it in this phase rather than leave R5 unverifiable.
- **Worktree required and used.** `agent-gov03` held an active claim on `phase-gov-03` for the
  duration of this session, and this phase touches `src/`, `tools/` and `test/`, so `AGENTS.md`
  required an isolated worktree (`../d-system-worktrees/phase-cap-04`) rather than working directly
  on `dev`. All verification before merge ran there; the fast-forward merge onto `dev` introduced no
  new commits.

## Corrections

- A YAML parse error broke `governance` after the first backlog checkpoint edit: an unquoted colon
  inside the `result:` field's prose ("the CLI: a single...") made the YAML parser read it as a
  nested mapping. Caught immediately by governance's own line/column error; fixed by rewording to
  avoid the colon rather than quoting the whole block.
- **Two separate incidents of a paused "agent-gemini" session writing directly into this shared
  primary checkout**, bypassing the worktree isolation `AGENTS.md` requires whenever a peer holds an
  active claim:
  1. Two untracked files (`docs/08-governance/GOV-007-repo-orientation.md`, `GEMINI.md`) appeared
     mid-session and broke the full suite's catalog-staleness check
     (`test_committed_catalog_matches_regenerated_output`), since a live filesystem scan for
     `--catalog` picks up untracked files regardless of git status. Neither file was declared in
     `phase-gov-03`'s own deliverables, and `GOV-007`'s content closely duplicated `CLAUDE.md`'s
     orientation section — the kind of duplicate bookkeeping `GOV-001` forbids, and arguably the
     scope creep that phase exists to catch. The owner chose, via `AskUserQuestion`, to move both
     into gitignored `_working/gemini-wip/` rather than delete them, so nothing is lost for that
     session to rework in a proper worktree later.
  2. Mid-`/session-close`, an uncommitted edit reappeared: a new backlog phase (`phase-agnt-01`)
     retroactively claiming the same two files, with an acceptance condition too vague for
     governance to accept (`'The files are created and governed.'`), again breaking governance and
     the full suite. The owner chose, via `AskUserQuestion`, to discard the uncommitted edit
     (`git checkout -- backlog.yaml`) since nothing had been committed. Neither incident touched
     `phase-cap-04`'s own commits; its own verification commands were rerun unchanged before and
     after each cleanup, confirming no interference with this phase's actual work.

## Left undone

- **`phase-cap-05`** (structuring, evidence scoring and routing) is the next phase in `PLAN-009` and
  depends on this one; nothing here blocks it beyond what the plan already expects.
- **The Gemini multi-agent orientation work** — the content that was `GOV-007-repo-orientation.md`
  and `GEMINI.md` — sits parked in `_working/gemini-wip/`, ungoverned and unclaimed by any phase.
  Whether and how to properly scope multi-agent orientation documentation is a decision for the
  owner; this session only stopped it from blocking the shared checkout, it did not resolve it.
