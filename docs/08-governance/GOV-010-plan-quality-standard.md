---
schema_version: 1
id: doc-plan-quality-standard
code: GOV-010
title: Plan and requirement quality standard — the sections and content a good plan or requirement carries, derived from the corpus
kind: governance
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-gov-docs]
depends_on: [doc-idea-graph-lifecycle-requirements, doc-governance-protocol]
---

# Plan and requirement quality standard

A plan or requirement document can be checked against this standard in two ways:

1. **Mechanically**, by searching the draft for the headings each required section accepts. Any
   script can do this. The idea planner agent (`phase-idg-12`) uses this check to satisfy `REQ-014`
   R20.
2. **By review**, against the content judgements below. Each judgement cites documents from
   `docs/01-plans/` or `docs/06-requirements/` that meet it and documents that do not, as `REQ-014`
   R17 requires. Where no document meets a whole judgement, as in P8, it says so and cites one
   document for each part.

The standard was derived from an audit of every plan in `docs/01-plans/` and the requirement
documents in `docs/06-requirements/`, carried out in `phase-idg-10` on 2026-09-22.

## Relation to the generic template

[`templates/governance/document.md`](../../templates/governance/document.md) remains the starting
file for every document kind. It supplies the front matter and four generic headings. This standard
does not rewrite or supersede the template. It sits beside it and applies only to documents of kind
`plan` and kind `requirement`. The template's four headings are accepted aliases below, so a plan
started from the template passes the mechanical check once it has the additional sections this
standard requires.

## Scope

The standard applies to plans and requirements written after 2026-09-22. Existing documents are
neither retrofitted to it nor judged non-compliant by it. Whether any existing document is brought
into line is a separate decision.

What the standard does not cover:

- **Front matter and lifecycle** — [`GOV-001`](GOV-001-protocol.md) and the governance check own
  these.
- **Whether a document still describes the system** — document staleness belongs to `phase-dgov-02`,
  which consumes this standard for plans rather than defining a second one (`REQ-015` R05).
- **Phase sizing** — how large a single backlog phase may be is not defined here.
- **How revisions of this standard cite the anti-pattern store** — `phase-irs-10` defines that
  (`REQ-022` R25).

## The mechanical check

A section is **present** when the document contains a line consisting of `## ` or `### ` followed by
one of that section's accepted headings, exactly as written below, case-sensitive, with nothing
after it. Lines inside a fenced code block do not count. Only one heading counts toward two
sections: `Requirement coverage`, explained under the plan table.

A plan **conforms** when every required section is present, and every conditional section is present
whenever its condition holds. A requirement conforms when the same holds for its sections and its
requirement rows pass the row check stated under the requirement table.

A shell form of the check for one section, which drops fenced lines before matching:

```bash
awk '/^```/{f=!f; next} !f' draft.md | grep -Eq '^#{2,3} (Context and scope|Summary|Outcome and scope)$'
```

### Plan sections

| Section | Required | Accepted headings |
|---|---|---|
| Context | always | `Context and scope`, `Summary`, `Outcome and scope` |
| Design | always | `Decisions`, `The chosen design`, `Chosen design`, `Design`, `Approach`, `This is an investigation plan`, `This is a discovery plan` |
| Work | always | `Implementation phases`, `Work and dependencies`, `Phases`, `Work`, `Ordered work and acceptance`, `Sequencing` |
| Verification | always | `Acceptance and verification`, `Requirement coverage` |
| Boundaries | always | `Out of scope`, `What this plan does not do` |
| Open questions | always | `Open questions`, `Open question`, `Open decisions` |
| Requirement coverage | when `depends_on` names a document of kind `requirement` | `Requirement coverage` |
| Concurrency | when the plan names two or more distinct `phase-` ids | `Execution order and real concurrency`, `Execution order` |

The Concurrency condition is read from the draft alone: count the distinct strings matching
`phase-[a-z]+-[0-9]+`, outside fenced lines. The Requirement coverage condition needs one lookup
outside the draft: each `depends_on` id is resolved to its document, and that document's `kind` is
read from its front matter.

Under the conditional rows, a plan paired with a requirement satisfies Verification and Requirement
coverage with the one `Requirement coverage` heading. The two investigation headings under Design
are for plans whose outcome is the thing being investigated. The discovery plan (`PLAN-007`) and the
session-lifecycle plan (`PLAN-008`) are the precedents, and both say why their later phases are not
specified yet.

An Open questions section with nothing open still appears and says so. The plans-directory
consolidation plan (`PLAN-018`) does this: "None outstanding", with the one question it did have
recorded as confirmed with the owner.

### Requirement sections

| Section | Required | Accepted headings |
|---|---|---|
| Problem | always | `Observed problem and scope`, `Problem being solved` |
| Requirements | always | `Observable requirements and verification`, `Requirements` |
| Boundaries | always | `What each requirement is not`, `Out of scope`, `What this deliberately does not require`, `Boundaries and open questions`, `Boundaries and unresolved compatibility` |
| Accepted decisions | optional; not part of conformance | `Accepted decisions` |

The requirement rows form one table with three columns: an ID of the form `R01`, the required
observable behaviour, and the verification method. A row is present when a line matches `^\| R[0-9]+
\|`. A requirement passes the row check when it has at least one such row and every such row has a
non-empty third cell. The requirement documents from `REQ-003` onwards mostly use this form, and it
is the only one a single pattern can check. `REQ-001`'s one-heading-per-requirement form is readable
but cannot be checked the same way.

An `Accepted decisions` section is worth writing when the owner has already ruled on choices the
requirements depend on, as in `REQ-001` and `REQ-004`. Whether that is so is a judgement, so the
section is not part of the mechanical check.

## Content judgements for plans

Each judgement states the standard, then the documents that meet it and the documents that do not. A
reviewer applies these after the mechanical check passes. A document can meet one judgement and fail
another. Several documents are cited on both sides.

### P1. The context names an observed problem and where the evidence is

The context section states what went wrong or what is missing, and points to the record of it.

- **Meets it.** The code-reservation plan (`PLAN-010`) opens with the date two phases both claimed
  `ADR-007`, why the allocator issued it twice, and where the collision is recorded (`GOV-003`). The
  confidentiality sweep (`PLAN-006`) carries an audit table listing each tracked file and what it
  exposes. The downstream-projections plan (`PLAN-034`) pastes the command and its output that show
  `000022`'s figures are stale.
- **Does not.** The mini-systems proposal (`PLAN-002`) opens by describing the systems it proposes,
  and names no observed problem anywhere. The reliability follow-up (`PLAN-004`) calls itself a
  "proposed follow-up to the architectural audit". Apart from one lint issue in step 1, it does not
  say which of that audit's findings each step answers.

### P2. Each decision names the alternative it rejected and what that alternative would have cost

"Chosen because it is good" is not a reason. The reason is what the rejected option would have cost
here.

- **Meets it.** The idea record system (`PLAN-016`) rejects one-file-per-idea and first removes the
  wrong objection with numbers: file count is not the problem, because ext4 and git handle far more
  files. It then states the real cost: a status change rewrites a file, so immutability becomes a
  claim about content rather than a fact about bytes. `PLAN-006` rejects gitignoring `_data/` in
  favour of relocating it, because the gitignore option leaves real files at a path the tooling
  expects. The concurrency programme (`PLAN-026`) ends its first and third decisions with "The cost
  accepted", stating what the chosen option gives up.
- **Does not.** The dynamic-HTML overview (`PLAN-003`) has a decisions table whose rationale column
  names an alternative only by implication, as in "no parallel app", and never states its cost.
  Tailwind is chosen for "Fast prototyping, consistent design system". `PLAN-002` contains no
  alternatives at all.

### P3. It is clear who decided each thing and whether it is settled

A settled decision is stated flatly, with who ruled and when. An unsettled one is marked as a
recommendation once, at the point it is made. The owner's words are quoted rather than paraphrased
when they are the reason.

- **Meets it.** The idea-graph programme (`PLAN-029`) marks its first two decisions "**Ruled:**" and
  states the others as settled. The standalone-explorations plan (`PLAN-037`) quotes the owner's
  2026-09-13 ruling on `G58` verbatim. `PLAN-016` quotes the owner's own constraint ("*some fields
  must change while the entry stays immutable*") as the reason for the event log. The idea-plan
  lifecycle overview (`PLAN-017`), conflict `C18`, says outright "do not claim mandatory reason was
  approved".
- **Does not.** The agent memory plan (`PLAN-001`) carries `status: approved` and a banner saying
  delivery is approved. Its body gives "**Recommendation: Chronicle**" for an agent name, and its
  open question 6 says to confirm that name before implementation. A reader cannot tell whether the
  name was approved. `PLAN-003`'s decisions table does not say who made any of its six decisions.

### P4. Claims about the repository are checked, and the check is shown

A statement about the current state of the repository comes with the command, file line or record
that confirms it.

- **Meets it.** `PLAN-029` has a section "What `G03` already ships, verified in code", naming the
  tool, the components and the routes. `PLAN-034` shows the backlog line proving `phase-idea-07`
  complete and the line where `fold()` is defined. `PLAN-037` backs "no `sys-observability` exists"
  with the `grep -c` that returns `0`.
- **Does not.** `PLAN-001` states that DuckDB VSS is "Available in DuckDB ≥0.10; 1M vectors before
  performance degrades", with no source. `PLAN-002` asserts each signal's value ("Surfaces neglected
  projects before they become embarrassing gaps") with nothing to support it.

### P5. Scope states what is excluded, and why

- **Meets it.** `PLAN-010` excludes three things and gives the reason in four words: "None of those
  failed." The status-regression guard plan (`PLAN-038`) has a "What this plan does not do" section.
  Its first exclusion gives the reason: no other instance is known, and searching for more is a
  separate question.
- **Does not.** `PLAN-002` has no boundary anywhere. `PLAN-001`'s scope line lists only what is
  included.

### P6. Acceptance is observable, and includes the case that must fail

Acceptance names the command or observation, the expected result, and at least one input that must
be rejected. A plan paired with a requirement maps every requirement row to a phase, and every phase
to a row.

- **Meets it.** The document-code plan (`PLAN-005`) gives the exact strings `--next-code` must
  print. It then requires a one-character filename change to fail with a named error. The idea
  priority queue (`PLAN-019`) lists the inputs the governance check must reject: an unknown id and
  an idea in a status the queue does not serve. `PLAN-026`'s requirement coverage table asserts
  coverage in both directions. `PLAN-034` explains, above its table, why `phase-proj-02` carries no
  row for R04.
- **Does not.** `PLAN-001` and `PLAN-002` have no acceptance section and no paired requirement.
  Nothing in either states when the work would be finished.

### P7. Concurrency is measured from declared systems and paths, not asserted

Where a plan registers several phases, it states which can run at the same time, working from each
phase's declared `systems` and `deliverables`.

- **Meets it.** `PLAN-029` names every collision among its five dependency-free phases. For example,
  `phase-idg-10` and `phase-idg-11` share `sys-gov-docs`. From those collisions it derives the one
  set that can run together. `--ready` reports the same collision on 2026-09-22. `PLAN-026`
  concludes that its realistic ceiling is one agent at a time, and says why.
- **Does not.** `PLAN-037` says six of its seven phases "depend on nothing and collide with
  nothing". In the next paragraph it concedes that two of them share `sys-governance`, and
  `PLAN-026` treats a shared system as a collision. The backlog on 2026-09-22 shows five of those
  six declaring `sys-governance`.

### P8. Each open question says who decides, when, and which way the author leans

- **Meets it.** No single plan meets all three parts. Each part is met somewhere:
  - **Who:** the ephemeral-plans policy (`PLAN-015`) records the owner's answer, with its date,
    above the question it answered.
  - **When:** `PLAN-005`'s two open questions each name when they will be settled: after the first
    few walkthroughs exist, and in phase 2 against the actual workflow.
  - **Leaning:** `PLAN-019` gives a leaning for each of its two questions.
- **Does not.** `PLAN-004`'s three open decisions are bare questions, with no owner, no deadline and
  no leaning. `PLAN-001`'s questions 1 to 5 share one deadline, "before Phase 3", and question 6 has
  its own. None names who decides, and only question 6 carries a leaning.

### P9. A superseded passage is marked, dated and explained, and the old text is kept readable

- **Meets it.** `PLAN-015` places each amendment in a dated block naming the owner and the session.
- **Does not.** `PLAN-016` states "**That is superseded.**" and gives the reason, and `PLAN-038`
  records that an earlier draft proposed comparing against `HEAD` alone and that the owner's ruling
  replaced it. Both mark and explain the change, but neither says when it was made. In `PLAN-005`'s
  phase 4 rename table, the From and To columns now read identically on most rows. The rename
  rewrote both columns, so those rows no longer show what was renamed. The content-extraction plan
  (`PLAN-041`) inserts an amendment between the sentence ending "results:" and the table that
  sentence introduces.

### P10. Every label is defined before it is used

A reader who was not in the session must be able to follow the document from the repository alone.

- **Meets it.** `PLAN-010` and `PLAN-019` use no label beyond document codes, phase ids and idea
  ids, each of which resolves to a file or record in the repository.
- **Does not.** `PLAN-029` and `PLAN-026` open with a table defining each group code, such as `G01`
  to `G04`, but then use programme codes such as `P4` and `P6` without defining them. `PLAN-017`'s
  overview uses `L1`–`L11`, `Q-A3` and categories `A`–`N`. Its child `PLAN-017.01` cites "(L7)",
  "the brief" and "this task directs". These labels are defined in a brief that is not in the
  repository.

### P11. The work section states each step's prerequisites

The Work section says which steps depend on which, so that the order can be checked rather than
assumed.

- **Meets it.** `PLAN-029`'s phase table has a "Depends on" column. `PLAN-018` states that steps 3–6
  "must land before or with steps 1–2", and gives the reason.
- **Does not.** `PLAN-002`'s implementation sequence has no dependency column. Its phase 4, the
  Session Briefing, reads the outputs of the signals built in phases 1 and 2, but that dependency is
  shown only in the separate Composition Map, not where the work is ordered.

## Content judgements for requirements

### Q1. The problem section names observed failures and their sources

- **Meets it.** The concurrency requirement (`REQ-013`) lists four failures "recorded in the
  repository rather than hypothesised", each with its idea id or incident. The idea-graph
  requirement (`REQ-014`) lists four gaps, "each observable today", each tied to an idea. The
  document-code requirement (`REQ-001`) cites the two ADR numbers claimed by backlog phases before
  either document existed.
- **Does not.** The idea realization requirement (`REQ-022`) has no problem section. It opens with
  "Observable statements for the pipeline mapped in ARCH-006". The session-taxonomy investigation
  requirement (`REQ-026`) describes what the investigation will do, but not what problem it answers.

### Q2. Each row states one observable behaviour

- **Meets it.** Each of `REQ-013`'s sixteen rows states one behaviour. `REQ-001` R2 is a single
  sentence: "No two governed documents share a code."
- **Does not.** The live-demo requirement (`REQ-006`) R13 puts a glossary of eight terms plus
  extras, a library of six SVG diagrams, an index page and offline viewing into one row. `REQ-022`
  R16 combines thin graph state, a rule for disagreement with the repository, and thread re-keying.

### Q3. Verification is a procedure someone else can run, including what must not happen

Verification names the input and the expected result, and where possible a control case that must
not trigger. A row that no command can verify says so.

- **Meets it.** `REQ-013` R01 requires the stale-claim report to flag a stale phase, and also
  requires "a genuinely live claim in the same run is not flagged". `REQ-001` R3 names two fixtures
  that must fail. The plans-directory requirement (`REQ-004`) R5 gives the grep with its exclusions
  and the expected count, zero. The document-template requirement (`REQ-024`) R06 states "No code
  verification applies — this is a design-record requirement".
- **Does not.** `REQ-022` R01's verification begins "Inspect the orchestrator's graph definition",
  and R04's is "Owner inspection of one queued item per gate category". R01 continues "trace one
  run's ledger entries against its gate decisions". Neither row says what result passes. `REQ-024`
  R01 names the passing and failing cases, but its command is written as `uv run python -c "..."`,
  so it cannot be run as written.

### Q4. Rows state behaviour, not implementation, unless the owner ruled on the implementation

- **Meets it.** `REQ-014`'s boundary section says R16 "does not prescribe the mechanism", and lists
  four surfaces that would satisfy it equally. `REQ-013` says R04 "is not a rule against `git
  stash`".
- **Does not.** `REQ-006` R04 specifies xterm.js, a PTY adapter, ConPTY and `pywinpty` inside the
  observable row, and does not say whether the owner ruled on those choices.

### Q5. A boundary section says what each requirement does not require

- **Meets it.** `REQ-013` and `REQ-014` each end with "What each requirement is not". The entries
  there rule out readings a builder would otherwise have to guess at, for example that `REQ-013` R11
  is satisfied by a recorded acceptance of the risk. `REQ-024`'s out-of-scope list gives a reason
  for each exclusion.
- **Does not.** `REQ-022` has no boundary section. `REQ-006` states its scope inline in its problem
  section, but says nothing about how any individual row may or may not be read.

## Tone

### T1. Say it literally

Write the direct statement. A metaphor carries connotations the author did not choose, and makes the
reader translate it back into the claim.

- **Meets it.** `PLAN-038`: "A guard that hard-fails when it cannot read history would block every
  rebase in the repository, which is a worse failure than the one it prevents." `PLAN-010`'s context
  is literal throughout.
- **Does not.** `PLAN-002` closes each signal with a "Why it matters" line, for example "Converts a
  database into a daily operating rhythm." and "Closes the loop." Dense plans do this too:
  `PLAN-016` writes "A guard proves the lock holds; it leaves the door." and `PLAN-026` writes "that
  is where the gate earns its cost". Each of these has a literal version that is shorter.

### T2. Do not repeat the front matter in the body

- **Meets it.** `PLAN-038` opens with one sentence stating what it implements and a link to its
  requirement. Status and dates stay in the front matter.
- **Does not.** `PLAN-001` repeats its status and date as bold lines under the title. Those lines
  can disagree with the front matter the governance check reads.

## Length

Length is not the measure of quality. A short plan is fine when it is complete. A thin plan is also
fine when it says why it is thin.

- **Short and complete.** `PLAN-018` is under 500 words. Every step has an acceptance-evidence
  column, and the historical documents it deliberately leaves unedited are named.
- **Thin, and says why.** `PLAN-014` has a section "Why this plan is thin, and what that
  demonstrates". `PLAN-007` states "This is a discovery plan" and explains why its later phases are
  absent.
- **Too thin.** `PLAN-004` is about 400 words. Its context gives no evidence (P1) and its open
  decisions are bare (P8).
- **Too long.** `PLAN-001` is over 3,000 words. Most of it specifies JSON contracts, a 30-day
  proposal expiry and vector-store options for agents that do not yet exist. `PLAN-014`'s constraint
  names this failure: "Three of today's four corrections came from building structure ahead of
  demonstrated need."
- **Too dense to read.** `PLAN-017`'s overview compresses twenty-one conflicts into table cells such
  as "Resolved by task synthesis: backward pointer plus merge chain, unique seq". A reader cannot
  evaluate these cells without the conversation that produced them (P10).

## Optional sections

These headings are not part of the mechanical check. Each is worth including only under the stated
condition. Each also has an example in the corpus of a plan that includes it without the condition
holding, which is what a copied-by-habit section looks like.

- **`Known facts not to rediscover`** — only for facts the body does not already state.
  - Meets it: `PLAN-026`'s list includes facts found nowhere else in the plan. The private-content
    check reports `0` identifiers in a worktree against `31` in the primary checkout, and `G09`
    deliberately does not wait for `G10`'s rewrite, for a stated reason.
  - Does not: each of `PLAN-037`'s eight bullets repeats a ruling already made in its body.
  - Where nothing new remains, omit the section.
- **`Key references`** — only links the reader needs that the body does not already give, each with
  a note on what it is needed for.
  - Meets it: `PLAN-034`'s entries for `ADR-009` and `AGENTS.md` each say why the reader needs them.
    `ADR-009` is listed as "why `_data/` no longer answers `000022`'s question". Its first entry,
    "The requirement", has no note.
  - Does not: `PLAN-026` links `REQ-013` in its opening section, then lists it again as "The
    requirement", with no note.
- **`Sizing against the partition`** — only in a plan derived from an idea partition, and only to
  explain a difference between the partition's estimate and the phases registered.
  - Meets it: `PLAN-026` explains its delta from 6–8 to nine phases.
  - Does not: every group in `PLAN-037` lands inside the partition's estimate, so there is no
    difference to explain. Its sizing section still lists each group's estimate and count.
- **`Deliverables`** — only when it lists what the work produces, each with what it is for, and not
  the plan itself.
  - Meets it: eight of `PLAN-016`'s nine entries say what they are for. The ninth, "An amendment to
    `ADR-010`", is explained in the body above it.
  - Does not: `PLAN-015`'s list opens with "This plan, as the standing policy". Its second item is a
    file it says was deleted.
