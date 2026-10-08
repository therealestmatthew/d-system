---
schema_version: 1
id: doc-session-execute-workbench-identifier-migration
code: SESS-2026-10-08-02
title: Execute the workbench identifier migration
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems:
- sys-wb-layout
- sys-wb-styles
- sys-wb-shared
- sys-wb-terminal
- sys-wb-notes
- sys-wb-explorers
- sys-wb-viewer
depends_on:
- doc-workbench-architecture-quality
- doc-workbench-architecture-quality-requirements
- doc-session-settle-workbench-vocabulary
---

# Execute the workbench identifier migration

## Phase

`phase-arch-02` — Execute the workbench identifier migration, from the workbench architecture and
quality plan (`PLAN-028`, programme `P10`), governed by
[REQ-011](../06-requirements/REQ-011-workbench-architecture-quality.md) rows `R03` and `R05`.
Built by `agent-batch-runner` on `agent/phase-arch-02` as a subagent of the Session Manager in the
pre-approved workbench run of 2026-10-08. The phase carries out the per-class rulings of
`phase-arch-01` (`SESS-2026-09-15-01`, `brain/concepts/terms-workbench-ui.md` "Migration ruling")
without re-deciding any of them.

## What changed, per ruling class

| Class | Ruling | Done |
|---|---|---|
| Layout `slot_id` values | Rename | `terminal`→`secondary`, `main`→`primary`, `notes-strip`→`strip`, `explorer` unchanged, in both layout files: `slots`, every panel's `eligible_slots`, `default_assignment` values, `default_visible_panel` keys and `grid.areas` tokens. `display_name` values are unchanged. |
| localStorage | Rename by version bump, no alias, no migration code | `schema_version` 2→3 in both layout files, in the same commit as the slot ids. The storage key is `d-system:workbench-state:v{schema_version}`, so the v2 key is never read again. No code in `storage.ts` changed. |
| Test fixtures | Rename, same commit | `test/test_workbench_layout_schema.py`: eligibility, default-assignment, default-visible and mutation fixtures now use the new ids. Only panel ids remain as `terminal`, `notes-strip`. |
| CSS class names | Alias (leave) | Untouched. `.stage-region--terminal` is the panel-type modifier and stays, as ruled. |
| `REQ-007` row wording | Alias (leave) | Untouched. |
| Panel registry ids | Alias (leave) | Untouched. |

Beyond the ruling's list, one code change was required and is in the declared scope
(`ts/src/workbench/`): `useWorkbenchLayouts.ts` held the slot id literal `'terminal'` as
`TERMINAL_SLOT_ID`, used to give the shells' slot its platform-conditional fresh-store default. It is
now `SHELL_HOME_SLOT_ID = 'secondary'`. The rest of the `ts/src` edits are comments: "terminal slot"
became "secondary slot" and "main slot" became "primary slot" where the comment meant the slot, and
the comments naming `schema_version` 2 were brought to 3.

### Finding: the ruling's "no engine code reads a slot id literal" was incorrect

Class 1 of the ruling says "No engine code reads a slot id literal." `useWorkbenchLayouts.ts` did:
`TERMINAL_SLOT_ID = 'terminal'`. Had only the data files been renamed, the Windows/Linux platform
default (PowerShell visible by default on Windows) would have silently stopped applying, with no
error. Corrected in this phase; the ruling text in `terms-workbench-ui.md` still carries the
incorrect sentence and was not edited here (outside this phase's deliverables).

### Side effect of the version bump, stated plainly

The v2 key also held `active_notes_file` and `html_viewer_tabs`, which `storage.ts` writes under the
same versioned key. A browser that had a chosen notes file or open HTML Viewer tabs loses both on
first load of v3 and falls back to the defaults. This follows from the ruling (one namespaced key,
version in the key) and is not an error state, but it is a visible reset beyond slot assignment.
The orphaned v2 key stays in the browser's localStorage unread and is not deleted.

## Evidence

### Zero stray hits

Old slot id values in the layout files: none. Every slot id and every reference to one (eligible
slots, default assignment, default visible, grid areas) resolves to a declared slot, and no slot id
equals any panel id in either layout:

```
layout-1.json slots ['explorer','primary','secondary','strip'] collide-with-panel-ids [] refs-not-slots [] v 3
layout-2.json slots ['explorer','primary','secondary','strip'] collide-with-panel-ids [] refs-not-slots [] v 3
```

Quoted `terminal` / `main` / `notes-strip` literals left in `ts/src` are all panel ids
(`BASH_PANEL_ID`, the registry key `'notes-strip'`, a `guardedPanel('notes-strip', ...)` test call).
No CSS selector is keyed on a slot id. One prose hit remains outside the diff: the docstring of
`src/api/routes/workbench.py` line 16 says "default the terminal slot"; `src/` was out of bounds
for this phase.

### R05 — stored browser state (Playwright against the Vite dev server on 5181, API on 8011)

Chromium via Playwright (global install, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`), 1600x900,
each scenario in a fresh browser context: seed localStorage, reload, snapshot the slots.
Scripts were kept in the scratchpad, not committed.

| Scenario | Page errors | `role=alert` | Result |
|---|---|---|---|
| A. no stored state | none | none | layout-1 defaults: secondary=Terminal (bash), strip=Notes, primary=HTML Viewer, explorer=File Browser |
| B. pre-migration `…:v2` key, old slot ids (`terminal`, `main`), `active_layout: layout-1`, with `active_notes_file` | none | none | slots identical to A; v2 key left untouched; v3 key written |
| C. same v2 state with `active_layout: layout-2` | none | none | layout-1 defaults, identical to A (the v2 `active_layout` is not read) |
| D. v3 key holding old slot ids (`terminal`, `main`) | none | none | identical to A (ADR-016 decision 3: references to an unknown slot are discarded silently) |
| E. v3 key with `panel_assignments: "garbage"` | none | none | identical to A |
| F. positive control: v3 key with valid new ids (`html-viewer`→`secondary`, `terminal-cmd`→`primary`) | none | one: "cmd is not available on this host" | honoured: HTML Viewer in secondary, CMD panel in primary. The alert is the CMD panel's own host-availability message on Linux, not a state error. |

Layout 2 (v3 `active_layout: layout-2`): grid areas `"strip primary explorer" "secondary secondary
secondary"`, four slots rendered, secondary spanning the full width at the bottom, page height equals
viewport height (no scroll), no page errors.

Not exercised: a real pre-migration browser profile (the v2 shape was seeded by hand from the
stored-state types, not captured from a live session), the Windows platform default for the secondary
slot (owner-machine, not run), and drag or dialog-driven reassignment.

### Verification commands

`uv run pytest` — `5 failed, 1649 passed, 1 skipped, 1 warning in 266.46s`. The five failures are
environmental and are listed under Unresolved. (A run made after adding this record and before
regenerating the catalog also failed the two catalog tests and `test_ideas_priority_yaml_is_governance_clean`;
all three pass once the catalog is regenerated.)

`cd ts && npm run build` — `✓ built in 1.73s` (chunk-size warning only, pre-existing).
`cd ts && npm test` — `Test Files 2 passed (2), Tests 7 passed (7)`.
`uv run python -m src.governance` — `Governance OK: 45 systems, 455 documents, 37 memories, 347 backlog phases`.
`uv run ruff check src/ test/ tools/` — `All checks passed!`.
`uv run mypy src/` — `Success: no issues found in 50 source files`.
`test/test_workbench_layout_schema.py` — `21 passed`.

## Unresolved

- Five pytest failures from the environment, not from this diff. `git rev-parse
  --is-shallow-repository` prints `true`, so history-reading tests cannot run:
  `test_idea_classification.py` (two tests run `git show 0f142ce:_data/ideas.jsonl`; the commit is
  absent, and also absent in the primary checkout), `test_containment.py::test_repository_history_reports_the_known_phase_prog_cases`
  (`phase-prog-04` reports "not locatable") and `test_engine_pages.py::test_a_known_idea_traces_to_the_git_log_and_the_fold`
  (a plan-approval date reads "not recorded"). `test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused`
  fails because the sandbox runs as root (uid 0), so the directory is writable. I did not run these
  on a clean trunk to confirm they fail there too; the causes above are what the failures print.
- `terms-workbench-ui.md` still says no engine code reads a slot id literal (see Finding above).
- `src/api/routes/workbench.py:16` docstring says "terminal slot".
- `schemas/workbench-layout.schema.json` describes `schema_version` 2 and has `minimum: 2`; left as is
  (outside deliverables, and 3 satisfies it).

## Assumptions and decisions awaiting ratification

- Renamed the constant to `SHELL_HOME_SLOT_ID` rather than keeping `TERMINAL_SLOT_ID` (a name that
  would now misdescribe, which is what the rename removes). No ruling covers a code constant's name.
- Updated slot-meaning prose in `ts/src` comments to the new role names. Comments are not one of the
  six ruled classes; this is the assumption that a comment saying "the terminal slot" about a slot
  now called `secondary` would be a stray old identifier.
- No ADR was written; no decision awaits ratification beyond those two.
