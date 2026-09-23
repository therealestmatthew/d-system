---
schema_version: 1
id: doc-session-capture-review-promotion
code: SESS-2026-09-23-02
title: Capture review and promotion into the source of truth
kind: session
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-capture, sys-portfolio]
depends_on: [doc-capture-build]
---

# Capture review and promotion into the source of truth

## Phase

`phase-cap-06` — Build review and promotion into the source of truth.

## Verification

Run in the worktree `/code/d-system-worktrees/phase-cap-06` after rebasing onto `dev` at `3f2b7b0`,
with the first review's fixes applied (`dddebf2`):

```
$ uv run pytest test/test_capture_review.py
12 passed, 1 warning
$ uv run pytest test/test_capture_promotion.py
37 passed, 1 warning
$ uv run python -m src.governance
Governance OK: 35 systems, 333 documents, 31 memories, 293 backlog phases
$ uv run pytest -q
954 passed, 1 warning
```

ruff and mypy are clean on every file this phase adds or changes. Before the fixes, a
mutation check made bulk promotion take every route, and
`test_bulk_promotion_moves_only_clean_records` failed. Reverting the change made it pass.

## Acceptance

- `Bulk promotion moves only clean records; a mixed batch leaves flagged and held staged.` —
  **Met**, by the author's check after the fixes.
  - `test_bulk_promotion_moves_only_clean_records` covers the mixed batch.
  - The review's defects beside it are fixed, and each has a test: a supplied id overwriting a
    record, duplicate ids losing one, a path outside the data root, and a failure mid-batch.
- `No capture path other than promotion writes to _data/.` — **Met.** "`_data/`" means the data
  root, per `ADR-009`. The R12 test now also covers `discard`. Nothing writes the tracked
  `_data/tags.json`.
- `A correction records the field, the previous value and the new one, and the prior value
  stays readable.` — **Met.**
  - The entry is appended and fsynced before the record changes.
  - `test_a_correction_that_cannot_be_logged_leaves_the_record_unchanged` covers a failed log
    write.
  - An absent previous value is marked `previous_absent`.

No review has yet examined the fixes. See `## Where this stands`.

## Backlog

`status: active`, held by `agent-builder-a`. `next_action`: the first review's findings are
fixed in `dddebf2`. Run an independent review of the fixes, then send READY per `GOV-017`.

## Unresolved

- No review has run on the fixes in `dddebf2`.
- On `dev`, CI's `ruff check src/ test/` and `mypy src/` failed in files outside this phase when
  last checked. This was reported to the Session Manager on 2026-09-23.

## Where this stands

Paused on 2026-09-23 at the Session Manager's overnight safe-point request. The claim is kept.
Everything is committed and pushed on `agent/phase-cap-06`.

**Done.** The phase is built:

- `src/capture/promote.py`
- `src/capture/review.py`
- `tools/review.py`
- `schemas/correction.schema.json`
- `docs/08-governance/OPS-024-review.md`
- both test files

One independent review has run, and its defects are fixed.

**Next on resume.**

1. Rebase onto `dev`. Re-run governance and pytest in the worktree, one pytest run at a time.
2. Dispatch a fresh, non-fork review of the fixes in `dddebf2`, against the defect table below.
   Fix what it finds.
3. Record that review here, then send READY with the post-rebase output.

## Review

### First review

An independent general-purpose sub-agent reviewed `dev...HEAD` before any fixes. It found
acceptance 1 met as worded, with a blocking defect beside it; acceptance 2 met; and acceptance
3 met in the normal path but not guaranteed on failure. It recommended not completing until
defects 1–3 were fixed.

| # | Finding | Disposition |
|---|---|---|
| 1 | A supplied `id` in a proposal or `--set` overwrote an existing record | Fixed: promotion assigns every id and refuses a supplied one. Records are created with `os.link`, which refuses an existing file |
| 2 | Two clean records with the same supplied id lost one | Fixed by 1. Test added |
| 3 | An unanchored id pattern let a record be written outside the data root | Fixed: every target is checked to be inside the data root. The unanchored schema patterns are not this phase's files and are left as they are |
| 4 | A correction wrote the record before the log, so a failed log write lost the previous value | Fixed: the log is appended and fsynced first, and the record is written atomically |
| 5 | A failure after the data write left the record staged; re-running duplicated it | Fixed: the archive entry is written first, and an interrupted promotion is finished rather than repeated. One record failing now skips only that record |
| 6 | A malformed `--set` or an OSError gave a traceback | Fixed: the CLI reports `PromotionError`, `StructuringError` and `OSError` as `error:` with exit 1 |
| 7 | A correction could set an unknown person, project or tag | Fixed: a correction is checked for unresolved references like a promotion |
| 8 | Review called records "ready" that bulk promotion would leave staged | Fixed: review runs promotion's own check and lists those records separately, with the reason |
| 9 | A null `previous` did not distinguish absent from null | Fixed: `previous_absent: true` is added to the entry and the schema |
| 10 | A tag from a capture was written to the tracked `_data/tags.json` | Owner ruling (below): it is refused and stays held |
| 11 | Minor items | Accepted: `assumed_fields` records promotion time and is not changed by corrections; tags are not correctable, since nothing here writes tags; `create` does not check references inside a new person or project; a held medium-stakes record sorts by its type's stakes; with `D_SYSTEM_DATA_ROOT` unset, promotion writes the fictional `_data/`, as `ADR-009` defines |

## Decisions

- **Corrections** go to an append-only `corrections.jsonl` in the data root, validated by the
  new `schemas/correction.schema.json`. Entity schemas are unchanged (owner). The lock is that
  one file, not all of `schemas/` (owner).
- **No default values** are filled in. A clean record that fails its entity schema stays
  staged, with the reason (owner).
- **New tag categories** stay held. Review presents them as proposals only (owner). Idea
  `000337` covers approving one. A later owner ruling, relayed by Ideation, moves categories
  out of the schema enum and into data.
- **`OPS-024-review.md`** was added to the deliverables, because every `tools/*.py` ships with
  an OPS document (owner).
- **Capture-derived tags** go under the private data root, not the tracked `_data/tags.json`.
  The owner ruled this directly to Ideation (idea `000343`) and confirmed it in this session.
  This replaces an earlier answer in this session: tracked, with a warning. For now `create`
  refuses a tag and it stays held. A follow-up phase builds the private tag file and teaches
  structuring, the validator and the rebuild to read it.
- **Promotion writes to the data root** (`D_SYSTEM_DATA_ROOT`, else `_data/`), per `ADR-009`.
  Promoted and discarded staged records move to `_capture/promoted/` and `_capture/discarded/`.

## Corrections

- Running `ruff format` over all of `src/capture/` reformatted `raw.py`, which is not this
  phase's file. The change was reverted before it was committed.
- The first build trusted a supplied `id` and wrote the record before the correction log. The
  review caught both (defects 1–5).

## Left undone

- The review of the fixes, and READY (see `## Where this stands`).
- Ideas sent to Ideation for work outside this phase:
  - `000341`: the `sys-capture` registry paths.
  - `000342`: REQ-002's status note.
  - `000343`: the private tag file, with the owner's ruling recorded on it.
