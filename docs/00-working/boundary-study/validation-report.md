# System boundary study — independent validation report

*Ran unclaimed: owner-directed work with no backlog phase; no peer holds a lock against it.*

Validation of the system boundary study: the draft decision report (`ARCH-012`), its requirements
(`REQ-033`), its plan (`PLAN-050` and children `PLAN-050.01` to `.05`) and the evidence files in
this folder. Run on 2026-09-28 from a cloud session on `agent/cloud-boundary-validation`, following
`docs/00-working/cloud-prompts/boundary-validation.md`. "Tip" in this report means `origin/dev` at
`9772c21`, the commit the validation started from. The study's own baselines are named where used:
`2fd11e9` (system inventory and boundary map), `7e3a067` (prompt corpus inventory), `4f3848e`
(portfolio review) and `0c47c27` (the reconciliation `ARCH-012` was written against).

## 1. Summary

The study's recommendation to keep one repository with explicit contracts (option A) and its
rejection of an immediate split (option C) still hold on the corrected evidence; the corrections
strengthen the rejection of C, because the idea-realization core holds one registered system and it
is planned, and the workbench reads the idea log directly. Two of `ARCH-012`'s supporting statements
do not hold as written: the default-entry-point split of the prompts was wrong at its own baseline
(corrected in `ARCH-012`), and the report did not weigh the idea-realization plugin, which was being
built during the study, is now complete, and meets some of option B's preconditions while failing
others. The validation does not choose between A, B and C; section 5 re-assesses each, and section 6
proposes the `ARCH-012` wording the owner may adopt before deciding.

## 2. Figures

### 2.1 The four headline figures and the other checked figures

Verdicts: *correct* (right at its baseline and now), *drift* (right at its baseline, changed since),
*error* (wrong at its own baseline).

| Figure (where the study states it) | Study value | At the study's baseline | At tip (`9772c21`) | Verdict | Command |
|---|---|---|---|---|---|
| Governed prompts (`ARCH-012`; rubric; inventory) | 40 | 40 at `7e3a067` and `0c47c27` | 41 (`PROMPT-042` added 2026-09-27) | drift | `git grep -l '^kind: prompt$' <commit> -- docs \| wc -l` |
| Default-entry-point split: direct entries or planning starts / sequence steps / owner-launched campaigns / no known entry (`ARCH-012`; navigation findings) | 13 / 14 / 12 / 1 | 15 / 18 / 7 / 0 at `7e3a067` | 15 / 18 / 8 / 0 (41 prompts) | error (corrected in `ARCH-012`) | Re-classification of every prompt, section 2.2 |
| Registry: implemented / scaffold / planned / retired (`ARCH-012`; portfolio review) | 17 / 4 / 21 / 1 | 17 / 4 / 21 / 1 at `4f3848e` and `0c47c27` | 17 / 4 / 21 / 1 | correct (but see note 1) | `git show <commit>:docs/08-governance/systems.yaml`, count of `status` |
| "The current four-slot claim limit is fully occupied" (`ARCH-012`) | 4 of 4 | 4 of 4 at `4f3848e` and `0c47c27` (`max_active: 4`) | 0 of 4 | drift (see note 2) | `git show <commit>:docs/09-backlog/backlog.yaml`, `max_active` and phases with `status: active` |
| Phases at reconciliation: total; complete / active / deferred / ready / waiting (`ARCH-012`) | 323; 117 / 4 / 8 / 84 / 110 | same at `0c47c27` | 332; 126 / 0 / 8 / 85 / 112, and 1 blocked | drift | `uv run python -m src.governance --backlog` at tip; the same counts from `backlog.yaml` at `0c47c27` |
| Governed documents and memories (`ARCH-012`: 378; review: 377 and 32) | 378; 377 / 32 | 378 at `0c47c27`; 377 / 32 at `4f3848e` | 398 / 34 | drift | `python -m src.governance` in a scratch worktree at each commit |
| Portfolio review phases: complete / active / queued / deferred; ready / waiting | 116 / 4 / 195 / 8; 84 / 111 | same at `4f3848e` | 126 / 0 / 197 / 8; 85 / 112 | drift | `backlog.yaml` at `4f3848e` |
| Plan documents: total; draft / approved / active / complete (review) | 77; 38 / 25 / 11 / 3 | same at `4f3848e` | 81; 40 / 27 / 11 / 3 | drift | `rg -n '^status:' docs/01-plans --glob '*.md'` in a worktree at the commit (see note 3) |
| Registry domains: application / delivery / governance / data / memory (review) | 15 / 11 / 8 / 5 / 4 | same | same | correct | `systems.yaml`, count of `domain` |
| Longest dependency chain: systems / phases (review) | 5 / 14 nodes | 5 / 14 at `4f3848e` | 5 / 14 | correct | Longest-path traversal of `depends_on` in `systems.yaml` and `backlog.yaml` |
| Ready phases that intersect an active lock (review) | 10 of 84 | 10 of 84 at `4f3848e` | 0 of 85 (no active claims) | drift | Ready queued phases whose `systems` meet the active phases' `systems` |
| Systems under active locks (review) | `sys-backlog`, `sys-gov-docs`, `sys-plugin-backlog`, `sys-plugin-generators`, `sys-plugin-ideas` | same at `4f3848e` | none | drift | Union of active phases' `systems` |
| Inventory rows (system inventory) | 43 | 43 at `2fd11e9` | 43 | correct | Row count against `systems.yaml` ids |
| `systems.yaml` unchanged since `2fd11e9` (`ARCH-012`) | empty diff | empty to `0c47c27` | empty to tip | correct | `git diff --stat 2fd11e9 <commit> -- docs/08-governance/systems.yaml` |
| No prompt changed from `7e3a067` to `0c47c27` (`ARCH-012`) | no change | no change | `PROMPT-037` changed, `PROMPT-042` added | correct, then drift | `git diff --stat 7e3a067 <commit> -- docs/02-prompts` |
| "Twenty-three documents are either owner-launched campaigns or sequence steps" (navigation findings) | 23 | 26 (12 + 14 in its own table) | — | error (corrected in the evidence file, with the owner's approval) | Sum of the file's own table |
| "The thirteen direct or planning-start prompts" (navigation findings) | 13 | 13 by the study's own values (9 + 4); 15 on re-classification | 15 | follows the entry-point error | Sum of the file's own table |
| Prompts in `REQ-033` ("39 active prompt documents") | 39 | 39 at `2f736a2`, where `REQ-033` was written | 41 | drift | `git grep -l '^kind: prompt$' 2f736a2 -- docs \| wc -l` |
| Full test suite (every phase record) | 1,115 | 1,115 collected at `13ea2fc` | 1,152 | drift | `pytest --collect-only -q` in a scratch worktree |
| Commits the phase-status log cites (`c389e03`, `2fd80bc`, `986d862`, `dda51e3`, `c620c6f`, `13ea2fc`, `1d8d005`) | exist | all exist and are on `dev` | — | correct | `git merge-base --is-ancestor <c> origin/dev` |

Session-record governance counts of 372, 375 and 376 documents were not re-derived; 377, 378 and 380
were, at `4f3848e`, `0c47c27` and `13ea2fc`.

**Note 1, registry.** The count is correct as a count of the `status` field. Nine of the 21
`planned` entries have built code and completed phases, which the field does not show: the eight
plugin systems (`plugins/idea-realization/`, 102 tracked files at tip, `phase-plug-01` to `-09`
complete) and `sys-demo-overview` (`tools/generate_overview.py`, `phase-demo-03` and `-04`
complete). At the study's own baseline `2fd11e9`, the plugin already had 26 Python files and
`phase-plug-01` and `-05` were complete, and `sys-demo-overview`'s phases were already complete.
The per-system table in section 2.3 marks these nine as contested.

**Note 2, claim load.** At `4f3848e` and `0c47c27` the four active claims were `phase-plug-02`,
`phase-plug-04` and `phase-plug-06` (the plugin build) and the study's own phase (`phase-bnd-03`,
then `phase-bnd-04`). The saturation came from building the plugin and from the study itself.

**Note 3, plan count.** The review's command counts 77 files under `docs/01-plans/`. 79 documents in
`docs/` carry `kind: plan`; the other two are a template
(`docs/00-working/framework/05-schemas/plan.template.md`) and an example inside `GOV-001`, so 77 is
the right count of governed plans. Stated so the difference is not mistaken for an error.

### 2.2 The default-entry-point figure: rule difference and per-prompt values

**The rule difference.** The study's rubric defines the field by the question "Where should a user
begin for the work this prompt covers?", but its pilot assigns `PROMPT-010` by its position in a
sequence ("so it is a sequence-factory step, not a default start"). The rubric names the allowed
values without defining them. The corpus inventory then applied the two readings unevenly. It used
position for the children of the demo factory (`PROMPT-011` to `-013`: sequence steps) and for four
of the five delegation packs. For the children of the demo coordinator it used "where the covered
work begins": `PROMPT-015` and `-017` are marked owner-launched campaigns, although their opening
line is the same wording as `PROMPT-011`'s ("Child of ... read at its Step N"). The same split
separates the `PROMPT-018` delegation pack from its four siblings, and `PROMPT-009` from its twin
`PROMPT-008`. Under neither reading, applied consistently, does 13 / 14 / 12 / 1 reproduce.

**The rule the validation applied.** The pilot's positional reading, applied to every prompt: a
prompt read or dispatched from inside another prompt's sequence is a sequence step; a prompt the
owner pastes to launch one dated, bounded build or campaign is an owner-launched campaign; a prompt
that starts a session whose output is planning documents is a planning start; a prompt run on its
own recurring trigger is a direct entry.

**How it was checked.** A `partition-analyst` agent classified all 40 prompts at `0c47c27`
(identical in `docs/02-prompts/` to `7e3a067`) without seeing the study's inventory. Its split was
14 / 20 / 6 / 0. I then read every prompt where it or I disagreed with the study. Its values and
mine differ on the planning-versus-direct line and on three close calls. They agree on the six firm
changes below, and neither reproduces the study's figure.

Nine rows change. Six are firm: the study's value is unsupported by the prompt's text, or
inconsistent with its treatment of a structurally identical prompt (`PROMPT-001`, `-009`, `-015`,
`-017`, `-018`, `-037`). Three are close calls (`PROMPT-016`, `-022`, `-030`). If all three close
calls went the study's way, the split would be 15 / 15 / 9 / 1, which still differs from
13 / 14 / 12 / 1. The corrected figure in `ARCH-012` is 15 / 18 / 7 / 0. The tip adds `PROMPT-042`,
an owner-launched campaign, giving 15 / 18 / 8 / 0 of 41. `PROMPT-037` changed after the study; the
change added contract items and did not move its entry point.

The finding that navigation depends on the reading still stands: 25 of the 40 prompts are sequence
steps or campaigns under the corrected values, against the study's 26.

| Prompt | Study value | Validation value | Agreement | Basis |
|---|---|---|---|---|
| PROMPT-001 | sequence-factory-step | direct-operational-entry | firm | 'Feed this prompt to a Claude instance' (line 17); no document names it as a step |
| PROMPT-002 | planning-sequence-start | planning-sequence-start | agree | definition session ending in requirement, plan and phases |
| PROMPT-003 | planning-sequence-start | planning-sequence-start | agree | ends in ADRs and phases; close call: requires PROMPT-004 first |
| PROMPT-004 | planning-sequence-start | planning-sequence-start | agree | first of the 004 then 003 sequence; close call: writes content, not a plan |
| PROMPT-005 | planning-sequence-start | planning-sequence-start | agree | ends in one ADR and phases; close call: run after PROMPT-004 |
| PROMPT-006 | direct-operational-entry | direct-operational-entry | agree | rubric pilot |
| PROMPT-007 | planning-sequence-start | planning-sequence-start | agree | turns a triaged idea into a requirement, plan and phases |
| PROMPT-008 | direct-operational-entry | direct-operational-entry | agree | 'run it repeatedly to advance the backlog' |
| PROMPT-009 | planning-sequence-start | direct-operational-entry | firm | 'Reusable, and deliberately read-only. Run it periodically' (line 20), the same framing as PROMPT-008 |
| PROMPT-010 | sequence-factory-step | sequence-factory-step | agree | rubric pilot |
| PROMPT-011 | sequence-factory-step | sequence-factory-step | agree | 'Child of ... PROMPT-010, read at its Step 1' |
| PROMPT-012 | sequence-factory-step | sequence-factory-step | agree | 'Child of ... PROMPT-010, read at its Step 2' |
| PROMPT-013 | sequence-factory-step | sequence-factory-step | agree | 'Child of ... PROMPT-010, read at its Steps 3 and 4' |
| PROMPT-014 | owner-launched-campaign | owner-launched-campaign | agree | the demo build's pasted coordinator; no separate kick-off |
| PROMPT-015 | owner-launched-campaign | sequence-factory-step | firm | 'Child of ... PROMPT-014, read at its Step 1', the wording the inventory marks as a step for PROMPT-011 |
| PROMPT-016 | no-default-known | sequence-factory-step | close | 'Child of ... PROMPT-014. Binding on the coordinator'; the study read it as a reference with no start |
| PROMPT-017 | owner-launched-campaign | sequence-factory-step | firm | 'Child of ... PROMPT-014, read at its Step 3' |
| PROMPT-018 | owner-launched-campaign | sequence-factory-step | firm | delegation pack 'Every prompt the build coordinator sends', the shape of 021, 024, 029 and 032, all steps in the inventory |
| PROMPT-019 | owner-launched-campaign | owner-launched-campaign | agree | single dated dispatch for phase-demo-07; close call with a direct entry |
| PROMPT-020 | planning-sequence-start | planning-sequence-start | agree | rubric pilot |
| PROMPT-021 | sequence-factory-step | sequence-factory-step | agree | delegation pack |
| PROMPT-022 | owner-launched-campaign | sequence-factory-step | close | coordinator; its kick-off PROMPT-023 is what is pasted and 'wins' where they differ |
| PROMPT-023 | owner-launched-campaign | owner-launched-campaign | agree | pasteable kick-off for the workbench build |
| PROMPT-024 | sequence-factory-step | sequence-factory-step | agree | delegation pack |
| PROMPT-025 | planning-sequence-start | planning-sequence-start | agree | Prompt A pre-plan package |
| PROMPT-026 | sequence-factory-step | sequence-factory-step | agree | Prompt B factory |
| PROMPT-027 | planning-sequence-start | planning-sequence-start | agree | Prompt A pre-plan package |
| PROMPT-028 | sequence-factory-step | sequence-factory-step | agree | Prompt B factory |
| PROMPT-029 | sequence-factory-step | sequence-factory-step | agree | delegation pack |
| PROMPT-030 | owner-launched-campaign | sequence-factory-step | close | coordinator; its kick-off PROMPT-031 is what is pasted |
| PROMPT-031 | owner-launched-campaign | owner-launched-campaign | agree | kick-off record for the literature review |
| PROMPT-032 | sequence-factory-step | sequence-factory-step | agree | delegation pack |
| PROMPT-033 | owner-launched-campaign | owner-launched-campaign | agree | kick-off record for idea batching |
| PROMPT-034 | sequence-factory-step | sequence-factory-step | agree | pack a workflow dispatches verbatim |
| PROMPT-035 | owner-launched-campaign | owner-launched-campaign | agree | dated one-run review kickoff |
| PROMPT-036 | direct-operational-entry | direct-operational-entry | agree | generic, idempotent coordinator the owner pastes every batch |
| PROMPT-037 | sequence-factory-step | direct-operational-entry | firm | 'a kickoff the owner pastes into the Session Manager session' (lines 17-20); nothing sequences it |
| PROMPT-038 | sequence-factory-step | sequence-factory-step | agree | dispatch prompt for GOV-018 step 3 |
| PROMPT-040 | owner-launched-campaign | owner-launched-campaign | agree | rubric pilot |
| PROMPT-041 | direct-operational-entry | direct-operational-entry | agree | phase runner for this study, run directly each session |
| PROMPT-042 | (not in study) | owner-launched-campaign | new | dated investigation pack with an owner-pasted kickoff (lines 596-607) |

### 2.3 Per-system concern table

The concern of every registered system, from the study's system inventory
(`system-interface-inventory.md`), which gives one disposition per system; `systems.yaml` has no
concern field. Every system is placed, so no row is *unplaced*. Nine rows are marked *contested*:
the inventory's disposition follows its own evidence rule (the registry entry), but tracked code and
completed phases contradict the registry status that rule relied on. The HTML overview's concern map
draws from this table.

| System | Registry status at tip | Concern | Source of the assignment |
|---|---|---|---|
| `sys-brain` | implemented | personal-productivity core | system-interface-inventory.md, `sys-brain` row |
| `sys-capture` | scaffold | personal-productivity core | system-interface-inventory.md, `sys-capture` row |
| `sys-portfolio` | implemented | personal-productivity core | system-interface-inventory.md, `sys-portfolio` row |
| `sys-retrieval` | implemented | personal-productivity core | system-interface-inventory.md, `sys-retrieval` row |
| `sys-realization` | planned | idea-realization core | system-interface-inventory.md, `sys-realization` row |
| `sys-demo-stage` | implemented | workbench core | system-interface-inventory.md, `sys-demo-stage` row |
| `sys-ui` | scaffold | workbench core | system-interface-inventory.md, `sys-ui` row |
| `sys-wb-explorers` | implemented | workbench core | system-interface-inventory.md, `sys-wb-explorers` row |
| `sys-wb-layout` | implemented | workbench core | system-interface-inventory.md, `sys-wb-layout` row |
| `sys-wb-notes` | implemented | workbench core | system-interface-inventory.md, `sys-wb-notes` row |
| `sys-wb-shared` | implemented | workbench core | system-interface-inventory.md, `sys-wb-shared` row |
| `sys-wb-styles` | implemented | workbench core | system-interface-inventory.md, `sys-wb-styles` row |
| `sys-wb-terminal` | implemented | workbench core | system-interface-inventory.md, `sys-wb-terminal` row |
| `sys-wb-viewer` | implemented | workbench core | system-interface-inventory.md, `sys-wb-viewer` row |
| `sys-backlog` | implemented | cross-cutting framework | system-interface-inventory.md, `sys-backlog` row |
| `sys-delivery` | implemented | cross-cutting framework | system-interface-inventory.md, `sys-delivery` row |
| `sys-gov-docs` | implemented | cross-cutting framework | system-interface-inventory.md, `sys-gov-docs` row |
| `sys-governance` | implemented | cross-cutting framework | system-interface-inventory.md, `sys-governance` row |
| `sys-api` | scaffold | shared foundation | system-interface-inventory.md, `sys-api` row |
| `sys-contracts` | implemented | shared foundation | system-interface-inventory.md, `sys-contracts` row |
| `sys-projection` | implemented | shared foundation | system-interface-inventory.md, `sys-projection` row |
| `sys-demo-kit` | planned | adjacent | system-interface-inventory.md, `sys-demo-kit` row |
| `sys-fw-templates` | planned | adjacent | system-interface-inventory.md, `sys-fw-templates` row |
| `sys-plugin` | planned | adjacent | system-interface-inventory.md, `sys-plugin` row; contested: registry says planned, but plugins/idea-realization/ exists; phase-plug-01 to -09 complete |
| `sys-research` | scaffold | adjacent | system-interface-inventory.md, `sys-research` row |
| `sys-auto-gateway` | planned | incubating | system-interface-inventory.md, `sys-auto-gateway` row |
| `sys-auto-ledger` | planned | incubating | system-interface-inventory.md, `sys-auto-ledger` row |
| `sys-demo-overview` | planned | incubating | system-interface-inventory.md, `sys-demo-overview` row; contested: registry says planned, but tools/generate_overview.py exists; phase-demo-03 and -04 complete |
| `sys-fw-analysis-patterns` | planned | incubating | system-interface-inventory.md, `sys-fw-analysis-patterns` row |
| `sys-fw-analysis-protocol` | planned | incubating | system-interface-inventory.md, `sys-fw-analysis-protocol` row |
| `sys-fw-analysis-sessions` | planned | incubating | system-interface-inventory.md, `sys-fw-analysis-sessions` row |
| `sys-html` | planned | incubating | system-interface-inventory.md, `sys-html` row |
| `sys-memory-agents` | planned | incubating | system-interface-inventory.md, `sys-memory-agents` row |
| `sys-plugin-absolutes` | planned | incubating | system-interface-inventory.md, `sys-plugin-absolutes` row; contested: registry says planned, but phase-plug-07 and -09 complete |
| `sys-plugin-backlog` | planned | incubating | system-interface-inventory.md, `sys-plugin-backlog` row; contested: registry says planned, but phase-plug-04 complete |
| `sys-plugin-core` | planned | incubating | system-interface-inventory.md, `sys-plugin-core` row; contested: registry says planned, but phase-plug-01 and -08 complete |
| `sys-plugin-documents` | planned | incubating | system-interface-inventory.md, `sys-plugin-documents` row; contested: registry says planned, but phase-plug-05 complete |
| `sys-plugin-generators` | planned | incubating | system-interface-inventory.md, `sys-plugin-generators` row; contested: registry says planned, but phase-plug-06 complete |
| `sys-plugin-ideas` | planned | incubating | system-interface-inventory.md, `sys-plugin-ideas` row; contested: registry says planned, but phase-plug-02 complete |
| `sys-plugin-partition` | planned | incubating | system-interface-inventory.md, `sys-plugin-partition` row; contested: registry says planned, but phase-plug-03 complete |
| `sys-signals` | planned | incubating | system-interface-inventory.md, `sys-signals` row |
| `sys-synthesis` | planned | incubating | system-interface-inventory.md, `sys-synthesis` row |
| `sys-course` | retired | retired | system-interface-inventory.md, `sys-course` row |

Per concern at tip: personal-productivity core 4 (3 implemented, 1 scaffold); idea-realization core
1 (planned); workbench core 9 (8 implemented, 1 scaffold); cross-cutting framework 4 (implemented);
shared foundation 3 (2 implemented, 1 scaffold); adjacent 4 (3 planned, 1 scaffold); incubating 17
(planned); retired 1.

## 3. Plan-altitude review (`GOV-018`)

Record: [`docs/08-governance/reviews/2026-09-28-plan-050.json`](../../08-governance/reviews/2026-09-28-plan-050.json).
Entry check on the `PLAN-050` overview: pass (exit 0). The adversary was `partition-adversary`
dispatched with `PROMPT-038` at the plan altitude, reading the five children as part of the plan,
with two additions to its brief: re-derive the four headline figures, and attack the case for
rejecting C and recommending A. `target.phases` is empty because all five phases are complete. The
record's `notes` state both departures from `GOV-018`.

| Id | Severity | Finding (one line) | Disposition |
|---|---|---|---|
| F01 | blocker | `ARCH-012`'s claim that no concern is ready for extraction is contradicted by the built idea-realization plugin | escalated-g3: the plan adds `phase-bnd-10`; the `ARCH-012` wording change is proposed in section 6, for the owner |
| F02 | major | The corpus-wide entry-point classification is inconsistent across structurally identical prompts | fixed: `ARCH-012` figure corrected; per-prompt table in section 2.2; `phase-bnd-08` defines the values. One of its four examples (`PROMPT-025`) is wrong and is noted in the disposition |
| F03 | major | No decision in the plan names its rejected alternative and cost (`GOV-010` P2) | fixed: `PLAN-050` overview, *Chosen design* table |
| F04 | major | No stage, gate or check says what happens when it fails | fixed: *When a check fails* paragraphs in the overview and all five children |
| F05 | minor | "40 governed prompts" is drift | accepted-no-change: drift is reported, not edited |
| F06 | minor | "four-slot claim limit fully occupied" is drift | accepted-no-change: reported, with the note on who held the slots |

The later-added-phase altitude ran over the deferred next-step phases (section 7 and the record):

| Id | Severity | Finding (one line) | Disposition |
|---|---|---|---|
| F07 | blocker | `phase-bnd-07` edits the registry, which `ARCH-012`'s option-A row says choosing A does not cause | fixed: `phase-bnd-07` now also needs the owner's separate approval of the registry change |
| F08 | major | `phase-bnd-08` combines two phases' work plus an independent check in one session | fixed: split into `phase-bnd-08` and `phase-bnd-14` |
| F09 | minor | `phase-bnd-09` has no constructed case that must fail | fixed: a control question with no tracked answer must be recorded as a miss |

**Departure from `GOV-018`, stated.** Step 2 reviews only `queued`, `waiting` or `blocked` phases at
the later-added altitude. The next-step phases are `deferred`, so that `--ready` does not offer them
before the owner decides, and they were reviewed anyway because the owner will rely on them.
`phase-bnd-14` was created by splitting `phase-bnd-08` in answer to F08 and had no separate dispatch.
The final adversarial review of this report (handoff file) was asked to read it.

## 4. Phase-level findings (retrospective)

`PROMPT-038`'s six phase checks, applied to the five completed phases, plus whether each phase's
evidence file meets the `REQ-033` row it claims and whether its session record matches the evidence.
These findings stay here and are not in the review record, by the owner's ruling.

| # | Phase | Severity | Finding | Evidence |
|---|---|---|---|---|
| P1 | `phase-bnd-01` | major | The inventory's evidence rule used registry text only. Rows for systems whose `planned` status tracked code contradicts say "No implemented writer" or "planned plugin sub-area" instead of *unknown*, against `REQ-033` R01 ("rows lacking evidence are marked unknown rather than inferred"). | At `2fd11e9`: 26 Python files under `plugins/`; `phase-plug-01` and `-05` complete; `phase-demo-03` and `-04` complete with `tools/generate_overview.py` present. The `sys-demo-overview` row says "planned despite named source inputs". |
| P2 | `phase-bnd-01` | major | The boundary map omits a current crossing: the workbench API reads idea state from the idea log through `fold()`. `REQ-033` R02 requires every inter-concern edge to be labelled. | `git show 2fd11e9:src/api/routes/workbench.py`, line 532 `return fold(load_events())`. The map's only workbench edges are to the shared foundation and from the framework. Its read of `backlog.yaml` (line 179) is covered by the framework edge "repository-state inputs". |
| P3 | all five | minor | No acceptance line names a case that must fail (`GOV-010` P6; `PLAN-050` was written after `GOV-010`'s 2026-09-22 cut-off). | The `acceptance` lists of `phase-bnd-01` to `-05` in `backlog.yaml`. |
| P4 | `phase-bnd-02` | major | The rubric names each field's allowed values but defines none. For the entry-point field, its assignment question conflicts with its own `PROMPT-010` pilot. This is the root cause of P6. `REQ-033` R03's verification ("defines each field's allowed values") is met only by naming. | `prompt-classification-rubric.md`, the field table and the `PROMPT-010` rationale. |
| P5 | `phase-bnd-02` | minor | The title says "Classify the governed prompt corpus", but the scope stops after a four-prompt pilot. | `backlog.yaml`, `phase-bnd-02` `title` and last `scope` line. |
| P6 | `phase-bnd-05` | major | Entry-point values are inconsistent across structurally identical prompts (section 2.2). Row citations are whole-document line ranges (for example `PROMPT-018:15-1345`), so no row outside the pilots shows why a field was assigned. | `prompt-corpus-inventory.md`, Evidence column. |
| P7 | `phase-bnd-05` | minor | Arithmetic error in the navigation findings ("Twenty-three"; the table gives 26). Corrected with the owner's approval. | `prompt-navigation-findings.md`, finding 1. |
| P8 | `phase-bnd-03` | major | The work-in-progress measure reports 4 of 4 slots and names the locked systems, but does not say that three claims were plugin build phases and one was the study itself. `ARCH-012` then reads saturation as support for a single repository. | Note 2 in section 2.1. |
| P9 | `phase-bnd-03` | minor | It declares `sys-backlog` but changes no backlog content beyond its own record, so it held a lock it did not need. | `backlog.yaml`, `phase-bnd-03` `systems`; `SESS-2026-09-26-06` scope boundary. |
| P10 | `phase-bnd-04` | blocker (same defect as F01) | The reconciliation checked `systems.yaml` text and prompt files only. It did not check code or backlog state, so the plugin build under way (three of the four active claims) was not weighed. | `ARCH-012`, *Evidence and reconciliation*; `backlog.yaml` at `0c47c27`, `phase-plug-*` statuses. |
| P11 | `phase-bnd-04` | minor | Its `verification` lists `--next-code architecture`, which reserves a code: an action, not a check. Its `deliverables` lock all of `docs/07-architecture/`. | `backlog.yaml`, `phase-bnd-04`. |

**Requirement rows.** R01 is partly met (one disposition per system, but P1). R02 is partly met
(P2). R03 is partly met (P4, P6). R04 is met, with an interpretation gap (P8). R05 and R06 are met.
R07 is partly met: the reconciliation reported backlog drift but not code-state drift (P10).

**Session records against evidence.** Every stated result I re-derived matches: 43 inventory rows;
40 prompts; 1,115 tests; governance counts of 377, 378 and 380 documents; 323 phases with the
stated splits; depth 5 and 14. The plugin's own suite was also run at tip, because it bears on
option B: `cd plugins/idea-realization && pytest` gives 3 failed, 494 passed
(`test_no_source_references.py::test_plugin_names_no_source_instance` and two parametrised cases of
`test_templates.py`). CI does not run that suite: `pyproject.toml` sets `testpaths = ["test"]`.

## 5. Options A, B and C re-assessed

Two facts from after the study bear on all three options. First, the owner reworded the project
purpose on 2026-09-27 so that the idea realization engine leads and personal consulting management is
secondary, and names the plugin as the portable form of the pipeline (`CLAUDE.md`, commit
`518188a`). `REQ-033`'s accepted decisions started from the opposite order. Second, the plugin build
finished: `phase-plug-01` to `-09` are complete.

**A. Keep one repository with explicit contracts.**
*For:* the idea-realization core, now the stated primary concern, holds one registered system, and
it is planned (section 2.3), so there is nothing implemented to separate. The idea log belongs to the
personal-productivity core and is read by the workbench API (`fold()`) and, as its source, by the
pipeline. The backlog and governance check constrain every concern. Atomic changes across these are cheap in
one repository.
*Against:* the registry the contracts would start from is stale for 9 of its 21 planned entries;
the study's map omits one current crossing; and the prompt navigation problem is larger than the
study's figure showed.
*What would have to be true to choose it:* no concern has an audience or release cadence of its own
today, and the contracts can be written and checked inside one repository. The corrected evidence
supports both, with the plugin as the one open question.

**B. Prepare selective extraction.**
*For:* the plugin is already packaged separately: its own directory, `pytest.ini` and README with
install, scaffold and doctor steps; 497 tests; an end-to-end exercise in a scratch repository
(`phase-plug-08`). Its registry description says nothing in this repository depends on it. It meets
the "documented contract" and "independent tests" preconditions at least in part, which the study
did not record.
*Against:* its tests are not run by CI and 3 fail at tip. No audience beyond the owner's private
installation, and no release cadence or maintainer other than the owner, is recorded. It is a copy
adapted for target repositories, so it may need no repository of its own: it is separable already.
`ARCH-012`'s option B text keeps "the personal core authoritative" and says "realization remains
integrated", which reads differently after the 2026-09-27 purpose change.
*What would have to be true to choose it:* the plugin, or another candidate, meets all five
preconditions in `ARCH-012`, above all an audience and a release cadence that the one-repository
layout blocks. `phase-bnd-10` measures that.

**C. Split now into four repositories.**
*For:* formal isolation and independent versioning in principle.
*Against:* stronger than the study stated. The realization repository would receive one planned
system and no implemented code. The idea log would have to live in one repository and be read from
two others. Governance would be duplicated four ways, or shared across repositories (`phase-bnd-13` would
design which). All work is claimed today through one backlog lock table.
*What would have to be true to choose it:* every concern has implemented systems, its own data
authority, and a release need, with migration resources. The evidence shows none of these for the
realization core.

**Does the evidence require a different recommendation?** No. The corrections leave A the
lowest-cost fit and strengthen the rejection of C. They do require `ARCH-012` to stop saying that no
candidate exists and to name the plugin's position against option B's preconditions (section 6).
The owner decides.

## 6. Proposed changes to `ARCH-012` beyond figures

Not applied: the owner's 2026-09-27 ruling limits this session's `ARCH-012` edits to figure
corrections. Each is offered for the owner to adopt at G3 (review finding F01).

1. *Decision purpose*, the recommendation paragraph. Current: "The evidence does not show an
   independently operated concern with a stable enough runtime contract, release cadence, or
   audience to justify immediate separation."
   Proposed: "The evidence does not show an independently operated concern with a stable enough
   runtime contract, release cadence, or audience to justify immediate separation. The nearest
   candidate is the idea-realization plugin (`plugins/idea-realization/`): it is packaged for
   installation into other repositories and carries its own test suite, but on 2026-09-28 CI did
   not run that suite, three of its tests failed, and no audience or release cadence beyond the
   owner was recorded."
2. *Evidence and reconciliation*. Current: "so its 43-system ownership and interface evidence
   remains current."
   Proposed: "so the registry text behind its 43-system ownership and interface evidence is
   unchanged. The registry's `planned` status no longer matches tracked code for nine entries: the
   eight plugin systems, whose build phases were under way at this revision, and
   `sys-demo-overview`, whose build phases were already complete."
3. *Prompt and portfolio implications*. Current: "The phase graph is deeper than the system graph,
   and the current four-slot claim limit is fully occupied. Those facts support a contract-first,
   single-repository approach:"
   Proposed: "The phase graph is deeper than the system graph. At the reconciled revision all four
   claim slots were occupied, three by the plugin build and one by this study, which shows the claim
   limit binding rather than coupling between the concerns. The depth of the phase graph supports a
   contract-first, single-repository approach:"
4. *Boundary options*, option B's first column. Current: "Keep the personal core authoritative;
   extract only a stable workbench or framework capability when proven; realization remains
   integrated until its orchestration contract is real."
   Proposed: "Keep the source records (portfolio and idea log) authoritative in this repository;
   extract only a capability whose contract is proven (the idea-realization plugin, the workbench
   or the framework); the realization orchestrator remains integrated until its contract is real."
5. *Proposed concern boundaries*, the paragraph after the table. Current: "the workbench uses APIs
   and the loopback-gated terminal backend;"
   Proposed: "the workbench uses APIs and the loopback-gated terminal backend, and its API reads idea
   state through `fold()` and `backlog.yaml` directly (`src/api/routes/workbench.py`);"
6. *Owner decision gate*, "First portability candidate" row, recommendation. Current: "Do not
   nominate one yet".
   Proposed: "Do not nominate one before the candidate assessment (`phase-bnd-10`); the
   idea-realization plugin is the only candidate already packaged separately."
7. *Constraints and limits*, a new last bullet: "The study started from the owner's history, with
   personal productivity as the original concern (`REQ-033`, accepted decisions). On 2026-09-27 the
   owner reworded the project purpose so that the idea realization engine leads (`CLAUDE.md`). The
   options do not depend on that order, but option B's first candidate and the order of the concern
   table do."

## 7. What this validation changed

- `ARCH-012`: the default-entry-point split corrected from 13 / 14 / 12 / 1 to 15 / 18 / 7 / 0, old
  values kept in the text with the date; `updated` set to 2026-09-28. No reasoning, option or
  recommendation changed.
- `prompt-navigation-findings.md`: "Twenty-three" corrected to "Twenty-six", with a dated note (owner
  approved).
- `PLAN-050` overview: dated amendment note; a rejected-alternatives table under *Chosen design*;
  *Next steps after the owner's decision* with the deferred phases per option; a requirement
  coverage row for them; concurrency for them; *When a check fails*; three new open questions.
- `PLAN-050.01` to `.05`: a *When a check fails* paragraph each; `PLAN-050.02` and `.03` gain the
  *Execution order and real concurrency* section the entry check requires.
- `backlog.yaml`: `phase-bnd-06` to `phase-bnd-14`, all `deferred`, `priority: 4`, none in
  `next_up`. `--ready` offers none of them. Governance: 341 phases.
- Review record `2026-09-28-plan-050.json`: nine findings, all dispositioned.

## 8. HTML overview

[`boundary-overview.html`](boundary-overview.html): the concern map, crossings, registry maturity,
prompt entry points, backlog and claim load, options, figures check and next steps on one page.
Generated by [`build_boundary_overview.py`](build_boundary_overview.py), which reads every count
from git at the commits named above. The only hand-entered values are the per-prompt
classification in section 2.2.
