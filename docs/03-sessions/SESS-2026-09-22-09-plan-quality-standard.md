---
schema_version: 1
id: doc-session-plan-quality-standard
code: SESS-2026-09-22-09
title: Plan-corpus audit and the plan and requirement quality standard
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-gov-docs]
depends_on: [doc-idea-graph-lifecycle]
---

# Plan-corpus audit and the plan and requirement quality standard

## Phase

`phase-idg-10` — Audit the plan corpus and write the plan-quality standard.

## Verification

```
$ uv run python -m src.governance
Governance OK: 35 systems, 323 documents, 30 memories, 293 backlog phases
```

Run in the worktree `/code/d-system-worktrees/phase-idg-10` after rebasing onto `dev` at `ce732f1`.

The standard's mechanical plan check was also run by hand, from a scratch script implementing the
heading rule as `GOV-010` states it, against eleven existing plans. The second review
reproduced this table with its own implementation of the rule:

```
PLAN-001-agent-memory-system.md missing: ['Context', 'Design', 'Work', 'Verification', 'Boundaries', 'Open questions']
PLAN-002-mini-systems-proposal.md missing: ['Context', 'Design', 'Work', 'Verification', 'Boundaries', 'Open questions']
PLAN-005-document-code-system.md missing: ['Design', 'Boundaries']
PLAN-010-code-reservation-enforcement.md missing: ['Design', 'Boundaries']
PLAN-016-idea-record-system.md missing: ['Verification', 'Boundaries', 'Open questions']
PLAN-019-idea-priority-queue.md missing: ['Boundaries']
PLAN-020-portable-agent-workflows.md missing: ['Work', 'Boundaries', 'Open questions']
PLAN-026-concurrency-git-safety.md missing: ['Boundaries', 'Open questions']
PLAN-029-idea-graph-lifecycle.md missing: ['Boundaries', 'Open questions']
PLAN-038-backlog-status-regression-guard missing: ['Verification', 'Open questions']
PLAN-043-literature-review-report-page.m missing: ['Context', 'Verification', 'Open questions']
```

The standard applies only to documents written after it, so existing plans failing the check is
expected. The result shows the check runs and separates documents. It is not a compliance finding
against the corpus.

## Acceptance

- `REQ-014 R17 holds: every judgement names plans from the corpus on both sides.` — **Met** after
  both reviews' corrections. Judgements P1–P11, Q1–Q5, T1–T2, the Length section and each of the
  four optional sections name corpus documents on both sides. P8 has no document meeting all three
  parts; it cites one per part and says so, and the introduction states that exception. Q1–Q5 cite
  requirement documents, under the owner's ruling that the requirement half uses the same rule.
- `The standard names a section list a later plan can be checked against mechanically.` — **Met.**
  Accepted-heading tables, a match rule that excludes fenced lines, a shell form that also
  excludes them, and a requirement row check, requiring at least one row, that is part of
  conformance.
- `It is written so phase-idg-12 can measure a draft against it, which is what R20 requires of it.`
  — **Met.** The Concurrency condition is evaluated from the draft alone, by counting distinct
  `phase-` ids. The Requirement coverage condition needs one lookup outside the draft, resolving
  each `depends_on` id to its document's `kind`, and GOV-010 says so. The one judgement-based row,
  Accepted decisions, was made optional and taken out of conformance.
- `The two bullets above … are judged by the session-close independent review, not by a mechanical
  command.` — **Met** on the two reviews in `## Review`. The first found condition 1 partly met;
  its gaps were fixed in `ec23709`. The second, run on those fixes, found one false citation and
  three rule gaps; they were fixed in `936a061`. No third review has run on `936a061`.

## Backlog

`status: active`, held by `agent-builder-a`. `next_action`: review findings fixed; awaiting a
relayed `GRANTED merge`, after which the completion edit follows on `dev`, per `GOV-017` and
`GOV-003`'s coordinator-completion rule.

## Unresolved

- Integration onto `dev` and the completion edit are still to happen. They follow `GOV-017`'s
  merge gate.

## Review

### First review

An independent general-purpose sub-agent reviewed the branch at the commit now rebased as
`b942f36`, before any fixes. SHAs in this section are the current, post-rebase ones.
It re-ran governance and checked every citation in GOV-010 against its source. Its findings,
condition by condition, as reported:

1. **R17, both sides.** Partly met. P1–P10, Q1–Q5, T1–T2 and Length each had both sides, and every
   cited document existed. The Optional sections did not: `Key references` cited nothing, `Sizing
   against the partition` and `Deliverables` had only a positive example, and only `Known facts`
   had both. The always-required Work section had no judgement behind it.
2. **Mechanical section list.** Met, with ambiguities. The tables, the rule and the grep agreed.
   The only alias in two sections was `Requirement coverage`, and GOV-010 declared it.
3. **phase-idg-12 can measure a draft.** Mostly met. Two problems:
   - "Registers two or more backlog phases" is unknowable for a draft whose phases are not yet
     registered.
   - "Accepted decisions — when the owner has already ruled" is a judgement.

   Two gaps in the rule:
   - The row rule was not part of conformance.
   - Headings inside code fences were not addressed. `PLAN-002` has some.
4. **Judged by this review.** Not met at the time. The record pointed at a `## Review` section that
   did not exist, and the backlog's `result` and `next_action` already said the review was done.

The discrepancies it listed, and their disposition:

| # | Finding | Disposition |
|---|---|---|
| 1 | Optional sections lacked both sides | Fixed: each now has a meets and a does-not example (`PLAN-026`/`PLAN-037`, `PLAN-034`/`PLAN-026`, `PLAN-026`/`PLAN-037`, `PLAN-016`/`PLAN-015`) |
| 2 | Premature review claims in the record and backlog | Fixed: this section now exists; `result` and `next_action` rewritten |
| 3 | P3: `PLAN-029` uses "Ruled:" only for decisions 1–2 | Fixed: wording narrowed |
| 4 | P9: `PLAN-016` and `PLAN-038` supersessions are undated | Fixed: cited as meeting it except for the date |
| 5 | P5: `PLAN-038`'s second exclusion has no reason | Fixed: cites the first exclusion only |
| 6 | P10: `PLAN-026`/`PLAN-029` use undefined `P4`, `P6` etc. | Fixed: stated as the same failure on a smaller scale |
| 7 | Q3: `REQ-024` R01 names its cases; fails only on runnability | Fixed: reworded |
| 8 | Q3: `REQ-022` R01 quoted in part | Fixed: second clause quoted |
| 9 | P7: the concession is in the next paragraph | Fixed |
| 10 | P8: `PLAN-001` questions have a deadline and one leaning | Fixed |
| 11 | P8: meets-side does not show "who" | Fixed: split into who, when and leaning, each with its document |
| 12 | P1: `PLAN-004` step 1 is a concrete finding | Fixed: reworded |
| 13 | P2: `PLAN-003` names alternatives by implication | Fixed: reworded |
| 14 | P6: `PLAN-034`'s explanation is above the table, about `phase-proj-02` | Fixed |
| 15 | Optional: `PLAN-016` "written before its phases" unsupported | Fixed: claim removed; criterion restated |
| 16 | Stale `320 documents` in the record | Fixed: rerun output above |
| 17 | P6 `PLAN-019` "three inputs"; Q5 `REQ-006` paragraph | Fixed |
| — | Two formatting slips, a mid-sentence wrap and a long line | Fixed |
| — | Mechanical ambiguities under condition 3 | Fixed: Concurrency condition reads from the draft's Work section; Accepted decisions made optional; fenced lines excluded; row check made part of conformance |

The review found no mannered prose, no out-of-scope file and no problem with the cross-references
or the `codes.yaml` reservation removal. It confirmed, verbatim or in substance, the P1, P2 and P4
citations it checked, and every requirement quote under Q1–Q5.

### Second review

At the owner's ruling, relayed by the Session Manager, a second, fresh independent sub-agent
reviewed the fixes in `ec23709`. It had the diff, the acceptance list and the table above, and not
the author's rationale. It re-ran governance and got the same result. Its verdict per condition:
condition 1 partly met, condition 2 met with one contradiction, condition 3 mostly met, and
condition 4 not met on the record as then committed.

It found 15 of the 19 table rows fixed. Rows 1, 10 and 15 were partly fixed, and so was the
unnumbered mechanical row. The formatting row was not fully fixed. It also found ten new
discrepancies. All are fixed in `936a061`:

| # | Finding | Disposition |
|---|---|---|
| 1 | Key references: `PLAN-034`'s first entry, "The requirement", has no note, so "each entry says why" was false. The claim that every new citation had been checked did not hold for this one | Fixed: cites only the `ADR-009` and `AGENTS.md` entries, and names the bare one |
| 2 | Row check passes a requirement with zero rows | Fixed: at least one row is required |
| 3 | The shell form counted fenced lines, contradicting the new rule | Fixed: the form now drops fenced lines with `awk` first |
| 4 | "Lists two or more phases" did not say what counts; the Requirement coverage condition needs a lookup outside the draft | Fixed: count distinct `phase-` ids; the lookup is stated |
| 5 | The Deliverables criterion was changed to fit its example, and recorded only as "restated" | Fixed and recorded: the criterion is now "lists what the work produces, each with what it is for, and not the plan itself". The example says eight of `PLAN-016`'s nine entries meet it, and why the ninth is covered. This is a deliberate change from the first draft's "only when no backlog phase lists the files yet", which had no example that could be verified |
| 6 | Sizing: `PLAN-037` does not merely repeat its counts | Fixed: reworded as a section with no difference to explain |
| 7 | Session record cited pre-rebase SHAs, a stale base and "Met" before any post-fix review; P9 and P10 kept failing documents under "Meets it" | Fixed: SHAs and base updated. P9 now cites `PLAN-015` alone as meeting it. P10 now cites `PLAN-010` and `PLAN-019` as meeting it. `PLAN-016`, `PLAN-038`, `PLAN-026` and `PLAN-029` moved to the failing side |
| 8 | P8: `PLAN-001`'s question 6 has its own deadline | Fixed |
| 9 | The introduction overstated P8 | Fixed: the introduction states the per-part exception |
| 10 | P11: the dependency is stated in `PLAN-002`'s Composition Map | Fixed: says it appears only there, not where the work is ordered |
| — | Line length and ragged wraps | Fixed: prose reflowed to 100 columns |

It found no mannered prose, and confirmed the P11, Known facts, Key references (`PLAN-026`),
Sizing (`PLAN-026`) and P7 citations it checked.

The two new passing examples for P10, `PLAN-010` and `PLAN-019`, were checked by the author
against their text: every label in each resolves to a document code, a phase id or an idea id.

## Decisions

- **Deliverables widened in the claim commit** (owner): `templates/governance/document.md`,
  because the scope asks for cross-references in both directions, and `codes.yaml`, because
  `GOV-005` removes a reservation in the same change as the document.
- **The requirement half uses the same evidence rule** (owner): real requirement documents cited
  on both sides. This follows the recommendation in `phase-review-decisions.md` item 35.
- **Sections are matched by lists of accepted headings** (owner), not one canonical heading each.
  Both heading families in use pass, and the generic template's four headings are among them.
- **The standard applies forward only** (owner). Retrofitting the existing corpus stays a separate
  decision, as idea `000047` itself said.
- **`GOV-010` stands beside the template, not over it**, as the phase scope and
  `phase-review-decisions.md` item 34 recommended. The template gains one pointer paragraph.
- **The weak examples were found by reading, not chosen to make a point**, as `next_action` asked.
  The weakest plans turned out to be `PLAN-001` and `PLAN-002`, not the shortest ones. The dense
  plans (`PLAN-016`, `PLAN-017`, `PLAN-026`, `PLAN-029`, `PLAN-037`) are cited as failing some
  judgements too.

## Corrections

- The first draft named `PLAN-014` as a precedent for the investigation headings. `PLAN-014` has
  no such heading; `PLAN-008` does. Corrected before commit.
- The first draft said `PLAN-005`'s rename table was identical on every row, and said
  `PLAN-026`'s known-facts list carried facts about the stale `G10` and `G12` blockers that its
  body also states. Both corrected before commit.
- The session record and backlog said the review was done before it had run. The review caught
  this, and it is fixed above.
- The seventeen citation and rule findings of the first review, and the ten of the second, in
  `## Review`.
- The record said every new citation had been checked before commit. The second review found one
  that had not: the Key references example.

## Left undone

- **No mechanical test of the standard.** `phase-review-decisions.md` items 38 and 44 recommended a
  read-check for now. `phase-idg-12` will implement the check and is the right place to find out
  whether the rule is workable.
- **The existing corpus is not graded.** The scratch run above is a demonstration, not a record of
  compliance.
- **How the standard cites the anti-pattern store when revised** is `phase-irs-10`'s work, and the
  standard says so.
