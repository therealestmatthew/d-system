---
schema_version: 1
id: doc-session-leak-check
code: SESS-2026-09-08-14
title: Harden ignore rules and add an enforceable leak check
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-delivery]
depends_on: [doc-confidentiality-sweep]
---

# Harden ignore rules and add an enforceable leak check

## Phase

`phase-priv-04` — Harden ignore rules and add an enforceable leak check.

## Verification

`uv run python tools/check_no_private_content.py`:

```
check_no_private_content: OK (251 tracked files, 30 identifiers checked)
```

Plant a real identifier in a tracked file, confirm the checker fails, then revert:

```
$ echo "test leak: <a real client project id> mentioned here" > _scratch_plant.md && git add -f _scratch_plant.md
$ uv run python tools/check_no_private_content.py
check_no_private_content: FAILED
  - _scratch_plant.md: matches confidential identifier '<the client identifier>'
  - _scratch_plant.md: matches confidential identifier '<the real project id>'
exit=1
$ git reset _scratch_plant.md && rm -f _scratch_plant.md
```

(The planted string was a real, non-tracked project id read from `_private/portfolio/` at test
time — not reproduced verbatim here, consistent with this phase's own no-tracked-identifiers rule.)

Separately verified (not a listed verification command, but the third acceptance condition depends
on it): `git add -f` of a file under `_private/portfolio/` is caught by the path check independent
of content —

```
$ mkdir -p _private/portfolio/test_dir && echo '{"id":"leak-test"}' > _private/portfolio/test_dir/leak.json
$ git add -f _private/portfolio/test_dir/leak.json && uv run python tools/check_no_private_content.py
check_no_private_content: FAILED
  - tracked file under a private path: _private/portfolio/test_dir/leak.json
exit=1
```

`uv run pytest test/test_private_content.py`:

```
12 passed, 2 warnings
```

`uv run python -m src.governance`:

```
Governance OK: 16 systems, 103 documents, 13 memories, 101 backlog phases
```

`uv run pytest`:

```
369 passed, 2 warnings
```

## Acceptance

- The checker fails on a deliberately planted identifier in a tracked file — **Met**. Shown above:
  planting a real, non-tracked project id in a newly force-added tracked file makes the checker
  exit 1 and name both the compound id and the bare client identifier.
- The checker passes on the cleaned tree and runs in CI before the other gates — **Met**. The
  checker exits 0 against the current tracked tree (251 files, 30 derived identifiers), and
  `.github/workflows/ci.yaml` runs it as the first step after `uv sync`, ahead of the governance
  check. Reaching a clean tree required scrubbing 19 tracked files phase-priv-02 had missed (see
  Decisions) — the checker surfaced them by doing its job, not by being loosened to avoid them.
- `git add -f` of a private file is caught by the checker rather than only by `.gitignore` —
  **Met**. Shown above: force-adding a file under `_private/portfolio/` is caught by the
  path check independent of its content.

## Backlog

`status: active`. `next_action`: write the session record and hand off for owner review (done by
this record) — `phase-priv-04`'s own work is complete by its acceptance conditions, but per
`AGENTS.md` only `session-close` may write `status: complete`.

`session: doc-session-leak-check`. `completion_evidence`: `tools/check_no_private_content.py`,
`tools/git-hooks/pre-commit`, `.gitignore`, `.github/workflows/ci.yaml`,
`test/test_private_content.py`, `docs/08-governance/OPS-009-check-no-private-content.md`,
`docs/07-architecture/ARCH-001-tagging-system.md`, `templates/README.md`,
`docs/03-sessions/SESS-2026-09-06-04-entity-contracts.md`,
`docs/03-sessions/SESS-2026-09-08-12-scrub-tracked-structure.md`,
`docs/03-sessions/SESS-2026-09-08-13-relocate-portfolio.md`, `docs/09-backlog/backlog.yaml`, this
session record.

`result`: Built `tools/check_no_private_content.py` (path check + runtime-derived content check,
never itself tracking real identifiers), wired it into CI ahead of governance, added
`tools/git-hooks/pre-commit` plus `docs/08-governance/OPS-009-check-no-private-content.md`, and
`.gitignore` now names the private portfolio paths explicitly. Orientation surfaced that the
checker's own derived identifier list found 22 tracked files phase-priv-02 had missed; the owner
approved scrubbing them within this phase rather than deferring, except one lower-sensitivity real
project identifier (explicitly left out — see Decisions) which is exempted in the checker with a
named, visible reason rather than silently passing. Full verification suite (above) is green:
checker OK, both plant tests fail
correctly, `test_private_content.py` (12 new tests) passes, governance OK at 103 documents, full
`pytest` at 369.

## Unresolved

- One real project identifier (12 hits across `systems.yaml`, `ADR-012`, `PLAN-015`, `backlog.yaml`
  and four session records) is a real but lower-sensitivity leak — the owner's own extracted course,
  not a client — deliberately left unscrubbed this session and excluded from the checker's
  identifier set via `EXEMPT_IDENTIFIERS` with a named reason. It remains a known gap the checker
  will not catch; a future phase should decide whether to scrub it, and `phase-priv-05` (history
  rewrite) needs to account for it explicitly before any push, since its own acceptance text
  requires no tracked file or commit to name a real project outside `_private/`. (Resolved by
  `phase-priv-06`, which purged it.)
- `EXEMPT_IDENTIFIERS` also carries `artifact-code-generation` (a coincidental name collision with
  the structural document `docs/02-prompts/PROMPT-001-artifact-code-generation-system.md`, not a
  leak) — no action needed, recorded so a future reader does not mistake the exemption for an
  oversight.

## Decisions

- Orienting surfaced that the checker's identifier derivation (real project filenames plus any
  filename prefix repeated across 2+ real projects) found 22 tracked files with genuine leftover
  leaks beyond phase-priv-02's original six-location audit — mostly session records narrating real
  work by name, plus `GLOSSARY.md`, `catalog.md`, `backlog.yaml`, `systems.yaml`, `.gitignore`,
  `ADR-012`, `PLAN-015`, and two doc/title collisions. Asked the owner whether to scrub now
  (widening this phase) or split into a follow-up phase; they chose to scrub now, so the phase's own
  acceptance condition ("passes on the cleaned tree") would be true rather than aspirational.
- Separately asked whether one identifier with materially different sensitivity — the owner's own
  product, not a client, and embedded in closed governance history about a completed phase rather
  than isolated mentions — should be scrubbed in the same pass. The owner chose to leave
  it out, given its lower sensitivity and the disruption of rewriting seven closed governance
  documents' historical record for a single-session phase. Recorded as `EXEMPT_IDENTIFIERS` with a
  reason rather than silently narrowing the checker's derivation logic, so the gap stays visible on
  every run rather than disappearing into the algorithm.
- Also asked whether the two same-name collisions (`artifact-code-generation`, and a real project id
  matching the phrase "HTML Generation Framework") were leaks or coincidences. The owner agreed with
  the read that
  `PROMPT-001`'s filename is genuinely structural (ADR-009's test) and should stay as-is with an
  exemption, while `templates/README.md`'s phrasing — which named this very repository as if it
  were a private portfolio entry — should be reworded rather than exempted, since the string itself
  was gratuitous (removing it lost no information).
- Chose to derive the client-identifier heuristic (a filename prefix repeated across 2+ real
  projects) against `_data/tags.json`, excluding any prefix that already appears there as a
  deliberately-kept tag id/label. Without this cross-check the heuristic also caught `anaplan` —
  a real platform name the sweep intentionally kept as public vocabulary (like `aws` or
  `playwright`), not a client identifier — which would have made the checker flag, and this session
  nearly scrub, content that was correct as tracked. Verified against the actual tag registry before
  committing to the rule rather than assuming a fixed threshold would separate the two cases.
- The confidential-identifier list is derived at runtime from `_private/portfolio/` and
  `_data/tags.json` and is never written to a tracked file — raised directly by the owner mid-session
  ("as long as the hardcoding is not tracked, because tracking the sensitive client names would
  itself be a breach of confidentiality") and confirmed by rerunning the checker with no
  `_private/portfolio/` present, where it correctly falls back to the path-only check.
- Wrote `tools/git-hooks/pre-commit` as a plain shell script installed via
  `git config core.hooksPath tools/git-hooks`, rather than adopting the `pre-commit` framework —
  the owner's choice, given no such framework exists in this repository yet and the check is a
  single command with no need for the framework's multi-hook orchestration.

## Corrections

The `## Verification` section originally quoted `Governance OK: ... 102 documents ...` for both the
`uv run python -m src.governance` run and the summary line in `## Backlog`'s `result`. The
independent review (below) caught that the live count is 103 — the session record and `OPS-009`
document themselves account for the +2 over the 101-document baseline this phase started from, and
the governance output pasted into this record had been captured before both existed. Corrected both
occurrences to 103, which matches a fresh rerun and the regenerated `docs/08-governance/catalog.md`
exactly. No other claim in this record was found wrong by the independent review or by rerunning any
verification command.

## Left undone

- The one exempted identifier remains unscrubbed (see `## Unresolved` above) — a deliberate, named
  gap, not an oversight, but real work `phase-priv-05` must account for before any push. (Later
  resolved by `phase-priv-06`.)
- This session's changes are all still uncommitted on `dev` — no commit was made during the session
  itself. Committing (and, per `AGENTS.md`, never as part of an agent's own judgement to push) is
  left to the owner alongside this closure.

## Review

Independent sub-agent review, launched fresh (no shared context with this session), reviewing the
uncommitted working-tree diff against HEAD (the commit “Close phase-priv-03 via /session-close”) since nothing had been committed:

> ## Verdict
>
> All 3 acceptance conditions hold, independently verified. No discrepancies found in the
> diff/logic itself. One minor documentation staleness noted below (non-blocking).
>
> ### Acceptance condition 1 — checker fails on a deliberately planted identifier
>
> Confirmed. `_private/portfolio/projects/` exists with 34 files including three real files for the
> same client — the record's claimed identifier is real. Planted one of those real project ids in a
> force-added file myself: checker exited 1, flagging both the bare client identifier and the
> compound project id. Reverted cleanly.
>
> Grepped tracked `tools/check_no_private_content.py` and `test/test_private_content.py` for the
> real client identifier and the real platform name — no real identifier is hardcoded. The only
> platform-name hits are fictional test fixtures (`anaplan-widget-build`, `anaplan-gadget-launch`
> in `test_private_content.py`),
> consistent with the runtime-derivation design goal. `confidential_identifiers()` genuinely
> computes the list at runtime from `_private/portfolio/` + `_data/tags.json`
> (`tools/check_no_private_content.py:93-112`).
>
> ### Acceptance condition 2 — checker passes on cleaned tree, runs in CI before other gates
>
> Confirmed. `uv run python tools/check_no_private_content.py` exits 0: `251 tracked files, 30
> identifiers checked` — matches the session record exactly. `.github/workflows/ci.yaml` diff adds
> the checker step immediately after `uv sync --extra dev` and before
> `uv run python -m src.governance`, the catalog check, ruff, mypy, and pytest — genuinely first.
>
> ### Acceptance condition 3 — `git add -f` of a private file caught by path check
>
> Confirmed independently. Force-added `_private/portfolio/test_dir/leak.json`; checker failed
> specifically with `tracked file under a private path: _private/portfolio/test_dir/leak.json` (the
> path-check message, not a content-check message). Unstaged and deleted the test artifact;
> `git status` clean afterward.
>
> ### Full verification suite (rerun myself)
>
> - `uv run pytest test/test_private_content.py` → 12 passed (matches record)
> - `uv run python -m src.governance` → `Governance OK: 16 systems, 103 documents, 13 memories, 101
>   backlog phases`
> - `uv run python -m src.governance --catalog` diffed against tracked `catalog.md` → clean, zero
>   diff (catalog is current)
> - `uv run pytest` (full suite) → 369 passed (matches record exactly)
>
> **One discrepancy**: the session record's own pasted governance output says "102 documents," but
> a fresh run now shows 103, and the tracked `catalog.md` diff itself confirms 103 (footer: `103
> documents — ... operation: 9 ... session: 34`, up from 101). This is minor documentation
> staleness — the record's quoted output was likely captured before the session record file itself
> (`SESS-2026-09-08-14...md`) was finalized and counted, since that file plus `OPS-009` together
> account for the +2. Not a functional defect: catalog.md is correct and matches the live count
> exactly.
>
> ### Scrub-quality spot check (5 files)
>
> Reviewed `docs/03-sessions/SESS-2026-09-08-12-scrub-tracked-structure.md`,
> `SESS-2026-09-08-13-relocate-portfolio.md`, `SESS-2026-09-06-04-entity-contracts.md`,
> `docs/07-architecture/ARCH-001-tagging-system.md`, `templates/README.md`. All edits read
> coherently — no broken grammar, no self-referential "renamed from X" where X was itself redacted.
> The real-client-identifier substitutions are contextually sound throughout, including inside
> quoted historical sub-agent review blocks.
>
> Grepped the whole tracked tree (excluding `_private/`) for claimed-removed identifiers: the bare
> client identifier and every real compound project id named in the session record's Decisions
> section — zero hits outside `_private/` and outside the test file's unrelated fictional fixtures.
>
> The one identifier left exempted (see Unresolved) was confirmed still present across several
> tracked files, consistent with the deliberate exemption described there.
>
> ### Exemption mechanism
>
> `EXEMPT_IDENTIFIERS` in `tools/check_no_private_content.py:62-75` genuinely exists, carries
> exactly two identifiers with the stated reasons, and is subtracted only from
> `confidential_identifiers()` (line 112) — `check_paths()` never consults it, so it cannot silence
> a path-check violation. This matches the record's claim precisely.
>
> ### Overall
>
> The phase's uncommitted diff, as it stands, satisfies all 3 declared acceptance conditions, and
> the full verification suite is genuinely green (369/369, 12/12, governance clean, catalog clean).
> The only flaw found is the cosmetic 102-vs-103 document count in the session record's pasted
> verification transcript, which doesn't affect any acceptance condition since the live catalog.md
> is correct.

The one discrepancy the review found (the 102-vs-103 count) is the same one already fixed above in
`## Corrections`, before this section was written. No unresolved discrepancy remains.
