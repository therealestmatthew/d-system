---
schema_version: 1
id: doc-agent-engineering-delegation-requirements
code: REQ-016
title: Agent engineering and delegation requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-delivery, sys-governance]
depends_on: [doc-portable-agent-workflows, doc-prompt-pack-protocol]
---

# Agent engineering and delegation requirements

## Observed problem and scope

This repository dispatches agents constantly and has no engineering discipline for it. Each dispatch
is authored from whatever the author remembers, the failures recur, and the lessons land in whichever
document the person who noticed happened to open.

The evidence is unusually good, because the failures are recorded rather than recalled.

1. **Agents are cut off mid-work and nothing says so.** On 2026-09-10 two of six parallel triage
   scouts stopped at exactly 30 tool calls with no finding; the four that completed used 14 to 19.
   The cap is documented nowhere, and a truncated report simply ends mid-sentence — in one case at
   "Now let me check if there's any existing metrics or report command anywhere:". Re-running pays
   for the whole context twice (`000077`).

2. **The same failure modes recur across builds.** The 2026-09-11 session alone produced a starter
   catalog: dispatches scoped past the turn budget, seven truncations across two phases, fixing
   runtime behaviour from assumption instead of measurement, validators passing work that did not
   run (`000138`, `000097`). Capture now exists — the `log-anti-patterns` skill routes and writes —
   but nothing detects recurrence or derives a rule from the accumulated record.

3. **Dispatch scoping is improvised.** Task size, model choice, what context to attach, which
   verification instrument to name, and when to escalate are decided per dispatch. Partial versions
   exist in `PROMPT-012`'s model policy, `PROMPT-021`/`024`'s conventions and `GOV-008`'s cost
   protocols, and they have never been consolidated or measured (`000139`).

4. **Cross-agent context is hand-carried.** A coordinator re-pastes established facts — an
   environment quirk, a corrected diagnosis, a decision taken — into every prompt, or the agent does
   without them (`000128`).

5. **Nobody has audited what the repository already ships.** `.claude/` holds commands, skills and
   agent definitions accumulated over weeks, none judged on whether their scope, tooling, model
   assignment and context cost fit the job (`000126`, `000013`).

6. **Agent construction has no named framework.** `000078` and its four children — guides, sensors,
   context pipelines, orchestration — propose naming the recurring concerns once instead of
   rediscovering them per agent.

**Two claims were verified in the repository before any phase was sized**, as this programme's
finalize phase requires.

- **`000097`/`000138`'s capture half is delivered.** `.claude/skills/log-anti-patterns/SKILL.md`
  exists as a full workflow: it takes an anti-pattern, decides which record should hold it, and
  writes the ones the owner confirms. What remains is detection of recurrence and derivation.
- **`000136`'s substance largely exists as a recorded lesson.**
  `brain/procedures/runtime-behavior-needs-runtime-evidence.md` carries the rule at `confidence:
  high`, with the `phase-wb-09` incident: a page-crash blocker that survived build, lint, pytest and
  the mechanical gate because all four are blind to runtime rendering, and two fix cycles burned
  patching from a batching assumption instead of a websocket-lifecycle measurement. What does *not*
  exist is the pack-authoring **convention** that would have prevented it.

This requirement covers the agent engineering and delegation programme (`P4`). It does **not** cover
unattended execution infrastructure — that is `P5` — nor the idea-log agents, which are `P1`'s. The
boundary is that `P4` decides how agents in general are instructed, observed, coordinated and
reviewed; `P1` applies that to one domain and `P5` runs it without a person present.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | The tool-use cap that truncates a subagent is documented with its actual value, and the standing instruction is to resume rather than re-run. | Read the guidance for a number, not "a cap exists". Confirm it states the cost of re-running — the whole context paid twice — rather than only the rule. |
| R02 | A truncated dispatch is distinguishable from a completed one without reading the output's last sentence. | Truncate a dispatch deliberately and confirm the signal is available to the caller. `000077`'s case is that nothing in the agent's own output says it was cut off. |
| R03 | Every command, skill and agent definition the repository ships carries an audit verdict: keep, redesign, retire, or missing-and-needed. | Read the audit for one row per item under `.claude/` and per shipped agent definition. Count the rows against the actual file count; a missing item is a defect. |
| R04 | Each verdict cites the item's scope, tooling, model assignment and context cost against its job, rather than a general impression. | Read five rows chosen at random for all four dimensions. A verdict citing none of them has not applied the criterion. |
| R05 | The audit rules on whether this repository needs Claude Code specifically or *an* agent runner, given `PLAN-020` makes `.claude/` generated output. | Read the ruling. Confirm it is decided rather than deferred, and that it states what would change the answer. `000069` exists so this is answered deliberately instead of by drift. |
| R06 | Anti-patterns are stored so that a recurrence is detected mechanically rather than by someone remembering. | Record an anti-pattern already in the catalog a second time and confirm the system identifies it as a recurrence. A store that accepts duplicates silently has not met this. |
| R07 | The store is populated from what already exists rather than started empty. | Confirm the `brain/procedures/` entries and the 2026-09-11 starter catalog are present at first run. Count them. |
| R08 | A rule derived from accumulated anti-patterns is fed back into how future work is authored, and the path from record to authored prompt is traceable. | Follow one rule from its originating incidents to the dispatch text it changed. A derivation that produces a document nothing reads has not closed `000097`'s rescoped half. |
| R09 | A delegation-scoping methodology states how to estimate task size against the turn budget, choose a model, select context, name the verification instrument, and escalate — as a procedure with inputs, not as advice. | Apply it to three dispatches of genuinely different size and confirm it yields a defensible answer for each. Confirm it consolidates `PROMPT-012`, `PROMPT-021`/`024` and `GOV-008` rather than adding a fourth partial version. |
| R10 | Every work item whose requirement is runtime behaviour carries a named runtime instrument and a live check inside its loop, not only at the phase gate. | Read the authoring convention for both. Confirm a frontend work item authored without them fails review. This is `000136` as a convention rather than as the recorded lesson it already is. |
| R11 | The methodology is measured against outcomes and updated, rather than written once. | Read the retrospective for dispatch counts, truncations, fix cycles against the cap, and escalations, with at least one rule changed as a result. A retrospective changing nothing has not demonstrated the loop. |
| R12 | Facts established mid-session are available to every dispatched agent without the coordinator re-pasting them. | Establish a fact, dispatch two agents, and confirm both can reach it without it appearing in either prompt. |
| R13 | The shared state names what may be written to it, by whom, and when it is released, and it never becomes a second lock table. | Read the contract for all three. Confirm it does not duplicate `backlog.yaml`'s claim semantics — `_tmpagent/` already has a claims ledger, and two lock tables is worse than one. |
| R14 | A named framework for agent construction exists, and each of its concerns is grounded in an incident from this repository rather than asserted. | Read the framework for a citation per concern. `AGENTS.md`'s drift, the `maxTurns` truncations, the claim protocol answering a real collision, and the `phase-wb-09` runtime blindness are the available material; a concern citing none of it has not used the evidence. |
| R15 | The framework states its boundaries against `P6`'s retrieval work and `P3`'s concurrency mechanics rather than restating them. | Read for an explicit cross-reference on context pipelines to `P6`, and on orchestration to `P3`. Duplicated content on either side is the defect. |
| R16 | A lifecycle agent roster exists, each role bounded so it cannot reach the decision the role above it owns. | Read each role for what it may not do. Confirm the pattern matches `idea-triage`, which scouts but never promotes or declines. |
| R17 | The roster does not include a planner agent, because one is already built in `P1`. | Confirm no roster role duplicates `phase-idg-12`. `000072`'s planner bullet is struck; a roster that reinstates it builds the same agent twice. |
| R18 | An expansion agent and a minimalist agent produce genuinely opposed outputs on the same input. | Run both against one real decision and confirm the recommendations differ. Two agents agreeing on everything are one agent with two prompts. |
| R19 | An arbiter ruling between them has a stated authority boundary, and cannot reach a decision reserved to the owner. | Read the boundary. Confirm it is at least as tight as `/session-close`, which a person types precisely so an agent cannot reach completion. Confirm the arbiter's ruling is advisory where scope is the owner's. |
| R20 | An independent reviewer reads a session transcript directly and produces its own record, which is then compared against the participant's. | Run both and diff the two accounts. Confirm the reviewer read the transcript rather than the participant's summary — inheriting the participant's framing is the failure this exists to avoid. |

## What each requirement is not

**R05 is not a decision to leave Claude Code.** The row requires the question answered and the
answer's trigger conditions stated. "Yes, and here is what would change it" satisfies it fully.

**R06 is not a new capture mechanism.** Capture ships. The row is about the store and recurrence
detection behind it, and a phase that rebuilds capture has spent a session re-delivering
`log-anti-patterns`.

**R10 is not `brain/procedures/runtime-behavior-needs-runtime-evidence.md`.** That document exists and
records the rule. The row asks for the convention that makes an authored work item carry the
instrument by construction, so the lesson stops depending on the author having read it.

**R19's boundary is the whole phase.** Building three deliberation agents is straightforward; the
arbiter's authority is the part `000075` itself calls the most dangerous, and the reason that phase is
separated from `R18`'s.
