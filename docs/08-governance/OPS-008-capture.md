---
schema_version: 1
id: doc-ops-capture
code: OPS-008
title: Quick-capture and inbox intake
kind: operation
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-capture]
depends_on: [doc-capture-routing, doc-capture-requirements]
---

# Quick-capture and inbox intake

## Trigger

Use whenever something needs to be captured before it is lost — a spoken request, a note, a
pasted transcript — and there is no time or need to structure it yet. Both paths write raw
records only (REQ-002 R1/R2, ADR-007 section 1): no interpretation, no structuring, so a later
bug in either can never cost a capture. Structuring, evidence and routing are a separate,
not-yet-built step (`phase-cap-05`).

## Command

```bash
# CLI quick-capture: one command, the text as its only argument (REQ-002 R5)
uv run python tools/capture.py "Call John about the Q3 deliverable by Friday."

# Piping on stdin is the safer route for text containing backticks, $(...) or quotes a
# shell might evaluate before this command ever sees them — the same lesson
# tools/append_idea.py's docstring records from idea 000019.
echo "Call John about the Q3 deliverable by Friday." | uv run python tools/capture.py

# Drain the inbox: converts every file in _capture/inbox/ to a raw record.
uv run python tools/capture.py --inbox
```

Drop any file-shaped input — a pasted note, an email, a transcript — directly into
`_capture/inbox/` for the second path; there is no required format.

## Expected result

Each capture becomes one file in `_capture/raw/`, named `raw-<timestamp>-<hex>.json`, matching
`schemas/capture.schema.json` and byte-identical to what was submitted. `_capture/` is
gitignored (ADR-007 section 8) — nothing here reaches `_data/`. A converted inbox file is moved
to `_capture/inbox/processed/` so a later run never recaptures it; `_capture/inbox/` itself
always shows exactly what is still waiting.

## Failure and recovery

A schema validation failure (most commonly empty content) prints the error and writes nothing.
For the inbox path, a file that fails to convert is left where it is rather than moved, and the
scan continues with the rest — one bad file never blocks the others (REQ-002 R9). Rerunning
`--inbox` after fixing the file picks it up on the next pass. A raw record, once written, is
never edited or deleted by either path.

<!-- generated:tool-reference:start -->

### Reference: `tools/capture.py`

Single-command CLI quick-capture, and the inbox scanner — REQ-002 R5, ADR-007 section 2.

Writes raw records only; no interpretation, no structuring (phase-cap-05 does that). A
capture landing here can never be lost to a later structuring bug, because it is stored
before structuring ever runs.

Usage:
    uv run python tools/capture.py "Call John about the Q3 deliverable by Friday."
    echo "Call John about the Q3 deliverable by Friday." | uv run python tools/capture.py
    uv run python tools/capture.py --inbox

The text is a single positional argument, or stdin when omitted — never both. Piping
through stdin is the safer route for anything containing a backtick, `$(`, or a quote the
calling shell might evaluate; see `tools/append_idea.py`'s docstring for the incident that
made that lesson permanent here.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `text` | the capture text; omit to read from stdin |  |  |  |
| `--inbox` | scan _capture/inbox/ and convert every file there instead of taking text |  |  |  |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
