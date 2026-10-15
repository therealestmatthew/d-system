---
schema_version: 1
id: doc-ux-kit-plan
code: PLAN-003
title: UX component kit for the product app and generated pages
kind: plan
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: [sys-ui-kit]
depends_on: [doc-ux-kit-requirements, doc-ux-kit-on-react-aria, doc-ux-design-guide]
---

# UX component kit for the product app and generated pages

## Context and scope

The team needs one component kit so that several developers and the page-generating agents produce
screens and reports with one look, one keyboard model and one accessibility standard. The design is
the UX design guide (`ARCH-001`), the observable requirements are the kit requirements (`REQ-001`),
and the architecture choice is the component kit decision (`ADR-001`).

**Kit v0 is being built now**, on branch `agent/idea-realization-ux-kit`, as owner-directed work
with no claimed phase. It covers:

- tokens (`ui-kit/tokens/tokens.json`, `ui-kit/tools/build_tokens.py`, `ui-kit/dist/tokens.css`),
  with light and dark themes and named candidate accents switched by `data-accent`;
- base and layout CSS (`ui-kit/src/css/base.css`, `ui-kit/src/css/layout.css`) and fixed shell
  layouts (`ui-kit/layouts/*.json`);
- the shell and the panel frame;
- buttons, cards, table, pills, empty / loading / error states, dialog, tabs and toast
  (`ui-kit/src/css/components/*.css`, `ui-kit/src/react/`);
- the theme sheet (`ui-kit/gallery/theme-sheet.html`) for the owner to choose an accent from;
- the gallery and tests for these (`ui-kit/gallery/`, `ui-kit/test/`).

This plan covers the work after Kit v0, as fifteen queued phases. Each phase's first action is to
read what Kit v0 actually shipped, because the exact split between CSS and React inside Kit v0 is
recorded in its own report, not here.

The kit lives in the top-level `ui-kit/` folder of this control repository for now and is planned
to move to `product:packages/ui/` in the product repository later. Every path below is a
control-repository path, and every verification command carries the `control:` prefix.

This work also gives the browser validator agent in the follow-on plan (`PLAN-001`, step 12) the
user interface and test harness it waits for.

## Decisions

Each decision was made by the owner on 2026-10-14 and is settled unless stated.

- **Own kit on React Aria Components, styled with our tokens** (`ADR-001`). Rejected: Cloudscape
  adopted wholesale (limited theming, an AWS console look, no static-page support), Radix or
  shadcn/ui with Tailwind (duplicated tokens, no class allowlist for generated pages), React only
  (generated pages would need Node), vanilla only (accessibility hand-written again).
- **Cloudscape's generative-AI patterns are the specification for the AI and agent set**, not a
  dependency.
- **React 19 + Vite + TypeScript** for the app; **Python** for the token build and page generators.
- **Static pages keep a small declared `ui.js`**; the app takes all behaviour from React Aria.
- **Light and dark from the start**, following the system setting with a toggle; presented in
  light.
- **System sans-serif stack**, no webfonts.
- **Fixed layout-as-data shell**: no runtime panel reassignment and no layout persistence.
- **The accent is not chosen.** The kit ships named candidates and a theme sheet; the owner chooses
  later (see Open questions).
- **The kit is built in `ui-kit/` in this repository now** and moved to `product:packages/ui/`
  later.
- **The design guide is an architecture document in `docs/architecture/`**, so no new code series
  is needed.

## Work and dependencies

Each step is one phase in `backlog/backlog.yaml`, sized to one session, with `systems:
[sys-ui-kit]` (the skill phase adds `sys-agents`). "Kit v0" is a prerequisite of every phase; it is
not a backlog phase, so it is not in any `depends_on`.

| Phase | Outcome | Depends on |
|---|---|---|
| `phase-ux-01` | Gallery generator and the browser test harness: one command builds the gallery and runs axe, focus-ring, request-origin, keyboard and shell-fit tests in both themes; any REQ-001 row Kit v0 left without a test gets one | Kit v0 |
| `phase-ux-02` | Static overlay behaviours in `ui.js`: toolbar, menu and context menu, popover, tooltip and toggletip, with the component manifest declaring each | `phase-ux-01` |
| `phase-ux-03` | Static disclosure and data behaviours in `ui.js`: accordion deep link and expand-all, JavaScript and CSS-only tabs, table sort and filter, in-page search, theme toggle, copy; `ui.js` within 8 KB gzip | `phase-ux-02` |
| `phase-ux-04` | The remaining static display components: stat row, callout, breadcrumbs, form and input styles, progress, code and JSON viewer, count badge, filter chip, tag and gate badge, with the class-contract test | `phase-ux-01` |
| `phase-ux-05` | React shell completion: typed bar elements that throw on an unadmitted type, panel registry, transient maximize and collapse that never remount, per-panel error boundary, status strip, skip link and F6 region cycling; the React-versus-catalogue class test | `phase-ux-01` |
| `phase-ux-06` | React overlay and navigation controls on React Aria: Toolbar, Menu, Popover, Tooltip, Accordion, Breadcrumbs | `phase-ux-02`, `phase-ux-04`, `phase-ux-05` |
| `phase-ux-07` | React forms and inputs on React Aria: text field, textarea and prompt input, select, combobox, checkbox, radio group, switch, segmented control, slider, file drop zone, search field | `phase-ux-04`, `phase-ux-05` |
| `phase-ux-08` | React DataTable: toolbar, filter chips with count, three-state sort, row selection, empty and loading states, virtualization above 500 rows, 1,000-row filter within 50ms | `phase-ux-03`, `phase-ux-07` |
| `phase-ux-09` | React command palette and tree view | `phase-ux-06` |
| `phase-ux-10` | AI streaming and run components: stream output, run timeline, AI output label, model and usage badge | `phase-ux-05`, `phase-ux-06` |
| `phase-ux-11` | AI provenance and approval components: citation chip and source drawer, provenance stamp, confidence indicator, approval card, with static variants for reports and a sanitizer test | `phase-ux-10` |
| `phase-ux-12` | Page generation: report and fragment templates, the template library, `render.py` and `lint_html.py` | `phase-ux-04` |
| `phase-ux-13` | The `ui-page` skill that tells agents to compose pages from the kit and gate them with the lint | `phase-ux-12` |
| `phase-ux-14` | Two exemplars built only from kit parts: a generated agent run report and an app screen with nav, explorer, viewer, inspector, agent panel and dock | `phase-ux-08`, `phase-ux-09`, `phase-ux-11`, `phase-ux-13` |
| `phase-ux-15` | A one-page cheat sheet and a guidelines page in the gallery, rendered from the design guide | `phase-ux-14` |

The source plan's units mapped onto these phases as follows: the static interactive unit became
`phase-ux-02` and `phase-ux-03`; the remainder of the display unit became `phase-ux-04`; the React
shell unit became `phase-ux-05`; the React controls unit became `phase-ux-06` to `phase-ux-09`; the
AI unit became `phase-ux-10` and `phase-ux-11`; the page generation unit became `phase-ux-12` and
`phase-ux-13`; the gallery and harness unit became `phase-ux-01`; the exemplar unit became
`phase-ux-14` and `phase-ux-15`. Units were split wherever their scope did not fit one session.

## Requirement coverage

| Row | Requirement | Met by |
|---|---|---|
| R01 | Deterministic token build | Kit v0; `phase-ux-01` confirms the test runs in the one command |
| R02 | Contrast pairs pass in both themes for every accent | Kit v0; `phase-ux-01` adds the test if Kit v0 did not |
| R03 | Dark sets colour only | Kit v0; `phase-ux-01` adds the test if Kit v0 did not |
| R04 | Theme follows the system setting unless overridden | Kit v0 (tokens); `phase-ux-03` (static toggle); `phase-ux-05` (app toggle) |
| R05 | Every candidate accent can be selected; theme sheet shows all | Kit v0 (theme sheet); `phase-ux-01` (browser test) |
| R06 | No external request | `phase-ux-01`; every later phase keeps it passing |
| R07 | Focus ring on every interactive element | `phase-ux-01`; every component phase keeps it passing |
| R08 | axe zero serious or critical on the gallery | `phase-ux-01`; every component phase keeps it passing |
| R09 | Keyboard specification per widget | `phase-ux-01` (dialog, tabs, toast from Kit v0); `phase-ux-02` and `phase-ux-03` (static widgets); `phase-ux-06` (React overlays); `phase-ux-08` (DataTable sort); `phase-ux-09` (tree, command palette) |
| R10 | No `<script>` on script-free pages | `phase-ux-02` (manifest declarations); `phase-ux-12` (`lint_html.py`) |
| R11 | Shell fit with zero page scroll at four sizes | `phase-ux-01` (test); `phase-ux-05` (shell completion) |
| R12 | React components emit the catalogue's classes | `phase-ux-05` (test introduced); `phase-ux-06` to `phase-ux-11` extend it |
| R13 | No colour literal in component CSS | Kit v0; `phase-ux-04` keeps it passing |

## Execution order

Every phase declares `sys-ui-kit`, and the backlog check refuses two active phases that share a
system. The phases therefore run one at a time, whatever their dependencies allow. Kit v0 itself is
unclaimed and holds no lock, so these phases are not claimed until Kit v0 has integrated.

The proposed order, for the owner to rank with `next_up`:

1. `phase-ux-01` (the harness every later phase uses to check itself).
2. `phase-ux-05` (React shell, so app screens can start).
3. `phase-ux-04`, then `phase-ux-07` (display components and forms, which most screens need).
4. `phase-ux-02`, then `phase-ux-06`, then `phase-ux-09` (overlays and the palette).
5. `phase-ux-03`, then `phase-ux-08` (static data behaviours, then DataTable).
6. `phase-ux-10`, then `phase-ux-11` (AI set).
7. `phase-ux-12`, then `phase-ux-13` (page generation and the skill).
8. `phase-ux-14`, then `phase-ux-15` (exemplars and onboarding).

Parallel kit work would need `sys-ui-kit` split into narrower systems; see Open questions.

## Acceptance and verification

The plan is done when every phase above is complete or cancelled by the owner, and:

- every REQ-001 row has a test that runs from one command and passes;
- the gallery shows every component in ARCH-001's component set, apart from the deferred list, in
  light and dark;
- both exemplars pass `lint_html.py`, axe and the shell-fit test;
- `uv run plugins/idea-realization/scripts/check.py` exits 0.

The case that must fail: each REQ-001 row names a fixture its test must reject, and the test suite
includes those fixtures.

## Out of scope

Deferred, with the reason:

- **Embedded terminal (PTY):** needs a server-side terminal process, and no product need is known.
- **Runtime panel reassignment and layout persistence:** excluded by the owner's fixed-layout
  ruling.
- **Menu bar:** the command palette covers the same commands.
- **Rich code editor:** no known product need; the code viewer is read-only.
- **Drag-and-drop layout:** excluded with runtime reassignment.

Also out of scope: the product's own screens (built by the team with the kit), the move of the kit
to the product repository, and choosing the accent, product name or logo.

## Open questions

1. **Accent choice.** The owner chooses one candidate from the theme sheet once Kit v0 publishes
   it. The kit works with any candidate; after the choice, the unused candidates may be removed in
   a small change. Decided by the owner, no deadline before the exemplar phase.
2. **Product name and logo.** Needed for the app header and the exemplars (`phase-ux-14`). Decided
   by the owner. The exemplars use a placeholder name until then.
3. **One system or several for the kit.** With one `sys-ui-kit`, only one kit phase can be active
   at a time. Splitting it (for example a static-pages system and a React system) would let two
   developers work in parallel, at the cost of more declarations. The author leans to splitting
   once more than one developer works on the kit. Decided by the owner.
4. **Kit workstream and owner.** The source design proposed a `ui-kit` workstream in
   `docs/workstreams.yaml`, owned by one developer. This change does not add it. Decided by the
   owner once developers are registered.
5. **Verification commands.** The phases' commands assume Kit v0 sets up `pytest` for Python tests
   under `ui-kit/test/`, and `vitest` and Playwright run from `ui-kit/`. If Kit v0 chose different
   commands, each phase's `verification` is corrected before it is claimed. Decided by whoever
   integrates Kit v0.
6. **A pointer to the `ui-page` skill in `CLAUDE.md`.** Agents find the skill faster with a pointer,
   but `CLAUDE.md` changes only with the owner's explicit approval. Proposed wording, not applied:
   "To build a page or screen, use the `ui-page` skill: compose it from `ui-kit/` components only
   and run its lint before handing it over." Decided by the owner when `phase-ux-13` completes.
7. **When the kit moves to the product repository.** The author leans to moving it once the product
   repository exists and before the app's first screens integrate, so that app code imports it from
   one place. Decided by the owner.
