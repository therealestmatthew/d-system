---
schema_version: 1
id: doc-system-boundary-study
code: PLAN-050
title: System boundary study
kind: plan
status: draft
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-28'
systems: [sys-gov-docs, sys-backlog]
depends_on: [doc-system-boundary-study-requirements, doc-system-audit, doc-idea-realization-system-plan, doc-prompt-pack-protocol]
---

# System boundary study

## Context and scope

This discovery plan assesses the boundaries among the personal-productivity system, the
idea-realization engine, the repository workbench, and the governance/framework layer. It also
accounts for every other registered system through an explicit disposition rather than forcing it
into those four concerns. The outcome is a governed draft architecture report for an owner decision,
not an extraction.

The detailed work is split into child plans. A phase reads its own child plan and the requirement it
cites; this overview is the map and completion gate, not required opening context for every phase.

**Amendment, 2026-09-28 (independent validation, owner-directed and unclaimed).** All five phases
completed on 2026-09-26 and produced the draft decision report
([`ARCH-012`](../../07-architecture/ARCH-012-system-boundary-decision-report.md)). An independent
validation then re-derived the study's figures, reviewed this plan under the three-altitude review
procedure (`GOV-018`), and re-assessed the three options. Its report is
[`validation-report.md`](../../00-working/boundary-study/validation-report.md) and its review record
is [`2026-09-28-plan-050`](../../08-governance/reviews/2026-09-28-plan-050.json). This amendment
adds the rejected alternatives, the failure paths, and the next steps for each option, with deferred
backlog phases. The text above this block is unchanged.

## Chosen design

The study is evidence first, then synthesis. It records a revision baseline for each inventory,
separates reusable prompt characteristics into independent fields, and treats no repository split as
a valid recommended outcome. Raw working evidence may be staged under `docs/00-working/`, but the
final phase promotes every relied-upon finding into a governed draft architecture document.

The alternatives each choice rejected, and what they would have cost (added 2026-09-28):

| Choice | Rejected alternative | What the alternative would have cost |
|---|---|---|
| Evidence first, then synthesis | Write the recommendation directly from the owner's stated history of the three concerns | The recommendation would rest on a framing nobody had checked. The framing did change: on 2026-09-27 the owner reworded the project purpose so that idea realization leads (`CLAUDE.md`, commit `518188a`). |
| One recorded baseline revision per inventory | Read the working tree without recording a commit | No figure could be re-derived later, and drift could not be told apart from error. The 2026-09-28 validation depended on these baselines. |
| Independent prompt fields | One composite category per prompt | A prompt that is both a reusable pattern and a dated campaign record would be forced into one bucket. `REQ-033` R03 forbids that. |
| No split as a valid outcome | Require the study to name at least one extraction | The report would commit to moving code before any interface contract existed. |
| Stage evidence under `docs/00-working/` | A governed document per evidence file | Five more codes and front-matter blocks for dated snapshots that are read once by the final phase. |
| Serial phases | Run the inventory, rubric and portfolio review in parallel | Every phase declares `sys-gov-docs`, so parallel claims would collide under the lock rules (`GOV-002`), and the corpus inventory reads the rubric's output. |

## Phases

| Child plan | Phase | Outcome | Depends on |
|---|---|---|---|
| [PLAN-050.01](PLAN-050.01-system-inventory.md) | `phase-bnd-01` | Whole-registry ownership and interface inventory | — |
| [PLAN-050.02](PLAN-050.02-prompt-classification-rubric.md) | `phase-bnd-02` | Prompt classification rubric and pilot | `phase-bnd-01` |
| [PLAN-050.03](PLAN-050.03-prompt-corpus-inventory.md) | `phase-bnd-05` | Complete prompt-corpus inventory and navigation findings | `phase-bnd-02` |
| [PLAN-050.04](PLAN-050.04-system-backlog-review.md) | `phase-bnd-03` | General system and backlog portfolio review | `phase-bnd-05` |
| [PLAN-050.05](PLAN-050.05-boundary-decision-report.md) | `phase-bnd-04` | Governed boundary report and owner decision gate | `phase-bnd-03` |

## Next steps after the owner's decision

Added 2026-09-28. The owner chooses option A, B or C at `ARCH-012`'s owner decision gate. Each
option's follow-up work is registered below as `deferred` backlog phases, so that none is favoured
before the decision and `--ready` offers none of them. The owner ruled on 2026-09-28 to register
phases for all three options. When the owner chooses, the chosen option's phases are reviewed
against current `dev` and released to `queued`; the other options' phases are cancelled with the
decision as the reason.

| Option | Phase | Outcome | Depends on |
|---|---|---|---|
| A. One repository with explicit contracts | `phase-bnd-06` | Governed concern ownership and interface contract: every system, every allowed crossing, a prohibited crossing per boundary | `phase-bnd-04` |
| A | `phase-bnd-07` | A `concern` field in the system registry, with a governance check that rejects a missing or unknown value | `phase-bnd-06` |
| A | `phase-bnd-08` | Defined entry-point values and a prompt operating index covering every governed prompt | `phase-bnd-04` |
| A | `phase-bnd-09` | Document retrieval measured against a fixed question set | `phase-bnd-04` |
| B. Prepare selective extraction | `phase-bnd-10` | Three candidates (the idea-realization plugin, the workbench, the governance engine) assessed against option B's five preconditions; the owner names one or none | `phase-bnd-04` |
| B | `phase-bnd-11` | Extraction discovery for the named candidate: contract, source authority, tests, versioning, migration and rollback, with no code moved | `phase-bnd-10` |
| C. Split now | `phase-bnd-12` | Migration architecture plan for the split: destinations, data boundaries, maintainers, release, compatibility, rollback | `phase-bnd-04` |
| C | `phase-bnd-13` | Cross-repository governance design: claims, backlog, codes, catalog and the governance check across repositories | `phase-bnd-12` |

`ARCH-012`'s conditional next actions are the source for each option's first phase. `phase-bnd-07`
and `phase-bnd-08` answer `ARCH-012`'s owner questions on registry contracts and prompt navigation.
`phase-bnd-09` measures the retrieval gap the portfolio review named as unmeasured.
`phase-bnd-10` exists because the validation found that the idea-realization plugin was built
during and after the study while the registry still lists it as `planned` (validation report,
figures and phase findings).

## Requirement coverage

| Requirement | Child plan / phase |
|---|---|
| R01–R02 | PLAN-050.01 / `phase-bnd-01` |
| R03 | PLAN-050.02 and PLAN-050.03 / `phase-bnd-02`, `phase-bnd-05` |
| R04 | PLAN-050.04 / `phase-bnd-03` |
| R05–R06 | PLAN-050.05 / `phase-bnd-04` |
| R06 (the sequenced next action after each possible decision) | `phase-bnd-06` to `phase-bnd-13`, one group per option |
| R07 | Every child plan |

## Execution order and real concurrency

The phases are serial. Each produces an input the next phase consumes, and all write study
evidence through the same documentation/governance surface. The active-claim budget may add waiting
time; none of these phases assumes a free slot.

The next-step phases run only for the option the owner chooses. Within an option they are also
close to serial, measured from their declared systems: `phase-bnd-06`, `phase-bnd-08`,
`phase-bnd-10`, `phase-bnd-11`, `phase-bnd-12` and `phase-bnd-13` all declare `sys-gov-docs`, so no
two of them can be active together. Under option A, `phase-bnd-07` (`sys-governance`) waits on
`phase-bnd-06` by dependency, and `phase-bnd-09` (`sys-retrieval`) is the one phase that can run
beside `phase-bnd-06` or `phase-bnd-08`.

## Acceptance and verification

The study is complete only when the five child-plan outcomes exist, the final architecture report
reconciles its evidence to current `dev`, and the owner has the explicit decisions and conditional
next actions required by `REQ-033` R06. Each phase runs governance and records its actual results.

**When a check fails** (added 2026-09-28). A phase whose governance run, count reconciliation or
diff check fails stays `active`. Its session record quotes the failing output, and it is not
completed until the check passes on a re-run after the cause is fixed. A reconciliation mismatch in
the final phase either refreshes the affected inventory or reports the drift in the report
(`REQ-033` R07). A figure found wrong after the study is complete is corrected in `ARCH-012` with
its old value kept and the correction dated, and the evidence behind it is reported, as the
2026-09-28 validation did. A next-step phase whose acceptance fails returns to `queued` with an
exact `next_action`.

## Out of scope

Implementing a repository split, changing product behaviour, reading `_private/`, modifying prompt
lifecycle status, or reprioritising the backlog.

The next-step phases keep these exclusions until the owner's decision releases one option's phases.
None of them moves code between repositories; option B's discovery and option C's migration plan
stop at documents.

## Open questions

The owner decides boundary direction, future portability, and any prompt-lifecycle change only after
the final report. No open question authorises a change during the study.

Added 2026-09-28:

1. **Which option, A, B or C?** The owner decides, at `ARCH-012`'s owner decision gate, after
   reading the validation report. The study recommends A. The validation does not choose; its
   re-assessment is in the validation report.
2. **Should each child plan get its own `GOV-018` review?** `GOV-018` step 2 says a child plan is
   its own target. The 2026-09-28 review read the five children as part of the plan instead, to fit
   one session. The owner decides whether separate child reviews are wanted. The reviewer's leaning
   is no: all five phases are complete, so a child review could change no execution.
3. **Should the registry's `planned` status for the plugin systems and `sys-demo-overview` be
   corrected?** Tracked code and completed phases contradict it. That is a registry change outside
   this plan; it is listed for local Ideation in the validation's handoff.
