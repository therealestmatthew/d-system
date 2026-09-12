---
schema_version: 1
id: doc-prompt-idea-batching-pre-plan-package
code: PROMPT-025
title: Idea-batching pre-plan package — seed the planning session that partitions the idea corpus into plannable batches
kind: prompt
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems: [sys-governance, sys-backlog, sys-portfolio]
depends_on: [doc-prompt-pack-protocol, doc-idea-record-system, doc-idea-staging, doc-conversation-guidelines]
---

# Idea-batching pre-plan package — seed the planning session that partitions the idea corpus into plannable batches

The idea log has reached 144 records and every one of them is triaged. Nothing is `open`; the
triage sweep that closed `SESS-2026-09-12-01` finished the per-idea work. What does not exist is
any grouping: 135 triaged ideas sit as 135 independent items, and no document says which of them
are parts of one thing.

This document is the pasteable seed for the **planning session** that manufactures the prompt
pack for fixing that — the Prompt A of the prompt-pack protocol
([GOV-008](../08-governance/GOV-008-prompt-pack-protocol.md)), whose adoption is recorded in
[ADR-017](../04-decisions/ADR-017-prompt-pack-methodology.md). Nothing here is analysis;
everything here is the owner's ratified input to planning.

The idea this work closes is `000125` (holistic triage of the accumulated idea batch:
categorize, prioritize, and split into plans). It is promoted only when the batching document
is approved, not when this package is written.

**The build this pack drives is the analysis itself.** That is unusual for a GOV-008 pack — the
two precedents drove code builds — and it is deliberate. The "work items" are agent dispatches
over a text corpus; the "deliverable" is a staging document. Every GOV-008 rule about worktrees,
ports and browser verification is therefore inapplicable and the pack must say so explicitly
rather than carry dead structure.

## How to run this

Paste the prompt block at the end into a fresh session. That session produces **Prompt B** — the
pack-factory prompt — and nothing else. It does not analyse ideas, does not dispatch agents, and
does not write the batching document.

## Decisions the owner has already made (do not re-ask these)

Ratified by the owner on 2026-09-12.

1. **The pack drives the analysis.** Prompt A and Prompt B manufacture a pack whose build is the
   batching analysis: four analyst agents, an adversarial reviewer run twice, and an agent
   integrator under owner review. The plans that the batches eventually become are out of scope
   here; each gets its own pack later, when it is time to build it.

2. **The demo work leaves by a separate lane.** The demo is the week of 2026-09-15. A fast lane
   runs outside this pack entirely: demo-blocking and demo-improving ideas are cut, ranked and
   handed to the build already in flight as backlog phases or fix items. The pack does not wait
   for it and does not re-plan what it consumes. See "The exclusion list" below — this is an
   input to the pack, not a part of it.

3. **Four full-corpus analysts plus an adversary that runs twice — six dispatches.** Each
   analyst reads all 135 triaged ideas, not a slice. Slices were considered and rejected: the
   partition criterion below is a property of the whole corpus, and an agent holding a slice
   cannot assess independence from a slice it never saw.

4. **All four analysts do the same complete job independently.** None is a partial lens; each
   produces a full partition covering the whole corpus under the criterion in decision 9, working
   alone and without sight of any other's output. Dependency, feature cohesion, system boundary
   and effort are things every analyst weighs, not assignments split between them.

   Four independent answers to one question. Where they agree, the corpus said it; where they
   diverge, the corpus is genuinely ambiguous at that boundary and the integrator rules.

5. **Input varies across the four as a bias control.**

   - **Analysts 1, 2 and 3** read title, body, links **and** the triage finding for every idea.
   - **Analyst 4** reads title, body and links **only** — no findings. It is the control.

   Analyst 4 exists because every triaged idea carries a finding written by one agent charter
   (`agent-idea-triage`). Anything the three finding-readers agree on that analyst 4 reproduces
   independently is not inherited framing.

   The three finding-readers additionally receive the corpus in **different presentation
   orders** — id ascending, id descending, and shuffled under a recorded seed. This controls for
   anchoring: an analyst that groups partly by what it read first would otherwise produce a
   stable artifact across all three that reads as consensus. The variation costs nothing and the
   seed is recorded so the run is reproducible.

6. **The adversary runs twice, on either side of synthesis.**

   - **Audit 1 — the four partitions.** Before synthesis: does each partition cover the corpus,
     are its groups actually independent, did the four agree for the right reasons?
   - **Audit 2 — the merge.** After synthesis: does the integrated partition follow from the four
     inputs, or did the integrator's judgment introduce groupings no analyst proposed?

   Audit 2 exists because synthesis is where the most judgment is applied and, until now, was the
   only step in the design nothing checked. Both audits are independent of whoever integrates,
   because a gate whose reviewer is also the integrator is not a gate.

   Analysts are general-purpose agents running pack-supplied prompts and need no charter; the
   adversary earns a committed charter in `.claude/agents/`, scoped as a **general partition
   adversary** — able to audit any proposed partition, whether of ideas, backlog phases or plan
   boundaries, so the role outlives this sweep. One charter serves both audits; the pack supplies
   a different brief for each.

7. **An agent integrates; the owner rules.** The agent running the build session reads all five
   analyst-and-audit reports against the corpus, resolves conflicts, and proposes the partition.
   Delegate and verify: where analysts disagree about independence, it checks the actual files
   before ruling rather than counting votes. Audit 2 then checks that merge, and the owner
   accepts or corrects the result — the owner rules on the partition and on every decline
   candidate. **No analyst agent has the final say**, and no integration reaches the owner
   unaudited.

8. **Output is an ungoverned staging document first.** It lands in `docs/00-working/` under
   [ADR-010](../04-decisions/ADR-010-idea-staging.md). The owner corrects it. Approved batches
   become governed plans in later sessions. The batching is **not** additionally recorded as
   anchor ideas and links in `_data/ideas.jsonl` — that option was considered and declined to
   avoid keeping two copies consistent.

   Ideas that survive synthesis without a confident home go into a named **unbatched** section
   with a reason each, rather than being forced into a best-fit batch or swept into a catch-all.
   The size of that section is a quality signal about the partition and is reported as one.

9. **The partition criterion, in the owner's words** — this is the specification, and all four
   analysts receive it verbatim:

   > We ultimately need to batch them up so that logically they can be implemented together,
   > that they are parts of a related feature, or that they have dependencies on each other. If
   > two groups of ideas can be completely independently implemented, and they are fully
   > mutually exclusive, then they belong in two separate plans.

10. **The partition is two-level: a fine partition, rolled up into 8–12 programmes.**

    Analysts first partition by the criterion in decision 9 alone — however many groups that
    yields, with nothing merged to hit a number. They then group those into **8–12 named
    programmes**, each becoming one governed plan, with the fine partition visible underneath as
    that programme's members.

    This exists because decision 9 and a batch target pull against each other. If the corpus
    holds twenty independent groups, a hard target of 8–12 forces merging things the criterion
    says to split — and four agents given a number tend to hit the number. The two levels
    separate the question the criterion answers (what is genuinely independent) from the question
    the owner is asking (what should I read and plan). Neither distorts the other.

    It also settles what happens when the corpus shrinks: the demo fast lane removes an unknown
    number of ideas, so the fine partition scales with whatever is left while the programme count
    stays 8–12, because that figure is a readability target for the top level rather than a
    property of the corpus.

11. **Decline candidates are flagged, never written, and presented stratified by agreement.**
    Every analyst must nominate ideas it judges dead, stale or not worth building, each with a
    reason — a required section of every report, not an optional aside. Nothing is written to the
    idea log: no `discarded` status event is appended by any agent in this build.

    Four analysts produce four overlapping lists, so synthesis presents them in three tiers —
    **nominated by all four**, **by a majority**, **by a single analyst** — each carrying the
    reasons given. The owner sees the confidence behind each nomination instead of a flattened
    list, can rule quickly on the unanimous tier, and nothing is filtered out by an agent on the
    way. The owner rules on each candidate individually.

12. **The build session stops at gates for owner check-in** — twice before synthesis, once after.
    It pauses when the four analyst reports land, again when audit 1 returns, and again when
    audit 2 has checked the merge. The third pause is where the owner accepts or corrects the
    partition. This is the `GOV-008` gate check-in policy answered up front, and it is recorded
    in the kick-off record. A critical issue still gets the dual review `GOV-008` requires before
    the build pauses for it outside a gate.

13. **`GOV-008` stages 6 and 7 collapse into the kick-off record.** No separate coordinator
    prompt is written: this build is one session of six dispatches and needs no resume harness.
    The kick-off record carries the starting state, the ratified deltas, the dispatch order and
    the kick-off paragraph. This is a deliberate, documented deviation from the protocol.

    The owner's observation when ratifying it, recorded because it outlives this pack: this may
    be a class of work that does not fully merit a prompt pack at all, and lighter planning
    methodologies are worth capturing separately. That is now idea `000145`, and it is **not** a
    task for this pack or its build.

14. **The exclusion list is a YAML file in `docs/00-working/`.** Ungoverned and machine-readable,
    one entry per excluded id with its disposition. The pack's corpus builder reads it, so
    exclusion is mechanical rather than something a human has to remember. The precedent is
    `ideas-priority.yaml`, which already holds an operational ordering decision in exactly this
    shape. It is **not** additionally recorded as annotations on the ideas — the same
    two-copies-to-keep-consistent objection that decision 8 raised applies here.

15. **A batch record states six things:** a short name; the member idea ids; why these belong
    together; the independence argument; which batches must precede it; and a rough size in
    sessions or phases. The independence field is the load-bearing one — it is what turns
    decision 9's criterion from an assertion into something the owner and the adversary can
    check. All four analysts use this shape, fixed here so four reports arrive comparable rather
    than in four formats.

    **Independence is argued in detail only against plausibly-overlapping batches** — those
    sharing a system, a file path, a dependency, or an idea that nearly went either way — and
    asserted in one line against the rest. Arguing every pair is quadratic: twelve batches is
    sixty-six arguments per analyst, four times over, and most of them would say "these share
    nothing." The detail goes where the criterion can actually fail.

16. **The descope ladder, in order:** the third finding-reader goes first, then the second, then
    the merge re-audit (audit 2), then audit 1, and the control (analyst 4) goes last. Replicates
    are the most redundant part of the design and are spent first; the bias control and the
    independent gate are what make the result trustworthy and are surrendered last. Per
    `GOV-008`, no rung is taken without the owner's explicit direction.

    Note for the owner: the ladder was ratified before decision 7 added audit 2. Its placement —
    the first thing spent after the replicates — is the drafter's, on the grounds that it guards
    a step the owner personally reviews anyway, whereas audit 1 guards four agent outputs nobody
    else checks. Reorder it if that reasoning does not hold.

## The corpus (measured 2026-09-12)

| Slice | Count | Size |
|---|---|---|
| Ideas in `_data/ideas.jsonl` | 144 | — |
| `triaged` — the corpus to partition | 135 | ~53k tokens of title and body |
| Their triage findings | 135 | ~74k tokens |
| Corpus with findings | — | ~127k tokens |
| Ideas carrying at least one link | 90 | — |
| `promoted` — excluded | 7 | `000003`, `000007`, `000019`, `000039`, `000067`, `000104`, `000112` |
| `discarded` — excluded | 2 | `000076`, `000094` |

All figures come from `fold(load_events())` in `src/db/ideas.py`. Agents read idea state through
`fold()` and never through the raw JSONL — the standing rule for every reader except idea-system
analysis itself.

Promoted ideas already have plans. Discarded ideas would need a `revisited` event before they
could re-enter, which nobody has requested.

## The exclusion list

The demo fast lane (ratified decision 2) runs before this pack executes and produces a YAML file
in `docs/00-working/` listing the idea ids it consumed, one entry each with its disposition:
queued as a backlog phase, fixed directly, or dropped. Prompt B specifies its exact filename and
key names, and states:

- that the pack's corpus is the 135 triaged ideas **minus** every id in that file;
- that an excluded idea the fast lane ends up not shipping returns to the corpus rather than
  falling between the two lanes — so the file records disposition, not merely membership;
- that the corpus builder reads the file rather than a human transcribing ids, since a corpus
  assembled by hand is the kind of error no gate in this pack would catch.

The candidate pool the fast lane cuts from runs roughly `000095`–`000137`: workbench defects,
HTML Viewer behaviour, rotator variants, runbook gaps, and cache invalidation during demo week.
The owner has ruled that the governance atlas page (`000093`) is **not** part of the demo. The
demo audience is novice practitioners and the subject is skills and agents, so the visuals that
earn a place are the ones that make skills and agents legible to someone seeing them for the
first time.

## What the planning session must produce, in order

1. **Prompt B — the pack-factory prompt**, as a governed document taking its code from
   `--next-code prompt`. Its required sections are in `GOV-008`'s template appendix: role
   statement and hard scope limits (documents only), preflight, the pack artifacts to produce in
   order with their codes, the open-questions protocol, and the stop condition.

2. Nothing else. Prompt B is the only deliverable of this session. The gate between Prompt A and
   Prompt B is real: the adversarial review of Prompt B (`GOV-008` stage 3) happens before
   Prompt B runs, and the owner signs off on the revised Prompt B before the pack is drafted.

Prompt B, when it later runs, must produce a pack containing at minimum:

- the four analyst prompts, each idempotent and dispatchable verbatim, each carrying the partition
  criterion from ratified decision 9 unaltered and the two-level structure from decision 10, and
  differing **only** in whether triage findings are supplied and in corpus presentation order;
- **two** adversary briefs — audit 1 over the four partitions, including the convergence check
  named under "Known failure modes" below, and audit 2 over the integrator's merge;
- the adversary's charter file for `.claude/agents/`, scoped as a general partition adversary and
  serving both briefs;
- the synthesis protocol the integrator follows to turn five reports into one partition,
  including how a disagreement about independence is resolved against the repository, how a 3–1
  split is read when the dissenter is the control, what unanimity means as against a bare
  majority, and how the three decline tiers in decision 11 are assembled;
- the output contract for the staging document, implementing decision 15's six fields, its
  plausibly-overlapping rule for the independence argument, decision 10's two levels, and the
  named unbatched section from decision 8;
- the corpus builder that assembles each analyst's input from `fold()`, applies the exclusion
  file from decision 14, includes or withholds findings per decision 5, and emits the three
  presentation orders with the shuffle seed recorded;
- the descope ladder in decision 16's order.

## Known failure modes the pack must address

**Framing inheritance.** Four agents reading one corpus under near-identical instructions can
converge because they were told to, not because the corpus says so. Decision 5's varied input and
presentation order are the first defence; audit 1's brief is the second, and must include:
*did the four analysts agree for the right reasons, or did they inherit the same framing from the
prompt?* Convergence that survives that question is signal; convergence that does not is an
artifact of the pack.

**Finding bias.** Every triaged idea carries a finding written by one agent charter
(`agent-idea-triage`). An analyst that reads findings inherits that charter's framing of what
each idea is about. Decision 5 addresses this by design rather than by review — analyst 4 never
sees a finding, so any grouping it reproduces independently is not an inheritance.

**Anchoring.** An analyst that reads the corpus in id order may group partly by reading order,
and three analysts given the identical ordering would reproduce that artifact identically — which
looks exactly like agreement. The three finding-readers therefore receive ascending, descending
and shuffled orderings, with the shuffle seed recorded.

**Partition completeness.** An analyst can produce a tidy grouping by quietly dropping the ideas
that do not fit. Every report must account for all 135 (minus exclusions) with no idea unassigned
and no idea in two groups, and must state its residual — the ideas it could only place weakly.
The adversary verifies the count arithmetically rather than trusting any analyst's claim to have
covered the corpus.

**Majority mistaken for truth.** Three of the four read identical evidence, so a 3–1 split where
analyst 4 is the dissenter is the expected shape of finding bias, not a settled vote. The
synthesis protocol must forbid resolving any disagreement by counting analysts. The integrator
checks the repository and rules; it never splits the difference, never defers to the majority,
and never defers to an analyst on the grounds that it read more.

## Open questions for the owner

**There are none.** Every question this package opened with was resolved with the owner on
2026-09-12 across four AskUserQuestion batches: agent count and composition, findings
distribution, presentation-order variance, gate check-in policy, stage 6/7 collapse, adversary
charter scope, batch granularity, decline authority, residual handling, exclusion-list format,
the batch record contract and the descope ladder. All of them are in the ratified section above.
**Do not re-ask any of them.**

This is stated as a section rather than omitted because `GOV-008` requires Prompt A to carry an
open-questions list, and an empty list is a fact about this package, not an oversight in it. The
planning session's job is therefore narrower than the protocol's default: draft Prompt B from
settled inputs, and raise a question only if drafting exposes something genuinely new.

One standing exception: the exclusion file does not exist yet, because the demo fast lane has not
run. Prompt B specifies its filename, keys and disposition values — it does not wait for the file
or invent its contents.

## Standing constraints

`AGENTS.md` governs. Plan before code. Every governed document takes its code from
`--next-code`. The idea log is written only through `tools/append_idea.py`, never by hand, and
never with a guessed id — the id comes from the writer's own output. `AGENTS.md` and `CLAUDE.md`
are never edited without the owner's explicit per-change approval. Integration into `dev` is the
owner's call each time; pushing an agent's own branch is not. A failing check is a result to
record, not a step to retry until quiet. New asks the owner raises mid-session are captured as
ideas immediately through the sanctioned writer, per
[GOV-006](../08-governance/GOV-006-conversation-guidelines.md), rather than folded into the work.

Cost protocol per `GOV-008`: Haiku for mechanical gates, Sonnet as the standard for judgment
work, Opus never pre-assigned and used at most as a single documented escalation. At most two fix
cycles per work item. Six dispatches — four analysts and the adversary twice — are the bulk of
this build's spend: analysts 1–3 at roughly 130k tokens of input each, analyst 4 at roughly 55k
without findings, audit 1 carrying four partitions plus the corpus it checks them against, and
audit 2 carrying the merge and the four inputs it must follow from. The close-out reports actual
spend against those figures.

Because the build is documents-only, the pack must **not** carry worktree setup, port
assignments, browser verification or schema-drift gates. Their absence is a deliberate scoping
statement, and Prompt B says so rather than leaving a reader to wonder whether they were
forgotten.

## Deadline context

The live demo is the week of 2026-09-15 — four days from this document. **This pack is not
demo-critical.** The demo's claim on the schedule is served by the fast lane in ratified decision
2, which runs first and independently. If the two compete for attention, the fast lane wins and
this pack waits; that is the intended behaviour, not a descope.

Two phases are claimed as of 2026-09-12: `phase-wb-10` (agent-fable) and `phase-demo-07`
(agent-demo-glossary). Neither this pack nor its build claims a phase or touches a locked system.

---

## The prompt

> You are the planner for the D-System idea-batching prompt pack. Read `AGENTS.md`, then
> `docs/08-governance/GOV-006-conversation-guidelines.md`, then
> `docs/08-governance/GOV-008-prompt-pack-protocol.md`, then this document
> (`docs/02-prompts/PROMPT-025-idea-batching-pre-plan-package.md`) in full — it carries the
> owner's sixteen ratified decisions, the corpus measurements and the known failure modes.
>
> Produce exactly one artifact: **Prompt B, the pack-factory prompt**, as a governed document
> whose code comes from `uv run python -m src.governance --next-code prompt`. Follow `GOV-008`'s
> template appendix for Prompt B's required sections.
>
> **Every question this package would normally leave open is already answered.** Do not re-ask
> any of the sixteen decisions. Use AskUserQuestion only if drafting Prompt B exposes something
> genuinely new — and if it does, ask rather than guess.
>
> Do not analyse ideas, do not dispatch agents, do not draft the analyst prompts, and do not write
> the batching document: those are Prompt B's job, and Prompt B runs only after its adversarial
> review (`GOV-008` stage 3) and the owner's sign-off. Read idea state through `fold()` in
> `src/db/ideas.py`, never the raw JSONL.
>
> Stop when Prompt B exists, the governance check exits 0, and the owner has a review summary
> naming what Prompt B will produce and what it deliberately omits.
