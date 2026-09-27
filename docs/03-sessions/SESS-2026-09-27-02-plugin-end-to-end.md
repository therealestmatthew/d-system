---
schema_version: 1
id: doc-session-plugin-end-to-end
code: SESS-2026-09-27-02
title: The idea-realization plugin exercised end to end in a scratch repository
kind: session
status: active
owner: repository-owner
created: '2026-09-27'
updated: '2026-09-27'
systems: [sys-plugin-core]
depends_on: [doc-idea-realization-plugin-end-to-end]
---

# The idea-realization plugin exercised end to end in a scratch repository

## Phase

`phase-plug-08` — End-to-end exercise in a scratch repository, install documentation, and
handover. The last phase of the idea-realization plugin build (`PLAN-048`, `REQ-031` R22).

## The scratch repository

An empty repository named `orchard`, created outside this repository and its worktrees, with one
commit on `main`, and a worktree of it on branch `exercise`. Every skill ran from that worktree,
so the partition sweep's primary-checkout staging path differed from the working directory.

`<scratch>` below stands for
`/tmp/claude-1000/-code-d-system/c16ba2d9-993e-4aee-b419-56e598993f6b/scratchpad/e2e`.

```
$ git init -q -b main orchard && ... && git commit -q -m "Initial commit"
$ git worktree add -q -b exercise ../orchard-worktrees/exercise main
$ git worktree list
<scratch>/orchard                     577c607 [main]
<scratch>/orchard-worktrees/exercise  577c607 [exercise]
```

Each step ran as a headless Claude Code session in `<scratch>/orchard-worktrees/exercise`:

```
claude -p --plugin-dir /code/d-system-worktrees/phase-plug-08/plugins/idea-realization \
  --allowedTools "Bash Read Grep Glob Write Edit Agent" --output-format stream-json --verbose \
  "/idea-realization:<skill> ..."
```

The plugin was loaded from this phase's worktree rather than the primary checkout, so the fix
below was exercised by the steps after it; at the start the two trees were identical. Where a
skill stopped for a person's answer (a consent, a claim, a partition gate), I answered as the
scratch repository's person by resuming that session with `--resume`. The quoted output below is
each command's tool result as the nested session received it.

## The exercise

### 1. Prerequisites

```
$ python3 ".../scripts/prerequisites.py" --feature all; echo "exit=$?"
ok       python  3.13
ok       uv      /home/mimmik/.local/bin/uv
ok       git     /usr/bin/git
ok       claude  /usr/bin/claude
exit=0
```

### 2. Scaffold, all features

The dry run, then the scaffold. The files the scaffold created:

```
$ uv run ".../scripts/scaffold.py" --feature all
created  ideas/ideas.jsonl
created  ideas/ideas.md
created  ideas/priority.yaml
created  .idea-realization/schemas/idea.schema.json
created  .idea-realization/schemas/idea-priority.schema.json
created  .idea-realization/staging/
created  .idea-realization/schemas/idea-partition-record.schema.json
created  backlog/backlog.yaml
created  .idea-realization/schemas/backlog.schema.json
created  docs/
created  docs/codes.yaml
created  docs/systems.yaml
created  .idea-realization/schemas/document.schema.json
created  .idea-realization/schemas/codes.schema.json
created  .idea-realization/schemas/systems.schema.json
needs consent  .gitignore: add /.idea-realization/staging/ (re-run with --consent gitignore)
recorded .idea-realization/install-state.json
```

On the person's yes to the `.gitignore` line:

```
$ uv run ".../scripts/scaffold.py" --feature all --consent gitignore
skipped  ideas/ideas.jsonl (exists)
... (the 15 paths above, each skipped (exists))
changed  .gitignore: added /.idea-realization/staging/ (consent recorded)
recorded .idea-realization/install-state.json
```

Committed as `a076f1c` (15 files: the 13 files above, `.gitignore` and the install-state record).

### 3. Doctor

```
$ uv run ".../scripts/doctor.py"; echo "exit=$?"
unchanged ideas/ideas.jsonl  (ideas)
unchanged ideas/ideas.md  (ideas)
unchanged ideas/priority.yaml  (ideas)
unchanged .idea-realization/schemas/idea.schema.json  (ideas)
unchanged .idea-realization/schemas/idea-priority.schema.json  (ideas)
unchanged .idea-realization/schemas/idea-partition-record.schema.json  (partition)
unchanged backlog/backlog.yaml  (backlog)
unchanged .idea-realization/schemas/backlog.schema.json  (backlog)
unchanged docs/codes.yaml  (documents)
unchanged docs/systems.yaml  (documents)
unchanged .idea-realization/schemas/document.schema.json  (documents)
unchanged .idea-realization/schemas/codes.schema.json  (documents)
unchanged .idea-realization/schemas/systems.schema.json  (documents)
unchanged .idea-realization/staging/  (partition)
unchanged docs/  (documents)
unchanged .gitignore  (consent: gitignore)
16 recorded, 0 drifted or missing
exit=0
```

### 4. Record, fold and render ideas

Four ideas about an orchard app, recorded with the idea skill, each from a file:

```
$ uv run ".../scripts/idea.py" add --file .../idea-$n.md   # n = 1..4
created 000001 at 2026-09-27T06:34:09-04:00 eid e18d92709ce6cc25e
created 000002 at 2026-09-27T06:34:10-04:00 eid e18d92709d484b944
created 000003 at 2026-09-27T06:34:10-04:00 eid e18d92709da9e6ded
created 000004 at 2026-09-27T06:34:10-04:00 eid e18d92709e0868131
$ uv run ".../scripts/render_ideas.py"
wrote ideas/ideas.md — 4 ideas
$ uv run ".../scripts/check.py" --feature ideas
ideas: OK
```

An amendment and a link, then the fold:

```
$ uv run ".../scripts/idea.py" amend 000003 --title 'Weekly picking-yield summary per block for the orchard manager'
amended 000003 at 2026-09-27T06:34:31-04:00 eid e18d9270ef0bf45d3
$ uv run ".../scripts/idea.py" link 000003 --type relates_to --target 000001
linked 000003 at 2026-09-27T06:34:34-04:00 eid e18d9270f81014723
$ uv run ".../scripts/idea.py" show 000003
{
  "title": "Weekly picking-yield summary per block for the orchard manager",
  "body": "Send the orchard manager a weekly summary of picking yields broken down by block. ...",
  "status": "open",
  "created": "2026-09-27T06:34:10-04:00",
  "updated": "2026-09-27T06:34:34-04:00",
  "revisits": 0,
  "promoted_to": null,
  "annotations": [],
  "links": [
    {
      "eid": "e18d9270f81014723",
      "type": "relates_to",
      "target": "000001",
      "retracted": false,
      "at": "2026-09-27T06:34:34-04:00"
    }
  ]
}
$ uv run ".../scripts/idea.py" list
000001 | open | Export the harvest calendar to CSV for the picking crew
000002 | open | Dated tree-health notes per orchard block (disease, pruning, frost damage)
000003 | open | Weekly picking-yield summary per block for the orchard manager
000004 | open | Rename 'block' to 'plot' across the data model and screens
$ uv run ".../scripts/render_ideas.py"
wrote ideas/ideas.md — 4 ideas
$ uv run ".../scripts/check.py" --feature ideas
ideas: OK
```

The folded title is the amended one; the body is elided here only.

### 5. Triage

The idea-triage skill, once per idea. Each run dispatched the `idea-realization:idea-triage`
agent with the literal write command, verified the finding with `show`, then moved the status:

```
$ uv run ".../scripts/idea.py" annotate 000001 --author agent-idea-triage --kind finding --file /tmp/triage_finding_000001.txt
annotated 000001 at 2026-09-27T06:36:02-04:00 eid e18d927240d06741e
$ uv run ".../scripts/idea.py" status 000001 triaged
status 000001 at 2026-09-27T06:36:18-04:00 eid e18d92727a185fdca
wrote ideas/ideas.md — 4 ideas
ideas: OK
```

The other three, from their runs:

```
annotated 000002 at 2026-09-27T06:37:26-04:00 eid e18d92737ac343e5d
status 000002 at 2026-09-27T06:37:41-04:00 eid e18d9273b223e874d
annotated 000003 at 2026-09-27T06:38:56-04:00 eid e18d9274c70ed2eb5
status 000003 at 2026-09-27T06:39:12-04:00 eid e18d9275058d3ecec
annotated 000004 at 2026-09-27T06:40:25-04:00 eid e18d927612d0c07cd
status 000004 at 2026-09-27T06:40:39-04:00 eid e18d927647723d29f
```

The triage runs reported five proposed links (000002 and 000003 each to 000004, and 000004 to
all three others) and no proposed promotion; the skill wrote none of them.

### 6. The partition sweep

**First attempt: refused, as designed.** The scaffold's ignore rule was committed only on
`exercise`, so the primary checkout did not ignore the staging directory:

```
$ uv run ".../scripts/idea_corpus.py" locate; echo "EXIT=$?"
refused: <scratch>/orchard/.idea-realization/staging is not gitignored in <scratch>/orchard
primary: <scratch>/orchard
staging: <scratch>/orchard/.idea-realization/staging
corpus: <scratch>/orchard/.idea-realization/staging/corpus
partitions: <scratch>/orchard-worktrees/exercise/ideas/partitions
primary_status: e3b0c44298fc
EXIT=1
```

Nothing was written. As the person, I fast-forwarded `main` to `exercise`
(`git -C <scratch>/orchard merge --ff-only exercise`, to `5060a4e`) and restarted the sweep. The
README's install section now states this step.

**Second attempt: the whole sweep.**

```
$ uv run ".../scripts/check.py" --feature ideas; echo "check exit: $?"
ideas: OK
check exit: 0
$ uv run ".../scripts/idea_corpus.py" locate; echo "locate exit: $?"
primary: <scratch>/orchard
staging: <scratch>/orchard/.idea-realization/staging
corpus: <scratch>/orchard/.idea-realization/staging/corpus
partitions: <scratch>/orchard-worktrees/exercise/ideas/partitions
primary_status: e3b0c44298fc
staging ignored: yes
locate exit: 0
$ uv run ".../scripts/idea.py" list --status open; echo "exit: $?"
exit: 0
$ uv run ".../scripts/idea_corpus.py" start; echo "exit: $?"
NEW: no manifest
exit: 0
$ uv run ".../scripts/idea_corpus.py" build; echo "build exit: $?"
corpus size: 4 (of 4 selected)
excluded: 0
layered evidence (>1 finding): 0
seed: 410808195
written to <scratch>/orchard/.idea-realization/staging/corpus
build exit: 0
$ uv run ".../scripts/idea_corpus.py" locate
...
primary_status: e3b0c44298fc
corpus_size: 4 | status: triaged | seed: 410808195 | corpus date: 2026-09-27
```

`prompt R1` and `prompt R4` printed their sections with absolute paths into the primary checkout's
staging directory; both went to `idea-realization:partition-analyst` in one turn, on sonnet.

```
$ uv run ".../scripts/idea_corpus.py" report R1 --file .../R1.md; ... report R4 --file .../R4.md
wrote <scratch>/orchard/.idea-realization/staging/corpus/report-R1.md
R1 exit: 0
wrote <scratch>/orchard/.idea-realization/staging/corpus/report-R4.md
R4 exit: 0
primary_status: e3b0c44298fc
```

GATE 1 stopped for a ruling; on yes, `prompt A1` went to `idea-realization:partition-adversary`:

```
$ uv run ".../scripts/idea_corpus.py" report A1 --file .../A1.md; echo "exit: $?"
wrote <scratch>/orchard/.idea-realization/staging/corpus/audit-1-findings.md
exit: 0
primary_status: e3b0c44298fc
```

Audit 1: no blocker; two major findings (the 000001 + 000003 group rests on a reuse assumption
000003 itself doubts; one analyst's "rename first" order traced to finding-only text) and three
minor. GATE 2 stopped; on yes, the synthesis ran in the nested session:

```
$ uv run ".../scripts/idea_corpus.py" name 2026-09-27; echo "exit: $?"
<scratch>/orchard/.idea-realization/staging/idea-partition-2026-09-27.md
<scratch>/orchard/.idea-realization/staging/idea-partition-2026-09-27.json
exit: 0
$ uv run ".../scripts/idea_corpus.py" check <markdown> <record>; echo "check exit: $?"
0 problem(s)
check exit: 0
```

**The second audit ran.** `prompt A2 --draft <scratch>/orchard/.idea-realization/staging/idea-partition-2026-09-27.md`
named the draft by its absolute path in the primary checkout, while the session worked in
`<scratch>/orchard-worktrees/exercise`. It went to `idea-realization:partition-adversary`:

```
$ uv run ".../scripts/idea_corpus.py" report A2 --file .../A2.md; echo "exit: $?"
wrote <scratch>/orchard/.idea-realization/staging/corpus/audit-2-findings.md
exit: 0
```

Audit 2's findings, from `audit-2-findings.md`:

- **Blocker:** none. **Major:** none. It checked coverage against the manifest itself (4 placed,
  0 unbatched, no duplicate), that the merge's three tracks and fine groups match what both
  analysts proposed, that the decline tiers match (only R4 nominated 000004), that the size ranges
  span both analysts rather than average them, and that the analysts' agreement rests on text
  both corpora carry.
- **Minor 1:** the merge states as fact that audit 1 traced one analyst's order to finding-only
  text, where audit 1 inferred it from matching wording; the ruling ("no precedence recorded")
  stands either way.
- **Minor 2:** the JSON record has no field for a group's condition, so the harvest group's
  conditional status exists only in the markdown and is lost to a reader of the record. Recorded
  as idea 000476.

The gate checklist `G`:

```
== item 1: step-5 check
0 problem(s)
exit: 0
== item 1: manifest vs record ids
manifest corpus_size 4 | corpus ids ['000001', '000002', '000003', '000004'] | placed ['000001', '000002', '000003', '000004'] | dupes 0 | equal True
== item 7
ideas: OK
exit: 0
== item 8
git diff --quiet 5060a4e -- ideas/ideas.jsonl exit: 0
```

At GATE 3 I accepted the partition as the person, kept 000004 (not declined) and left the rename
order open:

```
$ uv run ".../scripts/idea_corpus.py" accept <markdown> <record>; echo "accept exit: $?"
wrote <scratch>/orchard-worktrees/exercise/ideas/partitions/idea-partition-2026-09-27.md
wrote <scratch>/orchard-worktrees/exercise/ideas/partitions/idea-partition-2026-09-27.json
accept exit: 0
accepted ideas/partitions/idea-partition-2026-09-27.md
```

Four dispatches (R1, R4, A1, A2), none resumed, none above sonnet; about 15.5 minutes of sweep
time against the nested session's own estimate of 25 to 35. The partition: three programmes —
harvest export and yield reporting (000001, 000003, conditional), tree-health notes (000002),
and the block-to-plot rename (000004). Committed as `7d9832b`.

### 7. A requirement and a plan

The nested session was asked to write a requirement and a plan for the harvest programme from the
plugin's templates, with codes from next-code:

```
$ uv run ".../scripts/cli.py" next-code requirement; echo "exit=$?"
REQ-001
exit=0
$ uv run ".../scripts/cli.py" next-code plan; echo "exit=$?"
PLAN-001
exit=0
$ uv run ".../scripts/plan_check.py" docs/plans/PLAN-001-harvest-export-and-yield-reporting.md; echo "exit=$?"
docs/plans/PLAN-001-harvest-export-and-yield-reporting.md: OK
exit=0
$ uv run ".../scripts/check.py" --feature documents; echo "exit=$?"
documents: docs/catalog.md: is missing; run the catalog command and commit it
exit=1
$ uv run ".../scripts/cli.py" catalog; echo "exit=$?"
wrote docs/catalog.md (2 documents)
exit=0
$ uv run ".../scripts/check.py" --feature documents; echo "exit=$?"
documents: OK
exit=0
```

It registered `sys-harvest-reporting` in `docs/systems.yaml` with `status: planned`, since the
scratch repository has no path to name. To find where a requirement lives, how its file is named
and what a system needs, it read `documents.py` and `codes.py`: neither the templates nor the
README said. The README's use section now does. Committed as `46d079c`.

### 8. Register and claim a phase

`phase-harvest-01` was added to `backlog/backlog.yaml` and `next_up`, and validated against the
backlog schema. The backlog skill:

```
$ uv run ".../scripts/check.py"; echo "exit=$?"
backlog: status-regression not run: the backlog names no decision_record, so a reopened phase has nowhere to be recorded
backlog: OK
documents: docs/catalog.md: differs from the rendered catalog; run the catalog command and commit it, and never edit it by hand
ideas: OK
exit=1
$ uv run ".../scripts/cli.py" catalog
wrote docs/catalog.md (2 documents)
$ uv run ".../scripts/check.py"; echo "exit=$?"
backlog: status-regression not run: the backlog names no decision_record, so a reopened phase has nowhere to be recorded
backlog: OK
documents: OK
ideas: OK
exit=0
$ uv run ".../scripts/cli.py" ready
# Session backlog

1 phases; every phase has a one-session budget.
ready: 1

Active claims: 0 of 1 allowed.
...
Queued to the front: phase-harvest-01.

| Phase | Outcome | Queue | Priority | State | Prerequisites | Conflicts |
|---|---|---|---|---|---|---|
| phase-harvest-01 | Locate the harvest calendar and rule on whether the CSV export computes yield | 1 | 1 | ready | — | — |
```

session-start read its values from the worktree and stopped for the claim question:

```
$ uv run ".../scripts/paths.py"
root: <scratch>/orchard-worktrees/exercise
...
integration_branch: main
worktree_dir: <scratch>/orchard-worktrees/exercise/../exercise-worktrees
```

That `worktree_dir` is wrong: it names a directory beside the worktree, after the worktree, where
the session's worktree would have been cut. The defect is fixed below. With the fix, on the
person's yes, the claim ran:

```
$ git -C <scratch>/orchard merge --ff-only exercise
Updating 5060a4e..d351a53
Fast-forward
$ git -C <scratch>/orchard commit ... "Claim phase-harvest-01 for agent-harvest"
47237e0 Claim phase-harvest-01 for agent-harvest
 backlog/backlog.yaml | 3 ++-
 docs/catalog.md      | 2 +-
$ uv run ".../scripts/paths.py"      # from <scratch>/orchard
worktree_dir: <scratch>/orchard/../orchard-worktrees
$ git -C <scratch>/orchard worktree add -b agent/phase-harvest-01 <scratch>/orchard-worktrees/phase-harvest-01 main
<scratch>/orchard                             47237e0 [main]
<scratch>/orchard-worktrees/exercise          d351a53 [exercise]
<scratch>/orchard-worktrees/phase-harvest-01  47237e0 [agent/phase-harvest-01]
```

The nested session re-read the values from the primary checkout, which would have given the
right answer before the fix too. Run from the worktree with the fixed script:

```
$ uv run .../scripts/paths.py | grep worktree_dir      # from <scratch>/orchard-worktrees/exercise
worktree_dir: <scratch>/orchard/../orchard-worktrees
```

### 9. Allocate a code, render the catalog, doctor again, scaffold again

From the exercise worktree, fast-forwarded to `47237e0`:

```
$ uv run ".../scripts/cli.py" next-code adr; echo "exit=$?"
ADR-001
exit=0
$ uv run ".../scripts/cli.py" catalog; echo "exit=$?"
wrote docs/catalog.md (2 documents)
exit=0
$ uv run ".../scripts/doctor.py"; echo "exit=$?"
drifted   ideas/ideas.jsonl  (ideas)
drifted   ideas/ideas.md  (ideas)
unchanged ideas/priority.yaml  (ideas)
unchanged .idea-realization/schemas/idea.schema.json  (ideas)
unchanged .idea-realization/schemas/idea-priority.schema.json  (ideas)
unchanged .idea-realization/schemas/idea-partition-record.schema.json  (partition)
drifted   backlog/backlog.yaml  (backlog)
unchanged .idea-realization/schemas/backlog.schema.json  (backlog)
unchanged docs/codes.yaml  (documents)
drifted   docs/systems.yaml  (documents)
unchanged .idea-realization/schemas/document.schema.json  (documents)
unchanged .idea-realization/schemas/codes.schema.json  (documents)
unchanged .idea-realization/schemas/systems.schema.json  (documents)
unchanged .idea-realization/staging/  (partition)
unchanged docs/  (documents)
unchanged .gitignore  (consent: gitignore)
16 recorded, 4 drifted or missing
exit=1
```

The four drifted files are data files the pipeline is meant to change; the doctor cannot tell
them from a damaged schema, so it cannot pass after first use. Recorded as idea 000474.

**The second scaffold run created no file:**

```
$ uv run ".../scripts/scaffold.py" --feature ideas --feature partition --feature backlog --feature documents; echo "exit=$?"
skipped  ideas/ideas.jsonl (exists)
skipped  ideas/ideas.md (exists)
skipped  ideas/priority.yaml (exists)
skipped  .idea-realization/schemas/idea.schema.json (exists)
skipped  .idea-realization/schemas/idea-priority.schema.json (exists)
skipped  .idea-realization/staging/ (exists)
skipped  .idea-realization/schemas/idea-partition-record.schema.json (exists)
skipped  backlog/backlog.yaml (exists)
skipped  .idea-realization/schemas/backlog.schema.json (exists)
skipped  docs/ (exists)
skipped  docs/codes.yaml (exists)
skipped  docs/systems.yaml (exists)
skipped  .idea-realization/schemas/document.schema.json (exists)
skipped  .idea-realization/schemas/codes.schema.json (exists)
skipped  .idea-realization/schemas/systems.schema.json (exists)
skipped  .gitignore (already ignores the staging directory)
exit=0
$ git status --short
```

No `recorded` line, so the install record was not rewritten either, and the tree stayed clean.

## Defects found

| Defect | Disposition |
|---|---|
| `worktree_dir`, resolved from a worktree, named `<worktree>/../<worktree name>-worktrees` instead of the repository's sibling directory, so session-start would cut a session's worktree in the wrong place | **Fixed** in `66b6417` with `test_worktree_dir_from_a_worktree_is_the_repositorys`, which failed before the fix. `worktree_dir` now resolves against the primary checkout (`paths.primary_checkout`, moved from `idea_corpus.py`), and `render_template.py` fills `<repository>` from it too |
| The README described only the skeleton, and did not say that the staging ignore rule must reach the primary checkout, or where a governed document goes and how it is named | **Fixed** in `8e6e44b`: the install and use sections, checked by the R02 and no-history tests |
| The doctor reports ordinary edits to scaffolded data files as drift and exits 1 from first use on | Idea **000474** |
| The scaffolded backlog names no `decision_record`, so every check prints `status-regression not run` | Idea **000475** (overlaps 000470) |
| The partition record schema has no field for a group's condition | Idea **000476** |

All three ideas are linked to 000470, the anchor for the planning after this phase.

## Verification

Run in the worktree on `agent/phase-plug-08`:

```
$ cd plugins/idea-realization && uv run pytest
497 passed

$ claude plugin validate plugins/idea-realization --strict
✔ Validation passed

$ uv run python tools/check_no_private_content.py
check_no_private_content: OK (1052 tracked files, 0 identifiers checked)

$ uv run python -m src.governance
Governance OK: 43 systems, 388 documents, 34 memories, 323 backlog phases
```

## Acceptance

- The session record names the scratch repository, quotes each command's real output, and lists
  the scaffold's created files: **Met**, above.
- The partition sweep's second audit ran and its findings are in the record: **Met**. A2 was
  dispatched with the draft's absolute primary-checkout path and wrote `audit-2-findings.md`; its
  findings are quoted under step 6.
- A second scaffold run over the scratch repository creates no file: **Met**. Every line was
  `skipped`, with no `recorded` line and a clean `git status`.
- Every defect found is either fixed with a test or recorded as an idea by id: **Met**. The table
  above.

## Handover

**What shipped.** The idea-realization plugin, loadable with `--plugin-dir`, with fourteen skills
(prerequisites, scaffold, doctor, idea, idea-triage, partition-ideas, next-code, plan-check,
catalog, backlog, session-start, checkpoint, session-close, tools), three agents (idea-triage,
partition-analyst, partition-adversary), the governance documents as absolutes, templates, and a
497-test suite. This phase added the fix for `worktree_dir` from a worktree and the README's
install and use sections.

**What the exercise found.** Every feature ran once, in pipeline order, from a worktree of a
foreign repository. The partition sweep refused, correctly, until the ignore rule reached the
primary checkout, then ran all four dispatches including the second audit against the
primary-checkout draft. Five defects: two fixed here, three recorded as ideas 000474, 000475 and
000476.

**What is left.** The three ideas, batched on 000470. A persistent install waits for a
marketplace. Installing into a real repository is the owner's own step, outside this plan.

## Backlog

`status: active`, `agent: agent-builder-b`.

## Unresolved

None.

## Review

## Left undone

- The completion edit waits for the owner-approved merge.
