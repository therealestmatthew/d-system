# System Boundary Study — Prompt Corpus Inventory

## Snapshot and method

- **Baseline:** `7e3a06789458dfbb44bd79894e81f8662488203f` on `agent/phase-bnd-05`, 2026-09-26.
- **Measurement:** `rg -l '^kind: prompt$' docs | wc -l` returned **40**.
- **Method:** Applied the five independent fields from [the accepted rubric](prompt-classification-rubric.md) without changing a prompt or its lifecycle status. `unknown` remains available, but no row needed it: each document's stated purpose and execution posture supported a conservative assignment.
- **Citation convention:** Every row cites its prompt's title and operating material; the four pilot rows retain the fuller, prompt-local rationale in the rubric.

| Prompt | Operational role | Reuse disposition | Precedent status | Review disposition | Default entry point | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| PROMPT-001 | artifact-factory | adaptable-pattern | named-precedent | review-and-adapt | sequence-factory-step | `PROMPT-001:18-147` |
| PROMPT-002 | planning-input | adaptable-pattern | named-precedent | review-and-adapt | planning-sequence-start | `PROMPT-002:15-191` |
| PROMPT-003 | review-campaign | adaptable-pattern | named-precedent | review-and-adapt | planning-sequence-start | `PROMPT-003:15-146` |
| PROMPT-004 | planning-input | adaptable-pattern | named-precedent | review-and-adapt | planning-sequence-start | `PROMPT-004:15-134` |
| PROMPT-005 | review-campaign | adaptable-pattern | named-precedent | review-and-adapt | planning-sequence-start | `PROMPT-005:15-96` |
| PROMPT-006 | operational-procedure | run-as-is-recurring | canonical-current | direct-run | direct-operational-entry | rubric pilot; `PROMPT-006:17-104` |
| PROMPT-007 | planning-input | run-as-is-recurring | canonical-current | direct-run | planning-sequence-start | `PROMPT-007:17-111` |
| PROMPT-008 | operational-procedure | run-as-is-recurring | canonical-current | direct-run | direct-operational-entry | `PROMPT-008:17-109` |
| PROMPT-009 | review-campaign | adaptable-pattern | named-precedent | review-and-adapt | planning-sequence-start | `PROMPT-009:17-99` |
| PROMPT-010 | artifact-factory | adaptable-pattern | named-precedent | review-and-adapt | sequence-factory-step | rubric pilot; `PROMPT-010:17-107` |
| PROMPT-011 | artifact-factory | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | sequence-factory-step | `PROMPT-011:18-91` |
| PROMPT-012 | artifact-factory | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | sequence-factory-step | `PROMPT-012:17-42` |
| PROMPT-013 | artifact-factory | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | sequence-factory-step | `PROMPT-013:17-53` |
| PROMPT-014 | build-coordinator | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | owner-launched-campaign | `PROMPT-014:18-104` |
| PROMPT-015 | operational-procedure | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | owner-launched-campaign | `PROMPT-015:17-69` |
| PROMPT-016 | reference-or-other | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | no-default-known | `PROMPT-016:17-69` |
| PROMPT-017 | review-campaign | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | owner-launched-campaign | `PROMPT-017:17-77` |
| PROMPT-018 | build-coordinator | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | owner-launched-campaign | `PROMPT-018:15-1345` |
| PROMPT-019 | review-campaign | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | owner-launched-campaign | `PROMPT-019:19-30` |
| PROMPT-020 | planning-input | adaptable-pattern | named-precedent | review-and-adapt | planning-sequence-start | rubric pilot; `PROMPT-020:15-186` |
| PROMPT-021 | artifact-factory | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | sequence-factory-step | `PROMPT-021:15-1415` |
| PROMPT-022 | build-coordinator | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | owner-launched-campaign | `PROMPT-022:15-110` |
| PROMPT-023 | planning-input | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | owner-launched-campaign | `PROMPT-023:15-120` |
| PROMPT-024 | artifact-factory | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | sequence-factory-step | `PROMPT-024:15-341` |
| PROMPT-025 | planning-input | adaptable-pattern | named-precedent | review-and-adapt | planning-sequence-start | `PROMPT-025:15-370` |
| PROMPT-026 | artifact-factory | adaptable-pattern | named-precedent | review-and-adapt | sequence-factory-step | `PROMPT-026:15-278` |
| PROMPT-027 | planning-input | adaptable-pattern | named-precedent | review-and-adapt | planning-sequence-start | `PROMPT-027:15-228` |
| PROMPT-028 | artifact-factory | adaptable-pattern | named-precedent | review-and-adapt | sequence-factory-step | `PROMPT-028:15-327` |
| PROMPT-029 | artifact-factory | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | sequence-factory-step | `PROMPT-029:18-978` |
| PROMPT-030 | build-coordinator | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | owner-launched-campaign | `PROMPT-030:20-197` |
| PROMPT-031 | planning-input | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | owner-launched-campaign | `PROMPT-031:20-300` |
| PROMPT-032 | artifact-factory | adaptable-pattern | named-precedent | review-and-adapt | sequence-factory-step | `PROMPT-032:15-520` |
| PROMPT-033 | planning-input | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | owner-launched-campaign | `PROMPT-033:15-122` |
| PROMPT-034 | artifact-factory | adaptable-pattern | canonical-current | review-and-adapt | sequence-factory-step | `PROMPT-034:15-442` |
| PROMPT-035 | review-campaign | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | owner-launched-campaign | `PROMPT-035:15-191` |
| PROMPT-036 | build-coordinator | adaptable-pattern | canonical-current | review-and-adapt | direct-operational-entry | `PROMPT-036:15-394` |
| PROMPT-037 | artifact-factory | adaptable-pattern | canonical-current | review-and-adapt | sequence-factory-step | `PROMPT-037:15-103` |
| PROMPT-038 | artifact-factory | adaptable-pattern | canonical-current | review-and-adapt | sequence-factory-step | `PROMPT-038:15-28` |
| PROMPT-040 | review-campaign | campaign-specific-record | historical-or-campaign-evidence | review-before-rerun | owner-launched-campaign | rubric pilot; `PROMPT-040:15-245` |
| PROMPT-041 | operational-procedure | run-as-is-recurring | canonical-current | direct-run | direct-operational-entry | `PROMPT-041:19-45` |

## Reconciliation

The table has **40 rows**, matching the baseline count exactly. It includes no PROMPT-039 because
no governed document with that code exists at this baseline. The four pilot rows match the rubric
unchanged. This inventory does not change prompt status or imply that a historical campaign prompt
should be retired.
