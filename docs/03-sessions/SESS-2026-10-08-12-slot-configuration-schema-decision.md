---
schema_version: 1
id: doc-session-slot-configuration-schema-decision
code: SESS-2026-10-08-12
title: Decide the slot configuration-schema model, superseding ADR-016 (phase-arch-06)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-wb-layout, sys-wb-styles, sys-wb-terminal]
depends_on: [doc-adr-slot-configuration-schema-model]
---

# Decide the slot configuration-schema model, superseding ADR-016 (phase-arch-06)

## Phase

`phase-arch-06` (decide the slot configuration-schema model, superseding `ADR-016`), group `G43` of
[`PLAN-028`](../01-plans/PLAN-028-workbench-architecture-quality.md). Claimed by
`agent-batch-runner` (Session 5 - Batch Runner) under the Session Manager's pre-approved run of
2026-10-08. Worked in `/home/user/d-system-worktrees/phase-arch-06` on `agent/phase-arch-06`, cut
from the run's integration branch `ccr-b69b05b4-tdcrux`. No dev server was started.

## Outcome

One decision record, [`ADR-031`](../04-decisions/ADR-031-slot-configuration-schema-model.md), and a
superseded status plus a pointer on [`ADR-016`](../04-decisions/ADR-016-workbench-layout-persistence.md).
Nothing was built. The record's recommendation:

- **The four `ADR-016` decisions.** Decision 1 (layouts are versioned repository JSON) kept, minus
  its "set of panel types it admits" clause, which structural eligibility replaces. Decision 2
  (geometry changes are data edits only) replaced. Decision 3 (browser stores selections only,
  silent discard) kept, with the stored shape widened to instances. Decision 4 (repository defaults
  are the fallback) kept unchanged.
- **A slot is a schema-owned frame.** One top bar with four sub-slots (`identity`, `help`,
  `controls`, `frame_actions`) and one body. A panel declares element types and fills sub-slots; it
  has no way to render a bar, so `000101` (the double header) cannot arise from a panel that
  follows the contract.
- **Slot schemas are one tracked data file, one entry per role.** Nesting is a tree of depth two.
- **Eligibility is a structural match** of the panel type's element configuration (declared in
  `PANEL_REGISTRY`) against the role's schema. Checked by script against both shipped layouts: 16 of
  the 17 panel-in-layout rows match `REQ-007` W16; `overview` in layout 2 becomes eligible for
  `secondary` as well as `primary`.
- **Instance identity.** Layouts declare `instance_id` plus `panel_type`. Ids are workbench-wide
  (a live shell survives a layout switch because both layouts name the same id). The first instance
  of a type keeps the type id. Instances are declared in repository data, not created in the
  browser.
- **Session ownership** stays in the browser per instance; the server is unchanged.
- **Geometry.** Floors derived per body kind from the schema, applying to every role that admits the
  kind; topology stays data; track sizes become a browser selection clamped by the floors.
- **Maximize and collapse** are slot frame actions on transient state, with no reparent of the
  instance host.
- **Migration.** Version bumps 3 to 4 (`phase-arch-07`) and 4 to 5 (`phase-arch-08`); stored state is
  discarded by the versioned key, with no migration code.
- A table of what `phase-arch-07`, `-08`, `-09`, `-10` and `-17` each build, and which of their
  declared deliverables need widening (panel sources under `ts/src/stage/`, `StagePage.tsx`,
  `ts/vite.config.ts`, `schemas/`, `test/test_workbench_layout_schema.py`,
  `test/test_workbench_fit_contracts.py`).

## Status of the decision

**Proposed; awaiting the owner's ratification (pre-approved run, 2026-10-08).** The ADR front matter
is `status: draft`, following `ADR-029` and `ADR-030`. `ADR-016` reads `superseded` already because
the governance validator requires it of a `supersedes` target; until the owner ratifies, `ADR-016`
still describes what is shipped. Eleven ratification points are listed under "Open items for the
owner" in the ADR; the ones that change what a later phase builds are item 1 (browser track-size
selections, versus data-only geometry), item 2 (instances declared, not browser-created) and item 4
(the terminal's collapse toggle moves to the slot).

## Evidence

- `uv run python -m src.governance`: `Governance OK: 45 systems, 468 documents, 37 memories, 354
  backlog phases`, exit 0, after `--catalog`. Before the catalog was regenerated it failed with the
  catalog-differs error, and before `ADR-016` was marked superseded it failed with `replaced
  document doc-workbench-layout-decision must be superseded`, which is the rejection `REQ-011` `R11`
  relies on. One non-blocking warning, unrelated to this phase: `status-regression (dev):
  phase-wbf-01 complete -> active`.
- `uv run ruff check src/ test/ tools/`: `All checks passed!`
- `uv run mypy src/`: `Success: no issues found in 51 source files`
- `uv run pytest`: `1 failed, 1899 passed, 1 skipped`. The failure is
  `test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused` (`DID NOT RAISE
  Refused`): the session runs as root (`id -u` prints `0`), which ignores the `0o500` directory
  mode the test relies on. It fails identically with this phase's changes stashed. Environmental;
  not skipped.
- `cd ts && npm test`: not run. `ts/node_modules` is absent and this phase touched nothing under
  `ts/`.

## Assumptions

1. The new ADR is `status: draft`, not `accepted`, matching `ADR-029` and `ADR-030`.
2. Field and file names in the ADR (`slot-schemas.json`, `instance_id`, `panel_type`,
   `instance_state`, `grid_tracks`, `frame_actions`) are indicative; the ADR says the properties are
   binding.
3. The body-kind list (`terminal-screen`, `document-frame`, `tree`, `table`, `ticker`) and the four
   bar element types were read off the nine panels' source and `REQ-037`'s contract rows. Capacity
   numbers were not measured; the ADR assigns that to `phase-arch-07`.
4. All statements about the shipped code (headers in eight of nine panel types, the keyless
   `terminalBridge.register`, the single `html_viewer_tabs` and `active_notes_file` fields, the
   `eligible_slots` readers) come from reading source. Nothing was rendered in a browser.
5. `ADR-029` and other documents listing `ADR-016` in `depends_on` were not edited; this phase's
   declared deliverable is `docs/04-decisions/`, and the ADR says their owners may retarget them on
   ratification. `REQ-007`, `REQ-011`, `REQ-037` and the terms file were not edited either; the ADR
   assigns those amendments to the phases that build.
6. Windows and macOS checks: none apply to a decision record. Owner-machine, not run.

## Unresolved

- Ratification of the ADR, in particular the geometry decision.
- Whether the owner wants the `overview` eligibility change prevented (ADR open item 3).

## Review

The gating review (demo adversary) passed the phase with two major and eight minor findings. Verdict
record: `docs/08-governance/reviews/verdicts/2026-10-08-phase-arch-06-demo-adversary.json`, reply
`_working/session-manager/review-replies/phase-arch-06-demo-adversary.md` (not tracked). All ten were
fixed in `ADR-031`. The fixes are the Session Manager's choices under the owner's pre-approval and
are awaiting ratification with the rest of the ADR.

- F01 (major): the `phase-arch-08` `R14` instance is now `html-viewer-2` assigned to `secondary` in
  layout 2, hidden by default; `R14`'s test makes it visible through the `secondary` panel switcher.
  The decision 5 example changed to match.
- F02 (major): decision 4 and the `phase-arch-07` row now state where the rule lives. Element
  configurations are in `_data/workbench/panel-elements.json`, which the registry refers to; the
  matcher is written once in TypeScript and once in Python as a documented pair, with a shared
  fixture test over every shipped (panel type, role) pair. Open item 11 records the alternative.
- F03: decision 4 says the body kind is the only discriminator on shipped data and bar capacity
  guards future panels; `phase-arch-07` includes one negative bar-capacity case.
- F04: decision 5 no longer claims the first-instance convention exposes type/instance confusion;
  it requires branded types and a standing `-2`-instance test in `phase-arch-08`.
- F05: decision 1 says the guarantee is a standing test, and `R13` counts `header` elements and
  `role="banner"` inside a slot, not a class.
- F06: `identity` and `frame_actions` are optional per frame; `compact` omits `identity`; `REQ-007`
  W01 is among the rows `phase-arch-07` amends; a check bars multiple instances in a role whose frame
  has no `identity`.
- F07: the stored-state drop rule reads "undeclared in every layout file".
- F08: the cross-panel default is a caller-level resolver; `BridgeSlot.get()` and `ADR-029` are
  untouched.
- F09: the "in demo week" qualifier is restored in the keep/replace table; "no migration code, ever"
  is open item 10.
- F10: decision 8 says a spanning slot's floor applies to the sum of its tracks; the 1024x768 check
  uses those sums.
