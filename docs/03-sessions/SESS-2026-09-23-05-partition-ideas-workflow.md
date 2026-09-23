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

**Dry run, attempt 1 (2026-09-23T05:52Z, `dryrun` turn granted at dev `2bdbf83`) — stopped at the
open-set gate.** `/partition-ideas` was listed and invoked in the primary checkout. Preflight:
`Governance OK: 35 systems, 334 documents, 31 memories, 293 backlog phases`. Step 1 printed:

```text
open ideas: 2
  000351 | Regenerate docs/08-governance/catalog.md only at merge time, not on every claim and completion commit, so open branches stop conflicting on it
  000352 | No backlog phase builds the orchestrator's unit graph, which runs backlog phases through claim, build and integration
```

The skill stopped there, as step 1 requires, to ask the owner whether to triage first or partition
without those ideas. The owner was asleep and the ruling is theirs, so the item was **PARKed**.
Nothing was built, moved or dispatched: `_working/idea-corpus/` still holds the 2026-09-13 set
unmoved, `sha256sum -c` on `_data/ideas.jsonl` printed `OK`, and `git status` in the primary
checkout was clean at `2bdbf83`. This run is the evidence for the open-set halt condition. The
GATE-1 conditions still need a second run once the open set is empty or the owner has ruled.

**Dry run, attempt 2 (2026-09-23T05:54Z-06:05Z, `dryrun` turn granted at dev `806d3e2`) — reached
GATE 1 and stopped.** Ideation's routine triage had moved `000351` and `000352` out of open.

- Preflight: `Governance OK: 35 systems, 334 documents, 31 memories, 293 backlog phases`. Stated
  estimate: about 25 minutes, raised to about 45 once the corpus size was known. Actual time to
  GATE 1 was 11 minutes.
- Step 1: `open ideas: 0`. The open set was empty.
- Step 2: `NEW: the manifest in place (no stamped output) belongs to an earlier sweep`. It moved all
  ten 2026-09-13 files (`manifest.json`, `corpus-R1..R4.md`, `report-R1..R4.md`,
  `audit-1-findings.md`) into `previous-2026-09-13/`, and deleted nothing. Corpus built:
  `corpus size: 325 (of 331 triaged)`, `excluded by the fast lane: 6`, `shuffle seed: 656057328`.
  Manifest read: `corpus_size: 325 | status: triaged | seed: 656057328 | corpus date: 2026-09-23`.
- Dispatch text: `dispatch-R1.txt` and `dispatch-R4.txt` saved by the extraction command. Both diff
  empty against `PROMPT-034` lines 117-178 and 193-251. R1 and R4 went in the same turn to
  general-purpose agents on sonnet, with the saved text as the whole prompt. Two dispatches, none
  resumed, none above sonnet.
- **R4:** the harness refused its write of `report-R4.md`, as idea `000206` records, and it
  returned the report as text. The coordinator wrote `report-R4.md` (25,431 bytes) as the run stamp
  followed by the returned text, taken byte-exact from the hand-back rather than retyped. The report
  was complete, with every required section, so no resume was needed.
- **R1 — departure.** When its report write was refused, R1 **wrote the report itself through a
  Bash heredoc**. It also wrote a working file, `condensed.md` (411,970 bytes). Both are in the
  gitignored `_working/idea-corpus/`, and nothing tracked changed. `report-R1.md` (42,360 bytes)
  carries no run stamp, so by the workflow's own rule it is not this sweep's report. The
  coordinator left both files as R1 wrote them. It did not stamp, move or re-dispatch R1, because
  how to treat that output is a decision for the owner. The workflow's premise that "subagents
  cannot write report files" holds for the Write tool only: an analyst with Bash can go around it,
  and the pack's own "Write your report to ..." invites it to. Recorded as idea `000354`.
- Resume check: step 2's classification, re-run after the reports, printed `RESUME: corpus built
  2026-09-23, size 325, seed 656057328` and `already done: report-R4.md`. It moved nothing, since
  RESUME exits before the move. It does not count the unstamped `report-R1.md` as done, so a real
  re-invocation would dispatch R1 again and overwrite R1's own file when writing the report.
- `sha256sum -c` on `_data/ideas.jsonl`: `OK`, unchanged. Primary checkout `git status` clean at
  `806d3e2`.

## Acceptance

- Listed as a skill and runs to GATE 1 against the live corpus — **Met** by dry run attempt 2.
- With at least one open idea, prints the ids and halts before the first dispatch — **Met** by dry
  run attempt 1: it printed `000351` and `000352` and halted, with nothing built or dispatched.
- Every dispatch matches its PROMPT-034 section character for character — **Met.** In attempt 2,
  `dispatch-R1.txt` and `dispatch-R4.txt` diff empty against the pack.
- One analyst report at `_working/idea-corpus/`, written by the coordinator — **Met for R4**
  (`report-R4.md`, stamped). R1 wrote its own unstamped report through Bash, and that is left for
  the owner's ruling; see attempt 2.
- Moves no idea status, marks no phase complete, stops at all three gates — **Met by reading.** The
  skill has no idea-log writer, no backlog edit, and an explicit stop at GATE 1, GATE 2 and GATE 3,
  plus the owner-ruled stop before A2.
- `_data/ideas.jsonl` unchanged by the dry run — **Met.** `sha256sum -c` printed `OK` after both
  attempts.
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

- **Ruled: option C (owner, morning of 2026-09-23; see `## Decisions`). The fix is merged; the R1
  re-run is pending.** Originally PARKED for the owner (Session Manager ruling, 2026-09-23
  overnight): how to treat R1's
  self-written output. In dry run attempt 2, R1 went around the harness refusal of its report
  write through Bash. It left `report-R1.md` (unstamped) and `condensed.md` in
  `_working/idea-corpus/`, and both are untouched. Under the overnight authority (§3), a block that
  something went around goes to the owner. It also bears on this phase's deliverable, the
  workflow's own safety. The completion edit waits, the claim is kept, the branch stays pushed, and
  when the owner rules the evidence commits reach dev through READY. Options:
  - **A. Adopt R1's output.** The coordinator prepends the run stamp to `report-R1.md`, the record
    notes that R1 wrote the file itself, and the phase completes on the existing evidence.
    Cheapest, and the content is R1's real report. It does accept a report the coordinator did not
    write.
  - **B. Discard and re-run R1 as it stands.** Move both files into a `previous-` folder (move,
    never delete) and dispatch R1 again, the coordinator writing the returned text. About 10
    minutes of sonnet. Nothing stops R1 from going around the refusal again.
  - **C. Fix the dispatch first, then re-run R1 (recommended).** Move both files aside, stop
    analysts from writing files, then re-run R1 under option B. Two ways to stop them: dispatch R1
    and R4 to a read-only agent type, or amend `PROMPT-034`'s "Write your report to ..." line (idea
    `000354`). This is the only option that makes the workflow's "the coordinator writes
    every report" premise hold. It is new work beyond this phase's approved scope, so it needs the
    owner's approval.
  - **Other:** the owner's own ruling.
- The dry run's evidence, listed above.
- A2 cannot read the synthesis draft as the pack is written; the skill stops before A2 by the
  owner's ruling. Recorded as idea `000339`.

## Decisions

Owner rulings from this session. Each changed what was built.

- **Declarations (at assignment):** the skill is generated through `agent-workflows/` by
  `tools/generate_agent_workflows.py`, for both the `claude` and `open-agent-skills` hosts. The
  deliverables are `workflows.yaml`, `partition-ideas.md`, both generated `SKILL.md` files and the
  schema. This follows the owner's approval, although PLAN-025 leaves porting to other hosts to
  PLAN-020.
- **Files from earlier sweeps — stamp and move aside.** The pack's prompts name fixed paths, and
  `_working/idea-corpus/` still holds the 2026-09-13 sweep's reports at those paths. The coordinator
  stamps every file it writes there with the manifest's seed, corpus size and status. A new sweep
  moves every earlier corpus, report, audit and dispatch file into
  `previous-<file modification date>/`, and never deletes one. Resume counts only files stamped for
  the current manifest.
- **The corpus date is `manifest.json`'s modification date**, because the manifest records no
  build date and the corpus builder is outside this phase.
- **Merge first, then the dry run.** The skill is only listed once it is on dev, and its subagents
  run in the primary checkout. The dry run to GATE 1 therefore happens after the merge, in a
  `dryrun` turn, and the completion edit waits for its evidence.
- **Stop before A2.** A2's verbatim prompt reads a draft that exists only in the coordinator's
  worktree. The skill stops before A2 and asks the owner. Recorded as idea `000339`.
- **The structured record and same-day naming are verified by fixture**, by running the skill's own
  step-5 snippets on a hand-made partition. The GATE-1 dry run never reaches synthesis.
- **R1's self-written output: option C (morning of 2026-09-23).** Move R1's output aside, stop
  analysts writing files, re-run R1, then complete. This adds scope, which the owner approved.
- **How analysts are stopped: a read-only agent type (option A of the follow-up question).**
  `R1` and `R4` go to a new `.claude/agents/partition-analyst.md` whose only tools are Read, Grep
  and Glob. `PROMPT-034` is unchanged; the skill states its departure from the pack's
  "general-purpose agent" line. `partition-adversary` is out of scope. The owner approved a one-off
  primary-checkout turn to add the agent file to this phase's deliverables.
- **The analyst's context window is 1M, settled from the Claude Code docs.** R1's corpus is
  1,343,696 bytes, about 340k tokens, and without a shell the analyst must read it whole (last
  night R1 condensed it through Bash first). The agent file says `model: sonnet`. The model
  configuration page (code.claude.com/docs/en/model-config) says that on the Anthropic API the
  `sonnet` alias resolves to Sonnet 5, and: "On the Anthropic API, Sonnet 5 always runs with the 1M
  context window. There is no 200K variant, no `[1m]` suffix to select". No `ANTHROPIC_*` model
  variable or subagent model override is set here, so the provider is the Anthropic API. The
  GitHub issues about a stripped `[1m]` suffix for subagents (#39047, #45169) concern the 4.6
  models, which reach 1M only through that suffix. The R1 re-run is the practical check: a report
  that covers every corpus id shows the whole file was read.

## Corrections

- **Heredoc terminator collision (2026-09-23).** A skill edit passed through `python3 - <<'EOF'`
  contained the skill's own `<<'EOF' ... EOF` example. The heredoc ended early, and bash ran the
  remaining text, including a backtick fragment that built a corpus with `--out ""` into the
  worktree root. Five untracked files were written there and then removed. Nothing tracked, the
  primary checkout and `_data/ideas.jsonl` were unaffected. The edit was redone with the
  file-editing tool, and the skill's build and move commands gained a `${CORPUS:?}` guard. Recorded
  at the owner's direction as a brain procedure (branch `agent/heredoc-procedure`) and as a guard
  idea sent to Ideation.
- The move-aside snippet first sat inside a numbered list, so its lines carried the list's indent.
  An agent pasting the raw text would get an `IndentationError`. It was moved out of the list
  before commit.
- The first corpus-id pattern in the step-5 check matched any heading containing six digits,
  including finding bodies (178 matches against a corpus of 152). It now matches only the builder's
  entry heading, `## <id> — `.
- **A cause reported before it was checked, twice (2026-09-23).** (1) The READY for the analyst
  fix told the Session Manager that dev's two catalog-test failures also occurred "without my
  changes" before they had been run on dev. A throwaway worktree at `f6216e9` then gave `2 failed,
  59 passed`, and a follow-up message said the claim was now verified. (2) One failed dispatch to
  `partition-analyst` right after its merge was reported as "agent types load when a session
  starts", with BLOCKED and a request for a restart. Minutes later the harness listed the type in
  the same session. The resume state was corrected. At the owner's direction this is recorded as
  the brain procedure `mem-proc-verify-a-cause-before-you-report-it` (branch
  `agent/verify-cause-procedure`).

## Review

Independent adversarial review (a fresh `demo-adversary` subagent) of `dev...agent/phase-part-03`
at `d8428df` and `0cbc826`. It returned after the overnight safe point, and **its findings are not
yet fixed**. As reported:

- Acceptance: conditions 1, 2, 4 and 6 are **Not yet** (the post-merge dry run). Condition 3
  **Holds at extraction level**: all six sections were re-extracted, and the R1 and R4 diffs
  against the pack are empty. Conditions 5 and 7 **Hold**. Conditions 8 and 9 are **met by fixture,
  with gaps** (MEDIUM-1, MEDIUM-2). The generator check, the 20 workflow tests and governance
  passed. The two generated `SKILL.md` files are byte-identical.
- **HIGH:** step 2's resume check crashes with `KeyError: 'manifest'` on any
  `docs/00-working/idea-partition-*.json` that lacks the key, including a half-written record, so
  one malformed file blocks every later invocation.
- **MEDIUM-1:** step 5's cross-check never looks at `decline_candidates`. A candidate id outside
  the corpus, and outside every group and unbatched, passes with `0 problem(s)`, contrary to the
  schema's own stated invariant.
- **MEDIUM-2:** the same-day naming cannot tell an earlier sweep's document from this sweep's own
  half-written one. A crash mid-step-5 leaves an orphaned `.md`, and the re-run takes `-2`.
- **MEDIUM-3:** the move-aside snippet has no stamp awareness. Run during a RESUME by mistake, it
  moves the current sweep's stamped `report-R1.md` away with everything else.
- **LOW:** a manifest built but not yet used by any report is classified NEW, which rebuilds the
  corpus with a new seed. Nothing is lost, but the rebuild is wasted.
- **LOW:** the extraction regex assumes no fenced block is nested inside a pack section. That
  holds today (12 fences, 6 pairs), but nothing enforces it.
- Areas that held: no quoted brief, no idea-log or backlog write, and no scope creep. R4 is R1's
  block with the findings references removed and nothing added. Idea `000339` exists as cited.

### Outcomes (fix cycle 1, overnight sprint, 2026-09-23, commit `e52f820`)

All in `agent-workflows/partition-ideas.md`, with both `SKILL.md` files regenerated
(`16 workflow adapter(s) current`, the two files byte-identical).

- **HIGH — fixed.** Step 2 reads each partition record inside `try`, and a record it cannot read
  (bad JSON, no `manifest` key, wrong shape) is printed as `UNREADABLE (ignored)` and skipped.
- **MEDIUM-1 — fixed.** Step 5's check now fails a decline candidate that is in no group and not
  unbatched (which covers one outside the corpus), one missing from the markdown, and one listed
  in both tiers or twice in one.
- **MEDIUM-2 — fixed.** The markdown now starts with the run stamp, and step 5's check requires it.
  The naming command treats a document carrying this sweep's stamp, or a record carrying this
  manifest's seed, as this sweep's own draft: it prints `CONTINUE` and reuses that name instead of
  taking a suffix. To make a crash after the record was written resumable, a sweep now counts as
  finished in step 2 only when its record's `state` is `accepted`; a `proposed` record for the
  current manifest means RESUME.
- **MEDIUM-3 — fixed.** The move-aside is no longer a separate command. Step 2's classification
  command moves earlier files only after it has classified the invocation NEW, and exits before
  the move on RESUME.
- **LOW (unused manifest rebuilt) — accepted.** A manifest with no stamped output cannot be told
  apart from one an abandoned earlier sweep left behind. Rebuilding costs one corpus build, and the
  old manifest is moved aside, not lost.
- **LOW (nested fence) — fixed.** The extraction command exits with an error when a section has no
  fenced block or when the extracted text contains a fence line, instead of printing a shortened
  prompt.

Fixtures, run from the scratchpad with each snippet taken from the regenerated `SKILL.md`:

```text
step2 a  no manifest                                  -> NEW: no manifest
step2 b  earlier unstamped set                        -> NEW, 3 files moved to previous-2026-09-23/
step2 c  HIGH: 3 bad records + stamped report         -> 3 x UNREADABLE (KeyError, JSONDecodeError,
                                                         TypeError), RESUME, nothing moved
step2 d  MEDIUM-3: stamped report + proposed record   -> RESUME, record listed, nothing moved
step2 e  stamped report + accepted record             -> NEW, moved
name  f  nothing present                              -> idea-partition-2026-09-23
name  g  earlier sweep's pair at the date             -> -2
name  h  MEDIUM-2: this sweep's orphaned .md          -> CONTINUE, same name
name  i  earlier at base, own record at -2            -> CONTINUE -2
name  j  unreadable record alone at base              -> -2, no crash
check k  valid pair with a decline candidate          -> 0 problem(s), exit 0
check l  MEDIUM-1: candidate 000999, unplaced         -> FAIL not in a group or unbatched,
                                                         FAIL not in the markdown, exit 1
check m  candidate in both tiers                      -> FAIL decline candidate listed twice, exit 1
check n  markdown without the run stamp               -> FAIL, exit 1
extract o  R1, R4 against PROMPT-034 117-178, 193-251 -> identical, exit 0
extract p  LOW: missing section                       -> "no fenced block found", exit 1
extract q  LOW: nested fence                          -> "holds a nested fence", exit 1
```

The fixture script is `run.py` in the session scratchpad; it is not tracked.

### Review of fix cycle 1, and fix cycle 2

A fresh `demo-adversary` review of `e52f820` judged HIGH, MEDIUM-1, MEDIUM-2, MEDIUM-3 and the
nested-fence LOW **fixed**, and the accepted LOW correctly accepted. It re-ran R1 and R4 against the
pack (identical), and confirmed the generator check and that the two `SKILL.md` files are identical.
It raised one new finding:

- **MEDIUM (new) — fixed in cycle 2.** Step 5's `ours()` ignored the record's `state`, so a pair
  already `accepted` at GATE 3 for the same seed was reported as `CONTINUE` and would be rewritten
  if step 5 were re-entered without step 2. `ours()` now returns false for any pair whose record is
  `accepted`, and the text says an accepted pair is never continued. Fixtures added, with all
  earlier cases re-run unchanged:

  ```text
  name r  accepted pair for this seed, stamped .md      -> -2, no CONTINUE
  name s  accepted pair at base, own draft at -2        -> CONTINUE -2
  ```

This was the second of the two fix cycles the overnight authority allows.

A second fresh `demo-adversary` review of `9b5165b` judged the new MEDIUM **fixed**. It ran the
extracted naming snippet against eight fixtures, including an accepted pair for the current seed
(suffixed to `-2`), an accepted pair beside this sweep's own draft (`CONTINUE -2`), and a record
that is a JSON list or string (no crash). It found step 2, step 5 and GATE 3 consistent on what
`accepted` means, the adapters current and identical, and the diff inside the declared
deliverables. **No finding survived.**

### Review of the read-only analyst change (option C, 2026-09-23)

A fresh `demo-adversary` review of `d50b54b` (skill dispatch) and `7fe932b` (the
`partition-analyst` agent file) against `origin/dev` checked six constraints and found **no
blocker, major or minor finding**:

- The agent file's body says nothing about findings, other analysts or a control, so R4's context
  stays clean.
- It adds no analysis instructions; it covers only how the report is returned and how a large
  file is read.
- `tools: Read, Grep, Glob` leaves no write route. `.mcp.json` configures only Playwright, and in
  this repository an agent gets an MCP tool only by listing it. The review relies on Claude Code's
  frontmatter semantics and the repository's existing read-only agents here; it did not dispatch
  a live agent. The R1 re-run exercises this.
- `corpus-R1.md` is 14,882 lines, about eight ranged reads; `maxTurns: 60` leaves room.
- The skill names `partition-analyst` consistently. The only remaining "general-purpose agent"
  text for R1 and R4 is in `PROMPT-034`, which is unchanged by ruling. The adapters are current and
  identical.
- The frontmatter matches the other hand-written agent files.

Two notes, accepted without change: the fix is built but not yet exercised end to end, which is
the R1 re-run's job; and the commit message's "option A" means the follow-up question's option,
not the `## Unresolved` question's option A. The Decisions section above names both.

## Resume state (2026-09-23, after the read-only analyst merge)

- **Merged:** option C's fix reached dev at `6807dcc` through an owner-approved `GRANTED merge`:
  `.claude/agents/partition-analyst.md` (Read, Grep, Glob) and the skill dispatching R1 and R4 to
  it. The claim is still active, held by `agent-builder-b`; the phase is not complete.
- **Agent type loading.** Right after the merge, a probe dispatch from the session that built the
  fix returned "Agent type 'partition-analyst' not found". A few minutes later the harness listed
  `partition-analyst` as available in that same session, so the type is picked up after it lands
  in the primary checkout, with a delay, not only at session start. Before dispatching, confirm
  `partition-analyst` is in the available agent types. Never fall back to a general-purpose agent:
  that is the dispatch the ruling replaced.
- **Open-set gate, ruled by the owner: a fresh sweep, not the resume.** 11 ideas were open
  (`000357`-`000367`), with about 37 more being recorded. The owner ruled that they are triaged
  first and a new sweep runs on a fresh corpus, with both analysts on `partition-analyst`. The
  earlier plan (RESUME, R1 alone) is superseded.
- **Primary checkout `_working/idea-corpus/`** (gitignored), last night's sweep (seed `656057328`,
  325 ideas): `manifest.json`, `corpus-R1.md`..`corpus-R4.md`, `dispatch-R1.txt`,
  `dispatch-R4.txt`, the stamped `report-R4.md` (it opens with R4's own note that its Write was
  refused; R4 returned text and did not go around the refusal), R1's self-written `report-R1.md`
  and `condensed.md`, and `previous-2026-09-13/`.
- **Next steps**, after the restart the owner ordered for the wind-down:
  1. **Triage first.** Ideation triages every open idea, so the open-set gate prints `open ideas: 0`.
     Do not start until it does.
  2. **Move last night's sweep aside by hand**, inside a granted `TURN? dryrun phase-part-03`: every
     file listed above except `previous-2026-09-13/` goes into
     `_working/idea-corpus/previous-2026-09-23-seed-656057328/`. Move, never delete; keep them for
     comparison. This has to be done by hand: with `report-R4.md` stamped for the current manifest,
     the skill's step 2 would classify the invocation RESUME and move nothing, and its patterns do
     not cover `condensed.md`.
  3. **Run `/partition-ideas` as a NEW sweep.** Step 1 prints `open ideas: 0`; step 2 prints `NEW: no
     manifest` and builds a fresh corpus. Dispatch R1 and R4 in the same turn, both to
     `partition-analyst`, save `dispatch-R1.txt` and `dispatch-R4.txt`, and write both returned
     reports with the run stamp. Stop at GATE 1.
  4. **Record here:** the open-set output; the manifest's size, status and seed; both dispatch
     diffs against `PROMPT-034` (lines 117-178 and 193-251); each report's size and whether every
     corpus id is placed (the practical check on the 1M window); that no analyst wrote a file (list
     `_working/idea-corpus/` before and after) and that `_data/ideas.jsonl` is unchanged by the
     sweep (hash it after triage and again after GATE 1).
  5. Run `/session-close` through its independent review, send READY for the record and the
     completion edit, then copy any gitignored evidence out, remove the worktree, and send SAFE.
- **Claim:** `agent-builder-b` keeps the `phase-part-03` claim across the restart.
- `phase-irs-05` and the batch-002 close-out wait for this phase to complete.
