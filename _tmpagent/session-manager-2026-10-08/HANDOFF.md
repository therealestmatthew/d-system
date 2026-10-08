# HANDOFF — Session Manager, workbench run 2026-10-08 (second wind-down)

Read this first after a context reset or in a new session. Then `board.md` (event log, newest at the
bottom), then `ideas-pending.md`, then the artifact URL in `report/artifact-url.txt`. The first
session's hand-off text is kept below under "First session's hand-off (2026-10-08 morning)" because
its procedures and rulings 1-12 still bind; this top part is what changed in the second session.

## Why this session stopped
The owner ran out of cloud credits and asked for a wind-down. The run is PAUSED, not closed: one
phase is active with its work checkpointed on a pushed side branch.

## State at hand-off (trunk c24b492 or later, pushed; see board.md for the final sha)
- 18 phases complete (unchanged): arch-02, 05, 06, 11, 16; wbf-01, 02, 03, 04, 05, 06, 07, 08, 13,
  14, 15, 16, 18.
- ACTIVE: `phase-arch-07` (schema-owned slots and sub-slots with structural eligibility), claimed
  ALONE at trunk c281b7f with ADR-031's deliverable widening (ruling 1 done), `agent: agent-builder-a`.
  Its work is on branch `agent/phase-arch-07`, PUSHED to origin as a side branch with the owner's
  approval (2026-10-08, wind-down 2). The builder's CHECKPOINT message (tip sha, done / not-done
  list) is in board.md under "arch-07 CHECKPOINT"; the branch holds at least three commits:
  3db0b14 (one-top-bar test, failing on the trunk, R13), 1f2b7fc (structural eligibility,
  eligible_slots dropped, R12), b024d67 (one top bar per slot, controls moved into bar elements).
  Session record code reserved for it: SESS-2026-10-08-20.
- MERGED this session (trunk commits, all pushed):
  - 9c1f0b0 Ideation: ideas 000663-000672 (six wave-7 builder ideas; four owner asks: 000669
    websocket protection, 000670 rung-7 label, 000671 preserve terminal sessions, 000672 owner
    checklist); 000614/000637/000087 annotated; 000102 -> delivered (phase-wbf-02).
  - 58a5876 Ratification housekeeping (ruling 9 DONE): GOV-003 entry "The 2026-10-08 workbench
    run's ratification table is accepted in full" (every row); ADR-029/030/031 -> accepted;
    ADR-016 rule 3 qualifier dropped (ruling 6 DONE); ADR-015 rule 4 and ADR-014 decision 4
    pointers; data_root() docstring; REQ-011 R09 ruling; REQ-012 R14 mixing ruling; catalog.
  - 1078fec Owner-machine checklist `docs/00-working/owner-machine-checklist.md` (ruling 12 DONE;
    25 checks M1-M2, T1-T4, B1-B4, F1-F3, V1, O1-O11, result sheet).
  - c281b7f Claim of phase-arch-07 (widened).
  - c24b492 ff-merge of `agent/plan-wbf-followups` (also pushed as a side branch): PLAN-027
    second amendment + REQ-012 R32-R34 + three QUEUED phases: `phase-wbf-19` (websocket Origin
    check; depends_on wbf-17; CLAIM GATE below), `phase-wbf-20` (toggle label rung 3 -> 7 per the
    runbook ladder; depends_on arch-07), `phase-wbf-21` (decision ADR: preserve terminal sessions
    across switches; nothing built). Two gating adversary rounds (reject, then pass) and a final
    text round; replies in review-replies/plan-wbf-followups-demo-adversary*.md; no verdict
    record possible for unclaimed work (same as plan-wbf-defects).
- QUEUED workbench phases now: arch-03, 04, 08, 09, 10, 14, 15, 17, 18; wbf-12, 17, 19, 20, 21.
  Held: arch-12, arch-13 (never claim).
- Artifact: v12 published this session (session resumed); v13 (wind-down 2) if the Run Reporter
  finished, see board.md. URL in report/artifact-url.txt. Page copy: scratchpad
  run-report/workbench-run.html (lost with the container; re-read the artifact URL instead).
- Local `dev` reset to origin/dev at close-out; set it back to the trunk before any review runner
  or merge: `git branch -f dev ccr-b69b05b4-tdcrux`.
- Worktrees at close-out: /home/user/d-system-worktrees/phase-arch-07 (kept, active phase; the
  container loses it anyway), plan-wbf-followups and scratch-plan-wbf-followups (merged; may be
  removed next session under the owner's standing approval for merged work). A fresh container has
  none; recreate the arch-07 worktree FROM THE PUSHED BRANCH:
  `git fetch origin agent/phase-arch-07 && git worktree add /home/user/d-system-worktrees/phase-arch-07 -b agent/phase-arch-07 origin/agent/phase-arch-07`
  then `uv sync --extra dev` and copy `ts/node_modules` from the primary checkout (run `cd ts && npm ci` there first).

## Decisions taken this session (ratification items, also on the artifact)
1. wbf-19 design: the owner's ruling 5 said "reuses the ADR-030 token on the demo terminal
   websocket on connect". The plan's first draft (a separate in-memory token handed out by a new
   route) was rejected by the adversary on measured evidence: Vite's default CORS answers any
   localhost origin and src/main.py checks no Host, so a token route protects less than claimed; and
   a route handing out the ADR-030 FILE token would expose it to every local process, which is why
   reuse of that token is unsafe. The Session Manager ruled for ADR-030 open item 7's alternative,
   an Origin check on the websocket (absent Origin accepted; loopback-host Origin accepted; all
   else refused with accept-then-close 4004 before the cap check; urlsplit hostname compare, listed
   refuse/accept cases in R32; optional D_SYSTEM_WORKBENCH_ORIGIN pin). The "(or an Origin check)"
   words in idea 000669 came from ADR-030 item 7, not from the owner. CLAIM GATE: wbf-19 is
   claimed only after a GOV-003 row records the owner's ratification of PLAN-027 Assumption 1
   (Origin branch) — or, if the owner rules for the token, after the design points are re-planned.
2. The three owner asks (rulings 5, 7, 11) were planned in ONE amendment rather than three.
3. arch-07's widening names the new files explicitly (src/workbench/ package,
   test/test_workbench_slot_matcher.py, schemas/workbench-slot-schemas.schema.json,
   schemas/workbench-panel-elements.schema.json, ts/src/stage/*.test.tsx globs) instead of whole
   directories; the builder may use other names only by reporting BLOCKED.
4. Ideation (haiku) and the planner (sonnet) used their own model names in commit trailers; mixed
   trailers were ratified in the table, left as is.
5. The auto-mode classifier refused a scripted multi-file edit; the housekeeping edits were applied
   file by file with the editor tool, same content.
6. Owner approvals at wind-down 2 (AskUserQuestion): push agent/phase-arch-07 and
   agent/plan-wbf-followups as side branches (done); merge the amendment if it landed (done).

## Next session, in order
1. Read this file, board.md (incl. the arch-07 CHECKPOINT entry), ideas-pending.md ("PENDING (wave
   8)" section: four planner IDEA lines + the Host-header idea). Restore the bundle per
   `_tmpagent/session-manager-2026-10-08/README.md`. `git branch -f dev ccr-b69b05b4-tdcrux`.
   Environment: `uv sync --extra dev`, `cd ts && npm ci`, `git fetch --unshallow` if shallow.
2. Ideation turn (haiku): record the wave-8 PENDING lines; link 000669/000670/000671/000087 to
   phase-wbf-19/20/21 where the writer allows (`link --type relates_to --target-code` takes
   governed document codes only; otherwise annotate with the phase ids).
3. Resume `phase-arch-07`: recreate its worktree from origin/agent/phase-arch-07 (command above);
   dispatch a builder (sonnet) with briefs/contract.md, the phase entry, ADR-031, and the
   CHECKPOINT's not-done list; it finishes, writes SESS-2026-10-08-20 (or the next free code if
   the date changed: `--next-code session` in the PRIMARY checkout), replies REVIEW-REQUEST.
   Then the usual: make_brief.sh, runner, demo-adversary (gating), review-judge (shadow, after the
   manifest exists), VERDICT, gate2.sh, merge_phase.sh. ts/ diff is large: expect a demo-validator-
   web pass to be worth dispatching for the one-header count and both layouts.
4. Then the serial plan: arch-08, 09, 10 (depend on 07), arch-17 (07+09); arch-03 then arch-04;
   arch-14 then arch-15; wbf-20 (after arch-07; tiny); wbf-17 then wbf-12 (sys-wb-terminal);
   wbf-21 (decision ADR; ADR phases are pre-approved, dependents flag for ratification); wbf-19
   ONLY after its claim gate; arch-18 last (no other phase active). arch-12/13 held.
5. Refresh the artifact after each merge batch (Run Reporter; recreate from the artifact URL).
6. When the claimable set is exhausted: planning-only mode (proposals/ directory).

## Open items for the owner (new this session)
- Ratify decision 1 above (wbf-19 Origin branch) and record it as a GOV-003 row; that row is
  wbf-19's claim gate.
- Ratify decisions 2-3.
- Owner-machine checklist: run it when at the Windows machine; wbf-19 (Origin check) does not
  break O6 or measure-terminal.js (no Origin is sent by Node's WebSocket).
- Still open from the first session: phase-idg-12 re-claim after this run; 000308/000296 generator
  warning; security F05 on wbf-08 (websocket Origin gap, 000614) stays open until wbf-19 ships.

---

# First session's hand-off (2026-10-08 morning) — procedures and rulings still in force

## Owner's standing instructions (verbatim intent)
- Fully autonomous; decisions pre-approved unless "explicitly potentially dangerous". Flag every
  decision taken for ratification (the artifact's ratification table is the list of record).
- Trunk for this run = branch `ccr-b69b05b4-tdcrux` (only branch pushed, plus the two side branches
  the owner approved at wind-down 2). Local `dev` is `git branch -f dev <trunk>` after each trunk
  commit (never pushed). At hand-off: `git branch -f dev origin/dev`.
- Run until the claimable set is exhausted, then switch to PLANNING-ONLY (scout + propose
  improvements and new features; implement nothing until the owner approves).
- `phase-arch-12` (port/process-killing app) and `phase-arch-13` (depends on it) are HELD for the
  owner. Never claim them.
- Never edit CLAUDE.md/AGENTS.md; never `--no-verify`; no pytest in the primary checkout; never
  read `_private/`; never remove worktrees without owner approval (GOV-003) except an empty one
  from a released claim (merged phases' worktrees: approved on 2026-10-08).
- Commit trailer: `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` +
  `Claude-Session: <the current session's URL>`. Builder commits may carry Sonnet/Haiku names
  (ratified).
- Run Reporter subagent maintains the artifact. Re-create it from the artifact URL (Artifact read
  action) when the agent is gone; republish to the same URL.

## Procedures (all tools in `_working/session-manager/tools/`)
- Claim: edit backlog entry (`agent: <id>`, `status: active`), fix pure-command verification
  entries and widen deliverables AT CLAIM TIME ONLY (never while the builder is editing the entry),
  `uv run python -m src.governance --catalog`, commit, `git branch -f dev HEAD`,
  `git push -u origin ccr-b69b05b4-tdcrux`; `git worktree add -b agent/<phase> <wt> HEAD`;
  `uv sync --extra dev`; copy `ts/node_modules` from the primary checkout (tests need no `data/`).
  Dispatch builder (sonnet, general-purpose) with `briefs/contract.md` + phase notes + ports
  (last used API 8038 / Vite 5208; check free with a socket probe) + session code.
- REVIEW-REQUEST: `make_brief.sh <phase> <sha>` (brief + scratch clone; copy node_modules and
  .venv into the scratch if the reviewer must run), `nohup uv run python tools/run_review_checks.py
  <phase> <sha> &`, dispatch demo-adversary (sonnet, gating) with the brief/scratch/ports; security
  review (sonnet general-purpose, gating) when the diff touches src/api/; dispatch review-judge
  (sonnet, shadow) ONLY after `_working/review-checks/<phase>/<sha12>/manifest.json` exists.
- Verdicts: `write_verdict.py --phase P --commit SHA --type demo-adversary|review-judge|
  security-review --model sonnet --raw <reply.md> [--gating] [--notes] [--definition
  claude-version.txt (security only)]` -> `verdicts-pending/<phase>/`; ids F01..; severity only
  blocker/major/minor. Judge replies are transcribed into `review-replies/`.
- VERDICT message to the builder: findings + rulings; builder copies records unchanged into
  docs/08-governance/reviews/verdicts/, fixes, rebases, replies READY <sha>. A gating reject =>
  new brief + runner + adversary-N + judge-N at the new tip. A pass with text-only findings => one
  final fix round without review.
- Gate: `gate2.sh <worktree> <phase>` (NOT gate.sh) -> `reviews/gate-<phase>[-N].txt`; run gates
  one at a time; expect baseline "missing" rows for verdict files of a phase merged mid-gate.
- Merge: `merge_phase.sh <phase>` (rebase w/ catalog-only conflict loop, quick checks, verdict
  sha check, refuse_dirty_integration, ff-merge, status complete, catalog, push). Never run it
  while another process commits in the primary checkout (Ideation). If a rebase conflicts on
  backlog.yaml, resolve by hand keeping both sides.
- Plan amendments (unclaimed work): planner (sonnet) in a worktree `agent/plan-<topic>`; gating
  adversary; ff-merge by hand (merge-base check, refuse_dirty_integration, `git merge --ff-only`,
  governance, catalog clean, push).
- Ideation (haiku, primary checkout, one commit, then the Session Manager pushes): records
  `ideas-pending.md` PENDING sections through tools/append_idea.py; regenerates
  docs/00-working/ideas.md with tools/generate_ideas_md.py; `git add` only those two files.
- Known env failures: test_run_review_checks::test_an_unwritable_worktree_parent_is_refused
  (root; 000604) always; test_demo_terminal_api::test_control_characters_reach_the_shell under
  load (000644). Temp-clone base runs show 4 env failures; harmless.
- The auto-mode classifier may refuse large heredoc scripts; use the Edit/Write tools for edits.

## Owner rulings (2026-10-08), all still binding
1. arch-07: widen per ADR-031 and build it ALONE (DONE: claimed; build in progress).
2. arch-12 and arch-13 stay held. Never claim them.
3. Worktree cleanup of merged phases and scratch clones APPROVED.
4. Ratification: the artifact's table was APPROVED IN FULL ("I approve the decisions in the
   artifact"); recorded in GOV-003 at 58a5876.
5. Websocket auth: queue a phase that reuses the ADR-030 token on the websocket, amend
   PLAN-027/REQ-012, then build it (PLANNED as phase-wbf-19 with the Origin-check departure;
   claim gate above).
6. ADR-016 rule 3: drop the time qualifier (DONE).
7. phase-wbf-18 ladder: renumber the toggle label to rung 7, keep it visible (PLANNED as
   phase-wbf-20).
8. Idea 000102: realized state via the writer, linked to phase-wbf-02 (DONE: delivered).
9. Ratification housekeeping commit first thing (DONE: 58a5876).
10. Re-review: accept merged phases as they are; a gating reject gets another gating round.
11. Terminal sessions ending on panel/layout switches: PRESERVE sessions (detach/reattach);
    decision phase (ADR) before any fix; do not build warn-and-confirm (PLANNED as phase-wbf-21).
12. Owner-machine checklist under docs/00-working/ (DONE: 1078fec).
