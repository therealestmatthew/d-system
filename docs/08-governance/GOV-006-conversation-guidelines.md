---
schema_version: 1
id: doc-conversation-guidelines
code: GOV-006
title: How agents report to the owner
kind: governance
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-11'
systems: [sys-governance]
depends_on: [doc-governance-protocol]
---

# How agents report to the owner

`AGENTS.md` governs the work. This governs how the work is reported. It is imported into every
Claude Code session from `CLAUDE.md`, so it costs context on every turn — keep it short, and add a
rule only when its absence has actually caused a misunderstanding.

## Name things, then cite them

Lead with what something is. The code goes in parentheses as the lookup handle, never as the noun.

> **Raw capture contracts** (`phase-cap-03`) — what a captured note looks like on disk, and the
> ignore rules that keep it untracked.

Not "phase-cap-03 is next." A bare code is a filename; the owner cannot read it without opening a
file, which is the cost this rule exists to remove. On first mention in a session, add a one-line
gloss of what the phase does — the title alone is often not enough.

The same applies to governed documents: "the capture routing decision (`ADR-007`)", "the
accepted-decisions record (`GOV-003`)", "the capture requirements (`REQ-002`)".

Nothing has to be invented. Phase titles are in `docs/09-backlog/backlog.yaml`, track prefixes are
glossed in `docs/09-backlog/README.md`, and document titles are in
[the catalog](catalog.md).

**Ideas invert this.** An idea's six-digit id in `_data/ideas.jsonl` is the actual lookup handle —
its title is prose the owner chose, not a filename — so lead with the id and gloss it in
parentheses after: `000046 (idea planner agent)`, not "the idea planner agent (`000046`)". Applies
anywhere an idea is named: in prose, in commit messages, in finding annotations.

## Show the output that carries information

Paste the real result when the number or the message is the point — a row count, a failure, a
diagnostic the owner would otherwise have to reproduce. Summarise when the output is a wall of
passing checks. A summary of a failure is not a result; the failure is the result.

This extends `AGENTS.md`'s standing rule that a failing check is a result to record rather than a
step to retry until quiet. Reporting it accurately is the other half of that.

## Do not block on a question that can wait

Ask when the answer changes what gets built, and ask at the point the work reaches it. Otherwise
state the assumption, keep working, and surface it at the end.

This is the same principle the capture system applies to the owner's own notes in
[ADR-007](../04-decisions/ADR-007-capture-routing.md): ambiguity is flagged, not interrupted for. An
agent that asks about everything moves the organising load back onto the person it exists to unload.

## Capture new asks as ideas, immediately

When the owner names a want outside the session's current work — a bug they noticed, a feature,
an audit, an item "for the next planning session" — record it at once through the sanctioned idea
writer (`tools/append_idea.py`), one idea per distinct ask, and confirm the ids back. Do not fold
it into the active task, and do not hold it in conversation memory until the end of the session.
This is the primary capture path in every session and context: it keeps the current work
uninterrupted while guaranteeing the ask survives the session. `ADR-010`'s record-as-given rule
applies; asks that form a batch for one future session are linked and annotated onto a shared
anchor idea so they surface together.

## Say plainly when a correction is a correction

If the owner corrects something and they are right, say so in a sentence and move on. Do not
re-litigate, and do not soften a wrong call into a partly-right one — a correction that is not
legible as a correction leaves the owner unsure whether it landed.
