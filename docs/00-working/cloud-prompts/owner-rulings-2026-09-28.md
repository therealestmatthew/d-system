# Owner rulings, 2026-09-28

The owner's answers given in cloud session `session_011V3TLrNvv2R2cScsEtvTyr` on 2026-09-28,
through AskUserQuestion. Each line is the question as asked and the answer the owner chose,
recorded as given. Local Ideation records them as findings on the ideas named. Nothing here
changes a document except where a line says it was applied.

## Cloud prompt tracker

- Merge the boundary validation branch (`agent/cloud-boundary-validation`, `238b6a0`) into `dev`
  after re-running the gates: **yes**. Applied: governance, pytest (`1156 passed, 1 skipped`), ruff
  and mypy all passed; `dev` fast-forwarded `9772c21..238b6a0` and pushed.
- Who writes the fourth cloud prompt (the boundary follow-up for option A, including the F01
  wording changes): **Prompt Planner, locally**, from this file.

## System boundary (`ARCH-012`, `PLAN-050`)

- Boundary direction at `ARCH-012`'s owner decision gate: **option A**, one repository with
  explicit ownership and interface contracts. Next: the contract-and-measurement follow-up.
- F01, escalated to G3: **apply** the seven `ARCH-012` wording changes in section 6 of the
  validation report. Not yet applied; they belong in the follow-up.
- Separate `GOV-018` reviews for the five child plans `PLAN-050.01` to `.05`: **no**. All five
  phases are complete; this is recorded as the exception.
- `phase-bnd-07` (a required `concern` field in `docs/08-governance/systems.yaml`): **approved**.
  It is still deferred until `phase-bnd-06` is complete; its scope is reviewed against current
  `dev` before it is released. The backlog was not edited.

## Plan-folder standard (idea `000505`, `docs/00-working/plan-anatomy/proposed-standard.md`)

| | Decision | Owner's answer |
|---|---|---|
| A | Is every new plan a folder? | Yes |
| B | Are the 44 existing single-file plans migrated? | No |
| C | Split decisions into a one-line ruling in the plan and a record beside it? | Yes, for new plans |
| D | What is the decision record? | An uncoded member file, `decisions.md` |
| E | Do one-time prompts go in a `prompts/` member folder? | Yes; `000501` draws the one-time/reusable line; coded prompts keep their codes |
| F | Do review records stay in `docs/08-governance/reviews/`? | Yes |
| G | An `evidence/` member, with `_working/` evidence a tracked plan relies on copied into it? | Yes to both |
| H | Is the entry point always `PLAN-NNN-overview.md`, even for a one-document plan? | Yes |
| I | Fix the `GOV-018` entry-check script now, independent of the rest? | Yes |
| J | What happens to the flat child plan `PLAN-039.01`? | **Move it**: `PLAN-039` and `PLAN-039.01` go into a folder, with their path references rewritten (18 in 10 files, per the proposal). This differs from the proposal's recommendation |
| K | Settle the standard before `phase-idg-11` runs? | Yes |
| L | Does the idea-realization plugin adopt the same standard? | Decide after the repository adopts it |

## Planning protocol (`GOV-021`, idea `000500`)

- Open question 6, `ARCH-006`'s G5 row: **amend now**. Applied in this change: the row now says
  `/session-close` is run by the owner or by a coordinator once `GOV-003`'s three conditions hold.
  `AGENTS.md` was amended to the same effect earlier the same day, with the owner's approval.
- Open question 1, `GOV-008` and the optional pre-plan package: **amend `GOV-008` once, with the
  plan-folder standard's work**, after `000501` separates one-time prompts from reusable ones.
- Open question 2, what stops the decompose-and-audit loop until the phase-fit heuristic exists:
  **the loop stops when the phase-altitude audit proposes no further split; any doubt goes to the
  owner at G3.** Applied in this change: `GOV-021` step 10 and Open question 2.
- Open questions 3 and 4, the owner's step order against `GOV-018`, `GOV-002`, `GOV-014` and the
  backlog schema: **plan it later**. Both sides stay as they are until a planning session.

## Status follow-up

- Tracker row 3 (boundary validation): **mark it merged now**. Applied: `Status` merged, `Tip`
  `238b6a0`.
- Boundary phases after option A (`phase-bnd-06`, `-08`, `-09` released by A; `-10` to `-13` tied
  to options B and C): **leave for Prompt Planner**. The fourth prompt reviews their scope against
  `dev` and releases or cancels them. The backlog was not edited.
- Ideas `000500` and `000505`, still `open`: **local Ideation** records these rulings as findings
  and moves their status.
- `GOV-021` and `ARCH-012`: **both stay `draft`**. `ARCH-012` still needs the F01 wording changes.

## Branches on `origin` to delete

`agent/cloud-planning-protocol`, `agent/cloud-plan-anatomy` and `agent/cloud-boundary-validation`
are all merged into `dev`. The cloud session's delete of `agent/cloud-planning-protocol` was
refused with HTTP 403, so these need deleting from a local checkout or on GitHub.
