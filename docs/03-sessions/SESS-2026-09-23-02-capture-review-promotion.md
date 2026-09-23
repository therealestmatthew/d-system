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

Run in the worktree `/code/d-system-worktrees/phase-cap-06` on `dev` at `3f2b7b0`, after two
fix cycles on the second and third reviews (`7963ada` and the commit that adds this text). The
figures below are from before those cycles; the READY message to the Session Manager carries the
final run.

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

Acceptance 2 and 3 were found not met by the second and third reviews and fixed; see
`## Review`.

## Backlog

`status: active`, held by `agent-builder-a`. `next_action`: READY per `GOV-017`; the fourth
review found no HIGH or MEDIUM finding.

## Unresolved

- The fourth review's five LOW findings, accepted (see `### Fourth review`).

## Where this stands

Resumed on 2026-09-23 in the overnight sprint (Session 1 - Builder A, item B1). The claim was
already held and is pre-approved by the owner's overnight authority. Three further reviews ran,
with the two fix cycles the authority allows between them. The last found no HIGH or MEDIUM.

**Done.** The phase is built:

- `src/capture/promote.py`
- `src/capture/review.py`
- `tools/review.py`
- `schemas/correction.schema.json`
- `docs/08-governance/OPS-024-review.md`
- both test files

One independent review has run, and its defects are fixed.

**Next.** READY, then on `GRANTED merge` the ff-merge and the completion edit on `dev`.

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

### Second review

A fresh, non-fork general-purpose sub-agent reviewed the whole phase, focused on `dddebf2`. It
found first-review defects 1, 2, 7, 8, 9 and 10 fixed, and 3, 4, 5 and 6 partly fixed.
Fix cycle 1 is `7963ada`. Each new test fails against the code before it.

| # | Sev | Finding | Disposition |
|---|---|---|---|
| A | HIGH | Recovery trusted any file at the archived target, so a record later promoted into the same id was taken for the interrupted one, and the staged record was lost. A moved data root misdirected the stored absolute target | Partly fixed in cycle 1 (match on id and `capture_id`; target rebuilt under the current data root). Completed in cycle 2, see the third review |
| B | MEDIUM | `correct` built a path from an unchecked record id and could edit outside the data root | Fixed: the id must be a plain record id, and the target must be inside the data root |
| C | MEDIUM | An unchecked staged id let `discard` delete a data-root record | Partly fixed in cycle 1 (the argument is checked). Completed in cycle 2 |
| D | MEDIUM | A torn last line in `corrections.jsonl` swallowed the next entry, and `corrections()` failed for every record | Partly fixed in cycle 1 (fresh line before an append; an unparseable line is skipped). Completed in cycle 2 |
| E | LOW | `create_identity` writes the record before its archive entry and has no recovery | Accepted: a failed archive write leaves the held record staged and the identity created; the owner can `discard` it. Nothing is lost |
| F | LOW | A failed record write after the log append leaves an entry that was never applied | Accepted: the log is written first on purpose (defect 4); an extra entry is visible, a lost previous value would not be |
| G | LOW | A corrupt file or a missing field aborted a batch, and the CLI gave a traceback | Fixed: such a record is skipped, and the CLI reports it as an error |
| H | LOW | If removing the staged copy fails after the record is created, the record is reported as left staged | Accepted: the next run settles it through recovery |
| I | LOW | A filesystem without hard links can never promote | Accepted: nothing is left behind, and the repository is on ext4 |
| J | LOW | No test covered traversal or the id collision | Fixed: tests added |

### Third review

A fresh, non-fork general-purpose sub-agent reviewed `7963ada`. It confirmed B fixed and every
new test failing against the earlier code. Fix cycle 2 is the commit that adds this section.

| Sev | Finding | Disposition |
|---|---|---|
| HIGH | Records staged from one capture share a `capture_id`, so a sibling promoted into the pending id still passed the check (A) | Fixed: every archive entry's `record_id` is reserved when ids are assigned, so a pending id is never given to another record. Storing the staged id in the record was not used: `evidence.schema.json`'s `capture_source` forbids extra fields and is not this phase's file |
| MEDIUM | Paths were built from the id inside the staged file, which was never checked, so a bad staged file let `promote_clean` delete, or `discard` overwrite, a data-root record (C) | Fixed: a staged file's id must be a staged id equal to its filename, checked on every read. A bad file makes review and bulk promotion refuse with an error naming the file, before anything is written |
| MEDIUM | A tear inside a multi-byte character raised `UnicodeDecodeError` before the per-line check (D) | Fixed: the log is read as bytes and each line decoded inside the check |
| LOW | One corrupt staged file stops the whole batch at load | Accepted: nothing is written, and the error names the file for the owner |
| LOW | A crafted archive entry raised `TypeError` or `AttributeError` | Fixed: an entry that is not a well-formed promotion entry is dropped and the record is promoted afresh |
| LOW | Skipping unparseable lines also hides corruption mid-file | Accepted: after the fresh-line fix a torn entry can legitimately sit mid-file, and a torn entry was never applied, because the log is written before the record |
| LOW | `$` matched before a trailing newline | Fixed for `promote.py`'s own patterns, which use `fullmatch`. An id `create_identity` accepts through the entity schema can still end in a newline; see the fourth review |
| LOW | `RECORD_ID` rejected a leading hyphen that person and project ids allow | Fixed: `RECORD_ID` is now `[a-z0-9-]+`, matching those schemas. Ids the numbered schemas allow only because their patterns are unanchored (`c-1_x`) stay refused |

### Fourth review

A fresh, non-fork general-purpose sub-agent reviewed `ba30f49`, the tip after the second fix
cycle, rebased onto `dev` at `be1d78e`. It found A, C and D fixed, all three acceptance
criteria met, and **no HIGH or MEDIUM finding**. Each new test fails against the earlier code.
Its five LOW findings are accepted rather than fixed, because a fix would be a third fix
cycle, which the overnight authority treats as PARK. Each is a follow-up candidate.

| Finding | Why it is accepted |
|---|---|
| No test covers the check that a staged file's id equals its filename; both test cases are refused earlier by the id pattern | The check is present and correct; only its regression test is missing |
| `create_identity` checks the new id only through the entity schema, whose `$` lets `"sam\n"` through, creating `people/sam\n.json` | The file stays inside the data root and overwrites nothing; it needs the owner to type a newline into an id |
| A crash in `create_identity` after its archive entry and before the staged copy is removed, then `promote_one` on that record, drops the archive entry | Nothing is overwritten or lost from the data root; a second `create` refuses because the file exists, and the owner can `discard` |
| `discard` does not check `promoted/`, so discarding a record whose staged copy survived a promotion (finding H) leaves both archive entries | The data-root record is correct; only the archive holds two entries for one staged record |
| If `_create_json` fails after `os.link` succeeds (an interrupt, or failing to remove the temporary file), the archive entry is removed and the next run promotes the record again under a new id | A duplicate, not a loss, in a window of two system calls |

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
- The first test written for finding A used a made-up archive target, so it passed against
  the unfixed code. The mutation check caught it, and the test now uses the real path.

## Left undone

- The fourth review's LOW findings, as follow-up candidates (see `### Fourth review`).
- Ideas sent to Ideation for work outside this phase:
  - `000341`: the `sys-capture` registry paths.
  - `000342`: REQ-002's status note.
  - `000343`: the private tag file, with the owner's ruling recorded on it.
