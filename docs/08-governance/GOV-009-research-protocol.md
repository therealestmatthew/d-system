---
schema_version: 1
id: doc-research-protocol
code: GOV-009
title: Research pack protocol — the two-session methodology for literature review and research campaigns
kind: governance
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-governance, sys-backlog]
depends_on: [doc-prompt-pack-protocol]
---

# Research pack protocol — the two-session methodology for literature review and research campaigns

A **research pack** is the complete governed artifact set a research campaign runs from: a scope
record, a hypothesis register, a search-domain matrix, a delegation pack of pre-crafted search,
extraction and review prompts, a coordinator prompt and a kick-off record. This document is the
standard procedure for manufacturing and spending one. It applies the prompt-pack planning
protocol ([GOV-008](GOV-008-prompt-pack-protocol.md)) to research work: the pipeline and gates
are the same shape; the standing rules are replaced by research discipline.

This protocol governs **process** — sessions, gates, reviews, sign-offs. The **content**
methodology — what to search, how to score overlap, what a valid evidence row contains — already
exists in the research directory and is not restated here:

- the adversarial review instructions (`research/literature-review/CLAUDE.md`) — mission, null
  hypothesis, the hypothesis set under attack, search domains, scoring, deliverables;
- the search protocol (`research/protocols/literature_review_protocol.md`) — research questions,
  search strategy phases A–E, inclusion/exclusion, the four-pass workflow;
- the handoff note (`research/literature-review/HANDOFF.md`) — reading order and the frozen
  baseline rule.

Where this document and those files conflict on content method, those files win; where they are
silent on process, this document governs. A campaign that needs a different content methodology
writes its own before the pack is drafted — it does not improvise one mid-search.

The core split: a **planning session** manufactures the pack; a separate **execution session**
spends it. Nothing is authored mid-campaign — if the planning session did not write the prompt,
the execution session does not send it. The word for the artifact set is always *research pack*;
it is never called a prompt pack (that term belongs to multi-agent builds, `GOV-008`).

## The pipeline

Eight stages, each ending at a gate. Owner sign-off at a gate means the stage's artifact is
frozen; later changes go through the same gate again.

### 1. Prompt A — the research pre-plan package

A governed prompt document, planned **interactively with the owner** — AskUserQuestion batches,
one at a time, at the point each question matters. It carries:

- the owner's **ratified scope**: the questions the campaign must answer, the hypothesis set,
  and the null hypothesis the campaign works to support — marked explicitly as do-not-re-ask;
- the **artifact inventory** — every existing research input the campaign builds on, each marked
  frozen (read-only baseline), seed (encountered, not validated) or live;
- the **open-questions list** the later planning session must resolve with the owner;
- **standing constraints** (the research discipline rules below, plus any campaign-specific
  ones) and **effort and deadline context**.

### 2. Prompt B — the pack-factory prompt

A **separate** governed prompt document, drafted by executing Prompt A. Its purpose: investigate
the research directory and the repository, then write the research pack. Prompt A is the owner's
input; Prompt B is the machine that turns it into artifacts. They are never one document: the
gate between them is real.

### 3. Gate — adversarial review of Prompt B

An adversarial, opinionated agent audits Prompt B against Prompt A, the content methodology and
the actual state of `research/`, assuming it is broken and hunting for where it fails when
executed — a search prompt whose domain the methodology does not cover, an extraction prompt
that cannot fill the evidence schema, a stop condition no one can measure. Findings are
synthesized into fixes, and the owner signs off on the revised Prompt B before it runs.

### 4. Execute Prompt B — draft the pack files

**First in plan mode; auto execution only after the owner confirms the plan.** The output is the
pack body:

- the **scope record**: research questions, hypothesis register with a falsification criterion
  per hypothesis, and the status vocabulary verdicts will use;
- the **search-domain matrix**: every domain from the content methodology assigned to a phase,
  with the terminology variants each search must cover — no domain left to judgment;
- a plan with **backlog phases sized one session each**, dependency-ordered, encoded in
  `depends_on`. Phases follow the content methodology's pass structure — broad mapping before
  deep reading, deep reading before adversarial testing, adversarial testing before synthesis —
  so no synthesis phase can start while its evidence phases are open;
- the **evidence contract**: the schema every extraction fills, the reproducibility ledger
  format every search appends to, and where both live under `research/`;
- the **delegation pack**: per-phase sections in the established shape — kickoff (`K`), search
  and extraction pairs (`S*`/`X*`), collision review (`R`), phase gate (`G`), adversarial
  synthesis review (`A`) — each idempotent and dispatchable verbatim;
- the **descope ladder**: which domains, hypotheses or passes are cut first when the runway
  runs out, ordered for the actual deadline.

### 5. Gate — adversarial audit of the pack

A second adversarial agent audits the finished pack files against the content methodology and
repository reality. Findings are synthesized, fixes committed, and the governance check exits 0
before the pack is called done.

### 6. The coordinator prompt

A governed prompt document: preflight, the phase graph, the completion gate, close-out. Written
**generic and idempotent** — the same prompt whether the campaign takes one session or several,
so every re-run is a resume. Per-campaign owner rulings do not go here; they go in the kick-off
record.

### 7. Gate — owner sign-off on the coordinator prompt

Adversarial review at this gate is **optional and run only if the owner specifically requests
it** — the pack audit in stage 5 already covered the substance.

### 8. The kick-off record, then the kick-off paragraph

The **kick-off record** is a governed prompt document carrying:

- the owner's **per-campaign ratified deltas** — gate check-in cadence, descope authority,
  search-provider constraints — gathered via AskUserQuestion with recommendations before
  writing;
- the **pinned starting state** (queue state, peer claims, the frozen baseline's identity,
  deadline);
- the precedence rule: **where the kick-off record and the coordinator prompt differ, the
  kick-off record wins**;
- the **kick-off paragraph** as its final section, delivered in chat so the owner can paste it
  into a fresh terminal. It is the one artifact that is never governed and never tracked; its
  durable copy lives inside the kick-off record.

## Standing rules for every campaign

### Selective injection

Context is loaded when the step that needs it begins, never up front. The coordinator prompt
defers the content methodology to the agents that execute it; search prompts carry their domain
and terminology variants, not the whole domain matrix; the delegation pack is dispatched
verbatim one section at a time. Nothing front-loads the full pack into any agent's opening
context.

### Thesis discipline

- The campaign works to support the null hypothesis. Collisions are recorded first; the
  architecture is revised only in the synthesis phase, never during evidence collection.
- No agent renames a concept, narrows a hypothesis or rewrites scope to avoid a collision. A
  hypothesis change mid-campaign is a blocking finding for the owner, not an edit.
- The frozen baseline is never modified. Seed sources are never promoted to validated status
  without the verification steps the content methodology requires, and the historical seed
  ledger is never silently altered.
- Negative claims use the pack's status vocabulary. "No prior work exists" is not a permitted
  verdict; a failed search is recorded as a search that failed, with its queries.

### Evidence hygiene

- Every search appends to the reproducibility ledger: query, provider, date, filters, result
  identifiers, inclusion and exclusion rationale. A search that logged nothing did not happen.
- Generated summaries are leads, never evidence. Every synthesis claim traces to a primary
  source with a locator; a claim that cannot be traced is removed, not softened.
- Derivative sources are tracked to their shared ancestor and never counted as independent
  confirmation — of prior art or of novelty.
- Every critical collision receives a second review by an agent that did not produce the first
  assessment, and that receives the source and the evidence row — never the first agent's
  rationale.

### Agent hygiene

- The coordinator claims nothing, searches nothing, writes no findings, authors no prompts, and
  never does a worker's job. A missing prompt is a blocking finding for the owner, never
  something to improvise.
- Search, extraction and review are separate dispatches. Reviewers receive sources and evidence
  rows, never the searcher's interpretation of them.
- Peers' claims and fenced paths are never touched; `AGENTS.md`/`CLAUDE.md` are never edited;
  nothing confidential enters a tracked file. Findings commit before review, so a truncated
  agent is resumed, not re-run, and an orchestrator's assertion is verified against the ledger
  before anyone acts on it.

### Cost protocols

- Haiku for mechanical gates. **Sonnet is the standard model for search and extraction.**
  Judgment-heavy synthesis and collision review use Sonnet by default; Opus is never
  pre-assigned and is used at most as a single documented escalation per campaign.
- At most two fix cycles per work item; what survives them is reported, not looped on.
- Close-out reports spend posture: searches run, sources deep-read, any escalation, wall-clock
  against the runway.

### Gate check-in policy

Prompt A's open-questions list **always asks the owner up front** whether the execution session
should stop at gates for check-in or push through to close-out; the answer is recorded in the
kick-off record, not assumed. Whatever the answer, a **critical issue** — a collision that
falsifies scope, a methodology defect that invalidates collected evidence — first gets a dual
review: an adversarial agent challenges the finding and attempts a resolution. The campaign
pauses for the owner only if the issue survives that review unresolved.

### Stop conditions and descope

The pack encodes the content methodology's stop conditions as the completion gate — measured
against the ledger, not asserted. Saturation is demonstrated (searches returning duplicates,
every hypothesis with at least one serious challenger), never declared. The descope ladder
exists for emergencies, but no rung is taken without the owner's explicit direction unless the
kick-off record grants a stated exception. A campaign that stops early stops at a phase
boundary, with the resume state in its session record.

## Template appendix — required sections per artifact

**Prompt A (research pre-plan package)**: ratified scope (do-not-re-ask) · artifact inventory
with frozen/seed/live marks · what the planning session must produce, in order · open questions
for the owner · standing constraints · effort and deadline context · the prompt block that
drafts Prompt B.

**Prompt B (pack-factory prompt)**: role statement and hard scope limits (documents only, no
searching) · preflight (governance green, peer claims, content methodology read) · the pack
artifacts to produce, in order, with document codes drawn from `--next-code` · the
open-questions protocol (AskUserQuestion, batched, at the point each matters) · stop condition
(pack exists, governance 0, owner has the review summary).

**Delegation-pack phase section**: `K` kickoff (claim, output paths, ledger location, item
order) · `S*` searches and `X*` extractions in pairs · `R` collision review · `G` phase gate
(stop-condition measurements against the ledger, real output) · `A` adversarial synthesis
review where the phase produces synthesis.

**Coordinator prompt**: coordinator-only role statement · preflight (governance, clean
checkout, baseline integrity, ledger present) · phase graph with dispatch order and the
dependencies that force it · completion gate in stop-condition terms · close-out (checkpoint,
spend posture, resume state).

**Kick-off record**: starting state · owner-ratified deltas with the precedence rule · the
kick-off paragraph.
