---
schema_version: 1
id: doc-session-bookmark-category-surface
code: SESS-2026-10-08-08
title: Build the bookmark category surface and its consumers (phase-wbf-05)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-ui, sys-api]
depends_on: [doc-adr-bookmark-categories-batch-bridge, doc-session-panel-bridge-batch]
---

# Build the bookmark category surface and its consumers (phase-wbf-05)

## Phase

`phase-wbf-05` (build the bookmark category surface and its consumers), group of
[`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md). Builder B (`agent-builder-b`)
under the Session Manager's pre-approved run of 2026-10-08. Branch `agent/phase-wbf-05`, cut from
the run's integration branch `ccr-b69b05b4-tdcrux`.

## Outcome

Built against [`ADR-029`](../04-decisions/ADR-029-bookmark-categories-and-batch-bridge.md)
(proposed; awaiting the owner's ratification, pre-approved run, 2026-10-08).

Storage and routes:

- `src/api/routes/workbench_bookmarks.py` holds the six routes under `/api/v1/workbench/bookmarks`
  (list, read, create, rename, delete, add a file, remove a file). `src/api/__init__.py` mounts it
  under the same `D_SYSTEM_DEMO_TERMINAL=1` flag as `workbench.py`; with the flag unset every route
  is 404 and the module is not imported.
- One record per category at `<data root>/workbench/bookmarks/<category_id>.json`, with the data
  root resolved by `data_root()` on every request. Writes use a temporary file in the same
  directory, an atomic replace, and one process lock around each read-modify-write.
- Ids: lowercase slug, at most 64 characters, `-2`, `-3` on collision, `category` when the name has
  no ASCII letters or digits, `-category` appended to a Windows device name (`con-category`). A
  malformed or reserved id is reported as 404 before any file name is formed. Rename changes `name`
  only. Names are 1 to 80 characters, no control characters, unique case-insensitively.
- Entries are validated on write with the ADR-015 rules: absolute, drive-lettered, `..`, a symlink
  leaving the repository, a directory, `_private/`, `.git` and gitignored paths are refused (400);
  a path that does not exist is 404; a duplicate is 409. Backslashes become forward slashes, case is
  preserved. Every read resolves each entry to `present`, `missing` or `excluded` and prunes nothing.
  Removing an entry does not need the file to exist.
- `schemas/workbench-bookmark-category.schema.json` and the tracked example
  `_data/workbench/bookmarks/demo-tour.json` (three tracked files).

Consumers (File Browser and HTML Viewer only):

- `HtmlViewerRegion.tsx` implements `openFiles(paths)` with the section 6 point 8 placement policy.
  The policy is a pure function (`viewerPlacement.ts`): empty tabs first, then new tabs up to
  `MAX_TABS`, a tab holding a page is never replaced, overflow is declined `capacity`, an unsupported
  file `incompatible`, and the first delivered file's tab becomes active.
- `bookmarks.ts` is the API client and the one place a category is opened as a set: read the
  category, pass only `present` paths to `deliverBatch`, merge what the viewer declined with the
  `missing` and `excluded` entries, and render "Opened X of Y from NAME; N declined: reasons" with a
  line per path.
- `BookmarkCategories.tsx` (a section of the File Browser) lists, creates, renames and deletes
  categories, lists a category's files with missing and excluded entries marked by path, removes a
  file, and opens a category as a set. "Open as set" is disabled while no viewer is registered
  (`useBatchAvailable`), never an error. `FileTreeContextMenu.tsx` gains "Add to bookmark category",
  with a "New category" path that creates and adds in one step; the menu item is absent for a
  directory and disabled when the bookmark routes are unavailable.
- Private-file entries (under `_private/` or any gitignored path) are deliberately unsupported. This
  is stated in the route module, the schema description, `bookmarks.ts` and the context menu.

## Acceptance

- REQ-012 R09: met. Six operations work through the routes and through the UI; the stored record
  changes as the ADR specifies (pytest asserts the on-disk JSON after each operation, and validates
  each stored record against the schema).
- REQ-012 R10: met. `bookmarks.test.tsx` delivers a three-file category to a stub viewer and the
  viewer receives all three; `HtmlViewerRegion.openFiles.test.tsx` opens three files in three tabs
  of the real panel; the Playwright pass opened three files in three tabs of the running app.
- REQ-012 R11: met. A category naming a deleted file opens its remaining files and the receipt names
  the missing one by path (unit test, and the Playwright pass: "Opened 3 of 4 from "Demo three";
  1 declined: 1 file not found." with `docs/_pw_tmp_gone.md` listed).

## Review points addressed

- The route tests build their own category under a temporary data root and a temporary git
  repository standing in for the repository root; none reads the tracked example. The schema test
  validates the tracked example separately, by file, not through the routes.
- A category with more than `MAX_TABS` viewer-compatible files declines the overflow with `capacity`
  and the surface says "opened X of Y".

## Playwright pass

Run on API port 8014 and Vite port 5184 with `D_SYSTEM_DEMO_TERMINAL=1` and a temporary
`D_SYSTEM_DATA_ROOT`, Chromium headless. Exercised: the empty state; creating a category from the
context menu ("New category") and adding four files; the stored entry order through the API; a
private path refused with 400; the expanded file list; opening the set (3 of 4 opened, the missing
file named, 4 viewer tabs, first delivered file's tab active, each tab showing its file); a set
opened into a viewer whose four tabs all hold pages (restored from browser storage), which declined
all three files with `capacity`; rename (id unchanged); delete.

Not exercised in the browser: the viewer-absent state (layout with no HTML Viewer) and the flag-unset
state; both are covered by Vitest and pytest instead. One console error appeared: the browser
blocked a script in `_public/d-system-architecture.html` because the viewer iframe is sandboxed with
no `allow-scripts`. That sandbox predates this phase and is intended; it is not new behavior.

## Review

Three reviewers returned pass on commit `4bb71ff`. Verdict records, copied unchanged:
`docs/08-governance/reviews/verdicts/2026-10-08-phase-wbf-05-demo-adversary.json` (gating, 4 minor),
`docs/08-governance/reviews/verdicts/2026-10-08-phase-wbf-05-security-review.json` (gating, 1 major
and 5 minor) and `docs/08-governance/reviews/verdicts/2026-10-08-phase-wbf-05-review-judge.json`
(shadow, 3 minor).

- SEC F01 (major, a symlinked directory defeats the private and ignored check; a symlink to `.git`
  is accepted): fixed. `git check-ignore` runs on the resolved path only; the private test runs on
  the resolved repo-relative path; an entry whose lexical path differs from its resolved path
  (`os.path.normcase`) is refused on write and reads `excluded`; this module has its own ignore
  check that treats a git exit code other than 0 or 1, or git failing to run, as everything ignored
  (`workbench.py`'s helper fails open and is outside this phase's deliverables). Tests: a symlinked
  directory into `_private/`, a symlinked directory and a file symlink to `.git`, a symlink to an
  ordinary file, and a failing git.
- SEC F02, ADV F01, JUDGE F02 (hostile paths give 500; one bad stored entry breaks the category
  GET): fixed. `normalize_entry_path` refuses NUL, text that is not valid UTF-8, a path over 1024
  characters and a segment over 255 with 400; `_inspect` and `validate_entry_file` catch
  `OSError`, `ValueError` and `UnicodeError`; a hand-edited unusable entry reads `excluded`, the GET
  succeeds, and the entry can be removed by its stored text. A record holding text that cannot be
  encoded is treated as unreadable. Schema gained `maxLength` 1024 and `maxItems` 500.
- SEC F03, ADV F02 (`.git` and `_private` matched by first lexical segment, case-sensitively):
  fixed. Every segment of both the lexical and the resolved path is compared casefolded with
  trailing dots and spaces removed, at any depth. Tests: `sub/.git/config`, `.GIT/config`,
  `.git./config`, `docs/_PRIVATE/x.md`. The Windows presentation machine is owner-machine, not run.
- SEC F04 (cross-origin write protection rests on a FastAPI default): fixed with a router
  dependency: 415 unless `Content-Type` is `application/json` on POST, PATCH, and DELETE with a body
  (the category delete has no body). `pyproject.toml` untouched.
- SEC F05 (no size or count limits): fixed. 500 entries per category and 200 categories (409),
  request bodies over 64 KB refused (413, by `Content-Length` and by the body read). The body is
  still read by FastAPI before the dependency runs, so this bounds what is accepted, not what is
  read; a streaming limit would need middleware, outside the deliverables.
- SEC F06 (durability and locking): `os.fsync` before `os.replace`, fixed. The shared-data-root
  limit (the lock is per process) is named in the module docstring. Not done, outside the
  deliverables: a `.gitignore` entry for `_data/workbench/bookmarks/.*.tmp`, and an ADR-029 note that
  a data root shared across backends is unsupported.
- ADV F03 (the id guard is not pinned by a test): fixed. Unit tests of `is_valid_category_id` and
  `_record_path` for backslash, `..`, uppercase, `con`, `com1`, 65 characters, empty and `a--b`,
  plus valid ids.
- ADV F04 (first delivered file becomes the active tab is untested against the real panel): fixed.
  A vitest opens one file, then three, and asserts `Tab 2` is selected.
- JUDGE F01 (the full suite exits 1 on a root-only test): not changed. The failing test is
  unrelated and outside the deliverables; reported as an idea.
- JUDGE F03 (a path beginning with a letter and a colon is rejected as drive-lettered, including a
  valid POSIX name): accepted. Deliberate and consistent across the routes and the schema.

## Awaiting ratification

`ADR-029` is proposed; awaiting the owner's ratification (pre-approved run, 2026-10-08). A different
ruling changes this phase's scope. Ratification points that bear on the built behavior:

1. Records live under the data root, not always-tracked. With `D_SYSTEM_DATA_ROOT` unset, writes
   land in the tracked `_data/workbench/bookmarks/` and appear in `git status`.
2. The six write routes, the first in the workbench API.
3. A set never replaces a tab holding a page. The viewer's first tab is seeded with the overview
   page on a fresh browser, so a fresh viewer has room for three more tabs, and a viewer restored
   with four open pages declines every file.
4. Best-effort per target; no rename tracking and no auto-prune.

## Assumptions

1. Status codes for the new routes follow `workbench.py`: 400 for a path or name that is never
   valid, 404 for an unknown or malformed id and for a path that does not exist, 409 for a duplicate
   name or entry, 201 for create and add, 200 otherwise. The ADR names none.
2. Adding a file already in the category is refused (409) rather than accepted silently.
3. A name that is `con ` and `con` once trimmed is the same name (409), so the id `con-category-2`
   arises only from a different name such as `CON!`.
4. A record whose file name and `category_id` disagree, or that is not valid JSON, is skipped by the
   list route and reported 500 on read; a broken record still owns its file name, so a new category
   cannot overwrite it.
5. The `new tab` placement gives a new viewer tab the directory of its file; a filled empty tab keeps
   its own directory unless it has none, in which case it takes the file's, so the overview seed
   does not overwrite the file.
6. The category surface is a section of the File Browser (the ADR leaves the host to this phase),
   collapsed by default.
7. "Declined" in the receipt counts every entry not opened, including `missing` and `excluded`
   entries the surface withheld, because the owner reads one line for the whole set.
8. The commits carry the harness's attribution line for the model that did this work
   (`Claude Sonnet 5.5`), not the one the builder contract text names.

## Evidence

See the result line of the backlog entry and the final report for the command output.

## Unresolved

Nothing outstanding for this phase. Deferred by the ADR, not built: terminal injection of a
category's paths, and the notes rotator's image source.
