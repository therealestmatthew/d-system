---
schema_version: 1
id: doc-reviewer-contract
code: PLAN-047
title: Reviewer contract — a shell-less judge, a fixed command runner, coordinator dispatch and recorded verdicts
kind: plan
status: draft
owner: repository-owner
created: '2026-09-24'
updated: '2026-09-24'
systems: [sys-gov-docs, sys-governance]
depends_on: [doc-reviewer-contract-requirements, doc-realization-role-contracts, doc-multi-session-coordination-protocol, doc-design-document-amendments, doc-deterministic-guards]
---

# Reviewer contract

Delivers [REQ-030](../06-requirements/REQ-030-reviewer-contract.md).

## Context and scope

`REQ-030`'s problem section lists five failures, each with its record. In short: the session that
built a phase dispatches its own reviewer and hands it the session record; review dispatches name a
general-purpose agent; every reviewer type can run any command; no verdict is recorded; and the
owner's sampled re-review has nothing that draws the sample.

This is step 2 of the Scout's staged path (`_working/session-manager/scout/orchestration-3-architecture.md`,
section F, gitignored): "Reviewer contract and dispatch (R24): a general reviewer type with no Bash,
or the judge-plus-runner split; rationale-free input; the dispatcher is not the builder (Session
Manager or coordinator); named in `/session-close` step 3, PROMPT-036 and GOV-017 READY; verdicts
recorded (owner Q7)". R24 in the Scout's revised partition (section D.6) reads: "Dispatch and brief
every Assurance review: requirement, diff and commands only", owned by the coordinator.

The owner's rulings of 2026-09-23 that decide the design, as the Session Manager's board records
them:

| Ruling | Board line | Answers |
|---|---|---|
| "O-5 judge without Bash + fixed command runner" | "OWNER Scout rulings: ... O-5 ..." | `orchestration-3-architecture.md`, Owner decisions, O-5 (a) |
| "O-6 coordinator dispatches assurance (out of P3:164)" | same line | O-6 (a) |
| "Q7 record verdicts now, new reviewer types start in shadow" | "OWNER mapping rulings: Q7 ..." | Builder A's mapping (`reports/owner-design-mapping.md`), section 8, Q7 |
| "session-close reviewer gets no session record" | "OWNER Scout-1 rulings: ..." | `orchestration-1-evidence.md`, Owner decisions needed, item 4 (a) |
| "re-review 1 in 10 + every once-rejected" | "OWNER PLAN-046 answers: ..." | `PLAN-046` OQ3 |
| "Q7/Q9 -> second docs phase after reviewer contract" | same line | `PLAN-046` OQ5 |
| "Q9 security review plan-time (GOV-010) + diff-time at READY for auth/network/secrets/deps" | "OWNER mapping rulings: ... Q9 ..." | mapping section 8, Q9 |

The work sits under the owner's framing in idea `000411`: agents with defined contracts, and the
orchestration systems that manage them, are designed in parallel. Here the agent side is the judge's
contract and tools (R01, R06); the orchestration side is who dispatches it, what the brief holds and
where the verdict goes (R02-R05, R07).

**Partition placement.** In the partition the owner accepted at GATE 3 on 2026-09-23
(`docs/00-working/idea-partition-2026-09-23.md`):

| Idea | Track | Group |
|---|---|---|
| `000396` (dedicated validator and adversary types), `000241` (reviewers dispatched with write tools), `000215` (nothing records which model ran) | Agent engineering and review | Review independence and model assignment |
| `000392` (an assurance subsystem independent of delivery), `000387` (has the lifecycle's review discipline slipped) | Idea realization and multi-session coordination | Orchestration shape and assurance: the 000385 anchor's design questions |
| `000410` (no security review) | Governance checks, document hygiene and the portable framework | Delivery-safety gates in governance and CI |
| `000411` | not in the partition; recorded after its corpus was built | — |

The fourth member of the review-independence group, `000397` (validators on a different model or
provider), is out of scope: the owner ruled it comes after the ledger records the model (O-8), which
this plan builds.

## Decisions

**D1. The judge and the runner are separate: an agent with no shell, and code with no judgement.**
As ruled (O-5). The judge declares `tools: Read, Grep, Glob`, like `partition-analyst`. The runner is
a tool, `tools/run_review_checks.py`, that the coordinator runs before dispatching the judge; the
judge reads the runner's evidence files. The rejected alternatives were (b) keeping `Bash` and
relying on the prompt, which is today's state and what idea `000241` records failing, and (c)
permission rules per agent type, which waits on `phase-conc-08`'s placement rule and still gives the
reviewer a shell. The cost: the judge cannot try a command the runner did not run. That is the
point of the ruling, and a judge that needs another command says so in its verdict.

**D2. The runner executes only what the backlog already declares.** It takes a phase id and a
commit, and runs that phase's `verification` list and the four gate checks (`GOV-017` merge gate
step 1) in a detached temporary worktree, the way the Session Manager's merge-gate re-run already
does (`GOV-017` step 2). Accepting commands from its caller was rejected: that would make the runner
a shell with extra steps. Running in the builder's worktree was rejected: the builder's uncommitted
state would reach the evidence.

**D3. The coordinator dispatches every build review; the builder only asks.** As ruled (O-6, R24).
Today the coordinator is the Session Manager; later it is P3's tick. The building session sends a
review request and waits; the coordinator runs the runner, dispatches the reviewers with the brief
`REQ-030` R03 names, and returns the verdict record. When the owner runs `/session-close` in their
own session, that session is not the builder, so it may dispatch directly under the same brief rule.
The alternative, the builder dispatching a reviewer with a stripped brief, was rejected: the builder
would still choose what goes in the brief.

**D4. Verdicts are JSON records beside the plan reviews, committed on the phase branch.** Each
build review produces one file under `docs/08-governance/reviews/verdicts/`, validated by a new
`schemas/review-verdict.schema.json`. The coordinator writes it from the reviewer's reply without
changing a finding, keeps the raw reply as an evidence file with its sha256 (as the owner ruled for
the coordination log's evidence, protocol Q13), and hands it to the builder, who commits it
unchanged; the coordinator checks the sha256 at its merge-gate re-run. Outcomes arrive later (owner
overturned it at G4 or G5, a defect it passed was found on `dev`, a sampled re-review) and are
appended to the file's `outcomes` list, as `GOV-018` records append dispositions. Two alternatives
were rejected. An append-only ledger under `_data/` written by the coordinator: every verdict would
be a write to the primary checkout, needing a turn per review. A gitignored ledger under `_working/`:
the calibration data the owner asked for (Q7) would not survive a lost machine. OQ1 asks the owner to
confirm.

**D5. The judge starts in shadow; today's reviewers keep gating.** As ruled (Q7: "new reviewer types
start in shadow"). Until the owner promotes it, every build review runs the gating reviewer
(`demo-adversary` or `demo-validator-code`, as today) and the judge side by side on the same brief.
Both verdicts are recorded; only the gating one decides. The cost is two dispatches per review
during shadow. Promotion is the owner's decision, recorded in `GOV-003`; OQ2 asks what evidence the
owner wants before deciding.

**D6. The re-review sampler draws by recorded seed.** As ruled ("re-review 1 in 10 + every
once-rejected"). `tools/draw_rereview_sample.py` reads the verdict records since the last draw and
prints the sample and the seed, and the coordinator dispatches each re-review with a dedicated type
other than the one that passed the phase. The seed makes the draw repeatable, so the owner can check
that the sample was not chosen (the Scout's partition adversary, D.6 F6: the coordinator, not
Assurance, draws the sample).

**D7. The second docs phase is this plan's last phase.** The owner ruled that the Q7/Q9 docs phase
comes after the reviewer contract. It is registered here as `phase-asr-05` rather than as a new plan:
it documents Q7 as this plan builds it, and Q9's diff-time review is a `READY` step that
`phase-asr-04` writes the frame for. The security review itself is dispatched like any other review
(D3), with the type OQ3 settles.

## Implementation phases

| Phase | What | Requirements | Depends on |
|---|---|---|---|
| `phase-asr-01` | The reviewer-judge agent type and its `GOV-014` contract: tools, inputs, never-do, shadow status, and the assurance dispatch rule | R01, R03, R06 | `phase-dam-01` (it rewrites the same `GOV-014` contracts) |
| `phase-asr-02` | `tools/run_review_checks.py`, its operations document and tests | R02 | none |
| `phase-asr-03` | `schemas/review-verdict.schema.json`, `tools/draw_rereview_sample.py`, their operations documents and tests | R05, R07 | none |
| `phase-asr-04` | Wiring: `/session-close` step 3, `PROMPT-036` step 6 and its templates, `GOV-017`'s merge gate and messages, `PROMPT-037` | R04 | `phase-asr-01`, `phase-asr-02`, `phase-asr-03`, `phase-grd-03` and `phase-dam-01` (they edit the same passages) |
| `phase-asr-05` | The second docs phase: `GOV-010` threat surfaces, the `READY` security review, and `GOV-003` entries for O-5, O-6 and Q7 | R08, R09 | `phase-asr-04` |

## Requirement coverage

| Requirement | Phase | Acceptance evidence |
|---|---|---|
| R01 | `phase-asr-01` | The agent file's tools; a fixture with `Bash` fails |
| R02 | `phase-asr-02` | Four runner fixtures; the worktree is gone afterwards |
| R03 | `phase-asr-01` | The `GOV-014` passage |
| R04 | `phase-asr-04` | The three greps in `REQ-030` R04 |
| R05 | `phase-asr-03` | Three schema fixtures |
| R06 | `phase-asr-01` (contract), `phase-asr-04` (first recorded shadow verdict) | The contract text; the first judge verdict record |
| R07 | `phase-asr-03` | Three sampler fixtures |
| R08 | `phase-asr-05` | The `GOV-010` and `GOV-017` passages |
| R09 | `phase-asr-05` | The `GOV-003` entries |

Every row maps to a phase, and every phase carries a row.

## Execution order and real concurrency

- `phase-asr-02` and `phase-asr-03` depend on no phase: apart from their operations documents they
  touch only new files under `tools/`, `test/` and `schemas/`. Both declare `docs/08-governance/` for
  those documents, so they collide with each other and with `phase-grd-*` and `phase-dam-01`.
  Checked with `uv run python -m src.governance --ready` on this branch: both are `ready` and both show
  the active `phase-grd-01` as a conflict, so each waits for it.
- `phase-asr-01` waits for `phase-dam-01`, which rewrites `GOV-014`'s Validator contract (the
  close-reviewer rule and the re-review) and adds the Test Author contract.
- `phase-asr-04` waits for everything above and for `phase-grd-03`, which edits `GOV-017`'s merge
  gate and `PROMPT-037` item 4.
- `phase-asr-05` waits for `phase-asr-04`.

Proposed `next_up` placement: after `phase-dgov-06` and before `phase-cap-08`, in the order
`phase-asr-02`, `phase-asr-03`, `phase-asr-01`, `phase-asr-04`, `phase-asr-05` (OQ4).

## Out of scope

- **Cross-model review** (idea `000397`). The owner ruled it follows the ledger (O-8); this plan
  records the model, which is the precondition.
- **Promoting the judge to gating.** The owner decides that from shadow evidence (D5, OQ2).
- **Plan review under `GOV-018`.** It already has its own engine (`partition-adversary` with
  `PROMPT-038`) and records; this plan covers build review.
- **Moving merges out of the builder's session** (Scout O-3): builders self-merge under `GOV-017`
  until P3's merge-gate nodes exist.

## Open questions

- **OQ1. Where verdict records live** (D4). Who: the owner, at G3. Leaning: JSON files under
  `docs/08-governance/reviews/verdicts/`, committed on the phase branch unchanged and checked by
  sha256 at the merge gate.
- **OQ2. The evidence for promoting the judge.** Who: the owner, when the shadow period ends.
  Leaning: after at least ten reviewed phases, a table from the verdict records comparing the
  judge's verdicts with the gating reviewer's and with the owner's overturns, put to the owner as a
  gate item.
- **OQ3. Which reviewer does the diff-time security review** (Q9, `phase-asr-05`). Who: the owner, at
  G3. Leaning: the built-in `/security-review` command, run by the coordinator on the phase's diff
  and recorded as a verdict like any other review; a dedicated security agent type only if its
  shadow results show a need.
- **OQ4. Queue position.** Who: the owner, at G3. Leaning: after `phase-dgov-06`, with the two code
  phases first because they depend on nothing.
