---
schema_version: 1
id: doc-prompt-plan-audit
code: PROMPT-009
title: Audit plans against their phases and the implementation
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

# Audit plans against their phases and the implementation

Fourth of four: [PROMPT-006](PROMPT-006-idea-capture-and-triage.md) captures and triages,
[PROMPT-007](PROMPT-007-idea-to-plan.md) plans, [PROMPT-008](PROMPT-008-execute-a-phase.md)
executes, and this one checks whether the record still matches reality.

Reusable, and deliberately **read-only**. Run it periodically, or before committing to a large piece
of work, to find where the plan record and the repository have drifted apart.

---

## The prompt

> You are auditing the D-System repository. Read `AGENTS.md` first, then
> `docs/08-governance/GOV-001-protocol.md`, `docs/08-governance/GOV-002-backlog-protocol.md` and
> `docs/08-governance/GOV-006-conversation-guidelines.md`.
>
> **This is a read-only audit. Change nothing.** Do not fix what you find, do not edit a document, do
> not adjust a phase. The deliverable is the finding list. Fixing during an audit destroys the
> baseline you are measuring against, and the decision to act belongs to the owner.
>
> Your posture is adversarial toward the *record*, not toward the work. Assume documents overstate
> what exists, because they describe intent and are written before the work. Verify against code,
> schemas, tests and command output — never against another document's claim about the same thing.
>
> ### What to check
>
> **1. Plan and phase consistency.**
> For every plan in `docs/01-plans/`: does it have phases? An open plan with no phases fails the
> governance check. Are all its phases complete while the plan itself is still `draft` or `active`?
> Is it `complete` without `completion_evidence`? Does its `completion_evidence` name files that
> actually exist and actually demonstrate what they are cited for?
>
> **2. Claimed capability versus implemented capability.**
> Plans describe proposed work. For each plan claiming a capability exists, find it in the code. A
> phase marked complete whose deliverable is an empty scaffold is the specific failure to hunt for.
> Report the file and line that settles it either way.
>
> **3. Requirement coverage.**
> Which requirement statements have no phase that would satisfy them? Which phases satisfy nothing
> traceable to a requirement? Both directions matter — orphaned work and unimplemented intent are
> different problems.
>
> **4. Backlog integrity.**
> Phases whose `depends_on` names something that does not exist, is deferred, or is itself blocked.
> Phases `active` with no agent, or with an agent but no session record. Phases complete without a
> session or without completion evidence. Deliverable paths and systems that under- or over-declare
> what the phase actually touches — under-declaring breaks the lock table.
>
> **5. Stale references.**
> Documents naming a branch, path, tool, command or document code that no longer exists. Pointers to
> superseded documents. Anything asserting a state of the world that has since changed —
> `AGENTS.md` and `CLAUDE.md` both carried an obsolete no-remote rule for a day after
> `phase-priv-05` pushed, and nothing caught it automatically.
>
> **6. The governance checks themselves.**
> Run `uv run python -m src.governance`, `uv run pytest`, and
> `uv run python tools/check_no_private_content.py`. Record the literal output. If the tree is red,
> that is the first finding, not a reason to stop.
>
> ### How to report
>
> Rank findings by consequence, not by how easy they are to fix. For each:
>
> - **What is wrong**, in one sentence.
> - **The evidence** — file and line, or the command and its literal output. Never a claim from
>   another document.
> - **Confidence**, and the alternative reading where one is reasonable. "This looks unused" and
>   "this is unused" are different findings.
> - **What it would take to resolve**, without doing it.
>
> Separate three things that are easy to conflate: a document that is *wrong*, a document that is
> *out of date*, and a document that describes work that was *deliberately not done*. Only the first
> two are defects.
>
> Report clean findings explicitly. "No discrepancies found in the backlog dependency graph" is a
> result worth stating; silence is not.
>
> Do not commit. Do not push. Do not change a single file.

---

## Notes for the owner

The read-only rule is the load-bearing part. An auditing agent that fixes as it goes produces a tidy
tree and no reliable account of what was broken — and the fixes arrive without a requirement, a plan
or a phase, which is the process this repository exists to enforce.

The output of this prompt is input to [PROMPT-007](PROMPT-007-idea-to-plan.md): findings worth acting
on become ideas, then plans, then phases. Findings not worth acting on are still worth recording, so
the next audit does not re-derive them from scratch.
