---
schema_version: 1
id: doc-session-governance-atlas-page
code: SESS-2026-10-04-10
title: Build the governance atlas page
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-html]
depends_on: [doc-html-generation-design-system]
---

# Build the governance atlas page

## Phase

`phase-des-02` — Build the governance atlas page in the atlas family.

The title is out of date: the owner moved the page to the house family on 2026-09-30, and the
phase's own scope says so. The page is built from the house family.

## Verification

`uv run python -m src.governance`

```text
Governance OK: 44 systems, 435 documents, 36 memories, 347 backlog phases
```

`uv run pytest`

```text
1454 passed, 1 skipped, 1 warning
```

The acceptance conditions are about the page, which no test covers. The owner chose a hand-written
page, and the phase declares no `test/` deliverable. The following checks were run by hand:

- **Four subjects.** The page's sections are:
  - "The four parts";
  - "1. Document codes and the allocator";
  - "2. The backlog and the claim model";
  - "3. The `GOV` series";
  - "4. The idea lifecycle and the sanctioned writer";
  - "5. How the parts refer to each other".
- **House family, no colour literal.** The page is `templates/html/house-page.html` filled through
  `tools/generate_house_css.py`'s own strict `fill()`, with `house.css` and `house-components.css`
  inlined unchanged. With the inlined `house.css` removed, a search for colour literals
  (`#hex`, `rgb(`, `rgba(`, `hsl(`, `hsla(`) over the page finds none. The page has no `<script>`,
  and its HTML parses with every tag closed.
- **Light and dark.** `ROOT_ATTRS` is empty, so the page follows `prefers-color-scheme` through
  the family's own rules. It was rendered in headless Chrome with JavaScript disabled:
  - at 1280 px in the default light scheme;
  - at 1280 px with `--blink-settings=preferredColorScheme=0` for dark;
  - at 390 px.

  The page rendered completely in each mode. At 390 px, tables scroll inside their `.tbl-wrap`, and
  the page does not scroll sideways. No template or stylesheet file changed.
- **Private content.** `uv run python tools/check_no_private_content.py` in the worktree read 0
  identifiers, because the worktree cannot see `_private/portfolio/`. The same check was then run
  from the worktree with the primary checkout's identifier list, through the script's own
  `confidential_identifiers()` and `check_content()`: 31 identifiers, 0 violations.

## Acceptance

- `REQ-021` R13 as amended on 2026-09-30 (all four subjects appear, built from the house family,
  no colour literal outside the generated token CSS): Met. See the four checks above.
- `REQ-021` R12 (the page covers governance, not idea or backlog reporting): Met. The page
  explains how the idea log and the backlog work. It reports no ideas, phases or counts, so it
  makes none of `phase-idg-08`'s rulings. The 2026-09-30 amendment note to `REQ-021` also records
  R12 as spent.
- The page renders in light and dark through the house family's mode flag, with no change to the
  family: Met. `git diff dev -- templates/` is empty.

## Backlog

`status: active`. The phase stays active until the branch is merged onto `dev` with the owner's
approval. The completion edit follows the merge on `dev`.

## Unresolved

- The page is a snapshot written by hand. Its `GOV` table and series table list what existed on
  2026-10-04 and will need a hand edit when either changes.
- Research for the page found six places where the governing documents disagree with each other
  or with the code. The page states none of the disputed facts; each one went to Ideation as
  `000574` to `000579`. The repository idea writer's lack of a lock was already idea `000158`.
