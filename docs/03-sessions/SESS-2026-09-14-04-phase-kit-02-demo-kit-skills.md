---
schema_version: 1
id: doc-session-phase-kit-02
code: SESS-2026-09-14-04
title: 'phase-kit-02: build the consultant demo kit''s six skills'
kind: session
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-demo-kit]
depends_on: [doc-consultant-demo-kit, doc-consultant-demo-kit-requirements]
---

# phase-kit-02: build the consultant demo kit's six skills

Agent `agent-kit`, branch `agent/phase-kit-02`, worktree
`../d-system-worktrees/phase-kit-02`. The phase is left `active`; marking it complete and
integrating into `dev` are the owner's.

## What was built

Six skills under `.claude/skills/`, all `demo-skill-` prefixed, built in the order the phase
requires — the elicitation engine first, because three of the others call it.

| Skill | What it does |
|---|---|
| `demo-skill-ask-me` | The elicitation engine. Interviews before answering; the only component that gathers input |
| `demo-skill-flowchart` | Draws a described process, marking gaps rather than filling them |
| `demo-skill-brainstorm` | Diverges then converges, announcing which phase it is in |
| `demo-skill-meeting-notes` | Structures raw notes; never invents an owner or a date |
| `demo-skill-scorecard` | Weighted comparison with weights stated before scores |
| `demo-skill-make-it-a-skill` | Drafts a reusable skill from a manual sequence; writes nothing |

## Decisions taken with the owner before work started

Four questions were asked during orientation and answered before the claim.

1. **Claim as `agent-kit`.** Conflicts column was `—`; active claims were 2 of 3.
2. **Repository publish target: `_public/demo-kit/`.** `REQ-008` K17 requires a publish into the
   HTML Viewer but names no path. `_public/` is the precedent (`_public/overview/index.html`) and
   the repository's declared shareable-outputs directory.
3. **Standalone output: a directory the person names, defaulting to `~/demo-kit-output/`.** Never
   the current directory, so running a skill inside a repository cannot drop a file into a working
   tree.
4. **The stale phase title was corrected in the claim commit** — it read "two self-announcing
   skills" where its own scope, `PLAN-024`'s build order and `REQ-008` all say six.

## The publish-path constraint, verified rather than assumed

A gitignored location cannot be published into the HTML Viewer. `ts/vite.config.ts`'s
`serveRepositoryFiles` returns 404 for any path `git check-ignore` flags, and
`src/api/routes/workbench.py` applies the same rule to its listing routes (ADR-015 rule 3). So
`_working/` and `_capture/` were never candidates; the target had to be tracked.

Confirmed for the chosen path:

```
$ git check-ignore -v _public/demo-kit/reporting-tool-scorecard.html
NOT ignored -> viewer serves it (exit 1 = no match)
```

This also resolves the apparent conflict between "no skill writes a repository file" and K17's
required publish. `REQ-008` K03 is the governing wording: a component writes only to its stated
output location, and nothing writes into `docs/`, `.claude/`, `_data/` or any governed path.
`_public/demo-kit/` is none of those. Both file-emitting skills state the prohibition explicitly.

No file was added under `_public/` by this phase. The directory is created by the skill at run
time, keeping the change inside the phase's declared deliverable, `.claude/skills/`.

## Verification

**Governance and tests, in the worktree:**

```
Governance OK: 20 systems, 196 documents, 22 memories, 136 backlog phases
governance exit=0
580 passed, 2 warnings in 35.66s
```

No collision with the three skills generated from `agent-workflows/` (`checkpoint`,
`log-anti-patterns`, `orient`) or with `d-system-overview`; the generator's enforcing tests pass
unchanged.

**Structural check against the requirements**, run over all six files:

```
demo-skill-ask-me       name==dir:True  must-not-fire:True  self-announces:True  calls-ask-me:False
demo-skill-brainstorm   name==dir:True  must-not-fire:True  self-announces:True  calls-ask-me:True
demo-skill-flowchart    name==dir:True  must-not-fire:True  self-announces:True  calls-ask-me:True
demo-skill-make-it-a-skill name==dir:True must-not-fire:True self-announces:True calls-ask-me:False
demo-skill-meeting-notes name==dir:True must-not-fire:True  self-announces:True  calls-ask-me:False
demo-skill-scorecard    name==dir:True  must-not-fire:True  self-announces:True  calls-ask-me:True
```

K18 holds exactly: the three skills required to call `demo-skill-ask-me` do, and the other three do
not. K13 holds — the only occurrence of `argument-hint` anywhere in the six files is prose in
`ask-me`'s body explaining why there is none; its frontmatter carries `name` and `description` only.

**K17, the standalone half.** Two outputs were produced into `~/demo-kit-output/` — outside this
repository — and rendered in a real browser from a `file://` URL with no server and no network,
which is the "double-click it" case the requirement actually claims:

```
$ google-chrome --headless --screenshot ... file:///home/mimmik/demo-kit-output/invoice-approval-flowchart.html
77534 bytes written to file invoice-approval-flowchart.png
$ ... file:///home/mimmik/demo-kit-output/reporting-tool-scorecard.html
158739 bytes written to file scorecard-fixed.png
```

Both screenshots were read back and render correctly. Neither file contains a single `src=`,
`href=`, `@import`, URL or `<script>` tag — grepped and confirmed — so "self-contained" is a
verified property, not an intention. The flowchart is inline SVG, deliberately not a diagram
library, because any library would need the network the requirement says will not be there.

The Playwright MCP server could not be used for this: it blocks the `file:` protocol. Serving the
directory over HTTP would have verified a weaker claim than the requirement makes, so
`google-chrome --headless` against the file URL was used instead.

## A defect found by running the thing, and fixed in the skill

The scorecard produced during verification reported Option B winning with a weighted total of
**4.10** against scores that summed to **4.00**, and the sensitivity paragraph beneath it reasoned
from the wrong figure. Every total and every reweighting claim was then recomputed:

```
agreed weights:            A 4.0   B 4.1   C 3.1
cost 40 / time 30:         A 4.1   B 3.9   C 3.3
B cost 3->2, agreed:       B 3.8
stability weight to 0:     A 4.1   B 4.2   C 2.8
```

The score was corrected so the page's arithmetic is true, and each of the page's four claims about
sensitivity now checks out against those figures.

The more useful outcome is that `demo-skill-scorecard` gained a **"Check the arithmetic before
reporting it"** section requiring every weighted total and every sensitivity claim to be recomputed
before it is reported, and citing this occurrence. A component whose entire value is that its
conclusion is traceable to its weights fails completely when the total does not equal its own
scores.

## Not verified in this session

- **K02's skill-listing check.** Confirming each skill appears in the skill listing requires a
  session started with the kit present; this session's listing was captured before the files
  existed. What was verified mechanically: each file's frontmatter parses as YAML, carries `name`
  and `description`, and its `name` equals its directory name. `REQ-008` records testing and
  demonstration as the owner's.
- **The content half of `tools/check_no_private_content.py`.** It reported
  `_private/portfolio/ not found — content check skipped (path check still ran)`, because
  `_private/` is gitignored and therefore never reaches a worktree. The path check passed over 561
  tracked files. The content check needs a run on `dev`, where `_private/` exists.

## One judgement call worth recording

`demo-skill-make-it-a-skill` contains the phrase `"the quarter" became a date range` as an
illustration of a specific becoming a parameter. It is a quoted example of the generalisation
mechanic, not a subject the skill operates on, and the skill runs unchanged against anything —
so K15 holds. Recorded because a reader scanning for timeline references will hit it.

## State at hand-off

- Branch `agent/phase-kit-02`, two commits: the claim on `dev`, and the six skills.
- Governance exits 0 and 580 tests pass in the worktree; the tree is clean.
- No `_tmpagent/` claim was opened this session, so none needs releasing.
- The phase remains `active`. Marking it complete is `/session-close`'s, and integrating into `dev`
  is the owner's: `git diff dev..agent/phase-kit-02`.
