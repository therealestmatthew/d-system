# Review verification

Reviewed 2026-09-09 against commit “Document the recommended build order for the idea-node classification work”.

## Commands and actual outcomes

1. `uv run python -m src.governance --ready` succeeded: 102 phases, no active claims. The owner explicitly requested this bounded research review instead of the unrelated next phase; no claim, phase closure or production implementation was performed.
2. `D_SYSTEM_DATA_ROOT=_data uv run pytest -q --deselect=test/test_private_content.py::test_tracked_tree_passes_the_checker` exited 0: **394 passed, 1 deselected, 2 warnings in 7.36s**. Full output is [pytest-review.txt](pytest-review.txt). The deselected test invokes a scanner of the actual private portfolio; it was intentionally not run. Synthetic private-path tests use temporary trees and do not inspect the real `_private/`. The two warnings concern TestClient/HTTPX and the anyio BlockingPortal alias.
3. `uv run python research/evidence/review_probes.py` exited 0. [JSON results](review-probe-results.json) record adverse behavior, not a claim that the system passed the challenged guarantees. The script calls existing functions against synthetic `/tmp` stores and a local TestClient; it never opens/rebuilds the live database. The probe removes any inherited data-root override before creating its fixture stores.
4. `D_SYSTEM_DATA_ROOT=_data uv run python -m src.governance` exited 0: **Governance OK: 16 systems, 107 documents, 15 memories, 102 backlog phases**. Output is [governance-review.txt](governance-review.txt).
5. Generated the governance catalog to `/tmp/d-system-review-catalog.md` and compared it byte-for-byte with `docs/08-governance/catalog.md`: identical. Research is outside the validator's docs/brain document scan; no catalog mutation was needed.
6. Verified all 15 original research hashes, all 28 requested organized/reference copy hashes, all archive members against extracted bytes, and 88 implementation/configuration/test hashes against the snapshot captured during review. Twelve numbered reports exist. Checked local report links and cited path/range bounds. Final machine-readable results: [integrity-check.json](integrity-check.json).

## Scope and limits

- No `_private/` inspection, live database rebuild, data migration, source record correction, prompt execution, literature search, remote operation or deployment was performed.
- Tests read applicable tracked source records; no portfolio prose was copied into the reports. The real idea trace reproduces only selected structural promotion metadata, not idea content.
- The read-only review used the existing Python environment (Python 3.14); project requirement is >=3.12. No dependency install or production/frontend build artifact was needed.
- The environment's default shell sandbox failed before running commands with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`. Reviewed escalated calls were used for authorized reads and research writes. No approval rejection remained unresolved.
- No autonomous session-close or separate external review was performed. These artifacts await external review; the prepared literature-review directory contains only CLAUDE.md.
- Tests support bounded implementation claims. They do not prove exhaustive history preservation, research novelty, external deployment state, hard actor authorization or comparative context quality.

## Unrelated concurrent working-tree change

The initial repository status had only untracked `.agents/` and `research/`. Final `git diff` shows a two-line writing-style section added to root `CLAUDE.md`. No command in this review wrote that file; the addition occurred outside this review and was preserved. It was already present when the implementation hash snapshot was captured. All tracked implementation changes relative to HEAD are confined to that unrelated instruction edit; review writes are confined to `research/`. The snapshot comparison is a check since snapshot time, not a claim that the shared checkout had no external activity.
