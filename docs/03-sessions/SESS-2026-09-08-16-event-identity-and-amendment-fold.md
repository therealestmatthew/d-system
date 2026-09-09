---
schema_version: 1
id: doc-session-event-identity-and-amendment-fold
code: SESS-2026-09-08-16
title: Event identity and the amendment fold
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-portfolio, sys-projection]
depends_on: [doc-idea-plan-event-contract]
---

# Event identity and the amendment fold

## Phase

`phase-idea-07` — Add event identity and the amendment fold.

## Verification

`uv run pytest test/test_ideas.py`:

```
49 passed, 2 warnings
```

`uv run python -m src.governance`:

```
Governance OK: 16 systems, 104 documents, 13 memories, 101 backlog phases
```

`uv run pytest`:

```
382 passed, 2 warnings
```

Also run, not in the phase's `verification` list but confirming the deliverable directly:
`uv run python tools/rebuild_db.py` — `idea_events: 46 rows`, no error; `uv run ruff check
src/ test/ tools/` — one error, pre-existing on `dev` and unrelated to this phase (`src/governance/__main__.py`
import ordering, confirmed via `git diff dev -- src/governance/__main__.py` showing no change);
`uv run mypy src/` — no issues in 15 source files. `_data/ideas.jsonl` confirmed byte-identical
(untouched by `git diff dev..agent/phase-idea-07 -- _data/ideas.jsonl`, empty).

## Acceptance

- Two amendments correcting different fields of one event both survive; neither reverts the
  other. **Met** — `test_sibling_amendments_to_title_and_body_both_survive` and
  `test_a_second_amendment_to_the_same_field_wins_without_reverting_the_first`.
- Required fields cannot be cleared; optional contributions can, and clearing one leaves its
  siblings intact. **Partially met.** The cannot-clear half is met structurally:
  `field_shape.value` in `schemas/idea.schema.json` has no way to be `null`, so a clearing
  amendment is refused by the same schema check every event passes
  (`test_a_cleared_required_field_is_refused_by_the_schema`). The can-clear half is not
  exercised: title and body are the only amendable fields this phase adds, and both are
  required on every idea, so there is no real optional, clearable field yet to demonstrate
  against. PLAN-017.03's own conflict note (`C03`) assigns that demonstration to
  PLAN-017.04/`phase-idea-08`, which adds the note/link fields that are actually clearable.
- A fixture interleaving two worktrees' appended lines leaves every amends pointer
  resolvable. **Met** — `test_a_branch_merge_interleaving_leaves_every_amends_pointer_resolvable`.
- Two events resolving to one identity fail the fold rather than being silently accepted.
  **Met** — `test_fold_refuses_two_events_resolving_to_one_identity`.

## Backlog

`phase-idea-07` status: `active`, agent `agent-fold`, `session:
doc-session-event-identity-and-amendment-fold`. `next_action` states that scope and
acceptance are complete on `agent/phase-idea-07`, that PLAN-017.03 has been amended to
record the two confirmed decisions, and that the phase is ready for session-close and
integration.

## Unresolved

- `phase-idea-02`'s `next_action` in `backlog.yaml` names `phase-idea-08` as the phase that
  gives it somewhere to write findings; this session did not touch `phase-idea-08`.
- The independent review below (see `## Review`) found one latent gap not covered by any
  acceptance condition — a `rebuild_db.py` `KeyError` on an explicit-inherit amendment shape
  the schema permits but no writer emits. Fixed in this session (commit “Fix rebuild_db KeyError on an explicit-inherit amendment field”) with a
  regression test; not left open.

## Review

Independent review by a fresh, non-fork sub-agent, given the phase's `scope`/`acceptance`/
`verification` from `backlog.yaml`, the commit range `dev..agent/phase-idea-07`, and this
session record's content — instructed to reach its own verdicts from the diff and its own
reruns, not to check whether the record's claims read plausibly. Pasted verbatim:

> **Verdict**
>
> **Verification commands (run myself in `/code/d-system-worktrees/phase-idea-07`, branch
> `agent/phase-idea-07`):**
> - `uv run pytest test/test_ideas.py` → `48 passed, 2 warnings`
> - `uv run python -m src.governance` → `Governance OK: 16 systems, 104 documents, 13
>   memories, 101 backlog phases` (session record says 103 documents — off by one, harmless
>   drift, likely from a doc added after the record was written)
> - `uv run pytest` (full suite) → `381 passed, 2 warnings`
> - `uv run python tools/rebuild_db.py` → `idea_events: 46 rows`, no error, matching the
>   session record
>
> **`_data/ideas.jsonl`**: `git diff dev..agent/phase-idea-07 -- _data/ideas.jsonl` is empty
> — confirmed byte-identical, untouched.
>
> ### Acceptance conditions — independent verdicts
>
> **1. Two amendments to different fields both survive — Met.** Traced
> `_effective_fields`/`_effective_event` in `src/db/ideas.py` by hand: each amender's own
> contribution (only the field key(s) it carries) is merged into the running result only
> when `set: true`; an amendment that only carries `title` never touches `body`. Confirmed
> with the existing tests (`test_sibling_amendments_to_title_and_body_both_survive`) and
> reasoned through a manual trace — correct.
>
> **2. Required fields cannot be cleared; optional contributions can — Partially met**, same
> conclusion as the session record, independently verified rather than trusted:
> - Required-can't-clear half is real: `field_shape.value` in `schemas/idea.schema.json` is
>   `{"type": "string", "minLength": 1}` — no null/empty variant — so
>   `title: {"set": true, "value": null}` fails schema validation. I didn't just read the
>   docstring; I checked the schema definition and the test
>   (`test_a_cleared_required_field_is_refused_by_the_schema`) that exercises exactly this
>   via `append()` → `validate()`, which raises `IdeaError` with "refusing to append."
> - Optional-can-clear half genuinely isn't exercised: title/body are the only two amendable
>   fields this phase adds, and both are `required` on `created`, so there's no field in this
>   phase to demonstrate clearing on. This is a real gap, correctly attributed to
>   `phase-idea-08`, not a cover for missing work — the schema doesn't even have a
>   representable "clear" state yet (only replace/inherit `set: true/false`, no null/empty
>   semantics).
>
> **3. Merge-interleaving fixture leaves every amends pointer resolvable — Met.**
> `test_a_branch_merge_interleaving_leaves_every_amends_pointer_resolvable` builds a
> genuinely interleaved two-idea log and asserts both ideas fold correctly by identity
> regardless of adjacency to `seq`. Read it in full — it's a real fixture, not a trivial
> rename of an existing test.
>
> **4. Two events resolving to one identity fail the fold — Met.** `_identity_index` in
> `src/db/ideas.py` raises `IdeaError` on any identity collision. I independently reproduced
> this outside the test suite with a hand-built two-event list sharing an explicit `eid`, and
> it refused as expected.
>
> ### Additional scrutiny findings
>
> - **Nested amendment-of-amendment logic** (`_effective_fields`, recursive on
>   `by_target`): traced by hand for a 3-deep chain (base → A1 → A2 correcting A1). The
>   recursion resolves the amender's own effective fields first, then applies them only if
>   `set: true`; since `_amendments_by_target` already proves every target strictly precedes
>   its amendment in log position, there's no cycle risk. Logic is correct, not just
>   test-passing.
> - **One real latent gap not covered by the acceptance criteria or the session record**:
>   `tools/rebuild_db.py`'s unwrap logic (`title["value"] if isinstance(title, dict) else
>   title`) will raise `KeyError` if an `amended` event explicitly encodes `{"set": false}`
>   for a field with no `value` key — which the schema permits (a legal but pointless
>   "explicit inherit"). I confirmed the `KeyError` reproduces directly. The CLI
>   (`append_idea.py`) never emits this shape, and no test exercises it, so it's unreachable
>   through normal use today — but it's a schema/code inconsistency worth flagging since a
>   hand-crafted or future-writer-produced event could crash the rebuild.
>
> ### Discrepancies vs. the session record
>
> None material. The one-document-count difference (103 vs. 104) in the governance output is
> trivial drift, not a substantive claim mismatch. All four acceptance verdicts I reached
> independently match the session record's own verdicts, including its "partially met" call
> on condition 2 — I verified that call by reading the schema and test directly rather than
> trusting the docstring.

The reviewer's one substantive finding — the `rebuild_db.py` `KeyError` — was fixed in this
session immediately after the review returned, in commit “Fix rebuild_db KeyError on an explicit-inherit amendment field”, with a regression test
(`test_the_rebuild_survives_an_amendment_that_explicitly_inherits`) that fails against the
pre-fix code and passes against the fix. The reviewer's pass counts (48/381) and document
count (104, matching its own rerun rather than the record's then-stale 103) predate that
commit; the post-fix counts (49/382, 104 documents) are recorded in `## Verification` above.

## Decisions

- Scoped amendable fields to `title` and `body` only, matching the plan's concrete example
  and all four of the phase's acceptance bullets, rather than also supporting amendment of
  `status` events' `from`/`to`/`promoted_to`. The plan's broader "How it is verified" section
  mentions correcting a transition, but none of the four backlog acceptance conditions
  require it, and the backlog phase — not the parent plan's aspirational verification list —
  is the declared work boundary.
- The CLI's `amend <idea> [--title] [--body]` always targets the idea's `created` event by
  identity, regardless of how many times it has already been amended, rather than requiring
  the caller to know which prior amendment (if any) to target. This is semantically
  equivalent to targeting the latest amendment — traced by hand and confirmed by the nested-
  chain test — because the fold resolves a target's effective fields recursively before
  applying them, so accumulating amendments on one target and chaining amendments-of-
  amendments produce the same result for a single-field correction.
- Adopted the owner's two PLAN-017.03 decisions from the prior turn (append order for nested
  precedence; amendment reason optional) and amended PLAN-017.03 itself to record them,
  rather than leaving the plan document listing them as open questions the implementation had
  already answered.
- **Closed this phase despite acceptance condition 2 reading only "Partially met."** Both the
  checkpoint's own recomputed verdict and the independent review agreed on 3-Met/
  1-Partially-met, and session-close's own rule is not to mark a phase complete unless every
  condition is Met — so the phase was reported to the owner as open, with the exact reason
  and a named decision point, rather than closed unilaterally. The owner asked what
  "optional fields can be cleared" meant, confirmed the required/optional distinction was
  about title/body (correctly required, not a design defect) versus a future clearable field
  phase-idea-08 has not built yet, and then explicitly chose to close this phase now,
  accepting condition 2 as satisfied given phase-idea-07's declared scope rather than holding
  it open for a field that does not exist yet to exercise (2026-09-08). `status: complete`
  was set only after that explicit direction, not by this session's own judgement.

## Corrections

- The rebuild `KeyError` on an explicit-inherit amendment field (see `## Review` and
  `## Unresolved`) was found by the independent review, not during implementation or the
  original self-review. Fixed same-session, commit “Fix rebuild_db KeyError on an explicit-inherit amendment field”.
- The first version of this session record left its `## Backlog` and `## Unresolved`
  sections describing PLAN-017.03 as still needing amendment, even though the same commit
  that wrote the record also amended PLAN-017.03. Corrected during session-close's fresh
  checkpoint pass (this revision) rather than left to drift further.

## Left undone

- Amendment of `status` events (`from`/`to`/`promoted_to`) — deliberately out of scope; see
  `## Decisions`. Not needed by any declared acceptance condition, so not attempted.
- A real optional, clearable field to demonstrate the "optional contributions can be cleared"
  half of acceptance condition 2. That field does not exist until PLAN-017.04/`phase-idea-08`
  adds one (notes/links); this phase could not create a field outside its own scope just to
  test the mechanism. The owner explicitly accepted this as a closed scope boundary rather
  than unfinished work — see `## Decisions` — so `phase-idea-08` inherits the demonstration,
  not a reopened condition 2.
- `phase-idea-08` itself — the annotation/finding event `phase-idea-02`'s triage agent needs
  — is unstarted. This session only unblocks it (`phase-idea-08` depends on `phase-idea-07`).
