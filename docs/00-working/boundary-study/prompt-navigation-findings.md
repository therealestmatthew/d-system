# System Boundary Study — Prompt Navigation Findings

## Evidence basis

This finding is derived from the 40-row [prompt corpus inventory](prompt-corpus-inventory.md) at
`7e3a06789458dfbb44bd79894e81f8662488203f`. The classifications are independent fields; totals
below are counts of the default-entry-point field, not a lifecycle taxonomy.

## Observed navigation shape

| Default entry point | Count | Reading |
| --- | ---: | --- |
| owner-launched-campaign | 12 | Dated demo, workbench, literature-review, and review runs begin with owner-controlled context and prerequisites. |
| sequence-factory-step | 14 | Factories and delegation packs are useful within an established sequence, but are not safe standalone starts. |
| planning-sequence-start | 9 | Pre-plan and planning inputs form the most visible reusable route into new planning work. |
| direct-operational-entry | 4 | PROMPT-006, PROMPT-008, PROMPT-036, and PROMPT-041 expose recurring operational work. |
| no-default-known | 1 | The demo guardrail reference documents constraints rather than a start point. |
| total | 40 | Reconciles to the measured corpus. |

## Findings and limits

1. The corpus is not one menu of interchangeable commands. Twenty-six documents are either
   owner-launched campaigns or sequence steps, so presenting all `active` prompts as directly
   runnable would discard their recorded prerequisites.
   *Corrected 2026-09-28, with the owner's approval: this read "Twenty-three", but the table above
   gives 12 + 14 = 26. The table itself is unchanged; the independent validation's re-classification
   of the entry-point field is in [the validation report](validation-report.md), section 2.*
2. The thirteen direct or planning-start prompts provide a small navigable operating core;
   the remainder mainly preserves reusable patterns or evidence of bounded campaigns.
3. Reuse and review remain intentionally non-exclusive: adaptable patterns frequently require
   review because their source material carries dated assumptions. No classification recommends a
   lifecycle-status change.
4. The inventory records navigation only from tracked text. It does not measure actual user
   behavior, discoverability in a UI, or whether an unrecorded owner workflow exists.

## Question for the final report

If prompt navigation is made more explicit later, the owner can decide whether to publish a
separate operating index that routes to direct entries and planning starts while retaining campaign
records as evidence. That would be a future decision, not an action in this phase.
