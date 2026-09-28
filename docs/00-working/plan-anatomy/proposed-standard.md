# Plan folder standard: a proposal

*Ran unclaimed: owner-directed work with no backlog phase; no peer holds a lock against it.*

**This is a proposal for the owner. Nothing in it is adopted.** It moves, renames and deletes no
file, registers no phase, allocates no code, and amends no governed document. Idea `000505` (plan
and plan-folder anatomy). The evidence is in [inventory.md](inventory.md); the options and their
costs are in [findings.md](findings.md). This file takes the recommended option from each question
there and states it as one standard, so the owner can accept, change or reject it as a whole or
in parts.

## Scope

It covers plans created after the owner adopts it. Existing plans stay as they are unless the owner
asks for a migration (decision B below). This matches the plan quality standard's own scope rule
(`GOV-010`, Scope: "Existing documents are neither retrofitted to it nor judged non-compliant by
it").

It does not cover where a plan lives before it has a code; that is `phase-idg-11` (see "Overlap with
`phase-idg-11`"). It does not decide which prompts are one-time; that is idea `000501`. It does not
decide how requirements are generated; that is idea `000502`.

## The layout

```text
docs/01-plans/PLAN-NNN-<slug>/
  PLAN-NNN-overview.md        the plan: governed, coded, in the catalog
  PLAN-NNN.NN-<slug>.md       child plans, if any: governed, sub-coded (area folders as GOV-005 allows)
  decisions.md                the decision record: tracked, uncoded, no front matter
  prompts/                    one-time prompts written for this plan: tracked, uncoded
  evidence/                   records about this plan produced by its phases or its review: tracked, uncoded
```

Only the overview is required. `decisions.md` exists when the plan has a Decisions section.
`prompts/` and `evidence/` exist only when they have something in them.

## Rules

1. **Every new plan is a folder**, even when it is one document. The folder is named
   `PLAN-NNN-<slug>/` with the code from `--next-code plan`, as today.
2. **The plan's entry point is always `PLAN-NNN-overview.md`.** All five folders use this name
   today. A fixed name lets a tool or a reader find the plan without reading front matter.
3. **Member names are fixed**: `decisions.md`, `prompts/`, `evidence/`, lowercase. They are the
   only uncoded content a plan folder may hold. An area folder may not use one of these names.
4. **Member files carry no code and no front matter** and do not appear in the catalog. The
   governance check skips exactly these names inside a plan folder and checks everything else as
   it does today. They are tracked, so git history is their audit trail.
5. **The overview links every member it has**, in the block under its title, as the plugin audit
   remediation plan (`PLAN-052`) already does for its requirement, ADR and review record.
6. **Decisions are split into ruling and record.**
   - The overview's `## Decisions` section holds one line per decision: its number, the ruling in
     one sentence, who ruled, and a link to its entry in `decisions.md`. The `GOV-010` entry check
     reads headings only, so this section keeps the plan passing its "Design" row.
   - `decisions.md` holds one `## D<n>. <ruling>` entry per decision: who ruled and when, the
     reasons, the alternatives rejected and what each would have cost, the evidence, and any
     supersession, marked and dated (`GOV-010` P9). `GOV-010` P2 and P3 are judged against this
     file.
   - A decision that binds more than one plan, or the repository, is an ADR, and the plan's line
     links the ADR instead of `decisions.md`. `ADR-003`, `ADR-010` and `ADR-014` to `ADR-016` are
     today's examples of shared decisions. A backlog or process ruling stays in the
     accepted-decisions record (`GOV-003`).
7. **One-time prompts go in `prompts/`.** A prompt that serves more than one plan stays governed
   in `docs/02-prompts/`. Where the line between the two falls is idea `000501`'s decision. A
   pre-plan package written before the plan has a code moves into `prompts/` when the folder is
   created, so it no longer has to name a plan that did not exist when it was written.
8. **Records about the plan go in `evidence/`**: trace tables, audit inputs, validation reports and
   similar files that a phase or a review produced about this plan. A plan's product stays where the
   product belongs: code in `src/` or `plugins/`, a research corpus in `research/`.
9. **A tracked plan does not cite `_working/` as its only copy of evidence.** When a plan relies on
   a file under `_working/`, the file, or the part the plan relies on, is copied into `evidence/`,
   subject to the confidentiality check (`tools/check_no_private_content.py`).

## What stays outside the folder, and why

| Artifact | Stays in | Why |
|---|---|---|
| Requirement | `docs/06-requirements/` | Written before the plan (planning protocol `GOV-021`, step 5), so it exists before the folder does. One requirement (`REQ-007`) serves three plans. Whether a requirement can exist without a plan is idea `000502`. The plan already reaches its requirement by `depends_on` in 31 of 34 cases |
| ADR | `docs/04-decisions/` | Only for decisions that bind more than one plan or the repository (rule 6). Six of today's 22 ADRs are shared |
| Accepted-decisions record | `GOV-003` | Backlog and process rulings. 7 of its 22 sections name no plan at all |
| Review record | `docs/08-governance/reviews/` | Fixed there by the review procedure (`GOV-018`, step 4). Linked by code, not path. Read across plans by the schema test and, as specified, by the learning loop. A review of a draft with no code has no folder to go in. The overview names its record id (rule 5) |
| Session record | `docs/03-sessions/` | Belongs to a session, not a plan; ten sessions serve more than one plan family. The `SESS` series is located there |
| Backlog phases | `docs/09-backlog/backlog.yaml` | One file; the phase names its plan by id |
| Product outputs | wherever the product lives | They are the work, not a record of it (rule 8) |
| Reusable prompts | `docs/02-prompts/` | They serve many plans (rule 7) |
| Ephemeral task plans | `_working/` | Deleted rather than rewritten when the task ends (`AGENTS.md`, "Key conventions"); not tracked |

## Worked example: the plugin audit remediation plan (`PLAN-052`) under this standard

Illustration only. `PLAN-052` is not moved, and the file contents below are abbreviated.

`PLAN-052` today is one file, `docs/01-plans/PLAN-052-plugin-audit-remediation.md`, 2,651 words,
of which 871 are under `## Decisions` (D1 to D11). Its requirement is `REQ-035`; one of its
decisions is an ADR (`ADR-025`, the idea-log lock); its review record is `2026-09-27-plan-052`. Its
input, the audit report, is in `docs/00-working/chatgpt-plugin-audit-report.md`, and the
validation it relies on is in `_working/session-manager/reports/plugin-audit-validation.md`, which
a clone cannot open.

Under the standard:

```text
docs/01-plans/PLAN-052-plugin-audit-remediation/
  PLAN-052-overview.md
  decisions.md
  evidence/
    chatgpt-plugin-audit-report.md          the audit report the plan answers
    plugin-audit-validation.md              the validation, copied from _working/ (rule 9)
```

`PLAN-052-overview.md`, the block under the title:

```markdown
Delivers [REQ-035](../../06-requirements/REQ-035-plugin-audit-remediation.md). Decision record:
[decisions.md](decisions.md). Review record:
[`2026-09-27-plan-052`](../../08-governance/reviews/2026-09-27-plan-052.json), dispositioned.
Evidence: [the audit report](evidence/chatgpt-plugin-audit-report.md) and
[its validation](evidence/plugin-audit-validation.md).
```

`PLAN-052-overview.md`, the Decisions section:

```markdown
## Decisions

- **D1.** Configured paths are contained; `worktree_dir` must be outside. Owner, 2026-09-27.
  [Record](decisions.md#d1-configured-paths-are-contained-worktree_dir-must-be-outside)
- **D2.** `filelock`, pinned, lock file in the git common directory. Owner, 2026-09-27.
  [ADR-025](../../04-decisions/ADR-025-plugin-idea-log-lock.md)
- **D3.** Ideas are recorded only on the integration branch in the primary checkout; the writer
  warns elsewhere. Owner, 2026-09-27. [Record](decisions.md#d3-…)
- … D4 to D11, one line each
```

`decisions.md`, one entry:

```markdown
## D1. Configured paths are contained; `worktree_dir` must be outside

Ruled by the owner on 2026-09-27 in the Session Manager session.

Rejected: an explicit `--allow-outside` flag, which keeps an escape route every script must honour
and test. Also rejected: keeping today's behaviour and changing the manifest wording, which leaves
an absolute path copied from another clone writing silently into that clone.

Cost of the chosen option: anyone who deliberately configured an outside path gets exit 2 after
upgrading.
```

The D1 text above is `PLAN-052`'s own, moved without change. D2 shows the cross-plan case: its
reasoning is already in `ADR-025`, and `PLAN-052` already says "The alternatives and their costs
are in `ADR-025`", so under the standard it has no `decisions.md` entry.

A second case, for comparison: the idea-realization plugin plan (`PLAN-048`) holds two trace tables
typed as child plans (`PLAN-048.10`, `PLAN-048.11`). A new plan of that shape would put them in
`evidence/` with no code and no plan headings.

## Overlap with `phase-idg-11`

`phase-idg-11` (define where a promoted plan lives before it earns a code; `PLAN-029`, queued) will
write the promoted-plan staging decision and protocol. Their codes, `ADR-019` and `GOV-011`, are
reserved in `docs/08-governance/codes.yaml`. This proposal takes neither code.

Where they meet:

1. **The draft's shape.** If the folder is the unit of a plan, the draft location `phase-idg-11`
   defines should hold a folder with the same member names. Promotion is then a rename of one
   folder, and whatever was gathered before the code exists (a pre-plan package, early decisions,
   inputs) moves with it. If `phase-idg-11` defines a single-file draft location first, adopting
   this standard later changes that definition.
2. **Early codes.** `phase-idg-11`'s acceptance builds on `GOV-005`'s reservation mechanism
   ("reserve now, remove if the draft is abandoned"). Reserving the code at promotion would let the
   folder carry its final name from the start. This proposal is consistent with that and does not
   depend on it.
3. **The abandoned draft.** `phase-idg-11` must state what happens to an abandoned draft. Under this
   proposal the answer covers a folder, including any `prompts/` and `evidence/` gathered, not only
   one file.

No contradiction was found between this proposal and `phase-idg-11`'s scope or acceptance lines.
The risk is sequencing: see decision K.

## Where this proposal contradicts current documents

Each would need an amendment if the owner adopts the corresponding part. None is made here.

| Document | Current text | Conflict |
|---|---|---|
| Plan quality standard (`GOV-010`) | P2 and P3 are judged on the plan; the Design row lists the accepted headings | Under rule 6, P2 and P3 are judged on `decisions.md`. The Design row's headings still work |
| Document code protocol (`GOV-005`), "Multi-file plans" | "A plan set lives in a folder named for the parent code" | Rule 1 makes every new plan a folder, with or without children |
| Governance protocol (`GOV-001`) | "Only the exact navigation files listed in `src/governance/__main__.py:EXEMPT` … are exempt in the scanned roots" | Rule 4 adds the member names inside plan folders |
| Prompt-pack protocol (`GOV-008`) | Each pack stage is "a governed prompt document" | Rule 7 makes one-time prompts ungoverned members. The planning protocol (`GOV-021`, step 4) already records the owner's ruling that a pre-plan package may be ungoverned |
| Three-altitude review procedure (`GOV-018`), step 2 | The plan altitude reviews "the plan and the requirement it depends on" | With rule 6, `decisions.md` is dispatched too, as part of the plan |
| Plans README (`docs/01-plans/README.md`) | "Name files descriptively: `YYYY-MM-DD-topic.md`" | Already contradicts `GOV-005`; would also need the folder layout |

## Owner decisions needed

Each with this session's recommendation. The letters are for reference in this file only.

| | Decision | Recommendation |
|---|---|---|
| A | Is every new plan a folder (rule 1)? | Yes |
| B | Are the 44 existing single-file plans migrated? | No. The move breaks 263 path references in 94 files, and 8 in the append-only idea log cannot be fixed. A plan moves only if the owner asks, for example when it gains a child |
| C | Are decisions split into a one-line ruling in the plan and a record beside it (rule 6)? | Yes, for new plans |
| D | Is the decision record an uncoded member file (`decisions.md`), rather than a child plan or a new document kind? | Uncoded member file. A child plan is reviewed as a plan and fails the entry check; a new kind costs a series and changes two checks (findings, 2B) |
| E | Do one-time prompts go in `prompts/` (rule 7)? | Yes, with the one-time/reusable line drawn under `000501`. Already-governed prompts keep their codes |
| F | Do review records stay in `docs/08-governance/reviews/`? | Yes |
| G | Is there an `evidence/` member, and must `_working/` evidence a tracked plan relies on be copied into it (rules 8, 9)? | Yes to both |
| H | Is the entry point always named `PLAN-NNN-overview.md`, even for a one-document plan? | Yes |
| I | Is the `GOV-018` entry-check script fixed now, independent of the rest? | Yes. It misreports 11 plan documents today (inventory, section 1) |
| J | What happens to the flat child `PLAN-039.01`? | Leave it and record it as the one exception, then enforce "a child sits in its parent's folder" for new children. Moving `PLAN-039` and `PLAN-039.01` means rewriting 18 path references in 10 files |
| K | Is this settled before `phase-idg-11` runs? | Yes, or `phase-idg-11` is given this proposal as an input, so it defines a folder-shaped draft location |
| L | Does the plugin (`plugins/idea-realization/`) adopt the same standard? | Decide after the repository adopts it; the plugin has its own copy of the rules and its own users |

## Candidate work if adopted

Listed for planning; no phase is registered and no plan is written here.

1. **Fix the `GOV-018` entry-check script's `depends_on` lookup** so it finds documents at any depth
   under `docs/` and treats "not found" as "not a requirement". Verification: the eleven
   `PLAN-048` children stop reporting "Requirement coverage"; `PLAN-050.02` and `.03` still report
   "Execution order". Independent of everything else (decision I).
2. **Governance check: plan-folder members.** `markdown_paths` skips `decisions.md`, `prompts/**`
   and `evidence/**` inside a `docs/01-plans/PLAN-*/` folder; an area folder named like a member is
   rejected. New cases in `test/test_governance.py`; `test_new_readme_is_not_an_exemption` still
   passes. Decisions A, C, D, E, G.
3. **Governance check: a child plan sits in its parent's folder**, with `PLAN-039.01` handled per
   decision J. One condition in `naming_errors`, one test in `test/test_codes.py`.
4. **Amend `GOV-005`**, "Multi-file plans", into the plan-folder standard; amend `GOV-001`'s
   exemption sentence.
5. **Amend `GOV-010`** P2 and P3 to be judged against the decision record, and add the one-line
   ruling format; amend `GOV-018` step 2 and the single-adversary engine prompt (`PROMPT-038`) so
   the plan altitude receives `decisions.md`.
6. **Amend `GOV-008`** for one-time prompts, after `000501` settles the boundary.
7. **Rewrite `docs/01-plans/README.md`**, which is stale today (findings, other finding 7), and add
   a plan-folder skeleton to `templates/governance/`.
8. **Coordinate with `phase-idg-11`** (decision K).
9. **Plugin**, only if decision L says so: the same changes in `plugins/idea-realization/scripts/`
   and its tests, templates and documents.

No migration of existing plans is listed, because decision B recommends none.
