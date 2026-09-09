# `_tmpagent/` — shared files for agents across worktrees

This directory is **tracked in git**. That is its entire reason to exist: an ignored file does not
reach a worktree, so anything an agent in `../d-system-worktrees/` needs to read must be committed.
`_working/` is the opposite — gitignored, local to the primary checkout, and the owner's material.
See [PLAN-015](../docs/01-plans/PLAN-015-ephemeral-working-plans.md).

Nothing here is scanned by governance. `src/governance/__main__.py` walks `docs/` and `brain/` only,
so files here need no code, no front matter and no catalog entry.

**This contract is enforced by convention, not by a check.** No test reads `claims.jsonl` and no
validator fails on it. That is a deliberate choice while the directory is small, and it means the
ledger is only as good as the agents writing to it. If it starts drifting from reality, the fix is a
check, not a stricter rule.

## The rules

1. **A file here is read-only once it is active.** Create it, edit it freely while it is still
   `draft`, then flip it to `active` before anyone else reads it. After that its content is frozen.
   If an active file must change, create a successor and name the file it replaces in the new
   `created` line's `purpose`.

   Git does not track the write bit, so this cannot be a file permission — a `chmod -w` is lost on
   the next clone. It is a promise, and `claims.jsonl` is where the promise is recorded.

2. **Every reader claims, and every claim is closed explicitly.** A claim names *where* the file is
   being used, not just who is using it, so a claim nobody closed can still be investigated. Plan
   dependencies are claimed and released the same way as branches — a plan reaching `complete` is
   not the only way a claim ends, and deriving it would leave the other paths permanently open.

3. **A file is eligible for deletion only when every claim on it is closed.** Eligibility is
   derived, never written: latest status is `active`, and every `claimed` has a later matching
   `released`. Deleting the file is a separate act that writes a `removed` line saying why.

4. **Never delete a file with an open claim**, and never close another agent's claim to make a file
   eligible. If a claim looks abandoned, check whether its branch still exists — see below.

## `claims.jsonl`

One append-only JSONL ledger for the whole directory, one JSON object per line, newest last. It
mirrors `_data/ideas.jsonl` deliberately: append only, never edited, never reordered, and current
state is folded by replaying it in order.

| Field | On | Meaning |
|---|---|---|
| `file` | every line | Filename within `_tmpagent/`. The line's subject |
| `event` | every line | `created`, `activated`, `claimed`, `released`, `removed` |
| `at` | every line | RFC 3339 with a mandatory offset, e.g. `2026-09-07T00:31:04-04:00` |
| `by` | every line | Who wrote the line — `repository-owner`, or the agent name |
| `branch` | every line | Where the line was written from. `dev`, or `agent/phase-xxx-nn` |
| `purpose` | `created` | One line on why the file exists, and what it replaces if anything |
| `kind` | `claimed`, `released` | `branch` or `plan` |
| `ref` | `claimed`, `released` | The branch name, or the plan's document ID |
| `reason` | `removed` | Why it went, and where it went if it was kept |

A claim is addressed by `(file, kind, ref)` — a given branch or plan holds at most one open claim on
a file at a time, so a `released` line matches its `claimed` line by those three fields and needs no
identifier of its own. Claiming again after releasing is legal; replay in order and the last event
for a triple wins.

### Worked sequence

```
{"file":"extraction-notes.md","event":"created","at":"2026-09-07T09:00:00-04:00","by":"agent-slate","branch":"dev","purpose":"Step detail for phase-scope-01; too task-specific to govern"}
{"file":"extraction-notes.md","event":"activated","at":"2026-09-07T09:20:00-04:00","by":"agent-slate","branch":"dev"}
{"file":"extraction-notes.md","event":"claimed","at":"2026-09-07T09:21:00-04:00","by":"agent-slate","branch":"dev","kind":"plan","ref":"doc-ephemeral-working-plans"}
{"file":"extraction-notes.md","event":"claimed","at":"2026-09-07T09:22:00-04:00","by":"agent-slate","branch":"agent/phase-scope-01","kind":"branch","ref":"agent/phase-scope-01"}
{"file":"extraction-notes.md","event":"released","at":"2026-09-07T17:40:00-04:00","by":"agent-slate","branch":"agent/phase-scope-01","kind":"branch","ref":"agent/phase-scope-01"}
{"file":"extraction-notes.md","event":"released","at":"2026-09-08T11:05:00-04:00","by":"repository-owner","branch":"dev","kind":"plan","ref":"doc-ephemeral-working-plans"}
{"file":"extraction-notes.md","event":"removed","at":"2026-09-08T11:06:00-04:00","by":"repository-owner","branch":"dev","reason":"phase-scope-01 complete; nothing in it outlived the task"}
```

The `claimed` line for the branch is written **from** that branch, which is why `by` and `branch`
carry different information and both are required.

## Checking the ledger

There is no command for this yet. Read `claims.jsonl` and fold it in order.

**Is this file eligible for deletion?** Its latest status event is `activated`, and every
`(file, kind, ref)` triple with a `claimed` has a later `released`. If so, delete it and append
`removed`. If not, the open triples are your answer for why not.

**Is a claim abandoned?** Check whether its branch still exists:

```bash
git branch --list 'agent/*'
git worktree list
```

A `branch` claim whose branch is gone is stale — the work it belonged to was merged or abandoned, and
nothing is reading the file from there any more. That is a strong signal but not permission: close it
deliberately with a `released` line naming yourself, or ask the owner. A `plan` claim outlives
branches by design; check the plan's status in
[the catalog](../docs/08-governance/catalog.md) instead.

**What does this branch still hold?** Filter for `kind: "branch"` with your branch as `ref`, and
release every open one before you finish. An agent that ends a session without releasing its claims
leaves files that nobody can clean up without investigating.
