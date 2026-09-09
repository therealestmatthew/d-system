---
schema_version: 1
id: doc-session-scrub-tracked-structure
code: SESS-2026-09-08-12
title: Scrub client and personal identifiers from tracked structure
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-brain, sys-retrieval]
depends_on: [doc-confidentiality-sweep]
---

# Scrub client and personal identifiers from tracked structure

## Phase

`phase-priv-02` — Scrub client and personal identifiers from tracked structure.

## Verification

`git grep -Ii -e client-a -- .`:

```
_data/projects/client-a-ai-adoption.json:  "id": "client-a-ai-adoption",
_data/projects/client-a-ai-adoption.json:  "name": "Client A AI Adoption",
_data/projects/client-a-ai-adoption.json:  "tags": ["client-a", "claude", "ai-tools", "education", "consulting"],
_data/projects/client-a-mvp4-sc.json:  "id": "client-a-mvp4-sc",
_data/projects/client-a-mvp4-sc.json:  "name": "Client A MVP4 SC",
_data/projects/client-a-mvp4-sc.json:  "description": "Client A MVP4 Supply Chain engagement — now inactive.",
_data/projects/client-a-mvp4-sc.json:  "tags": ["client-a", "anaplan", "consulting"],
_data/projects/client-a-ortho-bridge.json:  "id": "client-a-ortho-bridge",
_data/projects/client-a-ortho-bridge.json:  "name": "Client A Ortho Bridge",
_data/projects/client-a-ortho-bridge.json:  "tags": ["client-a", "anaplan", "consulting"],
docs/09-backlog/backlog.yaml:  - git grep -Ii -e client-a -- .
```

Non-zero matches. The three remaining hits are `_data/projects/client-a-ai-adoption.json`,
`_data/projects/client-a-mvp4-sc.json` and `_data/projects/client-a-ortho-bridge.json` — the real client
project files, whose relocation out of the tracked tree is `phase-priv-03`'s declared deliverable,
not this phase's. The fourth hit is this phase's own verification command echoed literally inside
`docs/09-backlog/backlog.yaml`; it is the shell string `-e client-a`, not an identifier leak. Everything
this phase's own scope names — `README.md`, `_data/tags.json`, `docs/07-architecture/ARCH-001-tagging-system.md`,
`brain/concepts/tag-taxonomy.md`, `brain/index.md`, `tools/load_context.py` — carries no match, along
with `docs/08-governance/OPS-003-load-context.md` and `docs/02-prompts/PROMPT-002-capture-and-structuring-system.md`,
which were not in the declared deliverables list but contained the same real identifier in prose and
were scrubbed as squarely inside the scope's intent.

`uv run python -m src.governance`:

```
Governance OK: 16 systems, 100 documents, 13 memories, 101 backlog phases
```

## Acceptance

- No tracked file matches the client identifier in any casing — **Not met**. `_data/projects/client-a-ai-adoption.json`,
  `_data/projects/client-a-mvp4-sc.json` and `_data/projects/client-a-ortho-bridge.json` still match; relocating
  them is `phase-priv-03`'s deliverable.
- No tracked file outside `_private/` names a real project ID — **Not met**, same three files, same
  reason.
- The tag taxonomy still exercises all six categories — **Met**. `_data/tags.json`'s `client` category
  tag is now `client-a` (renamed from the real client identifier); `platform`, `tech`, `domain`, `methodology` and `context`
  are untouched by this phase's edits.

## Backlog

`status: active` (unchanged — two of three acceptance conditions are not met). `next_action`: owner
decision needed on whether `phase-priv-02` counts as complete now that its own scoped deliverables are
done, given the remaining gap is explicitly `phase-priv-03`'s deliverable, or should stay open until
that grep genuinely returns nothing. `session: doc-session-scrub-tracked-structure`.
`completion_evidence`: `README.md`, `_data/tags.json`, `docs/07-architecture/ARCH-001-tagging-system.md`,
`docs/02-prompts/PROMPT-002-capture-and-structuring-system.md`, `tools/load_context.py`,
`docs/08-governance/OPS-003-load-context.md`, `brain/index.md`, `docs/08-governance/catalog.md`,
this session record.

## Unresolved

Whether `phase-priv-02` should close now (its own deliverables are done; the remaining grep matches
are `_private/`-bound content that `phase-priv-03` explicitly owns) or stay open until that grep
returns zero matches. This is the question this `/session-close` run exists to settle.

## Review

Independent sub-agent review, run against commit range from “Claim phase-priv-02 for agent-clay” to HEAD (dev), reproduced verbatim:

> **Verification commands, run myself**
>
> **`git grep -Ii -e client-a -- .`** (exit 0, non-zero matches) — output is exactly:
> - 3 real matches in `_data/projects/client-a-ai-adoption.json`, `_data/projects/client-a-mvp4-sc.json`,
>   `_data/projects/client-a-ortho-bridge.json` (ids, names, descriptions, tags)
> - Self-referential lines inside `docs/03-sessions/SESS-2026-09-08-12-scrub-tracked-structure.md` and
>   `docs/09-backlog/backlog.yaml` — these are the session record quoting the grep command/output and
>   backlog prose discussing the leftover matches, not identifier leaks themselves.
>
> This matches the session record's claimed output verbatim. The characterization of the three real
> hits as `phase-priv-03`'s deliverable (relocating `_data/projects/client-a-*.json` out of the tracked
> tree) is accurate — those files are indeed absent from `phase-priv-02`'s deliverables list in
> `backlog.yaml`, and `phase-priv-03`'s title ("Relocate the portfolio and seed a fictional example
> set") confirms ownership.
>
> **`uv run python -m src.governance`** → `Governance OK: 16 systems, 100 documents, 13 memories, 101
> backlog phases`, exit 0. Matches session record exactly.
>
> **`uv run pytest -q`** (not a required verification command but cited in the backlog `result` field)
> → `386 passed`, matches the claim.
>
> **Acceptance conditions — my own determination**
>
> 1. No tracked file matches the client identifier in any casing — **Not met.** Confirmed
>    independently: 3 files still contain `client-a` in id/name/description/tags fields. The session
>    record's own framing ("Not met") is correct and not overstated.
> 2. No tracked file outside `_private/` names a real project ID — **Not met**, same three files. I
>    additionally checked this wasn't a narrower miss: grepped every other real project id
>    against the whole tree
>    excluding `_data/projects/*` — zero hits anywhere. So the README fix (replacing the real project
>    list with category counts) fully closed that surface; the only remaining exposure is the three
>    `_data/projects/client-a-*.json` files themselves, which are `_private/`-bound content owned by
>    `phase-priv-03`, not something this phase's diff missed.
> 3. Tag taxonomy still exercises all six categories — **Met.** I parsed `_data/tags.json` directly:
>    `methodology`, `platform`, `domain`, `context`, `tech`, `client` are all present, and the `client`
>    category's single tag is now `id: "client-a"` (was the real client identifier), with `related` arrays in the `anaplan`
>    and `consulting` tags updated to reference `client-a` too. Taxonomy shape survives.
>
> **Deliverables and diff scope**
>
> All six declared deliverables (`README.md`, `ARCH-001-tagging-system.md`,
> `brain/concepts/tag-taxonomy.md`, `brain/index.md`, `tools/load_context.py`, `_data/tags.json`) were
> checked in the diff or verified to already be clean. `brain/concepts/tag-taxonomy.md` shows no diff
> in this range because it already had zero `client-a` matches beforehand (confirmed via `git log`/grep) —
> nothing was missed there, it just needed no edit.
>
> Two extra files not in the deliverables list were also scrubbed
> (`docs/02-prompts/PROMPT-002-...md`, `docs/08-governance/OPS-003-load-context.md`) — reasonable,
> in-scope-by-intent additions the session record explains and I verified both previously contained
> real `client-a` prose references now replaced.
>
> The rest of the diff (`docs/08-governance/catalog.md` document count bump,
> `docs/09-backlog/backlog.yaml` bookkeeping fields, the new session file) is ordinary
> governance/session-record bookkeeping, not unexplained scope creep.
>
> **Overall**
>
> No discrepancies found between the session record's claims and my independent reruns. The record's
> central claim — that this phase did its own scoped work correctly but two of three acceptance
> conditions remain genuinely unmet because the real leak lives in `_private/`-bound files
> (`_data/projects/client-a-*.json`) explicitly owned by `phase-priv-03` — holds up under independent
> verification. The phase should not be marked complete as-is; that is an owner decision (hold open
> vs. accept partial scope), not a defect in the work done.

## Decisions

- Orienting on `phase-idea-02` (front of `next_up`) surfaced the same acceptance-gap shape a prior
  session already found and the owner already declined to fix: it requires attaching triage findings
  to an idea with no writer support for that. Asked the owner again rather than assuming the earlier
  answer still held; they chose to skip it again, for the same reason.
- Orienting on `phase-priv-02` surfaced that its acceptance grep cannot pass from its own scope alone
  — the real client project files live in `_data/projects/`, and relocating them is `phase-priv-03`'s
  job. Asked the owner how to proceed rather than silently narrowing the phase or silently pulling
  `phase-priv-03`'s work forward; they chose to do the scoped work and report the gap honestly, which
  is what this session did.
- `docs/02-prompts/PROMPT-002-capture-and-structuring-system.md` was scrubbed even though it was not
  in the phase's declared `deliverables` list, because it named the real client tag id in prose and
  is squarely inside what the scope's own language ("Replace client identifiers...") intends to catch.
  Treated as an in-spirit completion of the declared scope rather than an out-of-scope addition.
- Left `phase-priv-02` `active` rather than asserting `complete`, consistent with the acceptance
  verdicts in this record — two of three conditions are `Not met` by the phase's own declared
  acceptance, and `session-close`'s completion rule requires all conditions `Met` plus review
  corroboration before `status: complete` may be written.
- **After** this `/session-close` run concluded with the phase left `active`, the owner was asked
  directly whether real portfolio data belongs in git at all, was told the answer is no and that
  `phase-priv-03` is the queued fix, and was then asked explicitly whether to mark `phase-priv-02`
  complete so `phase-priv-03` becomes claimable (it depends on `phase-priv-02` reaching `complete`).
  The owner said yes. `status: complete` was then written to `phase-priv-02` in `backlog.yaml` as a
  **direct owner instruction given outside the `/session-close` procedure**, not as this session or
  an agent's own judgement that the phase was finished — the two acceptance conditions the grep
  checks remain literally `Not met`, and the `result` field says so plainly rather than
  retroactively claiming they passed. `next_up` had `phase-priv-02` removed in the same change.

## Corrections

None. No claim made during this session was found wrong by the independent review or by rerunning
the verification commands.

## Left undone

- `phase-priv-02`'s two unmet acceptance conditions are not resolved by this session and are not
  this phase's to resolve — they require `phase-priv-03` ("Relocate the portfolio and seed a
  fictional example set") to relocate `_data/projects/client-a-ai-adoption.json`,
  `_data/projects/client-a-mvp4-sc.json` and `_data/projects/client-a-ortho-bridge.json` out of the tracked
  tree.
- The three `client-a-*.json` project files still reference the retired tag id `client-a` in their own `tags`
  arrays, which no longer exists in `_data/tags.json`. This is a dangling reference within still-real,
  still-tracked portfolio data; `project_tags` in `sql/001_schema.sql` carries no foreign key, so
  `tools/rebuild_db.py` does not fail on it, but `phase-priv-03` should resolve it when it rewrites or
  relocates those files.
- Whether `phase-priv-02` itself should be treated as satisfied by its own scoped work, or must wait
  for `phase-priv-03` to literally zero out the grep, is an explicit open question for the owner —
  see `## Unresolved` above. Not decided by this session-close run; `phase-priv-02` stays `active`.
