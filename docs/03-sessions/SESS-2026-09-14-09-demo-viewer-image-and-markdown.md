---
schema_version: 1
id: doc-session-demo-viewer-image-and-markdown
code: SESS-2026-09-14-09
title: Widen the HTML Viewer to images and markdown the night before the demo
kind: session
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems:
- sys-demo-stage
- sys-ui
- sys-delivery
depends_on:
- doc-workbench-features-defects
- doc-workbench
---

# Widen the HTML Viewer to images and markdown the night before the demo

## Phase

None. This session ran as owner-directed work with no backlog phase, under `AGENTS.md`'s provision
for it: no claim commit, branch and worktree named after the work (`agent/demo-viewer-tonight`,
`../d-system-worktrees/demo-viewer-tonight`), and the absence of a lock stated in the session's first
report so peers knew nothing was held against them.

There was no phase to claim because P11 is not planned yet and its finalize phase `phase-prog-02` is
blocked behind `phase-prog-03`, which was active and unmerged for the whole session. No phase was
manufactured to have something to claim, and nothing is marked complete — `status: complete` needs a
phase, and there is none.

The work came from the Track A coordinator prompt (`_tmpagent/demo-track-coordinator.md`), itself
recorded as idea `000235`.

## Verification

All commands run in the worktree, then re-run on `dev` after the merge. The `dev` run is the one that
decided integration.

```
uv run pytest -q
580 passed, 2 warnings
```

```
uv run python -m src.governance
Governance OK: 20 systems, 219 documents, 24 memories, 150 backlog phases
```

```
uv run python tools/check_no_private_content.py
check_no_private_content: OK (620 tracked files, 31 identifiers checked)
```

The private-content run above is from the primary checkout, where `_private/portfolio/` exists and 31
real identifiers are therefore checked. The same command in a worktree reports `0 identifiers
checked` and skips the content half — a worktree run is not evidence of this gate passing.

```
cd ts && npm run lint && npm run build
tsc --noEmit — clean
✓ built
```

The bundle stayed at 539.75 kB across the commit that added `marked`, which is the evidence that it
is a serve-time dependency and does not ship to the browser.

Route behaviour, by `curl` against the running dev server:

```
sample.{png,jpg,jpeg,gif,webp,ico}                 200 text/html; charset=utf-8   (wrapper)
sample.{png,jpg,jpeg,gif,webp,ico}?raw=1           200 image/{png,jpeg,jpeg,gif,webp,x-icon}
sample.png with Sec-Fetch-Dest: image              200 image/png
sample.png with Sec-Fetch-Dest: iframe             200 text/html; charset=utf-8
sample.png with Sec-Fetch-Dest: document           200 text/html; charset=utf-8
sample.png?v=7  (the viewer's cache-busting form)  200 text/html; charset=utf-8
HEAD sample.png                                    200
agentic-loop.svg                                   200 image/svg+xml   (unwrapped)
README.md                                          200 text/html; charset=utf-8
```

Browser assertions, driven by `demo-validator-web` and finished by hand:

- All six image types appear in the viewer's dropdown and display in the panel.
- The File Browser's "Open in HTML Viewer" is present and enabled on them, and opens them.
- Markdown renders formatted — real headings, a 7x5 table, 6 `<pre>` blocks, 164 inline `<code>`,
  12 lists, 2 links, and no raw `#`/`*` outside code. Body text 20px at roughly 15.7:1 contrast.
- `.md` files are selectable, including through the File Browser's built-in Documentation preset,
  which previously could not open any of its own files into the viewer.
- Image presentation after the wrapper: `sample.png` measures 580.2x361 inside a 781x361 viewport
  with equal margins and no scrollbars, against 900x560 natural size.
- REQ-006 R02 zero page scroll and REQ-007 W15 fill: 16 of 16 combinations — four window sizes
  (1280x720, 1366x768, 1920x1080, 1024x768) in both layouts, run once with an image displayed and
  once with a markdown file displayed. Every one measured `fillDelta 0` with no vertical or
  horizontal page scroll. Representative figures, Layout 1 with an image:

```
1280x720    iframe 196.41  tablist 36.19  regionBody 232.59  fillDelta 0
1366x768    iframe 219.52  tablist 36.19  regionBody 255.70  fillDelta 0
1920x1080   iframe 361.03  tablist 36.19  regionBody 397.22  fillDelta 0
```

## Acceptance

No phase, so no `acceptance` list. Judged against what the coordinator prompt asked for:

- Six image formats selectable and displaying — **Met**. Verified in a browser, and the File Browser
  context action widened from the shared constant with no second list, as predicted but confirmed
  rather than assumed.
- No backend or `vite.config.ts` change needed for the image formats — **Met**. Confirmed by `curl`
  before any code was written.
- Markdown rendered route-side per the `000119` ruling — **Met**. The render sits inside
  `serveRepositoryFiles`, after every boundary check, reading the already-validated realpath.
- `.htm` gap closed in the same pass, per the ruling's consequence 3 — **Met**.
- Zero page scroll and fill assertions still hold — **Met**, 16 of 16 combinations.
- Panel maximize kept out of this track — **Met**. Not built, not started, and `PLAN-028` design
  decision 5 was not overridden.

## Backlog

No backlog line was touched. No phase was claimed, no `status` changed, and `next_up` was not
pruned — none of those have a subject in an unclaimed session.

## Unresolved

- `REQ-007` W07 now understates what ships: it still reads "the compatible files (`.html` and
  `.svg`)" and its verification says to assert the dropdown lists "exactly" those. The owner ruled
  that `phase-prog-02` owns those requirement rows, so the divergence is deliberate and recorded
  rather than fixed here.
- The eight markdown fill combinations were measured on the wrapper code before the `Sec-Fetch-Dest`
  commit. That commit changes only sub-resource handling and not layout, but they were not re-run.
- Assertion E is browser-verified for the `docs/` SVG copy. The `_public/images/` copy is verified by
  HTTP and byte-identity only: Playwright cannot evaluate inside a `Content-Security-Policy: sandbox`
  top-level document, so a fresh render of that specific file was not obtainable.
- `_public/demo-image-check/` holds six untracked test fixtures generated for this verification. They
  are not demo content, they do not survive `git worktree remove`, and the script that made them is
  in the session transcript rather than the repository.
- Idea `000132` ("rotate images through the panel, not just text") overlaps the stepping request the
  owner put on hold; the two should not be built twice.
- The dev server started for this session at 20:45 is serving stale code. Vite restarted it onto an
  intermediate tree state during one of the rebases and did not pick the final config back up, so
  `README.md` now answers `application/octet-stream` and `sample.png` answers raw bytes on that
  process. The merged code on `dev` is correct; only that long-running process is wrong. A fresh
  launch reads the merged config, so tomorrow's demo is unaffected — but anyone re-running the
  `curl` checks against that process will get pre-feature answers.

## Review

An independent `demo-adversary` sub-agent reviewed `85ec053..5e59b8a` with no access to this
session's reasoning, ran the verification itself, and attacked the new route branches. Its findings,
as reported:

> All twelve conditions **HOLD**. No failures survived attack.
>
> 1. **HOLDS** — `RASTER_IMAGE_EXTENSIONS` in `ts/vite.config.ts` and `COMPATIBLE_EXTENSIONS` in
>    `ts/src/stage/HtmlViewerRegion.tsx:26-36` both list `.png .jpg .jpeg .gif .webp .ico`; the
>    viewer list is exported and consumed by the File Browser's context menu rather than duplicated.
> 2. **HOLDS** — `git diff 85ec053..5e59b8a -- src/` is empty; zero backend files touched.
> 3. **HOLDS** — markdown renders via `marked.parse` inside `serveRepositoryFiles`
>    (`ts/vite.config.ts:351-427`), not in `HtmlViewerRegion.tsx` and not in a new FastAPI route.
> 4. **HOLDS** — verified precisely by reading line order: 400 empty-path (185-189) → repo-root
>    containment 403 (190-195) → `.git` segment 403 (207-215) → existsSync/isFile 404 (216-221) →
>    `realpathSync` symlink-boundary 403 (233-238) → `git check-ignore` 404 (239-244) → headers set
>    (245-264) → image-wrap branch (265+) → markdown branch (351+). Both new branches read
>    `realResolved`, never `resolved`.
> 5. **HOLDS** — `.md` and `.htm` are both in `COMPATIBLE_EXTENSIONS`.
> 6. **HOLDS** — wrapper HTML centers/fits the image (`flex`+`object-fit:contain`) and its own
>    `<img src>` points at `?raw=1` on the same URL.
> 7. **HOLDS** — `Sec-Fetch-Dest: image` (any case) and `?raw=1` each return raw image bytes with
>    correct MIME; plain requests return the wrapper.
> 8. **HOLDS** — `Cache-Control: no-store` and `CSP: sandbox` are set once (lines 251, 264) before
>    any branching, so both the wrapper and the raw/sub-resource paths carry them.
> 9. **HOLDS** — `.svg`/`.html`/`.htm` are excluded from `RASTER_IMAGE_EXTENSIONS` and served
>    unchanged regardless of `Sec-Fetch-Dest`.
> 10. **HOLDS** — all 6 `_public/images/*.svg` are byte-identical to
>     `docs/07-architecture/diagrams/demo/*.svg` (`cmp -s`), and all 6 base64-embedded copies in
>     `_public/skills-and-agents-lexicon.html` decode to byte-identical content.
> 11. **HOLDS** — `marked` is in `ts/package.json` devDependencies only, imported solely by
>     `ts/vite.config.ts` (no hits under `ts/src/`), and does not appear anywhere in
>     `ts/dist/assets/*.js` after a real `npm run build`.
> 12. **HOLDS** — `git diff` in the range and `check_no_private_content.py` (622 files, 31
>     identifiers checked, OK) show no personal/machine identifier added to a tracked file.

Its attack results, as reported:

> - **Path traversal / `.git` / gitignored, × `?raw=1` × `Sec-Fetch-Dest: image`**: all combinations
>   blocked correctly. `/../../etc/passwd` (+`?raw=1`): 403. `/.git/config` (+`?raw=1`,
>   +`Sec-Fetch-Dest: image`): 403 in all three combinations. Gitignored PNG: 404 in all of plain /
>   `?raw=1` / `Sec-Fetch-Dest: image`. Encoded traversal (`%2e%2e/...`, `..%2f..%2f...`) and encoded
>   `.git` segments (`%2egit`, `.git%2fconfig`): all 403.
> - **Query-string parsing changing path resolution**: no. The path is still split off before decode
>   and `query` is only ever read via `query.has('raw')`, never fed into path resolution.
> - **Image bytes without the sandbox CSP header**: none found.
> - **Non-UTF-8 markdown**: does not crash; renders with replacement characters, 200 OK.
> - **Very large markdown (60MB)**: `marked.parse` throws `RangeError: Maximum call stack size
>   exceeded`, caught by the route's own `try/catch` (`ts/vite.config.ts:421-426`), returning a
>   graceful `500 Failed to render markdown: <path>` in ~150ms. Process stayed alive.
> - **Is `marked.parse` genuinely synchronous?** Yes as used: called with `{ async: false }`, no
>   extensions registered, throwing synchronously rather than rejecting a promise.

The reviewer also caught something this session had wrong. It reported that the dev server on 5180
predated the wrap and markdown commits and that curling it gave a stale read, so it tested the
merged code by loading `vite.config.ts` through Vite's own `loadConfigFromFile` and driving the real
middleware with mock request and response objects instead. That was initially disbelieved here,
because the same curls had returned the new behaviour earlier in the session — and re-running them
confirmed the reviewer, not this session. See the last entry under `## Unresolved`.

## Decisions

**Markdown shipped with `marked`, over a recommendation to cut it.** The `000119` ruling fixed where
rendering goes but explicitly left the library to phases `phase-prog-02` has not created yet. The
recommendation here was to skip markdown and spend the clock on smaller items, because adding a
dependency means `ts/node_modules/` on the presentation machine no longer satisfies
`ts/vite.config.ts`, and the failure mode is a frontend that does not start at all rather than one
that degrades. The owner accepted that risk and chose to ship it. The mitigation is documentation:
`npm install` is now a stated prerequisite in both demo documents.

**Image presentation was fixed rather than deferred.** The coordinator prompt left the bare-image
question open and said to ask only if it looked wrong projected. It looked wrong: measured top-left
anchoring at natural size, with roughly 47% of a 900x560 image's height visible in the panel and its
label below the fold. The owner chose to wrap route-side in the same pass as the markdown work.

**`REQ-007` W07 was left stale deliberately.** The code now ships eight compatible types while W07
still says two and its verification says to assert "exactly" those. Amending a governed requirement
inside an unclaimed session, for rows the `000119` ruling assigns to `phase-prog-02`, is the
document-manufacturing `AGENTS.md` warns against. The owner ruled it stays.

**Panel maximize was not built.** `000233` was ruled into P10 as `phase-arch-17` and `PLAN-028`
design decision 5 records the cost. It was not started, not approximated, and the ruling was not
overridden.

**The canonical-copy question was settled by the owner and acted on.** The SVG files are canonical;
the base64 copies embedded in the lexicon page are not. Three had drifted and were the older art —
`command-skill-tool` missing its `HERE` caption and the `/backlog` and `/idea` lines,
`skill-architecture` missing the `orient`, `checkpoint` and `log-anti-patterns` entries. They were
re-embedded from the canonical files rather than left, because that page would otherwise have
described a smaller set of commands and skills than the repository ships.

**A peer's uncommitted idea events were committed before integrating, at the owner's direction.**
Ideas `000232`-`000235` existed only in the primary checkout's working tree. `000232` is cited
throughout this branch and `000235` records the prompt pack that produced the session, so that
provenance was one `git checkout` away from being lost.

## Corrections

**An idea capture took a live id and was reverted.** Recording the owner's file-stepping request
through `tools/append_idea.py` from the worktree produced `000232` — already in use for the image
formats idea this session was built on — because the worktree branched from `dev` and could not see
the four ideas sitting uncommitted in the primary checkout. The append was reverted rather than
renumbered by guesswork, and the request was left uncaptured rather than written under an id that
might collide again. The underlying cause is now gone: those events are committed.

**The stale dev server was disbelieved before it was checked.** The reviewer's claim that the running
server predated the feature commits was treated as probably wrong, because the same curls had
returned the new behaviour earlier. Re-running them showed the reviewer was right. The earlier
results were genuine when taken; the server drifted afterwards. Recorded because the reflex — trusting
one's own earlier observation over a second agent's contradicting one — is what would repeat.

**Committing the idea events left the tree red.** `docs/00-working/ideas.md` is generated from the
idea log, and the commit did not regenerate it, so
`test_the_committed_markdown_matches_regenerated_output` failed on the post-rebase run. Caught by
that run, which is exactly the run `AGENTS.md` positions as the one that decides integration, and
fixed by amending the commit to carry its own generated output.

## Left undone

**`000109`, double-click a tab to open the file in a new browser tab.** Cut on the coordinator's own
authority. It is roughly fifteen lines in a file the session had already touched three times, and the
route-side ruling had made it more valuable rather than less — a new tab now gets the same fitted
image and rendered markdown the panel does. It was cut because adding a fifth code change at 22:30
would have reopened a verification surface that was complete and green, not because it is hard.

**`000102`, the freshness badge.** Cut as the bottom rung of the descope ladder. It came from a
rehearsal dry-run rather than a real need and partly duplicates the refresh control already in the
header.

**The file-stepping request the owner raised mid-session.** Put on hold by the owner, and not
captured as an idea because of the id collision described under `## Corrections`. It needs recording
now that `000232`-`000235` are committed, and it overlaps `000132`.

**Re-running the eight markdown fill combinations.** They were measured before the `Sec-Fetch-Dest`
commit. That commit changes sub-resource handling only, not layout, so the risk is low — but "low"
is not "measured".

