---
schema_version: 1
id: doc-system-boundary-study-requirements
code: REQ-033
title: System boundary study requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-26'
systems: [sys-portfolio, sys-capture, sys-projection, sys-retrieval, sys-realization, sys-plugin, sys-wb-layout, sys-governance]
depends_on: [doc-system-audit, doc-idea-realization-system-plan, doc-prompt-pack-protocol]
---

# System boundary study requirements

## Observed problem and scope

D-System contains three distinct concerns that grew together: a private personal-productivity system,
an idea-realization engine, and a repository workbench originally built for HTML demonstration.
The system registry deliberately names many fine-grained components, but it does not state which of
these concerns own data, interfaces, release cadence, or a future repository boundary. The governed
prompt corpus has 39 active prompt documents; `active` preserves precedent and does not say whether
a prompt is an operating entry point, reusable template, or one-off campaign record.

This study creates evidence and a decision-ready boundary recommendation. It does not extract code,
move private content, retire documents, or change any current system's ownership.

## Observable requirements and verification

| Id | Requirement | Verification |
|---|---|---|
| R01 | The study maps every current registered system to one candidate concern or to a cross-cutting foundation, and records its source-of-truth data, writers, readers, and external interfaces. | A reviewer can trace every `systems.yaml` entry in the study inventory to exactly one classification; rows lacking evidence are marked unknown rather than inferred. |
| R02 | The study produces a dependency map for the personal-productivity system, idea-realization engine, repository workbench, and governance/framework layer. The map identifies allowed interfaces and prohibited ownership crossings. | The map has one node for each concern and labels every inter-concern edge with the data or capability crossing it; each proposed boundary names at least one negative rule. |
| R03 | The study classifies all governed prompt documents by role and reuse class, distinguishing operating prompts, reusable templates/protocols, campaign or build records, historical precedents, and material requiring review. | The inventory contains all 39 `kind: prompt` documents and reports category totals; spot checks against PROMPT-006, PROMPT-010, PROMPT-020, and PROMPT-040 show why each category was assigned. |
| R04 | The recommendation compares at least three repository-boundary options, including retaining one repository, and states the benefits, costs, migration preconditions, and triggers that would justify extraction. | The decision matrix names the three concerns and governance/framework layer for every option, includes one rejected alternative per recommendation, and identifies no-code-change as a valid immediate outcome. |
| R05 | The final report gives the owner the smallest set of explicit decisions needed to choose a boundary direction and a sequenced next action after each possible decision. | The report has an owner-decision section where each question names the decider, the decision point, a recommendation, and the consequence of each answer. |
| R06 | The study is reproducible from tracked material and does not read `_private/`, create a repository, move data, or change runtime behaviour. | The evidence inventory lists the read-only commands and tracked sources used; `git diff --check` is clean and no study phase lists source, data, or configuration mutations in scope. |

## What each requirement is not

- R01 does not reclassify the registry or edit `systems.yaml`; it records a proposed grouping for an
  owner decision.
- R02 does not require a new API. An interface may initially be a file contract or a documented
  adapter boundary.
- R03 does not retire prompts merely because they are campaign-specific; preservation as precedent
  is a valid classification.
- R04 does not require a repository split, package publication, or a migration schedule until the
  owner selects an option.
- R05 does not transfer decision authority from the owner to the study author.
- R06 does not prohibit creating study documents, session evidence, or a future owner-approved ADR.

## Accepted decisions

- The study starts from the owner's stated history: personal productivity is the original purpose;
  idea realization emerged as a secondary but major system; and the workbench began as an HTML
  demonstration.
- The study treats governance as a cross-cutting framework candidate, not as a fourth end-user
  product, unless the evidence contradicts that framing.
