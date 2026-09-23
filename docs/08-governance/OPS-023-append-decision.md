---
schema_version: 1
id: doc-ops-append-decision
code: OPS-023
title: Append a decision to the gate decision inbox
kind: operation
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-realization]
depends_on: [doc-governance-operations]
---

# Append a decision to the gate decision inbox

## Trigger

Use whenever the owner decides an interrupted orchestrator gate — approve, reject or amend.
This is the only sanctioned writer for `_data/gate-decisions.jsonl`, the decision inbox: the
idea log's discipline scaled down to one gate resumption (PLAN-039.01 section 7). The run
resumes at the next `uv run python -m src.orchestrator tick --dispatch`, not immediately —
this command only records the decision.

## Command

```bash
uv run python tools/append_decision.py decide <run_id> --gate dispatch-authorization \
    --decision approve --by repository-owner
uv run python tools/append_decision.py decide <run_id> --gate G2 --decision amend \
    --by repository-owner --notes "reordered next_up: phase-x before phase-y"
```

## Expected result

`decide` computes `decision_seq` automatically — one more than however many decisions this
`(run_id, gate)` pair already carries — validates the result against
`schemas/gate-decision.schema.json`, and appends one line. There is no flag to supply
`decision_seq` yourself in the ordinary path; it exists as an internal parameter so a caller
that has already computed the expected value can assert it, and a stale value is refused.

## Failure and recovery

A schema validation failure prints the error and appends nothing. A second decision for a
gate that has not been reached again since its last decision is refused — the dedup key
`(run_id, gate, decision_seq)` doing its job — before it is appended. The repository artifact
a decision produces remains the durable truth; `_data/gate-decisions.jsonl` only requests a
resumption and is never hand-edited or corrected in place.

<!-- generated:tool-reference:start -->

### Reference: `tools/append_decision.py`

The only sanctioned writer for `_data/gate-decisions.jsonl`, the decision inbox.

Thin CLI over `src.orchestrator.decisions.decide()`, validated against
`schemas/gate-decision.schema.json` before the line is appended. `src.orchestrator.tick`'s
`advance()` reads this file (via `decisions.load_decisions`/`latest_for_gate`) to find a
decision waiting to resume an interrupted gate. See `src/orchestrator/decisions.py` for the
dedup-key rationale.

Usage:
    uv run python tools/append_decision.py decide <run_id> --gate dispatch-authorization \
        --decision approve --by repository-owner
    uv run python tools/append_decision.py decide <run_id> --gate G2 --decision amend \
        --by repository-owner --notes "reordered next_up: phase-x before phase-y"

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `run_id` |  |  |  |  |
| `--gate` |  |  |  | yes |
| `--decision` |  | approve, reject, amend |  | yes |
| `--by` |  |  |  | yes |
| `--notes` |  |  |  |  |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
