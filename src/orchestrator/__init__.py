"""The LangGraph orchestrator skeleton (`phase-irs-04`, `ADR-018`, `PLAN-039.01`).

Builds the machinery every run kind shares -- thin graph state, the tick scheduler, gate
nodes, the run ledger reader, the dispatch adapter's interface -- and the one run kind this
phase implements end to end: `intake` (`graphs/intake.py`). The `batch`, `unit` and
`realization` graphs are later phases' work (`phase-irs-14`, `phase-irs-15`, and the
backlog-phase unit graph); nothing here assumes they exist.

ADR-018's boundary rule governs every module in this package: graph state carries run
identity and references into the repository's durable records, never copies of their
content. `_data/ideas.jsonl`, `backlog.yaml`, governed documents and the run ledger
(`_data/runs.jsonl`) remain the only sources of truth. `state.py` carries the three-field
state and the re-derivation rule; nothing else in this package, or anywhere in the
repository, caches record content in a checkpoint.

This phase does not build the daemon's own process management (`start`/`stop`/`status`,
the `flock` lock) -- that is `phase-irs-16`'s work. The CLI here exposes `tick`, `gate`,
`halt` and `resume-dispatch` only.

**Attended-only.** No agent dispatch happens unless `tick()` is called with
`dispatch=True` -- the owner-initiated flag PLAN-039.01 section 2 and REQ-017 R01 require.
Without it, `tick()` still reconciles the desired run set against the records and starts
missing runs (idempotent by natural key), but never advances a thread past its first node,
so no dispatch can occur.

This package defines no claim-recovery logic (REQ-022 R19). Claim-protocol recovery is
`phase-conc-04`'s deliverable, consumed from there when it exists; nothing here reads,
retries or repairs a `_tmpagent/` claim.
"""
