# System Boundary Study — Prompt Classification Rubric and Pilot

## Baseline and boundary

- **Baseline:** `6be599416d1bfcf7af517cc0f58ab2c4cd3c1334` on `agent/phase-bnd-02`, recorded 2026-09-26.
- **Count:** 40 governed prompts, measured with `rg -l '^kind: prompt$' docs | wc -l` at that revision.
- **Boundary:** This is a field model and four-prompt pilot only. It changes no prompt, status, or lifecycle record; `phase-bnd-05` owns the full corpus inventory.
- **Evidence rule:** Assign a value only when the prompt or a cited governance record supports it. Use `unknown` rather than infer. An `active` document status is lifecycle state, not a reuse, precedent, review, or navigation classification.

## Independent fields

Each prompt receives one value for each field. The fields are independent: for example, a prompt can be an operational procedure, reusable as-is, canonical, directly runnable, and a direct entry point. A campaign record can be a review campaign, require review before rerun, and be owner-launched.

| Field | Allowed values | Assignment question |
| --- | --- | --- |
| Operational role | `operational-procedure`, `planning-input`, `artifact-factory`, `build-coordinator`, `review-campaign`, `reference-or-other`, `unknown` | What job does the prompt direct at this snapshot? |
| Reuse disposition | `run-as-is-recurring`, `adaptable-pattern`, `campaign-specific-record`, `unknown` | May a future user run it unchanged, adapt its pattern, or retain it mainly as a bounded record? |
| Precedent status | `canonical-current`, `named-precedent`, `historical-or-campaign-evidence`, `unknown` | Does the repository present it as a current canonical entry, name it as a precedent, or retain it as dated evidence? |
| Review disposition | `direct-run`, `review-and-adapt`, `review-before-rerun`, `unknown` | Can it be selected under its stated prerequisites, does it need adaptation, or must campaign conditions first be reviewed? |
| Default entry point | `direct-operational-entry`, `planning-sequence-start`, `sequence-factory-step`, `owner-launched-campaign`, `no-default-known`, `unknown` | Where should a user begin for the work this prompt covers? |

`unknown` is valid in every field. The corpus phase must preserve it and must not collapse the five fields into a single prompt type.

## Pilot assignments

| Prompt | Operational role | Reuse disposition | Precedent status | Review disposition | Default entry point |
| --- | --- | --- | --- | --- | --- |
| PROMPT-006 | `operational-procedure` | `run-as-is-recurring` | `canonical-current` | `direct-run` | `direct-operational-entry` |
| PROMPT-010 | `artifact-factory` | `adaptable-pattern` | `named-precedent` | `review-and-adapt` | `sequence-factory-step` |
| PROMPT-020 | `planning-input` | `adaptable-pattern` | `named-precedent` | `review-and-adapt` | `planning-sequence-start` |
| PROMPT-040 | `review-campaign` | `campaign-specific-record` | `historical-or-campaign-evidence` | `review-before-rerun` | `owner-launched-campaign` |

### PROMPT-006 — Capture and triage ideas

- **Role and reuse:** It directs capture and triage, excludes planning and building, and says it is reusable whenever ideas need recording or scouting (`docs/02-prompts/PROMPT-006-idea-capture-and-triage.md:19-25,35-36`). That supports a run-as-is recurring operational procedure.
- **Precedent and review:** It is the first current entry in a four-prompt path (`docs/02-prompts/PROMPT-006-idea-capture-and-triage.md:19-22`) and gives executable instructions, not a historical campaign account. No prompt-local adaptation or owner review gate precedes use, so it is canonical-current and direct-run.
- **Entry point:** Its recurring trigger is a user with ideas to record or open ideas to scout (`docs/02-prompts/PROMPT-006-idea-capture-and-triage.md:24-25`), making it the direct operational entry for that task.

### PROMPT-010 — Demo agent factory

- **Role:** It creates governance documents, agent definitions, and delegation prompts for a later build, not implementation code (`docs/02-prompts/PROMPT-010-demo-agent-factory.md:19-23,40-43`); it is an artifact factory.
- **Reuse and precedent:** It is single-use in the dated demo but explicitly reusable in the factory pattern (`docs/02-prompts/PROMPT-010-demo-agent-factory.md:25-26`). The methodology names it as the factory precedent (`docs/08-governance/GOV-008-prompt-pack-protocol.md:20-24`), supporting adaptable-pattern and named-precedent.
- **Review and entry point:** Its body contains dated checkout and peer assumptions (`docs/02-prompts/PROMPT-010-demo-agent-factory.md:45-57`), requiring review-and-adapt. The methodology puts it after the owner’s pre-plan package as Prompt B (`docs/08-governance/GOV-008-prompt-pack-protocol.md:29-38`), so it is a sequence-factory step, not a default start.

### PROMPT-020 — Workbench pre-plan package

- **Role:** It carries ratified owner input into a planning session and explicitly says it is not implementation (`docs/02-prompts/PROMPT-020-workbench-pre-plan-package.md:17-23`), so it is a planning input.
- **Reuse and precedent:** The protocol identifies it as the pre-plan-package precedent (`docs/08-governance/GOV-008-prompt-pack-protocol.md:29-38`). Its durable value is an adaptable pattern and named precedent, while dated workbench decisions require review before reuse (`docs/02-prompts/PROMPT-020-workbench-pre-plan-package.md:36-59`).
- **Review and entry point:** It directs the owner to paste the prompt into a fresh planning session and stop before a build starts (`docs/02-prompts/PROMPT-020-workbench-pre-plan-package.md:30-34,176-186`). It is therefore a planning-sequence start but requires review-and-adapt for a new build.

### PROMPT-040 — Gemini review sequence

- **Role:** It directs a three-part external analysis campaign with named output areas (`docs/02-prompts/PROMPT-040-gemini-review-sequence.md:19-27`), making it a review campaign.
- **Reuse and precedent:** It is dated and tied to named Gemini worktrees, branches, and output paths (`docs/02-prompts/PROMPT-040-gemini-review-sequence.md:37-45`). No source names it as a general reusable precedent, so it is classified as a campaign-specific record and historical-or-campaign evidence rather than assumed reusable.
- **Review and entry point:** It requires merged inputs and assumes Gemini CLI with shell, git, uv, and push access (`docs/02-prompts/PROMPT-040-gemini-review-sequence.md:29-35`), which requires review before rerun. The owner launches the master prompt (`docs/02-prompts/PROMPT-040-gemini-review-sequence.md:59-85`), making it owner-launched-campaign.

## Pilot limits for the corpus phase

- `active` cannot determine the five fields: PROMPT-006 is a direct recurring operation, PROMPT-010 and PROMPT-020 are named precedents, and PROMPT-040 is a bounded campaign record.
- A prompt may have a reusable shape while still requiring review because dated scope, prerequisites, or repository instructions make a literal rerun unsafe.
- The corpus phase should retain the pilot assignments and citations, and use `unknown` wherever a prompt does not establish an assignment.
