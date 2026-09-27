# Research packs

How a research campaign is planned and run. A research pack is the governed artifact set a
campaign runs from: a scope record, a hypothesis register, a search-domain matrix, a delegation
pack of search, extraction and review prompts, a coordinator prompt and a kick-off record. The
artifact set is always called a research pack, never a prompt pack.

A research pack follows the pipeline and gates of `prompt-packs.md` (section 1). Research
discipline stands in place of the build's standing rules. A planning session manufactures the pack
and a separate execution session spends it; nothing is authored mid-campaign.

## 1. Process and content method

- This document governs process. The campaign's content methodology (what to search, how to score
  overlap, what an evidence row holds) is a separate document. On content the methodology wins;
  where it is silent on process, this document governs.
- A campaign that needs a content methodology writes it before the pack is drafted, never partway
  through a search.

## 2. The pipeline, as it differs for research

- **Prompt A** carries the ratified scope, marked do-not-re-ask: the research questions, the
  hypothesis set and the null hypothesis the campaign works to support. Its artifact inventory
  marks every existing research input as frozen (read-only baseline), seed (encountered, not
  validated) or live. It also carries open questions, the standing constraints and the effort and
  deadline context.
- **Prompt B** is a separate governed prompt document that investigates the campaign's research
  inputs and the repository, then writes the pack.
- **The Prompt B review** audits against Prompt A, the content methodology and the actual research
  inputs. It looks for a search outside the methodology's domains, an extraction that cannot fill
  the evidence schema, and a stop condition nobody can measure. Prompt B runs in plan mode first,
  as for a build.
- **The pack** carries:
  - a scope record: the research questions, a hypothesis register with a falsification criterion
    for each hypothesis, and the status vocabulary the verdicts use;
  - a search-domain matrix that assigns every domain in the methodology to a phase, with the
    terminology variants each search must cover. No domain is left to judgement;
  - phases in pass order: broad mapping, then deep reading, then adversarial testing, then
    synthesis. `depends_on` blocks synthesis while its evidence phases are open;
  - an evidence contract naming the schema every extraction fills, the reproducibility-ledger
    format every search appends to, and where both live;
  - delegation-pack phase sections: `K`, search and extraction pairs `S*`/`X*`, collision review
    `R`, gate `G` and adversarial synthesis review `A`, each idempotent and dispatchable verbatim
    (the opening sentence in `prompt-packs.md` section 2 applies);
  - a descope ladder stating which domains, hypotheses or passes are cut first, ordered for the
    actual deadline.
- **The pack audit** checks the finished files against the content methodology and the repository;
  the check exits 0 before the pack is done.
- **The coordinator prompt** is generic and idempotent. Per-campaign rulings go in the kick-off
  record.
- **The kick-off record's** changes cover gate check-in cadence, descope authority and
  search-provider constraints. Its pinned starting state includes the frozen baseline's identity.

## 3. Standing rules for every campaign

**Context.** The coordinator prompt leaves the content methodology to the agents that execute it.
A search prompt carries its own domain and terminology variants, never the whole matrix.

**Null-hypothesis discipline.**

- The campaign works to support the null hypothesis. Collisions are recorded first, and the
  architecture is revised only in the synthesis phase.
- No agent renames a concept, narrows a hypothesis or rewrites scope to avoid a collision. A
  hypothesis change mid-campaign is a blocking finding for the owner.
- The frozen baseline is never modified. A seed source is promoted only through the methodology's
  verification steps, and an existing seed ledger is never silently altered.
- Negative claims use the pack's status vocabulary. "No prior work exists" is not a permitted
  verdict, and a failed search is recorded as failed, with its queries.

**Evidence.**

- Every search appends to the ledger: query, provider, date, filters, result ids, and the reasons
  for inclusion and exclusion. A search that logged nothing did not happen.
- Generated summaries are leads, never evidence. Every synthesis claim traces to a primary source
  with a locator, and an untraceable claim is removed.
- Derivative sources are traced to their shared ancestor and never count as independent
  confirmation.
- Every critical collision gets a second review by a different agent, which receives the source and
  the evidence row but never the first agent's rationale.

**Agent hygiene.**

- The research coordinator claims nothing, searches nothing, writes no findings, authors no prompts
  and never does a worker's job. A missing prompt is a blocking finding.
- Search, extraction and review are separate dispatches. Reviewers get sources and rows, never the
  searcher's interpretation.
- The hygiene rules of `prompt-packs.md` section 3 apply; an orchestrator's assertion is verified
  against the ledger.

**Cost.** The standard model does search, extraction, synthesis and collision review; the
escalation and fix-cycle rules of `prompt-packs.md` section 3 apply. The close-out reports searches
run, sources read in depth, any escalation, and wall-clock time against the runway.

**Gates and stopping.**

- Gate check-in follows `prompt-packs.md` section 3. A critical issue is a collision that
  falsifies scope, or a methodology defect that invalidates collected evidence, and it gets a dual
  review before it pauses the campaign.
- The completion gate encodes the methodology's stop conditions and is measured against the
  ledger, never asserted.
- Saturation is demonstrated (searches return duplicates, and every hypothesis has at least one
  serious challenger), never declared.
- No descope rung is taken without the owner's direction. A campaign that stops early stops at a
  phase boundary, with the resume state in its session record.

## 4. Templates

| Artifact | Sections |
|---|---|
| Prompt A | Ratified scope; artifact inventory with frozen, seed and live marks; outputs in order; open questions; constraints; effort and deadline context; the Prompt B block |
| Prompt B | Role and hard scope limits (documents only, no searching); preflight (check green, peer claims, methodology read); pack artifacts in order with codes from the `next-code` skill; the open-questions protocol; the stop condition |
| Phase section | `K` (claim, output paths, ledger location, item order); `S*`/`X*` pairs; `R`; `G` (stop-condition measurements against the ledger, real output); `A` where the phase produces synthesis |
| Coordinator prompt | Role; preflight (check, clean checkout, baseline integrity, ledger present); phase graph; completion gate in stop-condition terms; close-out |
| Kick-off record | As for a prompt pack (`prompt-packs.md` section 4) |
