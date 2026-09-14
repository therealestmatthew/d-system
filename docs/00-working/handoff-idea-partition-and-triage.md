# Handoff — idea partition, triage sweep, and what comes next

Ungoverned staging note per `ADR-010`. Written 2026-09-13 at the end of the idea-batching build
and the triage sweep that followed it. Everything below is merged to `dev` and pushed.

## Where the process stands

**Done.**

1. **The idea-batching build ran end to end** under `PROMPT-033` / `PROMPT-032` — four independent
   analyst partitions, two adversarial audits, synthesis, three owner gates. All six dispatches on
   sonnet, no escalation.
2. **The partition is accepted**: `docs/00-working/idea-batching-partition.md` — 129 ideas into
   **62 fine groups and 12 programmes**, with a six-field record per group, an unbatched section,
   and decline candidates in three tiers.
3. **Every decline candidate was ruled on individually.** Eight discarded, eleven explicitly kept
   with the reason recorded on the idea itself.
4. **All 40 ideas that were open were triaged** through the `idea-triage` agent in four waves of
   ten. Every annotation was verified against the folded log before its status moved; 40/40 landed
   correctly.

**The open set was empty for about twenty minutes.** `agent/lit-campaign` then merged
`phase-lit-05` into `dev`, bringing **14 new open ideas, `000208`–`000221`**. State now: 221 ideas
— 190 `triaged`, 7 `promoted`, 10 `discarded`, **14 `open`**.

That is worth stating rather than hiding, because it is the whole problem in miniature: a triage
sweep is a snapshot, the log is written by concurrent sessions, and "everything is triaged" decays
the moment a peer integrates. The next sweep should triage `000208`–`000221` and expect the same.

**The partition is a map, not a plan.** Each approved programme still needs its own requirement and
plan before any code. That is the next body of work.

## The twelve programmes

| # | Programme | Ideas | One-line character |
|---|---|---|---|
| P1 | Idea graph and lifecycle | 19 | ARCH-005 schema bundle, idea agents, reporting, idea→plan drafting |
| P2 | Document and backlog governance | 7 | Requirement-vs-plan contract, backlog scaling, small registry gaps |
| P3 | **Concurrency, git safety and enforcement** | 10 | Claim recovery, branch protection, backup, harness enforcement |
| P4 | Agent engineering and delegation | 19 | Framework umbrella, lifecycle roster, anti-pattern tracking, audits |
| P5 | Autonomous agent operations | 5 | Trigger gateway, run ledger, worker, capability broker, librarian |
| P6 | Retrieval and knowledge infrastructure | 9 | Ordering, vector, code graph, documentation companion set, provenance |
| P7 | Blocked downstream projections | 4 | Portfolio data gap; temporal/scenario/calibration, all gated |
| P8 | Schema consistency and testing | 8 | Schema/DDL drift, contract compiler, testing strategy, drift tests |
| P9 | HTML generation and design system | 6 | Template/component/palette libraries, designer agent, atlas, reconciliation |
| P10 | Workbench architecture and quality | 13 | Vocabulary, audits, slot/panel redesign, sub-app packaging, performance |
| P11 | Workbench features and defects | 16 | HTML Viewer, bookmarks, rotator, terminal API, small defects |
| P12 | Standalone explorations and housekeeping | 11 | Observability, content strategy, repo tracker, platform evaluation |

**Excluded by owner ruling:** the 23 consultant-demo-kit ideas `000171`–`000193`. They are already
governed by `REQ-008`, `PLAN-024` and `phase-kit-01`–`08`. Two facts make re-planning them wrong:
the roster was cut from 23 to **16** (not 13 — `REQ-008`'s prose error, corrected today in
`22941c4`), and the scenario/fixture premise was **reversed** — components must now be general tools
taking user-supplied material, which is `REQ-008` K15.

**Unbatched, 2 of 129:** `000125` (discharged by the partition itself) and `000089` (already
delivered).

## What the sweep revealed

Two families dominate the backlog and cut across the programme boundaries:

- **Convention without enforcement** — `000150`, `000151`, `000152`, `000153`, `000154`, `000155`,
  `000156`, `000158`, `000196`, `000198`. One cause: work moved out of the shared primary checkout
  faster than the checks that assumed it. **This is P3**, and this session produced two fresh
  instances while triaging.
- **Evidence-contract under-specification** — `000147`, `000148`, `000149`, `000197`, `000199`,
  `000200`, `000201`, `000202`, `000203`. The contract names vocabulary but not the mechanical rule
  a gate depends on. One caused a 20% ranking distortion pointing *toward* the campaign's own
  hypothesis. Better settled as **one amendment to `PLAN-023.03`** than nine separate fixes, and
  `phase-lit-05` needs it.

## Outstanding questions and decisions

1. **Duplicate pairs — keep which?** `000150`/`000195` (private-content check silent in a worktree);
   `000198` and the peer branch's independently-captured `000208` (`--catalog` prints, never writes).
2. **Closure candidates, none acted on.** `000157` (all three hygiene items done), `000207`
   (`REQ-008` corrected today), `000198`/`000208` (fix exists on unmerged `agent/catalog-writer`).
   `000170` is *not* one — it is correctly open, with four phases queued and nothing built.
3. **Promotion path for `000170`** — it now has `REQ-008`/`PLAN-024` to promote to.
4. **Proposed links from triage — none were written.** Collected for manual review:
   `000152→000041`, `000157→000150/000195/000158`, `000160→000159`, `000161→000163/000164`,
   `000162→000167`, `000163→000061`, `000165→000159/000160`, `000166→000161`, `000169→000168`,
   `000195→000150` (`relates_to`, not `supersedes`), `000196→000051/000077/000165`,
   `000197→000199/000200`, `000199→000148/000149/000200/000201/000202`, `000201→000202`,
   `000204→000027`, `000205→000125`, `000206→000160/000165`.
5. **`000202` blocks nothing now** — `phase-lit-04` closed on the peer branch despite `dev`'s
   `next_action` still naming it as a blocker. `dev`'s text is stale, not wrong-headed.

## Next steps, in the owner's chosen order

1. **Generalize the partition process** — owner chose the full path: a governed **requirement + plan
   + backlog phases**, then a `/partition-ideas` skill. *Plan before code applies.*
2. **`P3` becomes the first governed plan** — concurrency, git safety and enforcement.
3. Then the remaining programmes, one pack at a time.

### What is already reusable, and what is not

| Reusable today | Not yet |
|---|---|
| `.claude/agents/partition-adversary.md` — chartered deliberately for *any* partition, ideas or otherwise | **No skill or command exists.** Re-running means hand-dispatching from `PROMPT-032` |
| `tools/build_idea_corpus.py` (`--seed`, `--out`, `--exclusions`, `--stats`) + `OPS-015` | `CORPUS_STATUS = "triaged"` is a **module constant, not a flag** — add `--status` |
| The four analyst prompts and both audit briefs, in `PROMPT-032` | The **synthesis protocol** lives inside a build-specific pack, not anywhere reusable |

**A repeat is cheaper than this run was.** `000205` established the ascending/descending/shuffled
variation changed presentation but not the answer — so the next sweep is **4 dispatches, not 6**
(R1, R4, A1, A2), keeping only the findings ablation, which is the manipulation that earned its cost.

## Practical notes for the next session

- **`dev` is green**, pushed. `578 passed`, governance exits 0, `31 identifiers checked`.
- **Evidence lives at `_working/idea-corpus/`** — four analyst reports, both audits, four corpora,
  manifest. **Gitignored and primary-checkout only**; a merge will never carry it and
  `git worktree remove` would destroy it.
- **Ideas captured this session:** `000204` (resolved work leaves its idea open — the systemic one),
  `000205`, `000206`, `000207`.
- **Peer branches:** `agent/lit-campaign` is now **fully merged** into `dev` through
  `phase-lit-05`. Still unmerged: `agent/catalog-writer` (`803af92`, the `--catalog` fix — until it
  lands, `--catalog` prints and does not write, so redirect it by hand), `kit-skills-six`,
  `phase-demo-07`, `phase-wb-07`.
- **Two harness constraints worth knowing.** Subagents **cannot write report files** (`000206`) —
  they return text and the coordinator persists it. Subagents also inherit the **primary checkout**
  as their working directory regardless of the coordinator's worktree, which is why the triage
  workflow writes there.
- The idea-id race fired once during this session's integration and was resolved by renumbering to
  `000204`–`000207`; it was then checked for in advance against the peer branch and did not recur.
