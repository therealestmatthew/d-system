---
schema_version: 1
id: doc-session-agentic-ai-planning-reference
code: SESS-2026-09-26-02
title: Agentic AI planning reference and adversarial revision
kind: session
status: active
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-26'
systems: [sys-governance]
depends_on: [doc-agentic-ai-planning-reference]
---

# Agentic AI planning reference and adversarial revision

## Scope

Owner-directed, unclaimed documentation work: create a durable reference on planning and
implementing with Agentic AI. The work ran in
`/code/d-system-worktrees/agentic-plan-reference` on branch
`agent/agentic-plan-reference`; no backlog phase was manufactured for it.

## Outcome

Added the agentic AI planning reference (`GOV-020`) and linked it from the governance index. It
covers outcome and boundaries, observable requirements, decisions and interfaces, modular phases,
dependencies, status and evidence, verification and recovery, agent execution safeguards, a
portable phase summary, and adversarial plan review.

The reference explicitly maps its advice onto this repository’s required workflow: non-trivial work
uses governed requirement and plan documents before implementation, while the backlog is the sole
execution-status ledger.

## Independent adversarial review

A read-only independent reviewer examined `dev...agent/agentic-plan-reference`. It found no
blocker and reported two major improvements plus one minor improvement:

1. The first draft presented `ready for review` as a generic stored status and supplied a phase
   card too incomplete to copy safely into the repository backlog.
2. The first draft did not state that this repository requires the governed requirement → plan →
   backlog-phase sequence before non-trivial implementation.
3. The first draft described adversarial review without explicitly directing readers to the
   repository’s three-altitude procedure.

All three findings were fixed in `GOV-020`: the status section now names `GOV-002`'s canonical
states and derived readiness; the phase card is relabeled as a portable summary with the required
backlog fields identified; a repository-mapping section states the formal workflow; and the review
section points to `GOV-018`.

## Verification

Run in the worktree after the review revisions:

```text
$ UV_CACHE_DIR=/tmp/d-system-uv-cache uv run python -m src.governance
Governance OK: 43 systems, 364 documents, 32 memories, 318 backlog phases
```

```text
$ UV_CACHE_DIR=/tmp/d-system-uv-cache uv run pytest -p no:cacheprovider test/test_codes.py::test_committed_catalog_matches_regenerated_output -q
1 passed, 1 warning
```

`git diff --check` also passed. The reviewer independently ran governance successfully and the
same catalog-drift test successfully before the final revisions.

## Handoff

The branch is ready for owner review. Adding this session record requires one final catalog
regeneration and governance run before committing.
