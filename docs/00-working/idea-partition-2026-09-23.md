<!-- partition-ideas: seed=1370316527 corpus_size=383 status=triaged -->

# Idea partition, 2026-09-23 corpus

- **Corpus:** 383 ideas, status filter `triaged`, manifest seed `1370316527`, corpus date 2026-09-23 (`_working/idea-corpus/manifest.json`).
- **State:** accepted by the owner at GATE 3, 2026-09-24, with the rulings recorded under *GATE 3 rulings*.
- **Built from:** `report-R1.md` (the owner-ordered re-run, which read the triage findings), `report-R4.md` (the control, which did not) and `audit-1-findings.md`, following `PROMPT-034` section S.
- **Record:** `docs/00-working/idea-partition-2026-09-23.json` carries the same tracks, groups and ids.

Ungoverned staging per `ADR-010`. Nothing here is recorded in `_data/ideas.jsonl`.

## How disagreements were ruled

R1 and R4 hold the same set of ideas in 23 fine groups; 18 of them stand unchanged here, and the other 5 were changed by the rulings their groups state (235 with 316, 346 into the harness group, 124 into slot and panel). Everywhere else, each divergence was ruled by the corpus links (`extends` and `supersedes` edges between ideas), `docs/08-governance/systems.yaml`, the documents the ideas name, and audit 1's per-divergence argument. Each group's **Basis** line says which. The rulings on audit 1's findings:

- **Finding A (000166 depends on 000020).** Placed together in *MCP-mediated access, enforcement harness and migration*.
- **Finding B (HTML generation merged with the workbench).** Split into two tracks, matching `sys-html` versus the `sys-wb-*` systems in `systems.yaml`.
- **Finding C (REQ-021 cited for independence it does not grant).** The explorer pages are not independent of HTML generation. REQ-021 gives the page decision to the idea programme and makes the pages consume the HTML-generation assets. The corpus also records an `extends` link between 000042 and 000302. So 000042 and 000299-000304 form one group in the idea track, with the HTML-generation library under **Precedes**.
- **Divergence 1 (one coordination programme or three).** Held as three tracks, as R1 had them, matching the separate `sys-backlog`, `sys-auto-gateway`/`sys-auto-ledger` and `sys-realization` registrations. The 000385 anchor's mechanical gates go to governance checks, where they land in code; its design questions stay with realization.
- **Divergence 3 (000122).** Kept in the one-nominator decline tier with both readings, since the audit could not tell.
- **R1's in-document duplicates and miscounts.** Every id below appears once; R1's own corrections were applied before comparing.
- **Audit 2** (`_working/idea-corpus/audit-2-findings.md`) found no blocker and confirmed coverage and the decline tiers. Its two major and four minor findings were Basis lines that misstated which analyst held a group; every Basis line was then checked mechanically against both reports and corrected. No placement changed.

## Completeness arithmetic

- Corpus in: **383** (`manifest.json`; `corpus-R1.md` lists the same ids).
- Placed in fine groups: **371**, in 87 groups under 12 tracks.
- Unbatched: **12**.
- 371 + 12 = **383**. No id is in two places; every decline candidate is in a group or in the unbatched section.

## Level 2: the tracks

| Track | Ideas | Fine groups | Rough size |
|---|---|---|---|
| Idea system and knowledge retrieval | 59 | 12 | Large: roughly 12-16 sessions across its groups. |
| Agent engineering and review | 30 | 13 | Large: roughly 12-16 sessions. |
| MCP mediation and autonomous operations | 14 | 3 | Large: roughly 10-15 sessions. |
| Idea realization and multi-session coordination | 37 | 6 | Very large: roughly 20-30 sessions. |
| Concurrency, claims, backlog and git safety | 37 | 15 | Large: roughly 15-20 sessions. |
| Governance checks, document hygiene and the portable framework | 70 | 18 | Large: roughly 25-30 sessions, most of them small. |
| HTML generation and design system | 6 | 1 | 3 sessions. |
| Workbench and demo stage | 33 | 9 | Large: roughly 15-20 sessions. |
| Literature-review campaign follow-ups | 38 | 6 | Medium: roughly 5-7 sessions. |
| Consultant demo kit | 28 | 1 | Delivered. |
| Organisational data model and portfolio productivity | 18 | 2 | Large: roughly 10-15 sessions. |
| Standalone items | 1 | 1 | Small. |

## Level 1: the fine groups, by track

### T1. Idea system and knowledge retrieval

- **Members (59):** 000018, 000053, 000055, 000061, 000062, 000064, 000065, 000204, 000236, 000268, 000313, 000366, 000367, 000008, 000010, 000050, 000071, 000127, 000038, 000046, 000047, 000048, 000049, 000125, 000157, 000206, 000243, 000244, 000339, 000354, 000388, 000395, 000407, 000042, 000299, 000300, 000301, 000302, 000303, 000304, 000305, 000002, 000004, 000005, 000040, 000043, 000044, 000045, 000060, 000161, 000162, 000163, 000164, 000167, 000032, 000036, 000033, 000034, 000216
- **Why together:** Everything about the idea log itself (its schema, tooling, agents and the partition process run over it) and the knowledge layer agents search. R4 held these as one programme; R1 as two. Level 2 is readability's call, and one track keeps the count at twelve while the fine groups stay separate underneath.
- **Independence:** Against agent engineering: the planner and scribe agents here are idea-log roles, not general agent construction. Against idea realization: this track owns the idea log's schema and the partition workflow; the realization pipeline reads them and changes neither. Against HTML generation: the explorer-page group depends one way on its assets (see that group). One line elsewhere: no shared file.
- **Precedes:** None as a whole.
- **Size:** Large: roughly 12-16 sessions across its groups.

#### T1.1 Idea ontology, tags, link vocabulary and lifecycle status

- **Ideas (13):** 000018, 000053, 000055, 000061, 000062, 000064, 000065, 000204, 000236, 000268, 000313, 000366, 000367
- **Why together:** One design thread on what an idea node is: classification axes, tags, link types, and its terminal states. 313 is a dated recurrence of 053's gap; 366 and 367 specialise 018.
- **Independence:** All edit schemas/idea.schema.json and the fold, so they are not mutually exclusive of each other. R1 split 204 and 236 into their own group; R4 merged them. Merged here because the status enum and the link vocabulary live in the same schema file.
- **Precedes:** None.
- **Size:** 3-4 sessions.
- **Basis:** R4's merge, on the shared schema file

#### T1.2 Idea management umbrella, metrics and capture delegation

- **Ideas (5):** 000008, 000010, 000050, 000071, 000127
- **Why together:** 050 is the umbrella and the corpus records an extends link between 050 and 010; 008, 010 and 071 are the dashboard and metrics asks; 127 moves /idea capture into a subagent under the same umbrella.
- **Independence:** Touches the /idea skill and fold() reporting only. Independent of the ontology group: it reads the schema and adds no field.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** ruling: the 050-010 extends link joins R1's F5 and F8

#### T1.3 Idea planner and scribe agents, and the requirements-versus-plans process

- **Ideas (5):** 000038, 000046, 000047, 000048, 000049
- **Why together:** 046 depends on 047's rubric, 049 came from triage of 046, 048 is the capture-time counterpart, and 038 relates to 047 in the corpus.
- **Independence:** Idea-log roles writing to docs/01-plans staging; no shared file with general agent construction.
- **Precedes:** 047 before 046's build.
- **Size:** 2-3 sessions.
- **Basis:** R4's placement of 038 with 046-049, on the 038-047 link

#### T1.4 Partition process: pack reliability, harness constraints and thresholds

- **Ideas (10):** 000125, 000157, 000206, 000243, 000244, 000339, 000354, 000388, 000395, 000407
- **Why together:** The partition pack's own defect and method trail: the 2026-09-13 partition's errors (243, 244), the subagent write constraint (206, 339, 354, 407), the close-out of the batching pack (157), and when a cluster must go through partition-ideas (388, 395).
- **Independence:** Self-contained to PROMPT-034, the partition-ideas skill and tools/build_idea_corpus.py. 388 and 395 sit under the 000385 anchor, but their subject is this workflow, not the Session Manager.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** R4's grouping; 388 and 395 moved from R1's 385-anchor groups on subject; 205 held out at GATE 3

#### T1.5 Explorer pages decision and build

- **Ideas (7):** 000042, 000299, 000300, 000301, 000302, 000303, 000304
- **Why together:** 299 anchors five page and graph asks; the corpus records an extends link between 042 and 302, and 042 is the decision phase-idg-08 rules on.
- **Independence:** Not independent of HTML generation: REQ-021 states the relationship runs one way. Whether a page exists is this track's decision (042); any page built uses the HTML-generation assets. Placed here because REQ-021 gives the decision to this programme; the dependency is recorded under precedes, not argued away. This rules on audit 1's Finding C.
- **Precedes:** phase-idg-08's ruling on 042; then the template, component and palette library group.
- **Size:** 3-4 sessions.
- **Basis:** ruling: the 042-302 extends link and REQ-021's boundary

#### T1.6 The /idea workflow's unnamed temp-file location

- **Ideas (1):** 000305
- **Why together:** Singleton: the workflow mandates a temp file and names no directory.
- **Independence:** A one-line fix in the idea workflow; shares nothing with 306, found in the same investigation.
- **Precedes:** None.
- **Size:** Under 1 session.
- **Basis:** ruling: R1's split of 305 from 306

#### T1.7 Retrieval mechanisms

- **Ideas (7):** 000002, 000004, 000005, 000040, 000043, 000044, 000045
- **Why together:** The how-to-find-the-right-file cluster: search order, vector and RAG, graph databases, document databases. The ideas cite each other as companions.
- **Independence:** Can be built against today's flat files with no knowledge-architecture work done.
- **Precedes:** None.
- **Size:** 3 sessions.
- **Basis:** agree

#### T1.8 Knowledge-base architecture

- **Ideas (6):** 000060, 000161, 000162, 000163, 000164, 000167
- **Why together:** One knowledge-substrate design: ingestion, event log, classification axes for all knowledge, memory buckets, gated on the literature review's terminology map (167).
- **Independence:** Classification here is for the whole knowledge base; the ontology group's is idea-specific.
- **Precedes:** The literature review (complete).
- **Size:** 3 sessions.
- **Basis:** R4's set; R1's group also held 032, 036 and 166

#### T1.9 Provenance graph and recommendation calibration

- **Ideas (2):** 000032, 000036
- **Why together:** 036 extends 032: calibration measures against provenance.
- **Independence:** R1 folded these into the knowledge-architecture group; R4 kept them apart. Neither needs the other's schema, so the criterion separates them.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R4's split

#### T1.10 Temporal projection explorer

- **Ideas (1):** 000033
- **Why together:** Singleton: snapshot and diff over idea history.
- **Independence:** R1 paired it with 034 as the same shape of ask while stating different gates; shape is not a dependency.
- **Precedes:** The fold work (phase-idea-07, complete).
- **Size:** 1 session.
- **Basis:** R4's split

#### T1.11 Portfolio scenario simulator

- **Ideas (1):** 000034
- **Why together:** Singleton: scenarios over portfolio signals.
- **Independence:** Gated on sys-signals, which neither 033 nor anything else here needs.
- **Precedes:** Portfolio signals (sys-signals, planned) and real portfolio data.
- **Size:** 1-2 sessions once unblocked.
- **Basis:** R4's split

#### T1.12 Routing brain procedures into the sessions that need them

- **Ideas (1):** 000216
- **Why together:** Singleton. Its text calls the failure a routing problem, not a knowledge problem: nothing in a session's entry path surfaces brain/procedures/ by topic.
- **Independence:** The fix is in session context loading (sys-brain, sys-retrieval). R4 placed it with the catalog bug and R1 with the literature campaign, where it was observed; neither is where the fix lands.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** ruling: placed by where the fix lands

### T2. Agent engineering and review

- **Members (30):** 000078, 000079, 000080, 000081, 000082, 000072, 000073, 000074, 000075, 000097, 000136, 000138, 000139, 000169, 000077, 000054, 000215, 000241, 000396, 000397, 000009, 000012, 000014, 000051, 000346, 000196, 000126, 000069, 000306, 000086
- **Why together:** How agents in this repository are built, bounded, observed and reviewed, and the harness configuration they run under.
- **Independence:** Against MCP mediation: the enforcement harness (165) stays there because it is the mechanism for MCP-held access; the harness guardrails here are hooks and settings. Against idea realization and multi-session coordination: 082 (orchestration) stays here as a named sub-topic of the 078 umbrella, the one convergence audit 1 could not break. One line elsewhere.
- **Precedes:** None.
- **Size:** Large: roughly 12-16 sessions.

#### T2.1 Agent-engineering framework

- **Ideas (5):** 000078, 000079, 000080, 000081, 000082
- **Why together:** The 078 umbrella and its four named sub-topics.
- **Independence:** A framework question, not a specific agent to build.
- **Precedes:** None.
- **Size:** 2 sessions design.
- **Basis:** agree

#### T2.2 Lifecycle agent roster and deliberation trio

- **Ideas (4):** 000072, 000073, 000074, 000075
- **Why together:** 072 and its three named children, each useless alone by its own text.
- **Independence:** Specific agents, not the framework.
- **Precedes:** None.
- **Size:** 2 sessions.
- **Basis:** agree

#### T2.3 Anti-pattern tracking and delegation scoping

- **Ideas (4):** 000097, 000136, 000138, 000139
- **Why together:** 097 seeds anti-pattern capture, 138 formalises it, 139 extends it into a scoping method, 136 is the pack convention the corpus links to 139.
- **Independence:** R4 added 169 here; its links run to 127, 128, 165 and 168, not to this chain.
- **Precedes:** None.
- **Size:** 2-3 sessions.
- **Basis:** R1's grouping

#### T2.4 Ephemeral purpose-built agents

- **Ideas (1):** 000169
- **Why together:** Singleton lifecycle design for disposable agents.
- **Independence:** Linked to capture and coordination ideas, not to the scoping chain.
- **Precedes:** None.
- **Size:** 1-2 sessions design.
- **Basis:** R1's split

#### T2.5 Subagent truncation handling

- **Ideas (1):** 000077
- **Why together:** Singleton measured defect with its own fix surface.
- **Independence:** Ships with nothing else here.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R4's singleton; R1 paired it with 054

#### T2.6 Observability and telemetry

- **Ideas (1):** 000054
- **Why together:** Singleton umbrella; relates to 080 (sensors).
- **Independence:** R1 paired it with 077; a telemetry umbrella does not depend on a truncation fix.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** R4's split

#### T2.7 Review independence and model assignment

- **Ideas (4):** 000215, 000241, 000396, 000397
- **Why together:** 241 is the defect (review agents carry write tools), 396 its fix (dedicated validator types), 397 extends it to a different model, and 215 records which model ran, which 397 needs in order to be checked.
- **Independence:** R1 placed 396 and 397 under the 000385 anchor and 215 with the literature campaign; the anchor is a planning batch and 215's gap is in delegation packs generally. The fix lands in .claude/agents and the review dispatch.
- **Precedes:** None.
- **Size:** 2 sessions.
- **Basis:** ruling: 396 fixes 241, and 397 needs 215

#### T2.8 Independent adversarial session review

- **Ideas (1):** 000009
- **Why together:** Singleton.
- **Independence:** Reviews transcripts after the fact; no dependency on the validator-type fix.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R1's split

#### T2.9 Harness guardrails: hooks, settings and preflight

- **Ideas (4):** 000012, 000014, 000051, 000346
- **Why together:** 051 is the umbrella, 012 and 014 its children; 346 is a pre-tool hook and lands in the same settings and hooks files as 014's audit.
- **Independence:** R1 put 346 with autonomous operations and R4 with governance checks; both analysts agree on 051, 012 and 014. The shared hooks file decides 346.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** ruling: 346 shares the hooks configuration

#### T2.10 Background-dispatch worktree hang

- **Ideas (1):** 000196
- **Why together:** Singleton: EnterWorktree hangs silently in a background subagent.
- **Independence:** A harness defect; R4's claim-mechanics placement fixes nothing in the claim system.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R1's placement

#### T2.11 Commands, skills and agents audit

- **Ideas (1):** 000126
- **Why together:** Singleton bounded audit.
- **Independence:** 127 and 136 were found by it but fix other things (the idea skill, pack conventions).
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R1's split

#### T2.12 Provider portability of agent definitions

- **Ideas (2):** 000069, 000306
- **Why together:** 069 asks whether Claude Code stays a dependency; 306 is a dated instance: .codex/agents files with no binding to their .claude/agents originals.
- **Independence:** R4 put 069 with the portable framework, whose templates are governance documents, not agent definitions.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** R1's pairing

#### T2.13 Repo tracker and multi-repo memory agent

- **Ideas (1):** 000086
- **Why together:** Singleton.
- **Independence:** No internal reference; nothing depends on it.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** R4's placement; R1 nominates it for decline

### T3. MCP mediation and autonomous operations

- **Members (14):** 000020, 000151, 000156, 000159, 000160, 000165, 000166, 000031, 000326, 000333, 000028, 000029, 000030, 000349
- **Why together:** What lets agents act without a human watching: MCP-mediated file access and its enforcement, the capability broker, and the trigger gateway, run ledger and worker host (PLAN-032, sys-auto-gateway, sys-auto-ledger).
- **Independence:** Against concurrency and claims: 151 and 156 propose replacing the claim system through a service, which is this track's subject; the existing mechanism's hardening stays there. Against idea realization: which run ledger is canonical (349) is a real shared decision, recorded under precedes on both sides rather than claimed independent. systems.yaml registers sys-auto-gateway and sys-auto-ledger separately from sys-realization.
- **Precedes:** None as a whole.
- **Size:** Large: roughly 10-15 sessions.

#### T3.1 MCP-mediated access, enforcement harness and migration

- **Ideas (7):** 000020, 000151, 000156, 000159, 000160, 000165, 000166
- **Why together:** One design: whether agents read files directly or through MCP, its tool surface, the enforcement harness, the version-control request queue, and the one-time migration. 166's own finding states it depends on 020.
- **Independence:** R1 placed 166 with knowledge architecture and never argued the dependency on 020; this rules on audit 1's Finding A. Today's claim mechanics keep working whether or not this is built.
- **Precedes:** None.
- **Size:** 6-8 sessions.
- **Basis:** ruling: audit 1 Finding A

#### T3.2 Capability broker and its denial taxonomy

- **Ideas (3):** 000031, 000326, 000333
- **Why together:** 031 is the broker; 333 decides what it denies first; 326 is PLAN-032's coverage table left mapping REQ-017 rows the broker work changed.
- **Independence:** R4 folded 031 into the MCP group; the broker is registered work under PLAN-032 and needs no MCP surface.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** ruling: neither analyst held these three together; R1 had 031 alone and 326 with 333, R4 put 031 in its MCP group. Joined on subject: 326 and 333 are about the broker 031 is

#### T3.3 Trigger gateway, run ledger and worker host

- **Ideas (4):** 000028, 000029, 000030, 000349
- **Why together:** The deliberately sequenced trilogy (028 then 029 then 030), plus 349's ruling on which run ledger is canonical, which is 029's subject.
- **Independence:** R1 put 349 with orchestrator defects; its question is which ledger this group builds.
- **Precedes:** The broker (031).
- **Size:** 3-5 sessions.
- **Basis:** ruling: 349 decides 029's ledger

### T4. Idea realization and multi-session coordination

- **Members (37):** 000247, 000248, 000249, 000250, 000251, 000252, 000253, 000254, 000338, 000348, 000350, 000352, 000355, 000356, 000128, 000319, 000320, 000327, 000328, 000332, 000334, 000340, 000347, 000358, 000359, 000369, 000370, 000389, 000391, 000404, 000385, 000386, 000387, 000392, 000393, 000235, 000316
- **Why together:** The automated idea-realization pipeline (PLAN-039, sys-realization) and its interactive counterpart, the GOV-017 Session Manager roster, which 334 asks to carry onto the same stack, together with the 000385 anchor's design questions about both.
- **Independence:** Against MCP mediation and autonomous operations: see 349, recorded under precedes. Against concurrency and claims: ideas that extend the existing claim mechanism stay there even where the Session Manager restated them. Against governance checks: the mechanical gates proposed under the 000385 anchor land in src/governance and CI, so they go there; only the anchor's design questions stay here.
- **Precedes:** The run-ledger ruling (349) in MCP mediation and autonomous operations.
- **Size:** Very large: roughly 20-30 sessions.

#### T4.1 Realization system formalization and daemon reach

- **Ideas (4):** 000247, 000248, 000249, 000250
- **Why together:** 247 is the originating decision idea with four rounds of rulings; 248-250 are the three daemon-reach facets raised together.
- **Independence:** R1 split 247 from 248-250; the three facets extend the daemon 247 established.
- **Precedes:** None.
- **Size:** 2-3 sessions design.
- **Basis:** ruling: 248-250 extend 247

#### T4.2 Queued-phase review defects

- **Ideas (4):** 000251, 000252, 000253, 000254
- **Why together:** 251 anchors three defects the 2026-09-16 review of the queue from phase-irs-03 found outside its scope.
- **Independence:** Defects in specific phases, not in the orchestrator code.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** agree

#### T4.3 Orchestrator code defects

- **Ideas (6):** 000338, 000348, 000350, 000352, 000355, 000356
- **Why together:** Code-reading findings against the merged src/orchestrator/: dispatcher, exception boundary, unit graph, lock scoping, and PLAN-039.01's stale wording.
- **Independence:** Patches code this track produced.
- **Precedes:** None (the code has landed).
- **Size:** 2-3 sessions.
- **Basis:** R4's set. R1 held 349 here and 338 alone; 349 is ruled to the run-ledger group, and 338 (PLAN-039.01's wording against the shipped dispatch gate) was found in the same code reading

#### T4.4 Session Manager roster, state and messaging

- **Ideas (16):** 000128, 000319, 000320, 000327, 000328, 000332, 000334, 000340, 000347, 000358, 000359, 000369, 000370, 000389, 000391, 000404
- **Why together:** The GOV-017 roster, its anchor (347), its role additions, state and resumability, the always-on broker question, multi-provider and LangGraph carry-over, the message log and board protocol, relay integrity, and alignment of /session-start with the merge gate.
- **Independence:** R1 split these into seven groups; all of them change GOV-017 and PROMPT-037, so they are not mutually exclusive. R4's single group holds.
- **Precedes:** None.
- **Size:** 8-10 sessions if formalised.
- **Basis:** R4's grouping, on the shared protocol documents

#### T4.5 Orchestration shape and assurance: the 000385 anchor's design questions

- **Ideas (5):** 000385, 000386, 000387, 000392, 000393
- **Why together:** The anchor and the structural questions it names: per-purpose orchestrators, review-discipline drift, an assurance subsystem separate from delivery, and mechanical coordination as code.
- **Independence:** The anchor's mechanical-gate members are placed with governance checks, where they land; this group is the design session.
- **Precedes:** None.
- **Size:** 1 planning session, then scoped.
- **Basis:** ruling: anchor design questions only

#### T4.6 Batch and wave coordination packs

- **Ideas (2):** 000235, 000316
- **Why together:** 235 generates coordinator packs from the backlog; 316 enforces the batch-table schema those packs and GOV-016 produce.
- **Independence:** R4 names 235 as what 316 validates; R1 held them as separate singletons.
- **Precedes:** Accurate collision detection (the lock-check group).
- **Size:** 1-2 sessions.
- **Basis:** ruling: R4's stated dependency

### T5. Concurrency, claims, backlog and git safety

- **Members (37):** 000025, 000041, 000152, 000168, 000368, 000390, 000153, 000154, 000158, 000283, 000318, 000280, 000288, 000217, 000285, 000027, 000239, 000242, 000245, 000321, 000322, 000336, 000398, 000234, 000284, 000037, 000224, 000240, 000011, 000403, 000066, 000091, 000021, 000058, 000059, 000286, 000323
- **Why together:** The existing claim, worktree and lock mechanism (sys-backlog, ADR-003) and the git rules around it: recovery, registries, identifier allocation, lock-check blind spots, backlog writes, and branch protection.
- **Independence:** Against idea realization: this track hardens the mechanism the Session Manager runs on; it does not design the Session Manager. Against governance checks: the catalog family and document drift touch different files. Against MCP mediation: that track proposes replacing this mechanism; neither blocks the other.
- **Precedes:** None.
- **Size:** Large: roughly 15-20 sessions.

#### T5.1 Abandoned-claim recovery and clobbering prevention

- **Ideas (2):** 000025, 000041
- **Why together:** Sibling protocol gaps from one incident window.
- **Independence:** Recovery process, not what the lock check can see.
- **Precedes:** None.
- **Size:** 2 sessions.
- **Basis:** R1's split of R4's F3.2

#### T5.2 Worktree registry and responsibility inventory

- **Ideas (4):** 000152, 000168, 000368, 000390
- **Why together:** The same registry asked for three times (152, 368, 390), and 168's fuller inventory of what a worktree holds.
- **Independence:** R1 put 168 with the Session Manager; its links run to 151, 152 and 156 and its subject is the claim system.
- **Precedes:** None.
- **Size:** 2-3 sessions.
- **Basis:** ruling: 168 on its links

#### T5.3 Hand-off protocol drift

- **Ideas (2):** 000153, 000154
- **Why together:** One protocol drift and its derivable check.
- **Independence:** Session hand-off, not claims or allocation.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** R1's split

#### T5.4 Identifier-allocation collisions

- **Ideas (3):** 000158, 000283, 000318
- **Why together:** Idea ids, session codes, and --next-code's lack of a read-only form: sequential allocation from local state collides.
- **Independence:** R4 paired 318 with 312, the literature-campaign code collision it explains; 312's fix is a deliverable correction there.
- **Precedes:** None.
- **Size:** 2 sessions.
- **Basis:** R1's grouping

#### T5.5 Multi-machine and multi-developer claims

- **Ideas (2):** 000280, 000288
- **Why together:** 288 is the accepted design answering 280.
- **Independence:** Mostly ruled already.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** R1's split

#### T5.6 Long-lived shared branches versus the claim protocol

- **Ideas (2):** 000217, 000285
- **Why together:** 217 is the clash that fired at every un-integrated phase boundary of the literature campaign; 285 is the never-remove-this-worktree exception it forced.
- **Independence:** R4 split them across two programmes. The campaign is closed; the lasting question is an exception to the claim protocol, which is this track's mechanism.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** ruling: R1's pairing, placed where the protocol lives

#### T5.7 Lock-check blind spots and declared-path enforcement

- **Ideas (8):** 000027, 000239, 000242, 000245, 000321, 000322, 000336, 000398
- **Why together:** Ways the lock check misses a real collision or mismeasures a declaration: candidate-versus-candidate, glob deliverables, cross-system overlap, deliverables' two meanings, and the commit-time check that a diff stayed inside its declared paths (027, extended by 398).
- **Independence:** All change src/governance/backlog.py's collision logic or what it compares. R1 put 398 under the 000385 anchor; both analysts tie it to 027.
- **Precedes:** None.
- **Size:** 3-4 sessions.
- **Basis:** R4's grouping, less 234 and 284

#### T5.8 System decomposition for false mutexes

- **Ideas (2):** 000234, 000284
- **Why together:** sys-ui and sys-governance acting as global mutexes, fixed the same way.
- **Independence:** Edits systems.yaml, not the collision code.
- **Precedes:** None.
- **Size:** 2 sessions.
- **Basis:** R1's pair; R4 held it inside its lock-check group

#### T5.9 Backlog file shape and write safety

- **Ideas (3):** 000037, 000224, 000240
- **Why together:** Whether to split backlog.yaml, a whole-file-revert incident, and YAML-anchor corruption: all about how the file is written.
- **Independence:** R1 paired 037 with 011; splitting the file changes the sanctioned writer 224 and 240 need.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** R4's grouping

#### T5.10 Backlog review and re-prioritisation recipe

- **Ideas (1):** 000011
- **Why together:** Singleton process recipe.
- **Independence:** No code; no shared file with the writer.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** ruling: neither analyst held it alone

#### T5.11 Phase versus claim-free fix branch rule

- **Ideas (1):** 000403
- **Why together:** Singleton rule.
- **Independence:** A claim-protocol rule. R4 placed it with delivery gates and called the choice close; R1 here. Its own finding relates it to 000385 and says it must fit together with 000398, which is in this track's lock-check group.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R1's placement; a close call, listed in the residual

#### T5.12 Branch protection and push-rule wording

- **Ideas (2):** 000066, 000091
- **Why together:** The main/dev PR-gate decision and the push-rule wording are the same AGENTS.md passage.
- **Independence:** R1 split them across programmes; the shared passage decides.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R4's pairing

#### T5.13 Repository resilience and git tooling

- **Ideas (3):** 000021, 000058, 000059
- **Why together:** 059 extends 058 in the corpus; 021 (backup and recovery) relates to 058.
- **Independence:** R4 left 021 standalone.
- **Precedes:** None.
- **Size:** 2-3 sessions design.
- **Basis:** R1's grouping, on the links

#### T5.14 Accepted follow-ups from the 2026-09-19 reviews

- **Ideas (1):** 000286
- **Why together:** Singleton bundle: an AST backlog-writer check, the stale-claim sample bias, checkpoint routing.
- **Independence:** Backlog and claim items.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R1's placement

#### T5.15 phase-mem-01's missing deliverable path

- **Ideas (1):** 000323
- **Why together:** Singleton backlog-entry correction.
- **Independence:** The owner ruled to leave it as-is.
- **Precedes:** None.
- **Size:** Under 1 session.
- **Basis:** R1's placement

### T6. Governance checks, document hygiene and the portable framework

- **Members (70):** 000155, 000198, 000208, 000324, 000325, 000335, 000351, 000353, 000357, 000405, 000406, 000106, 000231, 000150, 000195, 000384, 000024, 000035, 000052, 000345, 000023, 000341, 000342, 000329, 000330, 000331, 000371, 000372, 000373, 000374, 000375, 000376, 000382, 000298, 000377, 000378, 000381, 000383, 000379, 000380, 000394, 000399, 000400, 000401, 000402, 000408, 000409, 000410, 000056, 000026, 000057, 000337, 000343, 000006, 000145, 000237, 000291, 000292, 000293, 000294, 000270, 000271, 000272, 000273, 000276, 000277, 000278, 000279, 000281, 000314
- **Why together:** Keeping the repository's own governed documents true and its checks honest (the catalog family, drift, glossary, private-content check, delivery gates), plus the portable framework and the session-taxonomy tooling that generalise the same documents. R1 held these as one programme; R4 split the framework out. One track keeps the count at twelve; the fine groups keep them apart.
- **Independence:** Against concurrency and claims: different files (catalog, glossary, governed prose versus backlog.py and backlog.yaml). Against the literature-campaign follow-ups: those edit research/literature-review and PLAN-023.03, which nothing here touches. The portable framework (sys-fw-*) produces documents for other repositories and changes no check here.
- **Precedes:** None.
- **Size:** Large: roughly 25-30 sessions, most of them small.

#### T6.1 Catalog print-versus-write and stdout contamination

- **Ideas (11):** 000155, 000198, 000208, 000324, 000325, 000335, 000351, 000353, 000357, 000405, 000406
- **Why together:** One mechanical defect (--catalog printing instead of writing, then warnings on stdout breaking the same test) found independently in at least five sessions, its concurrent-pytest corruption (324, 325), and append_idea.py leaving the tree red in the same way (155).
- **Independence:** 324 and 325 change the same catalog test; R1 separated them. 155 is drawn as the same defect shape inside 208's finding.
- **Precedes:** None.
- **Size:** 1-2 sessions remaining.
- **Basis:** R4's grouping plus 155 from R1

#### T6.2 Generated artifacts with no drift test

- **Ideas (2):** 000106, 000231
- **Why together:** The overview page and the glossary generator's count: a generator's output is not tested against its committed file.
- **Independence:** Different generators from the catalog.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R1's grouping

#### T6.3 Private-content check silent pass

- **Ideas (3):** 000150, 000195, 000384
- **Why together:** The same defect found three times: the check passes without checking outside the primary checkout.
- **Independence:** One tool and one rule.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R4's set; R1's group also held 157

#### T6.4 Schema, DDL and model drift

- **Ideas (4):** 000024, 000035, 000052, 000345
- **Why together:** 052 is the umbrella; 024 and 035 its members; 345 is a column the rebuild silently drops.
- **Independence:** Schema-to-DDL consistency only.
- **Precedes:** None.
- **Size:** 3-4 sessions.
- **Basis:** R1's grouping, less 381

#### T6.5 Registry and requirement freshness

- **Ideas (3):** 000023, 000341, 000342
- **Why together:** A governed registry or status note fell behind a real build three times.
- **Independence:** Document freshness, not lock correctness.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R1's grouping

#### T6.6 GOV-010 wording corrections

- **Ideas (3):** 000329, 000330, 000331
- **Why together:** Three defects from one verification pass on one branch.
- **Independence:** One document.
- **Precedes:** None.
- **Size:** Under 1 session.
- **Basis:** R1's group; R4 held the trio inside a nine-member stale-reference group

#### T6.7 Glossary protocol and terminology tooling

- **Ideas (7):** 000371, 000372, 000373, 000374, 000375, 000376, 000382
- **Why together:** One glossary scout's cluster, named in the corpus for one terminology session.
- **Independence:** R4 held all thirteen of that scout's findings as one group; the other six fix different documents.
- **Precedes:** None.
- **Size:** 3-4 sessions.
- **Basis:** R1's split

#### T6.8 Cross-document textual drift

- **Ideas (5):** 000298, 000377, 000378, 000381, 000383
- **Why together:** One document's prose disagrees with another's: main for dev, completion authority stated six ways, an enum mismatch, PLAN-005's retired workaround, and CLAUDE.md's stale lines.
- **Independence:** Text fixes; a general consistency check is the delivery-gates group's concern.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** R1's grouping plus 381

#### T6.9 Backlog README track-table gaps

- **Ideas (2):** 000379, 000380
- **Why together:** Missing track-prefix rows and small stale facts from the same scout.
- **Independence:** One README.
- **Precedes:** None.
- **Size:** Under 1 session.
- **Basis:** R1's split

#### T6.10 Delivery-safety gates in governance and CI

- **Ideas (8):** 000394, 000399, 000400, 000401, 000402, 000408, 000409, 000410
- **Why together:** Mechanical gates proposed under the 000385 anchor and the agentic-SDLC design: the GOV-018 entry check, a test run after every write to dev, executable acceptance with mutation checks, evidence tracing, cross-document consistency, and the diff, test-count and security gates.
- **Independence:** They land in src/governance and .github/workflows/ci.yaml (sys-governance, sys-delivery), not in the orchestrator or the Session Manager. R1 held them under the anchor; R4 here.
- **Precedes:** None.
- **Size:** 3-4 sessions.
- **Basis:** R4's placement

#### T6.11 Documentation-governance umbrella

- **Ideas (1):** 000056
- **Why together:** Singleton umbrella.
- **Independence:** R1 paired it with testing; documentation governance does not depend on a test runner.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R4's split

#### T6.12 Testing strategy and the frontend test gap

- **Ideas (2):** 000026, 000057
- **Why together:** 057 is the umbrella; 026 its concrete gap (no ts/ test runner).
- **Independence:** Test infrastructure only.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** R4's pair; R1's group also held 056

#### T6.13 Tag-category approval and confidential tags

- **Ideas (2):** 000337, 000343
- **Why together:** 343 applies 337's approval-path question to a confidentiality case: whether capture-derived tags belong in the tracked tags file.
- **Independence:** Both analysts pair them; R1 placed the pair with concurrency because approving a category locked all of schemas/. The subject is tag governance, not the lock.
- **Precedes:** None.
- **Size:** 1 session (both ruled).
- **Basis:** agree on the pair; R4's placement

#### T6.14 Document-code index widths

- **Ideas (1):** 000006
- **Why together:** Singleton audit.
- **Independence:** No shared file.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** agree

#### T6.15 A lighter planning-methodology tier

- **Ideas (1):** 000145
- **Why together:** Singleton: a named gap between ad-hoc sessions and full GOV-008 packs.
- **Independence:** R1 put it with the partition method; it is a governance-process question.
- **Precedes:** None.
- **Size:** 1 session.
- **Basis:** R4's placement

#### T6.16 Checkpoint and session-close for unclaimed sessions

- **Ideas (1):** 000237
- **Why together:** Singleton, delivered (99a0f5e).
- **Independence:** Session-record protocol only.
- **Precedes:** None.
- **Size:** Delivered.
- **Basis:** agree

#### T6.17 Session-taxonomy investigation tooling

- **Ideas (4):** 000291, 000292, 000293, 000294
- **Why together:** One investigation's four follow-ons (PLAN-042).
- **Independence:** Unique to the session-taxonomy analysis.
- **Precedes:** None.
- **Size:** 2-3 sessions.
- **Basis:** agree

#### T6.18 Portable-framework templates, schemas and starter kit

- **Ideas (10):** 000270, 000271, 000272, 000273, 000276, 000277, 000278, 000279, 000281, 000314
- **Why together:** The 2026-09-19 framework batch, rolling up to the starter kit (281) and its assembly gap (314); PLAN-040 and PLAN-041.
- **Independence:** Output is copied into other repositories; changes nothing here.
- **Precedes:** The component phases before assembly (314).
- **Size:** 4-6 sessions.
- **Basis:** R1's group; R4 added 069

### T7. HTML generation and design system

- **Members (6):** 000001, 000083, 000084, 000085, 000092, 000093
- **Why together:** The generation side (sys-html, PLAN-003, REQ-021): template families, components and palettes, the agent that maintains them, and fixture testing.
- **Independence:** Against the workbench: systems.yaml registers sys-html separately from the sys-wb-* systems, and the workbench already renders HTML with none of this built. R1 merged the two against its own fine-group text; R4 split them. This rules on audit 1's Finding B. Against the idea system: the explorer-page group consumes this track's assets one way (see that group).
- **Precedes:** None.
- **Size:** 3 sessions.

#### T7.1 Template, component and palette library

- **Ideas (6):** 000001, 000083, 000084, 000085, 000092, 000093
- **Why together:** 083 is the library, 084 and 085 extend it, 092 maintains it, 093 is a page built from it, 001 is its fixture question.
- **Independence:** Independent of the workbench panels.
- **Precedes:** None.
- **Size:** 3 sessions.
- **Basis:** agree

### T8. Workbench and demo stage

- **Members (33):** 000087, 000095, 000096, 000100, 000137, 000140, 000246, 000113, 000114, 000121, 000109, 000110, 000118, 000119, 000232, 000238, 000111, 000120, 000124, 000133, 000134, 000135, 000141, 000233, 000115, 000116, 000123, 000131, 000132, 000142, 000143, 000144, 000102
- **Why together:** Features, audits and defects in the workbench and demo stage (sys-wb-*, sys-demo-stage): the terminal, the HTML Viewer, the slot and panel system, and the owner-commissioned audits.
- **Independence:** Against HTML generation: see that track. One line elsewhere: ts/src/stage and src/api/routes for the workbench are unique to this track.
- **Precedes:** None.
- **Size:** Large: roughly 15-20 sessions.

#### T8.1 Terminal stability and flag-off noise

- **Ideas (7):** 000087, 000095, 000096, 000100, 000137, 000140, 000246
- **Why together:** The same terminal stack (sys-wb-terminal): the TOCTOU cap race, shell override, websocket close reasons, the outside-the-page interaction API, the unowned disconnect that cost a live demo, the owner's websocket learning project, and the flag-off probes from InjectionDropdowns.tsx.
- **Independence:** R4 held 087 alone and put 100 with the Viewer; 100's probes come from InjectionDropdowns.tsx, which systems.yaml lists under sys-wb-terminal.
- **Precedes:** None.
- **Size:** 3-4 sessions; 246 first.
- **Basis:** R1's grouping

#### T8.2 Terminal persistence and performance audits

- **Ideas (3):** 000113, 000114, 000121
- **Why together:** 113 audits persistence across shells; 114 is the general performance and caching audit; 121 sharpens 114's invalidation case.
- **Independence:** Audits, not the defect fixes above; R4 split 113 from 114.
- **Precedes:** None.
- **Size:** 2 sessions.
- **Basis:** R1's grouping

#### T8.3 HTML Viewer features

- **Ideas (6):** 000109, 000110, 000118, 000119, 000232, 000238
- **Why together:** One component (HtmlViewerRegion.tsx): new-tab open, markdown rendering, the extension and render-location decisions, image formats, directory stepping.
- **Independence:** 118 and 119 depend on 110.
- **Precedes:** 110 before 118 and 119.
- **Size:** 3 sessions.
- **Basis:** the core both hold; R4 added 100, R1 added 111 and 120

#### T8.4 Bookmark categories and the panel bridge

- **Ideas (2):** 000111, 000120
- **Why together:** 120 extends 111's grouping into the panel bridge's batch actions.
- **Independence:** Consumed by the File Browser and the Viewer; a cross-panel design, separate from the Viewer's own features.
- **Precedes:** None.
- **Size:** 2 sessions.
- **Basis:** R4's split

#### T8.5 Slot and panel architecture

- **Ideas (6):** 000124, 000133, 000134, 000135, 000141, 000233
- **Why together:** Geometry, content fit, multi-instance modularity, the configuration schema and maximize, with 124's vocabulary, which 133, 135 and 141 each say must settle first.
- **Independence:** A stated dependency joins 124 to the group; R4 kept it separate with a precedes note.
- **Precedes:** None.
- **Size:** 5-7 sessions.
- **Basis:** ruling: 124's stated precedence

#### T8.6 Workbench audits: duplication, structure and plan reconciliation

- **Ideas (3):** 000115, 000116, 000123
- **Why together:** The owner's 2026-09-11 audit batch, less 124.
- **Independence:** Audits inform later work; no build dependency.
- **Precedes:** None.
- **Size:** 2-3 sessions.
- **Basis:** R1's grouping, less 124

#### T8.7 Rotator variants

- **Ideas (2):** 000131, 000132
- **Why together:** Two variants of one panel.
- **Independence:** No shared file with the other groups.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** agree

#### T8.8 Ports and processes tooling

- **Ideas (3):** 000142, 000143, 000144
- **Why together:** Exploration, the companion app, and its packaging as a workbench sub-app.
- **Independence:** R4 placed it standalone; 144 packages it into the slot system.
- **Precedes:** The slot and panel architecture, for 144.
- **Size:** 2-3 sessions.
- **Basis:** R1's placement

#### T8.9 Demo-stage residuals

- **Ideas (1):** 000102
- **Why together:** A rehearsal-only suggestion that records a demo artifact rather than asking for a build.
- **Independence:** No shared file with the other groups.
- **Precedes:** None.
- **Size:** Under 1 session.
- **Basis:** R1's pairing; 089 held out at GATE 3

### T9. Literature-review campaign follow-ups

- **Members (38):** 000147, 000148, 000149, 000197, 000199, 000200, 000202, 000211, 000212, 000213, 000221, 000289, 000295, 000307, 000201, 000214, 000218, 000219, 000220, 000227, 000228, 000297, 000225, 000226, 000229, 000230, 000203, 000209, 000210, 000296, 000308, 000309, 000310, 000311, 000312, 000287, 000315, 000344
- **Why together:** Defects and follow-through from the closed PLAN-023 campaign: the evidence contract, the gate, its deliverables, and the recommendations with no consumer.
- **Independence:** Self-contained to research/literature-review/, PLAN-023.03 and PROMPT-029. The two analysts agree on the boundary. Against governance checks: nothing here touches a governance tool.
- **Precedes:** None; the campaign is complete.
- **Size:** Medium: roughly 5-7 sessions.

#### T9.1 Evidence-contract amendments

- **Ideas (14):** 000147, 000148, 000149, 000197, 000199, 000200, 000202, 000211, 000212, 000213, 000221, 000289, 000295, 000307
- **Why together:** Every member is a gap in PLAN-023.03's evidence contract: identifier format, source-type and phase values, line endings, delimiters, tokenisation, dedupe and collision rules, the ledger's write validation, and the second_review writer clause.
- **Independence:** R1 split these four ways and R4 eight ways. They amend one document, so they are not mutually exclusive of each other.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** ruling: shared contract document

#### T9.2 Gate-method defects and the deterministic-gate proposal

- **Ideas (8):** 000201, 000214, 000218, 000219, 000220, 000227, 000228, 000297
- **Why together:** The gate measured the wrong population and reported PASS or FAIL on it; 297 is the gate contract's own undercount.
- **Independence:** All in PROMPT-029's gate logic.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** R1's grouping, less 199 and 202 (moved to the contract amendments); 290 held out at GATE 3

#### T9.3 Pre-synthesis check-in rulings

- **Ideas (4):** 000225, 000226, 000229, 000230
- **Why together:** 230 anchors the rulings; 225 and 226 link to it in the corpus; 229 is one of its disputes.
- **Independence:** Already ruled; recorded for completeness.
- **Precedes:** None.
- **Size:** Record only.
- **Basis:** R1's grouping

#### T9.4 Source identity and inventory corrections

- **Ideas (5):** 000203, 000209, 000210, 000296, 000308
- **Why together:** Aggregator mis-records, inventory-versus-matrix disagreement, a wrong author slug, and the inventory desync measured twice (308 supersedes 296).
- **Independence:** Corrections to deliverables, not the contract.
- **Precedes:** None.
- **Size:** 1-2 sessions.
- **Basis:** R1's grouping, less 216

#### T9.5 Report-phase deliverable defects

- **Ideas (4):** 000309, 000310, 000311, 000312
- **Why together:** Found building the phase-lrr report: a stale preamble count, a deliverable-count wording bug, a misdescribed rendering risk, and an OPS-code collision.
- **Independence:** One phase's deliverables.
- **Precedes:** None.
- **Size:** Under 1 session each.
- **Basis:** R1's group; R4 split it across three groups

#### T9.6 Post-campaign follow-through

- **Ideas (3):** 000287, 000315, 000344
- **Why together:** Recommendations with no consuming phase, and the source-archival draft.
- **Independence:** Using the campaign's output, not fixing its instruments.
- **Precedes:** None.
- **Size:** 2-3 sessions.
- **Basis:** agree

### T10. Consultant demo kit

- **Members (28):** 000170, 000171, 000172, 000173, 000174, 000175, 000176, 000177, 000178, 000179, 000180, 000181, 000182, 000183, 000184, 000185, 000186, 000187, 000188, 000189, 000190, 000191, 000192, 000193, 000194, 000207, 000222, 000223
- **Why together:** The finance-transformation teaching kit (REQ-008, PLAN-024, phase-kit-01 to 08), already built.
- **Independence:** Self-contained; both analysts hold the same 28 ideas and audit 1 confirmed the boundary against sys-demo-kit.
- **Precedes:** None.
- **Size:** Delivered.

#### T10.1 Demo-kit anchor, components, fixture and rosters

- **Ideas (28):** 000170, 000171, 000172, 000173, 000174, 000175, 000176, 000177, 000178, 000179, 000180, 000181, 000182, 000183, 000184, 000185, 000186, 000187, 000188, 000189, 000190, 000191, 000192, 000193, 000194, 000207, 000222, 000223
- **Why together:** One anchor, its components, the fixture question, REQ-008's arithmetic defect, and the owner's replacement rosters.
- **Independence:** Every member extends 170; cutting one shrinks this plan rather than creating another.
- **Precedes:** None.
- **Size:** Delivered.
- **Basis:** R4's set; R1 held 207 apart

### T11. Organisational data model and portfolio productivity

- **Members (18):** 000257, 000258, 000259, 000260, 000261, 000262, 000263, 000264, 000265, 000266, 000267, 000364, 000365, 000022, 000360, 000361, 000362, 000363
- **Why together:** The owner's consulting data: the ARCH-010 organisational model and the productivity gaps caused by having no real records.
- **Independence:** No schema, file or code path shared with any other track; audit 1 confirmed the boundary (20 of 20 in both reports).
- **Precedes:** None as a whole.
- **Size:** Large: roughly 10-15 sessions.

#### T11.1 Organisational entity model and its plan

- **Ideas (13):** 000257, 000258, 000259, 000260, 000261, 000262, 000263, 000264, 000265, 000266, 000267, 000364, 000365
- **Why together:** ARCH-010's accepted batch, the opportunity entity it names (364), and the plan that would deliver it (365).
- **Independence:** R4 put 364 and 365 with the productivity gaps and flagged 365 as belonging here itself.
- **Precedes:** ARCH-010's open gates.
- **Size:** 6-8 sessions.
- **Basis:** ruling: R4's own flag on 365

#### T11.2 Portfolio core-entity productivity gaps

- **Ideas (5):** 000022, 000360, 000361, 000362, 000363
- **Why together:** 022's zero-records finding and the four gaps it exposed: API and UI, quick entry, reminders, external intake. Each links to 022.
- **Independence:** Operates on the four existing entities.
- **Precedes:** phase-cap-08 (seeding).
- **Size:** 4-5 sessions.
- **Basis:** R1's grouping

### T12. Standalone items

- **Members (1):** 000282
- **Why together:** Small items with no build system, plan or consumer in common with any other track or with each other. Grouped at level 2 for readability only.
- **Independence:** Each group is independent of every other track by construction.
- **Precedes:** None.
- **Size:** Small.

#### T12.1 External reference link

- **Ideas (1):** 000282
- **Why together:** Singleton saved link.
- **Independence:** Nothing to build.
- **Precedes:** None.
- **Size:** Under 1 session.
- **Basis:** agree

## GATE 3 rulings

The owner accepted the partition on 2026-09-24 and ruled on every decline candidate:

- **Declined:** 000102, 000282, 000086, 000140. They stay in their groups here; recording the decline in `_data/ideas.jsonl` is a separate, owner-directed step.
- **Held out of this partition, not declined:** 000015, 000016, 000017, 000089, 000122, 000146, 000205, 000255, 000256, 000290. Each moved to the unbatched section; groups left empty were removed (master data management, public presence, the non-web rebuild evaluation, the session-record correction convention).

## Unbatched

12 of 383. Two came through as R1's unbatched pair, each with a reason (R4 placed each as a singleton); the other ten are held out by the owner's GATE 3 ruling and are not declined.

- **000013** — R1: could land in agent engineering (command boundary), governance process, or standalone, with no argument for one strong enough to state. R4 placed it as a singleton. It is carried forward unbatched: it belongs with whichever track picks it up.
- **000068** — R1: its action (mine research/ for new ideas) is idea-system work and its motivation (feed the knowledge-architecture set) is retrieval work. R4 placed it as a standalone singleton. Carried forward unbatched for whichever group claims it.
- **000015** — Held out of this partition by the owner's GATE 3 ruling, 2026-09-24. Not declined: its idea-log status is unchanged.
- **000016** — Held out of this partition by the owner's GATE 3 ruling, 2026-09-24. Not declined: its idea-log status is unchanged.
- **000017** — Held out of this partition by the owner's GATE 3 ruling, 2026-09-24. Not declined: its idea-log status is unchanged.
- **000089** — Held out of this partition by the owner's GATE 3 ruling, 2026-09-24. Not declined: its idea-log status is unchanged.
- **000122** — Held out of this partition by the owner's GATE 3 ruling, 2026-09-24. Not declined: its idea-log status is unchanged.
- **000146** — Held out of this partition by the owner's GATE 3 ruling, 2026-09-24. Not declined: its idea-log status is unchanged.
- **000205** — Held out of this partition by the owner's GATE 3 ruling, 2026-09-24. Not declined: its idea-log status is unchanged.
- **000255** — Held out of this partition by the owner's GATE 3 ruling, 2026-09-24. Not declined: its idea-log status is unchanged.
- **000256** — Held out of this partition by the owner's GATE 3 ruling, 2026-09-24. Not declined: its idea-log status is unchanged.
- **000290** — Held out of this partition by the owner's GATE 3 ruling, 2026-09-24. Not declined: its idea-log status is unchanged.

## Decline candidates

Nominations only. The owner rules on each one individually at GATE 3; nothing here changes an idea's status.

### Nominated by both

- **000102** — R1: a rehearsal artifact, not a feature ask; its text marks it as part of the demo record. R4: it states it is a fabricated rehearsal entry; nothing to build. Owner ruling at GATE 3: declined.
- **000282** — R1: a saved external link, not a proposal; brain/entities/ could hold it. R4: no proposed system change; close as a reference note. Owner ruling at GATE 3: declined.

### Nominated by one

- **000086** (R1) — Speculative cross-repository tooling; its triage found no internal reference to the tool it names and no repos domain in the schema. Owner ruling at GATE 3: declined.
- **000140** (R1) — The owner's own learning project, not a system deliverable; better served outside the backlog. Owner ruling at GATE 3: declined.
- **000255** (R1) — ARCH-010 marks the MDM system future work, parked; premature while the entities it would steward have no records. Owner ruling at GATE 3: held out of this partition, not declined.
- **000256** (R1) — A stewardship agent for a system (000255) and data that do not exist yet. Owner ruling at GATE 3: held out of this partition, not declined.
- **000290** (R1) — Soft decline: the campaign that motivated it is closed; a general gate-runner would be a different, unscoped idea. Owner ruling at GATE 3: held out of this partition, not declined.
- **000089** (R4) — The seeded content is live and will not be reverted; resolved in substance. Owner ruling at GATE 3: held out of this partition, not declined.
- **000205** (R4) — A measured result already folded into practice; nothing to build. Owner ruling at GATE 3: held out of this partition, not declined.
- **000015** (R4) — No follow-up across the corpus. Audit 1: R4 lacked the owner's 2026-09-13 ruling that dormancy is not deadness for this trio, which R1 cited in declining to nominate it. Owner ruling at GATE 3: held out of this partition, not declined.
- **000016** (R4) — As 000015: nominated for an explicit ruling. Audit 1 notes the 2026-09-13 ruling R4 could not see. Owner ruling at GATE 3: held out of this partition, not declined.
- **000017** (R4) — As 000015: nominated for an explicit ruling. Audit 1 notes the 2026-09-13 ruling R4 could not see. Owner ruling at GATE 3: held out of this partition, not declined.
- **000122** (R4) — Speculative, no trigger named, and the stack has been built on since. R1 declined to nominate it as strategic due diligence that is early, not stale. Owner ruling at GATE 3: held out of this partition, not declined.
- **000146** (R4) — The ruling it depends on is made; what remains is a one-sentence correction whose own text asks whether it should be made. Owner ruling at GATE 3: held out of this partition, not declined.

## Residual: placements made with less confidence

- **000157** — its items are the batching pack's close-out and the private-content bug (000150's family). Placed with the partition process by its title; the bug item is already tracked in *Private-content check silent pass*.
- **000216** — placed in retrieval, where neither analyst put it, because the fix lands in session context loading.
- **000403** — R4 called its placement close; placed with claims on its own finding's tie to 000398.
- **000346**, **000069** and **000306**, **000168**, **000100** — each ruled between the analysts on a shared file or the corpus links, as their Basis lines say; a planner could reasonably move any of them.
