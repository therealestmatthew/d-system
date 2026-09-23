---
schema_version: 1
id: doc-session-three-altitude-review-park
code: SESS-2026-09-23-07
title: Three-altitude review procedure — claimed, oriented and parked for owner rulings
kind: session
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-realization]
depends_on: [doc-idea-realization-system-plan]
---

# Three-altitude review procedure — claimed, oriented and parked

## Phase

`phase-irs-06` — Three-altitude review procedure with the interim adversarial engine. It writes
the review procedure (whole plan, each phase in isolation, each later-added phase against the
standing plan), runs it with a single adversary, makes the plan-quality conformance check
(`GOV-010`) its entry condition, and defines `schemas/adversarial-finding.schema.json`, the one
finding format `phase-irs-13` (gate queue) and `phase-irs-10` (learning loop) read.

## Claim

Claimed by `agent-builder-a` in `87cd88a` on `dev` at `5d71de6`, in a turn granted by the Session
Manager under `GOV-017`. The `/session-start` claim-approval question was answered by the owner's
overnight authority (`_working/overnight-sprint/01-authority.md`, section 1, which pre-approves
`phase-irs-06` for Session 1 - Builder A). Preflight in the worktree: `Governance OK: 35 systems,
335 documents, 31 memories, 294 backlog phases`; pytest `982 passed, 1 skipped`.

## Where this stands

**Parked before any build work**, under section 3 of the overnight authority: the finding schema
needs owner rulings that no document makes, and one of them depends on a question the owner has
left open. The branch holds only this record. The claim is kept.

## Questions for the owner

Each question names what the sources say. The recommendation is the builder's, not a ruling.

### 1. Recurrence key (depends on batch-005 Q1, still open)

`phase-irs-10` must route recurring adversarial findings into the anti-pattern store using that
store's recording contract unchanged (`backlog.yaml`, `phase-irs-10` scope). Batch-005 Q1 asks
how the store detects a recurrence; its recommended option is a required `slug`. The batch-005
pack's OWNER ANSWERS say "Q1–Q3 and Rounds 2–3 are still open."

- Does a finding carry a recurrence key, and is it required?
- **Recommendation:** answer batch-005 Q1 first. If it is option 1, a finding carries an optional
  `slug`, which the adversary proposes and whoever records the anti-pattern confirms.

### 2. Severity vocabulary

- `partition-adversary.md` (line 68) ranks findings `blocker / major / minor`, the format the
  2026-09-15 pass on `ARCH-006` used.
- The build adversary uses `HIGH / MEDIUM / LOW`.
- `ARCH-006` stage 5 speaks of "unresolved blockers" escalating to G3.
- **Recommendation:** `blocker | major | minor`, because stage 5's escalation rule is written in
  terms of blockers.

### 3. Disposition values, and who writes them

`GOV-014` (Adversary) says every finding "carries a disposition, even if that disposition is
'accepted as-is, no change'", but also that the adversary never approves and never writes the fix.
`ARCH-006` stage 5: "Findings return to stage 4 for one revision cycle; unresolved blockers escalate
to G3". No document lists the values or names the writer.

- **Recommendation:** the planner writes the disposition during the stage-4 revision, and the
  owner writes it at G3 for an escalated blocker. The values are `fixed` (with where),
  `accepted-no-change` (with reason), `rejected` (the finding is wrong, with reason) and
  `escalated-g3`. The adversary writes none of them.

### 4. Where findings records live, and the declared paths

The deliverables are `docs/08-governance/`, `docs/02-prompts/` and the schema. The acceptance
"one review produces a findings record" needs that record to live somewhere. A schema also needs a
test to prove it is valid draft-07 and that the sample record validates, and `test/` is not
declared.

- **Recommendation:** one JSON file per review, under a new path such as
  `docs/08-governance/reviews/` (inside the declared deliverable), holding the findings from all
  three altitudes, each tagged with its altitude. Widen the deliverables by one test file,
  `test/test_adversarial_finding_schema.py`. No writer tool.
- The alternative is a JSONL log with a sanctioned writer under `tools/`, which adds an OPS
  document and widens the phase further.

### 5. Adoption seam for the trio (deferred, but the schema shapes it)

The phase defers the design of the trio's adoption seam (`phase-agx-11` / `phase-agx-12`). The
arbiter's ruling cites both arguments (`phase-agx-12`), so a trio finding has more than one author
and a ruling.

- **Recommendation:** a finding carries `engine` (`single-adversary` now) and an `author` string
  now. The trio's argument and ruling fields are added later as optional properties, so records
  written now stay valid. This keeps the deferral real without locking the trio out.

## What is already settled

- **The conformance check** is `GOV-010`'s mechanical check (required and conditional section
  headings; the requirement row check). No checker exists in `src/` or `tools/`. Batch-004 Q6:
  "irs-06 keeps testing with a sample non-conforming draft."
- **The engine is a prompt, not an agent file.** `GOV-014`: the single-adversary engine "has no
  agent-definition file yet, and none is created by this phase." The engine prompt goes under
  `docs/02-prompts/`.
- **The prompt to generalize was never saved.** `SESS-2026-09-15-13` records that the
  `partition-adversary` agent ran against the `ARCH-006` draft and every finding was accepted. The
  prompt itself does not survive, so the new prompt draws on `partition-adversary.md` and that
  record.

## Resume

1. Take the owner's answers to questions 1–5, and record any declaration widening on `dev` first.
2. Write the procedure (`GOV-*`), the engine prompt (`PROMPT-*`) and the schema, then run one
   review that produces a findings record with dispositions, with a sample non-conformant draft
   returned at the entry check.
3. Run `/session-close` up to its independent review, then send READY per `GOV-017`.
