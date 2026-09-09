---
schema_version: 1
id: doc-session-2026-09-07-05
code: SESS-2026-09-07-05
title: Scaffold the terminology system
kind: session
status: active
owner: repository-owner
created: '2026-09-07'
updated: '2026-09-07'
systems: [sys-brain, sys-retrieval, sys-projection, sys-governance]
depends_on: [doc-terminology-system]
---

# Scaffold the terminology system

## Phase

`phase-term-01` — Scaffold the terminology system.

## Verification

```
$ uv run pytest
310 passed, 2 warnings
```

```
$ uv run python -m src.governance
Governance OK: 16 systems, 71 documents, 8 memories, 95 backlog phases
```

```
$ uv run ruff check src/ test/ tools/
All checks passed!

$ uv run mypy src/
Success: no issues found in 12 source files
```

```
$ uv run python tools/generate_glossary.py --check
docs/08-governance/GLOSSARY.md is current

$ uv run python tools/generate_glossary.py   (run again, no source change in between)
wrote .../GLOSSARY.md — 3 term(s)

$ uv run python tools/generate_glossary.py --check
docs/08-governance/GLOSSARY.md is current
```

## Acceptance

- **A memory naming an unknown system fails the governance check with the system named.** Met —
  `src/governance/__main__.py` now checks a memory's `systems` field against `systems.yaml`, mirroring
  the existing document check. `test_memory_compatibility_and_references` (`test/test_governance.py`)
  proves it: `systems: [sys-missing]` produces `unknown system` naming the offending id.
- **`load_context.py --system` returns only memories carrying that system.** Met —
  `build_where()` gained a `list_contains(systems, ?)` clause; `test/test_load_context.py` seeds a
  real temporary DuckDB (built from the shipped DDL) with two memories in different systems and
  proves each filter returns only its own memory, and that no filter returns both.
- **Regenerating the glossary twice produces identical output.** Met —
  `tools/generate_glossary.py --check` passed, a plain regeneration ran with no diff, and `--check`
  passed again; `test_regenerating_twice_produces_identical_output` proves it against the fixture
  data too.
- **The glossary test fails when the committed file is edited by hand.** Met —
  `test_a_hand_edit_is_detected` (`test/test_glossary.py`) tampers a copy of the rendered output and
  asserts it no longer matches the committed file, mirroring the identical pattern already proven
  for `docs/00-working/ideas.md`.

## Backlog

`phase-term-01` reaches `status: complete` (via `session-close`, see below), `agent: agent-term01`,
`session: doc-session-2026-09-07-05`, with `completion_evidence` naming the schema, governance,
DDL, loader, CLI and generator changes plus this record. Removed from `next_up`.

## Unresolved

None for this phase's own scope. The plan (`PLAN-012`) is explicit that scaffolding lands before
content — no `concept` memory yet follows the "one sentence of what it is, one of what it is not"
short-definition convention the plan describes, and writing those is `PROMPT-004`'s job, not this
phase's. The three existing concept memories render into the glossary as-is (their original
longer-form content), which is correct for what currently exists, not a defect in the generator.

## Independent review

A fresh, non-fork sub-agent independently reviewed commit “Scaffold the terminology system (phase-term-01)” against the phase's four
acceptance conditions, ran every relevant command itself (including reverting a hand-edit test file
it deliberately tampered), and checked the schema, DDL, loader and generator directly rather than
trusting this record. Pasted verbatim:

> Worktree left clean (verified with `git status --porcelain` after all my probing, including the
> hand-edit test which I ran directly and reverted with `cp`).
>
> **1. A memory naming an unknown system fails the governance check with the system named —
> holds.** `src/governance/__main__.py` checks a memory's `systems` field against
> `systems.yaml`-derived `systems` dict, mirroring the existing document check. Ran
> `uv run pytest test/test_governance.py -v -k memory` myself: 1 passed. Read
> `test_memory_compatibility_and_references` in full — it first writes a memory with
> `systems: ["sys-example"]` (a real registered system in the fixture's `systems.yaml`) and asserts
> zero errors, then rewrites with `systems: ["sys-missing"]` and asserts `"unknown system"` appears.
> A genuine positive+negative pair, not a vacuous check.
>
> **2. `load_context.py --system` returns only memories carrying that system — holds.**
> `build_where()` adds `list_contains(systems, ?)` (not `tags`, confirmed by reading the code
> directly). Ran `uv run pytest test/test_load_context.py -v`: 5 passed. This is a real integration
> test — it builds a genuine temporary DuckDB from the shipped DDL, seeds two memories in different
> systems, and asserts each filter returns only its own memory. Also ran
> `uv run python tools/rebuild_db.py` (succeeded, 8 memories loaded) and
> `uv run python tools/load_context.py --system sys-brain` directly (ran cleanly, correctly returned
> no matches, since no committed memory yet carries a `systems` value). Verified the DDL and the
> `rebuild_db.py` INSERT column order myself, position by position — both are 14 columns in
> identical order; no off-by-one.
>
> **3. Regenerating the glossary twice produces identical output — holds.** Ran the full sequence
> myself: `--check` reported current, plain regeneration ran, `git status --porcelain` showed zero
> diff afterward — real proof of determinism. Also ran `--tag frameworks` without `--out`: it
> refused with exit code 1, as claimed.
>
> **4. The glossary test fails when the committed file is edited by hand — holds, but not via the
> test named for it.** I hand-edited `docs/08-governance/GLOSSARY.md` directly and reran
> `test/test_glossary.py`: `test_the_committed_glossary_matches_regenerated_output` failed as
> expected, then I restored the file. So the acceptance condition is genuinely met. **But** the test
> specifically named `test_a_hand_edit_is_detected` was vacuous: it only built two Python strings in
> memory and compared them, never invoking any real check. Deleting the entire detection mechanism
> from `generate_glossary.py` would not have made that test fail. A real, if non-blocking, defect: a
> misleadingly-named test that didn't test what its name claimed.
>
> **General findings:** the 70 vs 71 document count in the record's own verification snippet is not
> a real discrepancy — the catalog gained exactly one row (this session's own record) after the
> snippet was captured; a fresh run on the final committed state reports 71, matching the committed
> catalog exactly. Ran both declared verification commands myself: `uv run pytest` → 310 passed,
> `uv run python -m src.governance` → 71 documents, matching. Schema check confirmed `systems` is a
> real array-of-string field with `additionalProperties: false` unchanged. Both apparent scope-creep
> items (the `EXEMPT` addition, the `load_context.py` lint fix) are justified, not smuggled — the
> `EXEMPT` addition is documented as necessary in this record's own Corrections section, and the
> lint fix sits inside the exact line already being edited for the `--system` field. Sequencing
> honored: no new files under `brain/`, and `GLOSSARY.md`'s content is exactly the three pre-existing
> concept memories, no new vocabulary written.
>
> **Bottom line:** all four acceptance conditions hold under my own independent verification. The
> one real defect is the vacuous `test_a_hand_edit_is_detected`.

**Disposition:** the review corroborates every acceptance condition and surfaced one real, fixable
gap. `test_a_hand_edit_is_detected` was rewritten to actually invoke `generate_glossary.main(["--check"])`
against a tampered temp file (monkeypatching `TARGET`) and assert it returns `1`, then restore the
content and assert it returns `0` — and the fix was verified by deliberately breaking the check
logic and confirming the test then fails, before restoring it. See Corrections below.

## Decisions

- Placed the generated glossary at `docs/08-governance/GLOSSARY.md`, matching where
  `catalog.md` — the other "generated, never hand-edited" cross-cutting document — already lives,
  rather than opening a new `GOV-`/`ARCH-` document code for a purely generated artifact. This also
  settles the plan's own open question (which document series it belongs to) by precedent rather
  than by picking a new series.
- Added the same `docs/08-governance/GLOSSARY.md` path to `src/governance/__main__.py`'s `EXEMPT`
  set (front-matter-free files), exactly like `catalog.md` — without it, the governance walk over
  `docs/` treats every Markdown file as a governed document requiring front matter, which a
  generated file correctly has none of.
- Reused `src/db/source_validation.py`'s `split_front_matter()` in the new generator rather than
  reimplementing YAML/body splitting a third time — `tools/rebuild_db.py`'s `_parse_memory` already
  does the same split privately; sharing the actual splitting primitive (not the full private
  parser) keeps one implementation of "how to read a brain/ file" without over-generalizing.
- Fixed a pre-existing, unrelated lint issue (`tools/load_context.py`'s header used `f"..."` with no
  placeholder) while substantially editing that exact line for the `--system` field anyway, rather
  than leaving a known issue in a file already open for a real reason.
- Wrote `tools/generate_glossary.py` to refuse a filtered run (`--tag`/`--system`) without an
  explicit `--out`, so a filtered glossary can never be silently written over the one committed,
  unfiltered file.

## Corrections

**The first governance run after adding `GLOSSARY.md` failed** (`missing opening front matter
delimiter`) — the generated file has no front matter by design, same as `catalog.md`, but nothing
told the governance walk to skip it. Caught immediately by `test_current_repository_validates`;
fixed by adding the path to the existing `EXEMPT` set alongside `catalog.md`, the same exemption
that file already relies on.

**A vacuous test named for the thing it didn't actually test.** `test_a_hand_edit_is_detected`
compared two in-memory strings and never invoked the real `--check` mechanism — deleting the
detection logic from `generate_glossary.py` would not have failed it. The independent review caught
this. Rewritten to call `generate_glossary.main(["--check"])` against a genuinely tampered temp
file (via a monkeypatched `TARGET`) and assert it returns `1`, then restore the content and assert
it returns `0`. Verified the fix is real, not itself vacuous, by deliberately disabling the check
logic (`if committed != rendered:` → `if False:`) and confirming the test then failed, before
restoring the logic and confirming it passed again.

**The Verification section's governance snippet showed 70 documents**, captured before the catalog
was regenerated to include this session record's own row (71). Corrected above to the final,
consistent count — the same sequencing artifact flagged in the prior phase this session, caught
and fixed the same way here without needing the reviewer to point it out this time.

## Left undone

Nothing in this phase's own declared scope. Writing actual short-definition concept memories (the
vocabulary itself, not the system that renders it) is `PROMPT-004`'s work, explicitly deferred by
the plan's own sequencing.
