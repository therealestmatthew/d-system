---
name: checkpoint
description: Record observed progress on the active backlog phase in its session record and backlog entry, without ever marking the phase complete; safe to repeat against unchanged state. Use mid-session to record where the work stands, before handing off, or when asked to checkpoint.
---

# Checkpoint

Records what has actually happened, leaves the tree honest, and stops. It never decides a session
is over: that judgement, and the transition to complete, belong only to the `session-close` skill.
Checkpointing mid-work is the ordinary case; most runs find acceptance unmet and record that
plainly.

## What this skill must never do

- **It never sets a phase's status to complete.** It leaves a phase `queued` or `active` only.
  Writing `status: complete` here is forbidden in every case, including when every condition looks
  met; only `session-close` may, after its own review.
- **It never runs `git worktree`, `git rebase`, or anything touching a remote.** It edits files in
  the working tree it is run from and nothing else.
- **It never touches a backlog line, session record or `next_up` entry belonging to a phase it is
  not working.** A peer's claim is a peer's claim.

## The values it uses

Backlog and document commands carry the person's saved options. An option never saved appears as
its `${user_config.…}` text; the scripts treat that as unset and use the documented default.

```bash
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/paths.py"
```

prints `backlog_path` — **the backlog** — and `docs_root` — **the document root**.

## The session record

One `kind: session` document per session, under the document root, in the location the code
register (`codes.yaml`) gives the session series. This skill defines its shape; `session-close`
extends it without redefining it.

Front matter:

```yaml
schema_version: 1
id: doc-session-<slug>           # permanent, independent of the code
code: <from next-code session>   # the dated code; its date equals `created`
title: <human title for this session>
kind: session
status: active                   # the status a session record keeps
owner: <an owner key from systems.yaml>
created: '<today>'
updated: '<today>'
systems: [...]                   # the systems this session actually touched
depends_on: [...]                # the plan(s) this session advances
```

`depends_on: []` is correct for an unclaimed session whose work advances no plan.

Body sections, in this fixed order. **Every run regenerates sections 2 to 6 from the state
observed at run time.** It never appends a block per run and keeps no log of past runs, which is
what makes a run against unchanged state produce no diff.

1. `# <title>`, matching the front matter.
2. `## Phase` — one line per phase this record covers: its id and title.
3. `## Verification` — for each runnable command in the phase's `verification` list, the literal
   command and the literal output produced just now; for a check written as prose, one line saying
   what was done and observed. Never paraphrase a failure into a pass.
4. `## Acceptance` — one line per `acceptance` entry: `Met` or `Not met`, with a short reason that
   points at the evidence in `## Verification`.
5. `## Backlog` — the phase's `status`, `next_action`, and any evidence, exactly as written to the
   backlog this run.
6. `## Unresolved` — anything real left open, or `None.` when that is honestly true.

## Sessions with no claimed phase

Owner-directed work with no phase still gets a record, with all six sections in the same order:

- `## Phase`: `Unclaimed — owner-directed work, no backlog phase.` and the branch or worktree slug
  with the owner's instruction restated in one sentence, written once and reused verbatim on every
  later run. Never write a phase id you do not hold.
- `## Verification`: the repository-wide gates, in this order — the plugin check (below) and the
  repository's own test command — plus any command the owner's instruction named. Nothing else.
- `## Acceptance`: opens with `Self-declared from the owner's instruction; no backlog acceptance
  list exists for this session.` then the ask restated as checkable conditions, written once and
  reused verbatim.
- `## Backlog`: `Unclaimed — no backlog phase was claimed for this session; no line of the backlog
  was changed.`

Before taking this branch, re-read the backlog for a phase that is `active` with your agent id. If
the work should have had a claim, say so under `## Unresolved`; never invent one after the fact.

## Running it

1. **Identify the phase**: the one entry in the backlog with `status: active` and your agent id. If
   more than one is plausible, ask which. If none, this is an unclaimed session; steps 5 and 6 then
   do not apply, and the report says so.
2. **Find or create the record.** Search the session location for a record whose `## Phase` names
   this phase (or this session's slug) and whose code carries today's date; if one exists, edit it
   in place, never create a second. Otherwise allocate a code:

   ```bash
   CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
   CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
   CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
   uv run "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" next-code session
   ```

   and name the file `<code>-<topic>.md`.
3. **Run verification** in the working tree you are in, and write the real output into
   `## Verification`. Strip only run-specific noise — timings, temporary paths, process ids — so a
   rerun against unchanged state produces identical text; never strip a count, an error or an exit
   code.
4. **Judge acceptance** one condition at a time from what `## Verification` shows and a direct look
   at the deliverables. Never mark something met because the scope says it should be by now.
5. **Update this phase's backlog lines only.** Keep `status: active`, or return it to `queued` if
   the phase is being handed off unfinished with nobody continuing it. Update `next_action` to name
   exactly what remains. While the phase is `active` or `blocked`, `session`, `completion_evidence`
   (files that exist now) and `result` (actual progress, not a completion claim) may be recorded.
   Returning the phase to `queued` releases the claim: clear `agent`, `session`,
   `completion_evidence` and `result` in the same edit. Mirror the same facts into `## Backlog`.
6. **Prune `next_up`** of any phase that is now genuinely complete, and nothing else.
7. **Regenerate the catalog** and run the check:

   ```bash
   CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
   CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
   CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
   uv run "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" catalog

   CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
   CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
   CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
   CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
   uv run "${CLAUDE_PLUGIN_ROOT}/scripts/check.py"
   ```

   If the check fails, fix the cause before finishing; never hand back a failing tree with a
   record describing it as fine.
8. **Report** the record's code, whether backlog fields changed, whether `next_up` was pruned, and
   the acceptance verdicts from step 4, and nothing more than the steps produced.
