---
schema_version: 1
id: doc-session-relocate-portfolio
code: SESS-2026-09-08-13
title: Relocate the portfolio and seed a fictional example set
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-portfolio, sys-projection, sys-contracts]
depends_on: [doc-confidentiality-sweep]
---

# Relocate the portfolio and seed a fictional example set

## Phase

`phase-priv-03` — Relocate the portfolio and seed a fictional example set. This record also covers
a follow-up documentation pass: updating every process note that told a reader to create
projects/people/commitments/tasks in `_data/` unconditionally, now that real records live at
`_private/portfolio/` instead.

## Verification

`uv run python -m src.governance` (no environment variable set, fictional set only):

```
Governance OK: 16 systems, 101 documents, 13 memories, 101 backlog phases
```

`uv run python -m src.governance` with `D_SYSTEM_DATA_ROOT=_private/portfolio` (real records):

```
Governance OK: 16 systems, 101 documents, 13 memories, 101 backlog phases
```

`uv run python tools/rebuild_db.py` (no environment variable set):

```
projects: 5 rows
people: 1 rows
tags: 28 rows
commitments: 1 rows
tasks: 3 rows
...
```

`uv run python tools/rebuild_db.py` with `D_SYSTEM_DATA_ROOT=_private/portfolio`:

```
projects: 34 rows
people: 0 rows
tags: 28 rows
commitments: 0 rows
tasks: 0 rows
...
```

`uv run pytest`:

```
357 passed, 2 warnings
```

(Was 386 on `dev` before this phase. The drop is `test_schemas.py::test_every_source_project_validates`,
parametrized over `_data/projects/*.json` — 34 real files became 5 fictional ones, so the same test
now runs 29 fewer times. Nothing else changed in the count.)

## Acceptance

- A clone with no environment variables set validates and rebuilds from the fictional set alone —
  **Met**. Both commands above pass with no `D_SYSTEM_DATA_ROOT` set, reading only the tracked
  `_data/`.
- The owner's real records still rebuild when the data root points at `_private/portfolio/` —
  **Met**. Both commands above pass with `D_SYSTEM_DATA_ROOT=_private/portfolio` set, reading the
  relocated real records.
- The example set contains at least one person and one commitment with tasks, which the tree has
  never had — **Met**. `_data/people/jordan-rivera.json` (1), `_data/commitments/c-1.json` (1),
  `_data/tasks/t-1.json` through `t-3.json` (3), linked by id.

## Backlog

`status: active`, `next_action: Complete.` — every acceptance condition is met and no further work
remains in this phase's own scope; `session-close` decides whether that becomes `status: complete`.
`session: doc-session-relocate-portfolio`. `completion_evidence` now also lists the documentation
follow-up files: `CLAUDE.md`, `README.md`, `brain/concepts/json-source-of-truth-pattern.md`,
`brain/procedures/add-new-project.md`, `docs/02-prompts/PROMPT-001-artifact-code-generation-system.md`,
`docs/08-governance/GLOSSARY.md`, `docs/08-governance/GOV-001-protocol.md`.

## Documentation follow-up

Searched the tree for anything telling a reader (human or agent) to create portfolio entities in
`_data/` unconditionally, and updated each to reflect the real/fictional split:

- `docs/08-governance/GOV-001-protocol.md` — removed the "until `phase-priv-03` relocates" caveat,
  now states the move happened and names `data_root()` as the resolution mechanism.
- `brain/procedures/add-new-project.md` — the "create the project JSON file" step now branches on
  real vs. fictional, with the actual paths for each.
- `brain/concepts/json-source-of-truth-pattern.md` — the "How It Works" diagram and rules now show
  the two-root split and the tags.json/ideas.jsonl exception; regenerated
  `docs/08-governance/GLOSSARY.md` from it (generated artifact, never hand-edited).
- `README.md` — the data-architecture rule section and the "Current Inventory" section (which cited
  `_data/projects/*.json` as where the 34-project counts come from — no longer true) both corrected.
- `CLAUDE.md` — Data Architecture section and the directory-reference table's `_data/`/`_private/`
  rows updated; `_private/portfolio/` given a first-class mention where it had none.
- `docs/02-prompts/PROMPT-001-artifact-code-generation-system.md` — the project-JSON generation rule
  now names the resolved data root instead of hardcoding `_data/projects/`.

Not touched: `docs/06-requirements/REQ-002-capture-requirements.md`, which describes an unbuilt
capture pipeline's promotion behavior in terms of `_data/people/`. That is a requirements document
for future work, not current guidance, and updating its promotion target to respect the data-root
split is a design decision for whoever builds that pipeline — noted in `## Unresolved` below instead
of decided here.

## Unresolved

`phase-cap-08` ("Seed the portfolio through the capture pipeline", queued, not yet ready) has the
acceptance condition "commitments, interactions and tasks are non-empty after a rebuild." That
condition is now trivially true before `phase-cap-08` ever runs, because this phase's fictional
`_data/commitments/c-1.json` and `_data/tasks/t-*.json` already make the default rebuild non-empty.
`phase-cap-08`'s other two conditions ("no project carries a retired review_cadence value", "every
promoted record traces back to a raw capture") still require real captured content and are not
satisfied by fictional data, so the phase is not actually done — but its first acceptance line no
longer distinguishes "seeded for real" from "the fictional example set exists." Left as-is; flagging
for whoever picks up `phase-cap-08` rather than editing a phase this session did not claim.

`REQ-002-capture-requirements.md` specifies capture-pipeline promotion behavior against `_data/people/`
without reference to the real/fictional data-root split this phase introduced. Once the capture
pipeline (`sys-capture`, currently scaffold) actually promotes content, it needs to write real
captures to the resolved data root, not the tracked `_data/` — otherwise promotion re-introduces real
content into git exactly as ADR-009 exists to prevent. Not fixed here: the requirement describes work
that has not started, and deciding how capture should resolve the data root is that work's design
question, not a documentation correction.

## Review

Independent sub-agent review, run against commit range from “Claim phase-priv-03 for agent-clay, correct its scope” to HEAD (dev), reproduced verbatim:

> **Acceptance conditions**
>
> **1. "A clone with no environment variables set validates and rebuilds from the fictional set
> alone" — Met.** Reran both commands with no `D_SYSTEM_DATA_ROOT` set:
> - `uv run python -m src.governance` → `Governance OK: 16 systems, 101 documents, 13 memories, 101
>   backlog phases`
> - `uv run python tools/rebuild_db.py` → `projects: 5, people: 1, tags: 28, commitments: 1, tasks: 3`
>
> Both match the session record exactly. The fictional set (`_data/projects/*.json`, 5 files)
> collectively covers every field in `schemas/project.schema.json` (id, name, status, category,
> type, description, tags, stakeholders, started, target_date, last_reviewed, review_cadence,
> repository, notes — `example-web-platform.json` alone exercises `repository` and `stakeholders`).
> `_data/people/jordan-rivera.json` (person), `_data/commitments/c-1.json` (commitment), and
> `_data/tasks/t-1.json`–`t-3.json` (tasks) are correctly linked by id (`commitment.promised_to` →
> person id, `task.commitment_id`/`task.project_id` → commitment/project ids).
>
> **2. "The owner's real records still rebuild when the data root points at `_private/portfolio/`"
> — Met.** `_private/portfolio/projects/` exists on the filesystem with exactly 34 `.json` files
> (verified via `ls`, not git — correctly gitignored, `git check-ignore -v` confirms). Reran with
> `D_SYSTEM_DATA_ROOT=_private/portfolio`:
> - governance → same `Governance OK` line
> - rebuild → `projects: 34 rows` (others 0, as expected — no real people/commitments/tasks exist
>   yet)
>
> `git diff` shows `_data/projects/` disjoint from the portfolio set (5 fictional ids vs. 34 real
> ids, zero overlap), confirming the real files were moved, not copied.
>
> **3. "The example set contains at least one person and one commitment with tasks, which the tree
> has never had" — Met.** Confirmed above; ids link correctly.
>
> **Other checks**
>
> - **`_data/tags.json`**: free of identifying content — client tag is the generic `client-a`, not
>   the real client identifier. All 28 tag ids used across the 34 real portfolio files resolve
>   against `_data/tags.json` (verified programmatically — sets are identical, no dangling
>   references).
> - **`git grep` for the real client identifier**: non-zero matches, but every hit is inside
>   `docs/03-sessions/SESS-2026-09-08-12-scrub-tracked-structure.md` (a prior session's historical
>   record quoting old file contents) and `docs/09-backlog/backlog.yaml`'s narrative history of that
>   prior phase — not live data. No `_data/` file or current code contains the real identifier. This
>   is expected/correct, not a leak.
> - **`D_SYSTEM_DATA_ROOT` implementation**: sound. `data_root()` in `src/db/source_validation.py`
>   resolves the override for entity directories only; `tags.json` and `ideas.jsonl` are hardcoded
>   to the tracked `_data/` regardless (both in `source_validation.py` and `tools/rebuild_db.py`).
>   `src/governance/__main__.py` deliberately bypasses `public_path()`'s `_private/`-block for the
>   one project-reference check, with a code comment explaining why — reviewed and correct.
> - **Prior-phase fix**: accurate. The real course project's file relocated from `_data/projects/`
>   to `_private/portfolio/projects/` (confirmed present, content intact, `repository` field
>   unchanged). The backlog entry correctly drops only the file from
>   `deliverables`/`completion_evidence` (a gitignored path can't serve as tracked evidence) while
>   leaving the rest of that phase's evidence and result text intact — not a cover for anything else.
> - **Documentation follow-up**: spot-checked `README.md`, `CLAUDE.md`, and
>   `brain/procedures/add-new-project.md` in full diff — all three accurately replace unconditional
>   `_data/`-only guidance with the real/fictional split and correct `D_SYSTEM_DATA_ROOT` usage
>   instructions. No stale guidance found in these three.
> - **pytest**: `357 passed, 2 warnings` — matches the session record's claimed count and
>   explanation (29 fewer due to `test_every_source_project_validates` now parametrized over 5
>   fictional files instead of 34 real ones).
>
> DB left rebuilt from the default (no-env) fictional data root, as instructed.
>
> **Conclusion**
>
> All three acceptance conditions: **Met**, independently confirmed. No discrepancies found between
> the session record's claims and the diff/filesystem/rerun evidence.

## Decisions

- Orienting on `phase-priv-03` after the owner confirmed real portfolio data should not live in git
  surfaced that its own scope named `tools/load_context.py` for `D_SYSTEM_DATA_ROOT` support, but
  that tool only reads the already-built `data/d_system.duckdb` and has no direct `_data/`
  dependency. Corrected the phase's deliverables before starting rather than making a no-op change
  to satisfy stale text: dropped `tools/load_context.py`, added `src/db/source_validation.py` (the
  file that actually needed the override, since it is `rebuild_db.py`'s own preflight and hardcodes
  `_data/` independently of `rebuild_db.py`'s `root` parameter).
- Chose to keep `_data/tags.json` as a single shared file rather than duplicating it into
  `_private/portfolio/tags.json`, departing from the plan's literal "move ... client tag entries to
  `_private/portfolio/`" wording. Reasoning: `phase-priv-02` had already renamed the client tag from
  the real client identifier to the generic `client-a`, so nothing in the tag registry remained real/identifying — ADR-009
  itself classifies "the tag taxonomy shape" as structure, not content. Verified zero real project
  tags fall outside the tracked tag set before committing to this, rather than assuming it.
- Governance's project-reference check (`src/governance/__main__.py`) needed to read real project
  ids from `_private/portfolio/` when the override is set, but `public_path()` blocks `_private/`
  everywhere else in that module by design. Added a narrow, explicitly-commented exception for this
  one lookup rather than loosening the general block, so the boundary stays in force for every other
  governance check.
- Found mid-implementation that a prior completed phase cited the real course project's
  `_data/projects/` file as completion evidence, which broke the moment that file
  relocated. Fixed it in the same session rather than leaving governance red or silently working
  around it: dropped the stale path from that phase's `deliverables`/`completion_evidence` with a
  note explaining why, leaving its other evidence and `result` text untouched.
- After merging the worktree branch, found `_private/portfolio/` did not exist in the primary
  checkout — gitignored content never travels through a git merge. Copied it over by hand, verified
  it byte-identical to the worktree's copy, and reverified both rebuild paths before removing the
  worktree. Recorded as a durable procedural note (own memory system) since this risk recurs on any
  future worktree-based phase touching `_private/`.
- When the owner asked for process notes to be updated to reflect the new folder location, searched
  broadly rather than fixing only the files already known to be stale: found and corrected six
  additional files (`GOV-001-protocol.md`'s dangling "until phase-priv-03 relocates" caveat,
  `brain/procedures/add-new-project.md`, `brain/concepts/json-source-of-truth-pattern.md`,
  `README.md`, `CLAUDE.md`, `PROMPT-001`), regenerated the glossary this touched, and explicitly
  declined to edit `REQ-002-capture-requirements.md` (a requirements document for unbuilt work) —
  flagging it in `## Unresolved` instead of making a design decision for a system that does not
  exist yet.
- Folded the documentation follow-up into this same phase's session record and `completion_evidence`
  rather than opening a new phase for it, since it is a direct, same-day correction of drift this
  phase's own relocation caused — not new scope.

## Corrections

None. No claim made during this session was found wrong by the independent review or by rerunning
the verification commands.

## Left undone

- `phase-cap-08`'s acceptance wording ("commitments, interactions and tasks are non-empty after a
  rebuild") is now trivially satisfiable by the fictional seed data this phase added, even though
  its real intent — real captured content — is not. Flagged in `## Unresolved` above; not edited,
  since this session did not claim `phase-cap-08`.
- `REQ-002-capture-requirements.md` does not yet account for the real/fictional data-root split when
  it specifies capture-pipeline promotion targets. Flagged in `## Unresolved` above; deciding how the
  not-yet-built capture pipeline should resolve the data root is that work's own design question.
- `phase-priv-04` ("Harden ignore rules and add an enforceable leak check") remains queued and is now
  unblocked now that this phase reaches `complete` — natural next step in the confidentiality sweep,
  not started here.
