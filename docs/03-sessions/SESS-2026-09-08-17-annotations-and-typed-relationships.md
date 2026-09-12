---
schema_version: 1
id: doc-session-annotations-and-typed-relationships
code: SESS-2026-09-08-17
title: Annotations and typed relationships
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-portfolio, sys-projection, sys-memory-agents]
depends_on: [doc-idea-plan-annotations-links]
---

# Annotations and typed relationships

## Phase

`phase-idea-08` — Add annotations and typed relationships.

## Verification

`uv run pytest test/test_ideas.py`:

```
62 passed, 2 warnings
```

`uv run python -m src.governance`:

```
Governance OK: 16 systems, 105 documents, 13 memories, 101 backlog phases
```

(104 at the mid-session checkpoint, before this session record itself — a governed document —
was committed; 105 now that it is on `dev`. No other figure moved.)

`uv run pytest`:

```
395 passed, 2 warnings
```

Also run, not in the phase's `verification` list but confirming the deliverables directly:
`uv run python tools/rebuild_db.py` — `idea_annotations: 0 rows`, `idea_links: 0 rows`, no error
(the committed log has no annotations or links yet, so both are empty and every other table's row
count is unchanged); `uv run python tools/generate_ideas_md.py --check` — `docs/00-working/ideas.md
is current`, exit 0; `uv run ruff check src/ test/` — one error, pre-existing on `dev` and unrelated
to this phase (`src/governance/__main__.py` import ordering, confirmed via `uv run ruff check
src/governance/__main__.py` reproducing the identical error against the primary checkout); `uv run
mypy src/` — no issues in 15 source files. `_data/ideas.jsonl` untouched (no writes were made to
the real log — every new test builds its own temporary log via the `log` fixture). Integrated onto
`dev` at commit “phase-idea-08: annotations and typed relationships” (fast-forward from the commit “Claim phase-idea-08 for agent-claude”), rebuilt and re-verified there directly —
all of the above is the post-integration rerun, not a repeat of the worktree's own numbers.

## Acceptance

- Annotations accumulate and never replace each other; an amendment corrects one annotation's
  text and not the collection. **Met** —
  `test_annotations_accumulate_and_an_amendment_corrects_only_one` asserts two annotations both
  survive a correction to the first, and that the correction appends rather than rewriting.
- A link never mutates its target; supersedes does not discard, and a legal revisit is not
  refused because of a graph edge. **Met** —
  `test_a_link_never_mutates_its_target_only_retraction_is_legal` proves a hand-built repoint
  amendment (`target: {"set": true, "value": "000003"}`) is refused by the schema
  (`link_retraction`'s `value` is `{"const": null}`), and that retraction is the only legal
  correction. `test_a_supersedes_edge_is_flagged_while_its_target_stays_working` proves a
  `supersedes` edge whose target has not been discarded produces a diagnostic rather than a
  refusal, and that discarding the target — a legal status event, unrelated to the graph — clears
  the diagnostic without touching the historical link. No mechanism added by this phase can refuse
  a status transition (annotations and links are validated independently of `fold`'s transition
  table), so a legal revisit is structurally never blocked by a graph edge.
- A cycle in `extends` is flagged at fold time and the capture still succeeds. **Met** —
  `test_an_extends_cycle_is_flagged_but_capture_still_succeeds` builds a two-idea cycle through
  the real `link()` writer, asserts `link_diagnostics` reports it, and asserts the second edge was
  still appended and folds successfully.
- Rendering is deterministic across processes and hash seeds, and `--check` detects stale output.
  **Met** — `test_rendered_findings_collapse_and_notes_stay_visible` asserts `render()` called
  twice against the same state produces identical output after adding the collapse logic, and the
  pre-existing `test_regenerating_twice_produces_identical_output` and
  `test_a_hand_edit_to_the_markdown_is_detected` continue to pass unmodified against the extended
  renderer — the `--check` mechanism itself was not changed, only the state it renders. Hash-seed
  independence is not separately exercised here or by the pre-existing determinism tests (`render`
  does not iterate any `dict`/`set` whose order depends on `PYTHONHASHSEED`; ideas are sorted by
  id and annotations/links are plain lists in append order), matching the verification bar the
  prior phase's rendering tests already set.

## Backlog

`phase-idea-08` status: `complete`, agent `agent-claude`, session
`doc-session-annotations-and-typed-relationships`. Integrated onto `dev` at the commit “phase-idea-08: annotations and typed relationships”; worktree
`agent/phase-idea-08` and its branch removed after the fast-forward merge.

## Unresolved

None.

## Review

Independent review by a fresh, non-fork sub-agent, given the phase's `scope`/`acceptance`/
`verification` from `backlog.yaml`, the commit range from “Claim phase-idea-08 for agent-claude” to HEAD (single commit “phase-idea-08: annotations and typed relationships”),
and this session record's content — instructed to reach its own verdicts from the diff and its own
reruns, not to check whether the record's claims read plausibly. Pasted verbatim:

> ## Verification output (run myself in `/code/d-system`, HEAD = “phase-idea-08: annotations and typed relationships”)
>
> - `uv run pytest test/test_ideas.py` → **62 passed, 2 warnings** — matches the session record
>   exactly.
> - `uv run python -m src.governance` → `Governance OK: 16 systems, 105 documents, 13 memories,
>   101 backlog phases` — one discrepancy from the record (`104 documents`, mine says `105`). Not
>   tied to phase-idea-08's mechanics (nothing in this diff's schema/fold/CLI logic touches
>   document counting), and every other figure (systems/memories/backlog phases) matches. Not
>   worth blocking on, but noting it as a discrepancy since the task asked me to flag any.
> - `uv run pytest` → **395 passed, 2 warnings** — matches the session record exactly.
> - `uv run python tools/rebuild_db.py` → `idea_annotations: 0 rows`, `idea_links: 0 rows`, all
>   other counts unchanged — matches the record.
> - `uv run python tools/generate_ideas_md.py --check` → `docs/00-working/ideas.md is current`,
>   exit 0 — matches the record.
>
> ## Condition-by-condition verdicts
>
> **1. Annotations accumulate and never replace each other — Met.** `fold()`'s `annotated` branch
> (`src/db/ideas.py`) appends to `current["annotations"]`, never replaces. `AMENDABLE_FIELDS`
> includes `text`, and `_effective_fields`/`_effective_event` resolve only the targeted
> annotation's identity — sibling annotations are untouched because each is folded independently
> by its own `eid`. `test_annotations_accumulate_and_an_amendment_corrects_only_one` (line 436)
> confirms both the resolved state and the raw log: 4 lines total (2 annotations + 1 correction...
> plus the `created`), correction never rewrites.
>
> **2. A link never mutates its target; supersedes doesn't discard; a legal revisit isn't blocked
> by a graph edge — Met.** Verified independently:
> - Schema-level: I ran the raw JSON Schema (`jsonschema.Draft7Validator`) against a hand-built
>   repoint amendment (`target: {"set": true, "value": "000003"}`) — it fails validation. A
>   retraction (`target: {"set": true, "value": null}`) validates cleanly. `link_retraction`'s
>   `additionalProperties: false` plus `value: {"const": null}` genuinely forbids repointing; only
>   `null` is legal.
> - Code-level: `retract_link` in `tools/append_idea.py` only ever builds `{"set": True, "value":
>   None}` — there is no code path in this diff that constructs a non-null `target` amendment.
> - `revisited` handling in `fold()` (lines ~286-294) checks only `current["status"] ==
>   "discarded"` and the revisit counter — no link/graph state is consulted anywhere in that
>   branch, and `link_diagnostics()` is a pure read-only reporting function called separately
>   (never invoked from inside `fold`'s transition logic, never raises). So a `revisited` event
>   structurally cannot be blocked by a graph edge — confirmed by reading, not just by test name.
> - `test_a_supersedes_edge_is_flagged_while_its_target_stays_working` demonstrates the diagnostic
>   clears once the target idea is legitimately discarded via an ordinary `status` event, with no
>   interaction between the two mechanisms.
>
> **3. An `extends` cycle is flagged at fold time and capture still succeeds — Met.**
> `link_diagnostics()` runs a standard white/gray/black cycle detection over the `extends`
> subgraph and never raises; `tools/append_idea.py`'s `link()` calls it *after* already having
> called `fold(events + [event])` successfully (i.e., the append happens regardless), then
> surfaces diagnostics as a return value / stderr warning.
> `test_an_extends_cycle_is_flagged_but_capture_still_succeeds` builds a real two-idea cycle
> through the writer and asserts both the diagnostic and the persisted state.
>
> **4. Rendering is deterministic across processes/hash seeds, `--check` detects staleness — Met,
> and I independently verified the hash-seed claim rather than trusting the session record's
> reasoning.** I wrote a throwaway script building a temp idea log with 20 findings + a link, and
> ran `generate_ideas_md.render()` under `PYTHONHASHSEED=1` and `PYTHONHASHSEED=9999` —
> byte-for-byte identical output. This confirms the record's reasoning (`render` iterates
> `sorted(state)` for ideas, plain ordered lists for annotations/links, and `dict` iteration order
> in CPython 3.7+ is insertion order, not hash-seed dependent) is actually correct in practice, not
> just asserted. Findings-collapse: `_render_annotations` puts every `kind != "finding"`
> annotation inline and wraps all findings in one `<details>` block with a count in the summary —
> confirmed with 100 findings in `test_rendered_findings_collapse_and_notes_stay_visible`, each
> finding text appears exactly once. `--check` itself was unmodified by this diff (still a
> byte-diff against committed output); I ran it live and it correctly reports "current."
>
> ## Additional scrutiny requested
>
> - **`link_retraction` enforcement**: confirmed both by direct schema validation and by code-path
>   reading — no way to repoint, only to null out.
> - **Terminal-idea annotations/links don't touch status**: `fold()`'s `annotated`/`linked`
>   branches only append to `annotations`/`links` and bump `updated`; they never read or write
>   `current["status"]`, and are dispatched unconditionally regardless of what status the idea is
>   in.
> - **Revisit not blocked by graph edges**: confirmed above — structurally true, not merely
>   test-covered.
> - **`promoted_to` legacy scalar handling**: `_as_promoted_to()` is a pure fold-time
>   normalization (str → `[str]`), invoked only when constructing derived state; it never touches
>   or rewrites the underlying JSONL event. Confirmed via
>   `test_promoted_to_accepts_an_array_and_a_legacy_scalar_reads_as_a_singleton`, which literally
>   injects a scalar-shaped event into the in-memory list (not the file) and folds it.
> - **Findings-collapse rendering control + determinism**: confirmed both by test and by my own
>   hash-seed experiment above.
>
> One soft (non-blocking) observation not raised in the session record: the schema does not tie an
> amendment's carried field (`text` vs `target`) to the *kind* of event it targets — e.g., nothing
> at the schema layer stops a hand-crafted amendment from carrying `text` while `amends` points at
> a `linked` event's identity, or `target` while pointing at an `annotated` event's identity. In
> practice this is harmless: `fold()`'s `annotated`/`linked` dispatch branches only ever read the
> fields relevant to their own kind, so a mismatched field is silently inert, and the CLI helpers
> (`amend_annotation`, `retract_link`) already guard against constructing such a mismatch. It's a
> gap only reachable by bypassing the CLI and calling `append()` with a hand-built dict (as the
> tests themselves do for other purposes) — not a violation of any of the four acceptance
> conditions, just worth knowing about if `phase-idea-08`'s writer surface is later hardened.
>
> ## Discrepancies
>
> One found: governance's document count (104 vs 105 documents) differs from the session record's
> captured output, though every other metric matches and it isn't connected to anything in this
> phase's actual diff. Everything else — test counts, rebuild row counts, `--check` behavior, and
> all four acceptance-condition claims — checks out under independent reading and independent
> re-execution. No discrepancies found in the substantive claims about annotations, links, cycle
> detection, `promoted_to`, or rendering determinism.

The one flagged discrepancy (104 vs 105 documents) is explained above under `## Verification`: the
reviewer ran governance after this session record itself — a governed document — was committed to
`dev`, one commit later than the number the record had captured mid-session. Not a substantive
finding.

## Decisions

- Kept `phase-idea-08`'s `next_action` ("update `phase-idea-02`'s scope") from being executed
  literally. `phase-idea-02`'s `acceptance` already read "using the finding-kind annotated event
  phase-idea-08 adds" before this session started — the cross-reference the `next_action` asked
  for already existed — so editing it again would have been a no-op edit for its own sake. Raised
  to the owner via `AskUserQuestion` during orientation and confirmed before starting the schema
  work.
- Restricted a non-owner `annotate` author to `kind: finding`, deferred a structured `assessment`
  score field, and scoped fold-time link diagnostics per-idea rather than per-graph — the three
  open questions `PLAN-017.04` left unresolved. All three followed the plan's own stated
  recommendation; confirmed with the owner via `AskUserQuestion` before implementation rather than
  choosing silently.
- Kept `promoted_to` validation to "non-empty array of strings, legacy scalar reads as a
  singleton" — the phase's literal scope bullet — rather than building the fuller governance-
  document resolver (checking kind/status/deprecation) that `PLAN-017.01` separately describes.
  That resolver is real future work but is not named by any of this phase's four acceptance
  conditions or scope bullets, and no other backlog phase currently claims it; building it here
  would have been scope creep into work nothing has budgeted.
- Designed link retraction as a narrow `link_retraction` shape (`{"set": true, "value": null}`
  only) rather than reusing the general `field_shape` with a widened `value` type, specifically so
  the schema itself — not just writer discipline — makes repointing a link structurally
  inexpressible. `field_shape`'s own docstring anticipated this ("a future optional, clearable
  field takes a wider `value` type in its own right"); this is that field.
- Extended `AMENDABLE_FIELDS`/`_effective_fields` generically to cover `text` and `target` rather
  than writing separate resolution logic for annotations and links — the existing
  replace/inherit-chain machinery `phase-idea-07` built for `title`/`body` applies unchanged, and
  reusing it was more reliable than a parallel implementation of the same merge-over-a-chain
  semantics.

## Corrections

- An early draft of `test_annotations_accumulate_and_an_amendment_corrects_only_one` and
  `test_a_link_is_asserted_and_the_inverse_is_derived_not_stored` contained leftover editing
  artifacts (a stray no-op attribute assignment, a redundant `... or True` assertion clause) from
  iterating on the test bodies. Caught before running the suite for the first time and cleaned up
  in the same session; never landed in a passing run.
- The `test_a_link_never_mutates_its_target_only_retraction_is_legal` test initially asserted the
  wrong post-retraction line count (miscounted the fixture's own `add`/`link`/`retract_link`
  calls). Caught on first test run (`4 == 3` failure) and fixed immediately.
- `docs/08-governance/catalog.md` and `docs/08-governance/OPS-005-append-idea.md` both went stale
  more than once during the session as schema/docstring edits landed — each time caught by
  `uv run pytest` before commit and regenerated with `tools/generate_tool_docs.py` /
  `src.governance --catalog` rather than hand-edited.

## Left undone

- The fuller `promoted_to` governance-document resolver described in `PLAN-017.01` (validating
  target kind/status, refusing deprecated or missing codes, deriving a reverse document-to-idea
  index) — deliberately out of this phase's scope; see `## Decisions`. No backlog phase currently
  claims it.
- The reviewer's soft observation that the schema does not tie an amendment's carried field
  (`text` vs `target`) to the *kind* of event its `amends` pointer targets — reachable only by
  bypassing the CLI writer with a hand-built event, currently harmless because `fold()`'s
  `annotated`/`linked` branches only read fields relevant to their own kind. Not a violation of
  any acceptance condition; worth a look if the writer surface is later hardened against malformed
  hand-crafted events, but not filed as a new backlog item by this session.
- `phase-idea-02` (the triage agent) remains unstarted — this phase only gives it somewhere to
  write findings; building the agent itself was never in scope here.
