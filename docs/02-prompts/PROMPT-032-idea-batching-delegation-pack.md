---
schema_version: 1
id: doc-prompt-idea-batching-delegation-pack
code: PROMPT-032
title: Idea-batching delegation pack
kind: prompt
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-13'
systems: [sys-governance, sys-backlog, sys-portfolio]
depends_on: [doc-prompt-idea-batching-pre-plan-package, doc-prompt-idea-batching-pack-factory, doc-prompt-pack-protocol]
---

# Idea-batching delegation pack

Every prompt the idea-batching build session dispatches, one delimited section per dispatch.
Produced by `GOV-008` stage 4 from the pack factory ([PROMPT-026](PROMPT-026-idea-batching-pack-factory.md)),
which was itself drafted from the owner's sixteen ratified decisions in
[PROMPT-025](PROMPT-025-idea-batching-pre-plan-package.md). Nothing is authored mid-build: the
session sends each fenced block **verbatim** and sends nothing that is not in this pack.

Where this pack and the kick-off record differ, **the kick-off record wins**.

## What this build is, and what it therefore does not carry

The build is an **analysis**, not a code build. Four analyst agents each partition the whole
idea corpus independently, an adversary audits twice, an agent integrates, and the owner rules.
The deliverable is one ungoverned staging document in `docs/00-working/`.

Because of that, this pack deliberately contains **no per-dispatch worktree setup, no port
assignments, no browser verification and no schema-drift gates**. Their absence is scoping, not
oversight — a reader arriving from the code-build precedents (`PROMPT-018`, `PROMPT-021`) should
not go looking for them. The analysts and the adversary are subagents dispatched inside the build
session, not sessions of their own, and they write only to the gitignored `_working/idea-corpus/`,
so none of them needs an isolated checkout.

**That scoping covers the dispatches, not the session.** The build session itself works in a
worktree like every session, per `AGENTS.md`'s worktree-everywhere rule (2026-09-12) — it writes
the batching staging document into `docs/00-working/`, which is a tracked file. `K` below carries
the step. Owner ruling, 2026-09-12: `PROMPT-025`'s "must not carry worktree setup" constraint is
read narrowly as scoping to the dispatches, and no ratified decision is amended.

## Section letters

The precedents fix `K` for kickoff, `C*`/`V*` for creator/validator pairs, `G` for the phase gate
and `A` for adversarial review. This build has **no creators and no validators** — it has
replicate analysts and two adversarial audits. So:

| Letter | Meaning here |
|---|---|
| `K` | kickoff |
| `R1`–`R4` | the four replicate analysts |
| `A1` | adversarial audit 1 — over the four partitions |
| `S` | synthesis protocol (not a dispatch) |
| `A2` | adversarial audit 2 — over the merge |
| `G` | the gate |

`C*` and `V*` go unused. **`A` keeps its established adversarial meaning** and `V*` is not
repurposed for the audits — a reader arriving from the precedents would otherwise read the
letters backwards.

## Conventions

- **Idempotency**: every dispatch opens with *"Assess the current state of the repository against
  the deliverables below; do only what is missing; report what already existed."* A dispatch may
  be re-sent in a later session without harm.
- **Truncation**: if a dispatched agent's output is cut off by its turn limit, resume that same
  agent; never re-run it from scratch (idea `000077`).
- **Model policy** (`GOV-008` cost protocol, binding): haiku for mechanical gates, **sonnet as the
  standard for judgment work**, opus never pre-assigned — at most one documented escalation per
  build, only when absolutely necessary. All four analysts and both audits are judgment work:
  sonnet.
- **Analysts are general-purpose agents.** They need no charter. The adversary has a committed
  charter, `partition-adversary`, and both audits dispatch to it with different briefs.
- **No analyst sees another's output**, and no analyst may dispatch subagents.
- **Nothing in this build writes to the idea log.** No `discarded` status event, no annotation, no
  link — by any agent, at any stage, including decline nominations.

## The corpus

Built by `tools/build_idea_corpus.py` ([OPS-015](../08-governance/OPS-015-build-idea-corpus.md))
into `_working/idea-corpus/`, which is gitignored. The builder emits one file per analyst plus a
manifest:

| File | Contents |
|---|---|
| `corpus-R1.md` | title, body, links, findings — id ascending |
| `corpus-R2.md` | title, body, links, findings — id descending |
| `corpus-R3.md` | title, body, links, findings — shuffled under the recorded seed |
| `corpus-R4.md` | title, body, links — **no findings** — id ascending |
| `manifest.json` | corpus size, the shuffle seed, excluded ids, the multi-finding set |

The corpus is the `triaged` ideas minus every id the demo fast lane's exclusion file records as
`queued` or `fixed`. **Read the manifest for the actual size before dispatching** — it was 129 at
pack time, and it moves whenever the fast lane or the idea log moves.

---

### K — kickoff

Not a dispatch to a subagent: the checklist the build session runs itself before dispatching
anything.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

1. Work in a worktree. AGENTS.md requires one for every session regardless of what the work
   touches; this build writes the staging document into docs/00-working/, a tracked file. From
   the primary checkout on an up-to-date dev:

     git worktree add -b agent/idea-batching ../d-system-worktrees/idea-batching dev
     cd ../d-system-worktrees/idea-batching
     uv venv && uv sync --extra dev

   Do not switch the primary checkout's branch, and run everything below in the worktree.

2. Preflight, recording real output:

     uv run python -m src.governance --inventory     # must exit 0
     uv run python -m src.governance --ready         # active claims; check max_active numerically
     uv run pytest                                   # must be green
     git status --short                              # clean checkout expected

   A failing check is a result to record, not a step to retry until quiet.

3. Build the corpus and read the manifest:

     uv run python tools/build_idea_corpus.py
     cat _working/idea-corpus/manifest.json

   Record the corpus size, the shuffle seed and the count of excluded ids. Do not assume 129.
   If the manifest's size disagrees with the kick-off record's pinned figure, that is a fact to
   report to the owner, not a discrepancy to reconcile silently.

4. Dispatch order. R1, R2, R3 and R4 are independent and may run concurrently; none may see
   another's output. Then GATE 1. Then A1. Then GATE 2. Then synthesis (S, in the main session).
   Then A2. Then GATE 3.

5. Gate schedule (PROMPT-025 decision 12) — the build stops for owner check-in at each:

     GATE 1  when the four analyst reports land
     GATE 2  when audit 1 returns
     GATE 3  when audit 2 has checked the merge — where the owner accepts or corrects the
             partition, and rules on every decline candidate individually

   A critical issue arising outside a gate STOPS AND GOES TO THE OWNER. GOV-008's dual review
   does not apply in this build: it requires an adversarial agent that challenges the finding
   and attempts a solution, and the only charter this pack ships is barred from repairing what
   it audits. The kick-off record's ratified delta 6 governs this.

6. Analyst reports are written to _working/idea-corpus/report-R1.md .. report-R4.md. The audits
   read them from there.
```

---

### R1 — analyst 1 (findings, id ascending)

Dispatch to a general-purpose agent, model sonnet.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

You are partitioning a corpus of parked ideas into groups that can each become one plan. You
work alone. Do not dispatch subagents. Do not write to _data/ideas.jsonl or any other
repository file; your only output is the report named at the end.

Read your corpus at _working/idea-corpus/corpus-R1.md. It contains every idea's title, body,
links and findings. Read all of it before grouping anything.

THE PARTITION CRITERION. This is the specification. Apply it as written:

    We ultimately need to batch them up so that logically they can be implemented together,
    that they are parts of a related feature, or that they have dependencies on each other. If
    two groups of ideas can be completely independently implemented, and they are fully
    mutually exclusive, then they belong in two separate plans.

TWO LEVELS. Produce both, in this order:

  Level 1 — the fine partition. Partition the corpus by the criterion above ALONE, into
  however many groups that yields. Do not merge anything to hit a number. If the criterion
  says there are twenty independent groups, there are twenty.

  Level 2 — the programmes. Roll the fine partition up into 8-12 named programmes, each of
  which would become one governed plan, with the fine partition visible underneath as that
  programme's members. The 8-12 figure is a readability target for the top level, not a
  property of the corpus — it constrains level 2 only and must never distort level 1.

BATCH RECORD. Every group at BOTH levels states six things:

  1. a short name;
  2. the member idea ids;
  3. why these belong together;
  4. the independence argument;
  5. which batches must precede it;
  6. a rough size in sessions or phases.

Field 4 is load-bearing — it is what turns the criterion from an assertion into something the
owner and an adversary can check. Argue independence IN DETAIL only against
plausibly-overlapping batches: those sharing a system, a file path, a dependency, or holding
an idea that nearly went either way. Against every other batch, one line asserting independence
is enough. Do not argue every pair; most pairs share nothing and the detail belongs where the
criterion can actually fail.

COMPLETENESS. Account for every idea in the corpus. No idea unassigned, no idea in two groups.
State your arithmetic explicitly: corpus size in, ids placed, ids unbatched, and confirm they
add up. State your residual — the ideas you could only place weakly — by id.

UNBATCHED SECTION. Ideas with no confident home go in a named "unbatched" section with a reason
each. Never force one into a best-fit batch and never sweep them into a catch-all. The size of
this section is a quality signal about your partition, not a failure; report it as one.

DECLINE CANDIDATES. A REQUIRED section, not an optional aside. Nominate every idea you judge
dead, stale or not worth building, with a reason each. Write NOTHING to the idea log — no
status event, no annotation. You are nominating for the owner to rule on, not deciding.

Some ideas carry MORE THAN ONE finding; the corpus marks them. Treat those as layered and
possibly internally contradictory evidence rather than a single settled account.

Write your report to _working/idea-corpus/report-R1.md. Stop when it contains the fine
partition, the programmes, the completeness arithmetic, the unbatched section and the decline
candidates.
```

---

### R2 — analyst 2 (findings, id descending)

Identical to `R1` except for the corpus file. Dispatch to a general-purpose agent, model sonnet.

```
[Send R1's block verbatim, with exactly one substitution:
   corpus-R1.md  ->  corpus-R2.md
   report-R1.md  ->  report-R2.md ]
```

The presentation order is a property of the file, not of the prompt. `R2` is never told its
ordering differs from anyone's — telling it would reintroduce the framing the variation exists
to control.

---

### R3 — analyst 3 (findings, shuffled under the recorded seed)

Identical to `R1` except for the corpus file. Dispatch to a general-purpose agent, model sonnet.

```
[Send R1's block verbatim, with exactly one substitution:
   corpus-R1.md  ->  corpus-R3.md
   report-R1.md  ->  report-R3.md ]
```

The seed is recorded in `manifest.json` so the run is reproducible. `R3` is not told the corpus
is shuffled.

---

### R4 — analyst 4 (no findings, id ascending) — THE CONTROL

Dispatch to a general-purpose agent, model sonnet.

**`R4` is the control and must never learn that it is one.** It is not told that findings exist,
that its input differs from anyone's, or that other analysts are running. A control that knows
it is a control is not one. The block below is `R1`'s with every reference to findings removed —
send it exactly as written and add nothing.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

You are partitioning a corpus of parked ideas into groups that can each become one plan. You
work alone. Do not dispatch subagents. Do not write to _data/ideas.jsonl or any other
repository file; your only output is the report named at the end.

Read your corpus at _working/idea-corpus/corpus-R4.md. It contains every idea's title, body and
links. Read all of it before grouping anything.

THE PARTITION CRITERION. This is the specification. Apply it as written:

    We ultimately need to batch them up so that logically they can be implemented together,
    that they are parts of a related feature, or that they have dependencies on each other. If
    two groups of ideas can be completely independently implemented, and they are fully
    mutually exclusive, then they belong in two separate plans.

TWO LEVELS. Produce both, in this order:

  Level 1 — the fine partition. Partition the corpus by the criterion above ALONE, into
  however many groups that yields. Do not merge anything to hit a number. If the criterion
  says there are twenty independent groups, there are twenty.

  Level 2 — the programmes. Roll the fine partition up into 8-12 named programmes, each of
  which would become one governed plan, with the fine partition visible underneath as that
  programme's members. The 8-12 figure is a readability target for the top level, not a
  property of the corpus — it constrains level 2 only and must never distort level 1.

BATCH RECORD. Every group at BOTH levels states six things:

  1. a short name;
  2. the member idea ids;
  3. why these belong together;
  4. the independence argument;
  5. which batches must precede it;
  6. a rough size in sessions or phases.

Field 4 is load-bearing — it is what turns the criterion from an assertion into something the
owner and an adversary can check. Argue independence IN DETAIL only against
plausibly-overlapping batches: those sharing a system, a file path, a dependency, or holding
an idea that nearly went either way. Against every other batch, one line asserting independence
is enough. Do not argue every pair; most pairs share nothing and the detail belongs where the
criterion can actually fail.

COMPLETENESS. Account for every idea in the corpus. No idea unassigned, no idea in two groups.
State your arithmetic explicitly: corpus size in, ids placed, ids unbatched, and confirm they
add up. State your residual — the ideas you could only place weakly — by id.

UNBATCHED SECTION. Ideas with no confident home go in a named "unbatched" section with a reason
each. Never force one into a best-fit batch and never sweep them into a catch-all. The size of
this section is a quality signal about your partition, not a failure; report it as one.

DECLINE CANDIDATES. A REQUIRED section, not an optional aside. Nominate every idea you judge
dead, stale or not worth building, with a reason each. Write NOTHING to the idea log — no
status event, no annotation. You are nominating for the owner to rule on, not deciding.

Write your report to _working/idea-corpus/report-R4.md. Stop when it contains the fine
partition, the programmes, the completeness arithmetic, the unbatched section and the decline
candidates.
```

---

### A1 — adversarial audit 1: the four partitions

Dispatch to `partition-adversary`, model sonnet. Runs after GATE 1.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

Adversarially audit four independent partitions of the same idea corpus. Assume each is broken
and find where it fails.

Inputs: _working/idea-corpus/report-R1.md through report-R4.md, the corpora they were built
from (corpus-R1.md .. corpus-R4.md) and _working/idea-corpus/manifest.json.

1. COVERAGE, ARITHMETICALLY. For each report, verify the count yourself against the manifest's
   corpus size. Do not trust an analyst's claim to have covered the corpus. Report any idea
   unassigned, any idea appearing in two groups, and any discrepancy between an analyst's
   stated arithmetic and the actual ids in its report.

2. INDEPENDENCE. Test the groups against the criterion the analysts were given:

       We ultimately need to batch them up so that logically they can be implemented together,
       that they are parts of a related feature, or that they have dependencies on each other.
       If two groups of ideas can be completely independently implemented, and they are fully
       mutually exclusive, then they belong in two separate plans.

   Check the repository where an independence claim is checkable — shared systems in
   docs/08-governance/systems.yaml, shared file paths, shared dependencies. An independence
   argument you could have tested and did not is not a finding.

3. THE CONVERGENCE CHECK. Did the four analysts agree for the right reasons, or did they
   inherit the same framing from the prompt? Convergence that survives that question is signal;
   convergence that does not is an artifact of the pack.

   R4 read a different corpus from R1-R3. A 3-1 split with R4 dissenting is the EXPECTED SHAPE
   OF FINDING BIAS, not a settled vote, and you must not read it as one.

   But the control is confounded, and you must say so rather than pretend otherwise. R4 differs
   from R1 in exactly one variable, which is a clean design — yet any divergence has TWO
   explanations, and they are not distinguishable from the split alone:

     (a) R1-R3 inherited the triage charter's framing of what each idea is about, and R4 did
         not; or
     (b) R4 simply had less evidence and produced a weaker partition.

   For EACH specific divergence, argue which explanation fits, citing the ideas involved. Where
   you cannot tell, say so plainly. Do not rubber-stamp a 3-1 split as bias-validated-by-design:
   that would launder a quality artifact as a finding and make the control worse than useless.

4. THE ORDER MANIPULATION. R1, R2 and R3 received the same corpus in ascending, descending and
   shuffled order. Did they differ in ways that track their ordering, or did order make no
   observable difference? Order-sensitivity in a whole-corpus read is plausible but unverified
   for these agents, and the pack spends real budget on it. If the manipulation had no effect,
   say so — that is a finding worth having, because a future sweep can then drop the variation
   and run cheaper.

Report ranked findings — blocker / major / minor — each naming the reports and ideas involved
and the concrete consequence. An empty findings list must mean you attacked and failed, not
that you skimmed. Change no repository file and dispatch no subagents.
```

---

### S — synthesis protocol

**Not a dispatch.** This is what the integrating agent does in the main session, after GATE 2.

```
You have four analyst reports and audit 1's findings. Produce one partition.

RESOLVING DISAGREEMENT ABOUT INDEPENDENCE. Check the repository and rule. Read the actual
files, the systems in docs/08-governance/systems.yaml, the paths, the dependencies — then
decide.

  - NEVER count analysts. Three of the four read identical evidence, so a majority is not
    independent corroboration.
  - NEVER split the difference.
  - NEVER defer to an analyst on the grounds that it read more.

  A 3-1 split where R4 is the dissenter is the expected shape of finding bias. Read audit 1's
  per-divergence argument before ruling on any such split, and treat "I cannot tell" from the
  audit as a reason to check the repository yourself, not as a tie.

UNANIMITY vs A BARE MAJORITY. Unanimity across all four — including the control, which read
different evidence — is the strongest signal available here, because it cannot be inherited
framing. A bare majority among R1-R3 with R4 dissenting is the weakest, for the same reason.
Weight them accordingly; do not treat them as points on one scale.

THE TWO LEVELS. Where analysts disagree about WHICH LEVEL a boundary belongs to — one making it
a programme split, another a split within a programme — the criterion decides level 1 and
readability decides level 2. A boundary the criterion demands cannot be dissolved to tidy up
level 2; a boundary only readability wants cannot be pushed down into level 1.

THE DECLINE TIERS. Assemble decision 11's three tiers, each carrying the reasons given:

     nominated by all four
     nominated by a majority
     nominated by a single analyst

Filter nothing out. The owner rules on each candidate individually, and sees the confidence
behind each nomination rather than a flattened list.

THE UNBATCHED SECTION. Carry it forward as a named section with a reason per idea. Report its
size as the quality signal it is.

OUTPUT. The batching staging document in docs/00-working/, ungoverned per ADR-010. It carries
both levels, the six-field batch record for every group, the unbatched section, the decline
tiers, and the completeness arithmetic. The batching is NOT additionally recorded as anchor
ideas and links in _data/ideas.jsonl — that was considered and declined, to avoid keeping two
copies consistent.
```

---

### A2 — adversarial audit 2: the merge

Dispatch to `partition-adversary`, model sonnet. Runs after synthesis, before GATE 3.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

Adversarially audit a merge. Four analysts independently partitioned an idea corpus; an
integrator merged their four partitions into one. Your question is narrow and specific:

    Does the integrated partition FOLLOW FROM the four inputs, or did the integrator introduce
    groupings no analyst proposed?

This audit exists because synthesis is where the most judgment is applied and was otherwise the
only step in the design that nothing checked.

Inputs: the four reports (_working/idea-corpus/report-R1.md .. report-R4.md), the merged
staging document in docs/00-working/, and audit 1's findings.

Attack at minimum:

  - Groups in the merge that no analyst proposed, and are not justified by a stated repository
    check. A group the integrator invented is the exact failure this audit is for.
  - Disagreements resolved by counting analysts, splitting the difference, or deferring to an
    analyst because it read more — all three are forbidden by the synthesis protocol. Look for
    them in the reasoning, and for merges whose shape is a majority vote wearing a rationale.
  - A 3-1 split with R4 dissenting that was resolved AS a vote rather than by checking the
    repository.
  - Ideas that changed group between the inputs and the merge with no reason given.
  - Coverage: verify arithmetically that the merge accounts for every idea in the corpus, with
    none unassigned and none in two groups. Verify it yourself; do not trust the document.
  - The decline tiers: does each tier's membership actually match what the four reports
    nominated, and did anything get filtered out on the way?
  - The unbatched section: was it used honestly, or as a place to hide ideas that would have
    embarrassed a group?

Report ranked findings — blocker / major / minor — each with the concrete consequence. An empty
findings list must mean you attacked and failed. Change no repository file and dispatch no
subagents.
```

---

### G — the gate

What must be true before the staging document reaches the owner at GATE 3.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

  1. Every idea in the corpus is accounted for — none unassigned, none in two groups —
     verified arithmetically against manifest.json, not taken from the document's own claim.
  2. The programme count is inside 8-12, or the document states why it is not.
  3. The six-field batch record is present for every group at both levels.
  4. The unbatched section is named, has a reason per idea, and its size is reported.
  5. The three decline tiers are assembled, with reasons, nothing filtered out.
  6. Audit 2 has returned and its blocking findings are addressed or explicitly carried.
  7. uv run python -m src.governance exits 0.
  8. Nothing was written to _data/ideas.jsonl by any agent in this build.
  9. SPEND POSTURE is reported, per GOV-008's cost protocol: how many dispatches ran, how many
     were resumed after truncation, how many fix cycles any item took, whether any model was
     escalated above sonnet (it should not have been), and wall-clock against the runway.
     PROMPT-025's estimate was roughly 130k tokens of input each for R1-R3, 55k for R4, plus
     the two audits. Report what it ACTUALLY cost against those figures, not the estimate.

Record real output. A failing check is a result to record, not a step to retry until quiet.
```

---

## Descope ladder

In `PROMPT-025` decision 16's ratified order. **No rung is taken without the owner's explicit
direction.**

| Rung | Surrender | Cost |
|---|---|---|
| 1 | `R3` — the third finding-reader | Loses the shuffled ordering; the order manipulation drops to ascending vs descending |
| 2 | `R2` — the second finding-reader | Loses the order manipulation entirely; one finding-reader plus the control remain |
| 3 | `A2` — the merge re-audit | Synthesis becomes unchecked except by the owner at GATE 3 |
| 4 | `A1` — the partition audit | The four partitions reach synthesis unchecked |
| 5 | `R4` — the control | Surrendered last; without it, nothing distinguishes corpus signal from inherited framing |

**Flag, carried from `PROMPT-025` and left standing by the owner on 2026-09-12:** the ladder was
ratified *before* decision 7 added `A2`. Rung 3's placement is the drafter's proposal, on the
grounds that `A2` guards a step the owner personally reviews at GATE 3 anyway, whereas `A1`
guards four agent outputs nobody else checks. The owner has seen this and chosen to leave the
order as ratified rather than rule now — the decision stays theirs at the moment a rung would
actually be taken.
