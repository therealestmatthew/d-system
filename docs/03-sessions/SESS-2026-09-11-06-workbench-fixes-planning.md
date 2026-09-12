---
schema_version: 1
id: doc-session-workbench-fixes-planning
code: SESS-2026-09-11-06
title: Workbench fixes planning — REQ-007 delta, phases wb-08..10, PROMPT-024 pack
kind: session
status: active
owner: repository-owner
created: '2026-09-11'
updated: '2026-09-11'
systems: [sys-ui, sys-demo-stage, sys-api, sys-backlog, sys-governance]
depends_on: [doc-workbench, doc-workbench-requirements]
---

# Workbench fixes planning — REQ-007 delta, phases wb-08..10, PROMPT-024 pack

## Phase

None claimed. This session executed the workbench fixes hand-off
(`docs/00-working/handoff-workbench-layout-and-terminal-fixes.md`) — a documentation-only
session run directly on `dev` per `GOV-003` — and *produced* the fix phases (`phase-wb-08`,
`phase-wb-09`, `phase-wb-10`) rather than working one. It also, on the owner's explicit
instruction, integrated the peer branch `agent/phase-wb-07` into `dev` and moved that phase to
`blocked` with its claim released. Active claim throughout, untouched: the glossary phase
(`phase-demo-07`, `agent-demo-glossary`).

## Verification

- `uv run python -m src.governance` — `Governance OK: 18 systems, 165 documents, 16 memories,
  122 backlog phases`, exit 0. (166 documents once this session record itself is counted; the
  independent review confirmed the delta is exactly this file.)
- `uv run python -m src.governance --ready` — `phase-wb-08` ready at queue position 1 with an
  empty Conflicts column; `phase-wb-09`, `phase-wb-10` and the blocked `phase-wb-07` behind it
  in `next_up`; one active claim (`phase-demo-07`), 1 of 3 slots.
- `uv run pytest` — 552 passed, 3 failed, 2 warnings. The three failures are the known
  environmental PTY set in `test/test_demo_terminal.py` (ideas `000097`/`000099`, host pyenv
  shim contention), reproducing identically before this session's changes and inside the
  rebased `agent/phase-wb-07` worktree.
- `uv run python tools/check_no_private_content.py`, run with all changes staged —
  `check_no_private_content: OK (500 tracked files, 31 identifiers checked)`.
- `uv run python -m src.governance --catalog` — catalog regenerated and committed with each
  change set.

## Produced

- **REQ-007 delta (rows W15–W18)** — terminal/panel fill (W15, broadened to the HTML Viewer
  after the owner's Windows report), the panel-to-slot assignment model (W16), concurrent
  shells with the six-session global cap and the backend-reported platform default (W17), and
  File Browser internal scroll (W18) — plus the amendments to W05/W06, ADR-016 decision 1 and
  the session caps. REQ-006 R10 amended to state both cap numbers.
- **PLAN-022 delta and backlog phases** — `phase-wb-08` (panel rendering fixes, first
  priority), `phase-wb-09` (layout assignment), `phase-wb-10` (runbook/checklist refresh),
  strictly sequential, front of `next_up`.
- **PROMPT-024** — the delegation pack for wb-08/09 in PROMPT-021's conventions, plus the
  `W08-M` diagnosis-dispatch convention (live measurements taken by `demo-validator-web`,
  consumed by the browserless creators).
- **GOV-008 stage-5 gate executed** — a haiku coverage audit (full coverage, no findings) and
  a `demo-adversary` pack audit (2 blockers, 2 majors, 1 minor — all fixed and committed;
  see `## Review` and commit `75c7442`).
- **GOV-003 extension** — the workbench completion gate extends to `phase-wb-08`/`09`
  (owner ruling 2026-09-11); `phase-wb-10` excluded, closing via `/session-close`.
- **PROMPT-023 delta 4 and the fix-build kick-off paragraph** — starting state, pre-approved
  green-gate integration for wb-08/09, owner checks homed in `phase-wb-07`'s checklist.
- **Idea-queue precedence correction** — the nonexistent `planned` status replaced with
  `reviewing` in REQ-007 W10 and `phase-wb-06`'s scope (session-close audit finding; verified
  against `schemas/idea.schema.json` and `IDEA_QUEUE_STATUS_PRECEDENCE`).
- **`agent/phase-wb-07` integrated** — rebased onto `dev` (11 commits, clean), verified
  (governance 0; pytest 552/3-environmental), fast-forwarded at `5f7a9a9` on the owner's
  instruction, and pushed. `phase-wb-07` moved to `blocked` (claim released,
  `blocked_reason`/`resume_when` recorded, `depends_on` gains `phase-wb-10`).

## Backlog

- `phase-wb-08`, `phase-wb-09`, `phase-wb-10`: `queued`, front of `next_up` in that order.
- `phase-wb-07`: `blocked`, claim released; resumes after `phase-wb-10` for the owner-machine
  checks; evidence branch integrated into `dev`.
- No phase reached `status: complete` this session; none was worked.

## Unresolved

None for this session's own scope. The fix build itself (wb-08 → wb-09), the runbook refresh
(wb-10) and the owner-machine checks (wb-07) are downstream work with their own gates.

## Review

Independent sub-agent review (fresh non-fork agent, no session context), verbatim:

> ### Condition 1 — Reruns
>
> - `uv run python -m src.governance` — exit 0, `Governance OK: 18 systems, 166 documents, 16
>   memories, 122 backlog phases`. The record claims **165** documents. Explained, not a
>   discrepancy: the committed catalog (`docs/08-governance/catalog.md` line 222) says 165,
>   and the one extra document in my live run is the session record itself — untracked on
>   disk, written after the session's verification runs, and absent from the committed
>   catalog. Everything else in the line matches exactly.
> - `--ready` — exit 0: `phase-wb-08` at queue position 1, Conflicts column `—` (empty);
>   wb-09, wb-10, blocked wb-07 behind it in next_up; exactly one active claim
>   (`phase-demo-07`, `agent-demo-glossary`), 1 of 3 slots. Matches the record.
> - `tools/check_no_private_content.py` — exit 0, `OK (500 tracked files, 31 identifiers
>   checked)`, identical to the record's line.
> - The 3 PTY failures are documented as pre-existing/environmental, not introduced here:
>   backlog.yaml (lines 4989, 5021–5023, 5318) records them as host pyenv-shim contention
>   predating the phases; idea `000099` records the red trunk and idea `000097` the root
>   cause, with a coordinator finding on 000099 clearing the suspect commit via baseline
>   evidence. Consistent with the record's claim.
>
> ### Condition 2 — Artifacts exist as claimed
>
> - REQ-007 has delta rows W15–W18 (lines 84–87), under a delta section referencing the
>   hand-off, with W15 covering terminal fill plus the HTML Viewer, W16 assignment model,
>   W17 concurrent shells/six-cap/platform default, W18 File Browser scroll. Confirmed.
> - REQ-006 R10 (line 44) states both caps: "up to four terminal sessions as tabs (the
>   backend session registry separately bounds concurrent sessions to six ... REQ-007 W17)".
>   Confirmed.
> - PLAN-022 has "## Delta 2026-09-11 — fix phases" describing wb-08/09/10 and the order
>   wb-08 → wb-09 → wb-10 → wb-07. Confirmed.
> - backlog.yaml: phase-wb-08/09/10 all present, `queued`, each with scope, acceptance,
>   verification and deliverables keys (parsed programmatically). Confirmed.
> - PROMPT-024 exists (596 lines added in d102c51) with exactly the claimed sections:
>   W08-K/M/C1/V1/G/A/W and W09-K/C1/V1/C2/V2/C3/V3/G/A/W. Confirmed.
>
> ### Condition 3 — Adversary-audit fixes in 75c7442
>
> - (a) W08-M "diagnosis: live measurements before the fix (demo-validator-web)" exists;
>   W08-C1 explicitly says "You have no browser tool — never report a measurement you did
>   not receive from W08-M" and "You cannot verify the fix in a browser yourself ... ask the
>   orchestrator to re-dispatch W08-M". Confirmed.
> - (b) Both kickoffs check the Conflicts column: W08-K (line 85) and W09-K (line 358) each
>   require confirming the phase's Conflicts column is empty before claiming. Confirmed.
> - (c) GOV-003 lines 285–290: completion authority "extends on identical terms to
>   `phase-wb-08` and `phase-wb-09`", with `phase-wb-10` completing through `/session-close`
>   instead. Confirmed.
> - (d) W15's verification cell ends: "The Windows confirmation ... is an owner check in the
>   `phase-wb-07` checklist, not closed by agent evidence." Confirmed (mirrored in wb-07's
>   `resume_when`).
> - (e) PROMPT-024 line 406 says `ADR-014's cap wording (its "four-session cap"
>   statements)`; the phrase "bounds concurrent sessions to four" does not appear anywhere
>   in PROMPT-024. Confirmed.
>
> ### Condition 4 — phase-wb-07 state and integrated branch
>
> - backlog.yaml: `status: blocked`, no claim, `blocked_reason` and `resume_when` both
>   present and substantive, `depends_on` includes `phase-wb-10`. The clean governance run
>   in condition 1 proves the validator accepts it.
> - `git log --oneline -3 -- docs/00-working/demo-runbook.md` on dev shows the rehearsal
>   commits; the full range d102c51..5f7a9a9 contains all 11 phase-wb-07 branch commits plus
>   the four out-of-scope owner audits. Confirmed.
>
> ### Condition 5 — Idea-status precedence
>
> - REQ-007 W10 (line 49): "status precedence (open → triaged → reviewing)". phase-wb-06's
>   scope in backlog.yaml contains "reviewing" and no "planned". `schemas/idea.schema.json`
>   status enum is `["open", "triaged", "reviewing", "promoted", "discarded"]` — no
>   "planned". `IDEA_QUEUE_STATUS_PRECEDENCE` in `src/api/routes/workbench.py` (line 441)
>   ranks open 0, triaged 1, reviewing 2. All consistent. Confirmed.
>
> ### Condition 6 — No completions, governing files untouched
>
> - Across all 14 in-scope commits (d102c51, 75c7442, 4e4f532, and the 11 integrated wb-07
>   commits), zero added lines matching `status: complete` in backlog.yaml, and no commit
>   touches CLAUDE.md or AGENTS.md. Confirmed.
>
> ### Verdict: clean
>
> Every claim in the session record that I checked holds against the diffs and my reruns.
> The single numeric divergence (166 vs 165 documents) is fully accounted for by the
> untracked session record itself, which post-dates the session's verification runs and is
> exactly the file `/session-close` will finalize — it is evidence of an active session
> record, not an inaccuracy.

## Decisions

- The owner confirmed the hand-off's four marked assumptions: overview stays main-slot-only;
  per-panel tab cap four with the global PTY cap six; storage migrates by `schema_version`
  bump under ADR-016 rule 3 with no ADR amendment; defaults reproduce the current arrangement
  with the terminal slot's visible shell defaulting to PowerShell on Windows, decided by a
  backend-reported platform route rather than user-agent sniffing.
- GOV-008's stage-5 pack audit ran as two passes on the owner's choice (coverage + adversary),
  and every finding was fixed rather than argued down.
- Mid-session the owner added two defects (HTML Viewer blank on Windows; File Browser missing
  scroll) and chose to fold both into `phase-wb-08` and to create `phase-wb-10` for the
  post-fix runbook refresh.
- The owner ratified: pre-approved green-gate integration for wb-08/09; the split Windows
  check schedule; extending GOV-003's completion authority to wb-08/09 only; leaving
  PROMPT-021's two stale `planned` mentions verbatim as the dispatch record; releasing
  `phase-wb-07`'s claim (blocked, not requeued — the validator requires a claimed state for a
  phase carrying checkpoint results); integrating `agent/phase-wb-07` and pushing `dev`.

## Corrections

- The session initially wrote the kick-off delta assuming `phase-wb-07` would close; the
  owner's session-close audit instead kept it active (later blocked). The delta's starting
  state, the owner-check homes and PLAN-022's ordering paragraph were rewritten to match
  reality.
- A YAML edit placed an unquoted colon inside `phase-wb-07`'s `next_action`, breaking the
  backlog parse; caught by the governance run and fixed immediately.
- The first attempt set `phase-wb-07` to `queued` while keeping its result record, which the
  governance validator correctly rejected; corrected to `blocked` with
  `blocked_reason`/`resume_when`.

## Left undone

Deliberately, for downstream sessions: the fix build itself runs from the fix-build kick-off
paragraph (PROMPT-023) in a fresh session; `phase-wb-10` follows `phase-wb-09` as a
documentation session; `phase-wb-07`'s owner-machine checks and both timed dry-runs close only
on the owner's recorded results, against the refreshed runbook, before the 2026-09-15 demo.
The `phase-wb-07` worktree is intentionally left in place until that phase finally closes.
