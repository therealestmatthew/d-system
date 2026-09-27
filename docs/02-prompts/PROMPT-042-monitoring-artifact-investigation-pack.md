---
schema_version: 1
id: doc-prompt-monitoring-artifact-investigation-pack
code: PROMPT-042
title: Monitoring artifact investigation pack
kind: prompt
status: active
owner: repository-owner
created: '2026-09-27'
updated: '2026-09-27'
systems: [sys-gov-docs, sys-backlog, sys-html]
depends_on: [doc-prompt-pack-protocol, doc-idea-staging, doc-multi-session-coordination-protocol, doc-html-generation-design-system, doc-batch-orchestration-protocol]
---

# Monitoring artifact investigation pack

The prompts one execution session sends to investigate idea `000497` (a monitoring artifact: one
place the owner can reference everything they need to know about the repository's state) and the
artifact ideas the owner put in scope with it: `000491` (a running list of active HTML artifacts),
`000492` (a reference artifact for each major area, the batch anchor), `000493` (an artifact that
tracks every artifact, and its maintenance protocol), `000494` (an agent that tracks artifacts,
protocols, governance and documents) and `000495` (an agent that tracks paths and finds things).

The pack investigates and synthesizes. It builds nothing: no generator, no page, no agent file, no
governed requirement or plan. It ends at the owner's ruling on a design brief.

**Tests never run in the primary checkout** (`/code/d-system`). Every `pytest`, rebuild, `ruff`,
`mypy` and governance run in this pack happens in the session's own worktree. `test/test_codes.py`
overwrites the tracked `catalog.md` while it runs, so a test run in the primary checkout breaks
every peer's view of `dev`.

## Where this pack sits in the owner's process

The owner's process for `000497`, in their words: make the idea, triage it immediately, "then
prompt plan it, then adversarially review it. Then expand, then iterate until it is a highly
functional and useful monitoring system that I can reference everything I need to know in one
place. Need to have agents investigate what is missing, figure out the best way to display the info
and so on." The reason they gave: "Things are evolving so rapidly that I am struggling to keep up."

| Stage | Where it happens |
|---|---|
| Idea and triage | Done: `000497` is triaged, with the owner's scope addition recorded on it |
| Prompt plan | This document |
| Adversarial review of the prompt plan | Before this document merged; see *Review of this pack* at the end |
| Investigate what is missing, how to derive it, how to display it | This pack, sections `S0`, `I1`–`I5` |
| Synthesis, with a build priority across the batch | This pack, section `S` |
| Adversarial audit of the synthesis, several facets | This pack, sections `A1`–`A3` |
| Expand into requirement, plan and backlog phases | **Not this pack.** A later planning session, from the brief this pack produces |
| Build and iterate | **Not this pack** |

The owner ruled on 2026-09-27 that this pack stops at the synthesis, that the audit uses several
agents on different facets, that the artifact batch (`000491`–`000495`) is fully in scope — as
inputs and for deciding what to build first — and that coordination data held only by the Session
Manager is read as a source and reported as a gap.

## What the owner wants tracked

This is the checklist every investigator and every auditor works against. It is the owner's list as
recorded on `000497`, split into items so coverage can be checked one by one. The owner said "not
limited to" and "maybe more": an investigator may propose an item not on the list, but must label
it as a proposal, never merge it into the list.

| Item | What the owner named |
|---|---|
| `O1` | The state of ideas in the fold, including triaged-versus-open metrics |
| `O2` | The idea priority queue |
| `O3` | Active plans |
| `O4` | Active phases |
| `O5` | Active batches |
| `O6` | The backlog |
| `O7` | `next_up` |
| `O8` | Other plans (not active) |
| `O9` | Plan metrics |
| `O10` | Governance documents |
| `O11` | Branches and worktrees, and their statuses |
| `O12` | Mappings from branches and worktrees to plans, phases, batches and unclaimed work |
| `O13` | Systems |
| `O14` | Artifacts: the active HTML artifacts, static and live (`000491`); every artifact and how it is maintained (`000493`); a reference artifact per major area (`000492`) |

`O14` comes from the batch, not from `000497` itself. `000494` and `000495` are agents rather than
things to display; they enter through `I5` and the build priority.

## What this pack carries, and what it does not

The work is an analysis. One coordinator session takes a snapshot, dispatches five read-only
investigators in parallel, holds an owner gate, writes a synthesis, dispatches three read-only
auditors in parallel, fixes what they find, and holds a second owner gate.

It carries no build dispatches, no creator or validator roles, no port assignments and no browser
verification. Their absence is scoping. The investigators and auditors are subagents of the
coordinator, not sessions, and none of them writes a file, so none needs its own worktree.

Nothing this pack dispatches writes to the idea log: no status event, no annotation, no link. When
the coordinator or an agent comes across a new idea, the coordinator sends it to the Ideation
session as `IDEA <the bare idea>` with its session name, per the coordination contract (`GOV-017`).
The coordinator never records it itself.

## Session mechanics (do these first)

This is owner-directed work with no backlog phase. There is nothing to claim. Say so in the first
report: the session runs unclaimed and peers hold no lock against it.

1. Send `ACK` to the Session Manager if you have not, and wait for the assignment of this pack.
2. From the primary checkout, create the worktree — this is the only primary-checkout action this
   pack takes:

   ```bash
   git -C /code/d-system worktree add -b agent/monitoring-investigation \
     /code/d-system-worktrees/monitoring-investigation dev
   cd /code/d-system-worktrees/monitoring-investigation
   uv venv && uv sync --extra dev
   ```

3. Every path in every dispatch is absolute. `{WT}` below means
   `/code/d-system-worktrees/monitoring-investigation`. Replace it before sending; replace nothing
   else.
4. Outputs:

   | Path | Tracked | Holds |
   |---|---|---|
   | `{WT}/_working/monitoring-artifact/snapshot/` | No (gitignored) | `S0`'s captured state, including copies of the Session Manager's reports |
   | `{WT}/docs/00-working/monitoring-artifact/` | Yes (ungoverned, `ADR-010`) | Investigator reports, the gate log, the design brief, the audit reports |

   The snapshot stays gitignored because it copies the Session Manager's gitignored reports.
   Everything the owner or a later session must read is under `docs/00-working/`, because
   gitignored content does not survive a merge or `git worktree remove`.

5. Owner questions go through `AskUserQuestion`, in batches, at the point the work reaches them.
   The owner is often on mobile, where option previews do not render: put every draft and every
   piece of content in the message text, never in a preview.

## Section letters

| Letter | Meaning here |
|---|---|
| `S0` | The snapshot (coordinator procedure, not a dispatch) |
| `I1`–`I5` | The five investigators |
| `G1` | Owner gate after the investigation |
| `S` | The synthesis (coordinator procedure) |
| `A1`–`A3` | The three auditors, one facet each |
| `G2` | Owner gate on the audited brief |

## Conventions

- **Idempotency.** Every dispatch opens with *"Assess the current state of the repository against
  the deliverables below; do only what is missing; report what already existed."* A dispatch can
  be re-sent in a later session without harm.
- **Truncation.** If an agent's output is cut off by its turn limit, resume that same agent. Never
  re-run it from scratch.
- **Agent types.** Investigators dispatch on `partition-analyst`: read-only, no command execution,
  returns its report as its final message, and the coordinator writes that message to the file
  named in the dispatch, unchanged. Auditors dispatch on `partition-adversary`: read-only, ranks
  findings blocker, major and minor. Neither is `general-purpose`. Both charters are written for
  partitions; each dispatch below carries everything specific to this work, as `PROMPT-038` does.
- **Model.** Sonnet for every dispatch (`GOV-008`'s cost policy). Opus is not pre-assigned.
- **Why a snapshot.** `partition-analyst` cannot run commands. `S0` runs every command once and saves
  the output, so all five investigators read the same state and cite the same files.
- **Idea state comes from `fold()` only.** No agent reads `_data/ideas.jsonl` directly. `S0` saves
  the folded state; investigators read that file.
- **No agent sees another investigator's report** before `G1`. Auditors see the reports and the
  brief.
- **Evidence.** Every claim about the repository cites a file and line, or a snapshot file.
  A claim that cannot be cited is labelled `unverified`.

## Owner gates

| Gate | After | The owner reads | The owner rules on |
|---|---|---|---|
| `G1` | `I1`–`I5` have returned | A summary of at most one screen per report, in the message text, with the report paths | Corrections to scope, anything an investigator flagged as needing the owner, and whether to proceed to `S` |
| `G2` | `A1`–`A3` have returned and the coordinator has fixed or answered every finding | The brief's summary and build priority, and each audit finding with its disposition | Accept the brief, correct it, or send it back. Acceptance ends the pack |

The coordinator records each question and ruling in
`{WT}/docs/00-working/monitoring-artifact/gate-log.md`, dated, with the owner's words as given.
The coordinator never skips a gate, and never descopes on its own; see *Descope ladder*.

---

### S0 — the snapshot

A coordinator procedure. Run each command in the worktree and save its output under
`{WT}/_working/monitoring-artifact/snapshot/` with the file name shown. None of these commands writes
to a tracked file. **Do not run `--catalog`**: it rewrites `catalog.md`. Read the committed catalog
instead.

| File | Command or source |
|---|---|
| `meta.txt` | `date -Iseconds`, `git -C /code/d-system rev-parse dev`, `git rev-parse HEAD` |
| `ideas-fold.json` | `uv run python -c "import json; from src.db.ideas import fold, load_events; print(json.dumps(fold(load_events()), indent=1, default=str))"` |
| `ready.txt` | `uv run python -m src.governance --ready` |
| `backlog.txt` | `uv run python -m src.governance --backlog` |
| `inventory.txt` | `uv run python -m src.governance --inventory` |
| `worktrees.txt` | `git -C /code/d-system worktree list --porcelain` |
| `branches.txt` | `git -C /code/d-system branch -a -vv` |
| `ahead-behind.txt` | For each local `agent/*` branch: the branch name, `git -C /code/d-system rev-list --left-right --count dev...<branch>`, and the date of its last commit |
| `dev-log.txt` | `git -C /code/d-system log --oneline -40 dev` |
| `session-manager/` | A copy of `/code/d-system/_working/session-manager/reports/` (read only; never write there) |
| `artifacts.txt` | The owner's published claude.ai Artifacts: title, URL, last updated, from the `Artifact` tool's `list` action. If the tool is not available in this session, write that sentence and nothing else |

Then commit nothing yet and dispatch `I1`–`I5` in parallel, in one message.

---

### I1 — existing surfaces and artifacts

Dispatch on `partition-analyst`, model sonnet.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

You are investigating what already shows the owner the state of this repository, for idea
000497 (a monitoring artifact: one place to reference everything about the repository's state).
The repository is at {WT}. A snapshot of commands run at one moment is in
{WT}/_working/monitoring-artifact/snapshot/; read meta.txt first for when and at which commit.
You are read-only. Return your whole report as your final message; the dispatcher writes it to
{WT}/docs/00-working/monitoring-artifact/I1-existing-surfaces.md.

Read the owner's checklist in {WT}/docs/02-prompts/PROMPT-042-monitoring-artifact-investigation-pack.md,
section "What the owner wants tracked" (items O1-O14). Read idea state only from
snapshot/ideas-fold.json, never from _data/ideas.jsonl. Ideas to read there: 000497, 000491,
000492, 000493, 000300, 000301, 000042, 000106.

Find every surface that shows repository state today. At least: {WT}/_public/ (every file, including
_public/overview/index.html), {WT}/docs/00-working/ideas.md, the governance reports in
snapshot/ready.txt, backlog.txt and inventory.txt, {WT}/docs/08-governance/catalog.md, the
workbench explorers under {WT}/ts/, the generators in {WT}/tools/ (generate_overview.py,
overview_metrics.py, overview_inventory.py, generate_ideas_md.py and any other), the Session
Manager's reports in snapshot/session-manager/, and the published Artifacts in snapshot/artifacts.txt.
Search for others; do not stop at this list.

For each surface report: its path; which O-items it covers, fully or partly; how it is produced
(generator, command, by hand); how it is refreshed and how stale it is at snapshot time, with the
evidence; whether a test catches drift; who it is written for. Then answer: which O-items no
surface covers; which items are covered by more than one surface and whether they agree; and, for
000491 and 000493, which of these surfaces are HTML artifacts, which are static and which are
live, and what keeps each in sync today, if anything.

Cite a file and line, or a snapshot file, for every claim. Label anything you could not verify
"unverified". Do not propose a design; that is another investigator's work. End with a section
"For the owner" listing anything only the owner can settle, and a section "Ideas outside this
brief", one line each.
```

---

### I2 — data sources and how to derive each metric

Dispatch on `partition-analyst`, model sonnet.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

You are investigating where the data for a repository monitoring artifact (idea 000497) comes
from, and how each number or list on it would be derived. The repository is at {WT}. A snapshot is
in {WT}/_working/monitoring-artifact/snapshot/; read meta.txt first. You are read-only. Return your
whole report as your final message; the dispatcher writes it to
{WT}/docs/00-working/monitoring-artifact/I2-data-sources.md.

Read the owner's checklist in {WT}/docs/02-prompts/PROMPT-042-monitoring-artifact-investigation-pack.md,
section "What the owner wants tracked". Your items are O1-O10 and O13. Read idea state only from
snapshot/ideas-fold.json, never from _data/ideas.jsonl; read {WT}/src/db/ideas.py to understand
what fold() returns.

Sources to examine, at least: {WT}/src/db/ideas.py; {WT}/docs/00-working/ideas-priority.yaml;
{WT}/docs/09-backlog/backlog.yaml (next_up, max_active, phase status and agent fields);
{WT}/docs/09-backlog/batches/ and its README; {WT}/docs/08-governance/GOV-016-batch-orchestration-protocol.md;
{WT}/docs/08-governance/catalog.md; {WT}/docs/08-governance/systems.yaml; the governance module
under {WT}/src/governance/ (what --ready, --backlog and --inventory compute, and which functions a
generator could call); {WT}/tools/overview_metrics.py and {WT}/tools/generate_ideas_md.py.

For each item O1-O10 and O13, report: the source file or files; the exact derivation (fields read,
filters, counts), with a worked value computed from the snapshot where you can compute it by
reading; existing code that already computes it, with file and function; what "active" means for
that item and where that definition lives; and traps — for example the priority queue drifting
from the idea log, a batch table that holds no phase facts, a plan whose status and whose phases
disagree. For O9, say which plan metrics already exist anywhere and which would be new, and do
not invent metrics the owner did not ask for without labelling them as proposals.

Cite a file and line, or a snapshot file, for every claim. Label anything you could not verify
"unverified". End with "For the owner" and "Ideas outside this brief", one line each.
```

---

### I3 — branches, worktrees, sessions and coordination state

Dispatch on `partition-analyst`, model sonnet.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

You are investigating how a repository monitoring artifact (idea 000497) would show branches,
worktrees, their statuses, and what each maps to. The repository is at {WT}. A snapshot is in
{WT}/_working/monitoring-artifact/snapshot/; read meta.txt first. You are read-only. Return your
whole report as your final message; the dispatcher writes it to
{WT}/docs/00-working/monitoring-artifact/I3-branches-and-coordination.md.

Read the owner's checklist in {WT}/docs/02-prompts/PROMPT-042-monitoring-artifact-investigation-pack.md,
section "What the owner wants tracked". Your items are O11 and O12. Read idea state only from
snapshot/ideas-fold.json. Ideas to read there: 000368, 000369, 000391, 000448, 000435, 000434.

Sources, at least: snapshot/worktrees.txt, branches.txt, ahead-behind.txt, dev-log.txt,
ready.txt; the agent and status fields in {WT}/docs/09-backlog/backlog.yaml; the batch tables in
{WT}/docs/09-backlog/batches/; {WT}/_tmpagent/claims.jsonl; the Session Manager's reports copied
into snapshot/session-manager/; the naming rules in {WT}/AGENTS.md (branch agent/<phase-id>,
worktree ../d-system-worktrees/<phase-id>, agent/<slug> for unclaimed work) and
{WT}/docs/08-governance/GOV-017-multi-session-coordination-protocol.md.

Report: for every worktree and every agent/* branch in the snapshot, what it maps to (a phase, a
batch, unclaimed owner-directed work, or nothing you can determine) and from which evidence;
which statuses can be derived from git and the tracked files alone (for example ahead of dev,
behind dev, merged, stale, detached, phase status) and how; and which facts exist only in the
Session Manager's board or reports — session roster, assignments, grants, queue, unclaimed
work, which session holds which branch. For each of those, say that it is not recorded durably,
where it lives today, and which of the ideas above would record it. The owner ruled that this
data is used as a source and reported as a gap; do both.

Cite a file and line, or a snapshot file, for every claim. Label anything you could not verify
"unverified". End with "For the owner" and "Ideas outside this brief", one line each.
```

---

### I4 — display, freshness and upkeep

Dispatch on `partition-analyst`, model sonnet.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

You are investigating the best way to present a repository monitoring artifact (idea 000497) and
keep it current. The owner wants "one place" to "reference everything I need to know", because
"things are evolving so rapidly that I am struggling to keep up". The owner often works from a
phone through Remote Control. The repository is at {WT}. A snapshot is in
{WT}/_working/monitoring-artifact/snapshot/; read meta.txt first. You are read-only. Return your
whole report as your final message; the dispatcher writes it to
{WT}/docs/00-working/monitoring-artifact/I4-display-and-freshness.md.

Read the owner's checklist in {WT}/docs/02-prompts/PROMPT-042-monitoring-artifact-investigation-pack.md,
section "What the owner wants tracked" (O1-O14). Read idea state only from
snapshot/ideas-fold.json. Ideas to read there: 000497, 000491, 000493, 000300, 000301, 000042,
000010, 000106, 000448.

Material to examine, at least: the existing pages in {WT}/_public/ and _public/overview/; the
Session Manager's hand-built status page in snapshot/session-manager/round-status.html; the
published Artifacts in snapshot/artifacts.txt; {WT}/docs/01-plans/PLAN-036-html-generation-design-system.md
and the template families under {WT}/templates/; {WT}/docs/01-plans/PLAN-021-live-demo.md and the
overview generator {WT}/tools/generate_overview.py; the workbench viewer and explorers under
{WT}/ts/; the phase that rules on 000042 (search {WT}/docs/09-backlog/backlog.yaml for
phase-idg-08) and its status.

Report: the display options that are realistic here — at least a generated HTML page in the
repository, a published claude.ai Artifact, a workbench panel, and a terminal report — and for
each: whether it can be read on a phone, how it gets refreshed (on demand, on commit, on a
schedule, by an agent), what breaks when it goes stale and whether staleness is visible, what
already exists to build it from, and its cost to keep in sync. Then describe, in text, how the
O-items could be arranged so the owner sees what changed and what needs them first. Say how the
answer to phase-idg-08's ruling on 000042 bears on this. Do not write HTML or mock-ups.

Cite a file and line, or a snapshot file, for every claim. Label anything you could not verify
"unverified". End with "For the owner" and "Ideas outside this brief", one line each.
```

---

### I5 — the artifact batch and what to build first

Dispatch on `partition-analyst`, model sonnet.

```
Assess the current state of the repository against the deliverables below; do only what is
missing; report what already existed.

You are investigating a batch of related ideas the owner wants built toward one goal: a monitoring
artifact they can reference for everything about the repository's state (000497), plus a running
list of active HTML artifacts (000491), a reference artifact per major area of the repository
(000492, the batch anchor), an artifact tracking every artifact and the protocol for maintaining
them (000493), an agent tracking artifacts, protocols, governance and documents (000494), and an
agent tracking paths and finding things (000495). The owner ruled these are in scope "first as
inputs but also to prioritize what we need to build to achieve what we want". The repository is
at {WT}. A snapshot is in {WT}/_working/monitoring-artifact/snapshot/; read meta.txt first. You are
read-only. Return your whole report as your final message; the dispatcher writes it to
{WT}/docs/00-working/monitoring-artifact/I5-batch-and-priority.md.

Read idea state only from snapshot/ideas-fold.json. Read every idea named above and every idea
they link to, plus 000300, 000301, 000042, 000010, 000448, 000368, 000369 and 000391. Read the
agent definitions in {WT}/.claude/agents/ and the skills in {WT}/.claude/skills/, and search
{WT}/docs/ for existing reference documents on the areas 000492 names (governance docs, the Idea
Realization Engine, the workbench, the HTML generator, the personal productivity system, protocol
docs, the boundary study, the plan and build audit procedures, the planning procedure, the idea
subsystems, the literature review protocol).

Report: for each idea in the batch, what it needs, what already exists toward it (with paths),
and which other ideas in the batch it depends on or duplicates; whether 000494 and 000495 overlap
existing agent types or skills; which open phases or plans already cover part of any of them; and
a dependency order. Then propose a build priority: the smallest first piece that would most
reduce the owner's difficulty keeping up, and the order after it, with the reason for each step.
Label the priority as a proposal; the synthesis and the owner decide it.

Cite a file and line, or a snapshot file, for every claim. Label anything you could not verify
"unverified". End with "For the owner" and "Ideas outside this brief", one line each.
```

---

### G1 — owner gate on the investigation

Write each report to its path exactly as returned. Then send the owner, in the message text, one
screen per report at most: what it found, what it flagged for the owner, and its path. Ask the
flagged questions with `AskUserQuestion`. Record questions and rulings in `gate-log.md`. Relay
each "Ideas outside this brief" line to Ideation as `IDEA ...`. Commit the reports and the gate log
on the branch. Proceed to `S` only on the owner's go.

---

### S — the synthesis

A coordinator procedure. Write `{WT}/docs/00-working/monitoring-artifact/design-brief.md` from the
five reports and the `G1` rulings only. The brief has these sections, in this order:

1. **Summary** — at most ten lines, readable on a phone.
2. **Coverage** — one row per O-item (and per proposed item, labelled as a proposal): source,
   derivation, existing code to reuse, and status: `available`, `derivable`, `not recorded
   durably`, or `missing`. Every row cites the report it came from.
3. **Display and freshness** — the recommended presentation and refresh model, the alternatives
   considered and why they lost, and how staleness is shown to the owner.
4. **Coordination data** — what is shown from the Session Manager's reports, marked as not
   durable, and which ideas (`000368`, `000369`, `000391`) would make it durable.
5. **Build priority** — the ordered list of pieces across `000497` and `000491`–`000495`, the
   first slice named explicitly, each step with its dependencies and the reason for its place.
6. **Open questions** — what only the owner can settle, one line each.
7. **Inputs for the next stage** — what the planning session that expands this into a requirement,
   a plan and backlog phases will need. Write no requirement or plan here.

The brief makes no claim the reports do not support. Where two reports disagree, it says so and
names the one it follows and why. Commit it, then dispatch `A1`–`A3` in parallel, in one message.

---

### A1–A3 — the audit, three facets

Each dispatches on `partition-adversary`, model sonnet, with the common text below followed by its
facet paragraph. Write each reply unchanged to
`{WT}/docs/00-working/monitoring-artifact/A<n>-<facet>.md`.

Common text:

```
You are an adversary auditing a design brief for a repository monitoring artifact (idea 000497)
and the artifact ideas batched with it (000491-000495). The repository is at {WT}. If any path
given to you is relative, stop and report it.

Read {WT}/docs/02-prompts/PROMPT-042-monitoring-artifact-investigation-pack.md (the owner's
checklist O1-O14 and the rulings), {WT}/docs/00-working/monitoring-artifact/design-brief.md, the
five reports I1-I5 and gate-log.md in the same directory. The snapshot the reports cite is in
{WT}/_working/monitoring-artifact/snapshot/. Read idea state only from snapshot/ideas-fold.json.

Assume the brief is wrong and find where it fails, within your facet below. You are read-only. Do
not edit, create or delete any file, do not write the idea log by any route, and do not dispatch
subagents. Do not approve the brief; approval is the owner's. Do not write the fix; you may name
the smallest change that would resolve a finding.

Check before you claim. Each finding needs evidence: the file and line you quoted, or the
snapshot file. Do not accept the brief's or a report's statement about the repository as
evidence; check it. Style preferences are not findings.

Return findings ranked blocker, major, minor. For each: an id (A<n>-F01 upward), the rank, the
brief section, the problem, the evidence, and the smallest change that resolves it. End with
anything you could not check.
```

Facet paragraphs:

- **`A1` — coverage and fidelity** (`A1-coverage.md`). Every O-item and every phrase of the owner's
  recorded words on `000497` and the batch ideas is covered or explicitly marked out of scope;
  nothing the owner did not ask for is presented as asked; the batch is treated as fully in scope;
  each report's claims are carried into the brief without being strengthened, weakened or
  dropped; the brief stops at synthesis and plans no build.
- **`A2` — data correctness and feasibility** (`A2-data.md`). Each derivation in *Coverage* is
  right against the code and files it names; idea state comes from `fold()`; each named command
  and function exists and does what the brief says; each status label (`available`, `derivable`,
  `not recorded durably`, `missing`) is correct; nothing presented as derivable depends on the
  Session Manager's gitignored reports.
- **`A3` — usefulness, upkeep and priority** (`A3-usefulness.md`). The recommended display serves
  one place to reference everything, readable on a phone; it stays current without the owner or an
  agent doing it by hand, or the brief says who does it; staleness is visible; the build priority's
  dependencies hold; the first slice is the one that most reduces the owner's difficulty keeping up,
  and nothing earlier in the order depends on something later.

---

### G2 — fixes and the owner's ruling

For each finding, fix the brief or record why it stands, in a *Dispositions* table at the end of
the brief: finding id, rank, `fixed` or `accepted`, and one line. A blocker is never accepted
without the owner's ruling. Commit. Then send the owner, in the message text, the brief's summary,
its build priority, and each finding with its disposition, and ask for the ruling with
`AskUserQuestion`. Record it in `gate-log.md`.

On acceptance: commit, rebase onto `dev`, and run the four gate checks **in the worktree**:

```bash
uv run python -m src.governance
uv run pytest
uv run ruff check src/ test/
uv run mypy src/
git diff --exit-code docs/08-governance/catalog.md
```

Stage the changes and run `uv run python tools/check_no_private_content.py` with them staged. Then
send `READY agent/monitoring-investigation` to the Session Manager with the owner's `G2` ruling
and the tail of each run. Merge only on `GRANTED merge`, following the Session Manager's merge
steps. Hand the brief's path to the Session Manager for the next stage: the planning session that
expands the brief into a requirement, a plan and backlog phases.

## Descope ladder

The owner may descope. The coordinator never does it on its own; if time or budget runs short it
stops at the next gate and asks. The rungs, in the order to offer them:

1. Merge `I5` into `S`: the coordinator derives the build priority from `I1`–`I4` and the batch
   ideas itself.
2. Merge `A3` into `A1`.
3. Replace `A1`–`A3` with a single `partition-adversary` dispatch that covers all three facets.

Skipping `G1` or `G2` is not a rung.

## Review of this pack

Recorded before this document merged: the adversarial review of the pack itself, its findings and
their dispositions.

<!-- review:start -->
Pending.
<!-- review:end -->
