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

All three of the phase's commands, run in the worktree after the final rebase onto `dev` — the run
that decides whether the branch may integrate.

`uv run python tools/generate_glossary.py`

```
wrote /code/d-system-worktrees/phase-arch-01/docs/08-governance/GLOSSARY.md — 10 term(s)
```

`uv run pytest`

```
580 passed, 2 warnings
```

`uv run python -m src.governance`

```
Governance OK: 27 systems, 227 documents, 25 memories, 181 backlog phases
```

The memory count moves 24 → 25. The document count reaching 227 is `dev`'s two session records plus
this one, not a second glossary document — `GLOSSARY.md` is generated and uncatalogued, which is the
check that `PLAN-028` design decision 1 was honoured.

`git status --porcelain` is empty after the regeneration above, so the committed glossary is not
stale.

All eleven terms grepped in the rendered glossary, lowest-frequency first: `template family` 2,
`visible panel` 3, `generated page` 3, `region` 10, `panel type` 10, `assignment` 12, `overview` 16,
`session` 30, `layout` 32, `slot` 52, `panel` 56. No term is absent.

### The first post-rebase run failed, and what it found

The green run above is the third. The first rebase produced `3 failed, 577 passed`, from two
unrelated causes, both recorded here rather than retried until quiet.

**Two were this session's error.** `test_committed_catalog_matches_regenerated_output` and
`test_catalog_flag_writes_committed_file` failed because the session record is a governed document
and the catalog was not regenerated when it was committed:

```
E  assert '# Documentat... session: 83.' == '# Documentat... session: 84.'
E  - | SESS-2026-09-15-01 | session | active | repository-owner | docs/03-sessions/SESS-2026-09-15-01-settle-workbench-vocabulary.md |
```

Fixed by regenerating the catalog in its own commit. The lesson is narrow and already encoded in the
protocol: the catalog regeneration is forced by *any* governed document, not only by the claim.

**One was inherited from `dev`.** `test_the_committed_markdown_matches_regenerated_output` failed on
`dev` itself, independent of this branch: commit `2d861ca` added idea `000237` to
`_data/ideas.jsonl` without regenerating `docs/00-working/ideas.md`.

```
E  AssertionError: docs/00-working/ideas.md is generated. Regenerate it with
   tools/generate_ideas_md.py; do not edit it by hand.
E  - - relates_to ← `000237`
```

Confirmed as `dev`'s rather than this branch's by reading `dev` directly — `git show
dev:_data/ideas.jsonl` carried `000237` while `git show dev:docs/00-working/ideas.md` did not. It
was not fixed here, on the owner's ruling: regenerating a peer's generated file inside this phase's
diff would have hidden that `dev` was red when the peer integrated. It was fixed on `dev` by its
owner (`2d9290f`), and this branch was rebased again onto the result.

**The second rebase conflicted on `docs/08-governance/catalog.md`**, because `dev` had meanwhile
added `SESS-2026-09-14-12` to the same generated file. Resolved by regenerating rather than by
choosing a side — `--ours`/`--theirs` on a generated file silently drops whichever record it does
not pick. Both session records are present in the committed catalog, and the document count is 227.

## Acceptance

One line per condition, against what `## Verification` above actually shows.

- **`REQ-011` R01 — all eleven terms appear in the regenerated glossary and the drift test passes.**
  Met. All eleven grep present in the rendered glossary, each as a real `###` entry rather than an
  incidental mention; `test/test_glossary.py` passes inside the 580. `GLOSSARY.md` is absent from
  `catalog.md`, which is the check that it stayed generated and that no second glossary document was
  created.
- **`REQ-011` R02 — one sentence names the container explicitly.** Met. One sentence, and only one:
  `grep -n "is the container"` over the concept memory returns a single hit. It states the answer —
  a slot is the container — rather than describing the ambiguity, which R02's verification column
  makes a defect.
- **`REQ-011` R04 — each of the six identifier classes carries a rename-or-alias disposition with a
  reason.** Met. Six `### N.` headings, three RENAME and three ALIAS, each with a reason specific to
  that class rather than a restatement of the disposition.

The phase's other obligation is negative and also holds: **no rename was executed.**
`git diff --name-only 2d9290f..e76a385` returns five files — the concept memory, the glossary, this
record, the catalog and the `_tmpagent` ledger. No layout JSON, no CSS, no test, no registry, no
TypeScript. `phase-arch-02` still owns the migration.

## Backlog

`phase-arch-01` is `status: complete`, `agent: agent-arch-vocab`,
`session: doc-session-settle-workbench-vocabulary`. Completion evidence is
`brain/concepts/terms-workbench-ui.md` and `docs/08-governance/GLOSSARY.md`. The `result` records the
container ruling, the eleven terms plus `element`, and the six dispositions with the migration
deliberately unexecuted. The phase was not in `next_up`, so nothing was pruned.

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

## Review

An independent sub-agent reviewed commit range `2d9290f..e76a385` with no context from this session,
ran the three verification commands itself, and was asked to judge the acceptance conditions from the
diff rather than from this record's claims. Its findings, condition by condition.

Its own runs:

```
$ uv run python tools/generate_glossary.py
wrote /code/d-system/docs/08-governance/GLOSSARY.md — 10 term(s)
$ git status --porcelain
(empty)

$ uv run pytest -q
580 passed, 2 warnings

$ uv run python -m src.governance
Governance OK: 27 systems, 227 documents, 25 memories, 181 backlog phases   [exit 0]
```

**Condition 1 — R01 — Met.** "All eleven terms exist as real definitional entries, not incidental
prose. … I read the bodies: each opens with a genus-and-differentia definition and a contrast clause
… and each is anchored to a file or field that exists. … These are definitions, not grep hits."
On the two qualified headings: "I judge these legitimate, not evasion. R01 asks that the vocabulary
*define* the terms; both entries do, and the qualifier is forced by genuine pre-existing overload
inside the same rendered file. `### Session` already exists at GLOSSARY.md:548 … an unqualified
`### Session` would have been a duplicate heading in one document." On `Region (workbench)`: "the
entry is the more useful for it: it records that `region` means *panel* in code identifiers …, which
is a substantive fact a bare heading would have hidden."

**Condition 2 — R02 — Met.** "Exactly one sentence. `grep -n \"is the container\"` … returns a
single hit, line 21. … It states the answer; it does not describe the ambiguity. R02's
verification-column defect condition is not triggered. The paragraph that follows *discusses*
`000135`'s doubt, but it does so to resolve it … an answer, not a survey."

**Condition 3 — R04 — Met.** "All six classes carry both a disposition and a reason. … No class is
missing either half. Each reason is specific rather than a restatement of the disposition."

**Scope check — no renames executed — confirmed.** "No layout JSON, no CSS, no test, no registry, no
`.ts`/`.tsx` … `git diff -M --summary` shows only two file creations, no git-detected renames. The
phase executed none of the migration, as it said it would not."

**Discrepancies between this record and what the reviewer found: none.** "Every claim I tested held."
Specifically corroborated:

- The committed glossary was not stale — regeneration left the tree empty.
- The `R03` severity claim: "True, and if anything understated by the requirement rather than
  overstated by the record. … I confirmed this by parsing both files and intersecting the id sets:
  `overlap: ['notes-strip', 'terminal']` in each."
- `phase-wbf-01` declares the wrong system: "True. … `HtmlViewerRegion.tsx` is not among them; it
  belongs to `sys-wb-viewer`. The lock does not cover the work."
- `panelRegistry.tsx` cites a non-existent field: "True. … `grep -c admits` on both layout files
  returns 0. `admits` exists only on the resolved in-memory `LayoutSlotDefinition`."
- The private-content figures and the memory and catalog counts all reconcile.

The reviewer could not reproduce the worktree-side private-content figure, because the worktree had
already been merged away by the time it ran: "the mechanism described … is consistent with the tool's
output shape." That is a limit on the corroboration, not a contradiction of the claim.

## Decisions

**The container ruling was the owner's to make, and was put to them before any file was written.**
The phase's `next_action` directs the agent to state the answer, and `R02` makes describing the
ambiguity a defect — but `000135` records the owner as explicitly unsure and directing that nothing
terminology-related change until it was settled. Settling it by agent judgement alone would have
answered a question the owner had reserved. It was put as a choice between the two readings with the
cost of each stated, alongside the slot-naming scheme and the heading-collision handling. The owner
took the recommendation in all three cases.

**`element` was added beyond the eleven terms `R01` requires.** Not scope creep: without a word for
what a panel contains, the container ruling reads as contradicting the owner's own observation in
`000135` rather than resolving it. The term is what makes "your instinct was right, one tier down" a
statement about the system instead of a concession.

**`primary`/`secondary` over geometry names.** The same slot is a different shape in each layout, and
assignments are stored per `layout_id` per `panel_id`, so geometry-derived ids would differ per layout
and break the moment `phase-arch-09` moves a slot.

**The inherited `dev` breakage was not fixed on this branch.** `test_the_committed_markdown_matches_
regenerated_output` was failing on `dev` itself, from a peer's commit. Regenerating `ideas.md` here
would have turned this branch green while hiding that `dev` was red when the peer integrated. The
owner ruled it fixed on `dev` instead, and this branch was rebased onto that fix.

**A peer's uncommitted work in the primary checkout was left untouched.** The claim commit was made
with explicit pathspecs rather than `git add -A`, so `_data/ideas.jsonl`, `systems.yaml` and a peer's
session record stayed exactly as found.

## Corrections

**The session record was missing `## Acceptance` and `## Backlog`.** Both are required by the session
record contract in `.claude/skills/checkpoint/SKILL.md`, and the first draft went straight from
`## Verification` to `## Found wrong in the source material`. Caught while running the checkpoint
procedure at close and added. The lesson is that writing a record from the shape of the work rather
than from the contract loses the sections that make records comparable to each other.

**The catalog was not regenerated when the session record was committed.** This turned the first
post-rebase run red — `test_committed_catalog_matches_regenerated_output` and
`test_catalog_flag_writes_committed_file`, two of the three failures. Any governed document forces
the regeneration, not only the claim. Fixed in its own commit.

**A cross-reference in the concept memory pointed at a heading that does not exist.** The first draft
cited `### Region` under *Skills and agents*; only `### Session` is there. Corrected before the file
was first committed.

**Wall-clock timings were left in the recorded command output.** The record contract requires them
stripped so that a rerun against unchanged state produces a byte-identical record. Removed at close.

## Left undone

**The migration itself**, deliberately and by design. `phase-arch-02` executes all six classes.
`PLAN-028` design decision 2 separates them precisely so the six ideas waiting on the vocabulary are
not held behind a rename touching layout data, CSS, requirement prose, stored state, the registry and
the tests.

**One constraint `phase-arch-02` inherits with nothing mechanical to enforce it**: the
`schema_version` bump and the slot id rename must land in the same change, or live browsers are
stranded on stored assignments naming slots that no longer exist. It is stated in the ruling and here;
a check for it would belong to that phase.

**The four source-material defects were reported, not fixed.** Each sits outside this phase's declared
systems, and three of them belong to phases that have not run yet:

- `phase-wbf-01` declares `sys-ui`, which no longer covers `HtmlViewerRegion.tsx`. Editing another
  phase's declarations is not this phase's to do, and the mis-declaration means the validator would
  not stop a peer editing that file concurrently. Worth fixing before that phase is claimed.
- `panelRegistry.tsx`'s doc comment cites an `admits` field that does not exist in the layout JSON.
  It is `ts/src/workbench`, inside `sys-wb-layout` which this phase holds — but it is a code comment,
  and `phase-arch-03`/`-04` are about to audit those files.
- `REQ-011` R03 records only half its own failing case, omitting the `slot_id`/`panel_id` collision.
  Amending a requirement row mid-programme was out of scope here; the naming rule covers both halves.
- The private-content check runs weaker in a worktree (`0 identifiers checked`) than in the primary
  checkout (`31`), because `_private/portfolio/` is absent there. The full check ran against the
  merged result. A worktree-only run is not the check it appears to be, which is worth knowing for
  every worktree session, not just this one.

**The `overview` panel type is left registered and unruled on** — whether `OverviewRegion` still earns
its place now that the HTML Viewer serves the same page is a duplication question for
`phase-arch-03`, not a naming one.

