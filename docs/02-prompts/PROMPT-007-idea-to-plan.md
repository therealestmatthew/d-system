---
schema_version: 1
id: doc-prompt-idea-to-plan
code: PROMPT-007
title: Turn a triaged idea into a requirement, a plan and phases
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

# Turn a triaged idea into a requirement, a plan and phases

Second of four: [PROMPT-006](PROMPT-006-idea-capture-and-triage.md) captures and triages, this one
plans, [PROMPT-008](PROMPT-008-execute-a-phase.md) executes, and
[PROMPT-009](PROMPT-009-plan-audit.md) audits.

Reusable. Run it against one triaged idea the owner has chosen to pursue.

---

## The prompt

> You are working in the D-System repository. Read `AGENTS.md` first — it governs everything here.
> Then `docs/08-governance/GOV-001-protocol.md` (document lifecycle),
> `docs/08-governance/GOV-002-backlog-protocol.md` (phase rules),
> `docs/08-governance/GOV-005-document-codes.md` (codes), and
> `docs/08-governance/GOV-006-conversation-guidelines.md` (reporting).
>
> Your job is to turn **one** triaged idea into governed work: a requirement, a plan, and backlog
> phases. You are not implementing it. Writing code during this session defeats the purpose of the
> rule you are enacting.
>
> The idea to plan is: **[IDEA ID]**
>
> ### Read before you write
>
> Read the idea through the fold, not raw `_data/ideas.jsonl` — see
> [PROMPT-006](PROMPT-006-idea-capture-and-triage.md) for why. Read every finding annotation on it;
> triage already did the scouting, and repeating that search wastes a session. Follow the annotations
> to the documents and phases they name and read those too.
>
> If the idea is still `open`, stop and say so. Triage it first with
> [PROMPT-006](PROMPT-006-idea-capture-and-triage.md); planning against an unscouted idea is how
> duplicate plans get written.
>
> ### The requirement document
>
> A requirement states **observable, testable claims about the finished system** — what must be true,
> and how you would know. It contains no implementation detail, no sequencing, and no file lists.
>
> Each statement should be falsifiable by running something. "The rebuild is atomic" is a
> requirement; "use a temp file and rename" is a design choice that belongs in the plan. If you
> cannot say how a statement would be verified, it is not a requirement yet — either sharpen it or
> record it as an open question.
>
> Allocate the code: `uv run python -m src.governance --next-code requirement`. Never pick a number
> by reading the directory; it cannot show reserved or retired codes.
>
> ### The plan document
>
> The plan says **how and in what order**, and carries the reasoning the requirement deliberately
> excludes: alternatives considered, the approach chosen and why, constraints, dependencies, and what
> is explicitly out of scope.
>
> Allocate with `uv run python -m src.governance --next-code plan` (add `--parent <doc-id>` for a
> child plan). Link the plan to its requirement through `depends_on`, and say in prose which
> requirement statements each part of the plan satisfies.
>
> ### The phases
>
> A phase is **the smallest planned unit of work that fits in one bounded session**. Add them to
> `docs/09-backlog/backlog.yaml`. An open plan with no phases fails the governance check, so the plan
> and its phases land together.
>
> Each phase carries:
>
> - `scope` — the work boundary, stated so an executing agent knows what not to touch.
> - `acceptance` — conditions that are individually checkable. Not "the feature works".
> - `verification` — the actual commands to run, or a prose behavioural check where no command fits.
> - `systems` and deliverable paths — these are the **lock table**; a peer's claim is checked against
>   them, so under-declaring causes collisions and over-declaring blocks peers needlessly.
> - `depends_on` — real prerequisites, not a wish about ordering.
>
> Size them honestly. A phase that cannot finish in one session is two phases. A phase whose
> acceptance you cannot check is not ready to be written down.
>
> ### Promote the idea
>
> Once the plan exists, move the idea `triaged` → `promoted` through the sanctioned writer
> (`tools/append_idea.py`), recording the plan it promoted into. Never hand-edit the log.
>
> ### Finishing
>
> - `uv run python -m src.governance --catalog > docs/08-governance/catalog.md`
> - `uv run python -m src.governance` must exit 0.
> - `uv run pytest` must be green.
> - `uv run python tools/check_no_private_content.py` **with your changes staged**.
> - Report: name the requirement, plan and each phase with its code, and say plainly what you left as
>   an open question rather than resolving by assumption.
>
> Do not push. Do not implement anything. Do not mark any phase complete.

---

## Notes for the owner

The requirement/plan split is the part most likely to be skipped. As of 2026-09-08 this repository
had far more plans than requirements, and most plans folded acceptance criteria directly into the
plan document — which is idea `000038`'s subject. This prompt takes the strict reading: observable
claims in the requirement, sequencing and rationale in the plan.

If that proves too heavy for small work, the honest fix is to write down when a requirement is
mandatory, not to quietly stop writing them.
