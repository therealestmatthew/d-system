---
schema_version: 1
id: doc-prompt-literature-review-pre-plan-package
code: PROMPT-027
title: Literature-review pre-plan package — seed the planning session that manufactures the adversarial literature-review research pack
kind: prompt
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems: [sys-governance, sys-backlog]
depends_on: [doc-research-protocol, doc-prompt-pack-protocol, doc-conversation-guidelines]
---

# Literature-review pre-plan package — seed the planning session that manufactures the adversarial literature-review research pack

The adversarial D-System literature review has a complete content methodology and no research
pack. The methodology — mission, null hypothesis, hypothesis set, search domains, scoring,
deliverables — sits in `research/`; the research pack protocol
([GOV-009](../08-governance/GOV-009-research-protocol.md)) defines how a campaign is manufactured
and spent; and the campaign itself has never started. This document is **Prompt A** of that
protocol: the owner's ratified input to the planning session that will draft Prompt B, the
pack-factory prompt. Nothing here is analysis; everything here is ratified input or pinned fact.

This is `GOV-009`'s first execution. The protocol has never been run
(`SESS-2026-09-11-01` records this), so where its stage templates prove awkward in practice,
that is a finding to surface to the owner, not a license to improvise around them.

## How to run this

Paste the prompt block at the end into a fresh session. That session produces **Prompt B** — the
pack-factory prompt — and nothing else. It does not search, does not write pack artifacts, and
does not touch `research/`.

## Ratified scope (do not re-ask)

Ratified by the owner on 2026-09-12 across two AskUserQuestion batches.

1. **The hypothesis set stands as written.** The campaign works to support the null hypothesis —
   **H0: D-System is primarily a recombination of known ideas** — and attacks **H1–H11** exactly
   as defined in the adversarial review instructions
   (`research/literature-review/CLAUDE.md`) and the frozen hypothesis register
   (`research/pre-literature-hypotheses.yaml`). No hypothesis is edited, dropped, narrowed or
   added before or during the campaign. A hypothesis change mid-campaign is a blocking finding
   for the owner, per `GOV-009` thesis discipline.

2. **The adversarial codebase review is a frozen input with no precondition.** The twelve-file
   audit under `research/adversarial-codebase-review/` is a read-only baseline the campaign
   builds on. The session record `SESS-2026-09-11-01` paraphrases the handoff note as requiring
   "external review of the codebase audit" first; the handoff note
   (`research/literature-review/HANDOFF.md`) contains no such requirement, and the owner has
   ruled the stricter paraphrase an error. No external review blocks this campaign.

3. **Gate check-in policy: stop before synthesis only.** The evidence phases — broad mapping,
   deep reading, adversarial testing — run through without waiting for the owner. The campaign
   pauses **once, before the synthesis phase begins**, for owner check-in. This is `GOV-009`'s
   up-front gate question, answered; the kick-off record carries it. A critical issue — a
   collision that falsifies scope, a methodology defect that invalidates collected evidence —
   still gets the dual adversarial review `GOV-009` requires, and pauses the campaign outside a
   gate only if it survives that review unresolved.

4. **Timing: the campaign may run alongside demo prep, and demo work wins every conflict.** The
   live demo is the week of 2026-09-15. This campaign is not demo-critical; it executes as
   capacity allows, and whenever it competes with demo work for attention or claimed systems,
   the demo wins. That is intended behaviour, not a descope.

5. **Search providers: web search and free/open APIs.** Search agents use the available web
   search and fetch tools plus open endpoints — arXiv, Semantic Scholar, OpenAlex, Crossref and
   the like. No paid database access exists. Where a relevant source is paywalled (ACM, IEEE,
   Springer, Elsevier), it is assessed from its abstract, preprint or authoritative secondary
   coverage, and the evidence row records that limitation explicitly rather than presenting the
   assessment as a full-text read.

6. **The full deliverable set of thirteen is in scope.** The campaign produces every deliverable
   the content methodology requires, `01_terminology_map.md` through
   `13_validated_bibliography.md`, in `research/literature-review/`. The methodology's stop
   conditions — all major domains searched with terminology variants, every hypothesis with at
   least one serious challenger, the strongest 20–30 sources deeply compared, saturation
   demonstrated against the ledger — bound the depth.

7. **Runway: whatever the passes need.** No session cap. The pack sizes phases honestly against
   the 72 search domains and the 20–30 deep reads — the planning session's estimate, not a
   commitment, is four to six execution sessions. Saturation is demonstrated, never squeezed
   into a budget. The descope ladder exists for emergencies only, and per `GOV-009` no rung is
   taken without the owner's explicit direction.

## Artifact inventory

Every existing research input, marked per `GOV-009`: **frozen** (read-only baseline), **seed**
(encountered, not validated), or **live** (the campaign writes here).

### The content methodology (wins on content; process defers to GOV-009)

- `research/literature-review/CLAUDE.md` — mission, H0, H1–H11, the 72 search domains,
  vocabulary translation, scoring, collision rules, the thirteen deliverables, stop conditions.
- `research/protocols/literature_review_protocol.md` — research questions, search strategy
  phases A–E, inclusion/exclusion, the four-pass workflow.
- `research/literature-review/HANDOFF.md` — reading order and the frozen-baseline rule.
- Supporting protocol notes: `research/protocols/agent_instructions.md`,
  `research/protocols/research_agent_addendum.md`, `research/protocols/research_expansion.md`.

A byte-identical copy of the review instructions sits at `research/CLAUDE.literature-review.md`;
the `research/literature-review/` copy is the one `GOV-009` names and is authoritative. The
duplicate is flagged in the open questions below.

### Frozen — read-only baseline; never modified by any campaign agent

- `research/pre-literature-baseline.md` and `research/pre-literature-baseline-plan.md` — the
  frozen pre-literature statement of what D-System claims.
- `research/pre-literature-hypotheses.yaml` — the hypothesis register.
- `research/hypotheses/novelty_hypotheses.md` — the hypothesis background.
- `research/adversarial-codebase-review/` — the twelve-file audit, its `CLAUDE.md` and
  `reference/` (ratified frozen, decision 2).
- `research/evidence/` — the audit's supporting evidence (probes, snapshots, matrices).
- The conceptual-architecture descriptions the campaign compares prior art against:
  `research/architecture/`, `research/two_system_architecture.md`,
  `research/knowledge_glossary.md`, `research/implementation_glossary.md`,
  `research/terminology_investigation.md`, `research/development_traceability_model.md`,
  `research/phase_context_contract.md`.

### Seed — encountered during ideation, not validated evidence

- `research/sources/cited_sources_chat_seed.md` — the conversational seed inventory.
- `research/sources/source_ledger.md` — the historical seed ledger; never silently altered.
- `research/sources/archive-extractions/` — extracted archive material.

Seed sources are promoted to validated status only through the verification steps the
methodology's seed-handling section requires; the validated bibliography
(`13_validated_bibliography.md`) is a separate artifact from the seed ledger.

### Live — where the campaign writes

- `research/literature-review/` — the thirteen deliverables land here.
- The evidence matrix, source inventory and reproducibility ledger, at locations and in formats
  the pack's evidence contract fixes under `research/` (Prompt B's decision, drawn from the
  methodology's evidence-extraction and reproducibility sections).

Archive material at the `research/` root (`*.zip`, `CREATED_FILES.md`,
`d-system-complete-chat-source-ledger.md`) is neither input nor output; the campaign ignores it.

## What the planning session must produce, in order

1. **Prompt B — the pack-factory prompt**, as a governed document taking its code from
   `uv run python -m src.governance --next-code prompt`. Its required sections are in
   `GOV-009`'s template appendix: role statement and hard scope limits (documents only, no
   searching), preflight (governance green, peer claims, content methodology read), the pack
   artifacts to produce in order with their codes, the open-questions protocol
   (AskUserQuestion, batched, at the point each matters), and the stop condition (pack exists,
   governance exits 0, owner has the review summary).

2. Nothing else. The gate between Prompt A and Prompt B is real: the adversarial review of
   Prompt B (`GOV-009` stage 3) happens before Prompt B runs, and the owner signs off on the
   revised Prompt B before the pack is drafted.

Prompt B, when it later runs, must produce a pack containing at minimum (per `GOV-009` stage 4):
the scope record with a falsification criterion per hypothesis and the status vocabulary
(`LIKELY_ALREADY_KNOWN` / `KNOWN_COMPONENT_NEW_INTEGRATION` / `POTENTIALLY_DISTINCT` /
`INSUFFICIENT_EVIDENCE` — `NOVEL` only under the methodology's stronger-scrutiny rule); the
search-domain matrix assigning all 72 domains to phases with terminology variants per search;
backlog phases sized one session each following the pass structure (broad mapping → deep reading
→ adversarial testing → synthesis) with dependencies encoded in `depends_on`; the evidence
contract and reproducibility ledger format; the delegation pack in the
`K`/`S*`/`X*`/`R`/`G`/`A` shape, each section idempotent and dispatchable verbatim; and the
descope ladder.

## Open questions for the later planning session

Resolve these with the owner via AskUserQuestion, at the point each matters — not up front.

1. **Descope ladder ordering.** With no hard deadline the ladder is emergencies-only, but
   `GOV-009` still requires it ordered. The planning session proposes an order — which domains,
   hypotheses or passes are surrendered first — and the owner ratifies it at the pack-audit
   gate.
2. **Phase count and domain grouping.** How the 72 domains fold into search phases, and how many
   search/extraction pairs each phase carries, is Prompt B's design work; raise it to the owner
   only if the resulting spend estimate departs materially from the four-to-six-session figure
   in ratified decision 7.
3. **The duplicate methodology file.** `research/CLAUDE.literature-review.md` duplicates the
   authoritative copy byte for byte. Whether to delete it, replace it with a pointer, or leave
   it is the owner's call; the planning session asks once, and no campaign agent reads the root
   copy either way.
4. **Critical-collision second review staffing.** Every critical collision gets a second review
   by an agent that did not produce the first assessment, receiving the source and the evidence
   row, never the first rationale. Whether that reviewer earns a committed charter in
   `.claude/agents/` or runs as a pack-supplied prompt on a general-purpose agent is the
   planning session's proposal and the owner's ruling.

The gate check-in question `GOV-009` requires asking up front is **already answered** (ratified
decision 3: stop before synthesis only) and is recorded in the kick-off record, not re-asked.

## Standing constraints

`GOV-009`'s standing rules apply in full — selective injection, thesis discipline, evidence
hygiene, agent hygiene, cost protocols, stop conditions — and are not restated here. Campaign
specifics on top of them:

- The frozen baseline is never modified; the seed ledger is never silently altered; no campaign
  agent begins implementation or refactoring (the handoff note's standing rule) — architecture
  is revised only in the synthesis phase, and only as recorded implications, not code.
- The provider constraint is ratified decision 5. Every search appends to the reproducibility
  ledger regardless of provider; a search that logged nothing did not happen.
- `AGENTS.md` governs. Every governed document takes its code from `--next-code`. `AGENTS.md`
  and `CLAUDE.md` are never edited without the owner's explicit per-change approval.
  Integration into `dev` is the owner's call each time; pushing an agent's own branch is not. A
  failing check is a result to record, not a step to retry until quiet. New asks the owner
  raises mid-session are captured as ideas immediately through `tools/append_idea.py`, per
  [GOV-006](../08-governance/GOV-006-conversation-guidelines.md), with ids taken from the
  writer's own output.

Cost posture per `GOV-009`: Haiku for mechanical gates; **Sonnet is the standard model for
search and extraction** and the default for synthesis and collision review; Opus is never
pre-assigned and is used at most as a single documented escalation per campaign. At most two fix
cycles per work item. Close-out reports spend posture: searches run, sources deep-read, any
escalation, wall-clock against the runway.

## Effort and deadline context

The live demo is the week of 2026-09-15. This campaign is not demo-critical (ratified decision
4): planning may proceed now, execution runs as capacity allows, and the demo wins every
conflict. No hard deadline exists; runway is whatever the passes need (ratified decision 7),
with four to six execution sessions as the planning estimate. Queue state, peer claims and the
frozen baseline's identity are pinned in the kick-off record at kick-off time, not here — this
package only records that the repository is active with concurrent demo work, so the planning
session must run the governance check and read live claims before drafting.

---

## The prompt

> You are the planner for the D-System adversarial literature-review research pack. Read
> `AGENTS.md`, then `docs/08-governance/GOV-006-conversation-guidelines.md`, then
> `docs/08-governance/GOV-009-research-protocol.md` (and `GOV-008` where it points there), then
> the content methodology — `research/literature-review/CLAUDE.md`,
> `research/protocols/literature_review_protocol.md`,
> `research/literature-review/HANDOFF.md` — then this document
> (`docs/02-prompts/PROMPT-027-literature-review-pre-plan-package.md`) in full. It carries the
> owner's seven ratified decisions, the artifact inventory with frozen/seed/live marks, and the
> open-questions list.
>
> Produce exactly one artifact: **Prompt B, the pack-factory prompt**, as a governed document
> whose code comes from `uv run python -m src.governance --next-code prompt`. Follow `GOV-009`'s
> template appendix for Prompt B's required sections.
>
> **Do not re-ask any of the seven ratified decisions.** Use AskUserQuestion, batched, one batch
> at a time, only for the open questions this package lists at the point each matters, or if
> drafting exposes something genuinely new — and if it does, ask rather than guess.
>
> Do not search, do not write any pack artifact, do not modify anything under `research/`, and
> do not draft backlog phases: those are Prompt B's job, and Prompt B runs only after its
> adversarial review (`GOV-009` stage 3) and the owner's sign-off. The frozen baseline is
> read-only.
>
> Stop when Prompt B exists, the governance check exits 0, and the owner has a review summary
> naming what Prompt B will produce and what it deliberately omits.
