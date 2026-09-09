---
schema_version: 1
id: doc-session-capture-contracts
code: SESS-2026-09-08-04
title: Define the raw capture and staging contracts
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-capture, sys-contracts]
depends_on: [doc-capture-build]
---

# Define the raw capture and staging contracts

## Phase

`phase-cap-03` — Define the raw capture and staging contracts.

## Verification

```
$ uv run pytest test/test_capture_contracts.py
26 passed, 2 warnings
```

```
$ git check-ignore -v _capture/raw/x.json
.gitignore:55:_capture/	_capture/raw/x.json
$ git check-ignore -v _capture/inbox/x.md
.gitignore:55:_capture/	_capture/inbox/x.md
$ git check-ignore -v _capture/staging/x.json
.gitignore:55:_capture/	_capture/staging/x.json
```

Also re-ran the full suite and governance after these changes, since the phase touched
`docs/08-governance/systems.yaml` (regenerating `catalog.md`) alongside its own deliverables:

```
$ uv run python -m src.governance
Governance OK: 16 systems, 87 documents, 13 memories, 97 backlog phases
$ uv run pytest
346 passed, 2 warnings
```

## Acceptance

- A raw capture record validates and carries content, an identifier and a timestamp. — Met:
  `test_raw_capture_fixture_validates` and `test_raw_capture_requires_content_id_and_timestamp`
  cover the fixture and each required field's omission.
- A staged record validates only with a resolvable raw source reference and a route. — Met:
  `test_staged_record_fixture_validates`, `test_staged_record_requires_its_core_fields` and
  `test_staged_record_rejects_empty_capture_id`/`test_staged_record_rejects_unknown_route` cover
  presence and shape of `capture_id` and `route`. True cross-file resolvability (that a given
  `capture_id` names a file that actually exists under `_capture/raw/`) is explicitly left to the
  code that reads staging and its tests — a JSON Schema cannot see the filesystem — and that code
  does not exist yet (phase-cap-04 onward).
- `git check-ignore` confirms every capture location is ignored. — Met: shown above for all three
  of `_capture/raw`, `_capture/inbox`, `_capture/staging`.

## Backlog

- `phase-cap-03` status: `active` (owner runs `/session-close` to move it to `complete`).
- `next_action`: All three acceptance conditions are met and both deliverable schemas plus their
  tests exist. Nothing further is planned for this phase; it is ready for `/session-close` review.
- `completion_evidence`: `schemas/capture.schema.json`, `schemas/staged-record.schema.json`,
  `.gitignore`, `test/test_capture_contracts.py`.
- `result`: Defined `schemas/capture.schema.json` (raw capture: id, captured_at, channel, content,
  optional source_path) and `schemas/staged-record.schema.json` (staged record: id, capture_id,
  entity_type, route, entity, optional evidence/staged_at, reusing `evidence.schema.json` for
  per-field evidence). Fixed the on-disk layout as `_capture/raw/`, `_capture/inbox/`,
  `_capture/staging/` (owner's choice, over nesting under `_private/` or `_working/`) and ignored
  the whole `_capture/` tree in `.gitignore`. Added 26 contract tests in
  `test/test_capture_contracts.py` covering both schemas, including that the staged-record
  wrapper transitively enforces REQ-002 R7 (an unflagged non-explicit protected field is rejected)
  through its `evidence` reference. Updated `sys-capture` in `systems.yaml` from `planned` to
  `scaffold` and regenerated `docs/08-governance/catalog.md`. No writer was built — this phase is
  contracts only, per its own scope and `next_action`.

## Unresolved

None. `entity_type` on the staged record is deliberately left as an open string rather than a
closed enum of the nine entity types, because ADR-007's stakes table also names a `raw note` tier
with no schema of its own yet; settling what that maps to belongs to structuring (`phase-cap-05`),
not this contract. This is noted in the schema's own description, not a gap in this phase's scope.

## Review

Independent sub-agent review, run fresh (`agent/phase-cap-03` diffed against `dev` via
`dev...HEAD`, isolating this phase's 4 commits from an unrelated commit `dev` picked up afterward),
with the reviewer running every verification command itself rather than trusting this record:

> ### Acceptance condition 1: "A raw capture record validates and carries content, an identifier and a timestamp."
> **Met.** `schemas/capture.schema.json` has `"required": ["id", "captured_at", "channel", "content"]` and `"additionalProperties": false`. `id` is constrained by pattern `^raw-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{6}$`, `captured_at` by an RFC3339 pattern, `content` by `minLength: 1`. I independently ran `uv run pytest test/test_capture_contracts.py -v`: all 26 tests pass, including `test_raw_capture_requires_content_id_and_timestamp` (parametrized over `id`, `captured_at`, `channel`, `content` — each omission independently rejected), `test_raw_capture_rejects_malformed_id`, `test_raw_capture_rejects_unknown_channel`, and `test_raw_capture_rejects_empty_content`. The tests genuinely exercise the `required` and pattern/enum constraints, not just check that a fixture with a plausible name validates.
>
> ### Acceptance condition 2: "A staged record validates only with a resolvable raw source reference and a route."
> **Met, with an honestly-scoped caveat that I judge reasonable rather than smuggled.** `schemas/staged-record.schema.json` requires `["id", "capture_id", "entity_type", "route", "entity"]` with `additionalProperties: false`. `capture_id` must be a non-empty string (`minLength: 1`); `route` is constrained to `enum: ["clean", "flagged", "held"]`. Tests confirm both a missing `capture_id`/`route` and an empty/unknown value are rejected (`test_staged_record_requires_its_core_fields`, `test_staged_record_rejects_empty_capture_id`, `test_staged_record_rejects_unknown_route`, `test_staged_record_accepts_each_legal_route`).
>
> The word "resolvable" in the acceptance wording could be read as requiring true filesystem cross-reference checking (does `capture_id` name a file that actually exists under `_capture/raw/`). The schema explicitly does **not** do this — its own description states plainly: "it does not check that `capture_id` actually resolves to a file under `_capture/raw/`... since a JSON Schema cannot see the filesystem." The session record states the same thing openly under this acceptance condition rather than glossing over it. I consider this a reasonable and honestly-declared scope boundary, not a claim smuggled past the acceptance wording — the phase's stated scope is to "define the staged record shape," not build the reader/writer that would perform such resolution (that's explicitly deferred to phase-cap-04 onward). Nothing in the diff or commit history claims filesystem resolvability was verified.
>
> ### Acceptance condition 3: "`git check-ignore` confirms every capture location is ignored."
> **Met.** `.gitignore` adds one line, `_capture/`, covering the whole tree. I ran independently:
> ```
> $ git check-ignore -v _capture/raw/x.json _capture/inbox/x.md _capture/staging/x.json
> .gitignore:55:_capture/	_capture/raw/x.json
> .gitignore:55:_capture/	_capture/inbox/x.md
> .gitignore:55:_capture/	_capture/staging/x.json
> ```
> Exit code 0, all three paths matched. `test_capture_locations_are_gitignored` in the test file also parametrizes over all three paths and asserts `git check-ignore -v` returns 0 for each; all three pass.
>
> ### Additional verification run independently
> - `uv run pytest test/test_capture_contracts.py -v` → 26 passed.
> - `uv run python -m src.governance` → `Governance OK: 16 systems, 87 documents, 13 memories, 97 backlog phases` (clean).
> - `uv run pytest` (full suite) → **346 passed**, 2 warnings (deprecation warnings unrelated to this phase). Tree is genuinely green.
>
> Minor, inconsequential note: the session record's own logged governance output shows "86 documents" while my run today shows "87 documents." This is not a discrepancy — the session record file itself is the 87th document, added to `catalog.md`'s table after the record's own verification snippet was captured. Sequencing artifact, not a false claim.
>
> ### Scope/quality concerns
> None found. All 8 changed files (`.gitignore`, the two new schemas, the new test file, `docs/09-backlog/backlog.yaml`, `docs/08-governance/systems.yaml`, `docs/08-governance/catalog.md`, and the new session record) are within or directly required by the phase's declared scope and deliverables list. `systems.yaml`'s `sys-capture` status change (`planned` → `scaffold`) and its updated description accurately reflect that contracts now exist but no writer does — matches the diff. `evidence.schema.json`, referenced via `$ref` from `staged-record.schema.json`, predates this phase (added in commit “Add the five new record types and the shared evidence shape”, not touched by this diff) — reusing it is not scope creep. `backlog.yaml`'s `phase-cap-03` entry correctly remains `status: active` (not `complete`) — consistent with the repo's rule that only `/session-close` moves a phase to complete.
>
> ### Overall
> The session record's account matches what I independently found. All three acceptance conditions genuinely hold based on my own reading of the schemas/tests and my own command runs, not merely the session record's claims. No discrepancies found between the claimed and actual state.

(Note added after the review, not part of it: the "86 vs 87 documents" point above was already
resolved before this review ran — the `## Verification` section above was updated to `87 documents`
at close time, for the reason the reviewer independently arrived at.)

## Decisions

- **`_capture/` as a new top-level directory**, over nesting under `_private/` or `_working/`. Put
  to the owner explicitly via `AskUserQuestion` before any file was written, because it is the one
  structural choice every later capture phase (`cap-04` onward) builds paths against. The owner chose
  the new-directory option, matching the existing pattern of `_data/`, `_private/`, `_working/` as
  purpose-named top-level directories, rather than overloading `_private/`'s documented meaning
  (credentials, personal notes) with a differently-shaped intake queue.
- **Raw capture ids are time-prefixed with a random suffix** (`raw-<UTC timestamp>-<hex6>`) rather
  than a single incrementing counter like `_data/ideas.jsonl` uses. This was my own design call, not
  put to the owner: ideas.jsonl's sequential counter works because it has one sanctioned writer
  (`tools/append_idea.py`); raw capture has three channels (session, inbox, CLI) that ADR-007
  requires to converge on the same shape without a shared writer, so a counter would need
  coordination this phase doesn't build. The random suffix disambiguates same-second collisions
  without one.
- **`entity_type` on the staged record stays an open string**, not a closed enum of the nine known
  entity types. ADR-007's stakes table names a `raw note` tier that has no schema anywhere in the
  repository yet, and REQ-002's "nine types" accounting doesn't obviously include it. Closing the
  enum now would mean guessing what `raw note` maps to — a call that belongs to structuring
  (`phase-cap-05`), not to this contracts phase. Recorded in the schema's own description so the
  decision doesn't get lost between phases.
- **Before claiming the phase**, walked the owner through the top-5 ready phases from
  `governance --ready` and asked (via `AskUserQuestion`) whether to claim-and-start,
  claim-only-and-pause, or hold off. The owner chose claim-and-start, which is what set `agent:
  agent-cap03` and opened the worktree.

## Corrections

- Early in the session, `/backlog` orientation skipped straight to deep-diving `phase-cap-03` (plan,
  ADR-007, REQ-002) without first showing the top-of-queue table the skill's step 2 requires. The
  owner caught this ("Shouldn't we share the priority queue items first"). Backed up, ran
  `governance --ready` properly, and presented the top-5 ready phases with titles, priorities,
  `next_up` status and plan links before returning to `phase-cap-03`.
- A stray edit added a blank line after `backlog.yaml`'s top-level `updated:` field while trying to
  "bump" it per `AGENTS.md`'s claim instructions — the date was already today's, so there was nothing
  to bump. Caught before committing and reverted in the same turn.
- `failing_paths()` in the new test file initially couldn't name a field for a plain `required`
  violation (jsonschema raises those against the object, with no path to the missing key), so nine
  parametrized tests failed even though the schemas were correct. Fixed by extending the helper to
  diff the failing subschema's `required` list against the instance's actual keys — the same fix
  pattern `test_schemas.py` doesn't need because it never asserts a specific missing-field name for a
  top-level `required` error.
- `docs/08-governance/catalog.md` went stale after editing `systems.yaml` and again after the
  `backlog.yaml` checkpoint edit — `governance --catalog` only prints to stdout, it doesn't write the
  file, so the first run appeared to do nothing. Caught both times by `test_codes.py`'s
  committed-catalog-matches-regenerated-output test failing; fixed by redirecting the command's
  output into the file and re-running governance to confirm.

## Left undone

- **No writer exists.** `tools/capture.py` (or equivalent) — the actual CLI command and inbox
  handling that would write a real file into `_capture/raw/` — is deliberately out of scope here;
  it's `phase-cap-04`'s job, and it can now be built against these two schemas.
- **`entity_type`'s closed vocabulary and the `raw note` tier's mapping** are open, as recorded under
  Decisions above. Whoever picks up `phase-cap-05` (structuring and routing) needs to settle this
  before the routing table (REQ-002 R8) can be fully implemented.
- **True `capture_id` → raw-file resolvability** is asserted only at the "non-empty string" level by
  this schema; nothing here checks a staged record's `capture_id` against an actual file on disk.
  Both this phase's own description and the independent review agree this is correctly out of scope
  for a schema-only phase, but it needs a home — most naturally in whatever code first reads
  `_capture/staging/` (`phase-cap-04` or `phase-cap-06`).
