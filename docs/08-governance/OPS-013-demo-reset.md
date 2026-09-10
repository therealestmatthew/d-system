---
schema_version: 1
id: doc-ops-demo-reset
code: OPS-013
title: Prepare and restore the demo stage
kind: operation
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-demo-stage]
depends_on: [doc-governance-operations]
---

# Prepare and restore the demo stage

## Trigger

Run before a rehearsal or the live demo session to prepare the stage, and run during or immediately
after the session when any fallback action is invoked.

## Context

The demo stage page shows a generated overview of the repository state, built from deterministic
scripts run over real data in the idea log, backlog, and systems registry. The stage also shows an
embedded terminal, talking-points rotator, and an embedded overview panel. Before any rehearsal or
live run:

- The overview must be regenerated fresh from current data.
- Demo scratch state must be cleared so any artifacts left by prior runs do not interfere.
- The pre-built overview skill must be parked so the live segment can rebuild it from scratch.
- The fallback audience idea must be seeded if not already present, so the live rebuild always has
  an idea to triage even if the audience does not supply one.

After the demo, or when a fallback action is invoked during the live segment, the pre-built skill
is restored and the overview is regenerated from current data.

## Command

```bash
uv run python tools/demo_reset.py prepare   # set the stage before rehearsal or live demo
uv run python tools/demo_reset.py restore   # restore fallback state during or after session
```

## Expected result

### `prepare`

- `_public/overview/index.html` is regenerated from current data.
- `_public/demo-scratch/` is cleared and recreated empty.
- `.claude/skills/d-system-overview/` is moved to `.claude/skills/_parked/d-system-overview/`.
- The fallback audience idea is appended to `_data/ideas.jsonl` unless an idea with the exact title
  "Demo fallback: audience idea seeded by tools/demo_reset.py" already exists in the folded state.
- A report is printed naming the overview path and the status of each operation.

### `restore`

- `.claude/skills/_parked/d-system-overview/` is moved back to `.claude/skills/d-system-overview/`.
- `_public/overview/index.html` is regenerated from current data.
- A report is printed with the skill's restoration status and the overview path.

Both commands are idempotent: a second consecutive run of the same command reports what is already
in place rather than erroring. The pre-built skill restores; the overview page always regenerates
forward from current data (the idea log is append-only, so page bytes will differ if ideas were
recorded since the last regeneration).

## Hard limits

The tool enforces these boundaries in code, not left as comments:

- It may never create, move or delete anything inside `_data/ideas.jsonl`, any path under `docs/`,
  `_private/`, `.agents/`, `.codex/`, or the files `AGENTS.md` or `CLAUDE.md`.
- It may only create, move or delete paths inside its own allowed list: `.claude/skills/d-system-overview/`,
  `.claude/skills/_parked/d-system-overview/`, `_public/demo-scratch/`, and `_public/overview/`.
- The only way it appends to the idea log is through `tools/append_idea.py`'s sanctioned `add()` function.

## Failure and recovery

- `tools/generate_overview.py failed: <detail>` means the overview generation subprocess failed.
  Run it directly to see the error: `uv run python tools/generate_overview.py --out _public/overview/index.html`.
- `refusing to touch <path> — inside or containing the hard-forbidden path` means the tool blocked
  an unsafe filesystem operation at its guard check. Do not run the tool differently. Report this
  as a bug.
- `refusing to touch <path> — outside tools/demo_reset.py's allowlist` means the tool is not
  permitted to touch the named path. Do not work around this boundary.
- Ambiguous park state (both the skill and parked skill exist, or neither exists) must be resolved
  by hand before running the tool again.

<!-- generated:tool-reference:start -->

### Reference: `tools/demo_reset.py`

Prepare and restore the demo stage around a rehearsal or the live run (`PROMPT-017`).

Two explicit subcommands, both idempotent on a second consecutive run:

    uv run python tools/demo_reset.py prepare
    uv run python tools/demo_reset.py restore

`prepare` sets the stage: it regenerates the overview outputs (`tools/generate_overview.py`),
clears the demo scratch directory this tool owns (`_public/demo-scratch/` — see "What
`prepare` clears" below), PARKS the pre-built overview skill
(`.claude/skills/d-system-overview/` moves to `.claude/skills/_parked/d-system-overview/`, a
location this tool owns), and SEEDS the fallback audience idea through
`tools/append_idea.py`'s sanctioned `add()` — but only if an idea carrying the fallback seed's
exact title is not already present in the folded idea state, so a second `prepare` seeds no
duplicate.

`restore` is the fallback and post-segment action the runbook invokes by name: it puts the
parked pre-built skill back in place and regenerates the overview outputs from current data.
A second `restore` finds the skill already in place and reports that rather than erroring.

**Contract: "pre-built state" means the pre-built SKILL is back in place.** The overview page
is always regenerated from current data, which grows as ideas are appended — the idea log is
append-only, so byte-identical pre-rehearsal page output is deliberately NOT the contract
(PLAN-021's afterlife decision keeps demo-recorded ideas as real work, and the page reflecting
them is intended behavior). `restore` never claims to reproduce pre-rehearsal page bytes.

**What `prepare` clears.** `_public/demo-scratch/` is the one directory this tool treats as
demo scratch state: reserved for ephemeral artifacts a rehearsal or the live run might drop
(nothing else in the repository writes there today, which is deliberate — it exists so a
future demo-run artifact has one tool-owned location guaranteed to start clean, rather than
`prepare`'s scratch-clearing step being a promise nothing checks). `prepare` removes it and
recreates it empty every run.

**Hard limits, enforced in code, not left as a comment.** Every filesystem create, move or
delete this tool performs passes through `_guard()`, which refuses a path inside
`_data/ideas.jsonl`, anything under `docs/`, `_private/`, `.agents/`, `.codex/`, `AGENTS.md` or
`CLAUDE.md` — even if it would otherwise fall inside this run's allowlist — and separately
refuses any path outside the allowlist the caller supplies. The only idea-log access this tool
ever makes is appending through `tools/append_idea.py`'s `add()`; it never opens
`_data/ideas.jsonl` for writing itself, and never rewrites or deletes a line already there.

No CLI arguments.

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
