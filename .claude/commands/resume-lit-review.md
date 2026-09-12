---
description: Resume the adversarial literature-review campaign — run one execution session of the next phase-lit phase
argument-hint: "[phase-id]"
---

# Resume the literature-review campaign

Runs **one execution session** of the adversarial D-System literature-review campaign. Every
invocation is a resume, never a restart: the campaign spans seven phases on one long-lived branch,
and this command picks up wherever the backlog says it is.

`$ARGUMENTS`, if given, names the phase to work. Otherwise the phase is determined from the
backlog — see step 2. Do not accept a phase named in conversation over what the backlog says;
the backlog is the lock table.

## This command adds nothing to the campaign's governance

It is a loader, not an authority. The campaign's instruments are governed documents and they win
over anything written here:

| What | Where | Authority |
|---|---|---|
| Per-campaign rulings, pinned state, the kick-off paragraph | `docs/02-prompts/PROMPT-031-literature-review-kickoff.md` | **Wins over everything below** |
| The coordinator role, preflight, close-out | `docs/02-prompts/PROMPT-030-literature-review-coordinator.md` | Generic and idempotent |
| Every prompt dispatched to a worker | `docs/02-prompts/PROMPT-029-literature-review-delegation-pack.md` | Verbatim; nothing authored mid-campaign |
| Phase graph, branch model, deliverable ownership | `docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023-overview.md` | |
| Domain matrix, evidence contract, scope record | `PLAN-023.02`, `PLAN-023.03`, `PLAN-023.01` | Win over a section on data |
| The research protocol this campaign tests | `docs/08-governance/GOV-009-research-protocol.md` | |

If this file ever contradicts one of them, that document is right and this file is stale — say so
and stop rather than following it.

## 1. Read, in this order

1. `AGENTS.md` — the working agreement, including the worktree rule and the concurrency protocol.
2. `docs/08-governance/GOV-006-conversation-guidelines.md` — how to report to the owner.
3. `docs/02-prompts/PROMPT-031-literature-review-kickoff.md` — the kick-off record. It carries the
   owner's four per-campaign deltas and **wins wherever it differs from the coordinator prompt**.
4. `docs/02-prompts/PROMPT-030-literature-review-coordinator.md` — in full.

Do **not** front-load the content methodology (`research/literature-review/CLAUDE.md`) into your own
context. The pack's sections carry what their workers need; load it only where a dispatched section
calls for it.

## 2. Preflight — a resume, not a first phase

Run these and record the real output. A failing check is a result to record, not a step to retry
until it goes quiet.

```bash
uv run python -m src.governance            # must exit 0
uv run python -m src.governance --ready    # claims, locked systems, queue front
git status --short                         # must be clean
git branch --show-current
```

Then confirm each of these, and stop rather than proceed if any fails:

- **The campaign branch and worktree exist.** `agent/lit-campaign` in
  `../d-system-worktrees/lit-campaign`. Every campaign phase commits to that one branch
  (`PLAN-023`'s owner-ratified branch model), so the ledger, inventory and matrix from earlier
  phases are present without cross-branch archaeology. If the worktree is gone, recreate it from an
  up-to-date `dev` (`git worktree add ../d-system-worktrees/lit-campaign agent/lit-campaign`) and
  install its own `.venv` — gitignored paths never come with a worktree. If the *branch* is gone,
  that is a blocking finding, not something to recreate.
- **A worktree is mandatory.** `AGENTS.md` as of 2026-09-12 requires every session to work in one,
  documentation-only work included. The only work permitted in the primary checkout is the claim
  commit and the catalog regeneration that claim forces.
- **Prior-phase evidence is present and must never be recreated.**
  `research/literature-review/00_search_ledger.csv` and `03_source_inventory.csv` carry the
  campaign's reproducibility record. If they are missing, **stop and report** — a recreated ledger
  silently erases the record the whole campaign rests on.
- **Baseline integrity.** `research/pre-literature-baseline.md`,
  `research/pre-literature-hypotheses.yaml` and `research/adversarial-codebase-review/` are
  unmodified. A modified baseline is a blocking finding; do not "restore" it yourself.
- **Peer claims do not collide.** Demo work wins every conflict. If a peer holds an active claim
  overlapping `sys-research`, stop and report rather than working around it.
- **Which phase is current**, read from `docs/09-backlog/backlog.yaml`: the first `queued`
  `phase-lit-*` whose `depends_on` are all `complete`. If a `phase-lit-*` is already `active`, this
  session is a **resume of it** — pick up from its first incomplete work item, and read its session
  record before dispatching anything.

**`phase-lit-07` has a stated entry condition.** It may not start until `PROMPT-031` carries a dated
`pre-synthesis check-in held: <date>, ruling: proceed` entry in its own section. That section is
empty by construction. A kick-off paragraph describing the planned pause is not a held check-in.

## 3. You are the coordinator

You dispatch the pack's sections and verify what comes back. That is the whole job.

**You do not** search, fetch, read a source, score a collision, write any campaign deliverable,
write a finding, author or edit any prompt, or fix a worker's output yourself. A coordinator that
"just adds the missing row" has destroyed the separation the campaign's evidence hygiene depends on.

**A missing prompt is a blocking finding for the owner**, never something to improvise.

**You verify rather than trust.** A worker's claim to have logged twenty rows is not twenty rows;
check the file. Measure gate conditions yourself against the deliverables before and after each
dispatch.

Dispatch rules, from the pack: sections go verbatim, one at a time, in the order the pack lists
them, assembled as shared blocks plus that section's payload — never the whole pack, never the whole
domain matrix. `K` first, then each `S`/`X` pair in order, `G` last. Models are fixed: `K` and `G`
on Haiku, everything else on Sonnet. At most **two fix cycles** per work item. Commit before review,
so a truncated agent is resumed rather than re-run.

## 4. Operational facts learned in `phase-lit-01`

These are observations from the campaign's first executed phase, recorded in
`docs/03-sessions/SESS-2026-09-12-05-literature-review-pass-1a.md` and ideas `000147`–`000150`
(anchored on `000147`). They are not new rules and do not override the pack — they exist so a fresh
coordinator does not pay to rediscover them. Pass the relevant ones into each dispatch as
addressing, the way that session did.

- **The ledger is CRLF-terminated throughout.** A text-mode read/write round-trip strips it; one
  dispatch did exactly that and needed a repair cycle. Read and write raw bytes, and verify the
  whole file rather than the tail.
- **Identifier form is not fixed by the evidence contract, and that gap bites the phase gate.**
  Write `kept` and `url_or_doi` in one canonical form per source — a bare DOI, `arxiv:NNNN.NNNNN`,
  `semanticscholar:<hash>`, `uspto:<number>`, or a plain URL only where no identifier exists. Never
  a `doi:` prefix. **Four rows deliberately keep `semanticscholar.org/paper/...` URLs**
  (`S052`, `S062`, `S082`, `S093`) because the inventory carries those sources in the identical
  form; "normalising" them creates the failure it appears to fix. Idea `000147`.
- **A gate measuring "a source absent from the inventory" must resolve identifiers against
  `url_or_doi`, not the `source_id` slug column.** `LIT-01 G` picked the slug column and reported
  435 missing sources against a true figure of 0. A measurement that condemns substantially all of
  its input is suspect before it is reported.
- **Every search gets a ledger row, including a bibliographic-verification lookup.** Block C is
  categorical — "a search that logged nothing did not happen". An extraction dispatch was sent back
  for sixteen unlogged year-checks. The `strategy_phase` enum has no value for verification; they
  were filed under `D` with the mismatch noted. Idea `000149`.
- **Block C's "methodology" and Block X's "search protocol" are two different documents, and the
  second is never given a path.** The methodology is `research/literature-review/CLAUDE.md`; the
  search protocol, whose §6 inclusion and §7 exclusion criteria Block X means, is
  `research/protocols/literature_review_protocol.md`.
- **`check_no_private_content.py` verifies nothing in a worktree.** `_private/` is gitignored and
  absent there, so the tool builds an empty identifier list and prints `OK (… 0 identifiers
  checked)` with exit 0. Report its identifier count verbatim; never record a worktree run as a
  passing verification. The real check happens in the primary checkout. Idea `000150`.
- **Provider behaviour.** OpenAlex and Crossref APIs work directly. `export.arxiv.org` needs `-L`
  and is intermittent. `api.semanticscholar.org` returns HTTP 429 for most domains and 200 for some
  — attempt it and log what happens rather than assuming failure. A rate-limited attempt is a real
  zero-yield ledger row with its query, never an omission.
- **Mandated variants are matched literally.** A near-paraphrase fails: `dependence-aware data
  fusion` did not satisfy `dependence-aware fusion`, and two further gaps needed supplementary
  searches. Require that any supplementary search be a **real** search with real results — a row
  manufactured to satisfy a string match is worse than the uncovered variant it hides.
- **Duplicates are evidence, not noise.** Late-search duplicate rates are how the final gate
  demonstrates saturation rather than asserting it. Record recurrence in `duplicate_handling` and
  `dedup_of`; a duplicate silently dropped is evidence destroyed.
- **The `source_type` enum has no bucket for a patent.** Granted patents were filed as
  `tech report`. Idea `000148`. Do not edit the contract to make data fit.

## 5. Thesis discipline

The campaign works to support **H0: D-System is primarily a recombination of known ideas.** No agent
may mutate a hypothesis, rename a D-System concept, or rewrite scope to avoid a collision. A
hypothesis that looks wrong is a blocking finding for the owner, never an edit.

The inverse error is equally damaging and is live: a shared *name* is not a shared mechanism.
`phase-lit-01` found "evidence graph" independently coined by three traditions and "evidence
network" carrying three further senses. Counting those as collisions would inflate the apparent
prior art in exactly the direction that flatters H0. A campaign built to support H0 is most exposed
where the evidence looks most favourable. Pass 1 records; `phase-lit-04` adjudicates.

## 6. Stop at the phase boundary

Do not run past it into the next phase, however much budget seems left.

1. **Checkpoint** with the `checkpoint` skill — it records observed progress and never marks a phase
   complete.
2. **Write the session record** (`uv run python -m src.governance --next-code session`), naming what
   was dispatched, what each gate measured with real output, and every finding raised. It lives in
   the worktree, not the primary checkout.
3. **Report spend posture**: searches run, sources deep-read, any Opus escalation, wall-clock against
   the runway. The campaign's runway is seven sessions, range six to eight.
4. **State the resume state explicitly**: which phase is current, which work item is next, what a
   fresh session must read.
5. **Leave the tree clean and governance exiting 0.** Rebase onto `dev` at the boundary rather than
   merging it in.

**Do not mark the phase `complete`** — that is the owner's `/session-close`, after its own
independent review. **Do not integrate into `dev`** — that is the owner's call, at the points
`PLAN-023` names. Both are refusals to make even if the work plainly looks finished.

## 7. When something goes wrong

- **A gate fails:** record the real measurement and stop at the phase boundary. Verify the failure
  yourself before acting on it — `phase-lit-01`'s gate produced one real failure and one artifact of
  its own method, and they needed different responses.
- **A critical issue** — a collision that falsifies scope, a methodology defect invalidating
  collected evidence — gets `GOV-009`'s dual review first. The campaign pauses for the owner only if
  the issue survives that review unresolved.
- **A section conflicts with the domain matrix or the evidence contract on data:** those documents
  win; report the conflict as a finding.
- **The descope ladder:** no rung without the owner's explicit direction, except the stated exception
  `PROMPT-031` grants — rung 1 is the coordinator's to take if Pass 1 overruns, reported afterwards,
  and only with that rung's gate re-parameterization.
- **The single Opus escalation** is the coordinator's to spend on its own judgment where a
  judgment-heavy step genuinely needs it, and must be named in the session record — which work item,
  why, and what it changed. A second needs the owner.

## 8. State as of `phase-lit-01`'s close (2026-09-12)

Verify this rather than trusting it; it is a pointer, and it will age.

- `phase-lit-01` **complete**, integrated into `dev` on the owner's direction at that phase boundary
  — earlier than the pre-synthesis check-in `PLAN-023` schedules. The second scheduled integration
  therefore covers phases 02–06.
- Evidence on the trunk: 267 ledger rows (`LIT-01-S001`–`S267`), 438 inventory rows (427 candidate,
  11 excluded), 159 flagged `collision_candidate: yes`, 26 terminology-map sections. Domains D01–D20
  and D28–D32 swept, plus the cross-domain H4 set.
- **Next: `phase-lit-02`** — Pass 1b, D21–D27 and D33–D45. Twelve sections: `K`, five `S`/`X` pairs,
  then `G`. Its `search_id`s start at **`LIT-02-S001`**: the contract numbers them
  `LIT-<phase>-S<seq>`, monotonic *per phase*, so they do not continue from `LIT-01-S267`. Its `K`
  continues on `agent/lit-campaign` and verifies the ledger and inventory rather than recreating
  them.
- Deliverables `01`–`03` are built incrementally from here and are `phase-lit-03`'s to close.
- No Opus escalation has been spent. No descope rung has been taken. 1 of 7 sessions used.
