---
schema_version: 1
id: doc-session-partition-generalization-and-programme-plans
code: SESS-2026-09-14-03
title: Generalizing the partition process, and twelve programme placeholder plans
kind: session
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems:
- sys-governance
- sys-backlog
- sys-portfolio
depends_on:
- doc-repeatable-idea-partition
- doc-idea-record-system
- doc-idea-staging
---

# Generalizing the partition process, and twelve programme placeholder plans

## Phase

None. This session claimed no backlog phase at any point — not one that closed partway through,
none from the start. It was owner-directed planning work under `AGENTS.md`'s "Owner-directed work
with no backlog phase" provision: the branch and worktree were named after the work, no claim
commit was made, and peers therefore held no lock against it. That was stated in the session's
first report rather than discovered at close.

Handling follows `brain/procedures/session-close-with-no-active-phase.md`. That entry's primary
case is a phase closing mid-session and work continuing unclaimed; this session is the further
variant — no phase was ever claimed — already handled once in `SESS-2026-09-12-03`.

Phases belonging to other sessions were `active` throughout and were not touched: `phase-demo-07`
(`agent-demo-glossary`), `phase-kit-02` (`agent-kit`) and `phase-lit-03` / `phase-lit-06`
(`agent-lit`). Their lines in `backlog.yaml` were left alone, including through two rebases that
conflicted on that file.

## Verification

No phase means no declared `verification` list. The checks below are the mechanical gates, run in
the session's own worktree at close:

```
uv run python -m src.governance
  -> Governance OK: 20 systems, 210 documents, 23 memories, 148 backlog phases

uv run pytest -q
  -> 580 passed, 2 warnings

uv run python tools/check_no_private_content.py
  -> check_no_private_content: OK (572 tracked files, 0 identifiers checked)
```

The identifier count is the finding, not a footnote. **`0 identifiers checked` is what this gate
reports from a worktree**, because `_private/portfolio/` does not exist there. Run in the primary
checkout after each of the three integrations, the same command reported
`31 identifiers checked` and passed. Every integration in this session was gated on the
primary-checkout run, not the worktree one.

Per-integration gate runs, all in the primary checkout on `dev`:

```
after d369386  Governance OK: 20 systems, 196 documents  | 580 passed | 31 identifiers checked
after e0638c8  Governance OK: 20 systems, 196 documents  | 580 passed | 31 identifiers checked
after c7b2f62  Governance OK: 20 systems, 209 documents  | 580 passed | 31 identifiers checked
after 39ba875  Governance OK: 20 systems, 210 documents  | 580 passed | 31 identifiers checked
```

## Acceptance

No phase, so no `acceptance` list to judge. The owner's four instructions and their outcomes:

| Instruction | Outcome |
|---|---|
| Generalize the partition process: governed requirement and plan first, do not begin the skill | Done. `REQ-009` and `PLAN-025` written; `phase-part-01`–`03` queued; no skill code written |
| Add `--status` to `build_idea_corpus.py` (`CORPUS_STATUS` is hardcoded) | **Planned, not built** — it is `phase-part-02`'s scope. Correct per the plan-before-code instruction |
| Draft a placeholder plan for each of the twelve programmes and append to the priority queue | Done. `PLAN-026`–`PLAN-037`, `phase-prog-01`–`12`, `next_up` appended |
| Move `P10` ahead of `P11` | Done. `next_up` swapped, both plans and the README corrected |

## Backlog

No phase's status changed. What was added:

- **Three phases** under `PLAN-025`: `phase-part-01` (write `PROMPT-034`), `phase-part-02`
  (`--status` plus the tests the corpus builder never had), `phase-part-03` (build
  `/partition-ideas`, depends on both).
- **Twelve phases** `phase-prog-01`–`12`, one per programme placeholder plan, each of which
  finalizes its plan into a real requirement and real phases.
- **`next_up`** now reads: `phase-wb-07`, `phase-port-02`, `phase-ses-01`, `phase-part-01`,
  `phase-prog-01`, `phase-prog-03`, `phase-prog-02`, then `phase-prog-04`–`12`.
- **`PROMPT-034` reserved** in `codes.yaml` as `phase-part-01`'s deliverable.
- **Two README track rows**: `phase-part-*` and `phase-prog-*`.

Nothing was pruned from `next_up`, because nothing reached `complete`.

## Unresolved

- **Sixteen open ideas, `000208`–`000223`, are untriaged** and therefore outside the accepted
  partition. The set refilled twice during this session, from 14 to 16.
- **The partition's loose ends are unruled**: two duplicate pairs, three closure candidates,
  seventeen proposed links from triage, and `000170`'s promotion path.
- **No ADR was written** for the three design rulings. `PLAN-025`'s open questions record why and
  invite the owner to overrule.
- **The backlog README track table is still missing four live prefixes** — `phase-agnt`,
  `phase-kit`, `phase-lit`, `phase-port`. Only the two rows this session introduced were added.
  Surfaced to the owner; not captured as an idea.
- **`PLAN-027`/`PLAN-028` code order does not match queue order** and cannot be made to. See
  `## Decisions`.

## Review

Independent review at close by a fresh general-purpose sub-agent (sonnet), given the four commit
hashes, fourteen claims to test, and the verification commands — and given none of this session's
reasoning. It reviewed each commit with `git show`, cross-checked every claim against repository
state, and ran the commands itself. Its findings, verbatim:

**1. REQ-009 — CONFIRMED.** `docs/06-requirements/REQ-009-repeatable-idea-partition.md` has valid
front matter (schema_version, id, code, title, kind, status: draft, owner, created/updated
2026-09-14, systems, depends_on) and a table of exactly 14 rows, R01–R14, each with a "Required
observable behavior" and a "Verification method" column. R02 and R12 are explicitly flagged as
verified only by reading a transcript, matching the claim's caveat.

**2. PLAN-025 — CONFIRMED.** Valid front matter, and the "Alternatives considered" section
documents three owner rulings dated 2026-09-14 (briefs become one governed document; open set
reported/gated rather than silently excluded; partition snapshots stay in `docs/00-working/` rather
than becoming governed documents), each with rejected alternatives — six alternatives total across
the three rulings.

**3. Three phases — CONFIRMED.** `phase-part-01`, `phase-part-02`, `phase-part-03` all exist in
`backlog.yaml` with `status: queued`. `phase-part-03` declares
`depends_on: [phase-part-01, phase-part-02]` (line 6756-6758).

**4. PROMPT-034 — CONFIRMED.** `docs/08-governance/codes.yaml` line 66-67 reserves it ("Reusable
partition pack; deliverable of phase-part-01"). No file under `docs/02-prompts/` exists yet, and no
document's front matter carries `code: PROMPT-034` — only forward references in backlog.yaml,
PLAN-025, and catalog.md (which lists it as `reserved`).

**5. Twelve placeholder plans — CONFIRMED.** PLAN-026 through PLAN-037 all exist, each
`status: draft`, `depends_on: []`, and each opens with the identical banner "**Placeholder. Not a
finalized plan.** ... **Do not build from this document.**"

**6. Twelve phase-prog phases — CONFIRMED.** `phase-prog-01`…`phase-prog-12` all exist,
`status: queued`, and each `plan:` field maps sequentially to PLAN-026…PLAN-037
(phase-prog-01→doc-concurrency-git-safety/PLAN-026 …
phase-prog-12→doc-standalone-explorations-housekeeping/PLAN-037).

**7. Coverage rule — CONFIRMED.** `src/governance/backlog.py:13` defines
`OPEN_PLANS = {"draft", "approved", "active"}`, and line 182-183 rejects an open plan with no
non-cancelled phase. Each of the twelve placeholder plans has exactly one phase pointing at it, and
`uv run python -m src.governance` exits 0, independently confirming coverage.

**8. Differing systems — PARTIAL, with a real discrepancy.** The twelve phases do not all share one
system (11 distinct values used across 12 phases), so the letter of "not all declare the same
system" holds. But the second part of the claim is **violated**: `phase-prog-01` (P3) and
`phase-prog-12` (P12) both declare `systems: [sys-governance]` (backlog.yaml lines 6805 and 7144),
and both phases' only deliverables are `docs/01-plans/PLAN-0XX-*.md` and `docs/06-requirements/` —
exactly the case the claim says shouldn't declare sys-governance. `sys-governance`'s actual owned
paths (`docs/08-governance/systems.yaml` lines 211-223) are `src/governance`, three schema files,
`docs/08-governance/systems.yaml`, `docs/08-governance/codes.yaml`, and
`tools/generate_tool_docs.py` — none of which either phase touches. Worse, this directly
contradicts commit `c7b2f62`'s own stated design: *"Each finalize phase declares its programme's own
system rather than sys-governance, which owns the governance machinery none of them touch —
declaring it would have falsely serialised all twelve."* That statement is false as written: two of
the twelve do declare it. And it is not merely cosmetic — `src/governance/backlog.py:39-40`
(`collisions()`) treats a shared system alone as grounds for a concurrency conflict, so
`phase-prog-01` and `phase-prog-12` mechanically cannot be claimed active at the same time, which is
exactly the "false serialization" the commit claims to have avoided.

**9. next_up order — CONFIRMED.** `backlog.yaml` lines 5-21 read exactly: phase-wb-07,
phase-port-02, phase-ses-01, phase-part-01, phase-prog-01, phase-prog-03, phase-prog-02,
phase-prog-04…phase-prog-12, with phase-prog-03 before phase-prog-02 as claimed.

**10. P10/P11 code-vs-queue-order note — CONFIRMED.** PLAN-027 states "Programme `P11` of the
twelve, **third in the owner's delivery order**" and "moved behind `P10`." PLAN-028 states
"Programme `P10` of the twelve, **second in the owner's delivery order**" and "moved ahead of
`P11`." `docs/09-backlog/README.md` line 25 states the delivery order "`P3`, `P10`, `P11`, then
`P1`, `P2`, `P4`–`P9`, `P12`" and explicitly notes the swap happened after codes were permanent,
pointing to `next_up` as authority. No remaining text found claiming P11 precedes P10.

**11. phase-part-03 next_action — CONFIRMED.** Current text: "Write the open-set gate first and run
it against the live log, which has had a non-empty open set every time it has been checked since the
first sweep... Read the count from fold() rather than from this line." No pinned count or id range
remains; commit `e0638c8` removed the earlier "14 open ideas, 000208 to 000221" wording.

**12. README track table row — CONFIRMED.** `docs/09-backlog/README.md` line 25 carries the
`phase-prog-*` row (quoted above under claim 10).

**13. No writes to ideas.jsonl — CONFIRMED.** `git show --stat` on each of the four commits
individually shows no `_data/ideas.jsonl` in any diff.

**14. AGENTS.md/CLAUDE.md untouched — CONFIRMED.** Same stat check confirms neither file appears in
any of the four commits' diffs.

### The reviewer's own verification output

```
uv run python -m src.governance
  -> Governance OK: 20 systems, 210 documents, 23 memories, 148 backlog phases  (exit 0)
uv run python -m src.governance --ready
  -> ran clean, ready-queue table renders correctly with the twelve phase-prog phases in order
uv run pytest -q
  -> 580 passed, 2 warnings
uv run python tools/check_no_private_content.py
  -> OK (572 tracked files, 31 identifiers checked)  (exit 0)
catalog regeneration vs committed file
  -> CATALOG-IN-SYNC (empty diff)
```

### Discrepancies, most serious first

> 1. **Claim 8 / commit message factual error.** `phase-prog-01` and `phase-prog-12` both declare
> `sys-governance`, contradicting commit `c7b2f62`'s explicit claim that none of the twelve does, and
> contradicting the stated rationale for avoiding it (false serialization). This is mechanically
> enforced: those two phases cannot be worked concurrently, which appears to be an unintended
> consequence rather than a deliberate choice — nothing in either phase's scope explains why P3's and
> P12's finalize work specifically needs `sys-governance` while all ten siblings, with the identical
> deliverable shape, use topic-specific systems instead.
>
> Everything else checked — REQ-009's fourteen rows, PLAN-025's three rulings, the three phase-part
> phases and their dependency, the PROMPT-034 reservation, the twelve placeholder plans and their
> phases, coverage under the governance rule, the next_up ordering and P10/P11 swap documentation,
> the de-pinned next_action, the README row, and the absence of any idea-log or protected-file
> writes — held up exactly as claimed, with no other discrepancies found.

### Response to the finding

**The finding is correct and is accepted.** `c7b2f62`'s commit message asserted something false, and
this record's first draft repeated it. The commit message cannot be amended — it is merged and
pushed — so the correction lives here and in `## Decisions`.

One clarification, not a defence: the two declarations were chosen rather than overlooked, which the
reviewer could not have known from the diff. `P3` is the governance-enforcement programme, so
`sys-governance` is its honest subject; `P12` was assigned it because every better-fitting system was
already taken by a sibling. The reviewer is right that the *stated rationale* does not cover either
case, and right that the resulting lock is mechanically real. The false claim was the error, not the
assignments — and the accepted collision is now written down where the next agent will find it
instead of rediscovering it from `collisions()`.

## Decisions

**The session ran unclaimed, deliberately.** Writing a requirement and a plan for work that had no
phase yet is exactly the case `AGENTS.md` provides for, and `CLAUDE.md` forbids manufacturing a
backlog phase to have something to claim. The alternative — claim one of the twelve phases this
session created — would have been circular. Stated in the first report, not discovered at close.

**Three rulings on how a partition sweep becomes repeatable** (owner, 2026-09-14, via
`AskUserQuestion` before any document was written, because each changes the requirement itself):

1. *The briefs go in one governed prompt document*, `PROMPT-034`, and the skill becomes a thin
   runner that dispatches its sections verbatim. Rejected: inlining them in the skill body, which
   would leave the synthesis protocol Claude-only, ungoverned and uncitable; and elevating them to a
   `GOV` document, which would mix dispatchable prompt text into a rules document.
2. *The open set is reported and gated, not silently excluded.* `triaged` stays the default corpus,
   but the sweep counts open ideas, prints every id, and stops. Rejected: running the triage sweep
   automatically first, which folds an owner-visible step into a subroutine; and partitioning
   `triaged,open` together, which feeds the finding-readers ideas that carry no findings.
3. *Each sweep writes a new dated document* under `docs/00-working/`. Rejected: overwriting the one
   partition file; and promoting the partition to a governed document, which `ADR-010` already
   argues against for an artifact that decays by design.

**Twelve sibling plans, not one parent with twelve children** (owner, 2026-09-14). The partition's
own claim is that the programmes are independently implementable, and siblings let any one be
finalized, superseded or dropped without touching a parent. The codes were assigned in *delivery*
order, which is what later produced the `PLAN-027`/`PLAN-028` mismatch below.

**Placeholder depth: deliberately minimal** (owner, mid-turn): "super high level, just a placeholder
with key references and summary and instructions that it needs to be finalized." Each plan therefore
carries a banner, a group table, references, what finalizing requires, and the facts a finalize
session should not have to rediscover — and no design.

**Each placeholder still needed exactly one phase, for a mechanical reason.**
`src/governance/backlog.py` defines `OPEN_PLANS = {"draft", "approved", "active"}` and rejects an
open plan with no non-cancelled phase. A zero-phase placeholder would fail the governance check, so
the honest phase is "finalize this plan" — which is also genuinely a session of work per programme.
This was checked in the source before the option was offered to the owner rather than assumed.

**`depends_on: []` on all twelve placeholders** (my call). A placeholder has source material, not
prerequisite documents. Setting edges now would mean guessing, and each finalize phase would have to
undo the guess. Each document states this explicitly so it does not read as an oversight.

**Each finalize phase declares a system chosen for its own programme rather than one shared system
for all twelve** (my call). `sys-governance` owns `src/governance`, three schemas, `codes.yaml`,
`systems.yaml` and `generate_tool_docs.py` — not `docs/01-plans/`. Declaring it on all twelve would
have locked machinery none of them touches and serialized the entire queue behind a false
dependency. Eleven distinct system values are used across the twelve phases.

**Two of the twelve do declare `sys-governance`, and `c7b2f62`'s commit message wrongly said none
did.** `phase-prog-01` (`P3`) and `phase-prog-12` (`P12`) both carry it, so the two mechanically
conflict — `src/governance/backlog.py`'s `collisions()` treats a shared system alone as grounds for
a conflict — and they cannot be claimed active at the same time. The independent review at close
caught the false claim; see `## Review`.

The two declarations are kept, for different reasons. `P3` *is* the governance-enforcement
programme — hooks, settings, tests and the harness rules are its subject — so `sys-governance` is
the honest declaration there, not a placeholder. `P12` is a readability bucket with no subject of
its own, and every alternative system is already taken by a sibling, so any reassignment moves the
collision rather than removing it. The practical cost is nil: `P12` is last in a twelve-item
sequential queue and `P3` is first, so they will not be worked concurrently. What was wrong was the
commit message's absolute claim, not the assignments. If the owner would rather `P12` collide with
nothing, giving it an empty `systems` list is a one-line change.

Conflicts as actually built: `phase-prog-01` against `phase-prog-12` (`sys-governance`, described
above), and `phase-prog-04` against the active `phase-demo-07` (`sys-portfolio`, which is a real
overlap on the idea log).

**`P10` moved ahead of `P11`** (owner, after I flagged it). `G40`'s container-vs-content vocabulary
sits in `P10` and is named a prerequisite by six ideas, four of them in `P11`. I raised it as a flag
rather than resolving it, and the owner ruled. The swap then required correcting four files, because
text in both plans, two phase entries and the README all asserted the old order.

**One commit for `REQ-009` + `PLAN-025` + three phases, not two.** `AGENTS.md` prefers narrow
diffs, but an open plan without its phases fails the governance check, so the two halves are only
coherent together. I began splitting them, found the first commit would have carried a catalog
describing documents it did not contain, and reversed.

## Corrections

**I asserted in a commit message that none of the twelve finalize phases declares
`sys-governance`. Two do.** `c7b2f62`'s message stated it as an absolute, and the stated rationale —
avoiding false serialization — is contradicted by `phase-prog-01` and `phase-prog-12` mechanically
conflicting over that exact system. The independent review at close caught it; I had not. The
commit is merged and pushed, so the message cannot be amended, and the correction lives in
`## Review` and `## Decisions` instead. The assignments themselves were deliberate and are kept;
what was wrong was claiming a clean rule where there were ten cases and two exceptions.

**I pinned an open-idea count into a tracked file.** `phase-part-03`'s `next_action` read "14 open
ideas today, `000208` to `000221`". Two more ideas arrived within the hour, and the count was wrong
before the ink dried — which is the exact fault `PLAN-025` criticizes `PROMPT-032` for carrying.
Fixed in `e0638c8`: the hint now states the condition and points at `fold()` for the number.

**I reported `dev` as clean and unmoved, and the owner corrected me.** It was true when I checked
and false by the time they read it — a peer integrated 26 commits, `phase-lit-06` among them, in
between. The owner caught it and directed a rebase before integration. The lesson is not that the
check was wrong but that its answer expires, so on this repository the rebase question is re-asked
at the moment of merge rather than at the moment of the report.

**I assumed the `Claude-Session` commit trailer identified a session.** It does not: the same id
appears on 39 commits spanning many sessions in this repository. Caught before it was used to scope
the independent review, which was given the four commit hashes explicitly instead. Worth recording
because the trailer looks exactly like a session discriminator and is not one.

**Two wasted steps, no bad state reached.** I ran `git merge --ff-only` once inside a worktree,
where it was a no-op, before running it in the primary checkout where it belonged; and I regenerated
the catalog for a two-commit split I then abandoned.

## Left undone

**Everything the partition system actually needs built.** `PROMPT-034`, the `--status` flag, and the
`/partition-ideas` skill are all queued as `phase-part-01`–`03` and none was started. That is not a
shortfall: the owner's instruction was plan before code, explicitly "do not begin the skill". The
corpus builder's missing tests went the same way, into `phase-part-02`.

**The twelve programmes have no designs.** Twelve placeholders and twelve finalize phases exist;
twelve requirements and twelve real phase sets do not. That is the next body of work, and
`phase-prog-01` (`P3`) is its front.

**Sixteen ideas remain untriaged**, `000208`–`000223`. They are outside the accepted partition
entirely, and the set grew twice during this session. A future sweep needs them triaged or an
explicit ruling to partition without them — which is precisely the gate `REQ-009` R05 exists to
force.

**The partition's own loose ends are untouched**: the duplicate pairs `000150`/`000195` and
`000198`/`000208`, the closure candidates `000157`, `000207` and `000198`, `000170`'s promotion path,
and seventeen links proposed by triage that nobody has ruled on. All are recorded in
`docs/00-working/handoff-idea-partition-and-triage.md`; none was acted on here because each is an
owner ruling rather than a task.

**Four track prefixes still have no README gloss** — `phase-agnt`, `phase-kit`, `phase-lit`,
`phase-port`. `GOV-006` sends agents to that table for prefix meanings, so those four currently
resolve to nothing. I added only the two rows this session introduced; backfilling the rest was
outside the ask and was surfaced to the owner instead.

**No ADR for the three design rulings.** `PLAN-025` records the reasoning and says plainly that if
the owner wants them citable on their own, an ADR should be added and the plan amended to reference
it.
