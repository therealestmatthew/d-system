---
schema_version: 1
id: doc-adr-bookmark-categories-batch-bridge
code: ADR-029
title: Bookmark categories are data-root records referenced by stable id, opened as a set through a batch panel bridge
kind: adr
status: draft
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-ui, sys-contracts]
depends_on: [doc-structure-content-boundary, doc-workbench-api-decision, doc-workbench-layout-decision, doc-workbench-features-defects-requirements]
---

# Bookmark categories are data-root records referenced by stable id, opened as a set through a batch panel bridge

## Status

**Proposed; awaiting the owner's ratification (pre-approved run, 2026-10-08).** Written by
`phase-wbf-03` under the Session Manager's pre-approved run. The owner has not reviewed it. The
decision gates `phase-wbf-04` (extend the panel bridge to batch, multi-target actions) and
`phase-wbf-05` (build the bookmark category surface and its consumers); both build against the
recommendation below, so a different ruling changes their scope. The ratification points are
collected in "Open items for the owner" at the end.

## Context

Two ideas ask one question from two directions
([`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md), group `G49`, decision 3).

- `000111` (file bookmark categories) asks for named groupings of files, such as "favorites" or
  "live-demo", that the owner can later reference to pull up the files as a set. It states two
  halves: the grouping surface, and how the grouping integrates with the rest of the system. It
  names a storage choice (a tracked `_data/` entity versus `localStorage`), states only a leaning
  toward tracked, and says the model "needs an owner-reviewed decision before creators build panels
  against it."
- `000120` (extend the panel bridge to batch, multi-target actions) observes that "pull up a
  category's files as a set" has no mechanism today. Without a batch contract the feature either
  builds a parallel mechanism beside the panel bridge, or opens the first file only.

Facts from the repository that bind the decision:

1. **The panel bridge is single-handle and single-action by design.** `ts/src/stage/panelBridge.ts`
   defines `BridgeSlot<T>`, which holds one live handle per panel type. Two exist:
   `viewerBridge` (`openInTab(tabId, relativePath)`, one file into one tab) and `terminalBridge`
   (`injectPath(relativePath)`, one path). An action with nothing registered reads `null` and
   disables; it never throws and never queues. The File Browser context menu is the only caller.
2. **The workbench API is read-only apart from one action.** [`ADR-015`](ADR-015-workbench-api-surface.md)
   rule 4 allows GET reads only and rule 5 allows the reveal route as the sole action. Its
   Consequences state: "If the workbench ever needs a write route ... that starts from a new
   decision record; nothing here authorizes one." Creating, renaming and deleting a category from
   the UI is a write. This record is that decision record for bookmark categories only.
3. **Layouts are tracked and read-only to the UI; the browser keeps only selections.**
   [`ADR-016`](ADR-016-workbench-layout-persistence.md) puts layouts in `_data/workbench/layouts/`
   because geometry changes are reviewed commits, and puts selections in `localStorage`, where
   "clearing one key" is the stated way to reset a machine to repository defaults.
4. **Structure is tracked and content is not.** [`ADR-009`](ADR-009-structure-content-boundary.md)
   gives the test: would the file still be correct if a different person adopted the system? The
   data root (`D_SYSTEM_DATA_ROOT`, defaulting to `_data/`) holds entity content; a fresh clone
   with no environment set must pass governance and tests against the tracked fictional set.
5. **Repository paths are already one model.** The file tree, the HTML Viewer and the bridge all
   carry repository-relative paths with forward slashes, and the server validates every path on its
   resolved form against the repository root and the ignore rules (`ADR-015` rules 2 and 3,
   `resolve_repo_relative_path` in `src/api/routes/workbench.py`).
6. **The HTML Viewer holds at most four tabs** (`MAX_TABS` in `HtmlViewerRegion.tsx`) and accepts
   only the extensions in `compatibleExtensions.ts`. A set larger than four files, or a set
   containing an incompatible file, cannot be fully opened in it. The bridge contract has to say
   what happens then.

Vocabulary follows `brain/concepts/terms-workbench-ui.md`: a slot is the container and a panel is
its content. This record names no slot by identifier. The panels involved are the HTML Viewer, the
File Browser and the terminal panels. `BridgeSlot` is a code name only: it is the panel bridge's
per-panel-type handle registry, called a **bridge channel** in this record, and is not a slot in the
container sense.

## Decision

### 1. Storage: one JSON file per category, under the data root

A category is stored as one JSON file at
`<data root>/workbench/bookmarks/<category_id>.json`, where `<data root>` is resolved exactly as
entity content is resolved (`data_root()` in `src/db/source_validation.py`: `D_SYSTEM_DATA_ROOT`
if set, else the tracked `_data/`).

- **With the environment variable set** (the owner's working configuration), real categories live
  under the private data root and are never tracked, in line with `ADR-009`. A category name such
  as a client or engagement is content, and the only protection that does not depend on remembering
  an ignore rule is that the file is not in the tracked tree.
- **With no environment variable**, the root is `_data/` and the tracked tree ships at least one
  fictional example category that names only tracked files. This keeps a fresh clone green and
  gives `phase-wbf-05` a fixture for its verification. Writes on a machine with no data root set
  land in the tracked tree and appear in `git status`, the same as editing any fictional example.

Record shape (schema version 1; `phase-wbf-05` adds the JSON Schema under `schemas/` and a test
that asserts it, as `ADR-016` does for layouts):

```json
{
  "schema_version": 1,
  "category_id": "live-demo",
  "name": "Live demo",
  "entries": ["_public/overview/index.html", "docs/04-decisions/ADR-016-workbench-layout-persistence.md"]
}
```

`entries` is an ordered list of unique repository-relative paths. Order is the order the set is
delivered in. Entries are files only; a directory is rejected on write.

### 2. Reference model: a stable `category_id`, resolved by the server

- `category_id` is a lowercase slug (`^[a-z0-9]+(-[a-z0-9]+)*$`, at most 64 characters) generated
  from the name when the category is created, with `-2`, `-3` appended on collision. **It never
  changes.** It is also the file name stem, so a record cannot name a different file than its id.
  Two cases need a fixed rule. A name with no ASCII letters or digits (for example `!!!` or
  non-Latin text) yields an empty slug, so the id falls back to `category`, with the same numeric
  suffix on collision (`category`, `category-2`). A slug that equals a Windows reserved device name
  (`con`, `prn`, `aux`, `nul`, `com1` to `com9`, `lpt1` to `lpt9`) gets `-category` appended
  (`con-category`), because Windows cannot create `con.json`. The display `name` is unaffected.
- `name` is free text for display, 1 to 80 characters, unique case-insensitively within the data
  root. **Rename changes `name` only.** This is why references use the id: `R09` requires rename,
  and a reference by name would break on the first one.
- Every consumer holds a `category_id` and nothing else. No consumer copies a category's entries.
  A consumer that remembers a selection (the HTML Viewer's category selector in `localStorage`,
  the rotator's future image source under `000132`) stores the id and re-resolves on use.
- Resolution is one server read. `GET /api/v1/workbench/bookmarks` lists `{category_id, name,
  entry_count}`. `GET /api/v1/workbench/bookmarks/{category_id}` returns the category with each
  entry resolved to `{path, status}`, where `status` is `present`, `missing` (not on disk) or
  `excluded` (private or gitignored now). The status is computed on every request and never
  cached, so it cannot go stale.
- An unknown id returns 404. A consumer treats that as "category not found" and names the id; it
  does not raise. Ids are not reserved after deletion; a stale reference to a deleted id resolves to
  a new category only if the owner created one with the same name, which is the owner's own act.
- No governed-document validator integration is decided here. A plan or note that mentions a
  category does so in prose.

### 3. Path validity as the repository moves

1. **Stored paths are repository-relative with forward slashes, never absolute.** Moving or
   re-cloning the repository, or opening it on Windows after Linux, cannot break an entry through
   an absolute-path change, because each is resolved against the current repository root at read
   time. This claim is limited to that. Case is preserved as stored, so an entry whose case differs
   from the file on disk can resolve on Windows and read `missing` on Linux; that is reported as
   `missing` by design and the owner re-adds the entry with the correct case.
2. **Every path is validated on write** with the same rule the rest of the API uses
   (`ADR-015` rules 2 and 3): reject absolute paths, `..` escapes, symlinks leaving the root,
   `_private/` and gitignored entries, and directories. Paths are stored as the file tree produces
   them; separators are normalised, case is preserved.
3. **A file renamed, moved or deleted inside the repository is not repaired and not pruned.**
   The entry stays in the record and resolves to `missing`; the consuming surface names it by path
   (`R11`). Auto-pruning is rejected below. Repair is the owner removing the entry and adding the
   new path. Tracking renames through git history is not decided here.

### 4. The write surface (extends `ADR-015`)

This record authorises six routes, and nothing else, under the existing prefix:

| Operation | Route |
|---|---|
| list categories | `GET /bookmarks` |
| list a category's files | `GET /bookmarks/{category_id}` |
| create | `POST /bookmarks` (body: `name`) |
| rename | `PATCH /bookmarks/{category_id}` (body: `name`) |
| delete | `DELETE /bookmarks/{category_id}` |
| add / remove a file | `POST /bookmarks/{category_id}/entries`, `DELETE /bookmarks/{category_id}/entries` (body: `path`) |

Constraints, each inherited from `ADR-015` rather than new: mounted only when
`D_SYSTEM_DEMO_TERMINAL=1` and under the loopback-only binding; ids validated against the slug
pattern before any file name is formed, so a request cannot steer a write outside
`<data root>/workbench/bookmarks/`; paths validated per section 3; no shell or OS command involved.
The data root itself is the write boundary for the records: `data_root()` may return an absolute
path outside the repository, and the repository-root check applies to the bookmarked file paths,
not to the location of the records.
Writes use a temporary file and an atomic replace. Each add or remove is a read-modify-write under
a process lock, so two browser tabs adding different files to one category do not lose either one.
`ADR-015` rule 4 is read as "GET only, plus the routes in this section", and rule 5's allowlist of
OS actions is unchanged.

### 5. Consuming surfaces

| Surface (panel) | Role | In `wbf-05`? |
|---|---|---|
| File Browser | Producer: its context menu adds a file to a category. Consumer: lists a category's files, including `missing` and `excluded` entries by path. | Yes |
| HTML Viewer | Consumer: opens a category as a set of tabs through the batch contract. This is the `R10` path. | Yes |
| Terminal injection dropdowns | Consumer: a bookmarks group could inject a category's paths. Admitted by the contract, not built, because shell quoting of paths with spaces differs between bash, CMD and PowerShell and is undecided. | No |
| Notes strip rotator (`000132`) | Consumer: a category as an image source. [`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md) decision 5 keeps it uncoupled; the id reference makes it cheap later. | No |
| Tools and agents | Reader: the records are plain JSON under the data root, readable without a browser. | n/a |

Which panel hosts the grouping surface (a section of the File Browser or a new panel type) is
`phase-wbf-05`'s choice. The constraint on it is that it registers no bridge of its own and passes
files only through `panelBridge.ts` (section 6).

### 6. The batch contract for the panel bridge

**Consequence for the bridge, stated explicitly (`R06`): opening a category as a set requires a
batch, multi-target contract in `panelBridge.ts`. Calling `openInTab` once per file from category
code is not that contract, and a second file-passing path outside `panelBridge.ts` is a defect.**

The contract, which `phase-wbf-04` implements for the bridge and `phase-wbf-05` for the viewer's
member (names are indicative; the properties are binding):

1. **A bridge channel (`BridgeSlot`) can hold several live handles, keyed by panel-instance key.**
   `register(handle, key)` replaces the handle with the same key and leaves others. While panels
   are singletons the key defaults to the panel type id, so today's behavior is unchanged and
   existing callers that pass no key keep working; `phase-arch-08` supplies real instance ids.
   `unregister(handle)` finds the entry by handle identity across all keys and removes it only if
   that exact handle is still registered, which keeps the identity guard against a superseded
   handle's belated cleanup. `get()` returns the most recently registered remaining handle, or
   `null`; when that handle unregisters it falls back to the previous remaining one, so the
   context menu's single-file actions are untouched. `getAll()` returns an array cached by the
   channel and replaced only on register or unregister, because `useSyncExternalStore` needs a
   referentially stable snapshot; a hook over it returns `null` when the array is empty.
2. **A target handle exposes a batch method that takes the whole ordered list and returns a
   receipt synchronously.** The viewer adds `openFiles(paths)`, an optional member of `ViewerBridgeHandle` in
   `phase-wbf-04` (so the existing handle literal in `HtmlViewerRegion.tsx` still type-checks) that
   `phase-wbf-05` implements; the terminal adds `injectPaths(paths)` only when its quoting is
   decided. A receipt is
   `{ delivered: string[], declined: { path: string, reason: 'incompatible' | 'capacity' | 'failed' }[] }`.
   **Every requested path appears in exactly one list.** This is the testable form of `R07`: N in,
   N accounted for.
3. **One entry point delivers a batch.** `deliverBatch(paths, targets)` takes an explicit list of
   targets, each `{ channel, call, key? }`; an omitted key means the channel's current handle. Each listed
   target receives the full ordered list. The caller chooses fan-out; the bridge never fans out on
   its own, because delivering a set to every instance of a panel type would open each file twice.
4. **The outcome is a value, never an exception:**
   `{ requested, targets: [{ channel, key, absent: boolean, receipt?, error? }] }`. A target with no
   registered handle has `absent: true`. A target whose method throws is caught, recorded in
   `error`, and all its paths are reported as declined with reason `failed`; it does not stop the
   other targets.
5. **Degradation is preserved.** With no target registered, `deliverBatch` returns every target as
   `absent`, delivers nothing and throws nothing, and the availability hook reads `null`, so the
   action disables (`R08`). **Nothing is queued:** an undelivered path exists only in the outcome.
   The category is already the durable store, so the caller can offer the action again; the bridge
   keeps no pending list.
6. **Partial targets are best-effort per target.** If some listed targets are registered and some
   are not, the registered ones receive the list and the absent ones are reported. The action is
   enabled whenever at least one listed target is registered, and the UI names the absent ones. The
   behavior `R08` asks to be stated is this one; it is not all-or-nothing.
7. **Path resolution stays out of the bridge.** The category surface resolves the category through
   the API first and passes only `present` paths to `deliverBatch`. It reports `missing` and
   `excluded` entries by path itself (`R11`). The bridge does no I/O and no path validation.
8. **Viewer placement policy.** `openFiles` fills the viewer's empty tabs first, then adds tabs up to
   the tab cap, and never replaces a tab that holds a page. Files beyond capacity are declined with
   `capacity`; files failing the compatible-extension rule are declined with `incompatible`. The
   first delivered file becomes the active tab. The surface reports "opened X of Y" from the receipt.

Sequence for opening a category in the HTML Viewer: `GET /bookmarks/{id}`, split entries by
`status`, `deliverBatch(presentPaths, [{ channel: viewerBridge, call: openFiles }])`, then show the declined
and non-present paths by name.

## Alternatives considered

### Storage

**Browser storage (`localStorage`).** Rejected. It is the fastest to build and needs no write route
and no `ADR-015` extension; that cost advantage is real. It fails the requirement the idea itself
states, that categories "outlive one browser": the store is per browser profile, so a second
browser, a Windows and a Linux checkout, or a cleared profile each see a different set. It also
collides with `ADR-016` rule 4, where clearing the one namespaced key is the documented reset to
repository defaults; a category stored there is destroyed by the reset meant to leave data alone.
Only the browser can read it, so a tool, an agent or the terminal cannot resolve a category, which
defeats "referenceable across the system". It cannot be diffed or backed up. The browser store
remains correct for what it holds now: selections, including the id of the category a selector last
used.

**A tracked `_data/workbench/bookmarks/` directory, always.** This is `000111`'s stated leaning
and the strongest alternative. It is rejected as the only location for three reasons. First,
`ADR-009`'s test: a real category such as "live-demo" encodes the owner's selection and may carry a
client or engagement name, so it is content, and a rule that depends on the owner never typing such
a name into a tracked file is the failure mode `ADR-009` removed. Second, `ADR-016` tracks layouts
because they are reviewed commits the UI never writes; categories are written by the UI, so a
tracked location makes every click a working-tree change in whichever checkout the server runs in,
in a repository where concurrent agents work in separate worktrees. Third, `ADR-009` already
provides the mechanism that gives the tracked benefit where it is wanted: with no environment
variable the data root is `_data/`, so the example categories are tracked and a fresh clone has them.
What the data root gives up is travel by git: private categories do not follow the owner to another
machine except by the owner copying the files. The owner can move any category into tracked `_data/`
deliberately by copying the file, which keeps the choice an act rather than a default.

**A DuckDB table or a new entity directory.** Rejected. `data/d_system.duckdb` is a derived layer
rebuilt from JSON and is never a source of truth (project instructions), and a category has no
relational query that needs it. Adding it to `ENTITY_DIRECTORIES` would put a UI configuration
record through the portfolio schema machinery for no consumer.

### Reference

**Reference by name.** Rejected: rename (`R09`) would break every reference.
**Copy entries into consumers.** Rejected: two sources of truth, and a removal in one place leaves
the file in another.

### Path validity

**Auto-prune entries whose file is missing.** Rejected. The workflow here switches branches and
worktrees constantly, and a file absent on one branch exists on another; pruning on read would
destroy the owner's list on a branch switch. It also hides the failure `R11` requires the UI to
show.

### Bridge

**A parallel file-passing mechanism for categories.** Rejected: it is the duplication `000115`
audits for, and `R07` makes it a defect.
**A loop of single-file `openInTab` calls from category code.** Rejected: it gives no per-file
accounting, no tab-capacity handling and no behavior when the target is absent, so the failure case
becomes silent or partial without a record of which files were dropped.
**All-or-nothing across targets.** Rejected: with the terminal absent, a category would not open in
the viewer that is on screen, which turns an unrelated panel's absence into a refusal of the whole
action.
**Queue the batch until a target mounts.** Rejected: it breaks the bridge's never-queues property,
which exists so a stale action cannot fire after the owner changed layout. The category is the
durable store.
**Fan out to every registered instance by default.** Rejected: once several viewer instances exist
it opens each file once per instance.

## Consequences

- `phase-wbf-04` is bounded by section 6: a keyed multi-handle `BridgeSlot` with `getAll()`, the
  batch receipt and `deliverBatch`, with existing single-handle callers unchanged. Its checks are
  the `R07` invariant (delivered plus declined equals requested), the `R08` absent and partial
  cases, and a grep of `ts/src/stage/` for any file-passing path outside `panelBridge.ts`.
  `phase-wbf-04` does not touch `HtmlViewerRegion.tsx`: it makes `openFiles` an optional handle
  member and tests the contract in a bridge-level test file using stub handles. That test file is
  not in the entry's current deliverables (`ts/src/stage/panelBridge.ts` only), so the entry's
  deliverables must also name its test file.
- `phase-wbf-05` implements the viewer's `openFiles` (the placement policy in section 6 point 8) in
  `HtmlViewerRegion.tsx` with its own test, so the `R10` check runs against a real target.
- `phase-wbf-05` builds the six routes, the schema and its test, the example category, and the
  File Browser and HTML Viewer consumers. Its entry lists `ts/src/stage/` as its only deliverable
  but declares `sys-api` and verifies with `uv run pytest`; the routes, schema and tests are
  outside that deliverable, so the entry needs widening before the phase is claimed.
- The workbench API gains its first write routes, bounded as in section 4. `ADR-015` is extended,
  not superseded; its other rules stand.
- Bookmark records are the first workbench data to honor the data root. Layouts and the injection
  overrides stay at `_data/workbench/`.
- A category of more than four viewer-compatible files cannot be fully opened in the HTML Viewer
  until its tab cap changes. The receipt makes that visible; `R10` is verified with a category of
  three files, as the requirement states.
- Deleting a category leaves any remembered id in a browser selector dangling; consumers handle the
  404 as "category not found".

## Open items for the owner

These are the points the owner is asked to ratify or change.

1. **Storage location.** Data root, not always-tracked. This departs from `000111`'s leaning
   toward tracked; the argument is above.
2. **First write routes.** Section 4 authorises six routes under `ADR-015`'s gate. A ruling against
   writes would force browser storage and its limits.
3. **Scope of `wbf-05`.** File Browser and HTML Viewer only; terminal injection and the rotator
   image source deferred.
4. **Viewer placement.** Set opens add to the viewer and never replace a tab holding a page, so a
   viewer with tabs already open can decline files for capacity. The alternative, replacing the
   open tabs with the set, loses the owner's tab state.
5. **Partial targets.** Best-effort per target, as in section 6.
6. **No rename tracking and no auto-prune.** A moved file shows as missing until the owner
   re-adds it.
7. **Pointers on ratification.** This record extends `ADR-015` rule 4 (GET only) and reads
   `ADR-009` section 2 more widely than before: the data root now also holds workbench records, not
   only the entity directories listed in the `data_root()` docstring. On ratification, add a one-line
   "extended by ADR-029" pointer to `ADR-015` rule 4 and update that docstring. The data root is the
   write boundary for the records (section 4).

## Revisit trigger

Revisit if the owner moves between machines often enough that private categories not travelling
becomes a recurring cost, which would argue for a tracked shared layer beside the data root. Revisit
the batch contract when `phase-arch-08` lands multi-instance panels, since the fan-out choice in
section 6 point 3 is first exercised then.
