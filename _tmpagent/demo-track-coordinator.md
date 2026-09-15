# Track A — demo-mandatory work, night of 2026-09-14

Coordinator prompt. The demo is **2026-09-15**. This track exists to put working, visible changes in
front of an audience tomorrow. Nothing here is architecture work.

`AGENTS.md` governs everything below. Where this prompt and `AGENTS.md` differ, `AGENTS.md` wins.

## Read this before dispatching anything

**Do not fan this work out across parallel agents.** That is the instruction, and it is the opposite
of what a coordinator prompt usually says, so here is the reason.

Every candidate change tonight lands in the same file — `ts/src/stage/HtmlViewerRegion.tsx` — or in
its immediate neighbours under `ts/src/stage/`. Four agents editing one 200-line component produce
four branches that all conflict, and the merge cost lands at the worst possible hour. The
parallelism is nominal; the conflicts are real.

**Run Track A as one implementation session, sequential commits, one branch.** The coordinator's
job here is sequencing and verification, not fan-out.

Where a second agent genuinely helps is on a *different surface*, and there are exactly two:

- **Browser verification** — `demo-validator-web` driving Playwright against the running workbench
  while the implementation session works. Different surface, no file contention, and it catches the
  zero-scroll and fill regressions that only show in a real browser.
- **Runbook and setup docs** — `docs/00-working/demo-runbook.md` and
  `docs/00-working/demo-windows-setup.md` both still name `http://localhost:8000` as the dev-proxy
  fallback, which went stale when the proxy default moved to `127.0.0.1` in commit `e1ab509`.
  Independent of every code change below.

So: **one implementation agent, one validator agent, optionally one docs agent. Three at most, and
only one of them touching `ts/`.**

## There are no backlog phases for this work

`P11` is not planned yet. Its finalize phase (`phase-prog-02`) is blocked behind `phase-prog-03`,
which is active and unmerged. So none of tonight's work has a phase to claim.

That is explicitly provided for. `AGENTS.md`, *Concurrent agents: claim a phase*:

> **Owner-directed work with no backlog phase** — a one-off document, a fix asked for directly — has
> nothing to claim. Skip the claim commit, name the branch and worktree after the work
> (`agent/<slug>`), and say plainly in your first report that the session is running unclaimed and
> peers therefore hold no lock against it.

**Do not manufacture a backlog phase to have something to claim.** Use `agent/demo-viewer-tonight`
as the branch and `../d-system-worktrees/demo-viewer-tonight` as the worktree, and state in the
first report that the session is unclaimed.

Because there is no lock, disjointness is the coordinator's responsibility rather than the
validator's. That is the second reason not to fan out.

## The work, in dispatch order

Ordered by ratio of demo value to risk. Stop when time runs out; each item is independently
shippable and leaves the tree green.

### 1. `000232` — the six already-served image formats

**Highest value per minute of anything available tonight.** Ship this first.

`ts/src/stage/HtmlViewerRegion.tsx:18` declares `COMPATIBLE_EXTENSIONS = ['.html', '.svg']`. Add
`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.ico`.

Facts already established — do not spend the session rediscovering them:

- `CONTENT_TYPE_BY_EXTENSION` in `ts/vite.config.ts` already maps all six to correct image MIME
  types, so `serveRepositoryFiles` serves the bytes correctly **today**. No backend change is
  needed.
- `GET /api/v1/workbench/search` in `src/api/routes/workbench.py` is extension-agnostic and filters
  on whatever `ext` values it is handed. The two-type limit is entirely a frontend decision.
- `FileBrowserRegion.tsx:4` imports that same constant rather than keeping its own copy, so the
  File Browser's "Open in HTML Viewer" context action widens **for free**. Verify that it did; do
  not assume it.
- This idea does **not** inherit `000118`'s dependency on markdown rendering. `000118` defers
  widening the list until rendering lands because `.md` without a render step shows raw source. That
  reasoning does not apply to image types that are already correctly served. Ship it independently.

One open question the owner flagged and nobody has answered: whether the iframe's bare-image
presentation is acceptable (browser default centering, background, zoom) or whether an image needs
wrapping in a minimal HTML document for consistent presentation. **The answer must be the same for
all six.** Try it first, look at it, and ask the owner only if it looks wrong on a projector — this
is a question a screenshot settles faster than a discussion.

Note the sandbox: the viewer iframe carries `sandbox=""` and served files carry
`Content-Security-Policy: sandbox`. Images are fine under both. Any change that assumes scripts run
inside the viewer is wrong.

### 2. Markdown rendering — only if the ruling is in hand

`000110`, and `000119` decides where rendering happens. The ruling is at
`_tmpagent/viewer-render-location-ruling.md`, `activated` on 2026-09-14 by `agent-viewer`.

**Claim it before reading it**, per `_tmpagent/AGENTS.md`: append a `claimed` line with `kind:
branch`, `ref: agent/demo-viewer-tonight`, an RFC 3339 timestamp with offset, your agent id, and the
branch you wrote it from. **Release it before the session ends.** No check enforces that, which is
exactly why it has to be deliberate.

Treat the ruling as settled input, not a proposal to re-litigate.

This is materially bigger than item 1 — it is a rendering step, not an array entry. If it will not
land cleanly, **stop and ship item 1 alone**. A half-rendered markdown view on a projector is worse
than no markdown view.

### 3. `000109` — double-click opens a file in a new browser tab

Small, self-contained, and demos well because it is visible in one gesture. Lands in the same file
as item 1, which is why it runs after it rather than beside it.

### 4. `000102` — freshness badge

Lowest priority of the four. Cut it first if time is short.

## What is explicitly NOT in this track

**Panel maximize (`000233`) is not here, and must not be added.** The owner asked for it for exactly
this demo — reading a generated page from the back of a room — and it was ruled into `P10`'s `G43`
as `phase-arch-17`, at the end of a six-deep critical path. It cannot exist by tomorrow.

The ruling and its cost are stated in `PLAN-028` design decision 5. The faster route — a viewer-only
maximize — was rejected on purpose because `G43` would throw it away. **If the owner decides tonight
that the demo needs it more than the architecture does, that is their call to make against that
trade-off, and it changes the ruling rather than bypassing it.** Do not quietly build a viewer-only
maximize because the demo is close.

If the owner does overrule: say plainly in the session record that `PLAN-028` decision 5 was
overridden by the owner on the night of 2026-09-14, and that `phase-arch-17` now has a throwaway
predecessor to delete rather than a clean field.

## Verification — run it in a browser, not only in a test

```bash
uv run pytest
cd ts && npm run build
uv run python -m src.governance
```

Then the part that actually matters for a demo. Dispatch `demo-validator-web` against the running
workbench and confirm, in a real browser:

- Each of the six image types opens in the viewer and displays.
- The File Browser's "Open in HTML Viewer" appears for them.
- `REQ-006` R02 zero page scroll and `REQ-007` W15's fill assertions still hold at 1280x720,
  1366x768, 1920x1080 and 1024x768, **in both layouts**. This is the regression most likely to
  arrive with a new content type and least likely to show up in `pytest`.

A failing check is a result to record, not a step to retry until quiet. If the fill assertions break
at one window size, report the size and the measurement rather than a summary.

## Agent hygiene and spend — binding

These are the repository's standing conventions, not new rules for tonight. `GOV-008`'s *Cost
protocols* and [PROMPT-016](../docs/02-prompts/PROMPT-016-demo-guardrails.md) are the sources; they
bind the coordinator and every agent it dispatches.

**Models.** Haiku for mechanical gates — the governance check, the staged private-content check,
front-matter audits. **Sonnet is the standard for judgment work**, which is every implementation and
validation dispatch tonight. **Opus is never pre-assigned.** It is available as at most **one
documented escalation** for the whole track, only after two failed sonnet attempts with validator
findings attached, and it must be reported. There is no second escalation — the second failure of
that kind goes to the owner.

**Loop caps.** At most **two** creator→validator fix cycles per work item. Then the coordinator
judges and reports up. **A third quiet retry is forbidden.** Two items exhausting their caps is a
stop-and-report signal for the whole track, not a reason to push on.

**Truncation: resume, never re-run.** If a dispatched agent's output is cut off by its turn limit,
resume that same agent with `SendMessage`. Re-running from scratch pays for the whole context twice
and is the single most expensive mistake available here (idea `000077`).

**Validator blindness.** A validator receives the diff, the requirement and the commands —
**never the creator's rationale**. A validator told why the code is right will confirm that it is.

**Dispatch discipline.** One work item per dispatch. Do not spawn an agent to answer something a
`grep` settles, and do not spawn a second agent to check the first one's reading of a file. Every
spawn starts cold and re-derives context this coordinator already holds; on this track that cost is
rarely worth paying, which is the same reason Track A runs one implementation agent rather than four.

**Ports.** Pick free ports explicitly — `uv run uvicorn src.main:app --reload --port 8010`, Vite on
5180. **Never assume 8000 or 5173**; peers are running. Note that `VITE_API_TARGET` now defaults to
`http://127.0.0.1:8000`, not `localhost` (commit `e1ab509`).

**Worktree hygiene.** Each worktree gets its own `.venv`, `data/` and `ts/node_modules/` — install
them, never symlink a peer's. `uv sync --extra dev`, or the governance check fails for the wrong
reason on a missing `jsonschema`. **Gitignored content never travels**: a merge does not carry it and
`git worktree remove` destroys it, so copy anything that must survive out by hand first.

**Git.** Never `--force` push and never rewrite pushed history. Pushing `agent/*` is free;
integration into `dev` is owner-approved. Run `tools/check_no_private_content.py` **with changes
staged** — it reads `git ls-files`, so an unstaged run passes by not looking.

**Release every `_tmpagent/` claim** this track opens, including the one on the render-location
ruling if item 2 runs. No check enforces it.

**When to ask.** Use `AskUserQuestion` only when the answer changes what gets built and this prompt
does not already answer it — a merge approval, overruling the `000233` ruling, the bare-image
presentation question if it looks wrong on a projector. Everything else: state the assumption, keep
working, surface it at close-out. An agent that asks about everything moves the load back onto the
person it exists to unload.

**Descope ladder.** Items 1–4 are already ordered by value. When behind, cut from the bottom — `4`,
then `3`, then `2` — **on your own authority**, and report the cut rather than negotiating it. Item
1 survives every rung; if item 1 cannot land, that is a stop-and-report, not a descope.

## Close-out report

Report per `GOV-006`: name things, then cite them. Lead with what shipped, in one line each.

Then the **spend posture**, which is not optional:

- dispatches run, and how many were resumed after truncation
- whether any model was escalated above sonnet (it should be zero; one is permitted and must be
  justified)
- fix cycles consumed per work item, against the cap of two
- wall-clock against the runway, and which descope rungs were taken

Then the real verification output — the failures in full, the walls of passing checks summarised.
A summary of a failure is not a result; the failure is the result.

## Hand-off

Push `agent/demo-viewer-tonight` freely — backing up your own branch needs no approval. **Ask the
owner before merging into `dev`.** Given the hour, expect to hand over a green unmerged branch and
name the command that shows it: `git diff dev..agent/demo-viewer-tonight`.

Do not mark anything complete. There is no phase to complete, and `/session-close` is the owner's.
