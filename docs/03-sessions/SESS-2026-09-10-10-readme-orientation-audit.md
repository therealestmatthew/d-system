---
schema_version: 1
id: doc-session-readme-orientation-audit
code: SESS-2026-09-10-10
title: README and GOV-007 orientation audit; idea 000091 recorded
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-governance, sys-portfolio]
depends_on: []
---

# README and GOV-007 orientation audit; idea 000091 recorded

## Phase

**None.** No phase was claimed for this session, and none reached any status as a result of it.

The owner opened the session by asking for an audit of `README.md` — specifically to remove the
Current Inventory section's project counts, which described gitignored `_private/portfolio/` records
inside a tracked file. That work grew into a second document (`GOV-007`) and an idea, none of it
under a backlog claim.

This is the process deviation `brain/procedures/session-close-with-no-active-phase.md` exists to
name rather than hide, though in a variant that procedure does not literally cover: there, a phase
closed mid-session and work continued past it; here no phase was ever claimed at all. The work was
documentation-only and touched no `src/`, `ts/`, `schemas/`, `sql/`, `tools/` or `test/` path, so
`AGENTS.md`'s worktree requirement did not bite — but a claim would still have made the work visible
to the two peer agents committing to `dev` throughout (`agent-codex-port` on `phase-port-01`,
`agent-demo-glossary` on `phase-demo-07`).

## Verification

No phase means no declared `verification` list. These are the checks actually run, with their real
output.

```
$ uv run python -m src.governance
Governance OK: 18 systems, 153 documents, 15 memories, 119 backlog phases
```

```
$ uv run pytest
495 passed, 2 warnings
```

```
$ uv run python tools/check_no_private_content.py     # run with changes staged
check_no_private_content: OK (449 tracked files, 31 identifiers checked)
```

These counts drifted upward *during* the session — document count went 150 → 153 and tracked files
449 → 451 — because two peer agents were committing to `dev` throughout. The numbers above are the
final state; an earlier draft of this record recorded 150, which was true when run and stale within
the hour. The systems, memory and phase counts did not move.

The `pytest` line is also a post-fix number. The review below caught the suite red at
`1 failed, 494 passed` — `test_codes.py::test_committed_catalog_matches_regenerated_output`, because
this record itself was written but `docs/08-governance/catalog.md` had not been regenerated to carry
its row. Regenerating the catalog fixed it.

```
$ uv run python tools/append_idea.py add --file <scratchpad>/idea-agents-push-rule.txt
created 000091 at 2026-09-10T18:16:47-04:00
```

```
$ uv run python tools/generate_ideas_md.py
wrote docs/00-working/ideas.md — 91 ideas
```

Facts asserted in the rewritten documents were each checked against the repository before being
written — `_data/` file counts, the 28 tags, the DuckDB table and view inventory, `load_context.py`'s
argument list, the venv's Python version against `pyproject.toml`, the `project_people` population
path in `tools/rebuild_db.py`, and the existence of every path the README links to.

## Acceptance

No phase means no declared `acceptance` list, so there is nothing to mark `Met` or `Not met`. The
owner's stated requirement — remove the projects section and find other inconsistencies — was met;
the four judgement calls it raised were put to them via `AskUserQuestion` and answered before any
edit was written.

## Backlog

`docs/09-backlog/backlog.yaml` was **not touched by this session**. No claim was made, no phase
status changed, and `next_up` was not pruned.

The only queue-adjacent write was `docs/00-working/ideas-priority.yaml`, which is the idea priority
queue, not the backlog: idea `000091` was appended to the back of `next_up` at the owner's
instruction to mark it "priority-ish."

## Unresolved

- **The `AGENTS.md` push-rule rewrite is approved but not applied.** The owner approved the plan;
  `.claude/settings.json` lines 4-7 hard-deny `Edit(AGENTS.md)` and `Write(AGENTS.md)`, and a deny
  rule overrides an approval at the tool level. Parked as idea `000091` with the full context and a
  pointer to the plan file. Two mechanical questions were put to the owner and deferred for time:
  whether they apply the hunks by hand or lift the deny for the duration, and whether the change
  commits and pushes when applied.
- **`GOV-007` is now corrected but was stale for two days** without anything detecting it. Nothing
  in the governance check validates a document's factual claims against the repository it describes;
  the check confirms front matter, codes and references, not whether a table list matches the DDL.
  The independent review below demonstrates the same gap from the other side — it caught two false
  claims this session newly introduced, and no mechanical check would have. No phase is proposed
  for this; it is recorded as an observation, not a recommendation.
- **`sys-contracts` in `docs/08-governance/systems.yaml` is stale** and was left that way. It
  describes the source preflight as enforcing six schemas and omits `task`; the preflight actually
  enforces eleven (`src/db/source_validation.py`). `systems.yaml` is a declared path of
  `sys-contracts` and this session held no claim, so `GOV-007` now names the discrepancy and points
  at the code as the authority rather than editing the registry.

## Review

An independent sub-agent (fresh context, not a fork) reviewed commits `7f58cbe` and `d529f26`
against repository reality and re-ran the checks. Its findings, condition by condition:

**Scope.** "The two commits touch exactly five files and nothing else: `README.md`,
`docs/08-governance/GOV-007-repo-orientation.md` (7f58cbe); `_data/ideas.jsonl`,
`docs/00-working/ideas-priority.yaml`, `docs/00-working/ideas.md` (d529f26). No `src/`, `ts/`,
`schemas/`, `sql/`, `tools/`, `test/` or `backlog.yaml` path in either."

**Verified correct, no discrepancy:** the DuckDB table/view inventory ("Exact match… 14 entity
tables + 2 junctions + 3 views — accounts for all 19 relations, none missing, none invented",
cross-checked against `information_schema.tables`); tasks as separate records; `project_people`
population from the person JSON's `projects` array; `ideas` folded from `idea_events` with `fold()`
at `src/db/ideas.py:230`; all seven `load_context.py` flags ("All seven correct, none missing");
the Python version claim ("Both halves correct"); `ideas.jsonl` written only by `append_idea.py`
("`tools/demo_reset.py` is the one other candidate and it loads append_idea as a module"); every
markdown link ("README… 8/8 exist. GOV-007… 2/2 exist"); the tool/OPS pairing ("True and
machine-enforced… 12 `.py` tools, 12 matching OPS documents"); and every directory entry in both
listings.

**Error (a) — GOV-007's schema/preflight claim was false.** "`sys-contracts` lists **six** schemas…
It does **not** include `task`, which GOV-007's own preceding clause names. So the sentence is
self-contradicting: it names seven and then points at a record listing six. Worse, neither number is
the truth. `src/db/source_validation.py:53-62` (`ENTITY_DIRECTORIES`) makes the preflight enforce
eight entity schemas… plus `tag` (:165), `memory` (:245) and `idea` (:279). That is **eleven**…
this diff newly introduced the pointer asserting it is authoritative for that set, so the false
claim now lives in GOV-007."

*Verified independently and fixed.* GOV-007 now states the eleven, cites
`src/db/source_validation.py` as the authority, and names `sys-contracts` as stale.

**Error (b) — README's `brain/index.md` pointer was inaccurate.** "The index's Memory Inventory
lists 10 entries; `brain/` holds 15 memory files… The replacement is still better than the
'*Current memory count: 7 entries*' it displaced, but it points a reader at a stale index and
asserts it is current."

*Verified independently and fixed.* The README now points at `uv run python -m src.governance` for
the count and says plainly that the index does not list them all.

**Precision note — the task/commitment relationship was overstated.** "`schemas/task.schema.json`
types `commitment_id` as `["string","null"]`… 'Both parents are optional… Parentless tasks are real
and intended'… true of the example set but overstates the contract."

*Fixed.* Both GOV-007 passages now say the parents are optional and name the `unfiled` view.

**Precision note — commit message arithmetic.** "7f58cbe says '8 of 18 DuckDB tables' and '7 of 18
tables'. The actual count is 16 tables, or 19 relations counting views. Neither reading yields 18.
The document itself is correct; only the commit message is off."

*Accepted, not corrected.* The commit is pushed; amending published history to fix a count in a
message is not worth the rewrite, and this record now carries the correction.

**Blocking finding — the suite was red.** "`1 failed, 494 passed`…
`test_codes.py::test_committed_catalog_matches_regenerated_output`… the catalog must be regenerated
before the session record is committed or the close lands a red suite on `dev`. The record does not
mention this outstanding step."

*Fixed.* Catalog regenerated; `495 passed, 2 warnings`.

**On removals, the reviewer checked whether information was lost** and found the project counts and
row counts correctly removed and unrecoverable-by-design, the tag count trivially recoverable, and —
having checked each named item — that "Planned But Not Yet Built" lost nothing: "Every one of those
names survives in `docs/08-governance/systems.yaml`… The pointer recovers everything the prose
carried, plus current status the prose did not."

**On the idea commit:** append-only property confirmed by numstat and a byte-identical comparison of
the first 378 lines; `ideas.md` confirmed current via `generate_ideas_md.py --check`; priority queue
ids all resolving to `open` or `triaged`; and "The appended log line's id, timestamp and eid… match
the `append_idea.py` output quoted in the session record exactly — the id was taken from the writer,
not guessed."

**On this record's honesty:** the no-phase claim, the untouched `backlog.yaml`, and the peer-agent
claim were each independently confirmed. It judged the record "candid," and flagged two omissions —
that the verification numbers drifted within the hour from peer commits, and that the catalog
regeneration was still outstanding. Both are now addressed above.

## Decisions

The audit opened on a specific complaint — the README's Current Inventory reported counts of the
owner's real portfolio, which lives gitignored at `_private/portfolio/`, inside a tracked file. Four
judgement calls followed and all four went to the owner rather than being decided here:

- **Drop the whole inventory section rather than correct it.** Every count in it had drifted at least
  once, and `tools/generate_overview.py` computes the same numbers against whichever data root is
  active. Correcting them would have reset a clock, not stopped it.
- **Delete the memory count outright** rather than update 7 → 15, for the same reason.
- **Add a Working Agreement section.** The README had no pointer to `AGENTS.md`, the governance
  documents or the backlog — the conventions that actually govern work here. For a repository whose
  premise is that any of three model families can pick it up, that was the largest single gap.
- **Replace "Planned But Not Yet Built"** — a snapshot naming 2 of 22 plans — with pointers to the
  backlog and `systems.yaml`, which carry live status.

Two decisions were the owner's alone and overrode the recommendation on the table:

- **The `AGENTS.md` push rule is a general rule plus a deliberate exception, not a contradiction.**
  The recommendation was to pick a survivor between the two passages. The owner rejected that: both
  are correct, and only the wording hides which is which. The plan was rewritten to make the
  structure legible in both places.
- **Park it rather than apply it.** With the plan approved and then blocked by the `settings.json`
  deny on `Edit(AGENTS.md)`, the owner deferred the mechanical question for time and directed it be
  marked priority-ish — hence idea `000091` and the priority-queue entry, rather than a backlog
  phase or a half-applied edit.

## Corrections

- **The push rule was mischaracterised as a contradiction.** Two `AGENTS.md` passages were read as
  conflicting and a plan was written to pick a survivor. They are one general rule and one
  deliberate exception. The owner corrected it; the plan was rewritten to preserve both and make
  the relationship explicit. This is the correction that produced `000091`.
- **`OPS-001` was described as the index of tool operations documents.** It is not — it is the
  governance operations document. Caught and fixed before the commit; the README points at the
  catalog instead.
- **Two false claims were written into the very documents this session set out to make accurate**
  (the eleven-vs-six schema count, and the `brain/index.md` pointer). Both were caught by the
  independent review, not by any check, and both are fixed above. That the failure mode of a
  correctness audit is introducing new incorrect claims is the most useful thing this session
  produced.

## Left undone

- **The `AGENTS.md` rewrite.** Approved, blocked at the tool level, parked as `000091` at the back
  of the idea priority queue. Two questions remain open for whoever picks it up: whether the owner
  applies the hunks by hand or lifts the deny for the duration, and whether the change commits and
  pushes when applied.
- **`sys-contracts` remains stale.** Correcting it means editing `docs/08-governance/systems.yaml`,
  a declared path of the very system it describes, while holding no claim and with a peer active on
  `sys-governance`. `GOV-007` names the discrepancy instead. A phase should own the fix.
- **`brain/index.md` lists 10 of 15 entries.** The five `terms-*.md` concept memories are absent.
  The README no longer implies otherwise, but the index itself was not updated — it is a curated
  document, and deciding what belongs in it is not this session's call.
- **No phase was claimed for any of this work.** The fix is to claim earlier next time, not to
  manufacture a retroactive claim now.
