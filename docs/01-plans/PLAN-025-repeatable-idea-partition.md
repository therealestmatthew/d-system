---
schema_version: 1
id: doc-repeatable-idea-partition
code: PLAN-025
title: Repeatable idea partition — a reusable pack, a status flag and one workflow
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-portfolio, sys-backlog, sys-governance]
depends_on: [doc-repeatable-idea-partition-requirements, doc-idea-record-system, doc-idea-staging, doc-prompt-pack-protocol, doc-ops-build-idea-corpus]
---

# Repeatable idea partition — a reusable pack, a status flag and one workflow

## Context and scope

[REQ-009](../06-requirements/REQ-009-repeatable-idea-partition.md) defines the observable contract.
The first sweep ran on 2026-09-12 and 2026-09-13 and its partition is accepted; what is missing is
the ability to run it again without reconstructing it. This plan extracts the reusable parts of the
first run, makes the corpus selection an argument, and puts a single workflow in front of both.

Three of the four inputs already exist and are reusable as they stand:

| Exists and is reusable | Needs building |
|---|---|
| `.claude/agents/partition-adversary.md` — chartered for any partition, not only ideas | The reusable prompt pack. Today the briefs live inside `PROMPT-032`, mixed with one build's pinned state |
| `tools/build_idea_corpus.py` with `--seed`, `--out`, `--exclusions`, `--stats`, and its operations document `OPS-015` | `--status`. The filter is `CORPUS_STATUS`, a module constant |
| The four analyst prompts and both audit briefs, as text inside `PROMPT-032` | The workflow. No skill and no command exists, so a repeat is hand-dispatched |

**A repeat costs four dispatches, not six.** The first run spent budget on a corpus-ordering
variation — the same ideas presented ascending, descending and shuffled — and audit 1 found it
changed presentation but not the answer. That result is recorded as `000205`. The ordering
variation is therefore dropped, and the sweep keeps only the findings ablation: one analyst that
reads findings, one control that does not. The control is the manipulation that earned its cost,
because nearly every triaged idea carries a finding written by one agent charter, and a grouping the
control reproduces without findings cannot be inherited framing.

## Chosen design

### The briefs become one governed prompt document

Create `PROMPT-034`, the reusable partition pack, carrying six blocks and nothing about any single
run: the analyst brief, the control brief, the two audit briefs, the synthesis protocol, and the
gate. The code is reserved in `codes.yaml` with this plan, so no peer takes it before the phase
that writes it.

What moves, what is dropped, and what is deliberately left behind:

- **Moved unchanged in substance:** the partition criterion as the owner wrote it, the two-level
  structure, the six-field batch record, the completeness arithmetic, the unbatched section, the
  decline tiers, and the three synthesis prohibitions — never count analysts, never split the
  difference, never defer to an analyst because it read more.
- **Rewritten for a four-dispatch sweep:** the section letters (`R1`, `R4`, `A1`, `A2`, plus `S`
  and `G`), audit 1's convergence check, which was written for a 3-1 split and now governs a 1-1
  comparison, and the descope ladder, whose first two rungs surrendered the analysts the sweep no
  longer runs.
- **Left in `PROMPT-032`:** the pinned corpus size of 129, the per-build owner rulings of
  2026-09-12, the kick-off deltas, and the record of what that run actually cost. `PROMPT-032`
  stays `active` as the record of the first sweep and is not rewritten into a template.

Audit 1's convergence brief needs the most care. With one finding-reader and one control, a
disagreement has the same two explanations it had before — inherited framing, or simply less
evidence — and with two analysts there is no majority to hide behind, so the brief must require a
per-divergence argument and must accept "I cannot tell" as an answer that sends the question to the
repository rather than to a vote.

This satisfies R01, R02, R07 and R08.

### `--status` replaces the module constant

Add `--status` to `tools/build_idea_corpus.py`, accepting one status or a comma-separated list,
defaulting to `triaged`. `CORPUS_STATUS` stops being the filter. The manifest records the selected
statuses so a partition document can be traced to the slice it was built from, and `OPS-015` gains
the flag in its narrative and in its regenerated tool-reference block.

An unknown status is rejected rather than silently producing an empty corpus: the tool already
exits 1 when no ideas are selected, and a typo should say it was a typo. The valid set comes from
the idea record system rather than from a second hard-coded list in this tool.

The default must be provably identical to today's behavior, which is why R03 verifies it by
comparing `--stats` output byte for byte across the change rather than by reading the code.

This satisfies R03 and R04.

### The open set is reported and gated, not silently excluded

`triaged` stays the default corpus, so an idea captured after the sweep begins is outside it by the
same status filter that has always applied. What changes is that the exclusion becomes visible: the
workflow's first step counts `open` ideas through `fold()`, prints every id, and stops for the
owner when the count is not zero. The owner then runs the triage sweep first or partitions without
them — a ruling, not a default.

This is the concrete answer to the failure the first run recorded: the open set emptied, and
refilled to 14 ideas twenty minutes later when a peer integrated. A sweep that does not look cannot
report it.

This satisfies R05.

### `/partition-ideas` is a thin runner

A skill under `.claude/skills/partition-ideas/`, whose body is procedure and whose every dispatch
is a pack section sent verbatim. In order: preflight and worktree; the open-set gate; build the
corpus and read the manifest for the real size; dispatch `R1` and `R4` concurrently; **GATE 1**;
dispatch `A1`; **GATE 2**; run synthesis in the main session; dispatch `A2`; run the gate checklist;
**GATE 3**, where the owner accepts or corrects the partition and rules on every decline candidate
individually.

Two harness constraints shape it rather than being worked around:

- Subagents cannot write report files, so each analyst and audit returns text and **the coordinator
  writes it** to `_working/idea-corpus/report-R1.md` and its siblings.
- Subagents inherit the primary checkout as their working directory regardless of the coordinator's
  worktree, so the corpus and the reports live in the primary checkout's gitignored
  `_working/idea-corpus/`. That directory never travels to a worktree and `git worktree remove`
  would destroy it, so the skill states that anything from it that must survive is copied out by
  hand.

Resumability is by inspection, not state: each step checks for its own output before dispatching,
which is the same idempotency convention every dispatch in the first run opened with. A truncated
agent is resumed, never re-run, per `000077`.

The output is a new dated document, `docs/00-working/idea-partition-<YYYY-MM-DD>.md`, recording its
corpus size, its status filter and its manifest seed. The accepted 2026-09-13 partition keeps its
filename and is never edited by a later sweep, so two snapshots can be diffed to see what moved.

This satisfies R06, R10, R11, R12, R13 and R14.

## Sequence and dependencies

1. **`phase-part-01`** writes `PROMPT-034`. Documentation only, and it is first because both later
   phases quote it — the skill dispatches its sections and the flag's operations text refers to the
   corpus it feeds.
2. **`phase-part-02`** adds `--status`, updates `OPS-015`, and adds the tests. Code only, and
   independent of the pack's wording, so it could run concurrently with `phase-part-01` if two
   agents were available; it is sequenced second only because `max_active` makes concurrency
   unlikely for one owner.
3. **`phase-part-03`** writes the skill. It depends on both: it dispatches `phase-part-01`'s
   sections and it calls `phase-part-02`'s flag.

No phase runs a full sweep. Verifying the skill end to end means spending a real sweep's budget,
which is the next sweep's work, not this plan's. `phase-part-03` verifies by dry run: the open-set
gate, the corpus build, and one analyst dispatch against the live corpus, stopping before GATE 1.

## Alternatives considered

**Rewrite `PROMPT-032` into the reusable template.** Rejected. It is the record of what the first
sweep actually sent and cost, including the descope ladder's ratification history and the owner's
rulings at three gates. Editing it to serve a second purpose destroys that record, and a template
carrying one run's pinned numbers is the problem this plan exists to fix.

**Put the briefs in the skill body.** Rejected at the owner's ruling of 2026-09-14. It would be one
file instead of two, but the briefs would be Claude-only, ungoverned, and uncitable from a plan or a
session record — and the synthesis protocol would again live inside a document about one host's
workflow rather than about the method.

**Promote the partition to a governed document.** Rejected at the same ruling. A partition is a
snapshot of a set that decays by design, which is a poor fit for the governed lifecycle; `ADR-010`
already puts exactly this kind of artifact in `docs/00-working/`.

**Make the workflow triage open ideas automatically before building the corpus.** Rejected at the
same ruling. It would keep the log fully triaged, but it folds an owner-visible step into a
subroutine and turns one sweep into two jobs of very different cost.

**Generalize the corpus builder to partition any set.** Rejected as scope. The adversary charter is
already general and needs no change; the builder reads the idea log through `fold()` and has no
second caller. A general corpus step should be built when a second set actually needs partitioning.

**Keep all six dispatches.** Rejected on the evidence. Audit 1 found the ordering variation changed
presentation and not the answer (`000205`); paying for it again would be spending on a manipulation
already measured as null.

## Acceptance and verification

- Every `REQ-009` row maps to at least one phase and is verified with recorded output.
- `PROMPT-034` exists, carries all six blocks, and names no pinned corpus size or per-build ruling.
- `build_idea_corpus.py --stats` with no status argument is byte-identical across the change.
- The manifest records the selected statuses; `OPS-015`'s generated tool-reference block lists
  `--status` after regeneration.
- `/partition-ideas` is discoverable as a skill, reports the open set and stops when it is
  non-empty, and dispatches only verbatim pack sections.
- A dry run reaches GATE 1 with a real corpus, a real manifest figure and one persisted analyst
  report written by the coordinator.
- `_data/ideas.jsonl` is unchanged by every verification run in all three phases.
- `uv run python -m src.governance` exits 0 and `uv run pytest` passes from the integrated tree.

## Out of scope and open questions

This plan does not turn any programme into a governed plan. The twelve programmes each still need
their own requirement and plan, and the owner's chosen order puts concurrency, git safety and
enforcement (`P3`) first. It does not act on the partition's outstanding items — the duplicate
pairs, the closure candidates, the seventeen proposed links from triage — which are owner rulings
recorded in `docs/00-working/handoff-idea-partition-and-triage.md`. It does not edit `AGENTS.md` or
`CLAUDE.md`, and it does not change the adversary charter.

**No ADR was written.** The three design rulings of 2026-09-14 are recorded above rather than in a
decision record, on the grounds that `ADR-010` already governs where a staging artifact lives and
`ADR-017` already governs pack methodology, so a third record would restate both. If the owner wants
these rulings citable on their own, that is an ADR to add, and the plan should be amended to
reference it.

**`phase-part-01` must decide how far audit 1's convergence brief can be trusted with two
analysts.** The first run's brief leaned on a 3-1 split being the expected shape of finding bias.
With one reader and one control there is no split to read, only a disagreement, and the brief has
to say what the adversary should do with it. The phase writes that wording; this plan does not
pre-empt it.

**A non-Claude host cannot run the workflow yet.** `PROMPT-034` is host-neutral text by design, so
the procedure is readable anywhere, but only the Claude skill exists. Porting it is
[PLAN-020](PLAN-020-portable-agent-workflows.md)'s contract, and `/partition-ideas` should be added
to that plan's surface once the adapter contract is proven rather than hand-translated here.
