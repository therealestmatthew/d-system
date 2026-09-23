---
schema_version: 1
id: doc-ops-review
code: OPS-024
title: Review staged captures and promote them into the source of truth
kind: operation
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-capture, sys-portfolio]
depends_on: [doc-capture-routing, doc-capture-requirements, doc-ops-capture]
---

# Review staged captures and promote them into the source of truth

## Trigger

Use when staged records are waiting in `_capture/staging/` and the owner is ready to decide
on them. This is the only way a captured record becomes real: nothing else in the capture
pipeline writes to the data root (REQ-002 R12). Every subcommand is one owner decision and
runs without prompting, so an agent can carry out the owner's decisions in a conversation.
An agent does not run `promote`, `create`, `discard` or `correct` on its own judgement.

## Command

```bash
# See what is waiting: clean ids, then every flagged or held item, highest stakes first.
uv run python tools/review.py show

# Promote every clean record, and nothing else (REQ-002 R13).
uv run python tools/review.py promote --clean

# Promote one flagged or held record, stating any value the owner decides.
uv run python tools/review.py promote staged-20260923T101500Z-a1b2c3 --set due_date=2026-10-01
uv run python tools/review.py promote staged-20260923T101500Z-a1b2c3 --keep-names

# The identity call for a held person or project.
uv run python tools/review.py create staged-20260923T101500Z-d4e5f6 --set id=sam-lee

# Drop a staged record without promoting it.
uv run python tools/review.py discard staged-20260923T101500Z-a1b2c3

# Correct one field of a promoted record (REQ-002 R15).
uv run python tools/review.py correct commitment c-4 due_date 2026-10-08 --reason "moved"
```

`--set field=value` reads the value as JSON when it parses (`true`, `3`, `["a"]`, `null`) and
as a plain string otherwise. A value the owner states is no longer counted as assumed.
`--keep-names` confirms that names in `participant_names` or `decided_by_names` stay as plain
text rather than becoming person records.

## Expected result

- **show** writes nothing. For each flagged or held item it prints the raw capture, the
  proposed record, and each assumed field with its level, supporting quote and reason
  (REQ-002 R14). A new tag prints as an `ALERT` and stays held. A new tag category prints as a
  proposal that this tool cannot approve (idea `000337` covers the approval path). A clean
  record that promotion would leave staged is listed separately, with the reason.
- **promote** writes each record to `<data root>/<type>/<id>.json` with the next free id of
  its type, for example `c-5`. Promotion assigns every id itself: a proposal or `--set` that
  supplies one is refused, and an existing file is never overwritten. The data root is `D_SYSTEM_DATA_ROOT` when set, otherwise
  `_data/` (ADR-009). The record keeps a `capture` block naming its raw capture, the fields
  that were still assumed, and the promotion date. The staged record moves to
  `_capture/promoted/`.
- **create** writes a person or project to the data root. The staged record moves to
  `_capture/promoted/`. A tag is refused and stays held: the owner ruled that capture-derived
  tags belong under the private data root (idea `000343`), and nothing reads a private tag
  file yet. Nothing here writes the tracked `_data/tags.json`.
- **discard** moves the staged record to `_capture/discarded/`.
- **correct** edits the record in place and appends one line to
  `<data root>/corrections.jsonl`, naming the record, the field, the previous value, the new
  value and the date (`schemas/correction.schema.json`). The entry is written and synced
  before the record changes, and the log is never rewritten, so every earlier value stays
  readable. A correction may not name a person, project or tag that does not exist. The raw
  capture is never touched.

## Failure and recovery

A refused action prints `error: …`, exits 1 and writes nothing. The common causes:

- A staged record that does not validate against its entity schema, for example a task with
  no `status`, or a `note`, which has no entity schema. Nothing is filled in by default.
  `promote --clean` reports each such record as `left staged` with the reason and carries on
  with the rest. State the missing values with `promote <id> --set …`, or discard the record.
- A record naming a person, project or tag that does not exist. Create the identity first,
  or point the field at an existing one with `--set`.
- `create` on a held record whose proposal has no `id`: give one with `--set id=…`.
- A correction to `id` or `capture`, one that would leave the record invalid, or one that
  changes nothing.

<!-- generated:tool-reference:start -->

### Reference: `tools/review.py`

Review staged captures and promote them into the source of truth — REQ-002 R11-R15.

Every subcommand is one owner decision, taken non-interactively so an agent can carry it
out in a conversation. Nothing prompts: an ambiguous or refused action exits non-zero and
says why, and writes nothing.

Usage:
    uv run python tools/review.py show
    uv run python tools/review.py promote --clean
    uv run python tools/review.py promote staged-... --set due_date=2026-10-01
    uv run python tools/review.py promote staged-... --keep-names
    uv run python tools/review.py create staged-... --set id=sam-lee
    uv run python tools/review.py discard staged-...
    uv run python tools/review.py correct commitment c-4 due_date 2026-10-08 --reason "moved"

`--set field=value` states a field value; the value is read as JSON when it parses
(`true`, `3`, `["a"]`, `null`) and as a plain string otherwise. A value the owner states is
the owner's word and no longer counts as assumed. `--keep-names` confirms that names in
`participant_names` or `decided_by_names` stay as plain text. Promotion writes to the data
root (`D_SYSTEM_DATA_ROOT`, else `_data/`); see `docs/08-governance/OPS-024-review.md`.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `staged_id` | promote: the staged record to promote |  |  |  |
| `--clean` | promote: every clean record |  |  |  |
| `--set` | promote: state a field value |  |  |  |
| `--keep-names` | promote: keep *_names values as plain text |  |  |  |
| `staged_id` | create: the held person or project record |  |  |  |
| `--set` | create: state a field value |  |  |  |
| `staged_id` | discard: the staged record to drop |  |  |  |
| `record_type` | correct: the record's schema, e.g. commitment |  |  |  |
| `record_id` | correct: the record's id, e.g. c-4 |  |  |  |
| `field` | correct: the field to change |  |  |  |
| `value` | correct: the new value, read as JSON when it parses |  |  |  |
| `--reason` | correct: why, recorded in the log |  |  |  |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
