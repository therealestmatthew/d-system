# Partition pack

Every prompt a partition sweep dispatches, one fenced block per dispatch, plus the synthesis
protocol the coordinator follows between dispatches and the gate a partition must pass before it
reaches the owner. The `partition-ideas` skill extracts each block with
`idea_corpus.py prompt <section>`, which fills the `{placeholders}` with absolute paths in the
primary checkout and saves the text as `dispatch-<section>.txt`. The skill sends that text
**verbatim** and writes no brief of its own.

## What this pack is, and what it deliberately does not carry

The work this pack dispatches is an **analysis**, not a code build: two analysts each partition
the idea corpus independently, an adversary audits twice, a coordinator integrates one partition,
and the owner rules. The deliverable is one partition document and its JSON record.

This pack carries **no per-dispatch worktree setup, no port assignments and no browser
verification**. The analysts and the adversary are subagents a coordinator dispatches, not
sessions of their own, and nothing they read is written anywhere but the gitignored staging
directory, so none of them needs an isolated checkout.

This pack carries no corpus size, no ruling from any particular sweep and no record of what a
sweep cost. Those belong to the sweep's own report, never to the pack.

## Placeholders

| Placeholder | Filled with |
|---|---|
| `{corpus_dir}` | the corpus directory in the primary checkout's staging directory |
| `{idea_log}` | the idea log in the primary checkout |
| `{systems_registry}` | the systems registry in the primary checkout's document root |
| `{draft}` | the synthesis draft in the primary checkout's staging directory (`S`, `A2`) |
| `{check_command}` | the plugin's repository check |

`idea_corpus.py prompt` refuses to emit a block with a placeholder it cannot fill.

## Section letters

| Letter | Meaning here |
|---|---|
| `R1` | the analyst that reads findings |
| `R4` | the control: reads no findings |
| `A1` | adversarial audit 1, over the two partitions |
| `S` | the synthesis protocol (not a dispatch) |
| `A2` | adversarial audit 2, over the merge |
| `G` | the gate |

`R2` and `R3` are not used. `A` keeps its adversarial meaning.

## Conventions

- **Idempotency**: every dispatch below opens with *"Assess the current state of the repository
  against the deliverables below; do only what is missing; report what already existed."* A
  dispatch may be re-sent in a later session without harm.
- **Truncation**: if a dispatched agent's output is cut off by its turn limit, resume that same
  agent; never re-run it from scratch.
- **Model policy**: sonnet is the standard model for judgment work, and no larger model is
  assigned in advance. Both analysts and both audits are judgment work: sonnet.
- **Agents**: both analysts go to `partition-analyst`, whose tools are read-only, so its report
  comes back as text and the coordinator writes it. Both audits go to `partition-adversary`, with
  different briefs.
- **No analyst sees the other's output**, and no analyst may dispatch subagents.
- **Nothing this pack dispatches writes to the idea log.** No status event, no annotation, no
  link, by any agent, at any stage, including a decline nomination.

## Owner gates

Three owner gates punctuate a sweep, held by the skill that dispatches this pack: after the
analyst reports land, after audit 1 returns, and after audit 2 has checked the merge, where the
owner accepts or corrects the partition and rules on every decline candidate individually. This
pack does not enforce those stops itself; it supplies what each gate reads.

## The corpus

Built by `idea_corpus.py build` into `{corpus_dir}`, which is gitignored. Its `--status` flag
selects which idea statuses form the corpus, accepting one status or a comma-separated list and
defaulting to `triaged`. This pack dispatches against whatever `--status` selected for that
build.

| File | Contents |
|---|---|
| `corpus-R1.md` | title, body, links, findings |
| `corpus-R4.md` | title, body, links, and **no findings** |
| `manifest.json` | corpus size, the selected status or statuses, the build's seed, excluded ids, the ideas with more than one finding |

`corpus-R4.md` never mentions findings anywhere, in an entry or in the header. The corpus builder
guarantees that, so `R4`'s brief does not restate or enforce it; a control whose file could tell
it is a control would not be one.

**Read the manifest for the actual corpus size and status selection before dispatching
anything.** This pack names no size of its own. The corpus moves whenever the idea log moves, and
a sweep that assumes a number instead of reading the manifest is partitioning a corpus that may
no longer exist.

---

### R1 — the finding-reading analyst

Dispatch to `partition-analyst`, model sonnet.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

You are partitioning a corpus of parked ideas into groups that can each become one plan. You
work alone. Do not dispatch subagents. Do not write to {idea_log} or any other
repository file; your only output is the report named at the end.

Read your corpus at {corpus_dir}/corpus-R1.md. It contains every idea's title, body,
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

Write your report to {corpus_dir}/report-R1.md. Stop when it contains the fine
partition, the programmes, the completeness arithmetic, the unbatched section and the decline
candidates.
```

---

### R4 — the control (no findings)

Dispatch to `partition-analyst`, model sonnet.

**`R4` is the control and must never learn that it is one.** It is not told that findings exist,
that its input differs from anyone's, or that another analyst is running. A control that knows it
is a control is not one. The block below is `R1`'s with every reference to findings removed; send
it exactly as extracted and add nothing.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

You are partitioning a corpus of parked ideas into groups that can each become one plan. You
work alone. Do not dispatch subagents. Do not write to {idea_log} or any other
repository file; your only output is the report named at the end.

Read your corpus at {corpus_dir}/corpus-R4.md. It contains every idea's title, body and
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

Write your report to {corpus_dir}/report-R4.md. Stop when it contains the fine
partition, the programmes, the completeness arithmetic, the unbatched section and the decline
candidates.
```

---

### A1 — adversarial audit 1: the two partitions

Dispatch to `partition-adversary`, model sonnet. Runs after the analyst reports land.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

Adversarially audit two independent partitions of the same idea corpus. Assume each is broken
and find where it fails.

Inputs: {corpus_dir}/report-R1.md and report-R4.md, the corpora they were built from
(corpus-R1.md and corpus-R4.md) and {corpus_dir}/manifest.json.

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
   {systems_registry}, shared file paths, shared dependencies. An independence
   argument you could have tested and did not is not a finding.

3. THE CONVERGENCE CHECK. You have exactly two partitions of the same corpus: one built from a
   corpus that carries findings (R1), one built from a corpus that does not (R4). There is no
   split and no majority to read here — only agreement or disagreement between two reports.

   AGREEMENT is not automatically bias-free. Two agents can agree for the same wrong reason, so
   do not rubber-stamp a matching grouping as validated by the control. Check whether the
   agreement holds for a reason you can find in the corpus material itself — not merely because
   both analysts produced the same shape, which two agents can do by inheriting the same
   surface reading of the ideas' titles.

   DISAGREEMENT has two possible explanations, and a single comparison cannot separate them on
   its own:

     (a) R1 inherited the triage findings' framing of what each idea is about, and R4 did not;
         or
     (b) R4 simply had less evidence to work with and produced a weaker partition.

   For EACH specific divergence between the two reports, argue which explanation fits, citing
   the ideas involved and what in the corpus or the finding text supports your reading. Where
   you genuinely cannot tell, say "I cannot tell" plainly — that is an accepted answer here, and
   it sends the question to the repository for someone to check further, not to a vote between
   the two reports. Do not force a call you cannot support.

4. Report ranked findings — blocker / major / minor — each naming the reports and ideas involved
   and the concrete consequence. An empty findings list must mean you attacked and failed, not
   that you skimmed. Change no repository file and dispatch no subagents.
```

---

### S — synthesis protocol

**Not a dispatch.** This is what the integrating agent does in the coordinator's own session,
after audit 1 has returned and the owner has cleared that gate.

```
You have two analyst reports and audit 1's findings. Produce one partition.

RESOLVING DISAGREEMENT ABOUT INDEPENDENCE. Check the repository and rule. Read the actual
files, the systems in {systems_registry}, the paths, the dependencies — then
decide.

  - NEVER count analysts. Two analysts agreeing is not corroboration if they agreed for a shared
    reason neither actually checked, and two analysts disagreeing is not resolved by picking the
    one you happen to trust more.
  - NEVER split the difference.
  - NEVER defer to an analyst on the grounds that it read more.

  Read audit 1's per-divergence argument before ruling on any disagreement between R1 and R4,
  and treat "I cannot tell" from the audit as a reason to check the repository yourself, not as
  a tie to break by guessing.

AGREEMENT vs DISAGREEMENT. Agreement between R1 and R4 is the strongest signal available here,
because R4 read no findings and cannot have inherited their framing — but only once audit 1 has
confirmed the agreement holds for a reason found in the corpus material, not merely that both
analysts produced the same shape. A disagreement is not resolved by preferring R1 because it saw
more evidence; it is resolved the way audit 1 argued it, or by checking the repository yourself
where audit 1 could not tell.

THE TWO LEVELS. Where the two analysts disagree about WHICH LEVEL a boundary belongs to — one
making it a programme split, the other a split within a programme — the criterion decides level
1 and readability decides level 2. A boundary the criterion demands cannot be dissolved to tidy
up level 2; a boundary only readability wants cannot be pushed down into level 1.

THE DECLINE TIERS. With two analysts, assemble two tiers, each carrying the reasons given:

     nominated by both
     nominated by one

Filter nothing out. The owner rules on each candidate individually, and sees the confidence
behind each nomination rather than a flattened list.

THE UNBATCHED SECTION. Carry it forward as a named section with a reason per idea. Report its
size as the quality signal it is.

OUTPUT. The partition document at {draft}, with its JSON record beside it. It carries
both levels, the six-field batch record for every group, the unbatched section, the decline
tiers, and the completeness arithmetic. The partition is NOT additionally recorded as anchor
ideas and links in {idea_log} — that would duplicate state that would then need to be kept
consistent by hand.
```

---

### A2 — adversarial audit 2: the merge

Dispatch to `partition-adversary`, model sonnet. Runs after synthesis, before the gate.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

Adversarially audit a merge. Two analysts independently partitioned an idea corpus; an
integrator merged their two partitions into one. Your question is narrow and specific:

    Does the integrated partition FOLLOW FROM the two inputs, or did the integrator introduce
    groupings neither analyst proposed?

This audit exists because synthesis is where the most judgment is applied, and without it
nothing checks that step.

Inputs: the two reports ({corpus_dir}/report-R1.md and report-R4.md), the merged
partition document at {draft}, and audit 1's findings
({corpus_dir}/audit-1-findings.md).

Attack at minimum:

  - Groups in the merge that neither analyst proposed, and are not justified by a stated
    repository check. A group the integrator invented is the exact failure this audit is for.
  - Disagreements resolved by counting analysts, splitting the difference, or deferring to an
    analyst because it read more — all three are forbidden by the synthesis protocol. Look for
    them in the reasoning, and for merges whose shape is a preference wearing a rationale.
  - A disagreement between R1 and R4 resolved by picking a side rather than by checking the
    repository or following audit 1's per-divergence argument.
  - Ideas that changed group between the inputs and the merge with no reason given.
  - Coverage: verify arithmetically that the merge accounts for every idea in the corpus, with
    none unassigned and none in two groups. Verify it yourself; do not trust the document.
  - The decline tiers: does each tier's membership actually match what the two reports
    nominated, and did anything get filtered out on the way?
  - The unbatched section: was it used honestly, or as a place to hide ideas that would have
    embarrassed a group?

Report ranked findings — blocker / major / minor — each with the concrete consequence. An empty
findings list must mean you attacked and failed. Change no repository file and dispatch no
subagents.
```

---

### G — the gate

What must be true before the partition document reaches the owner at the final gate.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

  1. Every idea in the corpus is accounted for — none unassigned, none in two groups —
     verified arithmetically against {corpus_dir}/manifest.json, not taken from the
     document's own claim.
  2. The programme count is inside 8-12, or the document states why it is not.
  3. The six-field batch record is present for every group at both levels.
  4. The unbatched section is named, has a reason per idea, and its size is reported.
  5. The two decline tiers are assembled, with reasons, nothing filtered out.
  6. Audit 2 has returned and its blocking findings are addressed or explicitly carried.
  7. {check_command} exits 0.
  8. Nothing was written to {idea_log} by any agent in this sweep.
  9. SPEND POSTURE is reported: how many dispatches ran, how many were resumed after
     truncation, whether any model was escalated above sonnet (it should not have been), and
     wall-clock against the estimate the skill stated before dispatching. Report what the
     sweep actually cost against that estimate; this pack names no estimate of its own, since
     that figure belongs to the run rather than to the pack.

Record real output. A failing check is a result to record, not a step to retry until quiet.
```

---

## Descope ladder

Ordered for the four-dispatch sweep this pack runs. **No rung is taken without the owner's
explicit direction.**

| Rung | Surrender | Cost |
|---|---|---|
| 1 | `A2`, the merge re-audit | Synthesis becomes unchecked except by the owner at the final gate |
| 2 | `A1`, the partition audit | The two partitions reach synthesis unchecked |
| 3 | `R4`, the control | Surrendered last; without it, nothing distinguishes corpus signal from inherited framing |

`A2` is surrendered before `A1` because it guards a step the owner reviews personally at the
final gate anyway, whereas `A1` guards two independent partitions that nobody else checks before
synthesis runs. `R1` carries no rung: it is the sole source of the actual partition, and
surrendering it leaves nothing for synthesis to work from.
