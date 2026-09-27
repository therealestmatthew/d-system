---
name: partition-ideas
description: Run a partition sweep over the idea log — build the corpus, dispatch the partition pack's two analysts and two audits verbatim, synthesize one partition, and stop for the owner at every gate. Use when someone asks to partition, batch or group the parked ideas into plans. Moves no idea status and writes nothing to the idea log.
---

# Partition the ideas

This skill is a runner, not an author. Every prompt it dispatches is a fenced block from the
plugin's partition pack (`${CLAUDE_PLUGIN_ROOT}/docs/partition-pack.md`), extracted and filled by
`idea_corpus.py prompt` and sent **verbatim**; nothing below is a brief.

**What this skill never does.** It writes nothing to the idea log: no status event, no
annotation, no link, including for a decline candidate. It marks no backlog phase complete. It
reaches no owner decision on its own: the partition, and every decline candidate, is ruled on by
the owner at a gate, and the skill stops at each gate rather than proceeding on a default.

Every `idea_corpus.py` command below starts with the same six option assignments, so the
person's saved plugin options reach the script. Run each from the current checkout's top level,
assignments included. An option the person never saved appears as its `${user_config.…}` text;
the script treats that as unset and uses the documented default.

## Where things live

Two properties of the harness shape every step.

- **Subagents cannot write report files.** Both analysts go to
  `idea-realization:partition-analyst`, whose only tools are Read, Grep and Glob, and both audits
  go to `idea-realization:partition-adversary`, which never edits a file. Each returns its report
  as text, and **you write it** with `idea_corpus.py report`. Never ask a subagent to write.
- **Subagents run in the primary checkout, whatever your worktree.** So the corpus, the
  dispatches, the reports and the synthesis draft all live in the **primary checkout's**
  staging directory (`staging_dir`), and every pack section is filled with absolute paths
  there. The primary checkout is the first entry of `git worktree list`; `idea_corpus.py`
  resolves it itself.

Writing into the primary checkout is held to three conditions, and `locate` checks the first
two:

1. **The staging directory is gitignored there.** `locate` exits 1 when `git check-ignore`
   does not accept it, and every writing subcommand refuses to write. If `locate` refuses,
   **stop before writing anything** and tell the person: the scaffold skill's `partition`
   feature offers the ignore rule, or `staging_dir` can name a directory that is ignored.
2. **The primary checkout's `git status` is unchanged.** `locate` prints `primary_status`, a
   digest of `git status --porcelain` there. Note it now; run `locate` again at every gate and
   at the end, and if the digest has changed, stop and report which files changed.
3. **Any turn the repository's coordination protocol requires is held first.** If the
   repository's working agreement requires a grant, a lock or a turn before anything writes in
   the primary checkout, hold it before the first write below (step 2), and for as long as the
   sweep writes there.

The staging directory never travels to a worktree, and neither a merge nor removing a worktree
carries it. The accepted partition leaves it through `accept` at GATE 3.

**Every file written into the corpus directory, and the draft markdown, starts with a run
stamp** naming the corpus build it belongs to. `locate` prints it once the corpus exists. The
stamp is how a later invocation tells this sweep's output from an earlier sweep's file at the
same path.

## 0. Preflight, location and estimate

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/check.py" --feature ideas

CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_STAGING_DIR='${user_config.staging_dir}' \
CLAUDE_PLUGIN_OPTION_PARTITIONS_DIR='${user_config.partitions_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea_corpus.py" locate

date -u +%Y-%m-%dT%H:%M:%SZ
```

Stop if the check fails or `locate` refuses. Show the person the `locate` output. Record the
start time, and **state a wall-clock estimate for the sweep before dispatching anything**; the
closing spend posture reports against it.

Keep a running count from here on: dispatches run, dispatches resumed after truncation, and any
dispatch that ran on a model above sonnet.

## 1. The open-set gate

Before anything is built or dispatched:

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" list --status open
```

Print the whole output to the person.

- **No open ideas:** say so in one line ("the open set was empty") and continue.
- **Open ideas:** **stop.** Ask the owner whether to triage them first (the sweep ends here; the
  idea-triage skill does it) or to partition without them (continue). Do not choose for them.
  Record the ruling and the ids for the closing report.

## 2. Resume or start, then the corpus

This is the first write into the primary checkout: hold any turn condition 3 requires.

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_STAGING_DIR='${user_config.staging_dir}' \
CLAUDE_PLUGIN_OPTION_PARTITIONS_DIR='${user_config.partitions_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea_corpus.py" start
```

`start` decides by inspection whether this invocation resumes a sweep or starts one, and moves an
earlier sweep's files aside **only** when it has classified the invocation NEW, so a sweep in
progress is never moved. Show every line it prints, including any `UNREADABLE` record. A sweep
counts as finished only once a record carrying its seed is `accepted` (GATE 3).

**RESUME**: do not rebuild the corpus; rebuilding would replace the manifest and orphan every
stamped report. Report the files already done, and any record of this sweep, then carry on from
the first step whose output is missing. Each step below also checks for its own output first.

**NEW**: `start` has moved every earlier `manifest.json`, `corpus-*.md`, `report-*.md`,
`audit-*.md` and `dispatch-*.txt` into `previous-<that file's modification date>/`. It moves and
never deletes, and never overwrites. Report the moves, then build the corpus. The status filter
defaults to `triaged`; add `--status <status>[,<status>…]` only when the request names another
selection, and `--exclude <file>` only when the person names a file of ids to leave out:

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_STAGING_DIR='${user_config.staging_dir}' \
CLAUDE_PLUGIN_OPTION_PARTITIONS_DIR='${user_config.partitions_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea_corpus.py" build
```

Then, in either case, run `locate` again and take from it the corpus size, status selection,
seed, **corpus date** and run stamp. The pack names no corpus size of its own, and neither does
this skill.

## How every dispatch below is made

1. **Check for this step's output first.** If its report exists in the corpus directory and
   starts with this sweep's run stamp, report that it already exists and dispatch nothing.
2. **Extract, fill and save the section** — never retype it. `<SECTION>` is `R1`, `R4`, `A1` or
   `A2`:

   ```bash
   CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
   CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
   CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
   CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
   CLAUDE_PLUGIN_OPTION_STAGING_DIR='${user_config.staging_dir}' \
   CLAUDE_PLUGIN_OPTION_PARTITIONS_DIR='${user_config.partitions_dir}' \
   uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea_corpus.py" prompt <SECTION>
   ```

   It prints the section with every placeholder replaced by an absolute path, and saves exactly
   that text as `dispatch-<SECTION>.txt` in the corpus directory, so the dispatch can be diffed
   against the pack afterwards.
3. **Dispatch that text, and only that text, as the whole prompt.** `R1` and `R4` go to
   `idea-realization:partition-analyst`; `A1` and `A2` go to
   `idea-realization:partition-adversary`; model sonnet for all four. Never escalate the model on
   your own.
4. **Truncation.** If the returned report is cut off (it stops mid-section, or lacks a section
   its block requires), resume that same agent and ask it to continue from where it stopped.
   Never re-run it from scratch. Count the resume.
5. **Write the report.** Save the agent's returned text, verbatim, to a scratch file outside
   the repository, then:

   ```bash
   CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
   CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
   CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
   CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
   CLAUDE_PLUGIN_OPTION_STAGING_DIR='${user_config.staging_dir}' \
   CLAUDE_PLUGIN_OPTION_PARTITIONS_DIR='${user_config.partitions_dir}' \
   uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea_corpus.py" report <SECTION> --file <scratch file>
   ```

   It writes the run stamp and then the text to the file the pack names (`report-R1.md`,
   `report-R4.md`, `audit-1-findings.md`, `audit-2-findings.md`), and refuses to replace one this
   sweep already wrote.

## 3. The analysts — `R1` and `R4`, concurrently

Dispatch `R1` (the finding-reading analyst) and `R4` (the control) **in the same turn**, so they
run concurrently. Neither sees the other's output. `R4` is sent its own section exactly as
printed: it is never told it is a control, that findings exist, or that another analyst is
running.

## GATE 1 — after the analyst reports land

**Stop.** Report: the corpus size, status selection and seed; the open-set ruling from step 1;
each report's path and size; which reports were written now and which already existed; and the
`primary_status` comparison. Ask whether to continue to audit 1. Do not continue without the
owner's yes.

## 4. Audit 1 — `A1`

Dispatch `A1` as in *How every dispatch below is made*, and write `audit-1-findings.md`.

## GATE 2 — after audit 1 returns

**Stop.** Show the owner audit 1's ranked findings and ask whether to proceed to synthesis. Do not
continue without the owner's yes.

## 5. Synthesis — `S`, in this session

`S` is not a dispatch. Name the draft first, from the corpus date `locate` printed (not today's
date):

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_STAGING_DIR='${user_config.staging_dir}' \
CLAUDE_PLUGIN_OPTION_PARTITIONS_DIR='${user_config.partitions_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea_corpus.py" name <corpus date>
```

It prints the draft's markdown path and record path, both absolute, in the primary checkout's
staging directory. A name that an earlier partition holds, in the staging directory or among the
accepted partitions, is suffixed rather than reused; an earlier partition is never edited. If it
prints `CONTINUE`, the draft there is this sweep's own, left by an interrupted synthesis: tell
the owner, then rewrite that draft and its record in full.

Then extract `S` with `prompt S --draft <the markdown path>` (same assignments) and follow it
yourself, in this session, as written. Write both files at the paths `name` printed:

- **The markdown** starts with the run stamp as its first line, then carries what `S` requires —
  both levels, the six-field batch record for every group, the unbatched section, the two
  decline tiers and the completeness arithmetic — and records its corpus size, status filter and
  seed near the top. Name each track (programme) and each fine group exactly as the record names
  it.
- **The record** is the same partition as JSON, per
  `${CLAUDE_PLUGIN_ROOT}/schemas/idea-partition-record.schema.json`: `corpus_date`; `markdown`, the
  markdown's path relative to the primary checkout's top level; the manifest's `corpus_size`,
  `status` and `shuffle_seed`; `state: proposed`; every track with its fine groups and member
  ids; the unbatched ideas with reasons; and both decline tiers. A track's `disposition` stays
  `null` unless the owner rules one; the pack asks for none.

**Check the pair before going on.** This validates the record, checks it against the corpus
arithmetically, and checks that the markdown carries the same tracks, groups and ids:

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_STAGING_DIR='${user_config.staging_dir}' \
CLAUDE_PLUGIN_OPTION_PARTITIONS_DIR='${user_config.partitions_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea_corpus.py" check <markdown path> <record path>
```

A failure is fixed in the document or the record, and the check re-run. Do not go on with it red.

## 6. Audit 2 — `A2`

The draft is already where the adversary can read it: in the primary checkout's staging
directory, at an absolute path built from the first entry of `git worktree list`. Extract `A2`
with that absolute markdown path, as `name` printed it:

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_STAGING_DIR='${user_config.staging_dir}' \
CLAUDE_PLUGIN_OPTION_PARTITIONS_DIR='${user_config.partitions_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea_corpus.py" prompt A2 --draft <markdown path>
```

`prompt` refuses a draft that is not in the primary checkout's staging directory or does not
exist yet. Dispatch the printed text to `idea-realization:partition-adversary`, model sonnet, as in
*How every dispatch below is made*, and write `audit-2-findings.md`. This step does not stop for
a ruling of its own; the next stop is GATE 3.

## 7. The gate checklist — `G`

Extract `G` with `prompt G` (same assignments) and run its checklist yourself, recording real
output. The coverage item is the step 5 check, run again. The check-command item is the command
printed in the section. The idea-log item compares the idea log with its state at the start of
the sweep: `git diff --quiet <start commit> -- <idea log>` in the current checkout, and the
`primary_status` digest from `locate` against the one noted in step 0.

## GATE 3 — the owner's ruling

**Stop.** Present the partition, audit 2's findings and the checklist. The owner accepts or
corrects the partition, and rules on **every decline candidate individually**. Apply their
corrections to both the markdown and the record in the staging directory, and re-run the step 5
check.

Only on the owner's explicit acceptance:

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_STAGING_DIR='${user_config.staging_dir}' \
CLAUDE_PLUGIN_OPTION_PARTITIONS_DIR='${user_config.partitions_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea_corpus.py" accept <markdown path> <record path>
```

`accept` re-runs the check, copies the pair into the partitions directory (`partitions_dir`) in
the current checkout, sets the copy's `state` to `accepted` and points its `markdown` at the copy.
An earlier partition there is never overwritten. The copy is an ordinary new file in the current
checkout; committing it follows the repository's own rules. A decline ruling changes no idea's
status here; recording it in the idea log is a separate, owner-directed action with the idea
skill.

## Closing — the spend posture

Every time this skill stops — at a gate, at the open-set gate, at a refusal, or at the end —
close with the spend posture:

- dispatches run;
- dispatches resumed after truncation;
- any dispatch that ran above sonnet (there should be none);
- wall-clock so far against the estimate stated in step 0.
