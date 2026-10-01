---
schema_version: 1
id: doc-engine-pages-house-style-requirements
code: REQ-036
title: Idea realization engine pages and the house-style tokens
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-30'
updated: '2026-09-30'
systems: [sys-html, sys-backlog, sys-governance]
depends_on: [doc-html-generation-design-system-requirements]
---

# Idea realization engine pages and the house-style tokens

The requirement for the 2026-09-30 amendment to the HTML generation and design system plan
(`PLAN-036`). `PLAN-036`'s own requirement (`REQ-021`) stays in force except where the
"Effect on REQ-021" section below changes it.

## Observed problem and scope

On 2026-09-30 the owner changed the priority of this programme to **the idea realization engine's
generated HTML pages**. The engine (`ARCH-006`) carries an idea from capture to delivered work through
nine stages and five owner gates, but no generated page shows that pipeline. The state is spread
across the idea log, `docs/09-backlog/backlog.yaml`, the seven batch tables under
`docs/09-backlog/batches/` and the plan documents.

Two earlier decisions feed this requirement:

- **The house style is decided.** Idea `000511` records the owner's rulings of 2026-09-28: one house
  style with variants on shared tokens, webfonts from Google Fonts with a system-font fallback, and
  repository tokens as the source of truth. On 2026-09-30 the owner approved the round-2 gallery
  as shown (`https://claude.ai/artifact/D15aCx8HqwfVmKmKtKDKFi`). It shows the magazine house style,
  Swiss and technical-mono variants that change only type, spacing and rules, and light and dark modes
  that swap colours only.
- **The ideas-and-backlog pages are wanted.** The owner ruled on 2026-09-21 that the generated pages
  idea `000042` asks for are kept (`GOV-003`, "The generated ideas-and-backlog page is kept, not
  declined"). `000300` and `000301` are the refinements of that ask.

### What exists today, verified on 2026-09-30

```
$ uv run python -c "... fold(ideas.jsonl) ..."
521 ideas: 490 triaged, 13 promoted, 10 reviewing, 7 discarded, 1 open
0 ideas carry any ARCH-005 classification field (record_kind, ontological, epistemic, lifecycle, temporal)
13 ideas carry promoted_to; 38 links point at a document code

$ backlog.yaml
341 phases: 193 queued, 129 complete, 17 deferred, 1 active, 1 blocked
no phase field names an idea; ideas appear only in phase prose

$ ls docs/09-backlog/batches/
batch-001 ... batch-007 (seven batch tables, schemas/batch.schema.json)

$ ls _data/gate-decisions.jsonl
No such file or directory
```

The current styles of every surface are inventoried in the Scout's report
`_working/session-manager/scout/style-inventory.md` (gitignored, 2026-09-28). No surface uses the
approved house style yet. The round-2 gallery is the only rendering of it.

### Owner rulings this requirement records (2026-09-30, in this session)

| Question | Ruling |
|---|---|
| How the old design phases fit the new ones | Pages first. The token phase and the four pages are not gated on the audit (`phase-des-01`). The palette library (`phase-des-05`) is superseded by the token phase. The template and component libraries (`phase-des-03`, `-04`) move after the pages and extract from them. The audit stays but gates nothing new. The governance atlas page (`phase-des-02`) and the designer agent (`phase-des-06`) stay, moved onto the house style. |
| Where the per-idea trace gets its links | A structured idea-id field on backlog phases, backfilled, before the trace page is built |
| Where gate decisions come from | Derived from existing records, each labelled with its source |
| What "axis" means in the idea funnel | The four `ARCH-005` axes, shown as they are, including "unclassified" |
| Mirroring the tokens to a Claude Design System artifact | Later. Recorded as open, not sized here |
| How generated pages are stored | Committed snapshots stamped with the source commit and its date. No CI gate fails when inputs move on |

## Observable requirements and verification

### House-style tokens and family

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | The house style's colour, font, size, spacing, rule and radius values are defined in one tokens data file under `templates/styles/`. The family's CSS is generated from that file, and regenerating it from an unchanged tokens file gives byte-identical CSS. | A test regenerates the CSS and diffs it against the committed file. A grep of the house family's templates finds no colour literal (`#hex`, `rgb(`, `hsl(`) outside the generated CSS. |
| R02 | The token values are the ones the owner approved in the round-2 gallery: the house palette in light and dark, the status pairs (ok, warn, info, error), and the fonts (Bricolage Grotesque display, Literata body, JetBrains Mono code, and Archivo for the Swiss body). | A test compares the tokens file with a fixture that transcribes the gallery's values. The fixture cites the gallery URL and the artifact version it was read from. A value that differs fails the test. |
| R03 | The Swiss and mono variants set no colour value. They change only type, size, spacing and rule tokens. | A test parses each variant's generated block and fails on any colour custom property in it. |
| R04 | Dark mode is one flag that redefines colour tokens only. Pages follow `prefers-color-scheme`, and the root element's `data-theme="light"` or `data-theme="dark"` overrides it. This is the mechanism `_public/idea-realization-system.html` uses. | A test parses every dark-mode block and fails on any non-colour property. Render one page in both modes and with each override, and confirm the layout does not change. |
| R05 | Each font token lists Google Fonts first and ends with a system stack and a generic family, so a page whose font request fails still renders in a readable system font. | A test asserts every font-family token ends with a generic family. Render a page with the Google Fonts request blocked and confirm the text renders. |
| R06 | The house family is registered in `templates/README.md`'s family table, with its files, its variants and how a page selects a variant and a mode. | Read the table. |

### All engine pages

| ID | Required observable behavior | Verification method |
|---|---|---|
| R07 | One command regenerates every engine page from tracked inputs only: the idea log, `backlog.yaml`, the batch tables, plan front matter and the git history of `dev`. Two runs on the same commit produce byte-identical output. | A test runs the generator twice into temporary directories and diffs the output. |
| R08 | Each page is committed under `_public/engine/` and states the source commit and that commit's date. It uses the commit date, not the time the generator ran, so R07 holds. No CI check fails because a page is older than its inputs. | Read the stamp on each page. Confirm no test or CI step compares `_public/engine/` against a fresh regeneration. |
| R09 | Pages are built from the house family. Their output contains no colour literal outside the generated token CSS. | Grep the generated pages. |
| R10 | Generators read idea state through `fold()` (`src.db.ideas`), never by parsing `_data/ideas.jsonl` themselves. | Grep the generator sources for direct reads of the idea log. |
| R11 | Every number and gate entry on a page comes from a named source. Where no record exists, the page shows "not recorded" and names the missing record instead of estimating. | A reviewer samples ten numbers per page and traces each to its source. A test confirms G2 entries read "not recorded" while no structured partition record exists. |
| R12 | A reader can read every page's content with script disabled. Mode switching by `prefers-color-scheme` needs no script. | Load each page with JavaScript disabled and confirm no content is missing. |
| R13 | Generated pages contain no confidential identifier. | Run `tools/check_no_private_content.py` with the pages staged and confirm it passes. |

### Page 1: pipeline overview

| ID | Required observable behavior | Verification method |
|---|---|---|
| R14 | The page shows the nine `ARCH-006` stages, each with a count or "not recorded", and the five gates, each with what is waiting at it. The waiting items are derived as the table below states. | A test recomputes each count with an independent script and compares. A reviewer checks the derivation table against the page. |

| Gate | What the page shows as waiting there | Source |
|---|---|---|
| G1 Idea approval | Nothing waits. The count shows ideas captured | `fold()` |
| G2 Track acceptance | Triaged ideas with no `promoted_to` and no phase naming them | `fold()`, the phase idea field (R17) |
| G3 Plan approval | Plans whose front matter reads `draft` | plan front matter |
| G4 Integration and G5 Completion review | `active` phases. Integration has been fast-forward-only since 2026-09-10, and the completion edit follows the merge in the same turn (the Session Manager's contract, item 4), so the two gates have one queue | `backlog.yaml` |

### Page 2: idea funnel and ledger

| ID | Required observable behavior | Verification method |
|---|---|---|
| R15 | Every idea in `fold()` appears exactly once in the ledger, with id, title, status, created date and the four axis values. The funnel's per-status counts sum to the `fold()` total. | A test compares ledger ids with `fold()` keys and sums the funnel counts. |
| R16 | Each of the four `ARCH-005` axes is shown with its distribution, and ideas without a classification are counted as "unclassified". Today that is every idea. | A test confirms the unclassified count equals the number of ideas with no `classified` event. |

### Structured idea links on phases

| ID | Required observable behavior | Verification method |
|---|---|---|
| R17 | A backlog phase may carry an `ideas` list of six-digit idea ids. The schema accepts it, and `uv run python -m src.governance` rejects any id that `fold()` does not contain. | Add a phase with a made-up id in a test fixture and confirm the validator fails naming it. Then confirm the committed backlog passes. |
| R18 | The field is backfilled. Every phase whose `scope`, `acceptance` or `next_action` names a six-digit id that exists in `fold()` carries that id. The backfill is a `src.governance` mode whose output can be re-run and compared. | Re-run the backfill in check mode and confirm it reports no missing and no extra ids. |

### Page 3: per-idea trace

| ID | Required observable behavior | Verification method |
|---|---|---|
| R19 | Each idea with a recorded plan or phase link (`promoted_to`, or a phase's `ideas` field) has a trace page. Every other idea shows "no recorded plan" in the ledger and has no trace page. | A test compares the set of trace pages with the set of linked ideas. |
| R20 | A trace shows capture, then plan, then phases with their states, then delivery, with gate entries derived as follows. G1 is the idea's `created` date. G2 is "not recorded", because no structured partition record exists in the repository. G3 is the plan's status, dated by the earliest `dev` commit where the plan's front matter reads `approved`, `active` or `complete`. G4 and G5 are one entry: the earliest commit on `dev`'s first-parent history where the phase reads `complete`. Owner rulings are the idea's annotations of kind `assessment`. Every entry names its source. | A test builds the trace for one idea with a known history and compares each entry with the git log and the fold. |

### Page 4: backlog and batch graph

| ID | Required observable behavior | Verification method |
|---|---|---|
| R21 | Every phase in `backlog.yaml` appears with its state: complete, ready, waiting, active, blocked, deferred or cancelled. Ready and waiting are computed by `src.governance.backlog.readiness`, the function `--ready` uses. | A test compares the page's states with `src.governance`'s own readiness computation. |
| R22 | Each batch table appears with its stages, their phases and their states, and its external dependencies. Dependencies (`depends_on`) are drawn as edges in a graph rendered without script. | A test compares each batch's phases and stages with its YAML. Load the page with script disabled and confirm the graph renders. |
| R23 | Every waiting, blocked or deferred phase states why. A waiting phase lists its unmet dependencies by id and state. A blocked or deferred phase shows its `blocked_reason` and `resume_when`. | A test confirms every non-ready queued phase on the page lists at least one unmet dependency, and every blocked or deferred phase shows both fields. |

### Effect on the existing design phases

| ID | Required observable behavior | Verification method |
|---|---|---|
| R24 | The backlog shows the owner's 2026-09-30 sequencing. `phase-des-05` is `cancelled` with a `blocked_reason` naming the token phase and this requirement. `phase-des-03` and `phase-des-04` depend on `phase-des-01` and the four page phases. `phase-des-06` depends on the token phase instead of `phase-des-05`. `phase-des-02` depends on the token phase and builds in the house family. No new phase depends on `phase-des-01`. | Read the six entries and run `uv run python -m src.governance`. |
| R25 | `REQ-021` records which of its rows this amendment changes: R09 and R10 are superseded by R01 to R04 here, R12 is spent by the 2026-09-21 ruling, and R13 moves to the house family. | Read `REQ-021`'s amendment note. |

## Effect on REQ-021

- **R09 and R10 (palette library) are superseded.** The palette's role set and its light and dark
  coverage were the open questions `000085` left. The owner's approval of the round-2 gallery
  answers both, and R01 to R04 here make the answer testable.
- **R12 is spent.** It forbade any design phase from building a page whose existence `phase-idg-08`
  was ruling on. The owner made that ruling on 2026-09-21 and kept the pages. Building the idea
  funnel and the backlog page here is therefore not a violation. `phase-idg-08` still records the
  ruling and wraps the metrics command, and it builds no page.
- **R13 changes family.** The governance atlas page is built in the house family, not the atlas
  family. The three existing atlas pages are not changed by this amendment.
- **R04 now applies only to the library phases.** The template and component phases still cite
  the audit. The token phase and the page phases do not wait for it.

## Boundaries

- **Monitoring artifact (`000497`, investigated by `PROMPT-042`).** The monitoring artifact covers
  sessions, branches, worktrees and claims. These pages show the engine's records only: ideas,
  plans, phases and batches. Sessions, branches and worktrees are not shown here. The monitoring
  work may reuse these pages or their family.
- **Batch graph orchestration (`phase-irs-14`).** That phase builds the orchestrator's batch graph,
  a LangGraph fan-out. Page 4 draws the batch tables. The two share a name and nothing else.
- **The workbench explorers (`phase-wb-06`).** These stay the live, interactive view. These pages
  are shareable snapshots. The 2026-09-21 ruling keeps both.

## Not in this requirement

- **The Claude Design System mirror of the tokens.** The owner ruled it later on 2026-09-30. The
  plan names it as open.
- **Migrating the existing pages.** The atlas, overview and lit-report families and the
  `_public/` pages keep their current styles.
- **Contrast admission checks for palettes.** `000085` raised the question, and the owner approved
  the gallery's values as shown. The question stays open on `000085`.
