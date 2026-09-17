---
schema_version: 1
id: doc-session-corpus-status-flag
code: SESS-2026-09-16-07
title: Corpus builder status filter made selectable and tested
kind: session
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-portfolio]
depends_on: [doc-repeatable-idea-partition, doc-repeatable-idea-partition-requirements, doc-build-coordinator]
---

# Corpus builder status filter made selectable and tested

First phase of [PROMPT-036](../02-prompts/PROMPT-036-build-coordinator.md) batch 1, built by
dispatched agents under the coordinator (`agent-build`), executing **phase-part-02** — make the
corpus status selectable and test the corpus builder — from the repeatable idea partition plan
(`PLAN-025`) and its requirements (`REQ-009`).

## Outcome

`tools/build_idea_corpus.py` gained a `--status` flag accepting one status or a comma-separated
list, defaulting to `triaged`. The `CORPUS_STATUS` module constant is gone; the valid status set is
derived from the idea record system (`legal_transitions()` over `schemas/idea.schema.json`), not a
second hard-coded list. `manifest.json` records the selected statuses on every full build. The tool
gained its first test file, `test/test_build_idea_corpus.py` (11 tests). The corpus builder
operations guide (`OPS-015`) was updated and its tool-reference block regenerated.

## Evidence

- Default `--stats` output is byte-identical to dev's under a fixed seed (`--seed 42`), verified by
  the coordinator against a pre-change baseline captured before any edit; the only unseeded
  difference between runs is the randomly drawn, recorded `shuffle_seed`, which is pre-existing
  behavior.
- `--status open` corpus size (43) equals an independent `fold()` count of open ideas (43), also
  verified against a comma-list and a rejected partial-invalid list by the adversary.
- `--status nonsense` exits 1 naming the five valid values.
- `uv run pytest`: 591 passed. `uv run ruff check tools/ test/`: clean. Governance OK.
- Independent validator: pass on all five acceptance conditions. Adversarial review: clean.

## Unresolved

- Minor, accepted: OPS-015's generated reference table shows a blank Default column for `--status`
  because `tools/generate_tool_docs.py` cannot evaluate a `Name` node (`DEFAULT_STATUS`) as an
  argparse default. Pre-existing generator limitation, not a regression; the prose help text states
  the default correctly.

Full evidence trail (recon, creator, validator and adversary reports) in the coordinator's working
directory for this run, `_working/build-b1/phase-part-02.md` (gitignored).
