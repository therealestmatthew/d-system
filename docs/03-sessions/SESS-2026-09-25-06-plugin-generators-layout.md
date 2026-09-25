---
schema_version: 1
id: doc-session-plugin-generators-layout
code: SESS-2026-09-25-06
title: The plugin's generators, layout reference and agreement templates
kind: session
status: active
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-generators]
depends_on: [doc-idea-realization-plugin-generators-layout]
---

# The plugin's generators, layout reference and agreement templates

## Phase

`phase-plug-06` — Generators, repository-layout reference, and the working-agreement and
orientation templates.

## Verification

Run in `/code/d-system-worktrees/phase-plug-06` on `agent/phase-plug-06`, rebased onto dev
`5f4a2b8`.

```
$ cd plugins/idea-realization && uv run pytest
266 passed
```

```
$ claude plugin validate plugins/idea-realization --strict
✔ Validation passed
```

```
$ uv run python tools/check_no_private_content.py
check_no_private_content: OK (974 tracked files, 0 identifiers checked)
```

The worktree has no `_private/portfolio/`, so the content half had no identifiers to look for; the
path half ran. At the claim commit the same check ran with 31 identifiers in the primary checkout.

```
$ uv run python -m src.governance
Governance OK: 43 systems, 364 documents, 32 memories, 318 backlog phases
```

Also run for the Session Manager's merge gate: `uv run pytest` → `1115 passed, 1 warning`;
`uv run ruff check src/ test/` → `All checks passed!`; `uv run mypy src/` → `Success: no issues
found in 46 source files`. Within the plugin, `uv run ruff check .` → clean.

## Acceptance

- Each generator run twice over a fixture produces identical output; a hand edit inside a generated
  block makes the generator exit 1 naming the file — **Met.** Tool docs:
  `test_running_twice_produces_identical_output` and
  `test_a_hand_edit_inside_the_block_fails_the_check_naming_the_file` (`--check` exits 1 with the
  document's path on stderr, and leaves the edit in place). Workflows:
  `test_rendering_is_deterministic` and `test_a_hand_edit_fails_the_check_naming_the_file`.
- The rendered templates contain no placeholder marker and pass the R02 check; a template with an
  unknown placeholder fails rendering — **Met.**
  `test_a_rendered_template_has_no_marker_and_passes_the_source_reference_check` (both templates,
  scanned with the plugin's own R02 scanner), `test_an_unknown_placeholder_fails_rendering` and
  `test_the_command_refuses_an_unknown_placeholder` (exit 1 naming it).
  `test_a_template_names_no_plugin_command_or_skill` keeps the templates to portable rules.
- `docs/tools.md` regenerated twice is identical and names every script under `scripts/` except
  `paths.py` and the `checks/` modules; a fixture script added to a copy of `scripts/` fails the
  committed-output comparison until the document is regenerated — **Met.**
  `test_regenerating_the_reference_twice_is_identical`,
  `test_the_reference_names_every_script_except_paths_and_the_checks`,
  `test_a_new_script_makes_the_reference_stale_until_regenerated`, and
  `test_the_committed_tools_reference_is_current`; `test_the_command_in_the_reference_header_runs_as_written`
  runs the regeneration command printed in the document's header, as written.

## Backlog

`status: active`, `agent: agent-builder-a`, `session: doc-session-plugin-generators-layout`.
`next_action`: every acceptance condition is met on `agent/phase-plug-06`; awaiting the independent
review's findings and the owner's merge approval, after which the completion edit is made on dev.

## Unresolved

- `docs/tools.md` goes stale whenever a later phase adds a script to `scripts/`, and
  `test_the_committed_tools_reference_is_current` then fails until it is regenerated. The command
  to regenerate it is in the document's own header. This couples every later script-adding phase
  to regenerating it, by design.
- `paths.add_arguments` flags are listed by key name only; their help text lives in the plugin
  manifest and the Configuration section, not per script.

## Decisions

- **The private-content check is not ported** (owner ruling, asked at the claim). PLAN-048.06 left it
  open, leaning to porting the path-prefix half with `confidential_dir` as the prefix. The owner
  declined. The source check's identifier half derives what counts as confidential from this
  repository's own portfolio layout, which a target does not share. Its path half is one prefix
  test that a target can write for its own confidential directory, and the rendered `AGENTS.md`
  already states the rule it would enforce. The phase's deliverables stay as declared.
- **The reference states its own regeneration command.** The generated `docs/tools.md` states the full command
  that regenerates it, `--root .` included whatever root was used, so it reads the same from any
  checkout and runs as written from the plugin directory.
- **The templates stay command-free.** They state the portable rules only and name no plugin
  command or skill, so they cannot claim behaviour a feature has not shipped (review Finding 1).

## Review

Independent adversarial review by a `demo-adversary` sub-agent (the owner chose the type), over
`dev...HEAD` at `d094ab4`. It re-ran the plugin suite (263 passed at that commit) and the repo's
ruff, executed the generators directly, and traced the renderer's edge cases. It could not run
`claude plugin validate` (no `claude` CLI in its session) and said so. Its verdicts and findings, as
reported:

- **Generators deterministic, hand edit exits 1 naming the file — Met.** Authority enforcement and
  the marker-quoting behaviour are preserved from the source.
- **Rendered templates marker-free and R02-clean, unknown placeholder refused — Met, mechanically**,
  with Finding 1 on scope. Whitespace-padded, empty and nested markers are all caught.
- **`docs/tools.md` identical twice, every script but `paths.py` and `checks/`, stale on a new
  script — Met structurally**, with Finding 2 on the header command.

1. **[Blocking] `templates/AGENTS.md` carried the whole claim, lock, hand-off and collision
   procedure and a backlog `ready` step**, beyond analysis 04 §5's portable list that PLAN-048.06
   restricts the templates to. Worse, it was false for the plugin as shipped: it said `check` is the
   lock check and refuses overlapping claims, and named a `ready` command, but the only installed
   check is `documents` and no `ready` command exists. That behaviour is phase-plug-04's, which is
   not merged and not a dependency. The template tests could not see it: they check markers and R02,
   not scope or truth.
2. **[Should-fix] The regeneration command printed in `docs/tools.md`'s header did not run as
   written**: it named `generate_tool_docs.py` without its `scripts/` path, and failed with
   "can't open file". The tests ran the script by absolute path, not the printed text.
3. **[Note] `docs/repository-layout.md` agrees with the scaffold's seeds and the manifest
   defaults** for every path checked.
4. **[Note] The tools skill names `docs/tools.md` as its only source** and runs nothing.
5. **[Note] `templates/CLAUDE.md` stays within the four placeholders and the portable list.**
6. **[Not confirmed] `claude plugin validate`**, which the reviewer could not run.

**Disposition.** Finding 1 is fixed: `templates/AGENTS.md` now holds exactly the portable rules:
the no-self-edit rule, ask rather than assume, plan before implementing, the confidentiality and
integration rules, generated files, one worktree per session, narrow diffs and honest reporting.
The claim, lock, hand-off and collision sections and the backlog step are gone, and
`test_a_template_names_no_plugin_command_or_skill` fails if a template names a plugin command or
skill, or mentions a lock, again. Finding 2 is fixed: the header now carries the full command,
`uv run scripts/generate_tool_docs.py …`, and
`test_the_command_in_the_reference_header_runs_as_written` runs it from a copy of the plugin.
Finding 6: `claude plugin validate --strict` passes in this session (see Verification). Findings 3
to 5 need no action.

## Corrections

- The reference header first recorded the caller's `--root`, which differs per checkout, then
  omitted the script's path; the review caught the second (Finding 2).
- The AGENTS template first carried rules beyond the portable list and statements about plugin
  behaviour that is not built yet (Finding 1).
- A first skill test forbade the words `uv run` in the tools skill, which its prose legitimately
  uses; it now forbids a code block instead.

## Left undone

- The claim, worktree and hand-off procedure a target repository needs is not in any template.
  Once phase-plug-04 ships the backlog check and `ready`, a template or governance document can
  state it truthfully; that belongs to the phases that build it (phase-plug-04, phase-plug-07).

