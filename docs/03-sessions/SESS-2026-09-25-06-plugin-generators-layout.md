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
263 passed
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
- `docs/tools.md` regenerated twice is identical and names every script under `scripts/` except
  `paths.py` and the `checks/` modules; a fixture script added to a copy of `scripts/` fails the
  committed-output comparison until the document is regenerated — **Met.**
  `test_regenerating_the_reference_twice_is_identical`,
  `test_the_reference_names_every_script_except_paths_and_the_checks`,
  `test_a_new_script_makes_the_reference_stale_until_regenerated`, and
  `test_the_committed_tools_reference_is_current`.

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
