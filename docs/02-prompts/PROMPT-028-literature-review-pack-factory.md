---
schema_version: 1
id: doc-prompt-literature-review-pack-factory
code: PROMPT-028
title: Literature-review pack factory — investigate the research directory and write the adversarial literature-review research pack
kind: prompt
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems: [sys-governance, sys-backlog]
depends_on: [doc-prompt-literature-review-pre-plan-package, doc-research-protocol, doc-prompt-pack-protocol]
---

# Literature-review pack factory — investigate the research directory and write the adversarial literature-review research pack

This is **Prompt B** of the research pack protocol
([GOV-009](../08-governance/GOV-009-research-protocol.md)) for the adversarial D-System
literature review. Prompt A is the pre-plan package
([PROMPT-027](PROMPT-027-literature-review-pre-plan-package.md)), which carries the owner's
seven ratified decisions, the artifact inventory with frozen/seed/live marks, and the open
questions this document encodes below. Prompt A is the owner's input; this document is the
machine that turns it into the research pack.

Per `GOV-009` stage 3, this document is adversarially audited against Prompt A, the content
methodology and the actual state of `research/`, and the owner signs off on the revised
version, **before** it runs. This is `GOV-009`'s first execution: where its stage templates
prove awkward in practice, that is a finding to surface to the owner, not a license to
improvise around them.

## Role and hard scope limits

You are the pack factory. You investigate `research/` and the repository, and you write the
governed documents that make up the research pack. That is the whole job. **Documents only, no
searching.**

**You must not:**

- run any literature search — no web search, no fetch, no arXiv/Semantic Scholar/OpenAlex/
  Crossref call, no source evaluation of any kind. Search is the execution session's job, and
  only from prompts this pack contains;
- write any campaign deliverable — nothing of `01_terminology_map.md` through
  `13_validated_bibliography.md`, and no partial draft of one;
- write any file under `research/`. The evidence contract *names* the locations and formats of
  the ledger and matrix files under `research/`; the delegation pack's first kickoff section
  instructs the campaign to create them. Until the campaign runs, `research/` is untouched;
- modify the frozen baseline or the seed ledger — Prompt A's inventory marks what is frozen
  and seed; the marks are the rule;
- re-ask any of Prompt A's seven ratified decisions (hypothesis set stands; codebase review is
  a frozen input with no precondition; stop before synthesis only; demo work wins conflicts;
  web search and free/open APIs only; all thirteen deliverables; runway is whatever the passes
  need);
- write the coordinator prompt or the kick-off record. Those are `GOV-009` stages 6–8 and come
  **after** the pack audit (stage 5), not from this prompt;
- dispatch any campaign agent or begin the campaign;
- edit `AGENTS.md` or `CLAUDE.md`, touch a peer's claim, or write a confidential identifier
  into a tracked file.

## Preflight

Run these before writing anything, and record the real output. A failing check is a result to
record, not a step to retry until it goes quiet.

```bash
uv run python -m src.governance --inventory     # must exit 0
uv run python -m src.governance --ready         # active claims and locked systems
git status --short                              # know what is uncommitted before you add to it
cmp research/literature-review/CLAUDE.md research/CLAUDE.literature-review.md   # duplicate check
```

Then confirm:

- **The content methodology is read in full**: `research/literature-review/CLAUDE.md` (mission,
  H0, H1–H11, the 72 search domains, vocabulary translation, scoring, collision rules, the
  thirteen deliverables, stop conditions), `research/protocols/literature_review_protocol.md`
  (RQ1–RQ7, search phases A–E, inclusion/exclusion, the four-pass workflow),
  `research/literature-review/HANDOFF.md`, and the supporting protocol notes Prompt A lists.
  The methodology wins on content; `GOV-009` governs process.
- **Prompt A (`PROMPT-027`) is signed off.** If it is unratified, stop and say so rather than
  building a pack on an unratified input.
- **The frozen baseline is present**: `research/pre-literature-baseline.md`,
  `research/pre-literature-hypotheses.yaml`, `research/adversarial-codebase-review/`, and the
  rest of Prompt A's frozen list. You read them to draft the pack; no campaign agent modifies
  them.
- **Peer claims do not collide.** Demo work wins every conflict (ratified decision 4). If a
  peer holds an active claim, follow `AGENTS.md`'s concurrency rules — work on your own
  `agent/<...>` branch, and remember integration into `dev` is the owner's call.
- **Prompt A and this document are tracked.** If `git status` shows `PROMPT-027` or
  `PROMPT-028` as untracked, stop and say so — a fresh worktree cut from `dev` would not
  contain your own inputs.
- The catalog matches `uv run python -m src.governance --catalog`; regenerate it whenever you
  add documents, committing the plan family as the one change described above.

**Ask the duplicate-file question here** (open question 3, the only up-front one): the byte
check above just told you whether `research/CLAUDE.literature-review.md` still duplicates the
authoritative copy. Ask the owner once, via `AskUserQuestion`, whether to delete it, replace it
with a pointer, or leave it. Whatever the answer, the pack directs every campaign agent to the
`research/literature-review/` copy and none to the root copy.

**Carrying out the owner's ruling on this one question — deleting the root copy or replacing it
with a pointer — is the sole sanctioned change under `research/`.** Record what was done in the
review summary; the stop condition's no-writes-under-`research/` rule reads subject to exactly
this carve-out and nothing else.

## The pack artifacts to produce, in order

Take every code from `uv run python -m src.governance --next-code <kind>` at the moment you
create the document — never guess a code and never reuse one seen earlier; peers allocate codes
concurrently, and `PROMPT-027`/`PROMPT-028` were themselves taken while other packs were being
drafted.

**Proposed kind mapping** (the drafter's proposal, not the owner's ruling — surface it in the
review summary so the stage-5 audit can challenge it): the campaign plan is `kind: plan` in
`docs/01-plans/`; the scope record, search-domain matrix and evidence contract are its child
plans (`--next-code plan --parent <plan-id>`); the delegation pack is `kind: prompt` in
`docs/02-prompts/`; the descope ladder is a section of the campaign plan.

Two mechanical facts govern the order of operations:

- `--next-code plan --parent <plan-id>` **errors unless the parent document already exists on
  disk** — allocating the parent's code is not enough. So: allocate the campaign plan's code,
  write its overview file as a skeleton (`docs/01-plans/PLAN-NNN-<slug>/PLAN-NNN-overview.md`,
  per `GOV-005`'s multi-file plan rules) **before** allocating any child code, then author the
  artifacts in the order below — `GOV-009` stage 4's order — filling the overview in as
  artifact 3.
- The governance check **fails any open plan not referenced by a backlog phase**. So every
  child plan must be listed in at least one phase's `sources`, and the plan family — parent
  plan, child plans, backlog phases and the regenerated catalog — is committed as **one
  change**, never document-by-document; intermediate states where a plan exists without its
  phases would otherwise commit governance-red.

### 1. The scope record

- The research questions **RQ1–RQ7**, carried from the search protocol.
- The hypothesis register: **H0** (D-System is primarily a recombination of known ideas — the
  campaign works to support it) and **H1–H11 with text and falsification criteria taken
  verbatim from the review instructions' "Falsify by finding" clauses** — not paraphrased, not
  narrowed. The review instructions (`research/literature-review/CLAUDE.md`) are the
  authoritative register text; `research/pre-literature-hypotheses.yaml` is the frozen
  cross-referenced register, and where its wording differs, the difference is noted in the
  scope record, never merged into a blended phrasing. **H0 carries no falsification clause** —
  it is the null: its register entry states that it stands unless some Hn survives adversarial
  testing as `POTENTIALLY_DISTINCT` or stronger. Thesis discipline: a hypothesis change
  mid-campaign is a blocking finding for the owner.
- One known discrepancy to record, not resolve: the search protocol's Pass 3 and stop
  conditions name only H1–H6, while the review instructions cover H1–H11. The pack follows the
  review instructions; the scope record notes the discrepancy as a finding for the owner and
  the stage-5 audit.
- The status vocabulary verdicts will use: `LIKELY_ALREADY_KNOWN`,
  `KNOWN_COMPONENT_NEW_INTEGRATION`, `POTENTIALLY_DISTINCT`, `INSUFFICIENT_EVIDENCE` — and
  `NOVEL` only under the methodology's stronger-scrutiny rule. "No prior work exists" is not a
  permitted verdict; a failed search is recorded as a search that failed, with its queries.

### 2. The search-domain matrix

- **All 72 search domains** from the review instructions' §5, each assigned to exactly one
  **Pass 1 search phase** — the session groupings artifact 3 designs, *not* the methodology's
  search-strategy Phases A–E, which every domain traverses — with the terminology variants each
  search must cover, drawn from the vocabulary-translation table (§6) and extended per domain.
  No domain is left to a search agent's judgment. Because the grouping is artifact 3's design
  work, draft the matrix and the phase plan together and finalize the matrix's phase column
  when the grouping is settled; the two are committed together in any case.
- The search protocol's separate 20-domain list must be reconciled against the 72: map each of
  the 20 onto the domains that subsume it. If any of the 20 is genuinely not subsumed, that is
  a finding to record in the matrix and surface to the owner — not a quiet 73rd row and not a
  deletion.
- Each domain row also carries at least one collision-search query in the methodology's Phase E
  style, so the collision pass has pre-crafted starting queries rather than improvised ones.

### 3. The campaign plan and backlog phases

- Backlog phases **sized one session each**, dependency-ordered via `depends_on`, following the
  methodology's pass structure: **Pass 1 broad mapping → Pass 2 deep reading → Pass 3
  adversarial testing → Pass 4 synthesis**. No synthesis phase can become ready while any
  evidence phase is open — encode that in the dependencies, not in prose.
- The owner's one check-in (ratified decision 3: stop before synthesis only) sits at the
  Pass 3 → Pass 4 boundary. Encode it as the synthesis phase's stated entry condition; the
  kick-off record will carry the ruling itself.
- How the 72 domains fold into Pass 1 search phases, and how many search/extraction pairs each
  phase carries, is your design work (open question 2). Estimate the total spend honestly.
  **If the estimate departs materially from four to six execution sessions, ask the owner via
  `AskUserQuestion` at that point** — with the estimate and the grouping options — before
  finalizing the phase plan. Inside that envelope, do not ask.
- Phases declare `systems` and deliverable paths per the backlog schema. `systems.yaml` has no
  system covering `research/` today: propose the minimal addition **via `AskUserQuestion` with
  the exact diff, and edit only on the owner's approval** — do not edit the register on your
  own judgment, and do not stretch an unrelated system's scope to avoid the question.
- **The thirteen deliverables are the plan's coverage test** (ratified decision 6): map each of
  `01_terminology_map.md` through `13_validated_bibliography.md` to the phase whose
  `deliverables` include it, so a deliverable no phase produces is impossible by construction.
  The mapping goes in the review summary.
- **Phases enter the backlog `queued` and are never added to `next_up`.** Demo work wins every
  conflict (ratified decision 4), and "execute the next task" means the front of the queue;
  promoting a campaign phase to the queue front is the owner's act at kick-off, not yours.
- Each phase's `verification` includes the governance check and the phase-gate measurements
  from the delegation pack's `G` section. The `G` sections are written in artifact 5, so
  finalize each phase's `verification` by backfilling from them **after artifact 5 and before
  the review summary** — the plan is not finished until that backfill is done.

### 4. The evidence contract

- The **extraction schema**: every field the methodology's evidence-extraction section
  requires (§9 of the review instructions; the search protocol's §8 minimum set), including
  strongest overlap, strongest difference, hypotheses challenged, evidence locator and
  interpretation confidence — plus an explicit **access-limitation field** recording when a
  paywalled source was assessed from abstract, preprint or secondary coverage rather than a
  full-text read (ratified decision 5).
- The **reproducibility ledger format**: query, provider, date, filters, result identifiers,
  inclusion and exclusion rationale, duplicate handling, citation-chain decisions — **plus the
  matrix domain id the search served**, so "domains searched with variants" is computable from
  the ledger rather than reverse-mapped from free-text queries. A search that logged nothing
  did not happen.
- The two **similarity scores** (component overlap 0–5, architecture overlap 0–5) and the
  `CRITICAL_COLLISION` flag rules, carried verbatim from the methodology.
- **Derivative-ancestry tracking**: shared-ancestor lineage recorded so derivative sources are
  never counted as independent confirmation.
- **Seed-promotion steps** (§16): the five verification steps a seed source passes before it
  can enter the validated bibliography; the historical seed ledger is never silently altered.
- The **file locations and formats under `research/`** for the ledger, the source inventory
  and the evidence matrix — fixed here (this is the decision Prompt A delegated to you), with
  the delegation pack's first kickoff creating the files.

### 5. The delegation pack

A governed prompt document holding every prompt the execution session dispatches **verbatim,
one section at a time**. Nothing is authored mid-campaign: if this document does not contain
it, the execution session does not send it. Per-phase sections follow `GOV-009`'s shape:

- **`K` — kickoff**: claim the phase, output paths, ledger location (create it on the first
  phase), item order.
- **`S*`/`X*` — search and extraction pairs**: each `S*` carries **only its own domains,
  terminology variants and collision queries** from the matrix — never the whole matrix
  (selective injection) — plus the provider constraint (web search and free/open endpoints;
  paywalled sources assessed from abstract/preprint/secondary coverage with the limitation
  recorded) and the logging obligation. Each `X*` fills the evidence contract's schema from
  sources the paired search logged; generated summaries are leads, never evidence.
- **`R` — collision review**: every `CRITICAL_COLLISION` gets a second review by an agent that
  did not produce the first assessment, receiving **the source and the evidence row, never the
  first agent's rationale**. **Ask the owner here** (open question 4), via `AskUserQuestion`
  when you draft the first `R` section: does the second reviewer get a committed charter in
  `.claude/agents/`, or run as a pack-supplied prompt on a general-purpose agent? Present a
  recommendation with the question.
- **`G` — phase gate**: the methodology's stop-condition measurements taken with real output,
  never asserted — **domains searched with variants and duplicate rates measured against the
  ledger** (which carries the domain id per search for exactly this purpose), **challengers per
  hypothesis measured against the evidence matrix** (its hypotheses-challenged field), with the
  `G` section naming both files it reads.
- **`A` — adversarial synthesis review**: for the synthesis phase only, auditing the
  anti-novelty case and the surviving distinctions against the evidence matrix.

Model assignments per `GOV-009` cost protocol, stated per section: Haiku for mechanical gates;
Sonnet as the standard for search, extraction, synthesis and collision review; Opus never
pre-assigned and used **at most as a single documented escalation per campaign**. At most two
fix cycles per work item. Every section idempotent, so a re-dispatch is a resume.

### 6. The descope ladder

Ordered — which domains, hypotheses or passes are surrendered first — even though no hard
deadline exists and the ladder is emergencies-only. **The order is your proposal** (open
question 1): flag it as the drafter's proposal in the document itself, to be ratified by the
owner at the stage-5 pack-audit gate, not asked mid-draft. No rung is ever taken without the
owner's explicit direction.

## The open-questions protocol

All questions to the owner go through the **`AskUserQuestion` tool, batched, at the point each
matters** — never in prose (`brain/procedures/ask-through-the-tool.md`). The seven ratified
decisions are never re-asked, and are not reopened because a repository fact seems to argue the
other way — surface the fact and let the owner decide.

Prompt A's four open questions, each already placed above at the point it matters:

1. **Descope ladder ordering** — proposed in artifact 6, ratified at the pack-audit gate; not
   an `AskUserQuestion` during drafting.
2. **Phase count and domain grouping** — your design work in artifact 3; ask only if the spend
   estimate materially departs from four to six sessions.
3. **The duplicate methodology file** — asked once, at preflight, after the byte check.
4. **Critical-collision second-review staffing** — asked when drafting the delegation pack's
   `R` section, with a recommendation.

The gate check-in question `GOV-009` requires up front is **already answered** (ratified
decision 3: stop before synthesis only) and belongs to the kick-off record, not to you. If
drafting exposes something genuinely new — a methodology conflict Prompt A did not settle, a
convention that makes a ratified decision unimplementable as written — ask rather than guess.

## Standing constraints

`AGENTS.md` governs. `GOV-009`'s standing rules apply in full — selective injection, thesis
discipline, evidence hygiene, agent hygiene, cost protocols, stop conditions — and bind every
prompt you write into the pack, not just your own session. Every governed document takes its
code from `--next-code` at creation. `AGENTS.md` and `CLAUDE.md` are never edited without the
owner's explicit per-change approval. Integration into `dev` is the owner's call each time;
pushing your own branch is not. Never write a confidential identifier into a tracked file. New
asks the owner raises mid-session are captured as ideas immediately through
`tools/append_idea.py`, one per distinct ask, ids taken from the writer's own output.

Regenerate `docs/08-governance/catalog.md` after adding documents and commit it in the same
change; it is generated, and CI fails on any difference.

## Stop condition

Stop when:

- all six pack artifacts exist — scope record, search-domain matrix, campaign plan with backlog
  phases, evidence contract, delegation pack, descope ladder;
- **no file under `research/` was created or modified**, with the single carve-out of the
  owner's ruling on the duplicate methodology file, executed as directed and recorded in the
  review summary;
- `uv run python -m src.governance` exits 0 and the catalog is in sync;
- the owner has a review summary naming: what the pack contains; the phase plan's spend
  estimate against the four-to-six-session figure; the proposals awaiting the pack-audit gate
  (the descope order and the kind mapping); and what the pack deliberately omits — the
  coordinator prompt and kick-off record (`GOV-009` stages 6–8, written after the stage-5
  audit) and every campaign deliverable (the execution session's job).

Do not start the campaign. The pack is adversarially audited (`GOV-009` stage 5) and the owner
approves it before the coordinator prompt is written or any search agent is dispatched.

---

## The prompt

> You are the pack factory for the D-System adversarial literature-review research pack. Read
> `AGENTS.md`, then `docs/08-governance/GOV-006-conversation-guidelines.md`, then
> `docs/08-governance/GOV-009-research-protocol.md` (and `GOV-008` where it points there), then
> the content methodology — `research/literature-review/CLAUDE.md`,
> `research/protocols/literature_review_protocol.md`, `research/literature-review/HANDOFF.md` —
> then `docs/02-prompts/PROMPT-027-literature-review-pre-plan-package.md` (the owner's seven
> ratified decisions), and then this document
> (`docs/02-prompts/PROMPT-028-literature-review-pack-factory.md`) in full.
>
> **Work in plan mode first.** `GOV-009` stage 4 — which is what executing this document is —
> requires the pack be planned before it is written, with auto execution only after the owner
> confirms the plan. Run the preflight, record the real output, present the plan, and wait.
>
> Once the owner confirms, produce the six pack artifacts in the order given: the scope record,
> the search-domain matrix, the campaign plan with backlog phases, the evidence contract, the
> delegation pack, and the descope ladder.
>
> **On a re-run after an interruption, this prompt is a resume, not a restart**: a pack
> artifact that already exists is verified against this specification and skipped — never
> re-created, never re-allocated a code. Two governed documents for one artifact is a failure
> the stage-5 audit should never have to untangle.
>
> You write documents and investigate the repository. You do **not** search the literature,
> write any campaign deliverable, touch anything under `research/`, write the coordinator
> prompt or kick-off record, or re-ask any ratified decision. Questions go through the
> `AskUserQuestion` tool, batched, at the point each matters — the four open questions are
> placed in this document where they arise.
>
> Stop when the six artifacts exist, governance exits 0, the catalog is in sync, and the owner
> has the review summary. The pack is adversarially audited and approved before any campaign
> agent is dispatched.
