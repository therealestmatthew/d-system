---
schema_version: 1
id: doc-session-settle-workbench-vocabulary
code: SESS-2026-09-15-01
title: Settle the workbench vocabulary and rule on identifier migration
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems:
- sys-brain
- sys-wb-layout
depends_on:
- doc-workbench-architecture-quality
- doc-workbench-architecture-quality-requirements
---

# Settle the workbench vocabulary and rule on identifier migration

## Phase

`phase-arch-01` — Settle the workbench vocabulary and rule on identifier migration, from the
workbench architecture and quality plan (`PLAN-028`, programme `P10`), governed by
[REQ-011](../06-requirements/REQ-011-workbench-architecture-quality.md) rows `R01`, `R02` and `R04`.
Claimed by `agent-arch-vocab`, worked on `agent/phase-arch-01` in
`../d-system-worktrees/phase-arch-01`. The phase is the gate six ideas cite as a prerequisite by
their own text: `000115`, `000116`, `000133`, `000135`, `000141` and `000144`.

The session opened late on 2026-09-14 and the claim commit carries that date; the work itself and
this record fall on 2026-09-15. The concept memory's front matter keeps `2026-09-14` to match the
claim, the plan and the requirement it answers.

## The ruling, which is the deliverable

**A slot is the container and a panel is its content — a slot is a named region of a layout's grid,
and a panel is a unit of content assigned into exactly one slot at a time.**

`000135` raised the possibility that this is backwards — that panels are the containers things get
placed into — and the owner was explicitly unsure, directing that nothing terminology-related change
until it was settled. The answer is that the sense is not backwards at the slot/panel boundary, and
that the question stayed open because the containment `000135` noticed is real but one tier down: a
panel does contain things, and what it contains are **elements** — the HTML Viewer's file tabs, an
explorer's rows, a terminal's session tabs. Naming that third tier is the fix rather than inverting
the first.

Three things in the shipped code already implement the ruling, so it describes the system rather than
proposing a change to it: `default_assignment` maps `panel_id` to `slot_id`, `eligible_slots` lists
the containers a given content may occupy, and `StagePage.tsx:250` sets `grid-area` from `slot_id`,
which makes slots the thing the grid is composed of. The alternative would have renamed every field
in the layout schema, the types, the registry and the storage shape, and would have required
`000141`'s "slots have sub-slots that panels populate" model to be rewritten in reverse before
`phase-arch-06` could consume it.

The owner chose this reading, the `primary`/`secondary` slot naming and the qualified `Session
(workbench)` / `Region (workbench)` headings from four options put during orientation, before any
file was written.

## What shipped

`brain/concepts/terms-workbench-ui.md`, rendered into `docs/08-governance/GLOSSARY.md` by the
existing generator. No second glossary document, per `PLAN-028` design decision 1 — the
hand-maintained duplicate `GOV-001` forbids, and the generated path is the only one with a drift test
behind it.

Eleven terms per `R01`: slot, panel, region, layout, assignment, visible panel, session, panel type,
template family, generated page, overview. Two additions beyond the eleven, both load-bearing rather
than decorative:

- **Element**, the tier a panel contains. Without a word for it the container question cannot be
  answered without appearing to contradict the owner's own observation in `000135`.
- **A slot naming rule**, which `R03` needs and which `phase-arch-02` executes against.

`Session` and `Region` are written as qualified headings. Both nouns already carry other senses here:
`### Session` under *Skills and agents* covers the conversation and session-record senses, and
*region* already means panel in code identifiers — every panel component is named `*Region` and
renders a `.stage-region` box. The workbench entries cross-reference rather than compete.

## The slot naming rule, and why role rather than geometry

A slot id names the slot's **role**. It never names a panel type, and no slot id may equal any panel
id.

The second clause is not redundant, and finding out why is the session's one genuine discovery beyond
what `R03` already states. In both shipped layout files the string `terminal` is **simultaneously a
`slot_id` and a `panel_id`**, so `default_assignment` reads `"terminal": "terminal"` — panel to slot
— while `default_visible_panel` reads `"terminal": "terminal"` — slot to panel. Two different
namespaces, the same string, pointing in opposite directions. `notes-strip` collides identically. A
reader cannot tell which is meant without knowing which map they are looking at. `R03` describes the
slot id as naming its first occupant, which is true; it does not record that the occupant and the
container are the same string.

Role rather than geometry because the same slot is a different shape in each layout — `terminal` is
the left column in `layout-1` and the full-width bottom row in `layout-2`. A geometry-derived id
would differ per layout, and assignments are stored per `layout_id` per `panel_id`, so a panel could
not keep a recognisable home across a layout switch. Role names also survive `phase-arch-09`'s
reconfigurable geometry, which would invalidate a geometry-derived id the first time a slot moved.

## The migration ruling

`R04`'s six classes, each with a disposition and a reason. **This phase executes none of it**;
`phase-arch-02` does, and gates nothing.

| Class | Disposition | Why |
|---|---|---|
| Layout `slot_id` values | **Rename** | `terminal`→`secondary`, `main`→`primary`, `notes-strip`→`strip`, `explorer` unchanged. These are the identifiers `000124` was raised about; an alias leaves the misdescription in the file `R03` reads. Also discharges the `slot_id`/`panel_id` collision. `grid.areas` tokens rename with them in the same file. |
| CSS class names | **Alias** | Internal to the frontend, invisible in every governed document, no cross-file contract. Renaming touches every panel component and the 1,289-line `StagePage.css` for a gain no reader outside `ts/src/` sees, and collides with `phase-arch-03`/`-04`, whose audits are about to restructure those files. |
| `REQ-007` row wording | **Alias** | The W-rows name slots by role — "the terminal slot" — which stays correct. Rewriting a shipped requirement's prose to match later vocabulary makes the record of what was built less accurate. W16 must change, but for `R12`'s structural eligibility, already assigned to `phase-arch-07`. |
| localStorage keys | **Rename, via version bump** | The key is `d-system:workbench-state:v{schema_version}`; the identifiers at risk are the fields inside it. `ADR-016` rule 3 puts the version in the key, so bumping `schema_version` 2→3 means the old key is never read again and readers fall through to layout defaults. No alias, no migration code, no broken intermediate — which is what `R05` requires `phase-arch-02` to show. |
| Panel registry ids | **Alias** | All nine already name a panel type rather than a container or location. `terminal` as a *panel* id is correct and always was; it was only wrong as a *slot* id, which class 1 removes. |
| Test fixtures | **Rename, same commit as class 1** | `test/test_workbench_layout_schema.py` hard-codes the slot literals and asserts the shipped files' actual contents, so a rename that leaves them behind turns the suite red on the same commit. A shim mapping old literals to new would be a second source of truth for slot ids inside the only test that checks them. |

One constraint carries forward for `phase-arch-02` and is stated in the ruling: the `schema_version`
bump and the slot id rename must land in the same change, or live browsers are stranded on stored
assignments naming slots that no longer exist.

## Verification

All three of the phase's commands, run in the worktree after the rebase onto `dev`.

`uv run python tools/generate_glossary.py`

```
wrote /code/d-system-worktrees/phase-arch-01/docs/08-governance/GLOSSARY.md — 10 term(s)
```

`uv run pytest`

```
580 passed, 2 warnings in 57.10s
```

`uv run python -m src.governance`

```
Governance OK: 27 systems, 225 documents, 25 memories, 181 backlog phases
```

The memory count moves 24 → 25; the document count is unchanged, which is the check that no second
glossary document was created.

**The committed glossary was not stale.** The phase's verification note treats a dirty tree after
regeneration as a result to report. Regenerating produced `231 insertions, 0 deletions` against the
committed file — purely this session's new section, with nothing else drifting.

The drift test's own gate, run directly:

```
/code/d-system-worktrees/phase-arch-01/docs/08-governance/GLOSSARY.md is current
```

All eleven terms grepped in the rendered glossary, lowest-frequency first: `template family` 2,
`visible panel` 3, `generated page` 3, `region` 10, `panel type` 10, `assignment` 12, `overview` 16,
`session` 30, `layout` 32, `slot` 52, `panel` 56. No term is absent.

## Found wrong in the source material

Four things, none of them in this phase's declared systems, so none were edited.

- **`phase-wbf-01` declares `sys-ui`, which no longer covers the file its scope names.** After
  `phase-arch-00`, `sys-ui`'s paths are `ts/src/App.tsx`, `main.tsx`, `vite.config.ts`,
  `package.json` and `PLAN-022`. The phase's scope confines it to
  `ts/src/stage/HtmlViewerRegion.tsx` and its tab strip, which is `sys-wb-viewer`. Its lock does not
  cover its work, so the validator would not stop a peer editing that file concurrently.
- **`panelRegistry.tsx`'s doc comment cites a field that does not exist on disk.** It refers
  repeatedly to "the terminal slot's `admits` list (`_data/workbench/layouts/*.json`)". The layout
  files carry no `admits` field; the `REQ-007` W16 delta moved eligibility to per-panel
  `eligible_slots`, and `admits` survives only on the resolved in-memory `LayoutSlotDefinition`. A
  reader following the citation finds nothing.
- **`REQ-011` R03 understates its own failing case.** It records `slot_id: "terminal"` as naming the
  panel that first occupied the slot, which is true, but not that `terminal` is concurrently a
  `panel_id` in the same two files, nor that `notes-strip` has the same collision. The naming rule
  in the concept memory covers both; the requirement row still describes only the first.
- **The private-content check is weaker in a worktree than in the primary checkout.** In the
  worktree it reports `627 tracked files, 0 identifiers checked` and notes that `_private/portfolio/`
  is absent, so only the path check ran, not the identifier scan. The same tool in the primary
  checkout checks 31 identifiers. Nothing in this session's diff carries portfolio content, and the
  full check ran against the claim commit in the primary checkout, but a worktree-only run is not
  the check it appears to be.

## Concurrent-agent note

A peer was writing into the **primary checkout** during this session, which the working agreement
reserves for the claim commit and the catalog regeneration it forces. Observed modification times:
`_data/ideas.jsonl` at 23:52:58, `docs/08-governance/systems.yaml` at 23:53:46, and
`docs/03-sessions/SESS-2026-09-14-11-decompose-sys-ui-lock.md` at 23:56:19, the last of these about
thirty seconds before this session looked. None of it was touched, stashed or committed. The claim
commit was made with explicit pathspecs — `docs/09-backlog/backlog.yaml` and
`docs/08-governance/catalog.md` only — so the peer's uncommitted work was left exactly as found.

`phase-arch-00` still reads `status: active` in `backlog.yaml` while its session record's
uncommitted text already describes it as complete. That is `/session-close`'s to reconcile, not this
session's.

## Unresolved

- **`phase-arch-02` inherits a constraint this phase could not discharge**: the `schema_version` bump
  and the slot rename must be one change. Nothing mechanical enforces that pairing today; it is
  stated in the ruling and in this record, and a check for it would belong to `phase-arch-02`.
- **The `overview` panel type is left registered and unruled on.** Whether `OverviewRegion` still
  earns its place now that the HTML Viewer serves the same page is a duplication question for
  `phase-arch-03`, not a naming one, and the ruling says so rather than deciding it quietly.
- **`REQ-007` W16's prose will describe slot ids that no longer exist** once `phase-arch-02` lands.
  The ruling accepts this deliberately, because the prose names roles rather than ids, but it is a
  gap a reader could mistake for staleness.
