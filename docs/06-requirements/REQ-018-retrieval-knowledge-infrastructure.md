---
schema_version: 1
id: doc-retrieval-knowledge-infrastructure-requirements
code: REQ-018
title: Retrieval and knowledge infrastructure requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-retrieval, sys-brain, sys-governance]
depends_on: [doc-adr-file-based-governance, doc-agent-memory]
---

# Retrieval and knowledge infrastructure requirements

## Observed problem and scope

This repository has accumulated a large body of knowledge and no stated way to search it. An agent
answering "how does X work here?" greps, reads a README navigation table, and guesses — and the
sources disagree with each other in predictable ways, because code is true about what exists, plans
describe intent that may never have been built, and the ideas log is explicitly speculation.

Five gaps, and one of them is blocking the other four.

1. **The programme is gated on evidence nothing collects.** `phase-mem-15`, `-16`, `-18` and `-19`
   are all `deferred`, and each waits on "the recorded retrieval failures". Nothing in this
   repository records a retrieval failure. The gate is therefore unreachable by waiting: the evidence
   that would unblock the work can only come from a system nobody is allowed to build until the
   evidence exists. Four phases have sat deferred behind a condition with no collection mechanism and
   no threshold.

2. **There is no stated search order.** `000002` names the candidate sources — developed code, plan
   documentation, ADRs, session records, the ideas list, `brain/` memories — and observes that what is
   missing is an *order*, not a set. `000040` is the deterministic layer beneath it, explicitly not
   the vector work.

3. **Document front matter is validated but not queryable.** Every governed document carries
   `schema_version`, `id`, `code`, `kind`, `status`, `owner`, `created`, `updated`, `systems` and
   `depends_on`, and `src/governance` uses all of it for uniqueness, status and dependency checks.
   None of it is queryable the way `_data/` is through DuckDB. The documents already form a real
   graph — `depends_on` edges, `promoted_to` links, `systems` membership — that nothing can query as
   one (`000043`, `000044`).

4. **The one retrieval path that is instrumented covers almost nothing.** `tools/load_context.py`
   queries the `memories` table and nothing else. Grep is how retrieval actually happens, and grep
   leaves no record of having failed.

5. **Nothing tracks whether what is found can be trusted.** No staleness detection, no contradiction
   handling, no confidence tracking over memory content, and no record of the sources behind a
   memory, report or recommendation (`000060`, `000032`).

This requirement covers the retrieval and knowledge infrastructure programme (`P6`) — how the system
finds and judges its own accumulated knowledge. It does **not** cover the shape of the idea graph,
which is `P1`; the boundary is that `P1` structures the corpus and `P6` searches it. `000081`'s
context-selection framework sits in `P4` and would consume this programme's query contract without
sharing its deliverable.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | A retrieval failure can be recorded when it happens, through a defined mechanism, and the record states what was sought, where it was looked for, and whether it existed. | Record one and read it back for all three. A record that does not say whether the thing existed cannot distinguish a retrieval failure from an absent answer, which is the distinction the whole gate rests on. |
| R02 | Existing session records are swept for retrieval failures already described in prose, and the recovered cases seed the collection. | Run the sweep and report a count. A collection starting empty measures only the future and leaves the gate unreachable for as long as it takes to accumulate; the corpus already contains cases. |
| R03 | The gate on `phase-mem-15`, `-16`, `-18` and `-19` is restated with a threshold and a review date, replacing "the recorded retrieval failures". | Read the restated gate for a number and a date. Confirm the four phases' `next_action` fields cite it. A gate with no threshold cannot be met, which is why those four have been deferred rather than progressing. |
| R04 | When the threshold is met, or the review date passes with fewer, the four deferred phases are re-ruled rather than left deferred. | Confirm the restated gate names what happens in both cases. "Wait longer" is not a ruling. |
| R05 | A prioritised search order exists, naming each source and what it is authoritative for. | Read the order for one entry per source. Confirm each says what that source is true about — code for what exists, ADRs for why a choice was made, the ideas log for what is explicitly not yet decided — rather than only ranking them. |
| R06 | The search order states what to do when two sources disagree. | Read for a conflict rule. `000002`'s point is that the sources "disagree with each other in predictable ways"; an order that ranks without resolving has not used that observation. |
| R07 | Deterministic search across ideas, backlog, memories, decisions and session records is designed, and the design is explicitly not semantic search. | Read the design for its method. Confirm no vector or embedding mechanism appears — `000040` is the deterministic layer by definition, and `000004` is the vector work. |
| R08 | `ADR-001`'s decision that governance metadata needs no DuckDB projection is revisited, and either reaffirmed or superseded, before any documentation database is designed. | Read the revisit. Confirm it engages `ADR-001`'s stated reason — that governance metadata is development tooling, not a business entity — rather than overriding it silently. If superseded, `ADR-001` is marked so in the same change. |
| R09 | Three surveys exist for the documentation corpus — structured front matter, graph, and vector — each stating what it would cost and what it would answer. | Read all three. Confirm each names a candidate tool or mechanism and what questions it would and would not answer for this corpus. |
| R10 | One decision is made for the documentation corpus, from all three surveys together. | Read the decision for references to all three surveys. A decision citing one survey has not used the companion set, which `000045`'s own body says was deliberately split so one decision could be made from all three. |
| R11 | A code-graph retrieval tool is evaluated against this repository's actual code, not against its documentation. | Run it over this repository and record what it answered. Confirm the evaluation is about code structure — functions, classes, imports — which is the corpus that distinguishes it from `R09`'s. |
| R12 | Memory staleness and contradiction are detectable, and confidence in a memory is tracked over time. | Introduce a memory contradicting an existing one and confirm the contradiction is surfaced. Confirm a confidence value exists and changes on evidence rather than being set once. |
| R13 | Every memory, generated report, recommendation and context pack records its sources: the source file or event and its anchor, the query or prompt that produced it, the model and tool versions, and any human decision made about it. | Read one of each for all four. `000032` unifies what two agents proposed separately as a provenance manifest and a claim registry; a record missing the human decision cannot distinguish an agent's inference from a ruling. |
| R14 | Retrieval over the documentation corpus is measured against the recorded failures from `R01`, not against constructed queries. | Run the chosen mechanism against the collected failure cases and report how many it now answers. A retrieval system evaluated on queries its designer wrote is evaluated on the wrong corpus. |

## What each requirement is not

**R01 is not a new tool for its own sake.** The cheapest mechanism that produces an honest record is
the right one. What it must not be is automatic instrumentation of `tools/load_context.py` alone —
that path queries the `memories` table and nothing else, so instrumenting it measures the one route
already working and misses grep, which is how retrieval actually happens.

**R03 is the phase's central act.** The existing gate is not a high bar, it is an unmeetable one. A
threshold and a review date convert it into a condition that can be satisfied or can expire, which is
what lets the four deferred phases move in either direction.

**R08 is not a licence to reverse `ADR-001`.** Reaffirming it is a complete outcome. `000043`
proposes something that decision explicitly ruled out, so the decision gets revisited on its own
terms first rather than worked around.

**R10 is the constraint that keeps `G28` whole.** Audit 2 caught synthesis silently splitting `000045`
out of this set on vector-mechanism grounds, against the ideas' own self-description. The three
surveys may be separate work; the decision may not be three decisions.

**R14 closes the loop that `R01` opens.** Without it the collected failures are a log nobody reads,
and the programme would have built a retrieval system measured against nothing.
