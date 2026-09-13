---
schema_version: 1
id: doc-prompt-idea-batching-kickoff
code: PROMPT-033
title: Idea-batching build kick-off record
kind: prompt
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems: [sys-governance, sys-backlog, sys-portfolio]
depends_on: [doc-prompt-idea-batching-delegation-pack, doc-prompt-idea-batching-pre-plan-package, doc-prompt-pack-protocol]
---

# Idea-batching build kick-off record

The record the idea-batching build session starts from. `GOV-008` stages 6 and 7 collapse into
this document per [PROMPT-025](PROMPT-025-idea-batching-pre-plan-package.md) decision 13: no
separate coordinator prompt is written, because this build is one session of six dispatches and
needs no resume harness. That is a deliberate, documented deviation from the protocol.

**Precedence rule: where this record and the delegation pack
([PROMPT-032](PROMPT-032-idea-batching-delegation-pack.md)) differ, this record wins.**

## Pinned starting state

Measured 2026-09-12. Re-measure at kickoff; a figure that has moved is a fact to report, not a
discrepancy to reconcile silently.

| Fact | Value at pack time |
|---|---|
| Corpus size | **129** ideas |
| Ideas in the log | 146 |
| `triaged` | 135 |
| Removed by the demo fast lane | 6 — `000101`, `000105`, `000107`, `000108`, `000117`, `000130` |
| Recorded by the fast lane but returning to the corpus | 6 — `000106`, `000110`, `000118`, `000119`, `000132`, `000137` |
| Outside the corpus by status | 7 `promoted`, 2 `discarded`, 2 `open` (`000145`, `000146`) |
| Layered evidence (>1 finding) | 7 — `000014`, `000070`, `000071`, `000077`, `000087`, `000091`, `000099` |
| Findings not by `agent-idea-triage` | 6, across 5 other authors including the owner |
| Backlog | 131 phases; `max_active: 3`, **1 active**, headroom 2 |
| Active claim | `phase-demo-07` (`agent-demo-glossary`), locking `sys-brain` and `sys-portfolio` |
| Governance | `--inventory` exit 0, 182 documents, 20 memories |
| Suite | `578 passed` |

**The `sys-portfolio` overlap is known and accepted.** `phase-demo-07` locks it; this build
claims no phase, writes no file under `brain/concepts/`, and touches no path that phase declares.
Recorded so the build session does not rediscover it as a surprise.

**Corpus size is read, not assumed.** The count above is a pin for comparison. The build session
takes the real number from `_working/idea-corpus/manifest.json` after running the corpus builder
([OPS-015](../08-governance/OPS-015-build-idea-corpus.md)).

## Deadline context

The live demo is the week of **2026-09-15**. **This pack is not demo-critical.** The demo's claim
on the schedule is served by the fast lane (`PROMPT-025` decision 2), which has already run and
produced `docs/00-working/demo-fast-lane-exclusions.yaml`. If the two compete for attention, the
fast lane wins and this build waits. That is intended behaviour, not a descope.

## Owner-ratified deltas for this build

Gathered 2026-09-12. These are per-build rulings; they do not generalise to the next pack.

1. **Integration cadence — nothing is merged onto `dev` without the owner.** The build session
   pushes its own branch freely (backing up work is not publishing), but integrates nothing. The
   owner merges after GATE 3, once they have accepted the partition. There is no pre-approval of
   any kind in this build, deliberately: the deliverable is one ungoverned staging document and
   nothing downstream is waiting on it.

2. **The four analysts are dispatched concurrently**, in one round. Their isolation is structural
   — each reads only its own corpus file and writes only its own report — not temporal, so
   running them at once costs nothing in independence and reaches GATE 1 fastest.

3. **No model escalation without the owner.** All six dispatches run on **sonnet**. At most two
   fix cycles per work item; if a dispatch fails twice, the session **reports it and stops**
   rather than spending `GOV-008`'s single Opus escalation. With three gate pauses already in the
   design, there is little an escalation buys that a pause does not.

4. **No special lanes.** The workbench build's bounded enhancement lane has no counterpart here.
   Anything the build session notices that is outside the partition task is captured as an idea
   through `tools/append_idea.py` and left there.

5. **The descope ladder stands as ratified**, with the flag on `A2`'s placement left standing
   (see `PROMPT-032`'s ladder section). No rung is taken without the owner's explicit direction.

## Gate schedule

`PROMPT-025` decision 12, binding. The build session **stops** at each of these:

| Gate | When | What the owner does |
|---|---|---|
| **GATE 1** | The four analyst reports land | Reads them; may correct course before the audit spends its budget |
| **GATE 2** | Audit 1 returns | Reads the coverage arithmetic, the convergence check and the order-manipulation finding |
| **GATE 3** | Audit 2 has checked the merge | **Accepts or corrects the partition, and rules on every decline candidate individually** |

A critical issue arising *outside* a gate gets `GOV-008`'s dual review first — an adversarial
agent challenges the finding and attempts a solution — and the build pauses for the owner only if
the issue survives that review unresolved.

## Standing prohibitions for this build

- **Nothing is written to `_data/ideas.jsonl`** by any agent at any stage — no `discarded` status
  event, no annotation, no link. Decline candidates are nominated for the owner, never recorded.
- No agent claims a backlog phase.
- `AGENTS.md` and `CLAUDE.md` are never edited.
- The batching output is an ungoverned staging document in `docs/00-working/` per `ADR-010`. It
  is **not** additionally recorded as anchor ideas and links in the idea log — that was considered
  and declined, to avoid keeping two copies consistent.
- Idea `000125` (holistic triage of the accumulated idea batch) is promoted only when the batching
  document is **approved**, not when it is written.

## The kick-off paragraph

The single paragraph to paste into a fresh terminal. The durable copy is here; any copy delivered
in chat is a convenience.

> You are running the D-System idea-batching build. Read `AGENTS.md`, then
> `docs/08-governance/GOV-006-conversation-guidelines.md`, then
> `docs/02-prompts/PROMPT-033-idea-batching-kickoff.md` — this record, which pins the starting
> state and the owner's ratified deltas and **wins wherever it and the delegation pack differ** —
> and then `docs/02-prompts/PROMPT-032-idea-batching-delegation-pack.md`, which holds every prompt
> you will dispatch. Background, if you need it: `docs/08-governance/GOV-008-prompt-pack-protocol.md`
> and `docs/02-prompts/PROMPT-025-idea-batching-pre-plan-package.md` (the sixteen ratified
> decisions — do not re-ask any of them). **Work in a worktree** — `AGENTS.md` requires one for
> every session regardless of what the work touches, and this build writes a tracked file — and
> never switch the primary checkout's branch. Run the delegation pack's `K` section first: the
> worktree, then preflight, then `uv run python tools/build_idea_corpus.py`, then read
> `_working/idea-corpus/manifest.json` for the real corpus size rather than assuming one. Dispatch
> `R1`–`R4` concurrently to general-purpose sonnet agents, sending each block verbatim and
> changing nothing — `R4` is a bias control and must never be told that it is one, that findings
> exist, or that other analysts are running. Stop at GATE 1. Then `A1` to `partition-adversary`,
> stop at GATE 2, then synthesise in this session under the `S` protocol, then `A2`, then stop at
> GATE 3 for the owner to accept or correct the partition and rule on every decline candidate.
> Write nothing to `_data/ideas.jsonl` at any stage, claim no backlog phase, merge nothing onto
> `dev`, and escalate no model above sonnet — report and stop instead. The deliverable is the
> batching staging document in `docs/00-working/`.
