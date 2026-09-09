# Sessions

Session records and walkthroughs. Both carry governed front matter and a date-derived code.

Name files `SESS-YYYY-MM-DD-NN-topic.md`, or `WALK-YYYY-MM-DD-NN-topic.md` for a walkthrough.
Allocate the code with `uv run python -m src.governance --next-code session`; the code's date must
equal the record's `created` date. Never pick the number by reading this directory.

A record captures what was decided, what was built, the verification output as actually observed,
any deviation from `AGENTS.md`, and what is left open. The closing procedure is in
[OPS-001](../08-governance/OPS-001-operations.md); `phase-ses-03` replaces it with a governed
protocol.
