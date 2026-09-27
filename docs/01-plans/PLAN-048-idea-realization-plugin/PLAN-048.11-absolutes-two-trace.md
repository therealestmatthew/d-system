---
schema_version: 1
id: doc-idea-realization-plugin-absolutes-two-trace
code: PLAN-048.11
title: Idea-realization plugin — trace table for the governance documents as absolutes, part two
kind: plan
status: approved
owner: repository-owner
created: '2026-09-27'
updated: '2026-09-27'
systems: [sys-plugin-absolutes]
depends_on: [doc-idea-realization-plugin-absolute-documents-two, doc-idea-realization-plugin-absolutes-trace]
parent: doc-idea-realization-plugin
---

# Trace table: the governance documents as absolutes, part two

Child of [PLAN-048](PLAN-048-overview.md); written by `phase-plug-09` under
[PLAN-048.09](PLAN-048.09-absolute-documents-two.md). It maps every rule in the plugin's
`docs/prompt-packs.md`, `research-packs.md`, `coordinator.md`, `batches.md`, `role-contracts.md`,
`plan-review.md`, `adversary-prompt.md`, `multi-session.md` and `session-manager-messages.md` to the
source passage it restates, and lists what was not shipped and why. The plugin never cites this
file (`REQ-031` R02). Part one's table is [PLAN-048.10](PLAN-048.10-absolutes-trace.md); its ledger
classification is the one used here.

## Context and scope

`REQ-031` R20, second half: families D (methodology: `GOV-008`, `GOV-009`, `GOV-013`, `GOV-016`),
E (role contracts and review: `GOV-014`, `GOV-018`, `PROMPT-038`) and F (multi-session
coordination: `GOV-017`, `PROMPT-037`). By the owner's ruling on 2026-09-26 the plan quality
standard (`GOV-010`), which no family covered, joined family E and its content judgements ship in
`plan-review.md` with the worked examples dropped.

Source line numbers refer to the files as they stood on `dev` when `phase-plug-09` was claimed.
`P:` abbreviates `plugins/idea-realization/`.

## Design

Four analyst dispatches ran in parallel: D, E, the plan quality standard (as a separate dispatch
within E), and F. Each returned one-line absolutes with source lines and the plugin mechanism
behind each rule, with part one's ledger classification attached. Rule ids are the analysts'
(`D`, `E`, `G`/`M`/`P`/`Q`/`T`/`L`/`O` for the plan quality standard, `F`), and ledger rules keep
their `C` ids. The "Rule as extracted" text is the analyst's; the plugin document states the same
rule in its own words, with the differences listed under "Changes made while writing".

## Work and dependencies

1. The four analysts reported (sections below).
2. The owner ruled on the choices they raised (see "Owner rulings").
3. The nine plugin documents were written from the extractions, and the plugin files the rulings
   touched were amended.

## Owner rulings

Given in the `phase-plug-09` session on 2026-09-26 and 2026-09-27:

- The plan quality standard's judgements go into `plan-review.md`, stated abstractly.
- The per-dispatch token ceiling is not shipped: nothing in the plugin enforces it.
- The plan-review record lives in the session record of the session that runs the review.
- Models are named by tier (the cheapest capable, the standard, the most capable), not by name.
- "No tests in the primary checkout" (C30) is scoped to multi-session operation, and the `backlog`
  and `session-start` skills are amended to run the preflight tests in the worktree under it.
- A relayed `GRANTED merge` (C29.4) is the owner's approval, and the `session-start` and
  `session-close` skills are amended to say so.
- Under multi-session operation, Ideation triages only the ideas the owner names.

## Family D: methodology (GOV-008, GOV-009, GOV-013, GOV-016)

G8, G9, G13, G16 and G3 abbreviate the four sources and the decision ledger. Rule ids run D1 to D132.

### 1. Per-document rules

#### A. P:docs/prompt-packs.md (from G8, plus C14)

**Preamble**
| Id | One-line absolute rule | Source | Mechanism |
|---|---|---|---|
| D1 | A prompt pack is the complete governed artifact set a multi-agent build runs from: a requirement, decision records, a plan, backlog phases, agent-roster deltas, a delegation pack, a coordinator prompt and a kick-off record. | G8:17-19 | conduct; kinds in protocol.md §4 |
| D2 | A planning session manufactures the pack and a separate build session spends it. The build session sends nothing the planning session did not write. | G8:25-27 | conduct |
| D3 | The artifact set is always called a prompt pack. | G8:27 | conduct |

**The pipeline**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D4 | The pipeline has eight stages, and each ends at a gate. Owner sign-off freezes the stage's artifact; a later change passes the same gate again. | G8:32-33 | conduct |
| D5 | Prompt A (the pre-plan package) is a governed prompt document, planned with the owner through AskUserQuestion batches, one at a time, at the point each question matters. | G8:37-39 | kind `prompt`, series `PROMPT` (document-codes.md, P:templates/codes.yaml:31); AskUserQuestion as in P:skills/backlog/SKILL.md:77-81 |
| D6 | Prompt A carries the ratified decisions marked do-not-re-ask, the feature inventory, the open-questions list, the standing constraints and the deadline context. | G8:41-44 | conduct |
| D7 | Prompt B (the pack-factory prompt) is a separate governed prompt document, drafted by executing Prompt A, and it investigates the repository and writes the pack. Prompt A and Prompt B are never one document. | G8:48-52 | conduct |
| D8 | An adversarial agent audits Prompt B against Prompt A and the repository, assuming it is broken. Findings become fixes, and the owner signs off the revised Prompt B before it runs. | G8:56-58 | conduct |
| D9 | Prompt B runs in plan mode first. Automatic execution starts only after the owner confirms the plan. | G8:62 | conduct |
| D10 | The pack carries requirement rows with observable verification methods (browser verification where the deliverable has a UI), and a decision record for every boundary the build needs settled. | G8:65-67 | protocol.md §4; P:templates/requirement.md |
| D11 | Pack phases are sized one session each, and their order is encoded in `depends_on`. | G8:68-69 | pointer: backlog-protocol.md §2, §14 |
| D12 | Agent-roster deltas extend existing agents' charters where possible. A new agent needs a stated cause. | G8:70 | conduct |
| D13 | The delegation pack has one section per phase: kickoff `K`, creator/validator pairs `C*`/`V*`, phase gate `G`, adversarial review `A`, and browser verification `W` where the phase has a UI. Each section is idempotent and is dispatched verbatim. | G8:71-73 | conduct |
| **C14** | Every dispatched block, and the gate block because a gate may re-run, opens with: *"Assess the current state of the repository against the deliverables below; do only what is missing; report what already existed."* A block the coordinating session performs itself is headed "Not a dispatch." and carries no idempotency sentence. | G3:384-392, 396-398 | conduct |
| D14 | The descope ladder is ordered for the actual runway. | G8:74 | conduct |
| D15 | A second adversarial agent audits the finished pack files. Fixes are committed, and the check exits 0 before the pack is done. | G8:76-77, 80-81 | P:scripts/check.py (protocol.md §7) |
| D16 | The coordinator prompt is a governed prompt document covering preflight, the phase graph, the completion gate, integration and close-out. It is generic and idempotent, so every re-run is a resume. Per-build rulings go in the kick-off record, not in the coordinator prompt. | G8:85-88 | conduct |
| D17 | The owner signs off the coordinator prompt. Adversarial review at this gate runs only when the owner asks for it. | G8:92-93 | conduct (coordinator.md D108 covers prompts written outside this pipeline) |
| D18 | The kick-off record is a governed prompt document. It carries the per-build ratified deltas (integration cadence, descope authority, any special lane), gathered through AskUserQuestion with recommendations before it is written, and the pinned starting state (queue state, peer claims, deadline). | G8:97-102 | conduct |
| D19 | Where the kick-off record and the coordinator prompt differ, the kick-off record wins. | G8:103-104 | conduct |
| D20 | The kick-off paragraph is the record's final section: one paragraph that references everything, also delivered in chat so the owner can paste it into a fresh terminal. The chat copy is never governed or tracked; its durable copy is the one inside the record. | G8:105, 107-110 | conduct |

**Standing rules for every pack**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D21 | Context is loaded when the step that needs it begins. Parent documents defer to their children, the coordinator prompt defers the phase protocol, and the delegation pack is dispatched one section at a time. No agent's opening context holds the whole pack. | G8:116-119 | conduct |
| D22 | In a prompt-pack build the coordinator claims nothing, writes no code, authors no prompts and never does a worker's job. A missing prompt is a blocking finding for the owner. | G8:123-124 | conduct (see conflict 1) |
| D23 | Before every claim, the active-claim budget and the path locks are checked numerically. The Conflicts column says nothing about the budget. | G8:125-126 | P:skills/backlog ("Active claims: N of M allowed", P:scripts/backlog.py:315); backlog-protocol.md §6 |
| — | One worktree per phase, with an explicitly chosen free port. | G8:125 | pointer: protocol.md §11 |
| — | Peers' claims are never touched, and the instruction files are never edited. | G8:127 | pointer: backlog-protocol.md §6; protocol.md §3 |
| D24 | Validators receive the diff, the requirement text and the verification commands, and never the creator's rationale or report. | G8:128-129; G13:238-239 | conduct |
| D25 | Work is committed before it is validated. A truncated agent is resumed, never re-run. An orchestrator's assertion is checked against real output before anyone acts on it. | G8:130-131; G13:240 | conduct |
| D26 | Haiku runs mechanical gates and Sonnet is the standard model for judgment. Opus is never pre-assigned and is used at most once per build, as a documented escalation. | G8:135-137; G13:223-225 | conduct |
| D27 | Each work item gets at most two fix cycles. Whatever survives them is reported, not looped on. | G8:138; G13:226-227 | conduct |
| D28 | The close-out reports spend: loop counts, any escalation, and wall-clock time against the runway. | G8:139; G13:231-232 | conduct |
| D29 | Prompt A's open questions always include whether the build stops at gates or runs through to close-out. The answer is recorded in the kick-off record. | G8:143-145 | conduct |
| D30 | A critical issue (a design or functional impact too costly to defer) first gets a dual review, in which an adversarial agent challenges it and attempts a fix. The build pauses for the owner only if the issue survives unresolved. | G8:145-148 | conduct |
| — | A failing check is a result to record, not a step to retry. | G8:148-149 | pointer: reporting.md "Show the output that carries information" |
| D31 | No descope rung is taken without the owner's explicit direction, unless the kick-off record grants a stated exception. | G8:153-154 | conduct |

**Template appendix**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D32 | Prompt A sections: ratified decisions (do-not-re-ask), feature inventory, what the planning session produces in order, open questions, standing constraints, deadline context, and the block that drafts Prompt B. | G8:158-160 | conduct |
| D33 | Prompt B sections: role and hard scope limits (documents only), preflight (check green, peer claims), the pack artifacts in order with codes from next-code, the open-questions protocol, and the stop condition (pack exists, check exits 0, owner has the review summary). | G8:162-166 | P:skills/next-code; P:scripts/check.py |
| D34 | Phase section: `K` (claim, worktree, ports, item order), `C*`/`V*` in pairs, `G` (verification commands with real output), `A`, and `W` where there is a UI. | G8:168-170 | conduct |
| D35 | Coordinator prompt sections: coordinator-only role, preflight (check, budget, clean checkout, tooling smoke test), phase graph with dispatch order and the locks that force it, completion gate and integration terms, and close-out (checkpoint, spend, resume state). | G8:172-174 | P:skills/checkpoint |
| D36 | Kick-off record sections: starting state, owner-ratified deltas with the precedence rule, and the kick-off paragraph. | G8:176-177 | conduct |

#### B. P:docs/research-packs.md (from G9)

**Preamble**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D37 | A research pack is the governed artifact set a research campaign runs from: a scope record, a hypothesis register, a search-domain matrix, a delegation pack of search, extraction and review prompts, a coordinator prompt and a kick-off record. | G9:17-19 | conduct |
| D38 | A research pack follows the pipeline and gates of prompt-packs.md. Research discipline replaces the build's standing rules. | G9:20-22 | pointer: prompt-packs.md D4-D20 |
| D39 | This document governs process. The campaign's content methodology (what to search, how to score overlap, what an evidence row holds) is a separate document. On content the methodology wins; where it is silent on process, this document governs. | G9:24-26, 35-36 | conduct (pattern; the source's named files are not shipped) |
| D40 | A campaign that needs a content methodology writes it before the pack is drafted, never partway through a search. | G9:36-37 | conduct |
| D41 | A planning session manufactures the pack and a separate execution session spends it; nothing is authored mid-campaign. The artifact set is always called a research pack, never a prompt pack. | G9:39-42 | conduct |

**The pipeline** (D4 and D9 apply by pointer: G9:46-47 and G9:79)
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D42 | Prompt A carries the ratified scope: the research questions, the hypothesis set and the null hypothesis the campaign works to support, marked do-not-re-ask. | G9:51-55 | conduct; D5 applies |
| D43 | Prompt A's artifact inventory marks every existing research input as frozen (read-only baseline), seed (encountered, not validated) or live. It also carries open questions, the standing constraints and the effort and deadline context. | G9:56-60 | conduct |
| D44 | Prompt B is a separate governed prompt document that investigates the campaign's research inputs and the repository, then writes the pack. | G9:64-67 | conduct |
| D45 | The Prompt B review audits against Prompt A, the content methodology and the actual research inputs. It looks for a search outside the methodology's domains, an extraction that cannot fill the evidence schema, and a stop condition nobody can measure. | G9:71-75 | conduct |
| D46 | The scope record holds the research questions, a hypothesis register with a falsification criterion for each hypothesis, and the status vocabulary the verdicts use. | G9:82-83 | conduct |
| D47 | The search-domain matrix assigns every domain in the methodology to a phase, with the terminology variants each search must cover. No domain is left to judgment. | G9:84-85 | conduct |
| D48 | Phases follow the pass order: broad mapping, then deep reading, then adversarial testing, then synthesis. `depends_on` blocks synthesis while its evidence phases are open. | G9:86-89 | pointer: backlog-protocol.md §2 |
| D49 | The evidence contract names the schema every extraction fills, the reproducibility-ledger format every search appends to, and where both live. | G9:90-91 | conduct (pattern) |
| D50 | Delegation-pack phase sections are `K`, search/extraction pairs `S*`/`X*`, collision review `R`, gate `G` and adversarial synthesis review `A`, each idempotent and dispatchable verbatim. | G9:92-94 | conduct; C14 applies |
| D51 | The descope ladder states which domains, hypotheses or passes are cut first, ordered for the actual deadline. | G9:95-96 | conduct |
| D52 | The pack audit checks the finished files against the content methodology and the repository; the check exits 0 before the pack is done. | G9:100-102 | P:scripts/check.py |
| D53 | The coordinator prompt is generic and idempotent. Per-campaign rulings go in the kick-off record. | G9:106-109 | pointer: D16 |
| D54 | The kick-off deltas cover gate check-in cadence, descope authority and search-provider constraints. The pinned starting state includes the frozen baseline's identity. | G9:120-124 | conduct; D18-D20 apply (G9:111-114, 125-129) |

**Standing rules for every campaign**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D55 | The coordinator prompt leaves the content methodology to the agents that execute it. A search prompt carries its own domain and terminology variants, never the whole matrix. | G9:135-139 | conduct; D21 applies |
| D56 | The campaign works to support the null hypothesis. Collisions are recorded first, and the architecture is revised only in the synthesis phase. | G9:143-144 | conduct |
| D57 | No agent renames a concept, narrows a hypothesis or rewrites scope to avoid a collision. A hypothesis change mid-campaign is a blocking finding for the owner. | G9:145-146 | conduct |
| D58 | The frozen baseline is never modified. A seed source is promoted only through the methodology's verification steps, and an existing seed ledger is never silently altered. | G9:147-149 | conduct |
| D59 | Negative claims use the pack's status vocabulary. "No prior work exists" is not a permitted verdict, and a failed search is recorded as failed, with its queries. | G9:150-151 | conduct |
| D60 | Every search appends to the ledger: query, provider, date, filters, result ids, and the reasons for inclusion and exclusion. A search that logged nothing did not happen. | G9:155-156 | conduct |
| D61 | Generated summaries are leads, never evidence. Every synthesis claim traces to a primary source with a locator, and an untraceable claim is removed. | G9:157-158 | conduct |
| D62 | Derivative sources are traced to their shared ancestor and never count as independent confirmation. | G9:159-160 | conduct |
| D63 | Every critical collision gets a second review by a different agent, which receives the source and the evidence row but never the first agent's rationale. | G9:161-163 | conduct |
| D64 | The research coordinator claims nothing, searches nothing, writes no findings, authors no prompts and never does a worker's job. A missing prompt is a blocking finding. | G9:167-169 | conduct |
| D65 | Search, extraction and review are separate dispatches. Reviewers get sources and rows, never the searcher's interpretation. | G9:170-171 | conduct |
| — | Peer claims, instruction files, confidentiality, commit before review, resume truncated agents. An orchestrator's assertion is verified against the ledger. | G9:172-175 | pointer: backlog-protocol.md §6; protocol.md §3, §10; D25 |
| D66 | Sonnet is the standard model for search and extraction. Synthesis and collision review also default to Sonnet. | G9:179-181 | conduct; D26-D27 apply (G9:182) |
| D67 | The close-out reports searches run, sources read in depth, any escalation, and wall-clock time against the runway. | G9:183-184 | conduct |
| D68 | Gate check-in follows D29. A critical issue is a collision that falsifies scope, or a methodology defect that invalidates collected evidence, and it gets a dual review before it pauses the campaign. | G9:188-193 | conduct |
| D69 | The completion gate encodes the methodology's stop conditions and is measured against the ledger, never asserted. | G9:197-198 | conduct |
| D70 | Saturation is demonstrated (searches return duplicates, and every hypothesis has at least one serious challenger), never declared. | G9:198-199 | conduct |
| D71 | A campaign that stops early stops at a phase boundary, with the resume state in its session record. | G9:201-202 | backlog-protocol.md §9, §11; D31 applies (G9:199-201) |

**Template appendix**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D72 | Prompt A sections: ratified scope, artifact inventory with frozen/seed/live marks, outputs in order, open questions, constraints, effort and deadline context, and the Prompt B block. | G9:206-209 | conduct |
| D73 | Prompt B sections: role and hard scope limits (documents only, no searching), preflight (check green, peer claims, methodology read), pack artifacts in order with codes from next-code, the open-questions protocol, and the stop condition. | G9:211-215 | P:skills/next-code |
| D74 | Phase section: `K` (claim, output paths, ledger location, item order), `S*`/`X*` pairs, `R`, `G` (stop-condition measurements against the ledger, real output), and `A` where the phase produces synthesis. | G9:217-220 | conduct |
| D75 | Coordinator prompt sections: role, preflight (check, clean checkout, baseline integrity, ledger present), phase graph, completion gate in stop-condition terms, and close-out. | G9:222-225 | P:skills/checkpoint |
| D76 | Kick-off record: as D36. | G9:227-228 | pointer |

#### C. P:docs/coordinator.md (from G13, plus C20-C23)

**Preamble**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D77 | A coordinator is a session that drives many units of work to completion through dispatched agents while holding almost nothing in its own context. | G13:17-18 | conduct |
| D78 | This document is for the planning session that writes a coordinator prompt. prompt-packs.md and research-packs.md govern the pack, and batches.md governs the batch the coordinator runs. | G13:20-23, 29-33 | pointer |

**Establish the constraints first**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D79 | Before proposing any batch size, order or loop shape, the design answers the constraint questions from the governing text, not from memory. | G13:41-42 | conduct |
| D80 | The questions are: who may mark a unit done and whether the coordinator may; the concurrency cap and whether claims are released or accumulated; what collides, computed with the real collision function; every gate that waits for a human; and what the protocol mandates for branches, worktrees and hand-off. | G13:44-52 | backlog-protocol.md §6, §10; protocol.md §11-12; P:scripts/backlog.py:111 `collisions()` |

**The completion trap**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D81 | Claims are released by completion, not by integration. A coordinator whose units cannot reach complete during the run accumulates claims and stalls at `max_active`. | G13:60-61, 63-64 | backlog-protocol.md §6, §10 |
| D82 | When units cannot be completed during the run, a batch holds at most `max_active` units, all mutually non-colliding and dependency-independent. | G13:64-66 | P:scripts/backlog.py:129-149 |
| D83 | The first design question is whether the coordinator can finish anything. The design secures that authority or plans for hand-off; it never assumes an authority nobody granted. | G13:68-70 | backlog-protocol.md §10 (completion needs the owner's integration yes) |

**Partitioning**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D84 | Batches are dependency-closed: nothing in a batch depends on a later batch. | G13:74 | conduct |
| D85 | Order within a batch is a valid build order. | G13:75 | conduct |
| D86 | The partition is verified by script against the backlog, and the prompt states that it was verified and how. | G13:76-78 | P:scripts/backlog.py (`collisions`, `dependency_closure`) |
| D87 | Every unit appears exactly once; coverage is confirmed, not only correctness. | G13:79-80 | conduct |
| D88 | Each exclusion is named with its reason and with what the coordinator must not do about it. | G13:81-83 | conduct |
| D89 | Batch size is fitted to context and wall-clock time once completion is settled. The first batch is the evidence for the size, and the close-out records the answer. | G13:84-86 | conduct |

**One worktree per unit**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D90 | Every unit gets its own branch and worktree, named as the protocol names them. A coordinator invents no naming scheme. | G13:90-91 | pointer: protocol.md §11; P:skills/session-start §4 |
| D91 | A shared batch worktree fails: integration removes the worktree and deletes the branch, a diff stops being the unit, a failed unit entangles the next, and peers cannot read what is being worked. | G13:93-105 | protocol.md §12 ("worktree is removed and the branch deleted") |
| — | Each worktree has its own environment and an explicitly chosen port. | G13:107-109 | pointer: protocol.md §11 |
| D92 | The coordinator gets no worktree. Its repository writes are claim and completion commits on the integration branch. Session records belong in each unit's worktree, and its tracker is gitignored working state. | G13:111-114 | protocol.md §11; backlog-protocol.md §10 (see conflict 6) |

**Batch approval and questions at the open**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| **C20** | When the coordinator runs an owner-approved batch that names its phases in build order, that approval is the claim approval for those phases and stands in for the per-claim question in session-start step 2. `max_active` and the Conflicts column are still checked numerically before each claim, and a phase a peer holds is skipped untouched. | G3:491-496 | P:skills/session-start/SKILL.md:69-80 (the gate it displaces); P:scripts/backlog.py:152 |
| D93 | Before claiming anything, a read-only reconnaissance agent per unit runs in parallel. Each reports what its unit requires, whether its acceptance is observable, and anything that would make a careful person decline to start it. | G13:121-124 | conduct |
| **C21** | The questions a per-claim gate would raise go to the owner as one batch before the first claim, with the recommendation first in each question. | G3:495-497; G13:125-126 | conduct (AskUserQuestion) |
| **C22** | After that, the coordinator stops mid-batch only when a unit looks genuinely wrong (an acceptance condition nothing can verify, a missing deliverable, an undeclared dependency) or when an obstacle survives resolution. | G3:497-499; G13:127-129 | conduct; the same three signals as P:skills/session-start/SKILL.md:77-78 |
| D94 | Every other question accumulates to the close-out, ranked by how much its answer changes. | G13:131 | pointer: reporting.md "Do not block on a question that can wait" |
| **C23** | A blocker goes first to a resolver agent, which gets the blocker, the evidence, the unit's definition and the governing documents. Only a blocker it cannot settle reaches the owner, with its findings attached. | G3:499-500; G13:135-142 | conduct |

**Deviations and the decision record**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D95 | Every deviation from a governing document is named in the prompt: what it displaces, why, and under whose authority. The test is whether an agent reading the displaced document mid-run would think the coordinator is misbehaving. | G13:146-147, 149-152 | conduct |
| D96 | Two instructions that together override a documented gate are a deviation, and they are written down as one. | G13:167-170 | conduct |
| D97 | Before proposing a decision, the design searches the decision record for the rule it would change and puts the prior ruling in front of the owner. The new entry names the clause it displaces. | G13:178-181 | backlog `decision_record` (backlog-protocol.md §12) |
| D98 | The design looks for an earlier exception of the same shape and reuses its conditions. | G13:183-185 | conduct |

**The templates are the prompts**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D99 | A coordinator with no delegation pack carries dispatch templates. It fills a template from a unit's own fields and never composes a dispatch freehand. A unit that cannot fill a template is a blocking finding. | G13:193-196 | conduct |
| D100 | Templates work only where unit definitions are rich enough to serve as specifications. Otherwise, a pack is written. | G13:198-199 | pointer: prompt-packs.md |

**Context discipline**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D101 | The coordinator never reads a plan, requirement or unit body. It reads only its tracker, its decisions file, returned summaries and the command output it must verify. | G13:207-209 | conduct |
| D102 | Every return is bounded to a verdict, counts and the path of the file written, about fifteen lines. Detail goes in that file. | G13:210-211 | conduct |
| D103 | A dispatch carries only the unit it concerns, never the pack or the queue. | G13:212-214 | conduct; D21 |
| D104 | An agent that stops without writing its file is truncated. It is resumed, never restarted. | G13:215-216 | conduct |

**Cost and verification**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| — | Model tiers, the fix-cycle cap and spend reporting. | G13:220-227, 231-232 | pointer: prompt-packs.md D26-D28 |
| D105 | The descope ladder is decided before the run. Stopping cleanly mid-batch with the tracker current beats finishing degraded. | G13:228-230 | conduct |
| D106 | The coordinator runs each unit's verification commands itself and keeps the real output. An agent's claim of a pass is not evidence. | G13:236-237 | backlog-protocol.md §9 |
| — | Validator inputs; commit before validate. | G13:238-240 | pointer: prompt-packs.md D24-D25 |
| D107 | A schema or test is never edited to make a failing check pass. A schema that rejects a change is telling you the change is wrong. | G13:241-242 | conduct |
| — | Adversarial review is a completion condition. | G13:245-247 | pointer: backlog-protocol.md §10 (2) |

**Review the coordinator prompt**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D108 | A coordinator prompt written outside the prompt-pack or research-pack pipeline is adversarially reviewed against the repository before it is committed. The review asks whether the authority it invokes exists, whether the partition is real, whether the loop survives the actual commands, and what it silently gets wrong. A prompt produced by that pipeline follows D17. | G13:159-165, 251-254 | conduct |

**Idempotence and the tracker**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D109 | The same prompt runs every batch, and every re-run is a resume. Only the batch identifier changes between runs. | G13:261-262 | conduct |
| D110 | State lives in a tracker file, not in session memory. A dead session resumes from it. | G13:263-264 | conduct (no plugin location; see §4 item 11) |
| D111 | The coordinator is the tracker's only writer. Agents write only their own evidence files. | G13:265-266 | conduct |
| — | Copy gitignored evidence out before removing a worktree. | G13:267-268 | pointer: protocol.md §11 |
| D112 | A run never stops holding an unrecorded claim. The phase is handed off under backlog-protocol.md §11, or the held claim is reported to the owner. | G13:269-270 | backlog-protocol.md §11 |

**Checklist**
| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D113 | The planning checklist, in order: constraint questions; the decision record; the completion question before sizing; partition and verify it by script; draft the prompt (worktree per unit, no coordinator worktree, questions at the open, resolver first, templates, tracker); name deviations; record new authority naming the clause it supersedes; adversarial review; state which parameters the first run tests and record the answer. | G13:274-283 | conduct |

#### D. P:docs/batches.md (from G16; pattern only, no schema or directory)

| Id | Rule | Source | Mechanism |
|---|---|---|---|
| D114 | A batch is an owner-approved ordered set of queued phases, grouped into stages, that a coordinator builds. | G16:17-18 | conduct (pattern) |
| D115 | A batch table records grouping, sequencing and parallelism only. Scope, acceptance, verification, systems, deliverables and `depends_on` stay in the backlog and are never restated. | G16:42-43 | backlog-protocol.md §2 |
| D116 | A phase title may be copied in for readability. The backlog wins wherever the two disagree. | G16:45-48 | conduct |
| D117 | Composing and superseding a batch is the owner's decision. A coordinator never composes, adds or edits a composition, whether to fix a defect or to absorb a newly ranked phase. A wrong composition is a question for the owner. | G16:52-55 | conduct |
| D118 | A batch runs only after its composition has been checked against the backlog by script, and the check is recorded with the batch. | G16:63-64 | P:scripts/backlog.py functions |
| D119 | The check confirms that every phase id resolves in the backlog. | G16:66 | P:scripts/backlog.py |
| D120 | The check confirms that every phase is queued and unclaimed. | G16:67 | backlog-protocol.md §3 |
| D121 | The check confirms that every `depends_on` edge points to an earlier phase in the batch or to a complete phase outside it. That is what dependency-closed means. | G16:68-70 | pointer: coordinator.md D84 |
| D122 | Every external dependency is listed with the batch. | G16:71-72 | conduct (pattern) |
| D123 | Every stage boundary follows from a real dependency edge or a real collision, computed with the collision function. | G16:73-74 | P:scripts/backlog.py:111 |
| D124 | A recorded check is history, not a licence. The coordinator re-verifies before every run. | G16:80-81 | conduct |
| D125 | Stages run in order. A stage opens only when every phase of the one before is complete and integrated. Phases within one stage share no dependency edge, no system and no overlapping deliverable path. | G16:86-88 | backlog-protocol.md §7 |
| D126 | A parallel stage means the check will admit its phases together, not that they run together. The numeric checks run before every claim, and a stage runs serially when peers leave room for only one. | G16:90-93 | backlog-protocol.md §6; see C20 |
| D127 | Collision, not dependency, usually serializes a batch. A recorded collision is a lock, not slack to reclaim. | G16:97, 99-100 | conduct |
| D128 | The collision rule on deliverable paths is path-component prefix: equal, or one contains the other. It is computed with the real function, never with exact matching. | G16:101-104 | P:scripts/backlog.py:92-95 `path_conflict` |
| D129 | A coordinator that finds nothing runnable computes a dependency-closed candidate from `next_up`, with its stages, puts it to the owner as a question, and stops. | G16:120-124 | conduct; backlog-protocol.md §4 |
| D130 | The coordinator proposes and the owner decides. A composition exists only after the owner's yes, and an unanswered proposal is not a yes. | G16:126-129 | conduct |
| D131 | Once a run opens against a composition it is frozen. Changed membership is a new composition that supersedes the old one, and the old one is kept, naming its replacement. | G16:153-155, 157-159 | conduct (pattern) |
| D132 | No check validates a batch table. The composing session runs the checks and records them. | G16:163-167 | fact about the plugin: P:scripts/check.py has no batch check |

---

### 2. NOT SHIPPED

| Source | Source rule | Why not shipped |
|---|---|---|
| G9:28-33 | The content method lives in the three named research files. | The plugin has no research tree or content-method files. D39 keeps the pattern. |
| G9:90-91 ("under `research/`") | The evidence contract lives under the research directory. | The directory is repository-specific. D49 keeps "where both live". |
| G16:26-33 | The mechanism is a batch schema, a batches directory and a named coordinator prompt. | The plugin has no batch schema, no batches directory and no coordinator prompt. |
| G16:57-59 | A coordinator writes only the selected table's `status` and `updated`. | Depends on schema fields. Also a primary-checkout write that protocol.md §11 does not allow. |
| G16:63-64 (fields) | The check is recorded in `provenance` and `verified`. | Named schema fields. D118 keeps the pattern. |
| G16:108-109, 111-115, 117-118 | Deterministic selection: discover tables, run the one `in_progress`, else the lowest-`sequence` `queued`, ask only when ambiguous, an owner-named batch overrides. | Needs a discoverable table location plus `status`/`sequence` fields. The plugin has no batch path option (P:.claude-plugin/plugin.json userConfig) and no schema. Rewording it to point at the tracker would describe something the plugin does not do. |
| G16:131-134 | The `sequence` field removes ambiguity between several queued tables. | Schema field; depends on the selection rule. |
| G16:138-145 | Status vocabulary and transitions (`queued`/`in_progress`/`complete`/`superseded`; a batch with phases outstanding stays `in_progress`). | Run state needs a shared, tracked location. The plugin's resume state is the coordinator's tracker (D110). |
| G16:147-149 | Batch status edits land on the integration branch in the primary checkout. | No location. Conflicts with protocol.md §11, which limits primary-checkout work to the claim commit and catalog, and the fast-forward. |
| G16:99-100, 155 (field names) | The `after`, `conflicts_with` and `superseded_by` fields. | Schema fields. D127 and D131 keep the pattern. |
| G16:169-170 | Nothing prevents two tables being `in_progress`. | Depends on selection and status, which are not shipped. |
| G8:65-66 ("established validator style") | Browser-verification rows follow the established validator style. | Refers to a specific browser validator agent. The plugin ships only P:agents/idea-triage.md. D10 keeps "browser verification where there is a UI" as conduct. |
| G3:442-449 (C16, for reference) | A queued-phase review pack may edit other phases' lines. | Already not shipped per the trace. Not in these four documents. |

---

### 3. Dropped as history, worked example or repository-specific

| Source lines | What | Why |
|---|---|---|
| G8:1-13; G9:1-13; G13:1-13; G16:1-13 | Front matter | Repository metadata |
| G8:19-23 | "Extracted from the two builds…" plus the adoption decision record | Origin story; names prompts and a decision record |
| G8:28 | "Never called a workbench" | Repository product name |
| G8:37, 48, 85, 97 | "(precedent: PROMPT-NNN)" | Cut per the constraints |
| G8:78-80 | Pack-audit example with commit hash | Worked example and hash |
| G8:100 | "The workbench build's bounded enhancement lane is the model" | Repository example |
| G13:25-27 | "Extracted from PROMPT-036 on 2026-09-16…" | Origin story |
| G13:37-39, 54 | "The partition was designed twice"; cost of not answering | Narrative (embedded rule is D79) |
| G13:95-96 (AGENTS.md wording) | Names the repository's AGENTS.md bundling | Replaced by a pointer to protocol.md §12 (D91) |
| G13:99 (`dev`), 104-105 (`agent/build-b1`) | Repository branch names | Rewritten as `<integration branch>` and the protocol's naming |
| G13:154-157 | The four deviations PROMPT-036 names | Worked example |
| G13:167-169 (narrative) | Draft PROMPT-036 silent stop-gate | Narrative (embedded rule is D96) |
| G13:174-176 | PROMPT-036's completion ruling "the day before" | History |
| G13:242-244 | Schema-forbidden value anecdote | Worked example (rule is D107) |
| G13:245-247 ("authority it did not previously have") | Framing of review as a new condition | Now a general completion condition; pointer to backlog-protocol.md §10 |
| G13:256-257 | PROMPT-036 review findings count | Worked example |
| G16:20-24 | Code-based division of labour | Rewritten without codes (D78 and the batches preamble) |
| G16:35-38 | "Written on 2026-09-22 when abstracted out of PROMPT-036" | Origin story |
| G16:76-78 | "GOV-013's first lesson…" | Narrative cross-reference |
| G16:81-82 | "Two phases ranked ahead of it after its partition was checked" | Worked example |
| G16:95, 97-99 | "Nearly got wrong"; the `batch-002` / `sys-governance` example | Narrative and batch id |
| G16:102-103 | `tools/git-hooks/` vs `tools/` example | Repository path (rule D128 kept) |
| G16:163 | Idea `000316` | Idea id; the fact survives as D132 |
| G3:380-383 | `phase-part-01` / `PROMPT-034` acceptance failure | History |
| G3:390-394 (names) | `PROMPT-032` and the "precedent" argument | Worked example; the rule is kept in C14 |
| G3:396 (date), 398-399 | "Ratified 2026-09-14"; the rejected alternative | Date and history |

---

### 4. Conflicts and resolutions

1. **Whether the coordinator claims.** In prompt packs (G8:123) and research packs (G9:167) the coordinator claims nothing, but C20 (G3:491-496) and G13:111-112 have the coordinator claiming. I scoped each rule: D22 and D64 apply to a pack build, where the `K` dispatch claims; C20 and D92 apply to a coordinator running dispatch templates (D99). Each document says which case it covers.
2. **Adversarial review at stage 7: optional or mandatory.** G8:92-93 and G9:113-114 make it optional; G13:159-165 makes it mandatory. Stated as one absolute (D108): mandatory outside the pack pipeline, optional inside it (D17). The "deviation" framing is dropped.
3. **Ports.** G8:125 says "fixed ports", G13:107-108 says "explicitly chosen", and the plugin says "a free port chosen explicitly" (protocol.md §11). The plugin wording wins, by pointer.
4. **C20 against the plugin.** P:skills/session-start/SKILL.md:69-80 says "Stop until the answer comes back" with no batch exception. coordinator.md states C20 as the named displacement. session-start does not mention it; a pointer there is outside this family.
5. **Validator inputs against the session-close reviewer.** D24 forbids giving a validator the creator's rationale, but backlog-protocol.md §10 gives the completion reviewer "the record", which contains the session's Decisions. These are different roles, so D24 stays scoped to creator/validator pairs. The plugin's inconsistency is flagged, not resolved here.
6. **Where the coordinator's completion commit lands.** G13:111-112 puts claim and completion commits in the primary checkout. protocol.md §11 lists only the claim commit with its catalog regeneration and the fast-forward, yet backlog-protocol.md §10 and session-close step 7 put the completion edit "on the integration branch". D92 says "on the integration branch" and does not enumerate the checkout. The §11 enumeration omits the completion commit; that plugin gap is outside this family.
7. **Batch status on the integration branch against protocol.md §11.** Not shipped (section 2).
8. **The completion trap in the plugin.** G13:63 assumes completion needs a human. The plugin lets a coordinator complete via session-close, but condition 3 still needs the owner's integration yes for each phase. D81-D83 are worded so the trap holds whenever the owner is absent from integration.
9. **`max_active` defaults to 1** (backlog-protocol.md §2). D82 and D126 make every stage serial at the default. That is correct as stated; no change.
10. **Trace-table corrections.**
    - **C14:** the source is G3:384-392 plus 396-398, with the 396 date cut; 398-399 is the rejected alternative, which is history.
    - **C20:** also carries G3:494-495 ("skips, untouched, any phase a peer holds").
    - **C21-C23:** each merges with its G13 counterpart (125-126, 127-129, 135-142), so G13 does not produce a second copy.
    - All four destinations are confirmed as coordinator.md, and C14's as prompt-packs.md. Each C-id appears once.
11. **No tracker location.** G13:113 calls the tracker gitignored working state, but the plugin configures no tracker path. `staging_dir` is defined for partition drafts and corpora, so pointing the tracker there would reword a mechanism. D110 is conduct; a tracker location option could be added later.
12. **Rules that appear in several sources.** Selective injection, agent hygiene and cost protocols appear in G8, G9 and G13. Each is stated once (prompt-packs.md D21, D24-D28), and the other two documents point to it and add only their own specifics.
13. **Model names.** D26 and D66 name Haiku, Sonnet and Opus. They are kept because the plugin targets Claude Code. The alternative is tier wording ("the cheapest capable model / the standard model / the most capable model"), which is for the owner to choose.
14. **"Prefix-based" collision (G16:101).** The plugin's `path_conflict` compares path components, not raw strings. D128 says "path-component prefix", so `a/b` and `a/bc` do not collide.

## Family E: role contracts and review (GOV-014, GOV-018, PROMPT-038)

**Key facts that shape everything below:**
- **Gate labels.** The plugin does not define G1-G5 anywhere (a grep of P: finds none). Every gate is named by its role: the idea-approval gate, the partition-acceptance gate, the plan-approval gate, the integration gate and the completion gate.
- **Phase statuses.** The plugin has no `waiting` status (P:schemas/backlog.schema.json:122-129). Waiting is derived from a queued phase whose dependencies are incomplete (backlog-protocol.md §3).
- **Session budget.** `session_budget` is exactly 1 in the plugin (backlog-protocol.md §2).
- **Review records.** The plugin has no review-record directory, no findings schema and no read-only adversary agent type.

---

### 1. Rules per document

#### 1a. P:docs/role-contracts.md

**Section 1: What a contract is**

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| E1 | Each pipeline role has one contract: what it receives, what it produces, and what it never does. The never-do list is the binding half. | GOV-014:17-19, 23-24 | conduct |
| E2 | Capturing an idea is the owner's work, done in conversation. It is not an agent role and has no contract. | GOV-014:19-21 | P:skills/idea |
| E3 | Where a role has an agent definition, the contract is the authority and the definition is changed to match it. | GOV-014:25-27 | P:agents/idea-triage.md |

**Section 2: Owner-reserved decisions**

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| E4 | No contract grants an agent an owner-reserved decision. The reserved decisions are: idea approval and `lineage` annotations; partition acceptance; plan approval; ranking `next_up` and all cross-track priority; integration; edits to the agent instruction files; anything in the confidential directory. | GOV-014:33-37 (completion and `_working/` removed, see conflicts 1 and 13) | pointers: P:scripts/idea.py:425 and P:skills/idea/SKILL.md:76-78 (lineage); protocol.md §6 (plan approval); C15 in backlog-protocol.md §4; C18 in protocol.md §12; C13 in protocol.md §3; protocol.md §10 |
| E5 | Phase completion follows the three completion conditions. It is not a role's decision. | replaces the stale GOV-014:34 clause | pointer: C17 in backlog-protocol.md §10 |
| E6 | Every "proposes" in a contract names a proposal waiting for the owner's gate, never the decision itself. A role never describes its own output as accepted, approved or ratified. | GOV-014:37-39, 93-94, 158-159, 217-218 | conduct |
| E7 | An agent may write the following, always leaving an audit trail: finding annotations and the status moves the writer permits; draft documents; `depends_on` and `systems` on phases within an approved plan; commits on its own branch. | GOV-014:42-45 (run ledger dropped) | P:scripts/idea.py:425; protocol.md §11 |

**Section 3: The evidence rule**

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| E8 | A validator's verdict rests on tests and repository checks it ran in the worktree, with their real output captured. It never rests on asserted confidence or on what the code "should" do. A claim with no command behind it is not evidence. | GOV-014:49-51, 198-199 | conduct; P:skills/session-close/SKILL.md:75-77 |
| E9 | Every agent in the pipeline is the same underlying model. A validator that judges by impression shares the developer's blind spots. | GOV-014:51-53 | conduct (stated as the reason for E8) |

**Section 4: Roles (one subsection per role, each with inputs, outputs and never-do)**

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| **Triage** | | | |
| E10 | Inputs: one open idea's id, title and body, read through the writer's `show`; the search list; the literal read and write commands. | GOV-014:74-75 (adapted) | P:skills/idea-triage/SKILL.md:93-131 |
| E11 | Outputs: one finding annotation naming related plans, phases, documents and overlapping ideas, and asserting no decision about them. The dispatching skill moves the idea from open to triaged only after it has verified the finding. | GOV-014:76-78 | P:skills/idea-triage/SKILL.md:137-156 |
| E12 | Never-do: never conclude decline or merge; never write a link, only a `PROPOSED LINK:` line; never promote, only a `PROPOSED PROMOTION:` line; never run a writer command other than annotate; never invent a relationship it has not verified by reading the target. | GOV-014:79-83 | pointer: P:agents/idea-triage.md:54-65 |
| **Partition** (only if shipped, see section 2) | | | |
| E13 | Inputs: ideas at `triaged`, the partition pack and its corpus, and the trigger that starts the run. | GOV-014:90-91 | partition-sweep skill (not on this branch); P:plugin.json `staging_dir` |
| E14 | Outputs: a proposed partition record (tracks, member ideas, and a new-plan-or-amendment ruling per track). It stays a proposal until the owner accepts it at the partition-acceptance gate. | GOV-014:92-94 | same |
| E15 | Never-do: never accept its own partition; after an adversary blocker, never proceed without one revision cycle first; never treat agreement between proposal and adversary as the owner's acceptance. | GOV-014:95-97 | same |
| **Planner** | | | |
| E16 | Inputs: an accepted track or the owner's request; triage's findings and links for the member ideas, so the draft does not duplicate coverage triage already established; the plan-quality standard. | GOV-014:106-109 | P:docs/plan-review.md (plan-quality part) |
| E17 | Outputs: a requirement and plan pair per track that meets the plan-quality standard, with phases decomposed to one outcome and one session when drafted. | GOV-014:110-112 | pointers: protocol.md §4; backlog-protocol.md §5; P:skills/plan-check; P:templates/plan.md, requirement.md |
| E18 | Never-do: never approve the plan (plan-approval gate); never move an idea to `promoted`; never leave a phase table undecomposed for a later stage to split. | GOV-014:113-115 (code-allocation clause dropped, see conflict 3) | P:skills/idea-triage/SKILL.md:85-86 |
| **Adversary** | | | |
| E19 | Inputs: a requirement and plan pair, and the three-altitude review procedure. | GOV-014:123-125 | P:docs/plan-review.md; P:docs/adversary-prompt.md |
| E20 | Outputs: findings in its reply. Every finding reaches the review record and receives a disposition, including "accepted-no-change". None is silently dropped. | GOV-014:126-128; GOV-018:202 | conduct |
| E21 | Never-do: never approve the plan; never author the fix beyond naming the smallest change; never skip the later-added altitude because the first two came back clean. | GOV-014:129-132 | P:docs/adversary-prompt.md |
| **Phase-fit** | | | |
| E22 | Inputs: the plan and its dispositioned review record; the phase-splitting rule. Splitting a phase is a different act on a different object from decomposing an idea. | GOV-014:141-144 | pointers: backlog-protocol.md §14; vocabulary.md "Decompose" |
| E23 | Outputs: the final phase set, each phase within one session. A split phase goes back to review at the phase altitude before mapping. | GOV-014:145-146 | conduct |
| E24 | Never-do: never decompose an idea; never skip re-review after a split. | GOV-014:147-149 ("never register" dropped, see conflict 10) | conduct |
| **Mapper** | | | |
| E25 | Inputs: the final phase set. | GOV-014:155 | — |
| E26 | Outputs: phases carrying `depends_on` and `systems` that pass the check, and a proposed `next_up` order that stays a proposal until the owner ratifies, amends or rejects it at the plan-approval gate. | GOV-014:156-159 | P:scripts/check.py; P:scripts/checks/backlog.py; pointer to backlog-protocol.md §4 |
| E27 | Never-do: never rank `next_up` or set cross-track priority (C15); never register a phase the check rejects without revising first; after a second rejection, never proceed without escalating to the owner with the check output attached. | GOV-014:160-163 | pointer: C15 in backlog-protocol.md §4 |
| **Developer** | | | |
| E28 | Inputs: one claimed phase, in its own worktree. | GOV-014:169-170 | P:skills/session-start; pointer: C12 in protocol.md §11 |
| E29 | Outputs: a branch whose diff meets the phase's acceptance, ready for independent review. | GOV-014:171-173 | P:skills/checkpoint (pointer: C5 in backlog-protocol.md §9) |
| E30 | Never-do: never integrate its own branch (C18); never complete a phase on its own judgement (C6, C17); never write a confidential identifier into a tracked file; never edit the agent instruction files (C13); never touch the confidential directory. | GOV-014:174-178 | pointers: protocol.md §12, §10, §3; backlog-protocol.md §10 |
| **Validator** | | | |
| E31 | Inputs: the requirement or the phase's acceptance, and the diff. | GOV-014:186 | P:skills/session-close/SKILL.md:65-74 |
| E32 | Outputs: a pass or fail verdict under E8, with findings and the verbatim output of every verification command run. | GOV-014:190-192 | P:skills/session-close/SKILL.md:79-86 |
| E33 | Never-do: never accept the developer's rationale as evidence; never edit the diff or fix a finding; never mark a phase complete; never merge; never substitute "this looks correct" for a check it ran. | GOV-014:194-197 | conduct; pointer to backlog-protocol.md §10 |
| **Realization** | | | |
| E34 | Inputs: an integrated branch, its verification output, the completed phase, and the originating idea's text read through the writer's `show`. | GOV-014:214-215 | P:scripts/idea.py |
| E35 (C27) | Outputs: evidence as finding annotations, and a proposal, carrying the evidence, that the idea close as `delivered` with its `closes_with` pointer. The owner ratifies proposals in batch. | GOV-014:216-218; GOV-003:626-630 | P:scripts/idea.py:425; pointers: vocabulary.md Statuses (C24, C25), P:skills/idea (C26) |
| E36 | Never-do: never write the terminal status itself; never close an idea silently when the capability cannot be verified against the idea's text; record a finding the owner sees instead. | GOV-014:219-222 | conduct |

#### 1b. P:docs/plan-review.md (the three-altitude part only)

**Section: The review**

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| E40 | A plan review runs the plan-quality entry check, then an adversary attacks the plan at three altitudes: the plan against its requirement; each phase in isolation; each phase added after the plan, against the plan as it stands. | GOV-018:17-23 | conduct |
| E41 | The review produces one review record, holding the entry check's result and every finding with its disposition. | GOV-018:25-27 (location and schema not shipped) | conduct (conflict 7) |
| E42 | The adversary's contract is in role-contracts.md. This procedure does not restate it. | GOV-018:32-34 | pointer: role-contracts.md |

**Section: Who does what**

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| E43 | The dispatcher runs the entry check and writes the record when the draft is returned. | GOV-018:40 | conduct |
| E44 | The adversary writes nothing and reports its findings in its reply. | GOV-018:41 | P:docs/adversary-prompt.md |
| E45 | The dispatcher records the findings from the reply without changing any of them. | GOV-018:42 | conduct |
| E46 | The planner writes dispositions during revision. The owner writes them, at the plan-approval gate, for escalated findings only. | GOV-018:43 | conduct |

**Section: Step 1, the entry check**

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| E47 | The plan's section check runs before any adversarial time is spent. It reads headings only. | GOV-018:51-52 | P:skills/plan-check; P:scripts/plan_check.py |
| E48 | The entry check does not include the requirement's own section check. The adversary reads the requirement at the plan altitude. | GOV-018:92-93 | conduct |
| E49 | Pass (exit 0): record the entry check as `pass` and continue. | GOV-018:97 | plan-check exit codes |
| E50 | Returned (exit 1): the plan goes back to the planner with the check's output and no adversary is dispatched. The record is marked `returned`, with the missing sections, an empty list of altitudes run, and no findings. | GOV-018:98-101 | plan-check |
| E51 | A plan returned twice is escalated to the owner at the plan-approval gate. | GOV-018:101-102 | conduct |

**Section: Step 2, what each altitude covers**

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| E52 | Each altitude's target list is written into the record before dispatch. The adversary reviews what the record names. | GOV-018:110-111 | conduct |
| E53 | Plan altitude: the plan and the requirement it depends on. A child plan is its own target and gets its own review. | GOV-018:113-114 | conduct |
| E54 | Phase altitude: every phase whose `plan` is this plan, that was in the original phase set, with status `queued` or `blocked`. Active and complete phases are not reviewed, because a finding could no longer change them. | GOV-018:115-118 | backlog (conflict 4) |
| E55 | Later-added altitude: phases with the same `plan` and status filter, first registered in a later commit than the original set. The original set is the phases first registered in the same commit as the plan's earliest phases. The command is `git log --format='%h %ad %s' --date=short -S "id: <phase-id>" --reverse -- <backlog> \| head -1`. | GOV-018:119-128 | git |
| E56 | Once any later-added phase exists, the third altitude runs, even when the first two came back clean. | GOV-018:130-131 | conduct |
| E57 | The record lists the altitudes dispatched, so a skipped altitude shows as skipped rather than as clean. | GOV-018:131-133 | conduct |

**Section: Step 3, dispatch**

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| E58 | The adversary is dispatched with adversary-prompt.md, once per altitude, in a fresh agent that shares none of the planner's context. A read-only agent type is preferred when the repository defines one. | GOV-018:137-142, 144 | P:skills/session-close/SKILL.md:65-67 (same pattern) |
| E59 | Every placeholder is filled with an absolute path. | GOV-018:144 | conduct |
| E60 | If the phase altitude's phases do not fit in one dispatch, they are split across dispatches, each covering only the phase altitude. | GOV-018:144-146 (the numeric ceiling is dropped) | conduct |
| E61 | What each altitude attacks, in summary. Plan: coverage both ways, rejected alternatives named, failure paths, repository claims checked. Phase: one session, observable acceptance naming a failing case, verification that runs, declared `systems` and `deliverables`, `depends_on`. Later-added: no contradiction, no duplication, dependency order holds, the addition is explained in a record. | GOV-018:148-158 | pointer: adversary-prompt.md |

**Section: Step 4, recording**

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| E62 | Each finding in the reply becomes one record entry, numbered `F01` onwards in the order read. The record's status is `open`. | GOV-018:163-165 | conduct |
| E63 | The dispatcher copies the adversary's fields without editing them. It adds only the id and an author naming the agent type and the prompt. | GOV-018:167-168 | conduct |
| E64 | No finding is dropped at recording. A finding the dispatcher believes is wrong is recorded as reported, and the planner dispositions it `rejected`. | GOV-018:168-170 | conduct |
| E65 | `slug` and `aliases` are optional. The adversary proposes them when a finding looks like an instance of a recurring kind of defect. | GOV-018:172-174 | conduct |

**Section: Step 5, dispositions**

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| E66 | Every finding carries a disposition. Each disposition is appended to the finding's list, and the last one is current. | GOV-018:185-187 | conduct |
| E67 | The values, and what each `reason` must say: `fixed` (where the change was made: document and section, or backlog line); `accepted-no-change` (why no change); `rejected` (why, with evidence); `escalated` (what the owner must decide). | GOV-018:189-194 | conduct |
| E68 | The planner may write any of the four values. | GOV-018:196 | conduct |
| E69 | The owner writes a disposition only on a finding the planner escalated, and never writes `escalated`. | GOV-018:197-198 (schema enforcement not shipped) | conduct |
| E70 | There is one revision cycle. A blocker still unresolved after it is escalated. | GOV-018:200-201 | conduct |
| E71 | The adversary writes no disposition. | GOV-018:202 | conduct |
| E72 | When every finding has a disposition, the record is `dispositioned`. It goes with the plan to phase-fit, and its escalated findings go to the owner at the plan-approval gate. | GOV-018:204-206 | conduct |
| E73 | The revised plan does not get a second review. Blockers unresolved after the one cycle go to the owner. | GOV-018:208-209 | conduct |

**Section: Boundaries**

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| E74 | Splitting an oversized phase belongs to phase-fit, not to this procedure. | GOV-018:221 | pointer: backlog-protocol.md §14 |
| E75 | The procedure is run by hand, by a person or a session. | GOV-018:224-225 (the orchestrator clause is dropped) | conduct |
| E76 | The entry check is the plan-check skill, and no other checker exists. | GOV-018:226-227 | P:skills/plan-check |

**Queued-phase review sessions** (C16, see section 3)

| Rule | One-line absolute rule | Source | Plugin mechanism |
|---|---|---|---|
| C16 | A review session working under a prompt pack the owner approved may edit only the in-scope phases' lines, the backlog `updated` field, and the catalog regeneration that edit forces. | GOV-003:442-449 | conduct; pointer: prompt-packs.md |

#### 1c. P:docs/adversary-prompt.md (a template)

The document has four parts:
1. **Purpose** (from PROMPT-038:17-19): "The dispatch prompt for the adversary step of the plan review (`plan-review.md`). It is sent once per altitude to a fresh agent that shares none of the planner's context, preferably on a read-only agent type when the repository defines one. Everything specific to a plan review is in this prompt."
2. **How to fill it** (from 30-32): "Replace each placeholder and keep only the altitude section that matches `<altitude>`; delete the other two. Every path is absolute: the primary checkout and each worktree contain the same paths, so a relative path can send the adversary to the wrong tree."
3. **The placeholder table** (from 34-40, with four placeholders added).
4. **The template**, pasted below a horizontal rule.

The template text is the body of `PROMPT-038` (lines 46-138), shipped in `P:docs/adversary-prompt.md` with the source placeholder table extended by `<backlog>`, `<plans directory>`, `<decision record>` and `<idea log>`.

**Edits made to the source template:**
- **Lines 69 and 86:** the plan-quality codes "(`GOV-010` P2)" and "(`GOV-010` P6)" are removed.
- **Line 83:** "is 1 unless stated" becomes "is 1" (conflict 5).
- **Line 54:** "at G3" becomes "at the plan-approval gate".
- **Lines 50, 53, 74-75 and 105:** the hard-coded paths become the `<backlog>`, `<idea log>`, `<plans directory>` and `<decision record>` placeholders.

---

### 2. What executes each role in the plugin

| Role | Plugin mechanism | Recommendation | Reason |
|---|---|---|---|
| Triage | P:agents/idea-triage.md, dispatched by P:skills/idea-triage; P:scripts/idea.py `annotate` (restricted to `finding` at :425) and `status triaged` | **SHIP** | The contract matches the agent's never-do list line for line (agent :54-65). One difference: the plugin splits the output, so the agent writes the finding and the skill moves the status after verifying it. |
| Partition | Nothing on this branch. `staging_dir` (plugin.json:66-69) and the `partition` prerequisite feature exist but have no consumer; the partition-sweep skill is being built in parallel. | **NOT SHIPPED** on this branch; ship if the partition-sweep skill lands in the same release. | Every rule refers to a partition record, the pack and an adversary cycle, none of which exists here. The acceptance gate has no mechanism to point to. |
| Planner | Any session writing a plan: protocol.md §4, P:templates/plan.md and requirement.md, P:skills/plan-check, P:skills/next-code | **SHIP AS CONTRACT** | Conduct for any author, and the plugin has the supporting tools. The "never allocate a code" and "drafts land elsewhere" clauses are dropped (conflict 3). |
| Adversary | P:docs/plan-review.md and adversary-prompt.md (new in part two); dispatched as a fresh agent, the same pattern as session-close:65-67 | **SHIP** | The procedure and template are the mechanism. The plugin has no read-only agent type, so "read-only" is enforced by the prompt alone unless the repository defines such a type. |
| Phase-fit | backlog-protocol.md §14 (splitting); vocabulary.md "Decompose" for the idea-level contrast | **SHIP AS CONTRACT** | Splitting is conduct already described in §14. Only the re-review-after-split and never-decompose-an-idea clauses are new. |
| Mapper | P:scripts/check.py and P:scripts/checks/backlog.py validate `depends_on`, `systems` and cycles; backlog-protocol.md §4 (proposal only) and §5 (registration) | **SHIP AS CONTRACT** | The check is the validator the contract names. The escalation goes to the owner. |
| Developer | P:skills/session-start, P:skills/checkpoint, P:skills/session-close | **SHIP** | Claim, worktree, checkpoint and hand-off all exist. The never-do list becomes pointers to protocol.md §3, §10 and §12 and backlog-protocol.md §10. |
| Validator | P:skills/session-close step 3, an independent fresh-agent review with its own verification run (:65-86) | **SHIP AS CONTRACT** | The evidence rule and never-do list bind the session-close reviewer and any repository validator. The pipeline-only parts are not shipped: excluding the developer's rationale from the inputs, the second-rejection queue, and the owner's spot-audit. |
| Realization | No agent. The idea writer: `status delivered` needs `closes_with` (vocabulary.md), and an agent may write only findings (idea.py:425). | **SHIP AS CONTRACT** | Proposing a delivery with evidence is conduct any agent can follow. The owner writes the status. C28's ratification marker does not exist, so no proposed-state marker is described. |
| Per-dispatch token ceiling (300,000) | Nothing reads it. The only per-dispatch bound in the plugin is `maxTurns: 30` in P:agents/idea-triage.md:6. | **NOT SHIPPED** | GOV-014:58-68 exists so that an unbuilt spend enforcer can read it, and the figure is an unmeasured default. A ceiling that nothing enforces is inert. |
| Validator evidence rule (E8) | session-close:75-77 already requires the reviewer to decide "from the diff and its own run of the verification commands" | **SHIP AS CONTRACT** | Pure conduct, consistent with the existing skill. |
| Owner spot-audit (1 in 10; always audit a unit rejected once) | None: no completion sittings, no queue of passed validations | **NOT SHIPPED** | It needs a batch queue of validator passes. The general responsibility of reviewing evidence quality is C34 in protocol.md §7. |

---

### 3. Ledger rules that amend the role contracts or the review

| C-id | Destination (exactly one) | Reason |
|---|---|---|
| C5 | Pointer: backlog-protocol.md §9 | The Developer records progress with checkpoint, and checkpoint never completes a phase. |
| C6 | Pointer: backlog-protocol.md §10 | Developer and Validator never-do. |
| C12 | Pointer: protocol.md §11 | Developer input: its own worktree. |
| C13 | Pointer: protocol.md §3 | Owner-reserved list; Developer never-do. |
| C14 | prompt-packs.md | The adversary prompt is a single dispatch template, not a pack block, so the idempotency sentence is not added to it. |
| C15 | Pointer: backlog-protocol.md §4 | Mapper never-do and proposal; owner-reserved list. |
| C16 | **plan-review.md** | The trace names plan-review.md if the pack ships. It is conditioned on an owner-approved prompt pack, which part two's prompt-packs.md defines. It is the rule that lets a review session edit queued phases' lines. |
| C17 | Pointer: backlog-protocol.md §10 | Completion leaves the owner-reserved list; Developer and Validator never-do. |
| C18 | Pointer: protocol.md §12 | Owner-reserved integration; Developer and Validator never-do. |
| C19 | Not shipped (already, in part one) | The owner re-running close as an audit is forbidden by session-close. |
| C23 | coordinator.md | A blocker goes to an agent first, then to the owner with findings. It is the same shape as E51 and E70 but a separate rule, so it is not restated in plan-review. |
| C24 | Pointer: vocabulary.md Statuses | Realization's terminal state needs a pointer. |
| C25 | Pointer: vocabulary.md Statuses | `promoted` is not terminal (Planner and Triage never promote). |
| C26 | Pointer: P:skills/idea/SKILL.md | Realization corrects by a later event. |
| C27 | **role-contracts.md** (Realization, E35) | Propose with evidence; the owner ratifies in batch. Conduct: the writer does not enforce it. |
| C28 | Not shipped | The ratification marker does not exist in the plugin. |
| C34 | Pointer: protocol.md §7 | Evidence quality is a human-review responsibility, which is what remains of the spot-audit rule. |

---

### 4. Not shipped

| Source | Source rule, one line | Why |
|---|---|---|
| GOV-014:56-68, 86, 102, 119, 137, 151, 165, 182, 210, 224 | 300,000-token ceiling for every role and dispatch | No enforcement in the plugin (section 2). |
| GOV-014:88-102 | Partition role contract | No partition component on this branch (section 2). |
| GOV-014:111-113 | Planner drafts land in a staging location; the planner never allocates a code | The plugin has no plan-draft location, and next-code is the normal allocation path (document-codes.md §2). |
| GOV-014:147-148 | Phase-fit never registers a phase | The plugin registers phases in the same change as the plan (backlog-protocol.md §5). |
| GOV-014:175-176 | Run the staged confidentiality check tool before any push | The plugin ships no such tool; protocol.md §10's rule is pointed to instead. |
| GOV-014:177-178 | Never delete under `_working/` without approval | The plugin has no such directory concept. |
| GOV-014:45 | Run-ledger entries are agent-writable | The plugin has no run ledger. |
| GOV-014:186-189 | The validator never receives the developer's rationale | session-close hands the reviewer the session record by design. Carried as "never accepts rationale as evidence" (E33). |
| GOV-014:192-193 | On a second rejection the finding surfaces in the completion queue | The plugin has no queue. |
| GOV-014:200-204 | Owner spot-audits 1 in 10 passed validations; a once-rejected unit is always audited | No sittings and no queue (section 2). |
| GOV-018:25-30 | The record lives under the reviews directory, in the finding schema, read by the gate queue and the learning loop | None of these is in the plugin. |
| GOV-018:56-88, 90-92 | The entry-check shell script, and "it implements the table exactly" | P:scripts/plan_check.py is the mechanism (E47). |
| GOV-018:103-106 | "Exempt" outcome for plans written before a scope date | plan_check has no date scope. |
| GOV-018:138-142 | Dispatch on the `partition-adversary` agent type | The plugin ships no such type. |
| GOV-018:162-164 | Record path and `review_id` format | No record directory. The storage location is open (conflict 7). |
| GOV-018:167-168 | `engine: single-adversary` field | Only meaningful when more than one engine exists. |
| GOV-018:174-175 | The anti-pattern store matches an exact slug plus aliases | The plugin has no store. |
| GOV-018:177-181 | Validate the record with pytest | The plugin has no schema. |
| GOV-018:198-199, 204-205 | The schema rejects an owner's escalation, an ownerless escalation, and an undispositioned finding in a dispositioned record | The plugin has no schema; the rules are carried as conduct (E69, E72). |
| GOV-018:211-217 | Trio engines and the future format | The plugin has no trio. |
| GOV-018:222-223 | Anti-pattern store and gate queue boundaries | Components are absent. |
| PROMPT-038:17-19, 21-22 | Sent on `partition-adversary`; its charter is the source | The plugin has no such agent. The charter's two rules (verify claims yourself; rank blocker, major, minor) are already in the template body. |

---

### 5. Dropped as history or example

| Source lines | What | Why |
|---|---|---|
| GOV-014:1-13; GOV-018:1-13; PROMPT-038:1-13 | Front matter | Repository metadata. |
| GOV-014:18, 24, 31 | ARCH-006 citations; "reproduced verbatim" | Document codes; the content is kept. |
| GOV-014:24-25 | The dispatch adapter in PLAN-039.01 §8 | A repository plan. |
| GOV-014:38-40, 53-54, 186-187, 198 | REQ-022 R03, R13 and R23 test cross-references | Repository requirement ids. |
| GOV-014:58-68 | Why the ceiling exists; nothing measured; a later build will read it | Origin story (the rule is also not shipped). |
| GOV-014:84-85, 98-101, 116-118, 133-136, 150, 164, 179-181, 205-209, 223 | "Existing agent definition" bullets | Repository files, phases and idea ids. |
| GOV-014:109, 111-112, 125, 142-144, 147 | phase-idg and phase-irs references | Phase ids; the meaning is kept by role. |
| GOV-014:226-231 | "What this document is not" | Refers to repository phases and plans. |
| GOV-018:17-19, 51-52 | ARCH-006, GOV-010 and REQ-022 R09 citations | Codes; the content is kept. |
| GOV-018:45-47, 185-186 | "The owner's rulings of 2026-09-23 …" | Dated origin. |
| GOV-018:103-106 | PLAN-030 to PLAN-043 lack headings | Example (the rule is also not shipped). |
| GOV-018:113-114 | "for example PLAN-039.01 under PLAN-039" | Example; the rule is kept. |
| GOV-018:124 | `phase-irs-17` in the git command | Replaced by `<phase-id>`. |
| GOV-018:137-138 | "until the trio ships (phase-agx-11, -12)" | Old and future state. |
| GOV-018:164 | `2026-09-23-plan-039` | Review id example. |
| GOV-018:175 | "owner ruling, batch-005 Q1" | Origin. |
| GOV-018:221-225 | phase-irs-05/10/13 and PLAN-039.01 pointers | Phase ids; E74 and E75 keep the meaning. |
| GOV-018:229-235 | First run | Worked example; dropped by instruction. |
| PROMPT-038:21-26 | The pass on ARCH-006 by SESS-2026-09-15-13; prompt not saved | Origin footnote; dropped by instruction. |
| PROMPT-038:69, 86 | GOV-010 P2 and P6 | Codes; the content is kept. |
| PROMPT-038:105 | GOV-003 path | Replaced by `<decision record>`. |

---

### 6. Conflicts and how each was resolved

1. **Completion authority.** GOV-014:34, 175-176 and 195-196 make completion owner-reserved through the owner's `/session-close`.
   - **Resolved to C17.** Completion is removed from the owner-reserved list (E4), and E5 points to backlog-protocol.md §10. The Developer and Validator never-do lists say "never complete on own judgement" (C6), not "owner-only".
2. **Gate labels.** The source uses G2-G5 throughout, and the plugin defines none.
   - **Resolved:** each gate is named by its role. The ARCH-006 G5 row ("owner runs /session-close") is stale under C17; the completion gate means backlog-protocol.md §10.
3. **Planner "never allocate a code" and staging drafts** (GOV-014:111-113), against protocol.md §4 and document-codes.md §2, which allocate through next-code for any author.
   - **Resolved to the plugin:** both clauses are dropped. The coordinator should confirm this.
4. **The `waiting` status** (GOV-018:117) is not stored in the plugin.
   - **Resolved:** the filter is `queued` or `blocked`. `queued` covers both ready and waiting phases, because readiness is derived.
5. **`session_budget` "1 unless stated"** (PROMPT-038:83) against the plugin's "exactly 1".
   - **Resolved to the plugin:** "is 1".
6. **The entry-check script** (GOV-018:56-88) against P:scripts/plan_check.py, which carries the same headings and conditional sections (plan_check.py:40-47).
   - **Resolved:** point to the plan-check skill. The script and the date-based "exempt" outcome are not shipped.
7. **Review-record storage.** The plugin has no reviews directory or findings schema.
   - **Resolved partly:** the record's content, statuses (`open`, `returned`, `dispositioned`), fields and disposition rules ship as conduct.
   - **Open question:** where the record lives. The plugin's session record, a file in the document root, or a path the owner names are the candidates. I did not choose one.
8. **Validator inputs.** GOV-014:186-189 excludes the developer's rationale, but session-close:71 gives the reviewer the session record.
   - **Resolved to the plugin:** "never accepts rationale as evidence" is kept (E33). The input exclusion is not shipped.
9. **Who accepts findings.** Plan-review dispositions (`accepted-no-change` and `rejected` by the planner, GOV-018:196) seem to clash with U2 and C17 (only the owner accepts a review finding).
   - **Resolved as separate reviews:** C17 governs the completion review of a phase's diff. The plan-review record goes to the owner in full at the plan-approval gate. No change is needed; plan-review.md should state this in one line.
10. **Pipeline order.** GOV-014 has the Mapper register phases after review and phase-fit, but GOV-018:115 reads phases from the backlog and backlog-protocol.md §5 adds phases in the same change as the plan.
    - **Resolved to the plugin:** phases exist when the plan does. Phase-fit splits registered phases (§14), and the Mapper validates and proposes an order. Phase-fit's "never register" is dropped.
11. **Adversary outputs.** GOV-014:126 says the Adversary outputs findings "with each finding's disposition", but GOV-018:202 says the adversary writes no disposition.
    - **Resolved:** the adversary produces findings; the planner, and the owner for escalated findings, write dispositions (E20, E71).
12. **Triage trigger.** GOV-014:74 names an `idea created` event as the input, but the plugin runs triage when a person invokes the skill, one idea at a time, and the skill (not the agent) moves the status.
    - **Resolved to the plugin** (E10, E11).
13. **Repository paths in the owner-reserved and never-do lists.** `_working/` and the staged private-content tool are not plugin concepts, and the confidential directory is `{{confidential_dir}}`.
    - **Resolved:** `_working/` is dropped; the confidentiality rule points to protocol.md §10.
14. **C16 against checkpoint.** P:skills/checkpoint forbids touching another phase's lines, while C16 permits a review session to edit in-scope queued phases.
    - **Resolved:** no clash in practice. C16 governs a review session under an owner-approved pack, and checkpoint's rule governs progress recording. plan-review.md should say C16 does not widen what checkpoint writes.
15. **Read-only adversary.** GOV-018:139-140 relies on an agent type with no Edit or Write tools.
    - **Resolved:** the plugin enforces read-only by the prompt alone. E58 prefers a tool-restricted type when the repository defines one, using the same wording as session-close:66-67.
16. **Possible banned words in the rendered documents.** "replaces" must not appear in any new document (P:test/test_no_history.py). The same test forbids "incident", "until 20", "was broken" and "precedent".
    - The phase-id regex in P:test/test_no_source_references.py forbids a literal like `phase-x-1`, so the git command uses `<phase-id>`.
    - The idea-id regex forbids any standalone six-digit number, so the `300,000` figure must not appear in these documents. Being not shipped, it doesn't.

## Family E, plan quality standard (GOV-010)


Source file: /code/d-system-worktrees/phase-plug-09/docs/08-governance/GOV-010-plan-quality-standard.md (396 lines, read in full). Below, P: means /code/d-system-worktrees/phase-plug-09/plugins/idea-realization/. P:docs/plan-review.md does not exist yet.

#### 1. Rules

##### Suggested section: How a plan or requirement is judged

| Rule id | One-line absolute rule | Source | Mechanism |
|---|---|---|---|
| G1 | A plan or requirement is checked in two ways. First, mechanically, by its headings. Then by review, against the content judgements. | GOV-010:17-22 | The plan heading check: P:scripts/plan_check.py and P:skills/plan-check/SKILL.md. Required sections are stated in protocol.md §4 (P:docs/protocol.md:53-58). |
| G2 | The reviewer applies the content judgements after the mechanical check passes. | GOV-010:123 | conduct |
| G3 | Each judgement stands on its own. A document can meet one and fail another. | GOV-010:123-124 | conduct |
| G4 | The judgements cover plans and requirements only. Front matter and lifecycle are covered by protocol.md §5 and §6 and the check. Phase sizing is not covered. Whether a document still describes the system is not covered. | GOV-010:34-35, 45-51 | Pointer to P:docs/protocol.md §5-§7 |

##### Suggested section: Mechanical check

| Rule id | One-line absolute rule | Source | Mechanism |
|---|---|---|---|
| M1 | The required plan sections, their accepted headings and the two conditions under which extra sections are needed are those in protocol.md §4 and plan_check.py. They are not restated here. | GOV-010:55-94 | P:docs/protocol.md:53-56; P:scripts/plan_check.py:36-47, 79-88 |
| M2 | A plan starts from the plan template, which passes the check as shipped. A requirement starts from the requirement template. | GOV-010:32-37 | P:templates/plan.md; P:templates/requirement.md; P:skills/plan-check/SKILL.md:25-26 |
| G5 | The two investigation headings in the design section are for a plan whose outcome is the thing being investigated. Such a plan says why its later work is not yet specified. | GOV-010:91-94 | conduct. The headings themselves are at P:scripts/plan_check.py:38-39. |
| G6 | An open questions section with nothing open still appears and says so. It records any question that has already been settled as confirmed. | GOV-010:96-98 | conduct. P:templates/plan.md:45-46 says "None outstanding". |
| G7 | A requirement's rows form one table with three columns: an ID of the form `R01`, the observable behaviour, and the verification method. Every row has a non-empty verification cell. | GOV-010:109-112 | conduct. The table shape is at P:templates/requirement.md:26-28. No script checks it (see section 2). |
| G8 | Write an accepted-decisions section in a requirement when the owner has already ruled on choices the requirements depend on. | GOV-010:116-118 | conduct |

##### Suggested section: Content judgements for plans

All of these are applied by the reviewer, after G2.

| Rule id | One-line absolute rule | Source | Mechanism |
|---|---|---|---|
| P1 | The context names the observed problem (what went wrong or what is missing) and points to the record of it. **Fails when:** the context describes only the proposed solution, or it cites a prior finding without saying which part each step answers. | GOV-010:126-128 | conduct |
| P2 | Each decision names the alternative it rejected and what that alternative would have cost in this setting. **Fails when:** the reason is only a merit of the chosen option, the alternative is only implied, its cost is not stated, or no alternative appears. | GOV-010:140-143 | conduct |
| P3 | A settled decision is stated flatly, saying who ruled and when. An unsettled one is marked as a recommendation once, at the point it is made. The owner's words are quoted, not paraphrased, when they are the reason. **Fails when:** the document's status and its body disagree about whether something is settled, or the reader cannot tell who made a decision. | GOV-010:157-161 | conduct |
| P4 | Any claim about the current state of the repository comes with the command, file line or record that confirms it. **Fails when:** a fact about the repository, or about a capability, is asserted with no source. | GOV-010:174-177 | conduct |
| P5 | Scope states what is excluded and why. **Fails when:** there is no boundary, or scope lists only what is included. | GOV-010:187 | conduct. The heading is required by protocol.md §4. |
| P6 | Acceptance names the command or observation, the expected result, and at least one input that must be rejected. A plan paired with a requirement maps every requirement row to a step, and every step to a row. Any deliberate gap in the mapping is explained. **Fails when:** nothing states when the work is finished. | GOV-010:196-200 | conduct. The heading is required by protocol.md §4. |
| P7 | A plan that registers several phases states which can run at the same time. It works this out from each phase's declared `systems` and `deliverables`, and treats a shared system or deliverable as a collision. **Fails when:** the plan asserts the phases are independent without checking the declarations, or its own text contradicts that assertion. | GOV-010:211-214 | conduct. The same collision rule is at P:docs/backlog-protocol.md:105-106, and `ready` shows conflicts with active phases (P:docs/backlog-protocol.md:15-17). |
| P8 | Each open question says who decides it, when, and which way the author leans. **Fails when:** a question is bare, or has a deadline but no decider or leaning. | GOV-010:225 | conduct |
| P9 | A superseded passage is marked, dated and explained, and the old text stays readable. **Fails when:** the change carries no date; an edit makes a before/after record identical, so the change no longer shows; or an amendment is inserted between a sentence and the content it introduces. | GOV-010:237 | conduct |
| P10 | Every label is defined before it is used. A reader who was not in the session can follow the document from the repository alone. Document codes, phase ids and idea ids count as defined because each one resolves to a record. **Fails when:** labels are defined only in a source outside the repository, or some labels are defined while others are not. | GOV-010:248-250 | conduct |
| P11 | The work section states each step's prerequisites where the work is ordered, so the order can be checked, not assumed. **Fails when:** a dependency is shown only in a separate section, or not at all. | GOV-010:260-263 | conduct |

##### Suggested section: Content judgements for requirements

All of these are applied by the reviewer, after G2.

| Rule id | One-line absolute rule | Source | Mechanism |
|---|---|---|---|
| Q1 | The problem section names the observed failures and where each is recorded. **Fails when:** there is no problem section, or it describes what the work will do, not what problem it answers. | GOV-010:273 | conduct |
| Q2 | Each row states one observable behaviour. **Fails when:** one row bundles several independent deliverables or rules. | GOV-010:284 | conduct |
| Q3 | Verification is a procedure someone else can run. It names the input and the expected result, and where possible a control case that must not trigger. A row that no command can verify says so. **Fails when:** verification says "inspect" without saying what result passes, or gives a command that cannot run as written. | GOV-010:292-295 | conduct. The template's verification cell states this: P:templates/requirement.md:28. |
| Q4 | Rows state behaviour, not implementation, unless the owner ruled on the implementation. **Fails when:** a row names specific libraries or mechanisms and does not say that they were ruled on. | GOV-010:308 | conduct |
| Q5 | A boundary section says what each requirement does not require, ruling out readings a builder would otherwise have to guess at. An exclusion gives its reason. **Fails when:** there is no boundary section, or scope is stated only as a whole and says nothing about how individual rows may be read. | GOV-010:316 | conduct. The heading is at P:templates/requirement.md:30-32. |

##### Suggested section: Tone

| Rule id | One-line absolute rule | Source | Mechanism |
|---|---|---|---|
| T1 | Write the direct statement, not a metaphor. A metaphor carries connotations the author did not choose, and the reader has to translate it back into the claim. **Fails when:** a figurative line stands where a shorter literal statement is available. | GOV-010:327-330 | conduct |
| T2 | Do not repeat the front matter (status, dates) in the body, because the copy can disagree with the front matter the check reads. **Fails when:** status or date lines appear under the title. | GOV-010:340-345 | conduct |

##### Suggested section: Length

| Rule id | One-line absolute rule | Source | Mechanism |
|---|---|---|---|
| L1 | Length is not the measure of quality. A short plan passes when it is complete. A thin plan passes when it says why it is thin. | GOV-010:349-350 | conduct |
| L2 | A plan is too thin when it is short and also fails content judgements, such as P1 or P8. | GOV-010:357-358 | conduct |
| L3 | A plan is too long when it specifies contracts and structure for components that do not yet exist, ahead of demonstrated need. | GOV-010:359-362 | conduct |
| L4 | A plan is too dense when its cells or sentences compress reasoning that cannot be evaluated without the conversation that produced it. This is a P10 failure. | GOV-010:363-365 | conduct |

##### Suggested section: Optional sections

None of these is part of the mechanical check. Each is included only when its condition holds. A copy of one of these sections written by habit, without its condition holding, is a failure.

| Rule id | One-line absolute rule | Source | Mechanism |
|---|---|---|---|
| O1 | Known facts not to rediscover: list only facts the body does not already state. When nothing new remains, omit the section. | GOV-010:369-378 | conduct |
| O2 | Key references: list only links the reader needs that the body does not already give, each with a note saying what it is needed for. | GOV-010:379-385 | conduct |
| O3 | Sizing against a partition: include it only in a plan derived from an idea partition, and only to explain a difference between the partition's estimate and the phases registered. | GOV-010:386-390 | conduct |
| O4 | Deliverables: list what the work produces, each with what it is for. Do not list the plan itself, and do not list anything removed. | GOV-010:391-396 | conduct |

**When each rule is applied.** GOV-010 sets only one point: after the mechanical check passes (GOV-010:123). It does not say at which review altitude each judgement belongs; that comes from the three-altitude procedure the other analyst is extracting. A likely fit is:
- P1, P2, P3, Q1 and Q4 at the design or intent level.
- P5, P6, P7, P11, Q2, Q3 and Q5 at the scope, acceptance and structure level.
- P4, P8, P9, P10, T1, T2, L1-L4 and O1-O4 at the text level.

This split is my suggestion, not something GOV-010 states.

#### 2. Mechanical check differences

| GOV-010 says (line) | Plugin does (file:line) | Resolution |
|---|---|---|
| A requirement conforms when its required sections (Problem, Requirements, Boundaries) are present and its rows pass the row check (62-64, 100-114) | No script checks requirements. Only the template carries the headings (P:templates/requirement.md:20-32). protocol.md §4 states the content (P:docs/protocol.md:57-58). | Not mechanical in the plugin. Point to §4 and the template. The row form becomes reviewer conduct (G7, Q2, Q3). |
| Row check: `^\| R[0-9]+ \|`, at least one row, non-empty third cell (110-112) | None | Dropped as a mechanism. Its intent is kept as G7. |
| Accepted headings for requirement sections, including five alternative boundary headings (104-106) | No accepted-heading list for requirements. The template uses one heading per section. | Point to the template. Do not restate the list. |
| `Accepted decisions` is optional (107, 116-118) | Absent | Kept as conduct only (G8). |
| Shell form of the check, using awk and grep (66-70) | A Python script with a skill wrapper (P:scripts/plan_check.py:53-63, 79-88; P:skills/plan-check/SKILL.md:15-19) | Dropped. The plugin's script is the check. |
| The generic governance template is the starting file. Its four headings are accepted aliases (32-37). | The plugin ships its own plan template, which passes as shipped (P:skills/plan-check/SKILL.md:25-26; P:templates/plan.md:20-46). There is no generic-template alias logic. | Point to P:templates/plan.md. |
| A `depends_on` id is "resolved to its document" and its `kind` is read (86-88) | Kinds are read from every readable document under the document root (P:scripts/documents.py:334-348). An id that does not resolve, or a draft whose front matter cannot be read, adds no condition (P:scripts/plan_check.py:66-76, 84). | Plugin behaviour is the rule. No restatement needed. |
| No output or exit contract | Prints `<draft>: missing: <section>` or `<draft>: OK`. Exits 0 when every section is present, 1 when any is missing, 2 when a draft cannot be read (P:scripts/plan_check.py:19-20, 102-114). | Plugin is the rule. It is documented in the skill (P:skills/plan-check/SKILL.md:21-23). |
| Section names Context, Design, Work, Verification, Boundaries, Open questions, Requirement coverage, Concurrency (76-83) | The script uses the same names (P:scripts/plan_check.py:36-47). protocol.md §4 names them in prose: "context and scope, design, work and dependencies, acceptance and verification, out of scope, open questions… requirement coverage… execution order" (P:docs/protocol.md:53-56). | Wording differs but the content is identical. Point to §4. |
| Accepted headings and conditions (76-88) | Identical: same heading lists, same `phase-[a-z]+-[0-9]+` count of 2 or more outside fenced blocks, same `#{2,3} ` exact match, same fence toggle on lines starting with three backticks (P:scripts/plan_check.py:36-50, 58-60, 86) | No difference. |
| "Only one heading counts toward two sections: Requirement coverage" (59-60) | Structurally the same: `Requirement coverage` is in both the Verification list and the coverage list (P:scripts/plan_check.py:42, 46). | No difference. |
| Scope: applies only to documents written after a date; existing ones are not retrofitted (41-43) | No date scoping | Dropped (date-scoping clause). |

#### 3. Dropped

| Source lines | What | Why |
|---|---|---|
| 1-13 | Front matter | Belongs to the source document only. |
| 19-21, 22-25 | Named consumer agent, the requirement rows this standard satisfies, and the note about a judgement no single document meets | Source-repository codes and origin. The citation requirement no longer applies once the examples are dropped. |
| 27-28 | How the standard was derived (a corpus audit, phase, date) | Origin story, with a date. |
| 32-37 (partly) | "Does not rewrite or supersede the template" | Relation to a document the plugin does not have. The surviving rule is kept as M2. |
| 39-43 | Date-scoped applicability and retrofit clause | Date scoping. |
| 49-53 | Staleness is owned by another phase; the anti-pattern citation rule is owned by another phase | Phase and requirement codes. The surviving fact is kept in G4. |
| 66-70 | Shell one-liner | The plugin script is the check (section 2). |
| 92-94 | Two plans named as the example investigation and discovery plans | Worked example. The rule is kept as G5. |
| 96-98 | A plan named as the example of "None outstanding" | Worked example. The rule is kept as G6. |
| 112-114 | Which requirement documents use the row form, and one that uses a different form | Worked example and history. |
| 116-117 | Two requirements named as examples of accepted decisions | Worked example. The rule is kept as G8. |
| 122, 124 | "States the standard, then the documents…"; "Several documents are cited on both sides" | Describe the example structure, which is dropped. |
| 130-138 | P1 examples | Worked examples |
| 145-155 | P2 examples | Worked examples |
| 163-172 | P3 examples | Worked examples |
| 179-185 | P4 examples | Worked examples |
| 189-194 | P5 examples | Worked examples |
| 202-209 | P6 examples. The "explains a gap in the mapping" point is kept as part of P6. | Worked examples |
| 216-223 | P7 examples, including dated backlog observations | Worked examples and dates |
| 227-235 | P8 examples, including the note that no single plan meets all three parts | Worked examples |
| 239-246 | P9 examples | Worked examples. The failure modes are kept in the abstract. |
| 252-258 | P10 examples | Worked examples. The rule that ids count as defined is kept. |
| 265-269 | P11 examples | Worked examples |
| 275-282 | Q1 examples | Worked examples |
| 286-290 | Q2 examples | Worked examples |
| 297-306 | Q3 examples | Worked examples. The "cannot run as written" failure is kept. |
| 310-314 | Q4 examples | Worked examples |
| 318-323 | Q5 examples | Worked examples |
| 332-338 | T1 examples (quoted metaphors) | Worked examples |
| 342-345 (examples only) | T2 examples | Worked examples. The reason is kept. |
| 352-365 (examples only) | Named plans with word counts and quotes for each length category | Worked examples. The categories are kept as L1-L4. |
| 370-371 (partly), 374-396 (examples) | "Each has an example in the corpus…" and each Meets/Does-not bullet | Worked examples. The rule that a section copied by habit fails is kept. |

#### 4. Could not be stated abstractly without the example

- **P7 without examples.** It reads fine abstractly. But the rule that a shared system counts as a collision is cited from another plan in GOV-010 (220-222). In the plugin it rests on P:docs/backlog-protocol.md:105-106 instead. **The rule survives**, pointed at that line.
- **P8.** The source states it only through its three parts, because the examples split them up. The abstract form (who, when, leaning) is complete. **The rule survives.**
- **P9.** "Marked, dated and explained" requires a date inside the adopting repository's plans. That does not break the no-dates constraint, which governs the plugin document's own text. The rule tells plan authors to keep old text readable, which runs opposite to the owner's instruction for the plugin docs themselves. That instruction governs the plugin's docs, not the plans users write, so there is no conflict. **The rule survives**, but the writer should word it carefully so it is not read as applying to plan-review.md itself.
- **O3 (sizing against a partition).** It assumes the plugin has idea partitions. The plugin has a partition vocabulary (P:docs/vocabulary.md has lifecycle labels), but I did not confirm that the plugin ships a partition workflow. **The rule survives only if the plugin produces partitions; otherwise drop O3.** Needs checking.
- **L2 and L3.** Without examples these become generic. L3's "structure ahead of demonstrated need" is defined in GOV-010 only by a quote from another plan (361-362). The abstract wording above is my own. **Both survive.**
- **Nothing else** depended on its example.

## Family F: multi-session coordination (GOV-017, PROMPT-037)

G is `docs/08-governance/GOV-017-multi-session-coordination-protocol.md`, M is
`docs/02-prompts/PROMPT-037-session-manager-starter-messages.md`, L is the decision ledger
(`GOV-003`). Rule ids are the analyst's; the plugin location is `multi-session.md` and its section.

### multi-session.md

| Rule | Rule as extracted | Source | Plugin location | Mechanism |
|---|---|---|---|---|
| F1 | One session, the Session Manager, coordinates several interactive sessions: roles, the primary-checkout lock, claim slots, merge relay, message contract. | G:17-20 | preamble | procedure |
| F2 | The protocol is a procedure; the plugin supplies no lock, relay or messaging; the backlog is the only lock table. | G:227-228 | preamble | procedure; backlog-protocol.md §6 |
| F3 | Sessions message through the host's cross-session messaging by registered name; the protocol runs only where the host provides it. | G:90, 96-98; M:45-48 | preamble | host |
| F4 | protocol.md and backlog-protocol.md govern each session; this document governs turn-taking, only while sessions run under it. | G:22-23, 36 | preamble | pointer |
| F5 | The kickoff and starter messages are in session-manager-messages.md. | G:27-29 | preamble | pointer |
| F6 | coordinator.md governs one coordinator; this document governs several top-level sessions. | G:24-25 | preamble | pointer |
| F7 | Meta sessions never claim; execution sessions build. | G:56-57 | §1 | procedure |
| F8 | The seven role kinds and their claim slots. | G:59-68 | §1 table | procedure |
| F9 | The Session Manager holds the lock, allocates slots, relays merges, keeps the board. | G:61 | §1 table | procedure |
| F10 | Ideation records ideas and triages; the Prompt Planner writes prompts; neither builds. | G:62-63 | §1 table | procedure |
| F11 | The Batch Runner holds one slot; builders hold the rest. | G:64, 74-76 | §1 table | pointer coordinator.md, batches.md |
| F12 | The Standby Builder is first in line; until then it reviews queued phases. | G:67, 82-83 | §1 table | pointer plan-review.md §4 |
| F13 | The Scout is read-only: candidates, reconnaissance, worktree and branch audit. | G:68, 84-86 | §1 table | procedure |
| F14 | No reviewer session; each path's own review is the phase review; the merge-gate re-run covers peers' merges. | G:77-81 | §1 | backlog-protocol.md §10 |
| F15 | Sessions are addressed by registered name, set in the session's own terminal. | G:90-91 | §2 | host |
| F16 | Renaming leaves the listing reference unchanged; messages carry the sender's name. | G:96-97 | §2 | host |
| F17 | The first message asks the session to state its phase and agent id. | G:97-98 | §2 | procedure |
| F18 | One session writes in the primary checkout at a time. | G:102-103 | §3 | procedure |
| F19 | Any session may read in the primary checkout, including the check and the ready queue. | G:105 | §3 | P:scripts/check.py; P:skills/backlog |
| F20 | Writing needs `TURN?` with one purpose; do only that; leave `git status` clean; report the commit. | G:106-108 | §3 | procedure |
| F21 | The Session Manager confirms the checkout before granting and after the report. | G:109-110 | §3 | procedure |
| C29.1 | Ideation records ideas in the primary checkout inside an `idea` turn. | G:38-39; L:660 | §3, §7 | P:skills/idea |
| C29.2 | Reports go in the ignored report directory without a turn and are never committed. | G:40-42; L:661-662 | §3 | procedure |
| F22 | A `dryrun` turn runs a merged skill for evidence, ignored writes only, no commit. | G:204 | §3 | procedure |
| F23 | Merges go through `READY` and the merge gate, not `TURN?`. | G:204 | §3 | procedure |
| C30 | While sessions run under this protocol, no tests or rebuilds run in the primary checkout; the skills' preflight tests run in the worktree once it exists. | G:50-52, 111, 114-116; L:670-673; M:93-95 | §4 | procedure; P:skills/backlog and P:skills/session-start amended (owner ruling) |
| F24 | One test run at a time per worktree. | G:117-118; M:96 | §4 | procedure |
| F25 | The check is not a test run and runs in the primary checkout. | G:105, 168 | §4 | P:scripts/check.py |
| F26 | The Session Manager allocates `max_active` claim slots. | G:125 | §5 | backlog-protocol.md §6 |
| C29.3 | Builders build the phase the Session Manager assigns and never pick from the queue. | G:43-44, 125-126; L:663-664 | §5 | procedure |
| F27 | The Session Manager assigns the earliest ready phase with an empty Conflicts column. | G:126-128 | §5 | P:skills/backlog |
| F28 | The owner approves each assignment; the session-start claim question still goes to the owner. | G:128-129 | §5 | P:skills/session-start |
| F29 | The Conflicts column misses assigned-but-unclaimed phases and undeclared edits. | G:131-134 | §5 | backlog-protocol.md §7 |
| F30 | Scout reports cover both gaps; flagged pairs never run together. | G:133-135 | §5 | procedure |
| F31 | The Batch Runner sends `NEXT-BATCH` before opening another batch. | G:137-138 | §5 | procedure |
| F32 | The Prompt Planner sends `PROMPT-FOR`; the Session Manager checks the prompt. | G:138-140 | §5 | procedure |
| F33 | A branch integrates only with the owner's approval, relayed. | G:144 | §6 | protocol.md §12 |
| F34 | `READY` carries the review verdict (findings fixed or accepted by the owner) and the post-rebase gate output. | G:146-148 | §6 | P:skills/session-close |
| C31 | The gate is the check, the repository's tests and every further gate the working agreement names, each clean. | G:147-150; L:734-738 | §6 | P:scripts/check.py plus the repository's gates |
| F35 | The Session Manager re-runs the gate in a detached temporary worktree and removes it. | G:151-153 | §6 | procedure |
| F36 | The owner gets both gate results and the diff stat. | G:154-155 | §6 | procedure |
| C29.4 | `GRANTED merge` is the owner's approval for every session and hands over the lock. | G:45-47, 156, 173-174; L:665-666 | §6 | procedure; P:skills/session-start and session-close amended (owner ruling) |
| F37 | If the integration branch moved, rebase and re-run under the lock; the Session Manager re-runs before the fast-forward. | G:156-159 | §6 | procedure |
| F38 | The primary checkout is confirmed clean before the fast-forward. | G:160-163 | §6 | pointer backlog-protocol.md §11 (C32) |
| F39 | Fast-forward, completion edit with the catalog in one commit, check, `TURN DONE`, in one turn. | G:164-168 | §6 | P:skills/session-close; backlog-protocol.md §10 |
| F40 | After a merge the Session Manager sends `REBASE`. | G:171 | §6 | procedure |
| F41 | A failing commit hook is never bypassed. | G:180-182 | §6 | procedure |
| F42 | A session sends an idea to Ideation as `IDEA` and does not record it. | G:188-191; M:90-91 | §7 | procedure; reporting.md pointer |
| F43 | Ideation batches waiting ideas into one turn; recording before triage. | G:190-191, 193 | §7 | P:skills/idea |
| F44 | When nothing waits, Ideation triages open ideas the owner names, inside a turn. | G:191-193; M:202-206 | §7 | P:skills/idea-triage (owner ruling: the owner names them) |
| F45 | Ideation returns `IDEA-RECORDED` with the id from the writer's output. | G:193-194; M:199-200 | §7 | P:skills/idea |
| F46 | The first line of every message is its type and subject. | G:198-199 | §8 | host |
| F47 | The message types. | G:201-219 | §8 table | procedure |
| F48 | The board in the ignored report directory. | G:223-224 | §9 | procedure |
| F49 | Scout and Standby report locations. | G:224-226 | §9 | procedure |
| F50 | Board and reports are ephemeral; the backlog is the lock table. | G:226-228 | §9 | backlog-protocol.md §6 |
| F51 | Start or resume sequence. | G:230-237 | §9 | procedure |
| F52 | Backlog claims are authoritative over the board; unexplained claims are asked about, never released. | G:238-239 | §9 | backlog-protocol.md §8 |

### session-manager-messages.md

| Block | Source | Changes from the source |
|---|---|---|
| Introduction and placeholders | M:17-22 | Revision history (M:22-30) dropped; roster and paths made placeholders |
| Kickoff | M:34-50 | Reading list names the plugin's documents; commands named by skill |
| Shared contract | M:54-101 | `batch` turn purpose dropped (see below); gate stated generically (C31); clean-checkout confirmation stands in for the hook script; hook rule added to item 10 (F41) |
| Batch Runner | M:105-125 | Batch-table status commit dropped |
| Builder | M:127-149 | One text for every builder |
| Standby Builder | M:151-165 | Review points to plan-review.md §4 |
| Scout | M:167-185 | Unchanged apart from placeholders |
| Ideation | M:187-209 | Triage limited to ideas the owner names (owner ruling) |
| Prompt Planner | M:211-226 | Prompt code made generic |

### Family F: not shipped

| Source | Source rule | Why |
|---|---|---|
| G:147-150; M:78-80 | Named test, lint and type commands and their zero baselines | Repository tooling; stated as "the repository's tests and further gates" (C31) |
| G:105, 148, 167; M:43, 78, 86, 173 | The repository's governance command | The plugin's check, backlog queue and catalog skill |
| G:160-163; M:83-85 | The dirty-integration hook script exits 0 before the fast-forward | No such script in the plugin; the clean-checkout confirmation (C32) carries the rule |
| G:119-121; M:96-98 | Diff the tracked catalog before commits not meant to change it | Exists because this repository's tests overwrite the catalog; the plugin's check renders it in memory |
| G:182-184 | The pre-commit hook script and shared hooks path | The plugin ships no hook; F41 stays as conduct |
| G:48-49; L:667-669 (C29.5) | Batch-table status lines committed in a `batch` turn | The plugin's batches have no status fields and no location (batches.md; family D not-shipped rows) |
| G:72; L:675 | `max_active` value | Repository setting; the plugin states slots relative to `max_active` |
| G:59-68; M:59-63, 105, 127-132, 151-154, 167-170 | Session instance names and the two-builder count | The owner's instances; placeholders in the template |
| G:223-226; M:42, 157, 181 | The report directory's path in this repository | `<report directory>` placeholder |

### Family F: dropped

| Source | What | Why |
|---|---|---|
| G:1-13; M:1-13 | Front matter | Repository metadata |
| G:22-25, 33-36 | The "Departures from AGENTS.md" section | Dropped by instruction; its rules are C29.1-C29.4 and C30, stated as rules |
| G:31 | Date and occasion of writing | History |
| G:49, 139-140, 173-178, 192, 204 | Dated ruling markers and first-use notes | History |
| G:72-76 | A dated count of blocked phases | History; the slot split is kept |
| G:77-86 | Reasons each role exists | Rationale |
| G:91-94 | A dated report about renaming from a mobile client | History; F15 keeps the rule |
| G:112-114 | Overlapping test runs corrupting the catalog | History; C30 keeps the rule |
| G:162-163, 165-166, 182-184 | Document-code citations | Codes |
| G:168-170 | A skipped regeneration leaving the integration branch red | History with a hash and ids |
| M:22-30 | Revision history | History |
| M:41, 145 | Document-code citations | Codes |
| L:651-658, 675-680, 728-733, 743-747 | Ledger preambles | History |

### Family F: conflicts and how each was resolved

1. **C30 against the skills' preflight.** The `backlog` skill runs the repository's tests in the
   primary checkout, and `session-start` runs `backlog` first. Owner ruling: C30 is scoped to
   multi-session operation and both skills gain a clause moving the tests to the worktree under
   `multi-session.md`; a red worktree preflight hands the phase back as interrupted.
2. **C29.4 against the skills' "in this session".** Owner ruling: `session-start` and
   `session-close` accept approval "given in this session or relayed as `GRANTED merge` under
   `docs/multi-session.md`".
3. **Primary-checkout work list.** `protocol.md` §11 listed only the claim and the fast-forward; it
   also omitted the completion edit. Fixed in `protocol.md` §11, with a pointer to the turn
   purposes in `multi-session.md` §3.
4. **C31 scope (U4).** Multi-session only, stated generically; `protocol.md` §12 keeps "the check
   and the tests" for a single session.
5. **Who accepts a finding (U2).** The plugin's "accepted by the owner".
6. **Idea capture against `reporting.md`.** `reporting.md` gains a pointer: under
   `multi-session.md`, capture means sending `IDEA` to Ideation.
7. **Triage choice.** The `idea-triage` skill may not choose an idea. Owner ruling: Ideation
   triages only ideas the owner names.
8. **Batch turn.** Family D found batch tables have no status fields in the plugin, so the `batch`
   turn purpose and C29.5 are not shipped; `NEXT-BATCH` stays as a message.

## Ledger rules in part two

Every still-standing ledger rule that amends the role contracts or the review procedure appears in
exactly one of the nine documents, or is pointed to where part one placed it, or is not shipped:

| Rule | Where |
|---|---|
| C14 | prompt-packs.md §2 |
| C16 | plan-review.md §4 |
| C20, C21, C22, C23 | coordinator.md §5 |
| C27 | role-contracts.md §3, Realization |
| C29.1, C29.2 | multi-session.md §3 |
| C29.3 | multi-session.md §5 |
| C29.4 | multi-session.md §6 |
| C29.5 | Not shipped: the plugin's batch tables have no status fields |
| C30 | multi-session.md §4 |
| C31 | multi-session.md §6 |
| C28 | Not shipped (part one): no ratification marker exists |
| C5, C6, C12, C13, C15, C17, C18, C24, C25, C26, C34 | Pointed to in part one's documents (`protocol.md`, `backlog-protocol.md`, `vocabulary.md`, the `idea` skill); not restated |

## Changes made while writing

- **Model tiers.** D26 and D66 name models; `prompt-packs.md` §3 and `research-packs.md` §3 name
  tiers instead (owner ruling).
- **Token ceiling.** Not in `role-contracts.md` (owner ruling); family E section 2 gives the
  reasons.
- **Review record.** `plan-review.md` §3 places the record in the reviewing session's record (owner
  ruling), which settles family E conflict 7.
- **Partition role.** Family E recommended shipping the Partition contract only if the partition
  sweep is on the branch. Resolved after the rebase onto the partition-sweep phase; see
  "Partition role" below.
- **D17.** Its pointer is to D108 (coordinator.md §10), not D114; the analyst corrected it.
- **batches.md §3.** "A recorded check is history, not a licence" (D124) is stated as "evidence of
  its moment, not a licence", keeping the rule without history wording.
- **research-packs.md preamble.** "Research discipline replaces the build's standing rules" (D38)
  is stated as "stands in place of", to keep a word the history test forbids out of the plugin.
- **multi-session.md §3.** The `claim` turn purpose also covers a widening of a phase's
  declarations, which uses the same turn in practice. The `batch` purpose is not shipped (C29.5).
- **session-manager-messages.md.** Contract item 10 adds the never-bypass-a-hook rule (F41) so the
  template carries it.
- **role-contracts.md.** The Validator's input exclusion (never receives the developer's
  rationale) is not shipped, because the `session-close` reviewer receives the session record by
  design; "never accepts the rationale as evidence" stays. The Planner's "never allocates a code"
  and Phase-fit's "never registers a phase" are dropped (family E conflicts 3 and 10).
- **plan-review.md §2, P9.** Worded as a rule for the plans a repository writes, not for the
  plugin's own documents.

## Partition role

After the rebase onto the partition-sweep phase, the plugin carries the `partition-ideas` skill,
`P:docs/partition-pack.md` and the `partition-analyst` and `partition-adversary` agents. The
Partition contract (E13 to E15, `GOV-014`:88-102) therefore ships in `role-contracts.md` §3, and
family E's not-shipped row for it no longer applies. The plan quality standard's optional
"sizing against a partition" section (O3) applies for the same reason.

## Acceptance and verification

As the `phase-plug-09` backlog entry states. A reviewer reads each row's source passage and the
named plugin section and finds the rule present; `P:test/test_no_history.py` and
`P:test/test_no_source_references.py` pass over `P:docs/`, and the latter fails on a fixture naming
a prompt code.

## Out of scope

Families A to C (part one). `GOV-007` and `GOV-015`, excluded by the owner. This repository's own
governance documents.

## Open questions

- None open for this phase; the owner ruled on each question the analysts raised (see "Owner
  rulings").
