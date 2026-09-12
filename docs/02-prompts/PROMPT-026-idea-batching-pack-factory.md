---
schema_version: 1
id: doc-prompt-idea-batching-pack-factory
code: PROMPT-026
title: Idea-batching pack factory — investigate the repository and write the batching prompt pack
kind: prompt
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems: [sys-governance, sys-backlog, sys-portfolio]
depends_on: [doc-prompt-idea-batching-pre-plan-package, doc-prompt-pack-protocol, doc-idea-record-system]
---

# Idea-batching pack factory — investigate the repository and write the batching prompt pack

This is **Prompt B** of the prompt-pack protocol
([GOV-008](../08-governance/GOV-008-prompt-pack-protocol.md)) for the idea-batching build. Prompt A
is the pre-plan package ([PROMPT-025](PROMPT-025-idea-batching-pre-plan-package.md)), which carries
the owner's sixteen ratified decisions. Prompt A is the owner's input; this document is the machine
that turns it into artifacts.

Per `GOV-008` stage 3, this document is adversarially audited against Prompt A and repository
reality, and the owner signs off on the revised version, **before** it runs.

## Role and hard scope limits

You are the pack factory. You investigate the repository and write documents. That is the whole job.

**You must not:**

- read, group, classify or partition any idea — the analysts do that, in the build session;
- dispatch any agent, for any reason;
- write the batching staging document, or any part of it;
- write implementation code beyond the corpus builder named below, which is a pack artifact;
- re-ask any of Prompt A's sixteen ratified decisions;
- edit `AGENTS.md` or `CLAUDE.md`;
- claim a backlog phase, or touch a peer's claimed systems or fenced paths.

**Scope note carried from Prompt A:** this build is documents-only. The pack must **not** contain
worktree setup, port assignments, browser verification or schema-drift gates. Say so explicitly in
the delegation pack so a reader understands their absence is scoping, not oversight.

## Preflight

Run these before writing anything, and record the real output:

```bash
uv run python -m src.governance --inventory     # must exit 0
uv run python -m src.governance --ready         # active claims and locked systems
uv run pytest                                   # must be green before and after
git status --short                              # clean checkout expected
```

Then confirm:

- `PROMPT-025` exists and the owner has signed it off. It is on branch
  `agent/idea-batching-planning` if it has not yet been integrated; if it is unmerged **and**
  unapproved, stop and say so rather than building on an unratified Prompt A.
- No peer claim covers `sys-governance`, `sys-backlog` or `sys-portfolio` in a way this pack's
  files would collide with. Check the budget **numerically** — the conflicts column says nothing
  about `max_active`.
- `docs/08-governance/catalog.md` matches `uv run python -m src.governance --catalog`. CI fails on
  any difference, so regenerate it after every document you add and commit it alongside.

A failing check is a result to record, not a step to retry until it goes quiet.

## The artifacts to produce, in order

The owner ratified a **light artifact set** on 2026-09-12: no requirement, no plan, no backlog
phase, no decision record. `GOV-008` stage 4's requirement-and-plan machinery exists to govern code
builds; this build writes no code and its deliverable is one ungoverned staging document. The
tension that makes this reasonable is recorded as `000145` (alternative planning methodologies
below a full prompt pack); do not attempt to resolve it here.

Take every code from `uv run python -m src.governance --next-code prompt` at the moment you create
the document — never guess a code, and never reuse one you saw earlier in the session. **No code is
predicted here on purpose.** Peers allocate prompt codes concurrently: `PROMPT-027` was taken by
another session's literature-review package while this document was being drafted, which is exactly
why a code read at drafting time is worthless by the time you write.

### 1. The delegation pack

A governed prompt document holding every prompt the build session dispatches verbatim, one section
at a time. Nothing is authored mid-build: if this document does not contain it, the build session
does not send it.

Required sections. The precedents (`PROMPT-018`, `PROMPT-021`) fix `K` for kickoff, `C*`/`V*` for
creator/validator pairs, `G` for the phase gate and `A` for adversarial review. This build has no
creators and no validators — it has replicate analysts and two adversarial audits — so `C*`/`V*`
go unused and the replicates take `R*`. **`A` keeps its established meaning: adversarial review.**
Do not repurpose `V*` for the audits; a reader arriving from the precedents would read the letters
backwards.

**`K` — kickoff.** Preflight, the corpus build, the dispatch order, and the gate schedule from
Prompt A's decision 12 (pause when the four analyst reports land; pause when audit 1 returns; pause
when audit 2 has checked the merge).

**`R1`–`R4` — the four analyst prompts.** Each idempotent and dispatchable verbatim. Every one
carries:

- the partition criterion from decision 9, **quoted verbatim and unaltered** — it is the
  specification, and paraphrasing it is the single most damaging thing this pack could do;
- the two-level structure from decision 10: partition by the criterion alone first, however many
  groups that yields, then roll those into 8–12 named programmes with the fine partition visible
  underneath as each programme's members;
- the batch record contract from decision 15 — name, member ids, cohesion, independence argument,
  preceding batches, rough size — with independence argued in detail only against
  plausibly-overlapping batches (shared system, shared path, shared dependency, or an idea that
  nearly went either way) and asserted in one line against the rest;
- the completeness obligation: account for every idea in the corpus, none unassigned, none in two
  groups, and state the residual explicitly;
- the unbatched section from decision 8: ideas with no confident home are named with a reason each,
  never forced into a best-fit batch and never swept into a catch-all;
- the decline-candidate section from decision 11 — a required section, not an optional aside, with
  a reason per nomination and an explicit instruction that **nothing is written to the idea log**;
- an instruction to work alone: no analyst sees another's output, and none may dispatch subagents.

The four prompts differ in **exactly two** respects and no others:

| Analyst | Triage findings | Presentation order |
|---|---|---|
| `R1` | included | id ascending |
| `R2` | included | id descending |
| `R3` | included | shuffled, seed recorded |
| `R4` | **withheld** | id ascending |

`R4` is the control. Do not tell it that it is a control, that findings exist, or that other
analysts are running — a control that knows it is a control is not one.

**`A1` — adversarial audit 1, the four partitions.** The adversary over all four reports: does each partition
actually cover the corpus (verify the count arithmetically, do not trust the analyst's claim); are
the groups genuinely independent under decision 9; and the convergence check — *did the four agree
for the right reasons, or did they inherit the same framing from the prompt?* State plainly that a
3–1 split with `R4` dissenting is the **expected shape of finding bias**, not a settled vote.

Then require the audit to weigh the competing explanation, because the control is confounded and
the pack must say so rather than pretend otherwise. `R4` differs from `R1` in exactly one variable,
which is a clean design — but any divergence has **two** explanations, and they are not
distinguishable from the split alone:

- `R1`–`R3` inherited the triage charter's framing, and `R4` did not; or
- `R4` simply had less evidence and produced a weaker partition.

The brief must force the audit to argue which explanation fits **each specific divergence**, citing
the ideas involved, and to say plainly when it cannot tell. Without this the audit can rubber-stamp
any 3–1 split as bias-validated-by-design, which would make the control worse than useless: it
would launder a quality artifact as a finding.

The audit must also report whether the presentation-order manipulation did anything at all — did
`R1`, `R2` and `R3` differ in ways that track their ordering, or did order make no observable
difference? Order-sensitivity in a whole-corpus read is plausible but unverified for these agents,
and the pack spends real budget on it. If the manipulation has no effect, that is a finding worth
having: it means a future sweep can drop the variation and run cheaper.

**`S` — synthesis.** Not a dispatch: the protocol the integrator follows in the main session.
Covers how a disagreement about independence is resolved (check the repository and rule — never
count analysts, never split the difference, never defer to an analyst because it read more), how
the three decline tiers are assembled (nominated by all four / by a majority / by a single
analyst, each carrying its reasons), and how the two levels are reconciled when analysts disagree
about which level a boundary belongs to.

**`A2` — adversarial audit 2, the merge.** The adversary again, after synthesis: does the integrated partition
follow from the four inputs, or did the integrator introduce groupings no analyst proposed? This
audit exists because synthesis is where the most judgment is applied and was otherwise unchecked.
Give it the four reports, the merge, and audit 1's findings.

**`G` — the gate.** What must be true before the staging document reaches the owner: every idea
accounted for, the programme count inside 8–12 or justified, audit 2 returned, the decline tiers
assembled, governance exits 0.

**Descope ladder**, in decision 16's order: third finding-reader (`R3`), then second (`R2`), then
audit 2 (`A2`), then audit 1 (`A1`), with the control (`R4`) surrendered last. Flag that the
ladder's placement of `A2` is the drafter's proposal, not the owner's ruling. No rung is taken
without the owner's explicit direction.

### 2. The adversary charter (`.claude/agents/`)

A committed charter for a **general partition adversary** — able to audit any proposed partition,
whether of ideas, backlog phases or plan boundaries, so the role outlives this sweep. One charter
serves both audits; the briefs differ and live in the delegation pack.

Follow the conventions of the existing charters in `.claude/agents/` — read two of them before
writing. Read-and-run only: it changes no repository file and spawns no subagents. Model per
`GOV-008`'s cost protocol: Sonnet, as judgment work.

The four analysts need **no** charter. They are general-purpose agents running the delegation
pack's prompts.

### 3. The corpus builder (a tool)

The one piece of code this pack contains, because four of Prompt A's decisions are inert without
it. It assembles each analyst's input and must:

- read idea state through `fold()` in `src/db/ideas.py` — **never** the raw JSONL;
- select `triaged` ideas only, excluding `promoted` and `discarded`;
- subtract every id in the demo fast lane's exclusion file (see below);
- emit title, body and links always; include or withhold **findings** per analyst, where "findings"
  means **every annotation with `kind == "finding"`, any author, in chronological order** — not
  only `agent-idea-triage`'s. `fold()` returns `annotations` as a flat, unfiltered list mixing
  `note`, `finding` and `assessment` kinds from any author, so the builder must filter by kind
  rather than assume a single field exists. Seven findings in the current corpus were written by
  other authors (`agent-demo-factory`, `agent-workbench-planner`, `agent-coordinator`,
  `agent-workbench-coordinator`, `agent-readme-audit`, and the owner directly) and all of them
  count;
- **flag the ideas carrying more than one finding**, so an analyst knows the evidence there is
  layered and may be internally contradictory rather than a single settled account. Eight triaged
  ideas qualify as of 2026-09-12 — `000014`, `000070`, `000071`, `000077`, `000087`, `000091`,
  `000099`, `000107` — but the builder computes the set rather than hard-coding it, since the log
  is append-only and the set grows;
- emit the three presentation orders, recording the shuffle seed so a run is reproducible;
- report the resulting corpus size, so the build session knows what the analysts actually received
  rather than assuming 135.

Decide its location and name by the conventions in `tools/`. **Every tool under `tools/` requires a
paired `OPS-*` document — there is no exception.** `test/test_tool_docs.py` asserts it
(`test_every_existing_tool_is_paired_with_a_document`), and a second test
(`test_every_paired_document_matches_regenerated_output`) asserts the document matches what
`tools/generate_tool_docs.py` regenerates from the tool's own docstring and argparse definitions.
Write the tool, generate its document, and run `uv run pytest` before calling the artifact done —
governance exiting 0 does not cover this, and the suite goes red if either test is unsatisfied.

**The exclusion file does not exist yet.** The demo fast lane has not run. Specify its path under
`docs/00-working/`, its key names, and its disposition values (queued as a phase / fixed directly /
dropped) — then have the builder treat a missing file as an empty exclusion set rather than an
error, so the pack is runnable before the fast lane finishes. Record that an excluded idea the fast
lane does not ship returns to the corpus, which is why the file records disposition rather than
bare membership.

### 4. The kick-off record

`GOV-008` stages 6 and 7 collapse into this document per decision 13 — no separate coordinator
prompt is written. It carries:

- the pinned starting state: queue state, peer claims, the corpus size, the deadline context;
- the owner's per-build ratified deltas, and the precedence rule that where this record and the
  delegation pack differ, **this record wins**;
- the gate schedule from decision 12;
- the kick-off paragraph as its final section — the single paragraph the owner pastes into a fresh
  terminal. Deliver a copy in chat; the durable copy lives here.

## The open-questions protocol

**Prompt A's open-questions list is empty by construction.** All sixteen decisions were ratified by
the owner on 2026-09-12 across five `AskUserQuestion` batches. Do not re-ask any of them, and do
not reopen them because a repository fact seems to argue the other way — surface the fact and let
the owner decide.

If drafting genuinely exposes something new — a convention that makes a ratified decision
unimplementable as written, a tool that does not exist where Prompt A assumed it does — **ask
through the `AskUserQuestion` tool**, batched, at the point it matters. Never in prose: a question
in a closing paragraph does not reliably get answered, and the owner has made this a standing rule
(`brain/procedures/ask-through-the-tool.md`). One question is enough for a tool call.

## Standing constraints

`AGENTS.md` governs. Every governed document takes its code from `--next-code` at creation.
`AGENTS.md` and `CLAUDE.md` are never edited. Integration into `dev` is the owner's call each time;
pushing your own branch is not. Never write a confidential identifier into a tracked file. New asks
the owner raises mid-session are captured as ideas immediately through `tools/append_idea.py`, one
per distinct ask, with the id taken from the writer's own output — never guessed.

Regenerate `docs/08-governance/catalog.md` after adding documents and commit it in the same change;
it is generated, and CI fails on any difference.

## Stop condition

Stop when all four artifacts exist — delegation pack, adversary charter, corpus builder, kick-off
record — `uv run python -m src.governance --inventory` exits 0, **`uv run pytest` is green**, the
catalog is in sync, and the owner has a review summary naming what the pack contains, what it
deliberately omits and why, and the dispatch order the build session will follow.

Do not start the build. The pack is audited (`GOV-008` stage 5) and the owner approves it before
any analyst is dispatched.

---

## The prompt

> You are the pack factory for the D-System idea-batching build. Read `AGENTS.md`, then
> `docs/08-governance/GOV-006-conversation-guidelines.md`, then
> `docs/08-governance/GOV-008-prompt-pack-protocol.md`, then
> `docs/02-prompts/PROMPT-025-idea-batching-pre-plan-package.md` — the owner's sixteen ratified
> decisions — and then this document
> (`docs/02-prompts/PROMPT-026-idea-batching-pack-factory.md`) in full.
>
> **Work in plan mode first.** `GOV-008` stage 4 — which is what executing this document is —
> requires the pack be planned before it is written, with auto execution only after the owner
> confirms the plan. Run the preflight, record the real output, present the plan, and wait.
>
> Once the owner confirms, produce the four artifacts in the order given: the delegation pack, the
> adversary charter, the corpus builder, and the kick-off record.
>
> You write documents and investigate the repository. You do **not** read or group ideas, dispatch
> agents, write the staging document, or re-ask any ratified decision. If drafting exposes
> something genuinely new, ask through the `AskUserQuestion` tool — never in prose.
>
> Stop when the four artifacts exist, governance exits 0, the catalog is in sync, and the owner has
> the review summary. The pack is audited and approved before any analyst is dispatched.
