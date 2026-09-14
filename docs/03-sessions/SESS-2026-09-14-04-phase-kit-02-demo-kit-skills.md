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

## Phase

`phase-kit-02` — Build the kit's six self-announcing skills.

## Verification

Every entry in this phase's `verification` list is a behavioural check rather than a runnable
command, so each is recorded as what was actually done and observed. The repository-wide gates were
run as well and are recorded beneath them.

**"Read each SKILL.md against REQ-008 K05, K06, K13, K15, K16, K17 and K18."** All six files were
read and then checked mechanically. Output of that check:

```
demo-skill-ask-me           name==dir:True  must-not-fire:True  self-announces:True  calls-ask-me:False
demo-skill-brainstorm       name==dir:True  must-not-fire:True  self-announces:True  calls-ask-me:True
demo-skill-flowchart        name==dir:True  must-not-fire:True  self-announces:True  calls-ask-me:True
demo-skill-make-it-a-skill  name==dir:True  must-not-fire:True  self-announces:True  calls-ask-me:False
demo-skill-meeting-notes    name==dir:True  must-not-fire:True  self-announces:True  calls-ask-me:False
demo-skill-scorecard        name==dir:True  must-not-fire:True  self-announces:True  calls-ask-me:True
```

K16: all six directories carry the `demo-skill-` prefix. K13: the only occurrence of
`argument-hint` in the six files is prose in `ask-me`'s body explaining why there is none; its
frontmatter carries `name` and `description` only. K15: a scan for industry, role, company,
headcount and timeline terms returned two hits, both benign — one is a prohibition in
`flowchart`'s own body, the other a quoted illustration in `make-it-a-skill` (recorded under
Unresolved). K03/K17 write targets: the only governed paths named anywhere in the six files are the
two "never write here" prohibitions.

**"Open a standalone HTML output from outside the repository and confirm it renders."** Two outputs
were produced into `~/demo-kit-output/`, outside this repository, and rendered with a real browser
from a `file://` URL with no server and no network — the "double-click it" case the requirement
actually claims:

```
$ google-chrome --headless --screenshot ... file:///home/mimmik/demo-kit-output/invoice-approval-flowchart.html
77534 bytes written to file invoice-approval-flowchart.png
$ google-chrome --headless --screenshot ... file:///home/mimmik/demo-kit-output/reporting-tool-scorecard.html
158739 bytes written to file scorecard-fixed.png
```

Both screenshots were read back and render correctly — the flowchart as inline SVG with its gap
nodes, the scorecard as a weighted table. Grepping both files for `src=`, `href=`, `@import`, any
URL and `<script>` returned nothing, so "self-contained" is verified rather than intended.

The Playwright MCP server could not be used: it blocks the `file:` protocol. Serving the directory
over HTTP would have verified a weaker claim than the requirement makes.

**"Confirm each skill appears in the skill listing."** Not observed — see Unresolved. What was
verified: each file's frontmatter parses as YAML, carries `name` and `description`, and its `name`
equals its directory name.

**Repository gates, in the worktree:**

```
$ uv run python -m src.governance
Governance OK: 20 systems, 197 documents, 22 memories, 136 backlog phases
exit=0

$ uv run pytest -q
580 passed, 2 warnings
```

No collision with the three skills generated from `agent-workflows/` (`checkpoint`,
`log-anti-patterns`, `orient`) or with `d-system-overview`.

```
$ uv run python tools/check_no_private_content.py
note: _private/portfolio/ not found — content check skipped (path check still ran)
check_no_private_content: OK (562 tracked files, 0 identifiers checked)
```

## Acceptance

- **Each skill names itself in its first output line when it fires** — Met at definition, firing not
  observed. Every file carries an explicit "First line of every run, before anything else" block
  naming the skill; the `self-announces:True` column above confirms it mechanically. Observing an
  actual firing needs a fresh session (see Unresolved).
- **Each skill's description states both its firing phrasings and its non-firing cases** — Met. Each
  description names concrete input phrasings and carries an explicit "Must not fire" clause; the
  `must-not-fire:True` column confirms the second half across all six.
- **`demo-skill-ask-me` documents its parameters in a table and carries no `argument-hint`** — Met. A
  three-row table covers question count, selection mode and recommendations, with recommendations
  defaulting to include; frontmatter has no `argument-hint`.
- **brainstorm, scorecard and flowchart call ask-me rather than implementing their own questioning**
  — Met. The `calls-ask-me` column is true for exactly those three and false for the other three;
  none of the three contains an elicitation sequence of its own.
- **meeting-notes never invents an owner or a date** — Met at definition, firing not observed. The
  rule is stated as the skill's central section with `missing` as the required output for both
  fields and an explicit prohibition on deriving either.
- **The standalone HTML outputs render from a directory outside this repository** — Met. Both
  rendered from `~/demo-kit-output/` over `file://` with no server; screenshots read back and
  confirmed.

## Backlog

- `status: active` — unchanged. Marking the phase complete belongs to `/session-close`.
- `session: doc-session-2026-09-14-01-phase-kit-02`
- `completion_evidence:` the six `SKILL.md` files under `.claude/skills/demo-skill-*/` and this
  record.
- `result:` Six skills built, `demo-skill-ask-me` first. Governance exits 0 and 580 tests pass in
  the worktree. Five of six acceptance conditions verified outright; two of those five rest on
  definitions whose firing was not observed this session.
- `next_action:` Fire each of the six skills in a fresh session to observe the self-announcing first
  line, the meeting-notes missing-field behaviour and the skill listing, then run
  `tools/check_no_private_content.py` on `dev` where `_private/` exists.
- `next_up` was not pruned: no phase completed this session.

## Unresolved

- **The skill-listing check (K02) was not observed.** It needs a session started with the kit
  present; this session's listing was captured before the files existed. `REQ-008` records testing
  and demonstration as the owner's.
- **The content half of `tools/check_no_private_content.py` did not run.** `_private/` is gitignored
  and so never reaches a worktree; the tool reported the skip itself. The path check passed over 562
  tracked files. The content check needs a run on `dev`.
- **One judgement call on K15.** `demo-skill-make-it-a-skill` contains the phrase `"the quarter"
  became a date range` as an illustration of a specific becoming a parameter. It is a quoted example
  of the generalisation mechanic, not a subject the skill operates on, and the skill runs unchanged
  against anything — so K15 holds. Recorded because a reader scanning for timeline references will
  hit it.

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
`src/api/routes/workbench.py` applies the same rule to its listing routes (`ADR-015` rule 3). So
`_working/` and `_capture/` were never candidates; the target had to be tracked. Confirmed for the
chosen path:

```
$ git check-ignore -v _public/demo-kit/reporting-tool-scorecard.html
(exit 1 — no match; the viewer serves it)
```

This also resolves the apparent conflict between "no skill writes a repository file" and K17's
required publish. `REQ-008` K03 is the governing wording: a component writes only to its stated
output location, and nothing writes into `docs/`, `.claude/`, `_data/` or any governed path.
`_public/demo-kit/` is none of those, and both file-emitting skills state the prohibition
explicitly.

No file was added under `_public/` by this phase. The directory is created by the skill at run time,
keeping the change inside the phase's declared deliverable, `.claude/skills/`.

## A defect found by running the thing, and fixed in the skill

The scorecard produced during verification reported Option B winning with a weighted total of
**4.10** against scores summing to **4.00**, and the sensitivity paragraph beneath it reasoned from
the wrong figure. Every total and every reweighting claim was then recomputed:

```
agreed weights:            A 4.0   B 4.1   C 3.1
cost 40 / time 30:         A 4.1   B 3.9   C 3.3
B cost 3->2, agreed:       B 3.8
stability weight to 0:     A 4.1   B 4.2   C 2.8
```

The score was corrected so the page's arithmetic is true, and each of its four sensitivity claims
now checks out against those figures.

The more useful outcome is that `demo-skill-scorecard` gained a **"Check the arithmetic before
reporting it"** section requiring every weighted total and every sensitivity claim to be recomputed
before it is reported, and citing this occurrence. A component whose entire value is that its
conclusion is traceable to its weights fails completely when the total does not equal its own
scores.

## What was built

| Skill | What it does |
|---|---|
| `demo-skill-ask-me` | The elicitation engine. Interviews before answering; the only component that gathers input |
| `demo-skill-flowchart` | Draws a described process, marking gaps rather than filling them |
| `demo-skill-brainstorm` | Diverges then converges, announcing which phase it is in |
| `demo-skill-meeting-notes` | Structures raw notes; never invents an owner or a date |
| `demo-skill-scorecard` | Weighted comparison with weights stated before scores |
| `demo-skill-make-it-a-skill` | Drafts a reusable skill from a manual sequence; writes nothing |

Agent `agent-kit`, branch `agent/phase-kit-02`, worktree `../d-system-worktrees/phase-kit-02`. No
`_tmpagent/` claim was opened this session, so none needs releasing. The phase remains `active`;
integrating into `dev` is the owner's: `git diff dev..agent/phase-kit-02`.
