---
schema_version: 1
id: doc-backlog-capture
code: GOV-004
title: Initial backlog coverage review
kind: governance
status: active
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems: [sys-backlog]
depends_on: [doc-backlog-decisions, doc-backlog-protocol]
---

# Initial backlog coverage review

Snapshot: 2026-09-05. Reviewed all substantive `kind: plan` documents under `docs/01-plans/` and `plans/`, plus the architectural audit, artifact-generation prompt and saved user answers. There are ten existing open plan documents across four design programs. They are approved for phased delivery under the user's answers; none is marked implemented by this capture.

The [catalog](../09-backlog/backlog.yaml) contains **53 one-session phases: 48 queued and 5 deferred**, with no active or completed product phase. The live command is authoritative for later state/counts. A queued phase with incomplete prerequisites displays as waiting rather than ready.

## Every open plan document

| Plan | Captured phases | Coverage of the source |
|---|---|---|
| `doc-reliability-follow-up` | `phase-rel-01`–`10` | Lint; shape/reference preflight; canonical membership; failure-safe publication decision and implementation; shared DB paths/dependency lifetime; global/--all retrieval; CI and documentation |
| `doc-html-00-overview` | `phase-html-01`–`10` | Complete YAML → JSON → API → React page workflow |
| `doc-html-01-build-tooling` | `phase-html-01`, `02`, `09` | Strict schemas, validated conversion, generated-file ownership and build integration |
| `doc-html-02-backend` | `phase-html-01`, `03`, `04` | Shared runtime contract, Pydantic models, API routes and invalid-input behavior |
| `doc-html-03-frontend-setup` | `phase-html-05`, `06` | Dependencies, Tailwind/theme, router bootstrap and existing-app entry point |
| `doc-html-04-frontend-components` | `phase-html-06`, `07`, `08` | Types, layout, navigation, loading/errors/404, four blocks, dispatch and DynamicPage |
| `doc-html-05-sample-data` | `phase-html-09` | Site/home/about YAML and source-authoring workflow |
| `doc-html-06-verification` | `phase-html-04`, `10` | API/invalid-input tests plus complete automated/manual verification |
| `doc-mini-systems` | `phase-sig-01`–`09`, `phase-syn-01`–`05` | Six SQL signals, view lifecycle, weekly snapshot ownership/writes, four synthesis workflows and digest HTML export |
| `doc-agent-memory` | `phase-mem-01`–`19` | Roles/contracts, candidate schema/validation/application, owner decisions, Librarian, blended hints, evaluation, memory review, pruning, optional review trigger and conditional retrieval extensions |

## Source section audit

The six signals each have a bounded implementation phase: Stale Radar (`sig-02`), Accountability (`sig-03`), Health (`sig-04`), Load (`sig-05`), Velocity (`sig-06`) and Tag Clusters/graph export (`sig-09`). Weekly velocity snapshots are separated into a contract decision (`sig-07`) and a writer (`sig-08`). Shared view installation is `sig-01`.

The four synthesis tools each have a phase: Context Pack (`syn-01`), Session Briefing (`syn-02`), Weekly Review (`syn-03`) and Portfolio Digest (`syn-04`). HTML report export is separately dependent on completed HTML generation (`syn-05`). Missing real commitments/history is handled with explicit empty states and synthetic test fixtures; backlog creation does not fabricate portfolio activity.

Memory contract A is covered by `mem-07` and its later retrieval extensions. Contract B is split across candidate generation, validation and application (`mem-03`, `04`, `06`). Contract C has separate proposal and approved-application phases (`mem-12`, `13`). Contract D and writer permissions are reconciled in `mem-01`. Vault Scribe is `mem-02`; owner conflict/promotion review is `mem-05`. Chronicle remains manual. Hint contract and implementation are `mem-08` and `09`, blending all selected options. Review/decay/orphan proposals are `mem-11`, with opt-in periodic review packaging in `mem-14`.

The old plan's six implementation stages are all represented: prompt roles (`mem-01`–`03`), Librarian (`mem-07`), embeddings (`mem-15`–`17`), semantic search (`mem-18`), agentic refinement (`mem-19`), and pruning/review (`mem-11`–`14`). Review/pruning no longer artificially wait for embeddings, since the accepted manual validated workflow can support them independently.

## Audit findings and user answers

| Outstanding concern | Phase(s) |
|---|---|
| Destructive rebuild before validation and no atomic publication | `rel-02`, `03`, `05`, `06` |
| Missing reference checks and duplicate global task IDs | `rel-03` |
| Project/person source-of-truth conflict | `rel-04` |
| Working-directory DB paths and untested context-manager dependency prompt | `rel-07` |
| Global-memory filtering and --all limit | `rel-08` |
| Existing lint failure and inadequate loader/retrieval CI coverage | `rel-01`, `09` |
| Stale counts, Python claims and proposal-as-implementation prose | `rel-10` |
| Generated JSON authority and strict runtime block validation | `html-01`–`04`, `09` |
| Snapshot ownership | `sig-07`, `08` |
| Direct authorized memory edits versus a sole-writer mandate | `mem-01`, `02`, `06` |
| Manual selected-session extraction and Chronicle naming | `mem-01`, `03` |
| Blended hint inference, registry vocabulary and optional metadata | `mem-08`, `09` |
| Owner resolution of conflicts and promotion | `mem-05`, `06` |
| Semantic provider/storage/privacy choice and unsupported scale thresholds | `mem-10`, deferred `mem-15`–`18` |
| Bounded agentic refinement only when simpler retrieval is insufficient | Deferred `mem-19` |

## Release gates and scope boundary

`mem-15`–`18` remain deferred until a baseline retrieval evaluation records actual unmet needs. `mem-15` then chooses provider/data-use boundaries and success targets. `mem-19` additionally needs evidence that semantic retrieval leaves useful failures unresolved. These are five captured phases, not omitted work or approvals inferred from elapsed time.

Completed governance deliverables are already present. Approval authenticity, historical ID permanence and evidence quality remain explicit human review responsibilities from the governance protocol; they were not promised as automated product features. The raw governance execution prompt is completed input. Scratch answers are source evidence, not a new implementation plan. Portfolio project records are not silently expanded into additional software roadmaps.

## Initial execution order

Start with `phase-rel-01`, then choose ready phases by priority and dependencies. The independent page-contract (`html-01`) and memory-contract (`mem-01`) phases are also initially eligible, but only one phase may be active. No product phase was started during backlog capture.

## Capture validation

- Default governance check passes: 14 systems, 20 governed documents, 7 memories and 53 phases.
- `uv run pytest`: 56 tests pass, including coverage gaps, cycles, deferred gates, readiness,
  evidence requirements and enforcement through the default CLI.
- `uv run mypy src/`: passes for 9 source files.
- `uv run ruff check src/governance/ test/`: passes.
- Full `uv run ruff check src/ test/` still reports only the existing `UP035` import issue
  in `src/db/connection.py`; it is captured as `phase-rel-01`, not repaired during capture.
- The user's raw answer file is preserved. No product phase was executed, database rebuilt,
  external system updated or commit created during this task.
