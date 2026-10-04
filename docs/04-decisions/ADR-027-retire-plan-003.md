---
schema_version: 1
id: doc-adr-retire-plan-003
code: ADR-027
title: Retire PLAN-003's authored YAML content site and cancel the ten phase-html phases
kind: adr
status: accepted
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-html]
depends_on: [doc-html-00-overview, doc-html-generation-design-system-requirements, doc-html-generation-design-system]
---

# Retire PLAN-003's authored YAML content site and cancel the ten phase-html phases

## Status

Accepted. The owner ruled on 2026-10-04, in the `phase-des-01` session, after the audit of
`PLAN-003` against the repository. The choices were to retire the plan, defer it, or keep it.

## Context

[`PLAN-003`](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003-overview.md) and its six child
plans were approved before the demo and the workbench were built. They describe an authored content
site:
- page configuration written in YAML under `_data/pages/`;
- converted to JSON by `tools/build_pages.py` and checked against two JSON Schemas;
- served by FastAPI at `/api/v1/pages/*`;
- rendered in React with React Router and Tailwind v4, through four block components.

Ten backlog phases, `phase-html-01` to `phase-html-10`, carry the plan. All ten were `queued` and
none had started.

`phase-des-01` audited every requirement in the seven documents against the repository at `dev`
`92777af`. It found 176 requirements. None of the plan's own files exists on any branch, and
nothing in `src/` or `ts/src/` calls `/api/v1/pages`. Other work took the plan's place:

- **Generated pages.** They are built from repository data, not authored configuration:
  - `tools/generate_overview.py` (182fefa, `phase-demo-04`);
  - `tools/generate_engine_pages.py` (1913f26, `phase-des-09`, with the ledger and trace pages
    added by `phase-des-10` and `phase-des-11`).

  Both write committed HTML snapshots under `_public/`. The workbench shows them through
  `ts/src/stage/HtmlViewerRegion.tsx` (3d24e5d, `phase-wb-04`).
- **Design tokens.** They come from the house family: `templates/styles/house-tokens.json`,
  generated into `templates/styles/house.css` by `tools/generate_house_css.py` (49b0ca2,
  `phase-des-07`). Tailwind was never installed.
- **The React app.** It is the demo stage and the workbench. `ts/src/App.tsx` renders the stage
  (b30b685, `phase-demo-02`). There is no URL routing, and the plan's instruction to delete `App.tsx`
  would now remove the stage.

The 2026-09-05 adversarial audit of the plan,
[`ARCH-003`](../07-architecture/ARCH-003-html-adversarial-audit.md), had already found:
- permissive contracts;
- a converter that publishes before it validates;
- a phase order that cannot build;
- verification steps that cannot pass as written.

Its amendments were never applied to the plan or the phases.

## Decision

1. **The authored YAML content site is retired.** No `tools/build_pages.py`, page schemas, page
   models, `/api/v1/pages` routes, React router or block components will be built under this plan.
2. **`PLAN-003` and its six child plans move to `deprecated`.** Nothing replaces the product they
   describe, so `superseded` would be wrong. Each document keeps its text and gains an "Audit
   disposition" section at its end, listing every requirement it states. Across the seven
   documents:
   - 9 are accomplished;
   - 14 are superseded by shipped work, named by file and commit or phase;
   - 153 are retired with a reason.
3. **The ten `phase-html-*` phases move to `cancelled`.** Each carries a `blocked_reason` naming
   this ADR. Their ids are kept and not reused. `--ready` no longer offers any of them (`REQ-021`
   R02).

## Alternatives rejected

- **Defer the plan.** The phases would move to `deferred` with a `resume_when`, and the plan would
  stay on file. This was rejected because no condition for resuming exists. The plan's premises have
  changed:
  - `App.tsx` is the stage;
  - the token set is the house family's;
  - generated pages are snapshots.

  A resumed plan would have to be rewritten first. A deferral would leave ten phases that look like
  work but cannot be built as written.
- **Keep the plan.** The phases would stay `queued`. Before anyone built them, `ARCH-003`'s
  amendments would have to be applied: the build-order defect, the unowned `NotFoundPage`, and the
  verification steps that cannot pass. Whoever applied them would also have to decide how a second
  styling system and a router would sit beside the stage. That is re-planning a product nobody has
  asked for since the plan was approved.

## Consequences

- The `GOV-003` rows "Page data authority" and "Runtime block validation" governed only
  `phase-html-*` phases. They have nothing left to govern. They are left in place as the record of
  what was decided at the time.
- `ARCH-003` stays as the record of why the plan was not buildable as written.
- `REQ-021`, `PLAN-036` and `ARCH-003` keep their `depends_on` on the overview, since they still
  refer to it.
- Two phases outside this decision depended on the retired work. The owner ruled that this phase
  reports them rather than editing them:
  - `phase-syn-05` (queued) depends on `phase-html-10` and needs the YAML-to-JSON page pipeline.
    Recorded as idea `000567`.
  - `phase-sch-06` (deferred) has a `resume_when` that waits for `PLAN-003` to be built. Recorded as
    idea `000568`.
- `sys-html` in `docs/08-governance/systems.yaml` is still `planned`, with `PLAN-003`'s overview as
  its path. Recorded as idea `000571`.
- Two gaps found by the audit outlive the plan:
  - the stage and workbench have no React error boundary and no accessible loading or error status
    (idea `000569`);
  - CI's ruff step does not lint `tools/` (idea `000570`).
- This audit gates two phases: the template library (`phase-des-03`) and the component library
  (`phase-des-04`). Both are told to scope against its findings (`REQ-021` R04). What carries over
  to them:
  - `PLAN-003` contributes no template or component to extract. Its four block types (hero, text,
    image, columns) correspond to the house components already shipped in
    `templates/html/house-components.html`.
  - Its one population model, authored YAML into JSON, is retired. The population methods
    `phase-des-03` declares start from the generators that exist.
  - `ARCH-003`'s accessibility findings still apply to any component that `phase-des-04` builds:
    - coherent heading levels and keyboard focus behaviour (M4);
    - a real breakpoint-aware columns layout, which the plan's inline grid style defeated (M4);
    - no long-text or long-label horizontal overflow at narrow widths (M4);
    - a stated policy for link schemes and image assets instead of accepting any URL (M1).
