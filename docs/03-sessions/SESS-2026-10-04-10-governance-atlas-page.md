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

`status: active`, with `session: doc-session-governance-atlas-page`, `completion_evidence` (the page
and this record) and `result` recorded on the branch, per `AGENTS.md` step 5. The phase stays
active until the branch is merged onto `dev` with the owner's approval. The completion edit on
`dev` then sets `status: complete`.

## Unresolved

- The page is a snapshot written by hand. Its `GOV` table and series table list what existed on
  2026-10-04 and will need a hand edit when either changes.
- Research for the page found six places where the governing documents disagree with each other
  or with the code. The page states none of the disputed facts; each one went to Ideation as
  `000574` to `000579`. The repository idea writer's lack of a lock was already idea `000158`.

## Review

A `demo-adversary` agent reviewed `b8dbdad..3ac69aa`. It reached its turn limit and was asked to
report from what it had. Its report, condition by condition:

- Verdict: PASS WITH FINDINGS. The findings concern process, not the page's content.
- R13: Met.
  - All four subjects are present (`#codes`, `#backlog`, `#gov`, `#ideas`), plus the cross-reference
    section.
  - The inlined CSS is byte-identical to `house.css` followed by `house-components.css`. The page
    skeleton matches `house-page.html`.
  - All 51 hex literals sit inside the style block. The body has no `style=` attribute and no
    `<script>`. A hit on `#bac` is the `href="#backlog"` anchor, not a colour.
- R12: Met. The page shows no idea or backlog counts or metrics.
- Light and dark: Met. The page rendered in headless Chrome in light, and in dark with
  `preferredColorScheme=0`, and the two screenshots differ. `git diff b8dbdad..HEAD -- templates/`
  is empty.
- Factual accuracy: no error found in more than 20 claims checked against primary sources:
  - the series table, the allocator and `--next-code <kind>`, and "a gap is never refilled";
  - the three reservation and retirement mechanisms;
  - the claim, worktree, rebase and merge steps;
  - the `GOV` list, with `GOV-012` reserved and `GOV-019` never issued;
  - the front-matter fields, and the statuses allowed for each kind, checked against the
    enforcement code;
  - the idea event kinds, and every row of the status-transition table, checked against the
    schema;
  - the `fold()` and `append_idea.py` behaviour;
  - the references table;
  - `GOV-003`'s three completion conditions.
- Finding 1, minor, process: `backlog.yaml` was not updated on the branch. `phase-des-02` had no
  `session`, `completion_evidence` or `result`, although `AGENTS.md` step 5 says to add them before
  asking to merge.
- Not checked: the full `pytest` run (it timed out in the foreground), the 390 px render, and the
  private-content check run with the primary checkout's identifiers.

Finding 1 is fixed. The three fields are now on the phase, with `status` still `active`. The
unchecked items were run in this session and are recorded under Verification.

## Decisions

- **The owner chose a hand-written page** over a generator that reads live data. That fits the
  declared deliverables, which include no `tools/` or `test/` path. The page therefore carries no
  live counts, in line with the house components' rule that numbers come from a generator. Its
  lists are dated by the header.
- **The page states no fact the governing documents disagree on.** Research found six such
  disagreements, sent to Ideation as `000574` to `000579`. For example, the claim maximum reads as
  "the configured `max_active`" rather than a number.
- **The page is assembled through the family's own `fill()`.** It is not a hand-copied skeleton,
  so it uses the house family's template and stylesheets exactly. The assembly script was a scratch
  file and is not tracked, because the content is hand-written.

## Corrections

- `AGENTS.md` hand-off step 5 was skipped: the session, evidence and result fields were left for
  the completion commit after the merge. The reviewer caught it here, and it is fixed on the branch.
  The same step was also skipped on `phase-des-11` and `phase-des-01` earlier today. On those
  phases, all three fields arrived only in the completion commit on `dev`.
- In the first render, the id cells nested `<code>` inside the already monospaced `td.id`, which
  shrank the text twice. The nesting was removed before the commit.

## Left undone

- `phase-des-02` stays `active` until the merge. The completion edit on `dev` sets
  `status: complete`.
- The page's tables are a snapshot and need a hand edit when the `GOV` series or the code register
  changes.
- The phase's title still says "in the atlas family". The phase entry is not edited for that here.
