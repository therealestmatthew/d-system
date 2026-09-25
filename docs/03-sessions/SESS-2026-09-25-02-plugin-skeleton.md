---
schema_version: 1
id: doc-session-plugin-skeleton
code: SESS-2026-09-25-02
title: Idea-realization plugin skeleton, prerequisites, scaffold and doctor
kind: session
status: active
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-core]
depends_on: [doc-idea-realization-plugin-skeleton-install]
---

# Idea-realization plugin skeleton, prerequisites, scaffold and doctor

## Phase

`phase-plug-01` — Plugin skeleton, prerequisites skill, scaffold with install-state record, and
doctor.

## Verification

Run in `../d-system-worktrees/phase-plug-01` on `agent/phase-plug-01`, Claude Code 2.1.280.

```text
$ cd plugins/idea-realization && uv run pytest
64 passed

$ claude plugin validate plugins/idea-realization --strict
Validating plugin manifest: .../plugins/idea-realization/.claude-plugin/plugin.json
✔ Validation passed

$ uv run python tools/check_no_private_content.py   # changes staged
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (938 tracked files, 0 identifiers checked)

$ uv run python -m src.governance
Governance OK: 43 systems, 359 documents, 32 memories, 318 backlog phases
```

The worktree has no `_private/`, so the staged check ran its path check only. The content check was
run separately from the primary checkout: its `confidential_identifiers()` against every file under
`plugins/idea-realization/` in this worktree, printing counts only —
`31 identifiers, 27 plugin files, 0 problems`.

Repository gates, same worktree: `uv run ruff check src/ test/` — `All checks passed!`;
`uv run mypy src/` — `Success: no issues found in 46 source files`; `uv run pytest` —
`1080 passed, 1 warning`; `git diff --exit-code docs/08-governance/catalog.md` — no change.

Loading check (behavioural), run headless from a scratch git repository outside this one:
`claude -p "<prompt>" --plugin-dir .../plugins/idea-realization "--allowedTools=Bash(uv run:*)"`.
The session listed the skills as `idea-realization:doctor`, `idea-realization:prerequisites`,
`idea-realization:scaffold`; quoted the doctor skill's command with the root substituted,
`uv run "/code/d-system-worktrees/phase-plug-01/plugins/idea-realization/scripts/doctor.py"`; and
ran `uv run <root>/scripts/paths.py --root .`, whose output began `root: <scratch repository>` and
`ideas_path: <scratch repository>/ideas/ideas.jsonl` and listed all ten keys with their defaults.

Manifest facts checked with the same CLI before the manifest was fixed, on scratch fixtures:
a manifest with `"license": "MIT"` gives `✔ Validation passed` and exit 0 under `--strict`; one with
an unknown top-level key gives `bogus: Unknown field 'bogus'. Claude Code ignores it at load time.`,
`✘ Validation failed (--strict treats warnings as errors)`, exit 1. A saved option substitutes into
skill text (`--settings` with `pluginConfigs["idea-realization@inline"]` gave `custom/x.jsonl`); an
unsaved one stays literal as `${user_config.ideas_path}`, the manifest default is not substituted;
a `multiple` option substitutes comma-joined (`docs/a b.md,x.md`).

## Acceptance

- `validate --strict` exits 0; a fixture with a license field or an unknown key fails --strict —
  Met for validation and the unknown key (`test_manifest.py`, run against the live CLI). The
  license half cannot hold: `license` is a valid manifest field and `--strict` passes it. Owner
  ruling this session: enforce "no license" with the plugin's own test
  (`test_manifest_names_the_plugin_and_has_no_licence`) and correct the wording (Unresolved).
- `--plugin-dir` lists the skills in a new session and `${CLAUDE_PLUGIN_ROOT}` resolves — Met, see
  the loading check above.
- Scaffold: one hash per created file, a no-op second run reporting skipped, a pre-existing
  `backlog.yaml` byte-identical, a dry run that writes nothing — Met (`test_scaffold.py`).
- Prerequisites without `uv` exits 1 naming `uv` and its install command and changes no file; only
  `--yes` installs — Met (`test_prerequisites.py`: a subprocess run with `PATH` holding only `git`,
  and in-process runs with a recording installer).
- R02 check passes over the plugin tree and fails on a fixture containing a phase id — Met
  (`test_no_source_references.py`).
- Scripts copied to a temporary directory run against a temporary data root; no `parents[` or
  `from src` in `scripts/` — Met (`test_scripts_portable.py`).

## Backlog

`status: active`, `agent: agent-builder-b`. `next_action`: run `/session-close` up to its
independent review, then send READY to the Session Manager; the phase completes only after the
owner-approved merge. `session: doc-session-plugin-skeleton`; `completion_evidence` cites
`plugin.json`, `paths.py`, `scaffold.py`, the scaffold and R02 tests, and this record; `result`
describes the build as not yet reviewed or merged.

## Unresolved

- **Wording correction awaiting approval** (owner chose "own test + fix wording"). Proposed text:
  - backlog acceptance, first entry: "claude plugin validate plugins/idea-realization --strict exits
    0; a fixture manifest with an unknown top-level key fails --strict; a test asserts plugin.json
    has no license key."
  - `REQ-031` R01 verification: "`claude plugin validate plugins/idea-realization --strict` exits 0.
    A fixture copy with an unknown top-level key fails `--strict`. A test asserts `plugin.json` has
    no `license` field."
- **Decisions made in this phase that later plugin phases inherit:**
  - Owner: the code register and systems registry are scaffolded at `<docs_root>/codes.yaml` and
    `<docs_root>/systems.yaml`; schemas are copied to `.idea-realization/schemas/`.
  - Owner: the scaffold's consent-gated write is `.gitignore` only (the staging directory line); it
    never writes `.claude/settings.json` or a hook. A later phase that needs one adds it.
  - Skills pass saved options as `CLAUDE_PLUGIN_OPTION_<KEY>='${user_config.<key>}'`,
    single-quoted: bash rejects the unsubstituted text inside double quotes ("bad substitution"),
    and `CLAUDE_PLUGIN_OPTION_*` is not exported to the Bash tool. `paths.py` treats unsubstituted
    text as unset. `test_skills.py` enforces the quoting.
  - Feature modules in `scripts/checks/<feature>.py` expose `check(config)` and/or `COMMANDS`;
    `check.py` and `cli.py` discover them.
  - Planner calls (PLAN-048 Q3 and the child plan's open question): `claude` is required only with
    `--feature triage|partition|all`, as `REQ-031` R04 states, otherwise reported optional;
    `worktree_dir` defaults to `../<repository>-worktrees`, derived from the repository directory's
    name at resolve time.
  - Seed files: the priority seed carries every field this repository's
    `schemas/idea-priority.schema.json` requires (`schema_version`, `updated`, `next_up`). The
    backlog seed does **not** match `schemas/backlog.schema.json`, which requires `decision_record`;
    the seed omits it deliberately, because its value is a document id and a fresh target has no
    decision record to name. `phase-plug-04` owns the plugin's backlog schema: it either drops
    `decision_record` from the required list or needs a seed edit in `scripts/scaffold.py`, which
    is outside its declared deliverables. Flagged to the Session Manager in READY.
- **Scope wording also stale:** the backlog scope bullet still reads "consent-gated writes to
  settings, hooks and .gitignore (R05, R06)"; under the owner's ruling this session it should read
  "a consent-gated write to .gitignore (R06); no write to settings or hooks". `REQ-031` R06 still
  names settings and hooks as consent-gated targets, which stays true as a rule for any later phase
  that adds such a write.

## Review

Independent adversarial review by a `demo-adversary` agent, given the scope, acceptance and
verification lists, the range `dev...HEAD` (6fb8913, 12ae04b, 2d8f3f2), this record, and the owner's
rulings. It re-ran every verification command, the repository gates, the loading check headlessly
from a scratch repository, the prerequisites check with a `PATH` holding only `git`, and the
scaffold, second run, dry run and doctor by hand. Its report, condition by condition:

1. `validate --strict` / unknown key / license — **Met.** "`claude plugin validate
   plugins/idea-realization --strict` → `✔ Validation passed`, exit 0. Independently reproduced the
   license-passes-strict fact the owner ruled on … confirms the acceptance wording is genuinely
   unsatisfiable as written, and confirms the mitigation is real."
2. Loading check — **Met.** "listed exactly `idea-realization:doctor`,
   `idea-realization:prerequisites`, `idea-realization:scaffold` … running that literal command
   against the scratch repo produced the documented `no install-state record … run the scaffold
   first`, exit 2."
3. Scaffold — **Met.** "dry-run wrote nothing … a second run reported every path `skipped …
   (exists)` and changed nothing; `doctor` after edit-and-delete correctly reported
   `drifted`/`missing`/`unchanged` and changed nothing."
4. Prerequisites — **Met.** Exit 1, `missing  uv      not on PATH; install: curl -LsSf
   https://astral.sh/uv/install.sh | sh`, "`keep.txt` in the working directory verified
   byte-identical before/after."
5. R02 — **Met.** "the only hit is the regex pattern's own source text in
   `test_no_source_references.py:26` (`r"\bSESS-"`), which is the detector, not an instance …
   Injected `phase-demo-99` into a copy's README … it correctly flagged" it.
6. Portability — **Met.** "`test_scripts_portable.py` does this and passes; I independently grepped
   the whole plugin tree for `parents[`, `from src`, `import src` and found nothing."

Gates it re-ran: plugin suite `63 passed`; repository `uv run pytest` `1080 passed, 1 warning`;
ruff clean; mypy `Success: no issues found in 46 source files`; governance OK; catalog unchanged.

Findings, as reported, and their disposition:

1. **should-fix** — `scripts/scaffold.py` backlog seed omits `decision_record`, "and the session
   record's stated justification is false": `schemas/backlog.schema.json` requires it. **Fixed in
   the record** (the claim was wrong; see Corrections). The omission itself is kept as a deliberate
   choice and handed to `phase-plug-04` in Unresolved and in READY.
2. **minor** — the exclusive-create write had no handling for `FileExistsError` when a file appears
   between the existence check and the write; the run would abort with earlier files unrecorded.
   **Fixed:** the scaffold now reports `skipped  <path> (appeared during this run)`, leaves the file
   untouched and continues; `test_a_file_appearing_mid_run_is_skipped_not_overwritten` covers it.
3. **minor** — the scope bullet's "settings, hooks and .gitignore" is stale against the owner's
   ruling and nothing tracked it. **Accepted and tracked:** proposed wording added to Unresolved.

"No other discrepancies survived the attack."

## Decisions

The loading check ran first, before any manifest shape was fixed, and passed on a minimal fixture.
The same scratch fixtures settled four manifest facts from the live CLI rather than from memory:
`license` passes `--strict`; an unknown top-level key fails it; `${user_config.KEY}` substitutes
only a saved value; list options arrive comma-joined. The owner then made three rulings: enforce
"no license" with the plugin's own test and correct the wording; put the registers under
`docs_root` and the schemas under `.idea-realization/schemas/`; gate `.gitignore` only, never
settings or hooks. The owner chose "gitignore only" over the recommended "mechanism only", so no
settings or hook code exists to maintain until a phase needs it.

The builder's own calls: skills pass options through single-quoted `CLAUDE_PLUGIN_OPTION_<KEY>`
assignments, because `CLAUDE_PLUGIN_OPTION_*` never reaches the Bash tool and bash rejects the
unsubstituted text in double quotes; `paths.py` reads the key list and defaults from the manifest,
so the ten keys are declared once; the scaffold copies a plugin file when this version ships it and
reports "not shipped" otherwise, so later phases' schemas and templates reach targets without an
edit to `scaffold.py`; `claude` is required only for triage and partition, as R04 states; the R02
check reads the repository name, remote owner and committer identity from git at test time, so no
forbidden literal is written into the plugin.

## Corrections

- The scaffold skill first passed options as `env $OPTS` with a quoted string; word-splitting would
  have kept the quotes inside each value. Replaced with inline assignments before any commit.
- The inline assignments were first double-quoted; a direct bash test gave `bad substitution` for an
  unset option. Switched to single quotes and added `test_skills.py` to hold that.
- A stray `.mypy_cache` from a manual mypy run inside `scripts/` made the R02 scan fail on cached
  text; the cache was deleted and tool caches added to the scan's skip list.
- The record claimed the backlog seed followed this repository's required fields; it does not
  (`decision_record`). Corrected after the review.

## Left undone

- The wording corrections in Unresolved (acceptance entry one, `REQ-031` R01, the scope bullet) are
  proposals for the owner, not edits: they touch shared planning text outside this phase's
  deliverables.
- The seed/schema agreement for the backlog belongs to `phase-plug-04`; for the priority file to
  `phase-plug-02`.
- The phase stays `active` until the owner approves the merge; completion follows on `dev`.
