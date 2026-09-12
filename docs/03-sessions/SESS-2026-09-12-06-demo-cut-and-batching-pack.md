---
schema_version: 1
id: doc-session-demo-cut-and-batching-pack
code: SESS-2026-09-12-06
title: Demo fast-lane cut and the idea-batching pack — two workstreams in sequence
kind: session
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems:
- sys-governance
- sys-backlog
- sys-portfolio
- sys-ui
- sys-demo-stage
depends_on:
- doc-prompt-pack-protocol
- doc-prompt-idea-batching-pre-plan-package
- doc-workbench
---

# Demo fast-lane cut and the idea-batching pack — two workstreams in sequence

## Phase

**No phase was claimed, and none reached `status: complete` in this session.** That is correct
rather than a gap, and it matches the precedent set by `SESS-2026-09-12-03` and
`SESS-2026-09-12-04`: both workstreams here manufacture governed documents and hand work to other
sessions, which is not phase work.

Workstream A *created* two phases — `phase-wb-11` (Popover height math and the multi-panel double
header) and `phase-wb-12` (runbook additions for the two demo-week presenter risks). Both enter the
backlog `queued`, both are in `next_up` behind `phase-wb-07`, and neither has been started.

Workstream B executed `GOV-008` stage 4 against the pack factory
([PROMPT-026](../02-prompts/PROMPT-026-idea-batching-pack-factory.md)), which forbids claiming a
phase outright.

Two peer claims were active and were never touched: `phase-demo-07` (`agent-demo-glossary`,
locking `sys-brain` and `sys-portfolio`) and, from partway through, `phase-lit-01` (`agent-lit`).
The `sys-portfolio` overlap with `phase-demo-07` is real — `PROMPT-026` names that system — but no
deliverable path collided, since that phase writes `brain/concepts/` and nothing here does.

Because no phase was claimed, there are no backlog `verification` or `acceptance` lists to
recompute. `PROMPT-026`'s own stop condition played that role for workstream B, the owner's
ratified brief played it for workstream A, and the independent review in `## Review` was run
against the session's diff rather than against a phase's acceptance conditions.

## Verification

Run at close, in the worktree `/code/d-system-worktrees/demo-cut-pack-factory` on
`agent/demo-cut-pack-factory`, after rebasing onto `dev` at `a28df37`, **with this session record
present and the catalog regenerated to include it** — so these figures are what a reader running
the same commands reproduces. The document count is 188 rather than the 187 the independent
review saw, because this record is itself the 188th:

```text
$ uv run python -m src.governance
Governance OK: 19 systems, 188 documents, 20 memories, 131 backlog phases

$ uv run pytest
578 passed, 2 warnings

$ uv run ruff check tools/build_idea_corpus.py
All checks passed!

$ uv run mypy src/
Success: no issues found in 24 source files

$ diff <(uv run python -m src.governance --catalog) docs/08-governance/catalog.md
(no difference)

$ uv run python tools/check_no_private_content.py     # with changes staged
note: _private/portfolio/ not found — content check skipped (path check still ran)
check_no_private_content: OK (528 tracked files, 0 identifiers checked)
```

The measurement that was workstream A's first task, recorded here because it is the session's
main evidential result — six consecutive full-suite runs, five in the primary checkout on `dev`
and one in the worktree:

```text
run 1   1 failed, 577 passed     0 PTY failures
run 2   578 passed               0 PTY failures
run 3   578 passed               0 PTY failures
run 4   578 passed               0 PTY failures
run 5   578 passed               0 PTY failures
run 6   578 passed               0 PTY failures   (worktree)
```

Run 1's single failure was `test_codes.py::test_committed_catalog_matches_regenerated_output`,
not a PTY test. It is explained in `## Corrections` and was not a defect.

The corpus builder was exercised against the real log and independently reproduced every figure
measured by hand during preflight:

```text
$ uv run python tools/build_idea_corpus.py --stats
corpus_size            129
triaged                135
excluded_by_fast_lane  000101 000105 000107 000108 000117 000130
recorded_but_returned  000106 000110 000118 000119 000132 000137
layered_evidence       000014 000070 000071 000077 000087 000091 000099   (7)
finding_authors        agent-idea-triage 130, agent-demo-factory 2,
                       repository-owner 1, agent-workbench-planner 1,
                       agent-readme-audit 1, agent-workbench-coordinator 1
```

## Acceptance

No phase acceptance lists apply. Judged instead against `PROMPT-026`'s stop condition and the
owner's ratified brief for workstream A:

- **All four pack artifacts exist** — Met. `PROMPT-032` (delegation pack), `partition-adversary`
  (charter), `tools/build_idea_corpus.py` with `OPS-015`, and `PROMPT-033` (kick-off record).
- **`--inventory` exits 0** — Met; 187 documents.
- **`pytest` is green** — Met; 578 passed, including `test_tool_docs.py`'s two assertions over the
  new tool/OPS pairing, which reach it through dynamic discovery rather than a hard-coded list.
- **Catalog in sync** — Met; regenerated and committed in the same change, twice (once per commit),
  and again after the rebase.
- **Owner has the review summary** — Met; delivered in chat naming what the pack contains, what it
  omits and why, and the dispatch order.
- **The build was not started** — Met. No analyst was dispatched; `GOV-008` stage 5 has not run.
- **Workstream A measured before trusting `000099`** — Met; six runs, distribution reported rather
  than a verdict.
- **Workstream A stopped for ratification before acting** — Met; the cut was presented and the
  owner ratified items 1–4 before any phase was queued or the exclusion file written.

## Backlog

Two phases added, both `queued`, both placed in `next_up` behind `phase-wb-07`:

- `phase-wb-11` — Popover height math and the multi-panel double header. `next_action` records
  that there is no frontend test framework in `ts/`, so the browser pass is the only real gate and
  a green build must not be accepted as evidence.
- `phase-wb-12` — Runbook additions for the two demo-week presenter risks. `next_action` records
  the overlap with `phase-wb-07`'s declared deliverables and what to confirm before claiming.

No existing phase's lines were edited. No phase reached `complete`. Nothing was pruned from
`next_up`. The peer's `phase-lit-01` claim arrived on `dev` mid-session and was preserved verbatim
through the rebase.

## Unresolved

- The branch `agent/demo-cut-pack-factory` is **unmerged and unpushed**. `phase-wb-11` and
  `phase-wb-12` are invisible to the in-flight demo build until it lands, and the demo is
  2026-09-15.
- `GOV-008` stage 5 — the adversarial audit of the finished pack — has not run. No analyst may be
  dispatched before it and the owner's approval.
- `AGENTS.md` contradicts itself on pushing: *Confidentiality and publishing* says "Pushing your
  own branch to `origin` needs no approval", while *Concurrent agents: claim a phase* says "ask the
  owner before pushing" and cites, as its authority, the section that says the opposite. Reported,
  not edited. This is the same stale-duplication failure `CLAUDE.md` documents for the no-remote
  rule.
- Six ideas are now `open` (`000145`–`000150`) and therefore outside the corpus. The builder
  still reports exactly 129, so the status filter is behaving as designed — but the open set was
  two when the owner ruled "triaged only" and is now six. Worth a decision before the build runs.
- `check_no_private_content`'s **content** check was skipped throughout, because
  `_private/portfolio/` is not present in this worktree. Only the path check ran. The
  `phase-wb-10` precedent symlinked `_private` in to get real identifier checking; this session
  did not, having no direction to touch `_private/`.
- The corpora under `_working/idea-corpus/` (1.7MB) exist only in this worktree and are gitignored,
  so no merge carries them. They are fully regenerable with `--seed 20260912`.

## Review

An independent sub-agent (fresh context, not a fork) reviewed `dev...HEAD` — commits `c18f3e6`
and `1907322` — against `PROMPT-026`'s stop condition and a list of specific claims to attack. It
built a throwaway worktree at `1907322` under the scratchpad to get clean signal, then removed it;
it modified no repository file. Its findings, condition by condition:

**A1–A8 — pack factory stop condition and owner brief**

- **A1 — HOLDS.** All four artifacts present: `PROMPT-032`, `.claude/agents/partition-adversary.md`,
  `tools/build_idea_corpus.py` + `OPS-015`, `PROMPT-033`.
- **A2 — HOLDS.** Isolated clean checkout: `--inventory` exit 0, `Documents: 187; memories: 20.`
- **A3 — HOLDS for the two commits.** Isolated checkout: `578 passed, 2 warnings in 31.12s`. Also
  verified `test_tool_docs.py` actually covers the new tool, not just "suite is green":
  `discover_tools()` dynamically found `build_idea_corpus.py` and `find_doc()` resolved it to
  `OPS-015-build-idea-corpus.md` — confirmed by direct Python invocation, not by reading the test.
- **A4 — HOLDS for the two commits.** Catalog diff produced no output in the isolated checkout.
- **A5 — HOLDS.** No batching staging document under `docs/00-working/`, no `report-R*.md` tracked,
  both new phases `status: queued`, and `AGENTS.md`/`CLAUDE.md`/`_data/ideas.jsonl` do not appear
  in the diff's file list.
- **A6 — HOLDS.** Enumerated all 14 tools via `discover_tools()`/`find_doc()` directly — every one
  has a paired OPS document, `build_idea_corpus.py → OPS-015` included.
- **A7 — HOLDS.** `_data/ideas.jsonl` absent from the diff.
- **A8 — HOLDS.** `phase-wb-11`/`phase-wb-12` added `queued` and inserted into `next_up` after
  `phase-wb-07`; no `+`/`-` line touches `phase-lit-01` or `phase-demo-07`'s blocks (grepped
  explicitly).

**B1–B10 — specific claims attacked**

- **B1 — HOLDS.** Imports `fold, load_events` from `src/db/ideas.py`; the only file read is the YAML
  exclusion file.
- **B2 — HOLDS.** `corpus_size: 129` = 135 − 6, not −12: the six `dropped` ids
  (`000106,000110,000118,000119,000132,000137`) stay **in** the corpus.
- **B3 — HOLDS.** Ran with a nonexistent relative path and with `/tmp/definitely-not-a-real-path-xyz123.yaml`
  outside the repository: both exit 0 with `corpus_size: 135`, no traceback.
- **B4 — HOLDS.** `findings_of()` filters by `kind == "finding"` with no author restriction;
  `corpus-R1.md` empirically carries bylines from 6 distinct authors.
- **B5 — HOLDS.** Grep for hard-coded idea ids in the tool → no matches; the set is computed.
- **B6 — HOLDS.** Built the corpora and inspected `corpus-R4.md` directly: header reads *"Each entry
  carries its title, body and links."*; `### Findings`, `LAYERED EVIDENCE` and byline-pattern greps
  all return **zero** matches. Every remaining occurrence of "finding" is inside idea body prose,
  never a structural marker.
- **B7 — HOLDS.** All four files' sorted id sets hash identically (129 ids each); orders differ
  correctly.
- **B8 — HOLDS.** Extracted the quoted criterion from R1's block and from `PROMPT-025` decision 9 —
  identical wording; only line-wrap differs, an artifact of blockquote vs fenced-code formatting,
  not a paraphrase.
- **B9 — HOLDS.** A `difflib` diff of R1's vs R4's dispatched blocks shows exactly three changes:
  the corpus filename and its description, the removed multi-finding paragraph, and the report
  filename. Nothing in R4's dispatched text mentions "control", "bias", "findings" or other
  analysts — the "THE CONTROL" label lives only in the pack's commentary, never in the text sent.
- **B10 — CANNOT VERIFY the historical six-run claim** (history cannot be replayed), but ran
  `test/test_demo_terminal.py` three times independently in the clean worktree: `46 passed` each
  run, 0 failures — consistent with, though not proof of, the record's claim.

**C1–C3** — all HOLD. Codes unique and matching their filenames; the exclusion file parses with
dispositions a subset of the declared set; no path outside expected scope touched.

**Discrepancies it found — both real, both since fixed:**

1. **The record's own verification was not reproducible in this worktree.** Running `pytest` here
   showed `1 failed, 577 passed` (`test_codes.py::test_committed_catalog_matches_regenerated_output`)
   with a non-empty catalog diff — not a defect in the two commits (green in isolation), but because
   this session record is itself a new governed document not yet in the committed catalog. A reader
   following the record's own commands would not reproduce its numbers. Fixed at close: the catalog
   was regenerated with this record present and the figures in `## Verification` re-taken from that
   state.
2. **Dangling section reference.** `## Verification` pointed at a `## Corrections` section that did
   not exist, because the close had not yet written it. Fixed by this edit.

No other discrepancies found. Every other condition holds against independently reproduced
evidence rather than the record's own account.

## Decisions

**The demo cut was drawn on one principle: one root cause is one fix, not three tickets.** The
three highest-value reported symptoms — the owner's file selector showing two entries (`000108`),
the rotator help tooltip cut off (`000130`), and the general popup-sizing complaint (`000117`) —
all trace to a single expression at `ts/src/stage/Popover.tsx:92`, where a 120px floor wins over
available space. Verifying that in code rather than trusting the idea text is what let one phase
absorb all three, and it is why `phase-wb-11` is small enough to be credible three days before the
demo.

**Verification beat reputation on `000099`.** The idea asserts in capitals that the PTY failures are
"NOT FLAKY, AND NOT LOCAL" and that the trunk is red. Six runs produced zero PTY failures. The
owner's brief demanded a distribution rather than a verdict, and that instruction is what kept the
session from either confirming a stale claim or declaring a fix from one green run.

**The owner overrode nothing, but did rule on four things the documents left genuinely open**, each
via `AskUserQuestion` rather than prose: ship items 1–4 of the cut and record 5–8 as `dropped`;
exclude the newly-`open` ideas rather than triage them into the corpus; leave the descope ladder's
`A2` flag standing rather than reorder it now; and grant the build session no integration
authority, no model escalation above sonnet, and concurrent analyst dispatch.

**The pack's controlled variations were deliberately put in the FILES, not the prompts.** `R2` and
`R3` are dispatched `R1`'s block with a filename substituted, and `R4` is `R1` with findings
removed. No analyst is told its input differs from anyone else's, because a prompt that explains
the variation reintroduces exactly the framing the variation exists to control.

**Two phases were created rather than folding the work into `phase-wb-07`.** That phase is blocked
on owner-machine checks and was previously another agent's; editing its lines would have taken a
claim that was not this session's to take.

## Corrections

**Switching the shared checkout's branch was the session's real mistake.** Asked to work on a new
branch, this session ran `git switch -c` inside `/code/d-system` while a peer session was live in
that same directory — against `AGENTS.md`'s rule that the primary checkout's branch is never
switched while a peer holds an active claim. Twelve seconds later the peer committed, and its work
(`74fbeae`, `PROMPT-030`) landed on this session's branch instead of `dev`. A second peer commit
(`635b7bc`, `PROMPT-031`) landed the same way during the repair, and was caught only because
`git branch -d` refused to delete a branch that was "not fully merged". Both were restored to `dev`
by fast-forward — the first under explicit owner ratification, the second under the same ruling —
and the session then moved to an isolated worktree, where it should have started.

The peer independently reported the same hazard from its side, having briefly believed a commit was
lost.

**A false conclusion was very nearly recorded as a finding.** The first full-suite run failed
`test_codes.py::test_committed_catalog_matches_regenerated_output`, which looked like an
intermittent test. It was not: the run started inside the 35-second window between the peer writing
`PROMPT-030` (06:56:38) and regenerating the catalog (06:57:13). Two sessions drawing wrong
conclusions from the same transient shared state is a sharper argument for worktree isolation than
the lost-commit risk, because a lost commit announces itself and a false conclusion does not.

**Two defects in the corpus builder were found by testing it rather than trusting it.** The
control's file header read *"Ideas marked LAYERED EVIDENCE carry more than one finding"* — telling
`R4` that findings exist and silently compromising the only bias control in the design. And
`--exclusions` with a path outside the repository crashed in `relative_to()` instead of taking its
own documented missing-file fallback. Both were fixed and re-verified, and the independent review
re-confirmed both fixes (B3, B6).

**The close review caught two self-consistency faults in this record**, both recorded above in
`## Review` and both fixed rather than argued away.

## Left undone

**The branch is unmerged and unpushed, and that is the one item with a deadline.** `phase-wb-11`
and `phase-wb-12` are the ratified demo fixes; they are invisible to the in-flight demo build until
the branch lands on `dev`, and the demo is the week of 2026-09-15. Integration is the owner's call
under `AGENTS.md`, and `dev` carried a peer's uncommitted work for most of this session, so nothing
was forced.

**`GOV-008` stage 5 has not run.** The pack is manufactured but not adversarially audited. No
analyst may be dispatched before that audit and the owner's approval — the pack itself says so, and
this session deliberately stopped there rather than starting the build.

**`AGENTS.md`'s self-contradiction on pushing was reported, not fixed.** *Confidentiality and
publishing* says pushing your own branch needs no approval; *Concurrent agents: claim a phase* says
to ask first and cites, as its authority, the section that says the opposite. Editing either file
requires the owner's explicit per-change approval, so this stops at a report with the passages
quoted.

**The open-idea set has grown since the owner ruled on it.** Two ideas were `open` when the ruling
was "triaged only"; six are now (`000145`–`000150`). The corpus still measures exactly 129, so the
filter is behaving as designed — but six ideas now sit outside the batch, and whether they should
be triaged in before the build runs is a decision for before stage 5.

**The private-content check ran at half strength all session.** `_private/portfolio/` is not present
in this worktree, so only the path check ran and zero identifiers were actually checked. The
`phase-wb-10` precedent symlinked `_private` in to get real coverage; this session had no direction
to touch `_private/` and did not. Anyone integrating this branch should run the check where the
portfolio is present.

**The built corpora are worktree-only.** 1.7MB under `_working/idea-corpus/`, gitignored, carried by
no merge. Fully regenerable with `--seed 20260912`, so removing the worktree loses nothing — but
removing it without regenerating first means the build session rebuilds them.
