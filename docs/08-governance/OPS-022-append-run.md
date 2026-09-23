---
schema_version: 1
id: doc-ops-append-run
code: OPS-022
title: Append an event to the run ledger
kind: operation
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-realization]
depends_on: [doc-governance-operations]
---

# Append an event to the run ledger

## Trigger

Use whenever an orchestrator run needs to be opened, moved, or closed in `_data/runs.jsonl`.
This is the only sanctioned writer for the run ledger (PLAN-039.01 section 5) — it is an
append-only event log, the idea log's own pattern applied to orchestrator runs, so a
malformed line written any other way is permanent. `src.orchestrator.tick` is the ordinary
caller; this script is for a human's manual correction to the record.

## Command

```bash
uv run python tools/append_run.py start --kind intake --natural-key intake:000123 \
    --ref idea_id=000123 --ref idea_status=open
uv run python tools/append_run.py position <run_id> --position dispatch_gate
uv run python tools/append_run.py dispatched <run_id> --role idea-triage --budget-cap 50000
uv run python tools/append_run.py dispatch-result <run_id> --outcome ok \
    --input-tokens 1200 --output-tokens 340
uv run python tools/append_run.py gate-reached <run_id> --gate dispatch-authorization \
    --position dispatch_gate
uv run python tools/append_run.py gate-decided <run_id> --gate dispatch-authorization \
    --decision approve
uv run python tools/append_run.py parked <run_id> --reason "budget cap reached"
uv run python tools/append_run.py abandoned <run_id> --reason "idea left open externally"
uv run python tools/append_run.py terminal <run_id> --outcome complete --position done
```

## Expected result

`start` generates a `run_id` and timestamp, validates the result against
`schemas/run.schema.json`, and appends one line. It refuses to open a second non-terminal run
under the same natural key (`kind:primary-ref`) — this is the idempotency guarantee
PLAN-039.01 section 4 requires: two ticks, or a reconcile pass that runs twice, cannot
double-start the same run. Every other subcommand appends a follow-on event for an
already-open `run_id`, reading its `kind` from the ledger so the caller does not have to
repeat it.

## Failure and recovery

A schema validation failure prints the error and appends nothing — the log is never left
with a malformed line. `start` against a natural key with a non-terminal run already open is
refused before writing; close or abandon the existing run first, or address it directly
rather than opening a second one. Any subcommand other than `start` against an unknown
`run_id` is refused. `_data/runs.jsonl` is never hand-edited or corrected in place; a
mistaken entry is superseded by a later event, not fixed.

<!-- generated:tool-reference:start -->

### Reference: `tools/append_run.py`

The only sanctioned writer for `_data/runs.jsonl`, the orchestrator's run ledger.

Thin CLI over `src.orchestrator.ledger` — every subcommand below is that module's own
`start()`/`record()` functions, validated against `schemas/run.schema.json` before the line
is appended. `src.orchestrator.tick` calls those functions directly; this script exists so a
human can write the identical events by hand for a manual correction. See
`src/orchestrator/ledger.py` for the append-only-log rationale and the natural-key
idempotency guarantee `start` enforces.

Usage:
    uv run python tools/append_run.py start --kind intake --natural-key intake:000123 \
        --ref idea_id=000123 --ref idea_status=open
    uv run python tools/append_run.py position <run_id> --position dispatch_gate
    uv run python tools/append_run.py dispatched <run_id> --role idea-triage --budget-cap 50000
    uv run python tools/append_run.py dispatch-result <run_id> --outcome ok \
        --input-tokens 1200 --output-tokens 340
    uv run python tools/append_run.py gate-reached <run_id> --gate dispatch-authorization \
        --position dispatch_gate
    uv run python tools/append_run.py gate-decided <run_id> --gate dispatch-authorization \
        --decision approve
    uv run python tools/append_run.py parked <run_id> --reason "budget cap reached"
    uv run python tools/append_run.py abandoned <run_id> --reason "idea left open externally"
    uv run python tools/append_run.py terminal <run_id> --outcome complete --position done

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--kind` |  | intake, batch, unit, realization |  | yes |
| `--natural-key` |  |  |  | yes |
| `--ref` | one reference field, repeatable |  | [] |  |
| `run_id` |  |  |  |  |
| `--position` |  |  |  | yes |
| `run_id` |  |  |  |  |
| `--role` |  |  |  | yes |
| `--budget-cap` |  |  |  | yes |
| `run_id` |  |  |  |  |
| `--outcome` |  |  |  | yes |
| `--input-tokens` |  |  |  | yes |
| `--output-tokens` |  |  |  | yes |
| `run_id` |  |  |  |  |
| `--gate` |  |  |  | yes |
| `--position` |  |  |  | yes |
| `run_id` |  |  |  |  |
| `--gate` |  |  |  | yes |
| `--decision` |  | approve, reject, amend |  | yes |
| `run_id` |  |  |  |  |
| `--reason` |  |  |  | yes |
| `run_id` |  |  |  |  |
| `--reason` |  |  |  | yes |
| `run_id` |  |  |  |  |
| `--outcome` |  |  |  | yes |
| `--position` |  |  |  | yes |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
