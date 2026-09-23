---
schema_version: 1
id: doc-session-partition-ideas-workflow
code: SESS-2026-09-23-05
title: The partition-ideas workflow
kind: session
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-governance]
depends_on: [doc-repeatable-idea-partition]
---

# The partition-ideas workflow

## Phase

`phase-part-03` — Build the partition-ideas workflow.

## Verification

The phase's verification runs in two parts. By the owner's ruling, the dry run happens after the
merge, because the skill is only listed once it is on dev and its subagents run in the primary
checkout. The checks that can run on the branch have run:

- `uv run python -m src.governance`:

  ```text
  Governance OK: 35 systems, 326 documents, 30 memories, 293 backlog phases
  ```

- `uv run python tools/generate_agent_workflows.py --check`: `16 workflow adapter(s) current`.
  `uv run pytest test/test_agent_workflows.py`: `20 passed, 2 warnings`. Full suite: `871 passed,
  1 skipped, 2 warnings`.
- **Read the skill body for any brief it quotes rather than dispatches.** The body contains no
  prompt text. Every dispatch goes through one extraction command that prints a pack section's
  fenced block from `PROMPT-034`, and the coordinator sends that output as the whole prompt.
- **Confirm the body names both R1 and R4 as dispatches ahead of GATE 1.** Step 3, "The analysts —
  `R1` and `R4`, concurrently", dispatches both in the same turn, before `## GATE 1`.
- **The R1 prompt against `PROMPT-034:112-182`.** The skill's extraction command, run on the
  branch, reproduces the pack text exactly: `diff <(sed -n '117,178p' PROMPT-034...) <extracted R1>`
  and the same for R4 (`193,251p`) both print nothing. (Lines 117-178 are the R1 block's contents
  inside its fence, within the cited 112-182 range.) The post-merge dry run repeats this against
  the prompt actually dispatched, which the skill saves to `dispatch-R1.txt`.
- **Structured record and same-day naming.** The owner ruled that these are verified by running
  the skill's own step-5 snippets, extracted from the generated `SKILL.md`, on a hand-made partition
  in the session scratchpad:

  ```text
  == naming, no earlier file
  docs/00-working/idea-partition-2026-09-23.md
  docs/00-working/idea-partition-2026-09-23.json
  == check, matching pair
  0 problem(s)
  exit=0
  == naming, same corpus date already present
  docs/00-working/idea-partition-2026-09-23-2.md
  docs/00-working/idea-partition-2026-09-23-2.json
  == naming, -2 also present
  docs/00-working/idea-partition-2026-09-23-3.md
  docs/00-working/idea-partition-2026-09-23-3.json
  == check, record drops 000102
  FAIL missing from the record: 000102
  FAIL in the markdown, not the record: 000102
  2 problem(s)
  exit=1
  == check, markdown disagrees (000102 -> 000109)
  FAIL in the record, not the markdown: 000102
  FAIL record names docs/00-working/idea-partition-2026-09-23.md, not bad2.md
  2 problem(s)
  exit=1
  == check, schema violation
  FAIL schema: state: 'done' is not one of ['proposed', 'accepted']
  1 problem(s)
  exit=1
  ```

- **Resume-or-start and moving earlier files aside**, exercised the same way on a scratch copy of
  the primary checkout's `_working/idea-corpus/` (the 2026-09-13 set):

  ```text
  == decide (the 2026-09-13 set)
  NEW: the manifest in place (no stamped output) belongs to an earlier sweep
  == move aside
  left: [] moved: 10 files
  == decide (stamped report for this manifest)
  RESUME: corpus built 2026-09-13, size 152, seed 1976391957
  already done: report-R1.md
  == read
  corpus_size: 152 | status: triaged | seed: 1976391957 | corpus date: 2026-09-13
  == move with a name already in the target
  moved manifest.json -> previous-2026-09-13/manifest-2.json
  moved corpus-R4.md -> previous-2026-09-13/corpus-R4-2.md
  ```

**Not yet run — the post-merge dry run** (a `dryrun` turn in the primary checkout): invoke
`/partition-ideas` and stop at GATE 1, recording the open-set output, the manifest's corpus size
and the report path; hash `_data/ideas.jsonl` before and after; diff `dispatch-R1.txt` against the
pack; re-invoke after abandoning at GATE 1 and confirm it reports the existing report and
dispatches nothing already done.

## Acceptance

- Listed as a skill and runs to GATE 1 against the live corpus — **Not met yet.** Needs the
  post-merge dry run.
- With at least one open idea, prints the ids and halts before the first dispatch — **Not met
  yet.** Step 1 is written to do this; the dry run will show it.
- Every dispatch matches its PROMPT-034 section character for character — **Met on the branch**
  for the extraction (R1 and R4 diffs empty). The dry run confirms the dispatched text.
- One analyst report at `_working/idea-corpus/`, written by the coordinator — **Not met yet.**
  Needs the dry run.
- Moves no idea status, marks no phase complete, stops at all three gates — **Met by reading.** The
  skill has no idea-log writer, no backlog edit, and an explicit stop at GATE 1, GATE 2 and GATE 3,
  plus the owner-ruled stop before A2.
- `_data/ideas.jsonl` unchanged by the dry run — **Not met yet.** Needs the dry run's hash check.
- R06, R11, R13, R05's empty-set branch and R14's GATE 2/GATE 3 halts are not exercised here — as
  the phase states.
- The structured record validates, and its tracks and ids agree with the markdown — **Met by
  fixture** (above), per the owner's ruling.
- Same-day re-invocation refuses or suffixes — **Met by fixture** (`-2`, then `-3`).

## Backlog

`status: active`, `agent: agent-builder-b`, `session: doc-session-partition-ideas-workflow`.
`next_action`: Branch work done; after the owner-approved merge, run the dry run to GATE 1 in a
`dryrun` turn and record its evidence here before the completion edit.

## Unresolved

- The dry run's evidence, listed above.
- A2 cannot read the synthesis draft as the pack is written; the skill stops before A2 by the
  owner's ruling. Recorded as idea `000339`.
