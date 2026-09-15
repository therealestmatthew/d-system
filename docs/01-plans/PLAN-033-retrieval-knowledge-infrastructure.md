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

## The gate is a deadlock, and breaking it is this programme's first job

The partition states that "the whole programme is gated on a recorded retrieval failure that nothing
currently collects — `G25` is what would supply it." The finalize phase's scope asks how `G25`
collects it. The answer has two halves, and the second matters more than the first.

**`phase-mem-15`, `-16`, `-18` and `-19` are all `deferred`, and each one's `next_action` cites "the
recorded retrieval failures".** Nothing records one. So the gate cannot be met by waiting: the
evidence that would release the work can only be produced by using a retrieval system nobody is
permitted to build until the evidence exists. Four phases have sat behind that condition, and the
condition has no threshold — no number, no date, nothing that could ever be satisfied or expire.

### 1. Collection is voluntary and seeded, not instrumented

The obvious mechanism is to instrument `tools/load_context.py`. **Ruled against.** That tool queries
the `memories` table and nothing else — `load_context.py:94` is `FROM memories`. Instrumenting it
measures the one retrieval route that already works and misses grep, which is how retrieval actually
happens in this repository and which leaves no trace when it fails.

So collection is a voluntary record with a defined shape, in the manner of the `log-anti-patterns`
skill that already works for its own subject: an agent that looked for something, did not find it,
and later learned it existed records that. `R01` fixes what the record must contain — what was
sought, where it was looked for, and **whether it existed** — because without the third field a
retrieval failure is indistinguishable from a question with no answer.

**And the collection is seeded from the corpus rather than started empty.** `R02` requires a sweep of
existing session records for failures already described in prose. This repository writes "Found wrong
in the source material" and "Unresolved" sections as a matter of course; the cases are already
written down, just not as data. Starting empty would leave the gate unreachable for however long it
takes to accumulate, which is the state the programme is already in.

### 2. The gate is re-specified with a threshold and an expiry

This is the more important half. `R03` requires the gate to be restated with **a number and a review
date**, and `R04` requires a ruling in both directions: threshold met, or date passed with fewer.

"Wait for recorded retrieval failures" is not a high bar, it is an unmeetable one, and the four
deferred phases are the evidence. A condition that can expire converts them from indefinitely parked
into scheduled for a decision. If the failures do not materialise, that is itself the answer —
retrieval is not the problem it was assumed to be, and the vector line should be re-ruled rather than
waiting longer.

The cost accepted: a threshold picked before the data exists is a guess. It is a better guess than no
threshold, and `R04`'s expiry is what stops a wrong guess from parking the work a second time.

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
