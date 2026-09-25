---
schema_version: 1
id: doc-prompt-gemini-review-sequence
code: PROMPT-040
title: Gemini review sequence — three analysis prompts and a master prompt that runs them in worktrees
kind: prompt
status: active
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-governance]
depends_on: [doc-adr-session-manager-into-orchestrator, doc-multi-session-coordination-protocol]
---

# Gemini review sequence

## For the owner: what this is and how to run it

The owner asked for prompts to run with Google Gemini (2026-09-24, relayed by the Session Manager):
three analysis prompts, and one master prompt that has Gemini work through them. Each prompt names
its exact outputs. Each runs in its own git worktree, on its own branch, and never touches `dev`.

| Prompt | Area | Output directory (on its own branch) |
|---|---|---|
| G1 | Stress-test the three-axis classification framework v3 | `docs/00-working/gemini/g1-three-axis-stress/` |
| G2 | Competing designs for ADR-023's open parameters | `docs/00-working/gemini/g2-adr-023-parameters/` |
| G3 | Contradictions, duplication, unenforced rules and terminology drift in the governance documents | `docs/00-working/gemini/g3-governance-analysis/` |

**Before running.** This document and its inputs under `docs/00-working/gemini/` must be merged to
`dev` first: Gemini cuts each worktree from `dev` and reads the prompts from there.

**To run.** Start Gemini CLI in the primary checkout (`/code/d-system`) and paste the master prompt
(the fenced block in the next section). Gemini needs a shell, `git`, `uv` and permission to push
branches to `origin`. This document assumes Gemini CLI. Another Gemini interface without a shell
cannot run it.

**What comes back.** Three branches (`agent/gemini-g1-three-axis-stress`,
`agent/gemini-g2-adr-023-parameters`, `agent/gemini-g3-governance-analysis`) and a fourth,
`agent/gemini-run-summary`, holding `docs/00-working/gemini/run-summary.md`. A Claude session
reviews each branch, and each merges through READY and the owner's approval, like any branch.
Gemini merges nothing.

**Where outputs go, and why.** Everything goes under `docs/00-working/gemini/`. It is ungoverned
staging (`ADR-010`), so the files need no code or front matter, and the governance check skips them.
Nothing Gemini writes is a decision or a governed document. A later session decides what to promote.
No governed location fits better: the outputs are proposals, and the governed homes (`ARCH-005`,
`ADR-023`, the `GOV-*` documents) belong to phases that have not run yet.

**Inputs copied for Gemini.** Gemini reads tracked files only. Two gitignored sources were copied
verbatim into tracked staging files for it:
- `docs/00-working/gemini/inputs/three-axis-v3.md`: framework v3 and its classification report, from
  `_working/ideation/three-axis/v3/`, final as of 2026-09-25;
- `docs/00-working/gemini/inputs/adr-023-design-context.md`: excerpts of the P3 design proposal and
  the Scout's D3 comparison.

`research/architecture/architecture.md` is untracked, so it does not exist in a worktree. G1 uses
the tracked page `_public/d-system-architecture.html` (§02 and §04) instead.

## The master prompt

Paste this block into Gemini CLI, started in `/code/d-system`.

```text
You are running a sequence of three analysis prompts in the git repository at /code/d-system.
The prompts are in the file docs/02-prompts/PROMPT-040-gemini-review-sequence.md on the branch
`dev`. You have not read it yet.

1. Read these two sections of that file in full, from `dev`
   (`git -C /code/d-system show dev:docs/02-prompts/PROMPT-040-gemini-review-sequence.md`):
   "Shared rules (every prompt)" and "Stop and report". They bind every step below and override
   anything in GEMINI.md or AGENTS.md that conflicts with them.
2. Process the prompts in this order: G1, then G2, then G3. For each one:
   a. Create its worktree exactly as the shared rules' "Worktree" section says.
   b. Read that prompt's section of the file, and only that section, from inside the worktree.
   c. Do the work, and write the outputs the prompt names.
   d. Run the done check the shared rules give. Fix every problem it prints and run it again
      until it prints OK. If a problem cannot be fixed without guessing, stop (see "Stop and report").
   e. Commit and push the branch as the shared rules say. Record the branch name and the commit sha.
   f. Leave the worktree in place. Do not remove it or delete the branch.
3. After G3, write the run summary as the "Run summary" section of the file says, on its own
   branch, and push it.
4. Finish by printing, in chat, the same table the run summary holds.

If you stop early, still write and push the run summary, listing what finished and where you
stopped, and print it in chat.
```

## Shared rules (every prompt)

### Scope and authority

- This work is owner-directed and has no backlog phase. **Do not claim a phase, edit
  `docs/09-backlog/backlog.yaml`, write a session record, update `catalog.md`, or run
  `/session-close` or any completion step.** Where `GEMINI.md` or `AGENTS.md` tells you to do any of
  these, this rule overrides it for this work.
- Everything you write is a proposal. You decide nothing. Never describe a proposal as the owner's
  decision.
- The owner's rulings are fixed. Do not argue that one should be reversed. If you see a risk in a
  ruling, record it as a finding with category `risk-in-ruling` and `touches_owner_ruling: true`.
  State the risk and what would show it, not a replacement ruling.

### Worktree

For prompt `Gn` with slug `<slug>` (G1 `g1-three-axis-stress`, G2 `g2-adr-023-parameters`, G3
`g3-governance-analysis`):

```bash
git -C /code/d-system rev-parse dev                    # record this full sha as dev_sha
git -C /code/d-system worktree add -b agent/gemini-<slug> /code/d-system-worktrees/gemini-<slug> dev
cd /code/d-system-worktrees/gemini-<slug>
uv sync --frozen --extra dev                           # this worktree's own .venv; --frozen leaves uv.lock unchanged
```

- If the branch or the directory already exists, stop and report. Do not reuse, reset or delete it.
- **Never write in `/code/d-system`**, the primary checkout. The only commands you run there are the
  two above (`rev-parse` and `worktree add`, which change no file in it). Never switch its branch,
  commit there, or merge anything into `dev` or any other branch.
- Work only inside your worktree, and write only under the prompt's output directory.

### What you may read

- **Tracked files only**, at the worktree's commit. `git ls-files` lists them.
- **Never read `_private/`.** It holds the owner's confidential records. Never read `_working/`. It
  holds gitignored boards, reports and rulings that are not part of this work. Neither exists in a
  fresh worktree; do not look for them in `/code/d-system` either.
- **Never read or write `_data/ideas.jsonl` directly.** Where a prompt needs an idea, its text is given
  in the prompt.
- Public web documentation is allowed where a prompt says so. Cite each page by URL and the date you
  read it.
- If a tracked file appears to contain a real client name, a person's private data or a credential,
  stop and report it. Do not copy it into any output.

### What you may run

- `git`, `grep`, `sed -n`, `nl`, `wc`, `ls`, `uv run python` for the done check and the governance
  check, and read-only commands like them.
- **No tests.** Do not run `pytest` or any test anywhere. None of these prompts needs one. (Under the
  repository's protocol, tests never run in the primary checkout, and at most one run at a time runs
  per worktree.)
- Do not run anything that writes outside your output directory: no `tools/*.py` writers, no
  `--catalog`, no `rebuild_db.py`.

### Messages

You are not part of this repository's multi-session protocol. Do not send or expect `TURN?`,
`GRANTED`, `READY` or any other session message, and do not open pull requests. Your hand-off is the
pushed branch and the run summary.

### Citations

- Every claim about the repository cites a tracked file and line: `path` (repository-relative),
  `line` (a number or an inclusive range such as `42-47`), and `quote` (the exact text at those lines,
  or an exact excerpt of it). Take line numbers from `grep -n` or `nl -ba` in your worktree, so they
  match `dev_sha`.
- In Markdown, write a citation as `path:line`. In JSON, use the evidence object in
  `docs/00-working/gemini/schemas/evidence.schema.json`.
- A claim you did not check is not written. Say "not checked" if you must mention it.

### Provenance

Every output file carries the same five facts:

- **JSON:** a top-level `provenance` object (`docs/00-working/gemini/schemas/provenance.schema.json`).
- **Markdown (`report.md`):** these lines, before the first `## ` heading, one per line, exactly in
  this form:

```text
model: <your model name and version, as you report it>
date: <YYYY-MM-DD>
prompt: PROMPT-040 Gn
dev_sha: <the full 40-character sha you recorded>
branch: agent/gemini-<slug>
```

### Writing

Plain wording. State what you mean directly. No metaphors or figures of speech: write "a parameter
to vary", not "a dial to turn". Short sentences. Name a thing before citing its code, for example
"the three-axis framework (`ARCH-005`)".

### Ideas

If you think of something outside the prompt's scope, do not record it anywhere in the repository.
List it in `report.md` under a final section `## Ideas outside this prompt`, one line each.

### Done check, commit and push

In the worktree, before committing:

```bash
uv run python docs/00-working/gemini/check_outputs.py Gn     # must print OK
uv run python -m src.governance                              # must exit 0
git status --porcelain                                       # only paths under your output directory
```

Then:

```bash
git add docs/00-working/gemini/<slug>/
git commit -m "Gemini PROMPT-040 Gn: <one line on what the outputs contain>"
git push -u origin agent/gemini-<slug>
git rev-parse HEAD                                           # record for the run summary
```

If the push fails, retry once. If it fails again, record the error in the run summary and continue
with the next prompt.

## Stop and report

Stop and report, rather than guess, when:

- an input the prompt names is missing, or says something different from what the prompt says it
  says;
- two instructions conflict and the rules above do not settle which wins;
- you would need to read `_private/` or `_working/`, or write outside your output directory;
- the branch or worktree already exists;
- the done check reports a problem you cannot fix without inventing content.

To stop: write what you were doing, the exact problem, and the file:line or command output that
shows it into `report.md` under `## Stopped`. Commit and push whatever passes the done check (a
partial output is fine if it validates). If nothing validates, commit nothing. Then go to the run
summary and end.

## Run summary

After the last prompt, or after a stop:

```bash
git -C /code/d-system worktree add -b agent/gemini-run-summary /code/d-system-worktrees/gemini-run-summary dev
```

Write `docs/00-working/gemini/run-summary.md` in that worktree, with the provenance lines (with
`prompt: PROMPT-040 G1` replaced by `prompt: PROMPT-040 run summary`), then this table:

| Prompt | Branch | Commit sha | Status (done / stopped / not run) | Outputs | Done check result |
|---|---|---|---|---|---|

Under the table, list every stop with its reason, and any push error. Commit it with the message
"Gemini PROMPT-040: run summary" and push the branch. The done check script does not cover this
file; check by hand that `git status --porcelain` shows only `run-summary.md` before committing.

---

## G1: stress-test the three-axis classification framework v3

**Slug** `g1-three-axis-stress`. **Output directory** `docs/00-working/gemini/g1-three-axis-stress/`.

### Background

Ideas in this repository are classified on four axes: Ontological (what the record is about),
Epistemic (the truth status of what it asserts), Lifecycle (where it is between a raw idea and
reviewed work) and Temporal validity (whether it is time-bound). Records that are not knowledge
carry a record kind instead of axis values. The governed vocabulary today is the idea node
classification (`docs/07-architecture/ARCH-005-idea-node-classification.md`). Framework v3 is a
draft that extends it. It has already been through an adversarial review and the owner's rulings,
and it goes to `phase-idg-01` as input.

Gemini's earlier feedback, forwarded by the owner, already proposed values that v3 adopted: E "Not
Applicable / Agnostic"; O "Actor / Agent" and "Metric / Standard"; L "Active / Evergreen" and
"Deprecated / Archived". **Do not propose these again.** Your job is to test v3, not to rebuild it.

### Inputs (read these)

1. `docs/00-working/gemini/inputs/three-axis-v3.md`: framework v3 (Part 1) and the classification
   report of all 454 ideas under it (Part 2). This is the primary input.
2. `docs/07-architecture/ARCH-005-idea-node-classification.md`: the governed vocabulary v3 would amend.
3. `docs/01-plans/PLAN-029-idea-graph-lifecycle.md`, section "The chosen design", item 2 ("Each axis
   is optional, and a blank axis must carry a reason"), which ruling C1 amends.
4. `_public/d-system-architecture.html`: section 02 (`id="axes"`, the three-axis classification) and
   section 04 (`id="vocab"`, the transition vocabulary).
5. Two ideas, given here because you may not read the idea log:
   - **000454:** "Not all knowledge or 'ideas' have an epistemic classification (artifacts for
     example - can a GitHub repo and it's link be true? Maybe not, but we should integrate it because
     it may have valuable context would be a hypothesis or assumption... this is what we were
     searching for, do we need additional items along these axes to account for these kind of
     situations? Maybe, park that as an idea to drill deeper into but leave it blank right now if none
     align." (Ruling C1 later replaced the blank with Not Applicable / Agnostic on E.)
   - **000453:** exactly three outcomes for an idea in partitioning and triage: "discard", "set aside"
     or "include in a partition", and how each is managed. The owner: "we really need clear and
     unambiguous terminology for these and how to manage them."
6. For test cases beyond ideas: tracked records of other types, such as ADRs (`docs/04-decisions/`),
   memories (`brain/`), session records (`docs/03-sessions/`) and research documents (`research/`,
   tracked files only).

### Fixed: the owner's rulings (do not re-open)

These are listed in Part 1 §6 of the input: C1 (N/A on E only; record kinds cover non-knowledge
records), C2 (discard and supersede are record dispositions, independent of every axis), C3 (widen
L), C4 (Axiom is "a claim accepted as verified within its stated scope"), C5 (record kinds accepted),
C6 (E stays on the record), C7 (agent types are Actor / Agent), L5 (Deprecated applies to the
record's subject), T (a full fourth axis on every knowledge record) and E4 (an Insight's E is Axiom
unless hedged). You may record a risk in any of them as a `risk-in-ruling` finding.

### What to do

1. **The barely used values.** Event (0 records), Anti-Pattern / Falsified Concept (0), Deprecated /
   Archived (0), Metric / Standard (2) and Hypothesis / Assumption (3). The report says they will
   matter for other record types. Test that claim. For each value, look through the tracked records
   of other types (input 6) and find up to three records the value clearly fits, with citations. If
   you find none, say so, and say whether that shows a problem with the value's definition or only
   that the corpus has no such record. Check each proposed example against v3's decision rule and
   tie-breaks, and say which rule decides it.
2. **E and T as near-functions of L.** Part 2 §4 item 3 gives the counts. Describe two or three
   concrete ways a schema could handle this, for example storing E and T and flagging divergence from
   an expected value, or deriving a default from L and storing only overrides. For each, give the
   query consequences: what a query for "current verified facts" or "open asks" returns, and where it
   goes wrong. T stays a full axis (ruled). Any design must keep a stored T value on every knowledge
   record.
3. **The decompose rule (O6) and `L_remedy` (L4).** Take the eight records flagged `decompose` (Part 2
   §3) and the rule text. Find the cases where O6 and L4 give an unclear or conflicting answer, and
   construct at least three test records (short invented idea texts, marked as invented) that the
   rules classify inconsistently. Say what a rule change would need to settle each one. This is a
   proposal.
4. **Record kinds.** Test the four kinds (knowledge, collection, fixture, reference) against edge
   cases: a record that groups others and also makes its own claim; a reference with a one-line
   opinion; a fixture that has since been reused as a real example. Say which kind each gets under the
   current rule text, and whether the answer is stable.
5. **Alternative schemas.** Write two alternative JSON Schemas for one classification row. Each must
   encode every ruling above, and they must differ in a stated way, for example: one flat row with an
   enum per axis, and one where each axis is an object `{value, confidence, reason}` with a separate
   derived-default marker. Save them as `alt-a.schema.json` and `alt-b.schema.json`. In the report,
   compare them on validation strength, ease of appending the existing 454 rows, and the queries in
   item 2.
6. **Terminology.** Check that these three vocabularies use each word for one thing only: the axis
   value names (v3), the idea dispositions (discard, supersede, and 000453's "set aside" and "include
   in a partition"), and the transition verbs on the architecture page (section 04). List every word
   used for two different things, and every thing given two different words, with citations. For
   example, check whether "Deprecated / Archived" (an L value), DEPRECATE and RETIRE (transition verbs)
   and "discarded" (a disposition) are kept apart as ruling C2 requires.

### Outputs (exactly these files)

| File | Content |
|---|---|
| `report.md` | Provenance lines, then the sections `## Summary` (at most ten lines), `## 1. Barely used values`, `## 2. E and T against L`, `## 3. Decompose and remedy`, `## 4. Record kinds`, `## 5. Alternative schemas`, `## 6. Terminology`, `## Risks in rulings`, `## Ideas outside this prompt`. Every numbered section refers to its findings by id |
| `findings.json` | Valid against `schemas/findings.schema.json`. Ids `G1-F001` upward. Use categories `unused-value`, `axis-dependence`, `decompose-rule`, `record-kind`, `alternative-schema`, `terminology`, `risk-in-ruling` |
| `alt-a.schema.json`, `alt-b.schema.json` | Two valid JSON Schemas (draft-07) for one classification row, as item 5 describes |

Invented test records (item 3) go in `report.md` only, each marked "invented". They are never
presented as ideas from the log.

---

## G2: competing designs for ADR-023's open parameters

**Slug** `g2-adr-023-parameters`. **Output directory** `docs/00-working/gemini/g2-adr-023-parameters/`.

### Background

`docs/04-decisions/ADR-023-session-manager-into-orchestrator.md` (accepted 2026-09-24) records how
the multi-session coordination system moves onto the LangGraph and Claude Agent SDK orchestrator.
It records the owner's rulings and lists parameters it leaves open. Your job is to write competing
designs for four of them. Each design is built on the ADR's rulings, not argued against them. A
design that contradicts a ruling is invalid. If a ruling looks risky, record a `risk-in-ruling`
finding instead.

### Inputs (read these)

1. `docs/04-decisions/ADR-023-session-manager-into-orchestrator.md`, in full.
2. `docs/00-working/gemini/inputs/adr-023-design-context.md`: excerpts of the design proposal (P3) and
   the Scout's comparison (D3). These are proposals. The ADR wins wherever they differ.
3. `docs/01-plans/PLAN-039.01-orchestrator-design.md` (the orchestrator design) and
   `docs/08-governance/GOV-017-multi-session-coordination-protocol.md` (the current protocol).
4. The orchestrator and broker code on `dev`: `src/orchestrator/` (for example `tick.py`, `gates.py`,
   `decisions.py`, `daemon.py`, `dispatch.py`, `ledger.py`) and `src/broker/`. Cite what exists; do not
   describe code that is not there as if it were.
5. Public documentation for LangGraph, the Claude Agent SDK and Claude Code, if you need a fact the
   inputs do not give. Cite each URL with the date you read it.

### The four parameters

For each parameter, write **two or three competing designs**, and mark exactly one as your
recommendation.

1. **`router-shadow`: the router's shadow-mode rules** (ADR-023, D3-3 and "Parameters left open").
   How many runs the router spends in shadow, what counts as agreement between its proposal and what
   happened, the share of agreement required before it may route, and what happens if it falls below
   that share after it starts routing. Include how the proposals and outcomes are recorded (the ledger
   `_data/runs.jsonl` is canonical, D13).
2. **`grant-records`: where delegated-authority grant records live** (D10: "grant records in a tracked
   file, evaluated in code at G4 and cited in each decision"). The file's path and format, who writes
   it and through what writer, how a grant expires and is revoked, and how the G4 evaluator reads it.
   Note the design context: the broker's approval store is under a gitignored path today.
3. **`owner-desk-events`: how the Owner Desk session learns of daemon events** (D3-5: poll or watch
   the gate queue and `orchestrator status`, with a spike before A1). The polling interval or watch
   mechanism, what the session reads, how it avoids re-presenting an item, and its cost. The design
   context gives facts about long-lived session cost. The injection hook (idea 000428) is parked:
   do not design it here.
4. **`lease-file`: the primary-checkout lease** (D12: "a lease file under `data/orchestrator/`
   (staleness by heartbeat), with audit events in the ledger"). The file's fields, the heartbeat
   interval and staleness threshold, how the path resolves to the primary checkout from a worktree,
   the clean-checkout check at release, and stale-lease recovery.

For every design state: the mechanism; the data shape (a JSON example or a field list); the ADR-023
lines it rests on; its failure paths (what happens when each step fails); the existing code it reuses
or must change; how it would be tested; and its drawbacks.

### Outputs (exactly these files)

| File | Content |
|---|---|
| `report.md` | Provenance lines, then `## Summary` (at most ten lines), one section per parameter (`## 1. Router shadow rules`, `## 2. Grant records`, `## 3. Owner Desk events`, `## 4. Lease file`), each comparing its designs in a table and stating the recommendation as a proposal; then `## Questions for the owner` (the decisions each recommendation still needs); `## Risks in rulings`; `## Ideas outside this prompt` |
| `designs.json` | Valid against `schemas/designs.schema.json`. Ids `G2-RS-1`, `G2-GR-1`, `G2-OD-1`, `G2-LF-1` and upward within each parameter |
| `findings.json` | Valid against `schemas/findings.schema.json`. Ids `G2-F001` upward. Use it for gaps the designs expose (`design-gap`), conflicts between the ADR and the code or the other inputs (`ruling-conflict`), and `risk-in-ruling` |

---

## G3: analysis of the governance and protocol documents

**Slug** `g3-governance-analysis`. **Output directory** `docs/00-working/gemini/g3-governance-analysis/`.

### Background

The rules for how agents work here are spread across many documents. Two open ideas describe the
problem:
- **000402:** consistency checks across governance documents. Phase-completion authority is stated
  differently in `GOV-003`, `.claude/commands/session-start.md`, the orient skill, `GOV-014` and
  `AGENTS.md`. Its proposed direction is a register of canonical rule statements that documents cite,
  plus a check that the cited text matches.
- **000378:** phase-completion authority contradicts itself across documents. Its body cites
  `GOV-003` lines 456-518, `session-start.md` lines 191-192 and 224, the orient skill lines 79-80,
  `resume-lit-review.md` line 182, `GOV-014` lines 34, 175 and 195, and `AGENTS.md` lines 179-180 and
  284. Those line numbers are from 2026-09-23 and may have moved. Re-check them.

Your job is to find contradictions, duplication, rules that are stated but not enforced, and
terminology drift, and to draft the register 000402 proposes.

### Corpus (read these)

- Every `docs/08-governance/GOV-*.md` and `docs/08-governance/OPS-*.md` (list them with
  `git ls-files 'docs/08-governance/GOV-*.md' 'docs/08-governance/OPS-*.md'`).
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`.
- `docs/02-prompts/PROMPT-037-session-manager-starter-messages.md`.
- `docs/08-governance/GLOSSARY.md`, for the defined terms.
- To decide whether a rule is enforced: `src/governance/`, `tools/git-hooks/`, `.claude/settings.json`
  (hooks), `.claude/commands/`, `.claude/skills/`, `.github/workflows/` and `test/`. Read these to
  check; they are not the corpus.

### What to do

1. **Contradictions.** Two statements of the same rule that cannot both be followed. Quote both.
2. **Duplication.** The same rule stated in more than one place, whether the wording matches or not.
   Name the document that should own it, with a reason (for example, `AGENTS.md` says it wins over
   `CLAUDE.md`).
3. **Unenforced rules.** A rule stated as "must" or "never" that no code, test, hook or check
   enforces. Say what you searched to conclude it is unenforced. A rule that only a person can follow,
   such as "ask the owner", is not a finding by itself. Report it only if a mechanical check is
   possible and missing.
4. **Terminology drift.** A term used with different meanings, or one thing given different names,
   across the corpus. Check against `GLOSSARY.md`.
5. **The register.** Draft `rule-register.json`: one entry per rule you examined, with its canonical
   statement, every place it is stated, what enforces it (empty if nothing), and its status. Cover at
   least the rules your findings touch. Do not try to register every sentence in the corpus.

Do not propose edits to `AGENTS.md` or `CLAUDE.md` as changes to make. The owner must approve any edit
to either file. Where a finding concerns them, state the problem and quote the passage.

### Outputs (exactly these files)

| File | Content |
|---|---|
| `report.md` | Provenance lines, then `## Summary` (at most ten lines, with the counts by category), `## 1. Contradictions`, `## 2. Duplication`, `## 3. Unenforced rules`, `## 4. Terminology drift`, `## 5. The register`, `## Ideas outside this prompt` |
| `findings.json` | Valid against `schemas/findings.schema.json`. Ids `G3-F001` upward. Categories `contradiction`, `duplication`, `unenforced-rule`, `terminology-drift` |
| `rule-register.json` | Valid against `schemas/rule-register.schema.json`. Ids `R-001` upward. Each entry's `finding_ids` lists the findings about it |
