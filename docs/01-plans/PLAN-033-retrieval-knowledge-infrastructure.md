---
schema_version: 1
id: doc-retrieval-knowledge-infrastructure
code: PLAN-033
title: Retrieval and knowledge infrastructure (P6)
kind: plan
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-15'
systems: [sys-retrieval, sys-brain, sys-governance]
depends_on: [doc-retrieval-knowledge-infrastructure-requirements, doc-adr-file-based-governance]
---

# Retrieval and knowledge infrastructure (P6)

## Summary

Programme `P6` of the twelve. Nine ideas across five fine groups: how the system finds and judges its
own accumulated knowledge. Distinct from `P1`, which is the idea graph's shape rather than search
over it.

| Group | Ideas | What it covers |
|---|---|---|
| `G25` Ordering and deterministic search | `000002`, `000040` | The stated search order, and the deterministic layer beneath it |
| `G26` Vector retrieval | `000004` | Vector/RAG tooling and the `phase-mem-*` line it gates |
| `G27` Code-graph retrieval | `000005` | A code-graph tool evaluated against this repository's code |
| `G28` Documentation companion set | `000043`, `000044`, `000045` | Structured front matter, graph and vector for the documentation corpus — three surveys, one decision |
| `G29` Memory lifecycle and provenance | `000060`, `000032` | Whether what is found can be trusted |

Partition-time sizing was 9–13 phases across the groups, "mostly design, not code". This plan lands
**ten**.

## The gate, and what the partition got wrong about it

The partition states that "the whole programme is gated on a recorded retrieval failure that nothing
currently collects — `G25` is what would supply it", and the finalize phase's scope repeats it. **That
premise is wrong, and checking it changed this plan.**

The gate is real, but it is not in `next_action` and it does not lack a collector. It lives in
`resume_when`, and it names one:

```
$ python3 -c "...resume_when.startswith('phase-mem-10 records')"
phases gated on phase-mem-10: ['phase-mem-15', 'phase-mem-16', 'phase-mem-17', 'phase-mem-18']
phase-mem-10 status: ['queued']
```

Four phases — not the three usually cited, and including `phase-mem-17`, which the partition does not
mention — carry `resume_when: phase-mem-10 records concrete unmet retrieval needs; review that
evidence before releasing this phase.` (`phase-mem-19` is gated differently, on `phase-mem-18`.)

**`phase-mem-10` is `status: queued`.** Not deferred, not blocked, dependent on nothing. It has simply
never been claimed. Its scope is to "create a small public/synthetic query-to-relevant-memory
evaluation set and a repeatable evaluation command" and "record misses, relevance/coverage and latency
before considering embeddings". Its deliverables — `tools/evaluate_retrieval.py`,
`test/fixtures/retrieval_cases.json` — do not exist on disk.

And its acceptance already carries the both-outcomes ruling that a gate needs: *"The report identifies
concrete unmet retrieval needs **or explicitly records that current retrieval is sufficient**."*

So the accurate statement is not that nothing collects the evidence. It is that **the collector is
ready, unclaimed, and four phases have waited behind it.** The cheapest unblocking move in this
programme is not to design anything; it is to claim `phase-mem-10`.

### 1. `phase-ret-01` complements `phase-mem-10` rather than replacing it

Having found the collector, the question becomes whether a second one is justified. **It is, and the
distinction is the corpus.**

`phase-mem-10` builds a *synthetic* evaluation set — deliberately so, since its own acceptance
requires it to run "without transmitting memories or requiring an embedding provider". That measures
retrieval against queries someone wrote in advance.

`phase-ret-01` records *actual* failures: an agent looked for something during real work, did not find
it, and later learned it existed. `REQ-018` `R14` is why both are needed — a retrieval system
evaluated only on queries its designer wrote is evaluated on the wrong corpus.

`phase-ret-01` therefore declares `depends_on: [phase-mem-10]` and states the complement explicitly,
so nobody builds a parallel evaluation harness.

The mechanism ruling stands: collection is a voluntary record, not instrumentation of
`tools/load_context.py`, which queries the `memories` table and nothing else (`load_context.py:94` is
`FROM memories`) and so would measure the one route that already works while missing grep. `R01`
requires the record to say **whether the thing existed**, because without that a retrieval failure is
indistinguishable from a question with no answer. `R02` seeds it from session records, which already
describe such cases in prose.

### 2. The gate is corrected before it is re-specified

`phase-ret-02`'s first job is no longer to invent a threshold. It is to **fix the record**: the gate
names `phase-mem-10`, that phase is claimable today, and `phase-mem-17` is gated the same way but is
absent from the partition's account.

Only then does the re-specification earn its place, and it is narrower than first drafted. What
`phase-mem-10`'s acceptance does not carry is a **review date** — a point at which, if nobody has
claimed it, the four waiting phases are re-ruled rather than waiting indefinitely. That is the gap
worth closing, and it is a smaller gap than "the gate has no collector".

The cost accepted: adding a date to another plan's phases is an edit across a plan boundary, which is
why `R03` keeps the ADR requirement.

## The chosen design

### 3. `G28` is kept whole, and the reason is recorded rather than restated

The phase's acceptance requires this, and requires audit 2's reason for restoring it.

**Audit 2's finding, as recorded in the partition:** *"The `043`/`044`/`045` companion set was split
with no entry in the disagreement table — a silent reassignment against the ideas' own
self-description."* The fix applied was *"Reunited as `G28`; `G26` is `000004` alone."*

The checkable fact is `000045`'s own body, which opens by naming the other two as "companion ideas
recorded alongside this one", deliberately split so one design decision — structured front matter,
graph, or vector for the documentation corpus — can be made from all three surveys together.
Synthesis had pulled `000045` in with `000004` on vector-mechanism grounds and had not recorded the
change; audit 2 caught it.

Audit 2's own summary of the pattern is why this matters beyond one group: it found no vote-counting,
but "unlisted or overstated convergence claims used to close off boundaries that were genuinely
contested — which is arguably worse, since it's harder for a reader to spot than an admitted vote
would be."

So `R10` makes wholeness a requirement rather than a note: one decision, citing all three surveys. The
three surveys are three phases, because three surveys in one session is not one session's work — but
`phase-ret-07` may not be claimed on one survey.

### 4. `ADR-001` is revisited before any documentation database is designed

`000043` proposes a queryable projection of document front matter. `ADR-001` explicitly decided
against exactly that: governance metadata "needs no DuckDB table, DDL migration, or API Pydantic
model. This is the explicit exception to the otherwise applicable entity schema → DDL → model
workflow."

`R08` requires the revisit to engage that stated reason rather than route around it, and permits
reaffirming it as a complete outcome. `phase-ret-05` is sized ahead of the surveys because a survey
of documentation-database tooling conducted while the governing decision still forbids the projection
is a survey of something that cannot be built.

### 5. `G26` gets no new phase

`000004` is vector retrieval, and the partition marks it "gated externally". What it describes is
already in the backlog: `phase-mem-15`, `-16`, `-18` and `-19`, which `000004`'s own body enumerates
by id. Creating parallel phases would duplicate a line that exists.

`phase-ret-02` therefore acts on `G26` by re-ruling the gate on those four phases rather than by
building beside them. This is why the programme lands at ten against a 9–13 range with one group at
zero, and it is a deliberate ruling rather than an omission.

### 6. `000040` is deterministic by definition, and `R07` enforces it

`000040` states in its own text that it is not semantic or vector search. That boundary is easy to
erode — a deterministic search design that reaches for embeddings when exact matching gets hard has
become `G26`'s work under `G25`'s name. `R07` makes the absence of any vector mechanism checkable.

### Which of these need a decision record

**Two.**

- **The gate re-specification needs one.** It changes the release condition on four phases that
  belong to another plan (`doc-agent-memory`), and a future reader finding those phases moving
  needs to know the gate was deliberately restated rather than quietly dropped. `phase-ret-02` writes
  it.
- **The `G28` decision needs one**, whatever it concludes. Choosing structured, graph or vector for
  the documentation corpus is a standing architectural commitment, and it either supersedes `ADR-001`
  or is constrained by it. `phase-ret-07` writes it.

`phase-ret-05`'s revisit may also produce a supersession of `ADR-001`, which is recorded in that
phase rather than counted separately here — reaffirming needs no new record, and superseding is an
edit to the existing one.

## Implementation phases

Ten phases under `phase-ret-*`, registered in [the backlog index](../09-backlog/README.md).

| Phase | Title | Group | Depends on |
|---|---|---|---|
| `phase-ret-01` | Build retrieval-failure collection and seed it from the session corpus | `G25` | — |
| `phase-ret-02` | Re-specify the gate with a threshold and expiry, and re-rule the deferred phases | `G25`, `G26` | `01` |
| `phase-ret-03` | State the prioritised search order and its conflict rule | `G25` | — |
| `phase-ret-04` | Design deterministic search across the surfaces | `G25` | `03` |
| `phase-ret-05` | Revisit `ADR-001` on a queryable document projection | `G28` | — |
| `phase-ret-06` | Survey structured, graph and vector retrieval for the documentation corpus | `G28` | `05` |
| `phase-ret-07` | Decide the documentation-retrieval mechanism from all three surveys | `G28` | `06` |
| `phase-ret-08` | Evaluate a code-graph tool against this repository's code | `G27` | — |
| `phase-ret-09` | Detect memory staleness and contradiction, and track confidence | `G29` | — |
| `phase-ret-10` | Record provenance behind every memory, report and recommendation | `G29` | `09` |

### Sizing against the partition

Group-level ranges were `G25` 3–4, `G26` 1–2, `G27` 1, `G28` 2–3, `G29` 2–3 — 9–13 in total. This plan
lands **ten**: `G25` at 4, `G26` at **0**, `G27` at 1, `G28` at 3, `G29` at 2.

`G26`'s zero is decision 5 and the only departure from a range. Every other group lands inside its
own.

## Execution order and real concurrency

`phase-ret-01` is the phase that unblocks the most: it feeds `phase-ret-02`, which releases four
deferred phases in another plan, and it produces the corpus `R14` measures the eventual mechanism
against. **It should be claimed first even though it is neither the largest nor the most interesting
phase here.**

Four phases declare `depends_on: []` — `-01`, `-03`, `-05` and `-08` — and `-08` collides with
nothing in this programme, so it is the one that can always run beside a peer. `-09` also starts free.

The critical path is three deep: `05` → `06` → `07`.

**This programme should run after `P1`.** `phase-ret-03`'s search order must rank the ideas log among
its sources, and `P1` is what gives that log classification and structure to rank by. Ordering an
unstructured corpus is possible but produces an order that changes as soon as `P1` lands.

## Requirement coverage

Every row of `REQ-018` maps to at least one phase, and every phase carries at least one row.

| Requirement | Phases |
|---|---|
| R01 A retrieval failure can be recorded, with existence stated | `phase-ret-01` |
| R02 The collection is seeded from existing session records | `phase-ret-01` |
| R03 The gate restated with a threshold and a review date | `phase-ret-02` |
| R04 The deferred phases re-ruled in either outcome | `phase-ret-02` |
| R05 A prioritised search order naming each source's authority | `phase-ret-03` |
| R06 A conflict rule for disagreeing sources | `phase-ret-03` |
| R07 Deterministic search, with no vector mechanism | `phase-ret-04` |
| R08 `ADR-001` revisited on its own terms | `phase-ret-05` |
| R09 Three surveys, each with cost and coverage | `phase-ret-06` |
| R10 One decision, citing all three | `phase-ret-07` |
| R11 A code-graph tool evaluated on real code | `phase-ret-08` |
| R12 Staleness, contradiction and confidence | `phase-ret-09` |
| R13 Provenance behind every artifact | `phase-ret-10` |
| R14 Retrieval measured against the recorded failures | `phase-ret-07`, `phase-ret-01` |

## Key references

- **The requirement** — [REQ-018](../06-requirements/REQ-018-retrieval-knowledge-infrastructure.md).
- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P6`, its disagreement table entry on `000043`/`000044`/`000045`, and *What audit 2 changed*.
- **`ADR-001`** ([file-based governance](../04-decisions/ADR-001-file-based-governance.md)) — the decision `000043` reverses, and the one `phase-ret-05` revisits on its own terms.
- **The memory plan** ([PLAN-001](PLAN-001-agent-memory-system.md)) — owner of `phase-mem-15`, `-16`, `-18` and `-19`, the four phases `phase-ret-02` re-rules.
- **Agent engineering and delegation** ([PLAN-031](PLAN-031-agent-engineering-delegation.md)) — `000081`'s context-selection framework consumes this programme's query contract without sharing its deliverable.

## Known facts not to rediscover

- **The gate is unmeetable as written.** Four phases are deferred behind "the recorded retrieval
  failures" and nothing collects them. That is a deadlock, not a high bar.
- **`tools/load_context.py` reads only the `memories` table** (`FROM memories`, line 94). It is not a
  proxy for retrieval in this repository, and instrumenting it would measure the wrong path.
- **`G28` is whole on the ideas' own self-description**, not on a synthesis judgement. `000045`'s body
  names the other two as companion ideas. Audit 2 caught a silent split; do not re-split it.
- **`ADR-001` explicitly forbids what `000043` proposes.** Revisit the decision before designing
  around it; reaffirming is a complete outcome.
- **`000004` duplicates the existing `phase-mem-*` line** and names those phases by id in its own
  body. It gets no new phase.
- **`000040` is deterministic by definition.** If a design under `G25` reaches for embeddings, it has
  become `G26`'s work wearing `G25`'s name.
- **`000005`'s named tool may be gone.** The owner's ruling of 2026-09-13 kept the idea and rescoped
  it: "Tool dead (KuzuDB archived), question alive. Any evaluation starts from a successor."
  `phase-ret-08` evaluates *a* code-graph tool, not that one.
