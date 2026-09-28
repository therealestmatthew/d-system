# Plan anatomy: findings

*Ran unclaimed: owner-directed work with no backlog phase; no peer holds a lock against it.*

Idea `000505` (re-investigate the anatomy of a plan and of a plan folder). This file answers the
owner's questions from [inventory.md](inventory.md). Under each question, **What the inventory
shows** is measured; **Options** gives what each choice costs; **Recommendation** is this
session's view, for the owner to accept or reject. A recommendation is never stated as a
finding.

The owner's question, as given (2026-09-27):

> "we need to reinvestigate the anatomy of a plan that we created and look at the anatomy of a
> plan folder ... Should we have a separate document just to hold the decisions for the plan and
> should all plans be in a folder? No free form plan files or even if the plan is a single file to
> start, should it still be in a folder? The decision should be kept separate from the plan. So we
> can trace back to them, but the specific decisions and reasoning is only necessary for auditing,
> not for actually planning. We might need a separate file or folder for the various prompt packs.
> Do we put all of this in the plan folder? I think it's currently scattered throughout the
> repository. Maybe some more investigating to do here."

## Layout tests

Some costs below depend on what the governance check accepts. They were tested, not reasoned.
Method: `git archive HEAD` into a scratch directory outside the repository, add one file, run
`python -m src.governance` there, remove the file. A throwaway plan `PLAN-099` was created as
`docs/01-plans/PLAN-099-folder-test/PLAN-099-overview.md`, copied from `PLAN-052` with its code,
id and status changed to `deprecated` so that the backlog-coverage rule did not fire. "Catalog
stale" is the message every new document produces until `--catalog` is run; it is not a layout
error.

| Test | Governance check result |
|---|---|
| (a) A single-file plan created as a folder holding only `PLAN-099-overview.md` | catalog stale only; no layout error |
| (b) An uncoded `decisions.md`, no front matter, inside that folder | `ERROR …/decisions.md: missing opening front matter delimiter` |
| (c) A `review.json` and an `evidence/t.csv` inside that folder | catalog stale only; non-Markdown files are not scanned |
| (d) A governed requirement `REQ-099-test.md` inside that folder | `ERROR …/REQ-099-test.md: requirement belongs under docs/06-requirements/` |
| (e) A decision record typed as child plan `PLAN-099.01-decisions.md`, with `depends_on: [doc-folder-test]` | catalog stale only. The `GOV-018` entry check on it: missing Context, Design, Work, Verification, Boundaries, Open questions and Requirement coverage; exit 1. The last of the seven is the entry-check fault (its parent is in a folder); the other six are real |

## 1. Should every plan be a folder, even when it is one file?

### What the inventory shows

- 44 of 49 top-level plans are single files; 5 are folders (`PLAN-003`, `PLAN-017`, `PLAN-023`,
  `PLAN-048`, `PLAN-050`).
- Every file in every folder is a plan document: an overview and its sub-coded children. No
  folder holds anything else, and the governance check allows nothing else in Markdown (tests b
  and d). A folder today means "a plan with child plans", not "a plan with its artifacts".
- The rule in the governing document is folder-when-there-are-children: `GOV-005`, "Multi-file
  plans": "A plan set lives in a folder named for the parent code". The check does not enforce it.
  The orchestrator design (`PLAN-039.01`) is a child stored flat beside its parent.
- A one-file plan can already be created as a folder with no code change (test a).
- Two trace tables (`PLAN-048.10`, `PLAN-048.11`, 13,915 and 18,945 words) are records produced
  by phases, typed as child plans. In a plan folder, only a plan document can be Markdown.
- Moving an existing single-file plan leaves references behind. There are 263 path references to
  single-file plans in 94 files, 103 bare sibling links inside `docs/01-plans/`, and 8 references
  in the append-only idea log (`_data/ideas.jsonl`), which cannot be edited.
- The `GOV-018` entry-check script misreports any plan whose `depends_on` names a document inside
  a plan folder: it demands a "Requirement coverage" section that the rules do not require
  (inventory, section 1). This accounts for 11 of the 13 entry-check failures today. The more
  plans are folders, the more plans it misreports.

### Options

| Option | What changes | Cost |
|---|---|---|
| **1A. Keep the current rule**: a folder only when a plan has children | Nothing, apart from resolving the flat child `PLAN-039.01` | Either move `PLAN-039` and `PLAN-039.01` into a folder (2 moves; their inbound references would need rewriting), or leave them and state the exception. Enforcing the rule means one more condition in `naming_errors` and one test in `test/test_codes.py` |
| **1B. Every new plan starts as a folder; existing plans stay where they are** | `GOV-005` "Multi-file plans" text; the plans README; the plan template's instructions | No code change for placement (test a). The entry-check fault must be fixed first, or every plan that depends on a newer plan is misreported. `PLAN-039.01` is resolved as in 1A |
| **1C. Every plan is a folder, and the 44 existing single files move** | Everything in 1B, plus 44 file moves | 263 path references in 94 files and 103 sibling links to rewrite or leave broken. 8 references in `_data/ideas.jsonl` stay broken, because the log is append-only. Session records are historical; rewriting their links changes history, and leaving them breaks the links. The plugin's copy of the rules (`plugins/idea-realization/scripts/codes.py`) is unaffected either way |

### Recommendation

A folder only pays for itself if something other than plan documents can go in it. That depends on
questions 2 and 3. Under 1A or 1B with no member files allowed, a folder for a one-file plan adds a
directory and nothing else.

**1B**, adopted together with the answer to question 2. Starting a plan as a folder costs nothing
now (test a) and avoids a later move when the plan gains a child or a member file. The move is the
expensive step in 1C, and part of its cost (the idea log) cannot be paid at all. Existing plans
move only if the owner asks. Fix the entry-check script first, whichever option is taken: it
misreports today.

## 2. Should decisions be kept in a separate document, traceable from the plan?

### What the inventory shows

`GOV-010` currently requires decisions, with their reasoning, inside the plan. Its plan-section
table:

> | Design | always | `Decisions`, `The chosen design`, `Chosen design`, `Design`, `Approach`, `This is an investigation plan`, `This is a discovery plan` |

and its content judgements:

> ### P2. Each decision names the alternative it rejected and what that alternative would have cost
>
> "Chosen because it is good" is not a reason. The reason is what the rejected option would have
> cost here.

> ### P3. It is clear who decided each thing and whether it is settled
>
> A settled decision is stated flatly, with who ruled and when.

`GOV-010` also limits its own reach: "Existing documents are neither retrofitted to it nor judged
non-compliant by it."

Measured:

- In the six top-level plans written under `GOV-010` that carry numbered decisions, decision
  sections are 33% to 57% of the words (`PLAN-045` 41%, `PLAN-046` 50%, `PLAN-047` 43%, `PLAN-048`
  44%, `PLAN-051` 57%, `PLAN-052` 33%). `PLAN-050` is 13%.
- Those six plans carry 60 numbered decisions: 11, 7, 7, 13, 11 and 11
  (`grep -cE '^(\*\*|- \*\*)D[0-9]+\.'` on each).
- Each decision has two parts: one sentence stating the ruling, then who ruled, the reasons and
  the alternatives rejected with their cost. In `PLAN-051` D1 the ruling is one 15-word sentence and
  the rest is 135 words.
- The ruling is read during execution, not only in audit. The orchestrator code cites the
  orchestrator design's sections for the rulings it implements; for example
  `src/orchestrator/tick.py:198`: "PLAN-039.01 section 4: the watermark initializes to *now* on
  first start".
- Decisions have three homes: the plan (51 of 81 plan documents have a decision heading), ADRs (22;
  6 of them shared by two or three plans), and the accepted-decisions record (`GOV-003`: 22
  sections, 15 naming a plan code or phase id).

What separating decisions would change for review:

- **`GOV-018`'s entry check** reads headings only. If the plan keeps a `## Decisions` heading with
  one line per ruling, it still passes. If the heading moves out with the decisions, the plan fails
  "Design".
- **The plan-altitude attack** (`GOV-018` step 3, `PROMPT-038`) checks that "each decision names
  the alternative it rejected". With the reasoning in another file, the adversary has to be given
  that file as well. `GOV-018` step 2 lists what the adversary receives: the plan and its
  requirement. The review record's `target` (`schemas/adversarial-finding.schema.json`) has
  `additionalProperties: false`, so naming a decisions file there needs a schema change. Leaving it
  unnamed works only if the decisions file is defined as part of the plan.
- **`GOV-010` P2 and P3** are judged "against the plan" today. They would be judged against the
  decision record, which is a text amendment to `GOV-010`.
- **Dispositions** (`GOV-018` step 5): a `fixed` disposition names "the document and section".
  A fix to a decision's reasoning would name the decision record. The schema needs no change.

### Options

| Option | What changes | Cost |
|---|---|---|
| **2A. Keep decisions in the plan** | Nothing | None. The plan stays the single file an agent and a reviewer read. The owner's point stands: in recent plans, a third to over half of what an executing agent loads is reasoning it does not act on |
| **2B. Split the ruling from its record.** The plan keeps `## Decisions` with one line per decision (number, ruling, link). A decision record in the plan's folder holds who ruled and when, the reasons, and the alternatives with their costs | `GOV-010` P2, P3 and the Design row's wording; `GOV-018` step 2 (dispatch both files); the plan template | Needs the plan to be a folder (question 1). The record's form is a sub-choice, below |
| **2C. Move every decision to an ADR** | Each plan decision becomes an ADR in `docs/04-decisions/`; the plan cites them | At the measured rate, about 60 ADRs for six plans, against 22 ADRs in the repository today. ADRs are allocated one code each and live away from the plan. Suits decisions that bind more than one plan, as the six shared ADRs already do |

Sub-choice for 2B, the form of the decision record:

| Form | Governance check | Cost |
|---|---|---|
| **2B-i. An uncoded member file** `decisions.md`, no front matter, part of the plan | Fails today (test b) | `markdown_paths` in `src/governance/__main__.py` must skip that one filename inside plan folders; `test/test_governance.py` gains a case, and `test_new_readme_is_not_an_exemption` must still pass; `GOV-001` "Only the exact navigation files…" gains the exemption. The record is not in the catalog; it is reached from the plan |
| **2B-ii. A sub-coded child plan** `PLAN-NNN.NN-decisions.md` | Passes today (test e) | The entry check and `GOV-018` treat it as a plan to review and demand six plan sections it cannot sensibly have (test e). This is the pattern the two `PLAN-048` trace tables already follow |
| **2B-iii. A new document kind** with its own series, located in plan folders | Fails today (test d, by analogy) | A new series in `codes.yaml` and `schemas/`; `location_error` and `naming_errors` changes, because a folder must today start with the document's own code stem; one code per plan spent on the record; catalog rows |

### Recommendation

**2B with 2B-i**, for plans written after the owner adopts it. Existing plans are not rewritten,
which matches `GOV-010`'s own scope rule. A decision that binds more than one plan, or the
repository, stays an ADR, as `ADR-003`, `ADR-010` and `ADR-014` to `ADR-016` are today. A
backlog or process ruling stays in `GOV-003`. This keeps the ruling where the executing agent reads
it and moves only the reasoning, which is what the owner described as needed "only for auditing".

## 3. Where should prompt packs, review records and session records for a plan live?

### What the inventory shows

**Prompts.** 41 governed prompts in `docs/02-prompts/`. Five are used across plans (`PROMPT-034`
to `PROMPT-038`). Most of the rest were written for one build: the demo pack (`PROMPT-010` to
`019`), the workbench pack (`020` to `024`), the idea-batching pack (`025`, `026`, `032`, `033`),
the literature-review pack (`027` to `031`), and single prompts such as `PROMPT-041`. The link to
the plan is uneven: 9 prompts are named by a plan or its phases, 15 name a plan only from their
own side, 12 only mention one in prose, and 5 have no link. A pre-plan package is written before
its plan, so it cannot name it; `PROMPT-020` and `PROMPT-025` name an earlier plan instead, and
nothing was updated afterwards. Four ungoverned prompts for the session-taxonomy plan (`PLAN-042`)
live in `docs/00-working/`.

`GOV-008` makes each pack stage "a governed prompt document". The owner has since ruled the
pre-plan package optional, and allowed it in `docs/00-working/` when it will not be re-run, has no
owner gates and needs no review of its own (planning protocol, `GOV-021`, step 4). Idea `000501`
asks for the goal "to not have governed prompts that are one time use".

**Review records.** 12 JSON files in `docs/08-governance/reviews/`, fixed there by `GOV-018` step
4. 11 name their plan by code in `target.plan`, which does not depend on paths. Eight of the ten
reviewed plans name their record's id in their own text. The schema test reads the directory one
level deep. `GOV-018` says the gate queue (`phase-irs-13`) and the learning loop (`phase-irs-10`)
read the record format, and `phase-irs-10`'s scope routes "recurring adversarial findings" from
across reviews. The reviewer-contract plan (`PLAN-047`) adds `reviews/verdicts/`. One record
targets a draft under `_working/` that has no plan folder.

**Session records.** 168, all in `docs/03-sessions/` under the dated `SESS` series. 138 name a
plan in their own `depends_on`; 10 name two or more plan families. A session record belongs to a
session, and a session may serve more than one plan.

### Options

Prompts:

| Option | Cost |
|---|---|
| **3P-A. Stay in `docs/02-prompts/`**; the plan names its prompts in `depends_on` or a pointer list | No moves. Back-links for existing packs are optional edits. `PROMPT-020` and `PROMPT-025` keep pointing at the wrong plan unless edited |
| **3P-B. One-time prompts for a plan go in a `prompts/` member folder, ungoverned; reusable prompts stay governed in `docs/02-prompts/`** | Same kind of scan exemption as 2B-i, for `prompts/**` inside plan folders. `GOV-008`'s "governed prompt document" wording changes for per-build stages. Existing governed prompts keep their codes: a code is permanent (`GOV-005`, Permanence), so moving one out of governance means retiring its code, which is `000501`'s decision to make, not this one |
| **3P-C. Governed prompts inside plan folders** | `codes.yaml` gives `PROMPT` a second location; `naming_errors` changes, because a folder must start with the document's own code stem; the workbench prompt route (`src/api/routes/workbench.py`) lists only files directly under `docs/02-prompts/` and would miss them |

Review records:

| Option | Cost |
|---|---|
| **3R-A. Stay in `docs/08-governance/reviews/`**; the plan names its record id | None beyond the habit already followed by eight of ten plans. Cross-plan readers (`phase-irs-10`, `phase-irs-13`) read one directory |
| **3R-B. Move into a `reviews/` member folder in each plan folder** | JSON is not scanned, so governance is unaffected (test c). `test/test_adversarial_finding_schema.py`'s glob, `GOV-018` step 4, `PLAN-047`'s verdicts path and the specifications of `phase-irs-10` and `phase-irs-13` change. A review of a draft with no code (the `_working/` sample) has no folder to go in |

Session records: **stay in `docs/03-sessions/`**. No other option is costed: the `SESS` series is
located in `docs/03-sessions/` by `codes.yaml`, and ten sessions serve more than one plan family.

### Recommendation

- **Prompts: 3P-B for new one-time prompts, with the boundary between "one-time" and "reusable"
  left to `000501`.** Reusable prompts stay governed. Nothing already governed moves.
- **Review records: 3R-A.** They are already linked by code, the consumers are cross-plan, and
  the review procedure fixes the location. Keep the habit of naming the record in the plan.
- **Session records: stay where they are.**

## 4. How scattered is it today?

From the inventory:

| What | Where it is | How it reaches the plan |
|---|---|---|
| The plan itself | `docs/01-plans/` (44 files, 5 folders, 1 flat child) | — |
| Requirement | `docs/06-requirements/` (34) | plan `depends_on` for 31 of 34; one shared by three plans |
| Decisions | plan body (51 of 81 plan documents); `docs/04-decisions/` (22 ADRs, 6 shared); `GOV-003` (15 of 22 sections name a plan or phase) | ADRs: plan-side link for 14 of 22; `GOV-003`: prose only |
| Prompts | `docs/02-prompts/` (41); `docs/00-working/` (4 prompt files and several prompt folders) | plan-side link for 9 of 41 |
| Review records | `docs/08-governance/reviews/` (12) | `target.plan` by code for 11; the plan names the record in 8 of 10 reviewed plans |
| Session records | `docs/03-sessions/` (168) | the session's own `depends_on` for 138; the plan side names one |
| Phases | `docs/09-backlog/backlog.yaml` | the phase's `plan` field, by id, for every phase |
| Outputs and evidence | wherever the work belongs: `research/`, `plugins/`, `docs/00-working/`, `src/` | phase `deliverables`; `completion_evidence` for complete plans |
| Other governed documents the plan builds on | `docs/07-architecture/`, `docs/08-governance/`, other plans | plan `depends_on`: of 49 plan families, 23 name a governance document, 13 another plan and 6 an architecture document; in the seven traced plans, 6 of 7 name one or more (inventory, 3.7) |
| Evidence the plan cites but a clone cannot open | `_working/` (6 distinct paths, cited by `PLAN-048` and `PLAN-052`) | a path in prose |

A plan's artifacts sit in at least seven directories. The links run mostly from the artifact to the
plan. From the plan itself, a reader can reach its requirement (by `depends_on`) and its phases (by
searching the backlog), and sometimes its review record (by id in prose). The plan does not list
its prompts, sessions or decision records outside itself in any consistent way.

### Reading (this session's view, not a measurement)

The numbers support the owner's impression that a plan's material is scattered. Two parts of the
scattering have a reason that the inventory shows: artifacts shared by several plans (one
requirement, six ADRs, ten sessions) cannot live in one plan's folder, and cross-plan readers such
as the review test read one directory. For per-plan prompts and decision reasoning, this session
found no recorded reason for where they are; that is an absence of evidence, not a finding that
there is no reason.

## Other findings

These surfaced while measuring and are not answers to the owner's four questions.

1. **The `GOV-018` entry-check script misreports plans that depend on a document inside a plan
   folder.** Its `depends_on` lookup searches `docs/*/*.md` only, and `xargs -r` exits 0 when
   the lookup is empty, so the script demands a "Requirement coverage" section. Evidence and
   commands: inventory, section 1. The plugin's `plan_check.py` resolves ids properly and could be
   the model for a fix. Whether to fix `GOV-018`'s script is for the owner; it is a governed
   document.
2. **`GOV-005`'s "a plan set lives in a folder" is not enforced**, and `PLAN-039.01` is the one
   child stored flat.
3. **Records typed as plans.** `PLAN-048.10` and `PLAN-048.11` are trace tables, typed as child
   plans with plan headings added, because only plan documents can be Markdown in a plan folder.
4. **Tracked plans cite `_working/` evidence.** Six distinct paths, in `PLAN-048` and `PLAN-052`.
   A reader of the repository, or a cloud session, cannot open them.
5. **Pre-plan packages point at the wrong plan.** `PROMPT-020` (workbench pre-plan package) names
   the live-demo plan (`PLAN-021`); `PROMPT-025` and `PROMPT-026` (idea batching) name the idea
   record plan (`PLAN-016`). Each was written before the plan it led to existed.
6. **The planning protocol (`GOV-021`)**, merged before this session, was read. Nothing in it is
   contradicted by this inventory. It points to `GOV-005` "Assigning a code" for step 6 and not to
   `GOV-005` "Multi-file plans", which is where the current folder rule is written.

7. **The plans README is stale.** `docs/01-plans/README.md` says "Name files descriptively:
   `YYYY-MM-DD-topic.md`", while `GOV-005` requires `<code>-<slug>.md` and the check enforces it.
   It also says "existing root `plans/` paths remain for compatibility"; root `plans/` was retired
   by the plans-directory consolidation (`PLAN-018`), and `GOV-001` says it "no longer exists".

## Related ideas

`000501` (archive one-time plans and prompts) decides which prompts count as one-time, which
3P-B depends on. `000502` (how requirements are generated) decides whether a requirement can exist
without a plan, which bears on whether a requirement could ever move into a plan folder; this
investigation keeps requirements outside. `000038` (formalize requirements versus plans), `000047`
(what makes a plan qualitatively good) and `000276` (how decision records are written) touch the
same documents.
