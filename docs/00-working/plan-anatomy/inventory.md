# Plan anatomy: inventory

*Ran unclaimed: owner-directed work with no backlog phase; no peer holds a lock against it.*

Idea `000505` (re-investigate the anatomy of a plan and of a plan folder). This file records what
the repository holds. It gives no recommendation; those are in [findings.md](findings.md) and
[proposed-standard.md](proposed-standard.md).

Measured on `origin/dev` at `518188a`, 2026-09-28, in a cloud clone. Every count below has a
command. The commands call [`measure.py`](measure.py) in this folder, which reads the repository
and writes nothing:

```bash
uv run python docs/00-working/plan-anatomy/measure.py plans       # section 1
uv run python docs/00-working/plan-anatomy/measure.py folders     # section 2
uv run python docs/00-working/plan-anatomy/measure.py scatter     # section 3.1
uv run python docs/00-working/plan-anatomy/measure.py decisions   # section 3.2
uv run python docs/00-working/plan-anatomy/measure.py gov003      # section 3.2
uv run python docs/00-working/plan-anatomy/measure.py prompts     # section 3.3
uv run python docs/00-working/plan-anatomy/measure.py trace PLAN-005 PLAN-022 PLAN-023 PLAN-029 PLAN-048 PLAN-050 PLAN-052   # section 3.7
```

The plan list comes from the catalog rows of kind `plan` (`docs/08-governance/catalog.md`), not
from directory names. The entry check is the script in `GOV-018` step 1, which `measure.py`
extracts from that document each time it runs, so the result is the script as written.

## 1. Every plan

### Counts

| Measure | Count | Command or source |
|---|---|---|
| Documents of `kind: plan` in the catalog | 81 | `grep -cE "^\| PLAN-[0-9.]+ \| plan \|" docs/08-governance/catalog.md` |
| Top-level plans (no `parent`) | 49 | `measure.py plans`, rows with an empty Parent cell |
| Child plans (sub-coded, with `parent`) | 32 | same |
| Top-level plans stored as a folder | 5: `PLAN-003`, `PLAN-017`, `PLAN-023`, `PLAN-048`, `PLAN-050` | `measure.py plans`, Layout column |
| Top-level plans stored as a single file | 44 | same |
| Child plans inside their parent's folder | 31 | same |
| Child plans outside any folder | 1: `PLAN-039.01` | same |
| Status of the 49 top-level plans | 25 draft, 11 active, 10 approved, 3 complete | same |

`grep -rl "^kind: plan$" docs` finds 83 files. The two extra are not governed plans: a template,
`docs/00-working/framework/05-schemas/plan.template.md`, and `GOV-001`, whose front-matter example
contains the line.

The five folders named in the prompt are confirmed. The prompt did not mention the sixth case:
**the orchestrator design (`PLAN-039.01`) is a child plan stored as a single file directly under
`docs/01-plans/`**, beside its parent, the idea realization plan (`PLAN-039`). `GOV-005`, "Multi-file
plans", says "A plan set lives in a folder named for the parent code". The governance check does not
enforce that sentence: `naming_errors` in `src/governance/codes.py` checks a containing folder only
when there is one (`len(relative.parts) > 1`), so a flat child passes. It was added in `f8c9e43`
on 2026-09-15.

### GOV-018 entry check

Plans created before 2026-09-22 are exempt (`GOV-010`, Scope). The table shows what the script
reports for them anyway, marked `exempt`.

| Result | Documents |
|---|---|
| Exempt (created before 2026-09-22) | 58, of which 1 (`PLAN-008`) would pass |
| Pass | 10: `PLAN-045`, `PLAN-046`, `PLAN-047`, `PLAN-048`, `PLAN-050`, `PLAN-050.01`, `PLAN-050.04`, `PLAN-050.05`, `PLAN-051`, `PLAN-052` |
| Fail | 13: `PLAN-048.01` to `PLAN-048.11`, `PLAN-050.02`, `PLAN-050.03` |

All seven top-level plans written after 2026-09-22 pass. Every failure is a child plan in a folder.

**Eleven of the thirteen failures come from a fault in the entry-check script, not from the plans.**
Each `PLAN-048` child fails for "Requirement coverage". A child's `depends_on` names only its parent
overview or a sibling, both of kind `plan`. The script resolves each `depends_on` id with
`grep -lx "id: $dep" docs/*/*.md`, which searches one directory below `docs/`. A document inside a
plan folder is two directories below, so the lookup finds nothing, and `xargs -r` then exits 0
without running `grep`. The script reads that exit 0 as "this dependency is a requirement":

```text
$ grep -lx "id: doc-idea-realization-plugin" docs/*/*.md; echo "grep exit=$?"
grep exit=1
$ echo -n "" | xargs -r grep -qx "kind: requirement"; echo "xargs -r on empty input exit=$?"
xargs -r on empty input exit=0
$ grep -lx "id: doc-idea-realization-plugin" docs/*/*/*.md
docs/01-plans/PLAN-048-idea-realization-plugin/PLAN-048-overview.md
```

So any plan whose `depends_on` names a document inside a plan folder is told it needs a
"Requirement coverage" section. The review record for the idea-realization plugin plan
(`2026-09-25-plan-048`) says the script exited 0 for the overview and every child at `fa44a92`.
That commit is not in this clone (`git cat-file -t fa44a92` reports "Not a valid object name"),
so the earlier run cannot be reproduced here. The plugin's own plan check,
`plugins/idea-realization/scripts/plan_check.py`, resolves `depends_on` by document id and does
not have this fault.

The other two failures are real under the rules as written: `PLAN-050.02` and `PLAN-050.03` each
name two or more phase ids, so `GOV-010` requires an "Execution order" section, and neither has
one.

`GOV-018` says a child plan "is its own target and gets its own review", and the script checks
one file. The `PLAN-048` review ran it on the overview and on each child separately.

### Two child plans that are records, not plans

`PLAN-048.10` (13,915 words) and `PLAN-048.11` (18,945 words) are trace tables: each maps the
plugin's governance documents, rule by rule, to the source passages they restate. They were
written by `phase-plug-07` and `phase-plug-09` as outputs. They carry `kind: plan`, a sub-code,
and the six plan headings the entry check reads. The next-largest plan document is 3,523 words
(`PLAN-039.01`). Section 2 explains why a record kept in a plan folder has to be typed as a plan.

### The full table

One row per `kind: plan` document, in catalog order. "Phases" counts backlog items whose `plan`
field is the document's id. "Words" is `len(text.split())` over the whole file, front matter
included.

| Code | Path under docs/01-plans/ | Layout | Parent | Status | Created | Phases | Words | GOV-018 entry check |
|---|---|---|---|---|---|---|---|---|
| PLAN-001 | `PLAN-001-agent-memory-system.md` | file |  | approved | 2026-09-05 | 19 | 3124 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions) |
| PLAN-002 | `PLAN-002-mini-systems-proposal.md` | file |  | approved | 2026-09-05 | 14 | 1281 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions) |
| PLAN-003 | `PLAN-003-dynamic-html-generation/PLAN-003-overview.md` | folder |  | approved | 2026-09-05 | 10 | 683 | exempt (missing Context; Work; Verification; Boundaries; Open questions) |
| PLAN-003.01 | `PLAN-003-dynamic-html-generation/PLAN-003.01-build-tooling.md` | folder | PLAN-003 | approved | 2026-09-05 | 0 | 457 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions) |
| PLAN-003.02 | `PLAN-003-dynamic-html-generation/PLAN-003.02-backend.md` | folder | PLAN-003 | approved | 2026-09-05 | 0 | 469 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions) |
| PLAN-003.03 | `PLAN-003-dynamic-html-generation/PLAN-003.03-frontend-setup.md` | folder | PLAN-003 | approved | 2026-09-05 | 0 | 642 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions) |
| PLAN-003.04 | `PLAN-003-dynamic-html-generation/PLAN-003.04-frontend-components.md` | folder | PLAN-003 | approved | 2026-09-05 | 0 | 1128 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions) |
| PLAN-003.05 | `PLAN-003-dynamic-html-generation/PLAN-003.05-sample-data.md` | folder | PLAN-003 | approved | 2026-09-05 | 0 | 356 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions) |
| PLAN-003.06 | `PLAN-003-dynamic-html-generation/PLAN-003.06-verification.md` | folder | PLAN-003 | approved | 2026-09-05 | 0 | 509 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions) |
| PLAN-004 | `PLAN-004-reliability-follow-up.md` | file |  | approved | 2026-09-05 | 11 | 396 | exempt (missing Design; Verification; Boundaries) |
| PLAN-005 | `PLAN-005-document-code-system.md` | file |  | complete | 2026-09-05 | 6 | 1945 | exempt (missing Design; Boundaries; Requirement coverage; Concurrency) |
| PLAN-006 | `PLAN-006-confidentiality-sweep.md` | file |  | complete | 2026-09-05 | 6 | 1562 | exempt (missing Design) |
| PLAN-007 | `PLAN-007-capture-and-structuring-system.md` | file |  | complete | 2026-09-05 | 1 | 497 | exempt (missing Boundaries; Concurrency) |
| PLAN-008 | `PLAN-008-session-lifecycle-protocols.md` | file |  | draft | 2026-09-05 | 6 | 1668 | exempt (would pass) |
| PLAN-009 | `PLAN-009-capture-build.md` | file |  | draft | 2026-09-06 | 8 | 1039 | exempt (missing Design; Boundaries; Requirement coverage; Concurrency) |
| PLAN-010 | `PLAN-010-code-reservation-enforcement.md` | file |  | draft | 2026-09-06 | 1 | 467 | exempt (missing Design; Boundaries; Concurrency) |
| PLAN-012 | `PLAN-012-terminology-system.md` | file |  | draft | 2026-09-06 | 2 | 885 | exempt (missing Verification; Boundaries) |
| PLAN-013 | `PLAN-013-tooling-documentation.md` | file |  | draft | 2026-09-06 | 2 | 638 | exempt (missing Design; Verification; Boundaries) |
| PLAN-014 | `PLAN-014-governance-and-complexity-review.md` | file |  | draft | 2026-09-06 | 5 | 535 | exempt (missing Work; Verification; Boundaries; Open questions) |
| PLAN-015 | `PLAN-015-ephemeral-working-plans.md` | file |  | draft | 2026-09-06 | 1 | 1252 | exempt (missing Work; Verification; Boundaries) |
| PLAN-016 | `PLAN-016-idea-record-system.md` | file |  | draft | 2026-09-06 | 3 | 1503 | exempt (missing Verification; Boundaries; Open questions; Concurrency) |
| PLAN-017 | `PLAN-017-idea-plan-lifecycle/PLAN-017-overview.md` | folder |  | draft | 2026-09-06 | 5 | 2021 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions; Requirement coverage; Concurrency) |
| PLAN-017.01 | `PLAN-017-idea-plan-lifecycle/The Idea Lifecycle/PLAN-017.01-capture-resolution-promotion.md` | folder | PLAN-017 | draft | 2026-09-06 | 0 | 1404 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions; Requirement coverage) |
| PLAN-017.02 | `PLAN-017-idea-plan-lifecycle/The Plan Lifecycle/PLAN-017.02-state-activation-closure.md` | folder | PLAN-017 | draft | 2026-09-06 | 0 | 1368 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions; Requirement coverage) |
| PLAN-017.03 | `PLAN-017-idea-plan-lifecycle/Idea Architecture/PLAN-017.03-event-contract-and-amendment-fold.md` | folder | PLAN-017 | draft | 2026-09-06 | 0 | 1358 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions; Requirement coverage) |
| PLAN-017.04 | `PLAN-017-idea-plan-lifecycle/Idea Architecture/PLAN-017.04-annotations-and-relationships.md` | folder | PLAN-017 | draft | 2026-09-06 | 0 | 1047 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions; Requirement coverage) |
| PLAN-017.05 | `PLAN-017-idea-plan-lifecycle/Idea Architecture/PLAN-017.05-writing-projection-and-analysis.md` | folder | PLAN-017 | draft | 2026-09-06 | 0 | 1028 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions; Requirement coverage) |
| PLAN-017.06 | `PLAN-017-idea-plan-lifecycle/Plan Architecture/PLAN-017.06-governance-integration-and-delivery.md` | folder | PLAN-017 | draft | 2026-09-06 | 0 | 1091 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions; Requirement coverage; Concurrency) |
| PLAN-018 | `PLAN-018-plans-directory-consolidation.md` | file |  | approved | 2026-09-08 | 1 | 469 | exempt (missing Design; Verification; Boundaries) |
| PLAN-019 | `PLAN-019-idea-priority-queue.md` | file |  | draft | 2026-09-08 | 1 | 793 | exempt (missing Boundaries) |
| PLAN-020 | `PLAN-020-portable-agent-workflows.md` | file |  | draft | 2026-09-09 | 3 | 1156 | exempt (missing Work; Boundaries; Open questions; Requirement coverage) |
| PLAN-021 | `PLAN-021-live-demo.md` | file |  | draft | 2026-09-10 | 7 | 1312 | exempt (missing Design; Work; Verification; Boundaries; Open questions; Requirement coverage; Concurrency) |
| PLAN-022 | `PLAN-022-workbench.md` | file |  | active | 2026-09-10 | 10 | 1318 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions; Requirement coverage; Concurrency) |
| PLAN-023 | `PLAN-023-literature-review-campaign/PLAN-023-overview.md` | folder |  | draft | 2026-09-12 | 9 | 1515 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions; Concurrency) |
| PLAN-023.01 | `PLAN-023-literature-review-campaign/PLAN-023.01-scope-record.md` | folder | PLAN-023 | draft | 2026-09-12 | 0 | 1161 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions) |
| PLAN-023.02 | `PLAN-023-literature-review-campaign/PLAN-023.02-search-domain-matrix.md` | folder | PLAN-023 | draft | 2026-09-12 | 0 | 2325 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions; Concurrency) |
| PLAN-023.03 | `PLAN-023-literature-review-campaign/PLAN-023.03-evidence-contract.md` | folder | PLAN-023 | draft | 2026-09-12 | 0 | 1519 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions) |
| PLAN-024 | `PLAN-024-consultant-demo-kit.md` | file |  | draft | 2026-09-12 | 4 | 3339 | exempt (missing Context; Design; Work; Verification; Boundaries; Open questions; Requirement coverage) |
| PLAN-025 | `PLAN-025-repeatable-idea-partition.md` | file |  | draft | 2026-09-14 | 3 | 2003 | exempt (missing Work; Boundaries; Open questions; Requirement coverage; Concurrency) |
| PLAN-026 | `PLAN-026-concurrency-git-safety.md` | file |  | active | 2026-09-14 | 10 | 3028 | exempt (missing Boundaries; Open questions) |
| PLAN-027 | `PLAN-027-workbench-features-defects.md` | file |  | draft | 2026-09-14 | 12 | 3073 | exempt (missing Boundaries; Open questions; Concurrency) |
| PLAN-028 | `PLAN-028-workbench-architecture-quality.md` | file |  | draft | 2026-09-14 | 20 | 3347 | exempt (missing Boundaries; Open questions) |
| PLAN-029 | `PLAN-029-idea-graph-lifecycle.md` | file |  | active | 2026-09-14 | 20 | 3094 | exempt (missing Boundaries; Open questions) |
| PLAN-030 | `PLAN-030-document-backlog-governance.md` | file |  | active | 2026-09-14 | 8 | 2626 | exempt (missing Boundaries; Open questions) |
| PLAN-031 | `PLAN-031-agent-engineering-delegation.md` | file |  | active | 2026-09-14 | 14 | 2800 | exempt (missing Boundaries; Open questions) |
| PLAN-032 | `PLAN-032-autonomous-agent-operations.md` | file |  | active | 2026-09-14 | 7 | 2386 | exempt (missing Boundaries; Open questions) |
| PLAN-033 | `PLAN-033-retrieval-knowledge-infrastructure.md` | file |  | active | 2026-09-14 | 11 | 2357 | exempt (missing Boundaries; Open questions) |
| PLAN-034 | `PLAN-034-blocked-downstream-projections.md` | file |  | active | 2026-09-14 | 5 | 1721 | exempt (missing Boundaries; Open questions) |
| PLAN-035 | `PLAN-035-schema-consistency-testing.md` | file |  | active | 2026-09-14 | 7 | 2238 | exempt (missing Boundaries; Open questions) |
| PLAN-036 | `PLAN-036-html-generation-design-system.md` | file |  | active | 2026-09-14 | 7 | 1938 | exempt (missing Boundaries; Open questions) |
| PLAN-037 | `PLAN-037-standalone-explorations-housekeeping.md` | file |  | active | 2026-09-14 | 8 | 2144 | exempt (missing Design; Verification; Boundaries; Open questions) |
| PLAN-038 | `PLAN-038-backlog-status-regression-guard.md` | file |  | draft | 2026-09-14 | 1 | 946 | exempt (missing Verification; Open questions; Requirement coverage; Concurrency) |
| PLAN-039 | `PLAN-039-idea-realization-system.md` | file |  | draft | 2026-09-15 | 14 | 1333 | exempt (missing Context; Design; Verification; Boundaries; Open questions; Requirement coverage) |
| PLAN-039.01 | `PLAN-039.01-orchestrator-design.md` | file | PLAN-039 | draft | 2026-09-15 | 3 | 3523 | exempt (missing Context; Design; Work; Verification; Boundaries; Requirement coverage; Concurrency) |
| PLAN-040 | `PLAN-040-portable-framework-document-templates.md` | file |  | draft | 2026-09-19 | 5 | 1961 | exempt (missing Design; Work; Verification; Open questions; Requirement coverage; Concurrency) |
| PLAN-041 | `PLAN-041-portable-framework-content-extraction.md` | file |  | draft | 2026-09-19 | 3 | 603 | exempt (missing Design; Work; Verification; Open questions; Requirement coverage; Concurrency) |
| PLAN-042 | `PLAN-042-session-taxonomy-investigation.md` | file |  | draft | 2026-09-19 | 2 | 577 | exempt (missing Design; Verification; Boundaries; Open questions; Requirement coverage; Concurrency) |
| PLAN-043 | `PLAN-043-literature-review-report-page.md` | file |  | approved | 2026-09-20 | 4 | 770 | exempt (missing Context; Verification; Open questions; Requirement coverage; Concurrency) |
| PLAN-045 | `PLAN-045-deterministic-guards.md` | file |  | approved | 2026-09-23 | 4 | 3480 | pass |
| PLAN-046 | `PLAN-046-design-document-amendments.md` | file |  | approved | 2026-09-23 | 1 | 2500 | pass |
| PLAN-047 | `PLAN-047-reviewer-contract.md` | file |  | approved | 2026-09-24 | 5 | 2149 | pass |
| PLAN-048 | `PLAN-048-idea-realization-plugin/PLAN-048-overview.md` | folder |  | approved | 2026-09-25 | 9 | 1945 | pass |
| PLAN-048.01 | `PLAN-048-idea-realization-plugin/PLAN-048.01-skeleton-install.md` | folder | PLAN-048 | approved | 2026-09-25 | 0 | 743 | missing Requirement coverage |
| PLAN-048.02 | `PLAN-048-idea-realization-plugin/PLAN-048.02-idea-system.md` | folder | PLAN-048 | approved | 2026-09-25 | 0 | 500 | missing Requirement coverage |
| PLAN-048.03 | `PLAN-048-idea-realization-plugin/PLAN-048.03-partition.md` | folder | PLAN-048 | approved | 2026-09-25 | 0 | 492 | missing Requirement coverage |
| PLAN-048.04 | `PLAN-048-idea-realization-plugin/PLAN-048.04-backlog-sessions.md` | folder | PLAN-048 | approved | 2026-09-25 | 0 | 462 | missing Requirement coverage |
| PLAN-048.05 | `PLAN-048-idea-realization-plugin/PLAN-048.05-document-governance.md` | folder | PLAN-048 | approved | 2026-09-25 | 0 | 411 | missing Requirement coverage |
| PLAN-048.06 | `PLAN-048-idea-realization-plugin/PLAN-048.06-generators-layout.md` | folder | PLAN-048 | approved | 2026-09-25 | 0 | 452 | missing Requirement coverage |
| PLAN-048.07 | `PLAN-048-idea-realization-plugin/PLAN-048.07-absolute-documents.md` | folder | PLAN-048 | approved | 2026-09-25 | 0 | 610 | missing Requirement coverage |
| PLAN-048.08 | `PLAN-048-idea-realization-plugin/PLAN-048.08-end-to-end.md` | folder | PLAN-048 | approved | 2026-09-25 | 0 | 470 | missing Requirement coverage |
| PLAN-048.09 | `PLAN-048-idea-realization-plugin/PLAN-048.09-absolute-documents-two.md` | folder | PLAN-048 | approved | 2026-09-25 | 0 | 438 | missing Requirement coverage |
| PLAN-048.10 | `PLAN-048-idea-realization-plugin/PLAN-048.10-absolutes-trace.md` | folder | PLAN-048 | approved | 2026-09-26 | 0 | 13915 | missing Requirement coverage; Concurrency |
| PLAN-048.11 | `PLAN-048-idea-realization-plugin/PLAN-048.11-absolutes-two-trace.md` | folder | PLAN-048 | approved | 2026-09-27 | 0 | 18945 | missing Requirement coverage; Concurrency |
| PLAN-050 | `PLAN-050-system-boundary-study/PLAN-050-overview.md` | folder |  | draft | 2026-09-26 | 0 | 459 | pass |
| PLAN-050.01 | `PLAN-050-system-boundary-study/PLAN-050.01-system-inventory.md` | folder | PLAN-050 | draft | 2026-09-26 | 1 | 245 | pass |
| PLAN-050.02 | `PLAN-050-system-boundary-study/PLAN-050.02-prompt-classification-rubric.md` | folder | PLAN-050 | draft | 2026-09-26 | 1 | 249 | missing Concurrency |
| PLAN-050.03 | `PLAN-050-system-boundary-study/PLAN-050.03-prompt-corpus-inventory.md` | folder | PLAN-050 | draft | 2026-09-26 | 1 | 230 | missing Concurrency |
| PLAN-050.04 | `PLAN-050-system-boundary-study/PLAN-050.04-system-backlog-review.md` | folder | PLAN-050 | draft | 2026-09-26 | 1 | 228 | pass |
| PLAN-050.05 | `PLAN-050-system-boundary-study/PLAN-050.05-boundary-decision-report.md` | folder | PLAN-050 | draft | 2026-09-26 | 1 | 248 | pass |
| PLAN-051 | `PLAN-051-session-autonomy-configuration.md` | file |  | draft | 2026-09-27 | 3 | 2791 | pass |
| PLAN-052 | `PLAN-052-plugin-audit-remediation.md` | file |  | draft | 2026-09-27 | 6 | 2693 | pass |

## 2. What each plan folder holds

```text
$ uv run python docs/00-working/plan-anatomy/measure.py folders
PLAN-003-dynamic-html-generation/
  PLAN-003-overview.md
  PLAN-003.01-build-tooling.md … PLAN-003.06-verification.md          (6 children)
PLAN-017-idea-plan-lifecycle/
  Idea Architecture/PLAN-017.03-…, PLAN-017.04-…, PLAN-017.05-…
  PLAN-017-overview.md
  Plan Architecture/PLAN-017.06-governance-integration-and-delivery.md
  The Idea Lifecycle/PLAN-017.01-capture-resolution-promotion.md
  The Plan Lifecycle/PLAN-017.02-state-activation-closure.md
PLAN-023-literature-review-campaign/
  PLAN-023-overview.md
  PLAN-023.01-scope-record.md, PLAN-023.02-search-domain-matrix.md, PLAN-023.03-evidence-contract.md
PLAN-048-idea-realization-plugin/
  PLAN-048-overview.md
  PLAN-048.01-skeleton-install.md … PLAN-048.11-absolutes-two-trace.md (11 children)
PLAN-050-system-boundary-study/
  PLAN-050-overview.md
  PLAN-050.01-system-inventory.md … PLAN-050.05-boundary-decision-report.md (5 children)
not a plan document, directly under docs/01-plans/: ['docs/01-plans/README.md']
```

The output above is abridged where it shows `…`; the command prints every file.

**Every file in every folder is a governed plan document.** No folder holds a requirement, a
decision record, a prompt, a review record, a session record or an evidence file.

Naming, as observed:

- The folder is `PLAN-NNN-<slug>/`.
- The entry point is `PLAN-NNN-overview.md` in all five folders.
- Children are `PLAN-NNN.NN-<slug>.md`.
- Only `PLAN-017` uses area folders (four, with spaces in their names: `Idea Architecture/`,
  `Plan Architecture/`, `The Idea Lifecycle/`, `The Plan Lifecycle/`). `GOV-005` permits one level.

Why a folder can hold nothing else today. Three checks in `src/governance/` apply:

1. `markdown_paths` in `src/governance/__main__.py` collects every `.md` file under `docs/` except
   the exact files in `EXEMPT` and anything under `EXEMPT_DIRS = ("docs/00-working/",)`. Every
   collected file must have front matter. `test/test_governance.py`,
   `test_new_readme_is_not_an_exemption`, asserts that `docs/01-plans/extra/README.md` without
   front matter fails.
2. `location_error` in `src/governance/codes.py` requires each kind to sit under the locations
   `docs/08-governance/codes.yaml` gives it. `PLAN` is the only series located in
   `docs/01-plans/`. A requirement, ADR or prompt placed there fails.
3. `naming_errors` requires a document inside a folder to sit in a folder whose name starts with
   the document's own code stem. A `REQ-033` document inside `PLAN-050-system-boundary-study/` would
   also fail this.

Files that are not Markdown are not scanned at all. A JSON, YAML or CSV file inside a plan folder
raises no governance error today.

## 3. What belongs to a plan but lives outside it

### Link types used below

| Link | Direction | Where it is written |
|---|---|---|
| Plan `depends_on` | plan → artifact | the plan's front matter |
| Artifact `depends_on` | artifact → plan | the artifact's front matter |
| Phase `plan` | phase → plan | `docs/09-backlog/backlog.yaml`, by document id |
| Phase `sources` | phase → artifact | `backlog.yaml` |
| Phase `deliverables` | phase → path | `backlog.yaml` |
| `completion_evidence` | plan → path | a complete plan's front matter |
| Review `target.plan` | review → plan | the review record's JSON, by document code |
| Code in prose | either | body text: a `PLAN-NNN` code or a phase id |

A "plan family" below is a top-level plan together with its children.

### 3.1 Scatter across the repository

```text
$ uv run python docs/00-working/plan-anatomy/measure.py scatter
```

| Kind | Total | Plan-side link to one plan | Plan-side link to several | Only the artifact names the plan | Prose mention only | No link |
|---|---|---|---|---|---|---|
| requirement | 34 | 31 | 1 | 1 | 1 | 0 |
| adr | 22 | 8 | 6 | 5 | 2 | 1 |
| prompt | 41 | 9 | 0 | 15 | 12 | 5 |
| session | 168 | 1 | 0 | 138 | 23 | 6 |
| architecture | 12 | 2 | 3 | 3 | 1 | 3 |
| governance | 18 | 1 | 9 | 1 | 3 | 4 |
| operation | 22 | 1 | 0 | 4 | 12 | 5 |

"Plan-side link" means the plan's `depends_on` or one of its phases' `sources` names the artifact.
"Only the artifact names the plan" means the artifact's own `depends_on` names a plan and nothing
on the plan side names the artifact back. Artifacts with no structured link are split by whether
their text mentions a plan code or one of a plan's phase ids.

Shared artifacts, from the same command:

- One requirement is shared: `REQ-007` (the workbench requirement) by `PLAN-022`, `PLAN-027` and
  `PLAN-028`.
- Six ADRs are shared: `ADR-001` (033, 035), `ADR-003` (026, 032, 038), `ADR-010` (015, 016,
  025), `ADR-014` (022, 027), `ADR-015` (022, 027, 028), `ADR-016` (022, 028).

**Review records.** 12 JSON files under `docs/08-governance/reviews/`. 11 target a plan code,
covering 10 plans: `PLAN-010`, `PLAN-029`, `PLAN-030`, `PLAN-039`, `PLAN-045` (two records),
`PLAN-046`, `PLAN-047`, `PLAN-048`, `PLAN-051`, `PLAN-052`. The twelfth,
`2026-09-23-sample-nonconforming-draft`, targets a path under `_working/`. A record names its plan
by code in `target.plan`. Eight of the ten plans name their own review record's id in their text
(`grep -rn -E "20[0-9]{2}-[0-9]{2}-[0-9]{2}-plan-" docs/01-plans`): `PLAN-029`, `PLAN-030`,
`PLAN-045`, `PLAN-046`, `PLAN-047`, `PLAN-048`, `PLAN-051` and `PLAN-052`. `PLAN-010` and
`PLAN-039` do not; `PLAN-045` names the records for `PLAN-010` and `PLAN-030`. `test/test_adversarial_finding_schema.py` validates
every record it finds with `REVIEWS_DIR.glob("*.json")`, one directory deep.

**Session records.** 168 governed `SESS` documents. 138 name a plan in their own `depends_on`;
one plan names a session back. 23 mention a plan only in prose; 6 have no link.

### 3.2 Decisions: three homes

Decisions about a plan are written in three places.

1. **Inside the plan.** 51 of 81 plan documents, and 29 of 49 top-level plans, have an H2 heading
   of a decision type (`Decisions`, `The chosen design`, `Chosen design`, `Design`, `Approach`,
   `Owner rulings`, and three variants; `measure.py decisions`). The seven top-level plans
   written under `GOV-010` put a large share of their words there:

   | Plan | Words in the body | Words under decision headings | Share |
   |---|---|---|---|
   | `PLAN-045` | 3,438 | 1,420 | 41% |
   | `PLAN-046` | 2,455 | 1,226 | 50% |
   | `PLAN-047` | 2,106 | 905 | 43% |
   | `PLAN-048` (overview) | 1,915 | 847 | 44% |
   | `PLAN-050` (overview) | 429 | 54 | 13% |
   | `PLAN-051` | 2,741 | 1,563 | 57% |
   | `PLAN-052` | 2,651 | 871 | 33% |

   Each decision in these plans opens with one bold sentence stating the ruling, followed by the
   reason, the alternatives rejected and what each would have cost. `PLAN-051` D1 is an example:
   the ruling is one sentence ("Definitions are tracked; the setting in force is a gitignored
   file in the primary checkout"), and the remaining 135 words give who chose it, why, and two
   rejected alternatives. `GOV-010` P2 and P3 require that second part to be in the plan.

2. **ADRs** in `docs/04-decisions/`: 22. By a plan-side link, 8 belong to one plan and 6 are
   shared by two or three (section 3.1). 5 point at a plan only from their own side; 3 have no
   structured link to any plan.

3. **The accepted-decisions record (`GOV-003`)**: 22 `##` sections. 15 name a plan code or a
   phase id; 7 are repository-wide rulings with no plan or phase named
   (`measure.py gov003`).

### 3.3 Prompt packs and prompts

41 governed `PROMPT` documents in `docs/02-prompts/` (`measure.py prompts`). By structured link:
9 are named by a plan or its phases, 15 name a plan from their own side only, 12 mention a plan
only in prose, and 5 have no link to any plan (`PROMPT-013`, `PROMPT-015`, `PROMPT-016`,
`PROMPT-032`, `PROMPT-038`).

The per-build packs cluster by build:

| Build | Prompts | Plan | How the prompts reach the plan |
|---|---|---|---|
| Live demo | `PROMPT-010` to `PROMPT-019` | `PLAN-021` | `PLAN-021` names `PROMPT-010` to `017` in prose; `PROMPT-018` and `019` name it in their own `depends_on`; `PROMPT-013`, `015`, `016` have no structured link and no plan code or phase id in their text |
| Workbench | `PROMPT-020` to `PROMPT-024` | `PLAN-022` | `PLAN-022` names all five in prose. `PROMPT-020`, the pre-plan package, names `PLAN-021` in `depends_on`, not `PLAN-022` |
| Idea batching | `PROMPT-025`, `026`, `032`, `033` | `PLAN-025` | `PROMPT-025` and `026` name the idea record plan (`PLAN-016`) in their own `depends_on`, not `PLAN-025`; `PLAN-025` names `PROMPT-032` and `034` in prose; `PROMPT-032` itself has no link |
| Literature review | `PROMPT-027` to `PROMPT-031` | `PLAN-023` | `PLAN-023` names `027`, `028` in `depends_on`; `029`, `030`, `031` name it back |
| Boundary study | `PROMPT-041` | `PLAN-050` | `PROMPT-041` names the plan in `depends_on` |

A pre-plan package is written before its plan exists, so it cannot name that plan. Two of them
(`PROMPT-020`, `PROMPT-025`) name an earlier plan they build on instead, and no later edit points
them at the plan they led to.

Some prompts serve many plans rather than one: the reusable partition pack (`PROMPT-034`), the
queued-phase review pack (`PROMPT-035`), the build coordinator (`PROMPT-036`), the Session Manager
starter messages (`PROMPT-037`) and the single-adversary engine (`PROMPT-038`).

Ungoverned prompts also exist. `docs/00-working/` holds four `PROMPT-session-taxonomy-*.md` files
that the session-taxonomy plan (`PLAN-042`) cites by path, and the folders `cloud-prompts/`,
`gemini/` and the files `overnight-run-prompt-2026-09-15.md` and `chatgpt-plugin-audit-prompt.md`.

### 3.4 Requirements

34 requirement documents. 31 are named by exactly one plan family's `depends_on` or phase
`sources`; `REQ-007` is named by three. Most requirements also name, in their own `depends_on`, an
earlier plan they build on. That is why a first count that mixes both directions shows 11
requirements linked to two or more plans; counted from the plan side only, it is one.

### 3.5 Evidence and outputs

Phase `deliverables` put a plan's outputs wherever the work belongs:

- the literature review campaign (`PLAN-023`): 14 files under `research/literature-review/`;
- the system boundary study (`PLAN-050`): 6 files under `docs/00-working/boundary-study/` and one
  under `docs/07-architecture/`;
- the idea-realization plugin (`PLAN-048`) and its remediation (`PLAN-052`): files under
  `plugins/idea-realization/`, plus the two trace tables typed as child plans (section 1).

A complete plan's `completion_evidence` lists paths; the document code plan (`PLAN-005`) lists six,
among them the ADR that records its decision (`ADR-006`), which has no other link to the plan.

### 3.6 Backlog phases

Every phase names its plan by document id in the `plan` field. The field holds an id, not a path,
so it does not depend on where the plan file sits. 45 lines of `docs/09-backlog/backlog.yaml`
contain a path under `docs/01-plans/` (`git grep -c -E '01-plans/PLAN-' -- docs/09-backlog/backlog.yaml`),
mostly in `deliverables`.

### 3.7 Seven plans traced

Chosen for spread of size, age, layout and status: `PLAN-005` (complete, 2026-09-05, single file),
`PLAN-022` (active, 2026-09-10, single file, prompt pack), `PLAN-023` (draft, 2026-09-12, folder,
prompt pack and research outputs), `PLAN-029` (active, 2026-09-14, single file, 20 phases),
`PLAN-048` (approved, 2026-09-25, folder with 11 children), `PLAN-050` (draft, 2026-09-26, folder,
outputs in `docs/00-working/`), `PLAN-052` (draft, 2026-09-27, single file). Command:
`measure.py trace <codes>`. "Belongs" below means written for this plan; documents that only cite
the plan as an example are left out.

| Artifact | `PLAN-005` document codes | `PLAN-022` workbench | `PLAN-023` literature review | `PLAN-029` idea graph | `PLAN-048` plugin | `PLAN-050` boundary study | `PLAN-052` plugin remediation |
|---|---|---|---|---|---|---|---|
| Requirement | `REQ-001`: plan `depends_on`, phase `sources` | `REQ-007`: plan `depends_on`, phase `sources`; shared with `PLAN-027`, `PLAN-028` | none; the campaign's scope record is child `PLAN-023.01` | `REQ-014`: plan `depends_on`, phase `sources` | `REQ-031`: plan `depends_on`, phase `sources` | `REQ-033`: plan `depends_on`, phase `sources` | `REQ-035`: plan `depends_on`, phase `sources` |
| Decisions in the plan | none under a decision heading | none under a decision heading | none under a decision heading | `The chosen design`, 992 words | `Decisions` in the overview and in each of `.01`–`.09` | `Chosen design` and `Approach` sections, 13–19% | `Decisions`, 871 words |
| Decision records outside | `ADR-006`: `completion_evidence` only; `GOV-003` "Root plans/ is retired": prose | `ADR-014`, `015`, `016`: plan `depends_on`, phase `sources`; `GOV-003`: 8 lines, prose | none | `ADR-024`: its `depends_on`; `ADR-019` reserved for `phase-idg-11`; `GOV-003`: 22 lines, prose | none | `ADR-017`: phase `sources` | `ADR-025`: plan `depends_on`, phase `sources` |
| Prompts | none | `PROMPT-020`–`024`: plan prose; `021`, `022`, `024` also name the plan | `PROMPT-027`–`031`: plan `depends_on` and theirs | none written for it | none; `PLAN-048.03` cites the reusable `PROMPT-034` | `PROMPT-041`: its `depends_on` | none |
| Review record | none (exempt era) | none | none | `2026-09-24-plan-029-idg-split`: `target.plan`; plan prose | `2026-09-25-plan-048`: `target.plan`; plan prose | none | `2026-09-27-plan-052`: `target.plan`; plan prose |
| Session records | 1 by its `depends_on` | 15 by `depends_on`, 10 prose only | 13 by `depends_on`, 14 prose only | 4 by `depends_on`, 13 prose only | 9 by `depends_on` | 6 by `depends_on` | none yet |
| Backlog phases | 6 (`phase-doc-*`) | 10 (`phase-wb-*`) | 9 (`phase-lit-*`) | 20 | 9 (`phase-plug-*`) | 5 (`phase-bnd-*`), on the children | 6 (`phase-plfx-*`) |
| Evidence and outputs | `completion_evidence`: 6 paths | `_data/workbench/`, `src/`, `ts/`, `test/`; the plan cites `docs/00-working/handoff-workbench-layout-and-terminal-fixes.md` | `research/literature-review/` (14 files) | spread over `docs/`, `schemas/`, `src/`, `tools/`, `.claude/`; the plan cites `docs/00-working/idea-batching-partition.md` | `plugins/idea-realization/`; trace tables `PLAN-048.10`, `.11` | `docs/00-working/boundary-study/` (6 files), `ARCH-012` | `plugins/idea-realization/`; its input, the audit report, is `docs/00-working/chatgpt-plugin-audit-report.md` |
| Paths the plan cites that a clone cannot open | none | none | none | none | 5 under `_working/session-manager/` | none | 1 under `_working/session-manager/` |

## 4. What this inventory cannot see

- **`_working/`** is gitignored and absent from this clone. Ephemeral task plans live there
  (`AGENTS.md`, "Key conventions"; `PLAN-015`). The inventory excludes them entirely.
  Six distinct `_working/` paths are cited by tracked plans: `PLAN-048-overview.md` cites
  `_working/session-manager/plugin-analysis/` and `restart-2026-09-25.md`; `PLAN-048.01` cites
  `reports/rulings-000347.md` and `scout/ext-ecc.md`; `PLAN-048.08` cites
  `plugin-build-2026-09-25.md`; `PLAN-052` cites `reports/plugin-audit-validation.md`. Whether
  those files still exist cannot be checked from here.
- **`_private/`** is not in the clone and was not read.
- **Unpushed branches, the local board, and other sessions** are not visible.
- **Why** a document was placed where it is: the inventory reads placement and links, not intent.

## 5. What depends on the plan layout

Searched with `git grep -n -E "01-plans|PLAN-|\"plan\"|'plan'" -- src tools test`, then
`git grep -n -E "08-governance/reviews|reviews/"`, and a read of the functions named.

| File | What it assumes about plans | Kind of dependency |
|---|---|---|
| `docs/08-governance/codes.yaml` | `PLAN` is located in `docs/01-plans/`; every other series has its own directory | configuration read by the check |
| `src/governance/codes.py`, `location_error` | a document's path starts with its series' location | check |
| `src/governance/codes.py`, `naming_errors` | filename starts with the code; a containing folder starts with the code stem; at most one area folder; the overview is not in an area folder | check |
| `src/governance/codes.py`, `parent_errors` | a sub-code and `parent` imply each other | check; independent of paths |
| `src/governance/__main__.py`, `markdown_paths`, `EXEMPT`, `EXEMPT_DIRS` | every `.md` under `docs/` outside the exemptions is governed and needs front matter | check |
| `test/test_codes.py` lines 262–336, 363–384 | fixtures for the naming and folder rules above | tests of those rules |
| `test/test_governance.py`, `test_new_readme_is_not_an_exemption` | an unexempted `.md` in a plan folder fails | test |
| `test/test_adversarial_finding_schema.py` | review records are `docs/08-governance/reviews/*.json`, one level | test |
| `GOV-018` step 1 script | `depends_on` targets are one directory below `docs/` (the fault in section 1) | procedure script, not code |
| `plugins/idea-realization/scripts/codes.py` and `test/test_codes.py` | the same naming and folder rules, for the plugin's `plans/` directory | separate copy of the rules |
| `src/api/routes/workbench.py:497`, `tools/check_dev_ci.py:31`, `tools/check_no_private_content.py:36`, `tools/lit_report_extract.py:4`, `.claude/commands/resume-lit-review.md:26` | a plan's current path, in a comment, docstring or table | prose only; nothing reads the path at run time |

The backlog's `plan` field, `parent`, `depends_on`, a review's `target.plan` and the catalog all
identify a plan by id or code, not by path. The catalog is regenerated by `--catalog`.

Path references to single-file plans, which a move would leave pointing at nothing:

| Measure | Count | Command |
|---|---|---|
| References of the form `01-plans/PLAN-NNN-<slug>.md` that resolve to an existing file, catalog excluded | 263, in 94 files | `git grep -o -E '01-plans/PLAN-[0-9]{3}(\.[0-9]{2})?-[a-z0-9-]+\.md' -- . ':!docs/08-governance/catalog.md'`, each result tested with `-f` |
| Of those, in `_data/ideas.jsonl` | 8 | same, grouped by file |
| Of those, in `docs/09-backlog/backlog.yaml` and `docs/09-backlog/README.md` | 34 and 38 | same |
| Links written as a bare sibling filename inside `docs/01-plans/` | 103 | `git grep -o -E '\]\((\./)?PLAN-[0-9]{3}(\.[0-9]{2})?-[a-z0-9-]+\.md' -- docs/01-plans` |

`_data/ideas.jsonl` is append-only: existing lines are never rewritten (`PLAN-016`, and `REQ-014`
R21's "byte-identical" check). A reference in it cannot be updated after a move.
