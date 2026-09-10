---
schema_version: 1
id: doc-session-portable-workflow-foundation
code: SESS-2026-09-09-03
title: Canonical workflows and portable skill adapters
kind: session
status: active
owner: repository-owner
created: '2026-09-09'
updated: '2026-09-10'
systems: [sys-governance, sys-delivery]
depends_on: [doc-portable-agent-workflows]
---

# Canonical workflows and portable skill adapters

## Phase

`phase-port-01` — Establish canonical workflows and portable skill adapters.

## Verification

`uv run python tools/generate_agent_workflows.py --check`

```text
4 workflow adapter(s) current
```

`uv run pytest test/test_agent_workflows.py`

```text
12 passed, 2 warnings
```

`uv run python -m src.governance`

```text
Governance OK: 16 systems, 117 documents, 15 memories, 105 backlog phases
```

`uv run pytest`

```text
407 passed, 2 warnings
```

Additional targeted quality checks:

```text
uv run ruff check tools/generate_agent_workflows.py test/test_agent_workflows.py
All checks passed!

uv run mypy src/ tools/generate_agent_workflows.py
Success: no issues found in 16 source files
```

A broader `uv run ruff check src/ test/ tools/generate_agent_workflows.py` run reported one existing
import-order failure in `src/governance/__main__.py:6`; this phase did not change that file. The
targeted generator and test files pass Ruff.

## Acceptance

- **Met:** Orientation and checkpoint have one body each under `agent-workflows/`; the generator
  produces current Claude and Open Agent Skills representations from those bodies.
- **Met:** Contract tests refuse owner-only workflows on agent-discoverable targets and refuse a
  required capability without a mapping or explicit unsupported declaration.
- **Met:** Contract tests detect adapter tampering, render deterministically, reject path traversal,
  and reject missing or out-of-tree canonical sources.
- **Met:** PROMPT-008 names the canonical checkpoint workflow and plain-prompt fallback, retains the
  owner-only completion boundary, and contains no Claude checkpoint path.

## Backlog

- Status: `active`
- Next action: Implementation and declared verification are complete; the owner can invoke
  session-close for independent review and the completion decision.
- Evidence: canonical workflow sources and manifest, four generated adapters, generator and tests,
  OPS-010, updated PROMPT-008, and this session record.

## Unresolved

A fresh independent review of the three corrections remains before the owner-controlled completion
transition. The unrelated existing Ruff import-order finding in `src/governance/__main__.py` remains
outside this phase.

## Review

### Initial independent review

> Independent review result: not ready for completion.
>
> 1. **Met — single-source, reproducible adapters.** Orientation and checkpoint each have one canonical body declared in `workflows.yaml`. All four Claude/Open Agent Skills adapters exactly match renderer output. Orientation retains its read-only boundary at `orient.md:12`; checkpoint retains the no-completion boundary at `checkpoint.md:13`. Comparison with `dev` found no altered repository decisions.
>
> 2. **Met — authority and required-capability refusal.** The renderer rejects owner-only workflows on every currently supported target, all of which are agent-discoverable skills, at `generate_agent_workflows.py:128`. It also rejects a required capability lacking either a nonempty mapping or explicit unsupported declaration at `generate_agent_workflows.py:142`. The focused tests exercise both refusals.
>
> 3. **Met — drift and determinism.** `--check` compares every declared adapter byte-for-byte at `generate_agent_workflows.py:195`. The tests demonstrate deterministic renders and a failed check after tampering at `test_agent_workflows.py:47`. Although the tamper fixture changes only the first adapter, the production comparison loops over all declared outputs, so the same check applies to all four.
>
> 4. **Met as written — host-neutral checkpoint lookup and completion boundary.** `PROMPT-008:80` points to the canonical checkpoint source and defines direct reading as the fallback, with no Claude checkpoint path. Its explicit prohibition on completion remains at `PROMPT-008:86`.
>
> Discrepancies:
>
> - **Blocking: the canonical checkpoint body is not location-neutral.** Its GOV-003 Markdown link at `checkpoint.md:18` uses `../../../docs/...`. That resolves correctly from both generated skill directories but resolves from the canonical plain-prompt source to `/code/docs/...`, which does not exist. The plain-prompt fallback therefore contains a broken repository reference. No test checks links from the canonical body.
> - **Manifest path validation permits machine-specific absolute paths.** `_inside()` joins and resolves paths but never rejects absolute inputs at `generate_agent_workflows.py:53`. Independent probes confirmed that absolute in-repository source and target paths are accepted. This bypasses the intended repository-relative portability contract; existing tests cover escapes and traversal only.
> - **Malformed capability mappings can be silently ignored.** At `generate_agent_workflows.py:142`, only nonempty string values enter `mapped`. An undeclared entry such as `bogus: false` is therefore neither mapped nor reported as unknown; an independent probe confirmed acceptance. Required capabilities remain protected, but the manifest does not strictly validate all capability declarations.
>
> Independent verification reproduced every numerical and quality claim in the session record:
>
> ```text
> 4 workflow adapter(s) current
> 10 passed, 2 warnings
> Governance OK: 16 systems, 117 documents, 15 memories, 105 backlog phases
> 405 passed, 2 warnings
> Targeted Ruff: All checks passed!
> mypy: Success: no issues found in 16 source files
> ```
>
> The broader Ruff run also reproduced the recorded pre-existing import-order failure in `src/governance/__main__.py`. The branch is clean, contains one commit over `dev`, and `git diff --check dev...HEAD` passes.
>
> The command outputs in `SESS-2026-09-09-03` are accurate. Its claim that implementation is complete and its `## Unresolved` section are not accurate because they omit the broken canonical link and manifest-validation gaps.
>
> **Completion is not justified. Unresolved discrepancies remain.**

## Decisions

The portability work was moved to the front of `next_up` at the owner's direction. The implementation
uses host-neutral Markdown bodies plus a manifest as the source and generates checked-in Claude and
Open Agent Skills adapters. Existing mature checkpoint instructions were preserved rather than
condensed. Session-close remains outside the manifest because its owner-only boundary must not become
agent-discoverable.

## Corrections

The first draft condensed the checkpoint procedure too aggressively; it was replaced with the full
existing procedure before the implementation commit. A tamper test initially exposed a Python
default-argument bug that made its isolated root ineffective; the command now passes root and manifest
explicitly. The independent close review then found and caused three further corrections: the
canonical checkpoint's GOV-003 reference is now repository-root-relative text, absolute source and
target paths are rejected, and every capability mapping must be a nonempty string. Regression tests
cover all three findings, increasing the focused suite from 10 to 12 tests and the full suite from 405
to 407 tests.

## Left undone

The safe commands and idea-triage agent remain for `phase-port-02`; clean-host discovery and fallback
walkthroughs remain for `phase-port-03`. Neither belongs in this foundational phase. The existing
repository-wide Ruff import-order failure remains outside this phase because its source file was not
touched by the portability work.
