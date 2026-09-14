---
schema_version: 1
id: doc-repeatable-idea-partition-requirements
code: REQ-009
title: Repeatable idea-partition requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-portfolio, sys-backlog, sys-governance]
depends_on: [doc-idea-record-system, doc-idea-staging, doc-prompt-pack-protocol, doc-ops-build-idea-corpus]
---

# Repeatable idea-partition requirements

## Observed problem and scope

The idea-batching build ran once, end to end, on 2026-09-12 and 2026-09-13. Four analysts
partitioned the corpus independently, an adversary audited twice, an agent synthesized one
partition, and the owner accepted it at the third gate: 129 ideas into 62 fine groups and 12
programmes, recorded in `docs/00-working/idea-batching-partition.md`.

Nothing about that run is repeatable without rebuilding it by hand. Four problems, each observed
rather than anticipated:

1. **The prompts are build-specific.** The analyst brief, the control brief, both audit briefs, the
   synthesis protocol and the gate exist only inside the idea-batching delegation pack
   ([PROMPT-032](../02-prompts/PROMPT-032-idea-batching-delegation-pack.md)), interleaved with that
   build's pinned corpus size, its section-letter rationale and its per-build owner rulings. The
   synthesis protocol is the worst case: it is the step where the most judgment is applied, and it
   has no home outside a document about one particular run.
2. **No workflow exists.** There is no skill and no command. Re-running means a session reading a
   538-line pack and hand-dispatching from it, which is how a prompt gets paraphrased instead of
   sent verbatim.
3. **The corpus selection is fixed in code.** `tools/build_idea_corpus.py` filters on a module
   constant, `CORPUS_STATUS = "triaged"`. Partitioning any other slice of the idea log requires
   editing the tool.
4. **The corpus decays while the sweep runs.** The corpus is `triaged` ideas only. The open set was
   empty for about twenty minutes on 2026-09-13 and then refilled to 14 ideas, `000208`–`000221`,
   when a peer integrated `phase-lit-05`. A sweep is a snapshot of a set that concurrent sessions
   keep writing to, and the first run had no step that made that visible.

This requirement covers repeating a partition sweep over the idea log: the reusable prompt set, the
corpus selection, the invocable workflow, and what each sweep records. It does not cover turning a
programme into a governed plan — that is the work each accepted programme still needs, and the
partition is input to it.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | Every prompt a sweep dispatches — the analyst brief, the control brief, both audit briefs, the synthesis protocol and the gate — exists in one governed document that names no single build's pinned state. | Read the document for a pinned corpus size, a per-build owner ruling or a kick-off delta; each is a defect. Confirm it carries all six blocks and that governance exits 0 with it present. |
| R02 | A sweep authors no prompt text of its own. Each dispatch is a verbatim fenced block from that document. | Read the workflow body: every dispatch names the pack section it sends and quotes no brief of its own. Run a sweep and compare each dispatched prompt against its pack section character for character. |
| R03 | The corpus status filter is a command-line option, not a source constant. Omitting it selects `triaged`, reproducing current behavior exactly. | Run `build_idea_corpus.py --stats` with no status argument before and after the change and compare output byte for byte. Run it with a different status and confirm the selected ids match a direct `fold()` query for that status. Grep the source for a module-level constant used as the filter. |
| R04 | The manifest records which status or statuses produced the corpus, so a partition document can be traced to the slice it was built from. | Build a corpus under a non-default status and read the manifest for the recorded value; confirm the default run records `triaged` rather than omitting the field. |
| R05 | Before any analyst is dispatched, the sweep reports every `open` idea by id and count, and stops for the owner when that count is not zero. | With at least one open idea, run the sweep and confirm it prints the ids and halts before the first dispatch. With none open, confirm it proceeds and states that the open set was empty. |
| R06 | Each sweep writes a new dated partition document under `docs/00-working/` and modifies no earlier partition document. | Run two sweeps dated differently; confirm two files exist and `git diff` shows the earlier one untouched. Confirm the new document records its own date, corpus size and status filter. |
| R07 | The default sweep is four dispatches — one finding-reading analyst, one no-findings control, and two adversarial audits. The corpus-ordering variation is not run by default, and the document records why. | Read the pack's dispatch table and its record of the ordering result. Run a sweep and count the dispatches actually made. |
| R08 | The control is never told that it is a control, that findings exist, that its input differs from anyone's, or that other analysts are running. | Diff the control brief against the analyst brief and confirm every such reference is absent. Grep the control's corpus file for a findings section, a layered-evidence marker and an author byline. |
| R09 | No agent in a sweep writes to the idea log — no status event, no annotation, no link — including when nominating an idea for decline. | Hash `_data/ideas.jsonl` before and after a full sweep and confirm it is unchanged. Confirm decline nominations appear only in the partition document. |
| R10 | Analyst and audit reports are persisted by the coordinator, not by the dispatched agent, and the sweep states the directory they are written to. | Read the workflow's report-handling step. Run one dispatch and confirm the report file exists, contains the agent's returned text, and was written by the coordinator. |
| R11 | Coverage is verified arithmetically against the manifest, never taken from the partition document's own claim. | Hand the gate a partition document that omits one corpus idea while claiming full coverage, and confirm the gate fails and names the missing id. |
| R12 | A sweep interrupted at a gate resumes without re-dispatching completed stages, and a truncated agent is resumed rather than re-run. | Run to the first gate, abandon the session, re-invoke the workflow, and confirm it reports the existing reports and dispatches only what is missing. |
| R13 | Every sweep closes with its spend posture: dispatches run, dispatches resumed after truncation, any model escalated above sonnet, and wall-clock against the estimate. | Read the closing report of a completed sweep for each of the four figures. |
| R14 | The workflow moves no idea's status, marks no backlog phase complete, and reaches no owner decision on its own. Every ruling — the partition, each decline candidate — is the owner's at a gate. | Enumerate the writes the workflow makes. Confirm three owner gates are present and that the workflow stops at each rather than proceeding on a default. |

## Boundaries and unresolved compatibility

**Ideas, not partitions in general.** The workflow partitions the idea log. The adversary charter
(`.claude/agents/partition-adversary.md`) was deliberately written for any partition — ideas,
backlog phases, plan boundaries — and stays that way; the corpus builder is idea-specific and stays
that way. Partitioning some other set would reuse the adversary and the synthesis protocol, and
would need its own corpus step.

**Two harness constraints bind the design and are not negotiable from inside it.** Subagents cannot
write report files, so the coordinator persists every report (R10). Subagents also inherit the
primary checkout as their working directory regardless of the coordinator's worktree, so corpus and
report paths resolve there rather than in the worktree. Both were observed during the first run and
recorded as `000206`. Neither is worked around; the workflow is built to match them.

**The corpus will keep decaying.** R05 makes the open set visible at the start of a sweep, and R06
dates the output. Neither prevents a peer integrating mid-sweep. A partition is accurate as of its
recorded corpus, and the document says so rather than implying it is current.

**Verification of R02 and R12 is by reading a transcript.** No mechanical check can prove a
dispatched prompt was sent verbatim or that a resumed stage was not re-run, because the dispatch
does not pass through a tracked file. Those two rows are verified by the session record naming the
dispatches it made, which is weaker evidence than a test and is stated as such.
