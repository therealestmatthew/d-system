---
schema_version: 1
id: doc-session-2026-09-08-idea-priority-queue
code: SESS-2026-09-08-08
title: Build the idea priority queue
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-portfolio, sys-governance]
depends_on: [doc-idea-priority-queue]
---

# Build the idea priority queue

## Phase

`phase-idea-09` — Add an ordered priority queue for open ideas.

## Verification

```
$ uv run pytest -q
371 passed, 2 warnings
```

```
$ uv run python -m src.governance
Governance OK: 16 systems, 94 documents, 13 memories, 99 backlog phases
```

```
$ uv run python tools/generate_ideas_md.py --check
docs/00-working/ideas.md is current
```

Additionally verified by hand, twice — once during implementation and once independently
re-derived by the sub-agent reviewer (see `## Review` below) — by temporarily swapping
`docs/00-working/ideas-priority.yaml` for bad variants and confirming each failed governance with
the expected message, then restoring the real file exactly: unknown idea ID
(`next_up names unknown idea 999999`), terminal-status idea (`000039 is promoted, not open or
triaged — remove it from next_up`), and a future `updated` date (`updated is in the future`).

## Acceptance

- `ideas-priority.yaml` validates against its schema. — Met: `uv run python -m src.governance` is
  clean, which validates the file via `audit_idea_priority`; corroborated independently by the
  sub-agent review.
- `uv run python -m src.governance` fails on a next_up entry naming a nonexistent idea ID or one
  whose status is reviewing, promoted or discarded. — Met: confirmed by hand for all three cases
  above, covered by `test_inspect_idea_priority_rejects_unknown_and_terminal_ideas` and
  `test_inspect_idea_priority_rejects_a_future_updated_date`, and independently reproduced by the
  sub-agent review.
- `tools/generate_ideas_md.py` renders the priority order deterministically; running it twice with
  no source change produces an identical file. — Met: `test_regenerating_twice_produces_identical_output`
  passes; `generate_ideas_md.py --check` reports the file current; the sub-agent review ran it
  twice independently and diffed the two outputs as identical.
- No change to `tools/append_idea.py`, `schemas/idea.schema.json`, or any existing idea event. — Met:
  `git diff HEAD -- tools/append_idea.py schemas/idea.schema.json` is empty. Idea `000039` gained
  one new `status` event (`open` -> `promoted`, `promoted_to: PLAN-019`) appended through the
  sanctioned writer — an addition, not a change to an existing event; the sub-agent review confirmed
  `git diff HEAD -- _data/ideas.jsonl` shows only added lines, no altered ones.

## Backlog

`phase-idea-09` — `status: complete`, `agent: agent-claude`, `session: doc-session-2026-09-08-idea-priority-queue`.
`completion_evidence`: `schemas/idea-priority.schema.json`, `docs/00-working/ideas-priority.yaml`,
`src/governance/idea_priority.py`, `test/test_ideas.py`, `docs/00-working/README.md`. `result`:
implementation, verification and documentation are complete; independent sub-agent review found
one real gap (undocumented file, scope bullet 4) during review, which was fixed before close and
reverified.

## Unresolved

The two open questions recorded in `PLAN-019` are still genuinely open and were not resolved by
this implementation: whether reordering the queue should ever carry a logged reason, and whether
the future idea-triage agent (`phase-idea-02`) may propose reorderings or must stay out of ordering
entirely.

## Review

Independent sub-agent review (fresh, non-fork agent), reviewing `git diff HEAD` against the
working-tree changes (no commits were made this session) and rerunning every verification command
itself. Findings, verbatim from its report:

> ### Condition 1 — `ideas-priority.yaml validates against its schema`
>
> **Verdict: holds.**
>
> ```
> $ uv run python -m src.governance
> Governance OK: 16 systems, 94 documents, 13 memories, 99 backlog phases
> ```
>
> `schemas/idea-priority.schema.json` requires `schema_version` (`const: 1`), `updated` (date
> pattern, no future-date enforcement in the schema itself — that's delegated to
> `inspect_idea_priority`), and `next_up` (array of unique `^[0-9]{6}$` strings).
> `docs/00-working/ideas-priority.yaml` (`schema_version: 1`, `updated: '2026-09-08'`,
> `next_up: []`) matches. `additionalProperties: false` is set, so the schema is actually
> load-bearing, not decorative. Cross-file existence/status checks are correctly deferred to
> `inspect_idea_priority` per the schema's own description field — matches the plan's stated
> design.
>
> ### Condition 2 — governance fails on unknown ID or terminal status
>
> **Verdict: holds, independently reproduced.**
>
> I edited `docs/00-working/ideas-priority.yaml` in place (backed up first) and reran governance
> three times:
>
> - Unknown ID `999999`: `ERROR ideas-priority.yaml: next_up names unknown idea 999999`
> - Idea `000039` (confirmed `promoted` in `_data/ideas.jsonl`): `ERROR ideas-priority.yaml: 000039
>   is promoted, not open or triaged — remove it from next_up`
> - Future `updated: '2099-01-01'` (combined with the promoted-idea case, both errors fired
>   together): `ERROR ideas-priority.yaml: updated is in the future` plus the promoted-idea error
>
> Restored the file afterward; byte-diff against my pre-edit backup came back identical, and
> governance is clean again (`Governance OK: 16 systems, 94 documents, 13 memories, 99 backlog
> phases`). The wiring in `src/governance/__main__.py`'s `audit_idea_priority()` (only runs after
> doc/backlog audits pass, folds `_data/ideas.jsonl` via `src/db/ideas.fold`/`load_events`, and
> calls `inspect_idea_priority`) matches what the acceptance condition and `test_ideas.py`'s
> `test_inspect_idea_priority_rejects_unknown_and_terminal_ideas` /
> `test_ideas_priority_yaml_is_governance_clean` assert.
>
> ### Condition 3 — `generate_ideas_md.py` renders deterministically
>
> **Verdict: holds, independently reproduced.**
>
> Ran it twice back-to-back and diffed the outputs:
>
> ```
> $ uv run python tools/generate_ideas_md.py   # wrote docs/00-working/ideas.md — 40 ideas
> $ uv run python tools/generate_ideas_md.py   # wrote docs/00-working/ideas.md — 40 ideas
> $ diff run1.md run2.md && echo "RUN1==RUN2 IDENTICAL"
> RUN1==RUN2 IDENTICAL
> $ uv run python tools/generate_ideas_md.py --check
> docs/00-working/ideas.md is current
> ```
>
> `render()` is a pure function over `sorted(state)` and an explicit ordered `next_up` list (no
> dict-iteration-order or timestamp dependence), so determinism is structural, not incidental.
>
> ### Condition 4 — no change to `append_idea.py`, `idea.schema.json`, or existing events
>
> **Verdict: holds.**
>
> ```
> $ git diff HEAD -- tools/append_idea.py schemas/idea.schema.json
> (empty)
> ```
>
> `git diff HEAD -- _data/ideas.jsonl` shows only added lines (`+`), no `-` on any pre-existing
> line: four new `created` events (000037–000040) and one new `status` event for `000039` (`open`
> → `promoted`, `promoted_to: PLAN-019`). That status event is exactly the shape
> `tools/append_idea.py`'s `status` subcommand produces, and nothing in the diff rewrites an
> earlier line.
>
> ### Full test suite and governance, run fresh
>
> ```
> $ uv run pytest -q
> 371 passed, 2 warnings in 3.19s
> ```
> (Session record claims `371 passed, 2 warnings` — matches exactly.)
>
> ### Point 6 — backlog.yaml entry internal consistency
>
> `completion_evidence` lists `schemas/idea-priority.schema.json`,
> `docs/00-working/ideas-priority.yaml`, `src/governance/idea_priority.py`, `test/test_ideas.py` —
> all four exist and each genuinely demonstrates what it's cited for (schema, data file,
> validator, tests). `next_action` field is absent from the entry (I don't see a `next_action` key
> in the `phase-idea-09` block at all — only `result: "Implementation complete and verified ...
> Awaiting /session-close."`). The session record's Backlog section paraphrases a `next_action` of
> "Implementation and verification are done; nothing remains but /session-close review," but the
> actual backlog YAML I read has no `next_action` key on this phase — it only has `result`. This is
> a minor discrepancy between the session record's paraphrase and the literal backlog entry, though
> the substance (awaiting session-close) is consistent either way.
>
> ### Point 7 — "Document the new file and who may edit it"
>
> **Verdict: not done as scoped — a real gap.**
>
> PLAN-019 itself, step 5, explicitly prescribes: "Update `docs/00-working/README.md` (or wherever
> the ideas workflow is documented) to name the new file and who may edit it." I checked:
>
> - `git diff HEAD --stat -- docs/00-working/` shows only `ideas.md` (generated output) changed
>   plus the new untracked `ideas-priority.yaml` — `docs/00-working/README.md` was **not touched**.
> - Reading `docs/00-working/README.md` in full: its "Files" section still lists only `ideas.md`
>   and `codex-answers.md`. There is no mention of `ideas-priority.yaml` anywhere in it, and no
>   statement of who may edit it.
> - A repo-wide grep for `ideas-priority` outside code/tests/backlog turns up only the schema's own
>   `description` field (a design rationale, not an edit-authorization statement) and PLAN-019's
>   own prose.
>
> So the only documentation of the new file and its edit model lives in the plan document
> (`PLAN-019`, status `draft`) and inline code/schema comments — not in the targeted location the
> plan's own work list named. This scope bullet is not satisfied by what's in the diff.
>
> ### Summary
>
> All four `acceptance` conditions independently verified as holding, with the mutation tests
> reproduced by hand and the file restored cleanly. The one finding worth surfacing before
> `/session-close`: **scope bullet 4, "Document the new file and who may edit it," was not done**
> — `docs/00-working/README.md` was never updated, despite PLAN-019 itself specifying that exact
> file as the target. This should block a clean session-close, or be explicitly deferred/waived,
> rather than passed over silently.

**Disposition of the two findings, after the review returned:**

- **Point 7 (documentation gap): accepted and fixed.** `docs/00-working/README.md` gained a new
  rule 4 naming `ideas-priority.yaml`, describing its shape, who edits it (hand-edited by whoever
  reorders the queue, same as `backlog.yaml`'s `next_up`), and the governance constraint on its
  contents; a `Files` entry was added pointing to it. Re-verified after the fix: `uv run pytest -q`
  (371 passed), `uv run python -m src.governance` (clean, 94 documents), and
  `tools/generate_ideas_md.py --check` (current) all rerun and green.
- **Point 6 (`next_action` "missing"): checked, not a real discrepancy.** The field is present in
  `backlog.yaml` — it is simply the last key in the `phase-idea-09` block (after `deliverables`),
  well below where `result` sits near the top of the entry, matching every other phase's field
  ordering. The reviewer's read did not reach it; there was nothing to fix.

## Decisions

- **The priority list lives beside the append-only idea log, never inside it**, mirroring
  `backlog.yaml`'s `next_up` exactly — a plain hand-edited ordered list, not a new event type. This
  was decided in `PLAN-019` before this session and confirmed rather than revisited here.
- **Idea `000039` was promoted to `PLAN-019` mid-implementation, not left `open`.** The idea that
  proposed this exact feature no longer belongs in its own "look at next" list once the feature it
  asked for is built; seeding the queue with it would have been definitionally wrong. The queue was
  seeded empty instead, with the reasoning written into both the YAML file's comment and `PLAN-019`.
- **The owner directed the plan straight to the top of the backlog's `next_up`** (ahead of
  `phase-idea-02`, the idea-triage agent, which had just been moved there in the same session) and
  directed the implementation to proceed immediately after the plan was written, rather than
  pausing for a separate go-ahead. Both were owner instructions, not this agent's initiative.
- **Documentation of the new file was treated as fully satisfied by `PLAN-019`'s own prose during
  implementation** — this was a misjudgment, corrected in step 6 above once the independent review
  named the specific gap against the plan's own explicit instruction.

## Corrections

- The scope bullet "Document the new file and who may edit it" was initially left unaddressed
  beyond the plan document itself. The independent sub-agent review caught this against `PLAN-019`'s
  own explicit instruction (update `docs/00-working/README.md` specifically); it was fixed before
  close rather than closed over. See `## Review` and its disposition above.

## Left undone

- The two open questions in `PLAN-019` (logged rationale for reordering; whether the idea-triage
  agent may propose reorderings) are left genuinely open for whoever next touches this area — most
  likely whoever implements `phase-idea-02`, since that phase is what would first make the question
  concrete.
- No other backlog phase or idea was touched by this implementation beyond what `PLAN-019` scoped.
