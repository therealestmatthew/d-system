---
schema_version: 1
id: doc-prompt-idea-capture-and-triage
code: PROMPT-006
title: Capture and triage ideas
kind: prompt
status: active
owner: repository-owner
created: '2026-09-09'
updated: '2026-09-09'
systems:
- sys-governance
- sys-backlog
depends_on: []
---

# Capture and triage ideas

First of four prompts covering the idea-to-delivery path: **capture and triage** (this document),
then [PROMPT-007](PROMPT-007-idea-to-plan.md) to turn an idea into a plan,
[PROMPT-008](PROMPT-008-execute-a-phase.md) to execute one, and
[PROMPT-009](PROMPT-009-plan-audit.md) to audit what exists.

Reusable. Run it whenever ideas need recording, or whenever open ideas have accumulated enough to be
worth scouting.

---

## The prompt

> You are working in the D-System repository. Read `AGENTS.md` first — it is the working agreement
> and governs everything here, whatever framework you are running under. Then read
> `docs/08-governance/GOV-006-conversation-guidelines.md` for how to report.
>
> Your job is to **capture new ideas and triage open ones**. You are not planning or building
> anything. An idea is a parked thought; turning it into work is a separate step with its own prompt.
>
> ### Reading idea state
>
> `_data/ideas.jsonl` is an append-only event log. A single idea's current state is the *fold* of its
> events, not any one line. **Never read raw `ideas.jsonl` to determine an idea's state** — a raw
> read shows superseded titles, retracted annotations and stale statuses as though they were current.
> Use the fold in `src/db/ideas.py`, or the generated view at `docs/00-working/ideas.md`, which is
> regenerated from the log by `tools/generate_ideas_md.py`. The one exception is analysis *of the
> idea system itself*, where the raw event shapes are the subject.
>
> ### Writing ideas
>
> **Never hand-edit `_data/ideas.jsonl`.** Every write goes through the sanctioned writer,
> `tools/append_idea.py`, which allocates the six-digit id, validates the event against
> `schemas/idea.schema.json`, and enforces the legal status transitions. Hand-editing bypasses the id
> allocator and the transition table, and has produced a corrupted record before.
>
> Legal statuses are `open` → `triaged` → `reviewing` → `promoted` or `discarded`. Nothing skips
> backwards.
>
> ### Capturing a new idea
>
> Record what the owner actually said, not a tidied version of it. A good idea record carries:
>
> - **What the idea is**, in enough detail that it survives being read cold in six months.
> - **What it would touch** — files, schemas, systems, other ideas.
> - **How it would be verified** if built, even roughly. An idea with no observable outcome is a
>   wish; say so rather than inventing criteria.
> - **What is unresolved** — the open design questions, the dependencies that do not exist yet, the
>   reason it is parked rather than planned.
> - **Where it came from** — the conversation, the session, the observation that prompted it.
>
> Do not merge two ideas because they are adjacent, and do not split one because it is long. Record
> what was meant.
>
> ### Triaging an open idea
>
> Triage is *scouting*, not judgement. For each idea at `status: open`:
>
> 1. Search the repository for what already relates to it — existing plans, backlog phases, ADRs,
>    requirements, governance documents, other ideas.
> 2. Record what you found as a **finding annotation** on the idea, through the sanctioned writer.
>    Name what relates and how, with document codes and phase ids.
> 3. Move it `open` → `triaged`.
>
> **Never move an idea past `triaged`.** Promoting or discarding is the owner's decision, and
> promotion requires a plan to promote *into* — that is [PROMPT-007](PROMPT-007-idea-to-plan.md)'s
> job. Do not merge, decline, or rewrite an idea's substance during triage. If two ideas look like
> duplicates, say so in the annotation and let the owner decide.
>
> Write annotations in your own voice as an agent, distinctly from the owner's. Preserve dissent:
> if an idea looks wrong to you, record why as an annotation rather than discarding it.
>
> ### Finishing
>
> - Regenerate the view: `uv run python tools/generate_ideas_md.py`
> - `uv run python -m src.governance` must exit 0.
> - `uv run pytest` must be green.
> - Run `uv run python tools/check_no_private_content.py` **with your changes staged** — it reads
>   `git ls-files` and cannot see an unstaged file.
> - Report using the ideas convention: lead with the six-digit id, gloss it after —
>   `000046 (idea planner agent)`, not "the idea planner agent (`000046`)".
>
> Do not push. Do not mark any backlog phase complete.

---

## Notes for the owner

Triage is deliberately incapable of closing anything. The system's value is that a parked idea stays
parked with its reasoning attached, rather than being quietly resolved by whoever read it last. The
agent scouts and reports; you decide.

If triage keeps surfacing the same relationship between two ideas, that is a signal worth acting on —
but the action is yours, and it belongs in a plan, not in the idea log.
