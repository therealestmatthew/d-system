---
schema_version: 1
id: doc-system-boundary-decision-report
code: ARCH-012
title: System boundary study decision report
kind: architecture
status: draft
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-28'
systems: [sys-portfolio, sys-realization, sys-ui, sys-governance, sys-gov-docs, sys-backlog]
depends_on:
  - doc-system-boundary-study
  - doc-system-boundary-study-requirements
  - doc-system-boundary-study-system-inventory
  - doc-system-boundary-study-prompt-rubric
  - doc-system-boundary-study-prompt-inventory
  - doc-system-boundary-study-system-backlog-review
---

# System boundary study decision report

## Decision purpose

This is a draft architecture recommendation for the repository owner. It promotes the System
Boundary Study's working evidence into a decision-ready form; it does not create a repository,
move data, change a prompt lifecycle, alter the system registry, or implement an extraction.

**Recommendation:** retain one repository now and establish explicit ownership and interface
contracts before considering a package or repository extraction. The evidence does not show an
independently operated concern with a stable enough runtime contract, release cadence, or audience
to justify immediate separation.

## Evidence and reconciliation

The report was reconciled on `dev` revision `0c47c27dd9423f5128d9e28edac5b29352e64b17` on
2026-09-26, using only tracked material. The earlier system/interface inventory was recorded at
`2fd11e9`; `git diff 2fd11e9..0c47c27 -- docs/08-governance/systems.yaml` was empty, so its
43-system ownership and interface evidence remains current. The prompt corpus inventory was
recorded at `7e3a067`; no prompt document changed between that revision and this reconciliation,
and `rg -l '^kind: prompt$' docs | wc -l` still returned 40.

The portfolio review's snapshot at `4f3848e` needs a narrow refresh because the backlog changed.
At the reconciled revision, `uv run python -m src.governance --backlog` reports 323 phases: 117
complete, 4 active, 8 deferred, 84 ready, and 110 waiting. This is a governance-workflow change,
not evidence of a new runtime boundary. `uv run python -m src.governance --inventory` continues
to report 43 systems and 378 governed documents. The original inventories, their methods, and
their limits remain the factual basis for this report:

- `docs/00-working/boundary-study/system-interface-inventory.md`
- `docs/00-working/boundary-study/current-boundary-map.md`
- `docs/00-working/boundary-study/prompt-corpus-inventory.md`
- `docs/00-working/boundary-study/prompt-navigation-findings.md`
- `docs/00-working/boundary-study/system-backlog-review.md`

## Proposed concern boundaries

| Concern | Owns | Runtime or operating interfaces | Release cadence and audience | Boundary rule |
| --- | --- | --- | --- | --- |
| Personal-productivity core | Durable portfolio source records, memory records, capture and retrieval intent | Source files projected into DuckDB; read-only context/retrieval interfaces | Owner-facing, ongoing personal operating system | Derived DuckDB data and downstream workflows must not become authority for portfolio or memory records. |
| Idea-realization core | The process that turns durable idea records and validated backlog work into delivery proposals | Idea log and backlog contracts; planned orchestration interfaces | Owner-facing development workflow; currently mostly planned | It must not change idea lineage, priority, approval, or phase completion outside their established records and owner gates. |
| Workbench core | Browser composition, panel state, viewers, explorers, notes, styles and terminal experience | FastAPI-facing browser surface; loopback-gated PTY capability remains behind its backend | Interactive development UI; releases can be paced with the workbench | Panels must not own backend security controls, PTY lifecycle, or another panel's cache policy. |
| Governance/framework layer | Documentation rules, validation, claims, delivery gates, reusable process conventions | Files, commands, CI and review gates rather than a product API | Cross-cutting maintainer framework; used by all concerns | It may constrain work but must not decide product priority, integration, portfolio content, user state, or business outcome. |
| Adjacent and incubating systems | Their explicitly documented local responsibility only | Mostly planned adapters, packaging, analysis, research, automation or demo contracts | Uneven or future-facing; not an independently proven product boundary | Do not present a planned interface as implemented or silently absorb a core concern's source authority. |

The map in `current-boundary-map.md` supports these seams: source records flow through the shared
projection; realization consumes the idea/backlog workflow; the workbench uses APIs and the
loopback-gated terminal backend; governance applies rules across all concerns. These are allowed
crossings, not evidence that the concerns should be separated today.

## Prompt and portfolio implications

Prompt documents are operating material, templates, and campaign evidence—not a single product
surface. The reconciled inventory contains 40 prompts, of which 15 are direct operational entries
or planning starts, 18 are sequence steps, 7 are owner-launched campaigns, and none has no known
default entry point. (Figure corrected 2026-09-28 from 13, 14, 12 and 1: the independent validation
found the inventory's default-entry-point values inconsistent across structurally identical prompts
at the same baseline. The per-prompt values and the rule applied are in
`docs/00-working/boundary-study/validation-report.md`, section 2.) Their independent reuse, precedent, and review fields mean a prompt's active
status must not be interpreted as a separate release unit or a reason to retire it. A future
operating index can improve navigation without changing lifecycle status.

The portfolio is also not a release map. The registry includes 17 implemented, 4 scaffold, 21
planned, and 1 retired system according to the recorded review. The phase graph is deeper than the
system graph, and the current four-slot claim limit is fully occupied. Those facts support a
contract-first, single-repository approach: today's coupling includes governance sequencing and
documentation surfaces as well as runtime relationships.

## Boundary options

| Option | Three cores and framework | Benefits | Costs and risks | Preconditions and extraction trigger |
| --- | --- | --- | --- | --- |
| A. Retain one repository with explicit contracts | Keep personal productivity, realization, workbench, and framework together; formalize source authority and allowed crossings | Lowest migration risk; preserves atomic governance changes and shared tests; supports planned systems without inventing interfaces | Requires continued discipline to prevent boundary erosion; a large repository can remain harder to navigate | **Recommended now.** Document ownership and interfaces, then collect evidence of independently releasable contracts and audience needs. |
| B. Prepare selective package or repository extraction | Keep the personal core authoritative; extract only a stable workbench or framework capability when proven; realization remains integrated until its orchestration contract is real | Enables later reuse and independent cadence for a genuinely stable concern without forcing a three-way split | Adds versioning, compatibility, publishing and cross-repository governance work; can freeze immature contracts | A candidate has a documented API/data contract, independent tests, an identified audience, a maintainer/release owner, and repeated change pressure that cannot be handled by a module boundary. |
| C. Split immediately into personal, realization, workbench, and framework repositories | Make all four concerns independently versioned and coordinated now | Maximum formal isolation and independently scheduled releases in theory | High migration and coordination cost; duplicates governance; creates external contracts for planned systems; weakens atomic changes across the current workflow | Rejected at this point. Reconsider only after each candidate has stable ownership, interfaces, release need, and migration resources demonstrated by operating evidence. |

The rejected alternative is option C: the current evidence does not establish four independently
operated products. Option B is a conditional future path, not a commitment to extract. Option A is
the valid no-code-change immediate outcome required by the study.

## Conditional next actions

| If the owner selects | Next action | What does not happen automatically |
| --- | --- | --- |
| A: single repository with contracts | Commission a bounded follow-up to publish ownership/interface contracts and measure the identified navigation and retrieval gaps. | No package, repository split, system-registry reassignment, or prompt-status change. |
| B: prepare a selective extraction | Choose one candidate concern and commission a discovery phase to specify its API, source authority, tests, versioning, migration and rollback plan before any code move. | No extraction until the preconditions in the options matrix are evidenced and approved. |
| C: immediate split | First require an owner-approved architecture/migration plan that names destination repositories, data boundaries, maintainers, release process, compatibility, and rollback. | No repository creation or data movement follows from this report alone. |

## Owner decision gate

| Decision | Decider and decision point | Recommendation | Consequence of each answer |
| --- | --- | --- | --- |
| Boundary direction | Repository owner, after reviewing this draft and its cited evidence | Select A: retain one repository with explicit contracts | A starts a contract-and-measurement follow-up; B starts one scoped extraction-discovery phase; C requires a separate, owner-approved migration plan before any implementation. |
| First portability candidate, if any | Repository owner, only after choosing B or after new evidence satisfies its preconditions | Do not nominate one yet | Naming a candidate authorizes discovery only; declining keeps all concerns in the one-repository boundary. |
| Prompt navigation treatment | Repository owner, after deciding whether current prompt discoverability is insufficient | Preserve current lifecycle statuses; consider a separate operating index later | An index creates navigation, not a lifecycle change; declining preserves the current corpus and its existing entry points. |
| Evidence threshold for revisiting extraction | Repository owner, when a concern develops a stable audience and release need | Require stable contracts, independent verification, named maintenance/release responsibility, and repeated pressure beyond a module boundary | Meeting the threshold triggers a fresh decision report; not meeting it keeps option A in force without treating deferral as failure. |

## Constraints and limits

- This report is a recommendation based on tracked evidence, not a statement that an extraction is
  implemented or that a proposed boundary is already enforced in code.
- The study did not read `_private/`, inspect untracked worktrees, measure user behavior, or infer
  a release audience from document counts.
- Planned registry systems and dashed map edges are not runtime contracts. They require later
  implementation evidence before they can justify independent release or ownership.
- The owner remains the authority for priority, integration, phase completion, boundary direction,
  portability, and prompt-lifecycle actions.
