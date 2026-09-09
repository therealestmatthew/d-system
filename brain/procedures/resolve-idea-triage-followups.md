---
id: mem-proc-resolve-idea-triage-followups
title: Resolving Staged Idea-Triage Follow-ups via AskUserQuestion
type: procedure
tags: [ai-tools, agentic-systems, knowledge-base]
source_model: anthropic/claude-sonnet-5
project: d-system
created: 2026-09-09
updated: 2026-09-09
confidence: high
related: [mem-proc-session-close-no-active-phase]
scope: project
---

## The situation

`.claude/commands/idea-triage.md` (`phase-idea-02`) scouts every open idea and writes a
`kind: finding` annotation on each, collecting any `PROPOSED LINK:` / `PROPOSED PROMOTION:`
lines it surfaces — but it never executes them. Those proposals, plus any borderline or
not-directly-executable observations (a link that names a document code instead of an idea
id, a sequencing note), get staged as an ephemeral file under `_working/`
(`idea-triage-followups.md`, per `PLAN-015`) for a **separate, later session** to work through
with the owner. This procedure is that later session's job.

## Steps

1. **Re-check current state before presenting anything.** Some proposals may already be
   resolved (an idea promoted or discarded since the file was written) or contradicted (a link
   already exists). Fold the log rather than reading raw JSON — `_data/ideas.jsonl` is an
   append-only event log, and a raw line can be stale if the idea was later `amend`ed — and
   check both `status` and existing `links` for every idea named in the file:

   ```bash
   uv run python -c "
   from src.db.ideas import fold, LOG
   import json
   events = [json.loads(l) for l in open(LOG) if l.strip()]
   state = fold(events)
   # inspect state[id]['status'], state[id]['links'], state[id]['promoted_to']
   "
   ```

   Drop stale items silently — do not present something already resolved as if it were still
   live.

2. **Present in batches of up to 4 via `AskUserQuestion`**, grouped by the clusters the
   triage file already lays out (a starting grouping, not mandatory — merge or split if it
   reads better). Each question:
   - Names both ideas by id and a short gloss of what each is, not just the id — the owner
     should not have to open the file to know what they're deciding.
   - Carries a recommendation as the first, explicitly-labeled option, per this repo's
     `AskUserQuestion` convention (`(Recommended)` suffix).
   - Offers a real alternative (skip, reject, or "review individually" for a whole cluster)
     rather than a single confirm button.

3. **Execute only what the owner actually approved**, using the sanctioned writer — never
   hand-edit `_data/ideas.jsonl`:
   - Link: `uv run python tools/append_idea.py link <idea> --type <type> --target <target>`
   - Promotion: `uv run python tools/append_idea.py status <idea> promoted --promoted-to <code>`

4. **Expect the owner to restructure proposals, not just approve/reject them** — this is the
   step worth documenting, because it is not what the mechanical `link`/`status` commands
   alone suggest. In the run this procedure was written from, the owner:
   - Changed a proposed `extends` link to `relates_to` between two siblings, then asked for a
     **new shared parent idea** for both to `extend` instead ("they are both extensions of
     idea management system as a whole").
   - Flagged that a proposed link named a *document* code (`PLAN-001`) as a target, which the
     `linked` event schema does not support (idea-to-idea only) — the resolution was to leave
     it as prose-only context for that session, but also to **capture the gap itself as a new
     idea** (schema should support idea-to-document links), since a design limitation surfaced
     mid-review is exactly what the idea system exists to catch.

   When this happens: create the new idea(s) first with
   `uv run python tools/append_idea.py add --title "..." --body "..."` (use `--file` for
   anything with backticks/quotes/newlines), capture the returned id, then link the original
   ideas to it. Don't force the owner's restructuring request into the original two-idea link
   shape just because that's what was already staged.

5. **The owner may keep going past the staged file's contents** — asking for entirely new
   ideas captured in the same sitting (a new agent concept, a new umbrella topic). Treat these
   with the same rigor as anything in the triage file: write full bodies (scope, what exists
   today, what's unresolved, cross-references to related ideas by id), not one-line stubs, and
   link them into the existing graph rather than leaving them as orphans. This is a natural
   extension of the same session, not a scope violation.

6. **After every batch of writes** (not just at the very end):
   ```bash
   uv run python tools/generate_ideas_md.py
   uv run python -m src.governance
   ```
   A red governance check is never something to carry into the next batch.

7. **Delete the ephemeral `_working/` file once fully worked through**, per `PLAN-015` — it is
   gitignored and ungoverned by design, not a record to preserve. The durable record of what
   happened is the idea log itself (the `linked`/`status`/`created` events) plus this
   procedure, not the staging file.

## Why this is worth a durable entry

The mechanical half of this (re-check state, batch via `AskUserQuestion`, run `link`/`status`,
regenerate, delete) is easy to reconstruct from `PLAN-015` and the triage command doc alone.
The half that is *not* obvious from those documents — and the reason this exists — is that the
owner treats this resolution session as a second design pass, not a rubber stamp: proposed
relationships get restructured (new parent ideas introduced), gaps in the idea schema itself
get surfaced and captured as new ideas, and the session naturally extends into capturing
further new ideas beyond the staged list. An agent that treats step 3 as the whole job will
under-deliver relative to what the owner actually wants from this step.

## Worked example (2026-09-09)

Resolved `_working/idea-triage-followups.md` from `SESS-2026-09-08-18`'s addendum (33+ staged
proposals across 8 clusters plus 3 promotions). Outcome: 2 promotions applied (000003, 000019),
1 held back pending further review (000045, borderline); ~35 links written across all clusters;
3 new umbrella ideas created (000050 idea management system, 000051 agent harness and
guardrails, 000052 schema-driven consistency) to hold restructured relationships instead of the
originally-proposed idea-to-idea links; 1 new idea created (000053) capturing the idea-to-document
link-schema gap, then linked as `extends` onto the existing idea (000018) that already covers
tagging/schema extension, once a search of the current corpus showed it wasn't actually a novel
concept. The same session, still in the same sitting, then captured 7 further new ideas the
owner raised from scratch (000054–000060: observability, a connection-builder agent, doc
governance, testing strategy, version control, git, memory/context management), cross-linked
into the existing graph rather than left standalone.
