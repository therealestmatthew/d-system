---
schema_version: 1
id: doc-session-productivity-core-plan-parked
code: SESS-2026-09-23-08
title: Productivity core plan, parked at the wind-down - resume point
kind: session
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems:
- sys-portfolio
- sys-backlog
depends_on:
- doc-productivity-core-enhancements
- doc-backlog-decisions
---

# Productivity core plan, parked at the wind-down

Prompt Planner session, 2026-09-23. The Session Manager relayed the owner's wind-down ruling: finish
the two small `phase-cap-08` branches, park this branch with a resume point, and move to the agent
orchestration systems. This record is that resume point. Nothing on this branch has merged.

## Where the work stopped

Branch `agent/plan-productivity-core`, worktree `../d-system-worktrees/plan-productivity-core`. It is
based on `4f01363` and has not been rebased onto current `dev`. It carries:

- `d3e7d09`, `48c807c`, `55747f9`: the same `phase-cap-08` changes that merge separately as
  `agent/queue-cap-08` and `agent/amend-cap-08`. After those merge, a rebase drops them.
- `28342fb`: `PLAN-044`, phases `phase-pc-01` to `phase-pc-09`, `batch-007` and `batch-008`,
  `PROMPT-039`, the GOV-003 entry, the `next_up` reordering, the `phase-des-01` edge on the ten
  HTML phases, and the scope lines added to `phase-idg-01` and `phase-idg-04`.
- This record.

An independent review of `28342fb` returned sixteen findings, listed below. None is fixed yet. That
review ran as a general-purpose sub-agent, so it does not satisfy new requirement 3.

## The owner's answers, Q1 to Q10 (2026-09-23)

All ten follow the recommendation that was put to the owner. They are recorded in the GOV-003 entry on
this branch.

1. The prompt pack is batch tables (`batch-007` onward, approved by the owner with READY) plus a
   short prompt document with Builder prompts.
2. The weekly-review path goes in `next_up` directly after `phase-cap-08`, ahead of `phase-irs-14`.
3. Each new idea gets one specification phase (`phase-prog-*` pattern), which adds build phases once
   the design is settled with the owner.
4. `phase-html-01` to `phase-html-10` depend on `phase-des-01`.
5. `000343`: a `tags.json` under `D_SYSTEM_DATA_ROOT`, merged with the shared taxonomy by
   `rebuild_db.py`; the capture writer targets it.
6. `000366` goes into `phase-idg-04`'s scope and `000367` into the idg phase that owns link targets.
   Neither gets a productivity-core phase; both are noted in the traceability table.
7. `000361`: a quick front end that writes into staging, with no ADR. Its specification runs after
   `phase-cap-08`.
8. Two waves. Wave 1 is the path to `phase-syn-03`, plus `000345`, `000343`, `phase-conc-07` and the
   `000360` API/UI specification after `phase-rel-07`. Wave 2 is `000362` (after `phase-sig-03`),
   `000363` (after `phase-cap-08`), and `000365` as the design phase that closes ARCH-010's gates,
   with `000364` inside it.
9. The links proposed by triage go into the traceability table as proposals only.
10. `phase-cap-08` uses an absolute `D_SYSTEM_DATA_ROOT=/code/d-system/_private/portfolio`, and
    `_capture/` is copied back before the worktree is removed. No code change.

## New requirements set at the wind-down

1. The productivity cluster (`000360` to `000367`, plus `000255` to `000267`) goes through the
   partition-ideas workflow before the plan is finalised, once `phase-part-03` completes.
2. The plan gets a GOV-018 three-altitude review record before G3.
3. READY reviews come from a dedicated validator or adversary agent type, not a general-purpose
   sub-agent. For `agent/amend-cap-08` the owner chose `demo-adversary`.

The glossary-classification specification phase and the Session Manager board/state protocol draft
also move to after the clear.

## Review findings on 28342fb, not yet fixed

1. **Both tables give PROMPT-036 phases it cannot run.** PROMPT-036 may not allocate document codes
   or record owner answers in GOV-003, and it allows one owner interruption, at batch open.
   `phase-cap-08` needs the owner live. Proposed fix: give wave 2 and `phase-cap-08`/`phase-pc-03`
   to Builders only, and put the change to the owner, since composition is theirs.
2. **The `phase-idg-04` line puts real project ids into the tracked `_data/ideas.jsonl`.** It also
   extends the `000343` ruling to idea tags, which the owner did not rule. Proposed fix: replace the
   sentence with an open question to the owner.
3. **The GOV-003 entry and PLAN-044 wrongly say wave 1 does not overlap batch-003 to batch-006.**
   `phase-idg-01` shares `sys-contracts` and `sys-portfolio`, and several irs phases declare `src/`
   and `test/`. Proposed fix: say that the two sets contend for slots, and name the collisions.
4. **As written, `phase-pc-02` fails on the default data root:** the private file and `_data/tags.json`
   are the same file, so every id is a duplicate. Proposed fix: read one file when the root is `_data/`.
5. **`phase-pc-02` omits deliverables:** `src/capture/review.py`, three test files and GOV-001. The
   CLAUDE.md:121 and AGENTS.md:67 wording will need owner-approved edits.
6. **`batch-008`'s external dependencies are not complete (GOV-016 rule 3)**, and its
   `verified.method` states a rule GOV-016 does not contain. A Builder-held phase also blocks
   PROMPT-036 from opening the next stage.
7. **`batch-007` is missing `external_depends_on`** for `phase-rel-02`, `phase-cap-06` and
   `phase-cap-07`.
8. **The specification phases omit GOV-003 and `backlog.yaml` from their deliverables**, so the
   collision rule cannot see them.
9. **`phase-pc-09` is too large for one session.** Split it into the four gates, then the requirement,
   plan and review.
10. **`PROMPT-039` has no confidentiality line for the specification phases**, and those phases have
    no leak check.
11. **The `phase-idg-01` addition leaves the build to the builder's discretion.** Make it
    decision-only, or ask the owner.
12. **GOV-003 says "roughly twenty".** The count is seventeen, and the entry omits that `000365`
    becomes three phases.
13. **PLAN-044 inconsistencies:** line 59 includes `000255`; the wording on real records; citations of
    gitignored reports; `phase-proj-01` is not reconciled with `000022`; the `systems` front matter
    is incomplete.
14. **Phase details:**
    - `phase-pc-01`'s next_action overclaims the ARCH-010 gate, and its `sys-contracts` lock is not
      needed.
    - `phase-pc-03`'s `sys-api`/`sys-ui` locks block real builders.
    - The `phase-pc-06` storage wording should be a question.
    - Question for the owner: should `phase-conc-07` (backup) come before `phase-cap-08`?
15. **An existing `next_up` defect:** `phase-irs-14` is listed before its dependency `phase-irs-11`.
16. **Metaphors to replace:** "front", "ride", "nowhere to go", "reliability chain".

## Glossary-classification input received

The Standby Builder sent its proposal for the glossary phase. Its content, for the phase that picks
this up after the clear. The phase goes on the terminology plan (`PLAN-012`), not `PLAN-044`.

- **Problem:** tags and systems apply to whole concept files, and the ~140 existing terms are
  headings inside 11 grouped files. A tag cannot apply to a single term.
- **Structure options, for the owner to decide:**
  - S1: one concept memory per term under `brain/concepts/<group>/`. This reverses draft PLAN-012's
    grouped-file decision and produces ~250 files.
  - S3: a schema-validated data file with a sanctioned writer that generates `GLOSSARY.md`.
    Definitions move out of `brain/`, and it needs a new schema, a writer and a generator rewrite.
- **Dimensions** (approved):
  - system: validated against `systems.yaml`.
  - term_kind: concept, acronym, identifier-pattern, status-value, role, artifact, process,
    command-tool, label.
  - standing: implemented, planned, proposed, retired.
  - audience: owner, agent-builder, training, newcomer.
  - reach: repo-wide, single-document.
  Senses of one word become separate cross-referenced entries, not a dimension.
- **Where values live:** a governed `docs/08-governance/glossary-facets.yaml` with its own schema,
  not `_data/tags.json`. That file's category enum is a portfolio taxonomy.
- **Build:** optional facet fields in `schemas/memory.schema.json` (S1) or the S3 schema; governance
  validation; a repeatable `--where field=value` filter and grouping in `tools/generate_glossary.py`;
  a drift test per committed slice. Today only `GLOSSARY.md` has one (`test/test_glossary.py`).
- **Retrieval:** unverified. Under S1, `tools/load_context.py --type concept` returns one row per
  term. Under S3, concepts leave `brain/` and retrieval needs a new source. The phase must check both
  against the code.
- **Related ideas sent to Ideation**, with no ids yet: a table of contents, acronym index and
  anchors; ruling sections that render as fake terms; entries generated from registries; a glossary
  protocol; a sanctioned concept writer.

## To resume

1. Rebase onto `dev` after `agent/queue-cap-08` and `agent/amend-cap-08` have merged. Re-allocate
   `PROMPT-039` and this record's code if a peer has taken them, and regenerate the catalog.
2. Once `phase-part-03` is complete, run the productivity cluster through the partition-ideas
   workflow (requirement 1). Its partition may change the phase set, so fix the sixteen findings
   after it, not before.
3. Put the owner questions in findings 1, 2, 11 and 14 to the owner through the Session Manager.
4. Write the GOV-018 three-altitude review record (requirement 2), then get the READY review from a
   dedicated validator or adversary agent type (requirement 3).
