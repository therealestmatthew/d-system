---
schema_version: 1
id: doc-document-backlog-governance-requirements
code: REQ-015
title: Document and backlog governance requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-governance, sys-backlog]
depends_on: [doc-governance-protocol, doc-backlog-protocol, doc-document-code-protocol]
---

# Document and backlog governance requirements

## Observed problem and scope

`src/governance` already verifies that the document corpus is structurally sound: codes are unique,
catalog entries match the files, backlog phases reference real plans. What it does not verify is
whether a document is *the right kind of document*, whether it still describes the system it claims
to, whether the registries that index everything have room to grow, or whether a phase's actual
change set stayed where the phase said it would.

Five gaps, each measurable today.

1. **The requirement-versus-plan boundary is convention, not rule.** `AGENTS.md` states the pair —
   a `requirement` of observable statements, and a `plan` — as a single instruction. The corpus does
   not match it. `000038` counted 18 plans against 4 requirements on 2026-09-08, with only
   `REQ-001`/`PLAN-005` a clean paired example; the rest fold acceptance into the plan and have no
   standalone requirement. Nothing in `AGENTS.md`, `GOV-002` or either directory README says when a
   requirement is mandatory and when a plan's own acceptance section suffices.

2. **Nothing governs document staleness or retirement.** `000056` names the gap: the governance check
   verifies structure, not whether a document still reflects the system it describes, and there is no
   defined path for retiring or superseding one when the thing it describes changes.

3. **Index widths were never chosen against a horizon.** `schemas/document.schema.json` pins document
   codes to three digits, so `PLAN-999` is the per-series ceiling, sub-codes cap at `.99`, and dated
   session codes allow 99 per day. `GOV-005` forbids reuse, so retirements consume the space
   permanently. The ideas log went to six digits before its third entry; nothing else was audited
   (`000006`). Widening a pattern is cheap; renumbering issued codes is forbidden, so the cost of
   being wrong is asymmetric.

4. **`backlog.yaml` only grows, and everything that reads it raw pays for the whole history.**
   `GOV-002` forbids deleting completed phases. The file was 98 phases and ~142KB when `000037` was
   raised; it is over 200 phases now. The CLI filters, but an agent orienting by reading the file
   pulls every completed phase's full record into context regardless of relevance.

5. **Nothing checks that a completed phase stayed inside its declared paths.** Collision-checking
   compares *declared* deliverables between phases before work starts. `AGENTS.md`'s instruction to
   stay inside declared systems and deliverables is enforced only by an agent choosing to follow it;
   nothing diffs the actual `git diff` against the declaration afterwards. A solo agent drifting
   outside its declaration is caught only if it happens to collide with a peer (`000027`).

A sixth is near-mechanical: `_tmpagent/`'s claim protocol is load-bearing enough for `AGENTS.md` to
give it a full section, but `docs/08-governance/systems.yaml` has no entry for it, so the registry
that answers "what exists and how mature is it" is blind to a mechanism in daily use (`000023`).

This requirement covers the document and backlog governance programme (`P2`): the document contract,
the backlog substrate's capacity, the containment check, and the missing registry entry. It does
**not** cover plan *quality* — what makes a plan well written is `000047`, which sits in `P1` as
`phase-idg-10`. The boundary is stated under `R05`.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | A written rule states when a `requirement` document is mandatory and when a plan's own acceptance section suffices, in terms someone can apply without judging "non-trivial". | Read the rule and apply it to five existing plans chosen without regard to outcome. Confirm it yields the same answer for each as a second reader. A rule whose only gate is the word "non-trivial" has not closed `000038`'s gap. |
| R02 | The existing corpus is classified against that rule, and every plan lacking a required requirement is listed. | Run the classification and read the list. Confirm the count is stated as a number rather than as "several". A rule applied to nothing is untested. |
| R03 | The governance check rejects a new plan that the rule says needs a requirement and does not have one. | Add a fixture plan meeting the mandatory condition with no paired requirement; confirm governance fails and names the plan. Confirm existing plans grandfathered by R02's list still pass, so the rule does not turn `dev` red retroactively. |
| R04 | Every governed document carries a way to tell whether it still describes the system it claims to, and a defined path to retirement or supersession. | Read the mechanism. Confirm it distinguishes a document that is *wrong* from one that is merely *old* — age alone is not staleness, and a rule that flags by date will flag `ADR-003`, which is both old and correct. |
| R05 | The boundary between document-staleness governance and plan-quality assessment is stated, and neither duplicates the other's checks. | Read both `R04`'s mechanism and `phase-idg-10`'s standard for a statement of what each owns. Confirm the staleness mechanism consumes the plan-quality standard rather than defining a second one for plans. `000056`'s own text admits this overlap is unresolved; leaving it unresolved is the defect. |
| R06 | Every index in the system is audited against a stated horizon, and each one's headroom is a number. | Read the audit for one row per index — document codes per series, sub-codes, dated session sequences, phase numbers within a track, and identifiers under `_data/`. Each row carries its current pattern, its ceiling, current usage, and the horizon it was judged against. An index with no stated horizon has not been audited. |
| R07 | Any index judged too narrow is widened in the same programme, and widening does not renumber an issued code. | Confirm the widened pattern accepts both old and new forms. Confirm no existing document's code changed — `GOV-005` forbids renumbering, so a migration that renumbers has failed rather than succeeded. |
| R08 | Completed and cancelled phases live outside the file an agent reads to orient, and their ids and completion evidence are preserved exactly. | Confirm a completed phase's record is byte-identical before and after the move. Confirm `--ready` and `--backlog` report unchanged totals across both files. This is a location change, not a deletion, and must not conflict with `GOV-002`'s preservation rule. |
| R09 | Reading the working backlog file costs materially less context than before the split, stated as a measurement. | Report the file's size and phase count before and after. A split that leaves the working file the same size has not solved `000037`'s problem. |
| R10 | A backlog review and re-prioritisation procedure exists, naming what triggers it, how `next_up` is rebuilt and by whom. | Read the procedure for all three. Confirm it answers what un-defers a phase whose gate cannot be met by waiting — `phase-mem-15` through `-19` gate on recorded retrieval failures that nothing currently records, which is the case that proves the procedure is needed. |
| R11 | The procedure states whether it is a session type or a command, and is reachable that way. | Invoke it as whatever it claims to be and confirm it runs. A procedure that exists only as prose in a governance document is not reachable. |
| R12 | A completed phase's actual change set is diffed against its declared `systems` and `deliverables`, and files outside the declaration are named. | Run the check against a phase whose diff is known to include an undeclared path; confirm it names the phase and the file. Run it against the repository as it stands and record the result — a check whose first run reports zero findings across 70-plus completed phases is more likely broken than vindicated. |
| R13 | The containment check reports rather than blocks, and its output distinguishes a declaration that was too narrow from work that genuinely strayed. | Read the output for that distinction. Confirm nothing in the check writes to `backlog.yaml` or reopens a completed phase — judging which of the two a finding is belongs to a person. |
| R14 | `_tmpagent/`'s claim protocol has an entry in `docs/08-governance/systems.yaml` with a maturity, and `--inventory` reports it. | Run `uv run python -m src.governance --inventory` and confirm the entry appears with a maturity level. Confirm the maturity is justified by what the mechanism actually does rather than asserted. |

## What each requirement is not

**R01 is not a demand that every plan gain a requirement.** The rule may legitimately say that most
plans do not need one. What it may not do is leave the question to each author's reading of
"non-trivial", which is the state `000038` reports.

**R04 is not a staleness date.** Age is not the signal. `ADR-003` is among the oldest documents in
the corpus and is entirely current; a recently written document describing a route that was renamed
last week is stale. The mechanism must key on the relationship between a document and what it
describes, not on a timestamp.

**R08 and R09 are one change measured two ways.** R08 is the safety property — nothing is lost — and
R09 is the point of doing it at all. A split satisfying R08 alone is a file move that helped nobody.

**R12's zero-finding case is called out deliberately.** The check runs against a corpus where
`AGENTS.md`'s containment rule has been enforced only by agents choosing to follow it, and where at
least one class of violation is already known: every `phase-prog-*` phase rewrites `backlog.yaml`
without declaring it. A first run reporting nothing would contradict evidence already in hand.
