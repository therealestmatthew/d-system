---
schema_version: 1
id: doc-ops-overview-metrics
code: OPS-011
title: Generate chart-ready metrics from the idea log and backlog
kind: operation
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-portfolio]
depends_on: [doc-governance-operations]
---

# Generate chart-ready metrics from the idea log and backlog

## Trigger

Run to generate metrics for dashboard or reporting views. This tool reads only from `_data/ideas.jsonl` and `docs/09-backlog/backlog.yaml`, using the same sanctioned readers as the rest of the system (`load_events()` and `fold()` from `src/db/ideas.py`). Its output is fully deterministic: two runs against an unchanged repository produce byte-identical JSON, with no dependence on wall-clock time.

## Command

```bash
uv run python tools/overview_metrics.py               # print to stdout
uv run python tools/overview_metrics.py --out FILE     # write to FILE instead
```

## Expected result

Exit 0. A JSON document is emitted, deterministically ordered by key and sorted across every list. The document carries metadata (idea count, event count, backlog phase count, reference timestamp), followed by eight metric sections, each shaped for a chart library:

- `funnel`: Idea counts and rates by current status
- `cycle_time`: Elapsed hours between status transitions
- `annotation_coverage`: Ideas with and without annotations
- `link_distribution`: Non-retracted links by type
- `link_orphans`: Ideas with no link connections
- `throughput_by_day`: Ideas created per calendar day, gap-filled across the range
- `age_of_open_ideas`: Days since creation for each currently-open idea
- `backlog_by_status`: Phase counts by execution status from `docs/09-backlog/backlog.yaml`

Every status, transition, link type, and backlog status that exists in the schema appears in output, even at zero count. Each section is shaped as `{"labels": [...], "series": [{"label": ..., "values": [...]}, ...]}`, with values aligned to labels.

## Failure and recovery

An error in reading `_data/ideas.jsonl` (schema violation, missing files) prints to stderr with exit 1; fix the source file and rerun. The tool never modifies any source file. If the output looks malformed, verify `_data/ideas.jsonl` is valid against `schemas/idea.schema.json` and that `docs/09-backlog/backlog.yaml` exists and is valid YAML.

<!-- generated:tool-reference:start -->

### Reference: `tools/overview_metrics.py`

Chart-ready JSON metrics over the idea log and the backlog — idea `000071`'s metric set.

Every number here is read through the sanctioned readers — `load_events()` and `fold()` in
`src/db/ideas.py` — never by parsing `_data/ideas.jsonl` by hand, and through a plain
`yaml.safe_load` of `docs/09-backlog/backlog.yaml` for phase counts. The tool makes no model or
network call and asks the wall clock for nothing: every value is a pure function of the two
source files. Two runs against an unchanged repository produce byte-identical output — see
`meta.reference_at` below for how "age of open ideas" stays deterministic without `datetime.now()`.

Emitted, per idea `000071`'s candidate metric set: funnel counts and rates by status; cycle time
between statuses; annotation coverage; link-type distribution and orphan count; throughput by
day; and age of open ideas — plus backlog phase counts by status, the one metric this tool draws
from `docs/09-backlog/backlog.yaml` rather than the idea log. A status, transition, link type or
backlog status that has never occurred still appears with a zero value; it is never omitted.

Each section is shaped for a chart library: `{"labels": [...], "series": [{"label": ...,
"values": [...]}, ...]}`, with `values[i]` aligned to `labels[i]`. Every list is sorted and every
dict key is emitted in sorted order (`json.dumps(..., sort_keys=True)`), which is what makes two
runs byte-identical rather than merely equal.

    uv run python tools/overview_metrics.py               # print to stdout
    uv run python tools/overview_metrics.py --out FILE     # write to FILE instead

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--out` | write the JSON here instead of stdout |  |  |  |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
