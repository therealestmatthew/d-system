---
schema_version: 1
id: doc-session-purge-course-identifier
code: SESS-2026-09-08-15
title: Remove the standing checker exemption and purge the remaining identifier
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-delivery, sys-governance]
depends_on: [doc-confidentiality-sweep]
---

# Remove the standing checker exemption and purge the remaining identifier

## Phase

`phase-priv-06` — Remove the standing checker exemption and purge the remaining identifier.

## Verification

`uv run python tools/check_no_private_content.py`:

```
check_no_private_content: OK (255 tracked files, 31 identifiers checked)
```

`uv run python -m src.governance`:

```
Governance OK: 16 systems, 103 documents, 13 memories, 101 backlog phases
```

`uv run pytest`:

```
369 passed, 2 warnings
```

Not a listed verification command, but worth recording since it caught a real gap: the checker was
rerun against the fully **staged** tree (`git add -A` first), not just the working tree, since
`git ls-files` — what the checker and the pre-commit hook both use — only sees the index. An earlier
unstaged run had silently skipped `phase-priv-04`'s own new session record, which still quoted
several real identifiers verbatim as evidence. Once staged, the checker correctly flagged it; fixed
in this phase (see Decisions).

Planted the now-purged identifier itself in a force-added file to confirm the checker treats it like
any other real project id with no lingering exemption:

```
$ echo "test leak: <the identifier> mentioned here" > _scratch_plant2.md && git add -f _scratch_plant2.md
$ uv run python tools/check_no_private_content.py
check_no_private_content: FAILED
  - _scratch_plant2.md: matches confidential identifier '<the identifier>'
exit=1
$ git reset _scratch_plant2.md && rm -f _scratch_plant2.md
```

At `/session-close`, a broader grep for the deleted backlog phase's id (`phase-scope-01`, not the
confidential identifier the checker covers) across all of `docs/` — not just `depends_on` fields —
found two current, non-narrative documents still citing it as a live fact:
`docs/07-architecture/ARCH-004-architecture-overview.md`'s system table and
`docs/04-decisions/ADR-012-systems-review.md`'s reasoning text. Both reworded to state the fact
(the course was extracted to its own repository) without the dead id. Remaining hits are all inside
session records narrating what happened at the time, which is a legitimate use of a since-removed
id — left as-is.

## Acceptance

- The checker passes on the cleaned tree with no exemption for this identifier — **Met**. Shown
  above: `EXEMPT_IDENTIFIERS` in `tools/check_no_private_content.py` no longer carries it, and the
  full staged tree still passes (256 files, 31 identifiers — up from 30, since the identifier is now
  actively checked instead of exempted).
- Nothing depends_on the deleted session record or backlog phase (verified before deleting, not
  assumed) — **Met**. Grepped for `doc-session-2026-09-07-04` and `phase-scope-01` across
  `docs/` before deleting either; only the phase's own entry and its own session record referenced
  them structurally, both being removed together. Governance and the full suite pass after removal.
  A second, broader grep at close (see Verification above) found two current documents citing the
  id in prose rather than in a structural field — not a `depends_on` violation, but a dangling
  reference the original check did not think to look for. Both fixed; see Corrections.
- Every reworded passage still reads coherently and preserves its original point — **Met**. Every
  file touched was read back after editing; no broken grammar or self-referential nonsense
  (the "renamed from X" failure mode from `phase-priv-04` was checked for specifically and not
  repeated here).

## Backlog

`status: active`. `next_action`: All three acceptance conditions are Met (see this record). Owner
review and `/session-close` needed to mark this phase complete; not done by this session.

`session: doc-session-purge-course-identifier`. `completion_evidence`:
`tools/check_no_private_content.py`, `docs/04-decisions/ADR-012-systems-review.md`,
`docs/08-governance/systems.yaml`, `docs/01-plans/PLAN-015-ephemeral-working-plans.md`,
`.gitignore`, `docs/09-backlog/backlog.yaml`, this session record.

`result`: Deleted the extraction session record and its now-orphaned backlog phase — confirmed
first that nothing else referenced either. Reworded the identifier out of `.gitignore`,
`ADR-012`, `systems.yaml`, `PLAN-015`, and five session records (three from `phase-priv-04`'s own
scrub pass plus two more this phase found: `SESS-2026-09-06-08` and `SESS-2026-09-06-10`, which
hadn't been touched before since the identifier was still exempted then). Removed the
`EXEMPT_IDENTIFIERS` entry. Also fixed a verification gap in the closed `phase-priv-04`'s own
session record, which still quoted several real identifiers verbatim — found only because this
phase's rerun used a fully staged tree rather than the working tree the earlier session had checked.
Full verification (checker, governance, full pytest, both plant tests) all green.

## Unresolved

None.

## Decisions

- The owner asked directly whether the extracted course's session record and backlog phase still
  carried value now that the extraction itself was independently confirmed complete in a separate
  repository. Judged they did not, and deleted both rather than redacting them in place — the
  alternative this session had planned (rename the session file, rewrite its ~24 mentions, keep the
  backlog phase as historical record) was substantially more invasive for no retained value once the
  owner made clear the content itself, not just its identifier, was disposable.
- Before deleting, verified nothing else referenced either the session record's document id
  (`doc-session-2026-09-07-04`) or the backlog phase id (`phase-scope-01`) — a grep across `docs/`
  found only the phase's own entry and its own session record. Governance and the full suite passing
  after removal is the actual proof; the grep was the check before acting, not a substitute for it.
- Discovered mid-session that the checker's `tracked_files()` (via `git ls-files`) only sees the
  index, not the working tree — meaning any unstaged new file is invisible to it. This is correct
  behavior for the pre-commit hook (files are staged by the time it fires) but meant every manual
  verification run this session and in `phase-priv-04` needed `git add -A` first to be meaningful.
  Re-ran the checker against the fully staged tree specifically because of this, which is what
  surfaced the gap in `phase-priv-04`'s own session record.
- Reworded rather than deleted the five affected session records (`SESS-2026-09-06-08`,
  `SESS-2026-09-06-10`, `SESS-2026-09-07-06`, `SESS-2026-09-08-13`, and `phase-priv-04`'s own
  `SESS-2026-09-08-14`) — these carry substantial unrelated content (cadence rename work, idea-list
  architecture, a five-phase session overview, the portfolio relocation, the leak-checker build) and
  deleting them to remove a handful of incidental mentions would have destroyed real information.
  This mirrors the same in-place-redaction approach `phase-priv-04` used, extended to two records
  (`SESS-2026-09-06-08`, `SESS-2026-09-06-10`) that phase hadn't touched because the identifier was
  still exempted at the time.

## Corrections

`phase-priv-04`'s own session record (`SESS-2026-09-08-14-leak-check.md`) was found, mid-session, to
still quote several real identifiers verbatim in its Verification and Review sections — the plant
test's example identifier, and the sub-agent review's spot-check output. This had passed that
session's own checker run because the file was never staged when the checker ran (see Decisions).
Redacted all of it to generic descriptions consistent with the rest of that record's existing
redaction style. This is a correction to a record from a different, already-closed session, made
here because fixing it required exactly the tooling and context this phase already had loaded, and
leaving it wrong until some future phase happened to touch that file again was worse than fixing it
on discovery.

At `/session-close`, the acceptance re-check for "nothing depends_on the deleted id" turned up two
current documents — `ARCH-004-architecture-overview.md` and `ADR-012-systems-review.md` — still
citing the deleted `phase-scope-01` id as a live fact, which the original pre-deletion grep missed
because it only checked structural `depends_on` fields, not prose. Both fixed (see Verification).
The lesson: "nothing depends on it" needs a text search across `docs/`, not just a schema-field
check, whenever a deletion removes an id that other documents might cite by name rather than by a
governed reference.

## Left undone

One item the independent review surfaced that this session did not act on:
`_tmpagent/AGENTS.md`'s "Worked sequence" section contains an illustrative, dated JSONL example
that references `phase-scope-01` as a past, already-removed claim. That file is explicitly
ungoverned (its own header excludes it from the governance scan) and the reference reads as
historical narration — the example's own last line shows the phase already complete and its file
already removed — the same category this phase already treats as acceptable in session records.
Left as-is rather than edited on the reviewer's finding alone; noted here so it is a deliberate
choice, not a miss repeated silently. If it should be scrubbed, that is a small follow-up, not a
reason to hold this phase open.

Otherwise nothing. This phase's scope is fully addressed. `phase-priv-05` (history rewrite) can now
proceed once phases priv-01 through priv-04 and priv-06 are all `complete` — this phase removes the
last named blocker in its `resume_when` text.

## Review

Independent sub-agent review, launched fresh (no shared context with this session), reviewing the
combined uncommitted working-tree diff against HEAD (the commit “Close phase-priv-03 via /session-close”) — both `phase-priv-04` and
`phase-priv-06` remain uncommitted, so the diff includes both, but the review was scoped explicitly
to this phase's 3 acceptance conditions only:

> This all matches the phase scope as declared. Status is still `active` (not complete), consistent
> with the record's claim that closure is pending owner review.
>
> ## Findings
>
> **Condition 1 — checker passes with no exemption**: Met. `uv run python
> tools/check_no_private_content.py` → `check_no_private_content: OK (256 tracked files, 31
> identifiers checked)`, exit 0. `EXEMPT_IDENTIFIERS` in `tools/check_no_private_content.py`
> (lines 62-69) contains only `"artifact-code-generation"` with its stated reason; the purged
> identifier is absent.
>
> **Condition 2 — nothing depends_on the deleted ids**: Met.
> The extraction session record's old file (its filename embedded the purged identifier) is
> confirmed deleted (`git status` shows `D`, file absent from disk).
> `grep "id: phase-scope-01" docs/09-backlog/backlog.yaml` →
> zero hits. Repo-wide grep for `doc-session-2026-09-07-04` and `phase-scope-01` outside
> `docs/03-sessions/` found only one hit not mentioned in the record: `_tmpagent/AGENTS.md` lines
> 64-70, a "Worked sequence" documentation example that uses `phase-scope-01` as an illustrative
> past claim/release/removal sequence. It's narrative and dated, and the example itself shows the
> phase already complete/removed rather than asserting it's live — closer in spirit to the
> session-record narration the acceptance condition explicitly allows than to a live-fact citation.
> It's not scanned by governance (per that file's own line 8) and isn't a `depends_on` violation.
> I'd call this a minor miss in the closure grep rather than a real gap, but it wasn't caught or
> mentioned, so flagging it. `ARCH-004-architecture-overview.md` and `ADR-012-systems-review.md` —
> the two corrections the record claims to have made — both verified clean: no `phase-scope-01`
> reference remains in either, and both read coherently in context.
>
> **Condition 3 — reworded passages read coherently**: Met on all files checked (`.gitignore`,
> `PLAN-015`, `ADR-012`, `systems.yaml`, `ARCH-004`, and the three session records
> `SESS-2026-09-06-08`, `SESS-2026-09-06-10`, `SESS-2026-09-07-06`). No broken grammar, no dangling
> markdown links (the `[SESS-2026-09-07-04](...)` link in `SESS-2026-09-07-06` was properly
> removed, not left dangling), no self-referential nonsense.
>
> **Enforcement plant test**: Force-added a file containing the purged identifier; checker correctly
> failed, flagging it by name, exit 1. Cleaned up (`git reset` + `rm`). Independently confirmed the
> corresponding real project file exists under `_private/portfolio/projects/`, so the identifier is
> real and derivable, not a decorative string.
>
> **Verification commands**: `uv run python -m src.governance` → `Governance OK: 16 systems, 103
> documents, 13 memories, 101 backlog phases`. Note: the session record claims **102 documents**; I
> independently got **103** on two separate runs. Minor discrepancy in the record's pasted output —
> doesn't affect pass/fail, and governance still exits clean, but the number in the record doesn't
> match a live rerun. `uv run pytest` → `369 passed, 2 warnings`, matches the record exactly.
> `--catalog` output diffed byte-identical against tracked `docs/08-governance/catalog.md`.
>
> **phase-priv-05 unblocking claim**: Confirmed — `phase-priv-05`'s `depends_on` list (backlog.yaml
> line 2313-2315) is `[phase-priv-04, phase-priv-06]`, so phase-priv-06 is indeed a named blocker
> as the record states.
>
> ## Overall verdict
>
> All 3 acceptance conditions hold on independent verification. Two minor, non-blocking
> discrepancies worth surfacing to the owner before close: (1) an unflagged `phase-scope-01`
> mention in `_tmpagent/AGENTS.md`'s worked-example ledger — arguably legitimate historical
> narration but not caught by this session's grep or mentioned in its Corrections section; (2) the
> session record's pasted governance output says 102 documents where a fresh rerun says 103 —
> cosmetic, doesn't change the pass/fail outcome. Neither discrepancy undermines the three
> acceptance conditions as declared.

Both discrepancies the review found were corrected in this record before closure: the 102-vs-103
count is fixed in `## Verification` above, and the `_tmpagent/AGENTS.md` finding is now recorded
above in this section rather than left unmentioned. No unresolved discrepancy remains.
