# HANDOFF — Session Manager, workbench run 2026-10-08

Read this first after a context reset. Then `board.md` (event log, newest at the bottom), then
`ideas-pending.md`, then the artifact URL in `report/artifact-url.txt`.

## Owner's standing instructions (verbatim intent)
- Fully autonomous; decisions pre-approved unless "explicitly potentially dangerous". Flag every
  decision taken for ratification (the artifact's ratification table is the list of record).
- Trunk for this run = branch `ccr-b69b05b4-tdcrux` (only branch ever pushed). Local `dev` is
  `git branch -f dev <trunk>` after each trunk commit (never pushed). At hand-off:
  `git branch -f dev origin/dev`.
- Run until the claimable set is exhausted, then switch to PLANNING-ONLY (scout + propose
  improvements and new features; implement nothing until the owner approves).
- `phase-arch-12` (port/process-killing app) and `phase-arch-13` (depends on it) are HELD for the
  owner. Never claim them.
- Never edit CLAUDE.md/AGENTS.md; never `--no-verify`; no pytest in the primary checkout; never
  read `_private/`; never remove worktrees without owner approval (GOV-003) except an empty one
  from a released claim.
- Commit trailer: `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` +
  `Claude-Session: https://claude.ai/code/session_01RtMnXEnatV62SdHgZTaA6z`. Some builder commits
  carry Sonnet/Haiku names; a history rewrite was refused by the permission classifier; left
  as is; listed for the owner.
- Run Reporter subagent maintains the artifact (v8 now). Send it `UPDATE ...` via SendMessage
  (agent id in board.md line "Run Reporter"); if the agent is gone, re-create from
  `report/` (page file in the scratchpad `run-report/workbench-run.html`; URL in
  `report/artifact-url.txt`; republish to the same URL).

## State at hand-off (trunk f8e298a, pushed; local dev reset to origin/dev)
- 18 phases complete: arch-02, 05, 06, 11, 16; wbf-01, 02, 03, 04, 05, 06, 07, 08, 13, 14, 15, 16, 18.
- NO active phase. Worktree cleanup DONE (owner-approved): /home/user/d-system-worktrees is empty;
  `make_brief.sh` recreates a scratch clone per review; create phase worktrees per the Claim step.
- Local `dev` was reset to origin/dev at close-out; set it back to the trunk
  (`git branch -f dev ccr-b69b05b4-tdcrux`) before running the review runner, which reads the
  backlog from local `dev`.
- phase-wbf-02 MERGED at f8e298a (two gating rounds + security review); phase-arch-16 MERGED at 1f025db.
- QUEUED workbench phases: arch-03, 04, 07, 08, 09, 10, 14, 15, 17, 18; wbf-12, 17.
  Held: arch-12, arch-13.
- Serial plan (system/path overlaps force it): after wbf-02 and arch-16 merge ->
  1. `phase-arch-07` ALONE, re-claimed WITH ADR-031's widening (see board entry "arch-07
     BLOCKED"): systems + sys-demo-stage, sys-wb-terminal, sys-wb-notes, sys-wb-explorers,
     sys-wb-viewer, sys-ui; deliverables + StagePage.tsx, TerminalRegion.tsx,
     HtmlViewerRegion.tsx, OverviewRegion.tsx, FileBrowserRegion.tsx, explorer/ExplorerRegion.tsx,
     NotesStripRegion.tsx, ts/src/stage/ region tests, _data/workbench/, schemas/
     workbench-layout.schema.json + new schemas, test/test_workbench_layout_schema.py,
     test/test_workbench_fit_contracts.py, new pair-test module, ts/vite.config.ts (only if
     fetched). The governance hook refuses the widening while ANY phase sharing those paths or
     systems is active, so claim it only when nothing else is active. Ratification item.
  2. then arch-08, 09, 10 (depend on 07), arch-17 (07+09); arch-03 then arch-04; arch-14 then
     arch-15; wbf-17 then wbf-12 (both sys-wb-terminal); arch-18 last (edits backlog.yaml and
     33 docs; must run with no other active phase).
- Session record codes: trunk has SESS-2026-10-08-10..16; branches hold 17 (arch-16),
  18 (wbf-14, merged), 19 (wbf-02). Tell the next builder to use 20 (`--next-code` in a
  worktree returns a taken number).

## Procedures (all tools in `_working/session-manager/tools/`)
- Claim: edit backlog entry (`agent: <id>`, `status: active`), fix pure-command verification
  entries and widen deliverables AT CLAIM TIME ONLY (never while the builder is editing the entry),
  `uv run python -m src.governance --catalog`, commit, `git branch -f dev HEAD`,
  `git push -u origin ccr-b69b05b4-tdcrux`; `git worktree add -b agent/<phase> <wt> HEAD`;
  `uv sync --extra dev`; copy `data/` and `ts/node_modules` from a sibling worktree.
  Dispatch builder (sonnet, general-purpose) with `briefs/contract.md` + phase notes + ports
  (last used API 8037 / Vite 5207; check free) + session code.
- REVIEW-REQUEST: `make_brief.sh <phase> <sha>` (brief + scratch clone; copy node_modules and
  .venv into the scratch), `nohup uv run python tools/run_review_checks.py <phase> <sha> &`,
  dispatch demo-adversary (sonnet, gating) with the brief/scratch/ports and the report-file
  instruction; security review (sonnet general-purpose, gating) when the diff touches src/api/;
  dispatch review-judge (sonnet, shadow) ONLY after
  `_working/review-checks/<phase>/<sha12>/manifest.json` exists.
- Verdicts: `write_verdict.py --phase P --commit SHA --type demo-adversary|review-judge|
  security-review --model sonnet --raw <reply.md> [--gating] [--notes] [--definition
  claude-version.txt (security only)]` -> `verdicts-pending/<phase>/`; ids must be F01..;
  severity only blocker/major/minor (map "note" to minor with --notes). Judge replies are
  transcribed from the agent output JSONL into `review-replies/<phase>-review-judge[-N].md`.
- VERDICT message to the builder: findings + rulings; builder copies records unchanged into
  docs/08-governance/reviews/verdicts/, fixes, rebases, replies READY <sha>. A gating reject =>
  new brief + runner + adversary-N + judge-N at the new tip.
- Gate: `gate2.sh <worktree> <phase>` (NOT gate.sh: it masks rebase conflicts and truncates the
  vitest summary) -> `reviews/gate-<phase>[-N].txt`; run gates one at a time (CPU) and expect
  baseline "missing" rows for verdict files of a phase merged mid-gate (timing artefact).
- Merge: `merge_phase.sh <phase>` (rebase w/ catalog-only conflict loop, quick checks, verdict
  sha check, refuse_dirty_integration, ff-merge, status complete, catalog, push). Never run it
  while another process commits in the primary checkout (Ideation). If a rebase conflicts on
  backlog.yaml, resolve by hand keeping both sides.
- Ideation (haiku, primary checkout, one commit, then push): records `ideas-pending.md`
  PENDING sections through tools/append_idea.py; regenerates docs/00-working/ideas.md with
  tools/generate_ideas_md.py. PENDING NOW: "wave 7" section (arch-16 F13, wbf-02 x5, wbf-14
  short-viewport trigger).
- Known env failures: test_run_review_checks::test_an_unwritable_worktree_parent_is_refused
  (root; 000604) always; test_demo_terminal_api::test_control_characters_reach_the_shell under
  load (000644). Temp-clone base runs show 4 env failures; harmless.

## Owner decisions taken at the wind-down (AskUserQuestion, 2026-10-08)
1. arch-07: widen per ADR-031's row and build it ALONE after the reset (first claim of the next
   session, once wbf-02 and arch-16 are merged and nothing else is active).
2. arch-12 and arch-13 stay held. Never claim them.
3. Worktree cleanup APPROVED: remove merged phases' worktrees and all scratch clones
   (`git worktree remove <path>`; keep worktrees of active phases; branches stay). Do it at
   hand-off, after the last merge.
4. Ratification: the owner reviews the artifact's table themselves and will confirm all or name
   adjustments. Record nothing as accepted (no GOV-003 entries) until they say so.

## Open items for the owner (also on the artifact)
- Ratify: REQ-011 R09 live-suite ruling; ADR-030 choices; ADR-031 fix choices; wbf-06 mixing
  ruling + hidden-scrollbar + 100 px image floor; wbf-13 8 px bubble loss; wbf-14 side-above +
  Popover import; wbf-16 CSP:sandbox discriminator; wbf-02 ISO/local badge + header wrap cost;
  arch-16 D1-D5; arch-07 widening; mixed commit trailers; `phase-idg-12` to re-claim for
  batch-004 after this run; worktree cleanup; 000308/000296 generator warning (pre-existing).
- Security F05 on wbf-08 (websocket Origin gap, 000614) left open on purpose.

## Planning-only mode (after the claimable set is exhausted)
A first proposal draft already exists: `proposals/non-defect-workbench-ideas.md` (from the early Ideation/scout turn). Scout `_working/session-manager/scout/*.md` and the ideas 000600-000662 for themes; propose
improvements/new features as a proposal document under `_working/session-manager/proposals/`
(gitignored) and on the artifact; implement nothing until the owner approves.

## Owner rulings at the wind-down, batch 2 (AskUserQuestion, 2026-10-08) — the ratification table on
## the artifact is APPROVED IN FULL ("I approve the decisions in the artifact"). Plus:
5. Websocket auth (ADR-030 item 7, idea 000614): QUEUE A PHASE in the features plan that reuses
   the ADR-030 token on the demo terminal websocket on connect (ADR-014 route owner). Amend
   PLAN-027/REQ-012 with the phase (same pattern as the wbf-12..18 amendment), then build it.
6. ADR-016 rule 3: DROP the time qualifier; "no migration code, ever" stands for all bumps.
7. phase-wbf-18 ladder: RENUMBER THE TOGGLE LABEL to match the runbook ladder (rung 7); keep the
   toggle visible. Small follow-up (idea, then a tiny phase or part of the housekeeping commit if
   the label is a one-liner; it touches ts/, so a phase).
8. Idea 000102: MOVE to the realized state via tools/append_idea.py status, linked to phase-wbf-02.
9. Ratification housekeeping: ONE governance-only commit on the trunk FIRST THING next session,
   before arch-07: GOV-003 acceptance entries for every row of the artifact's table; ADR-029,
   ADR-030 (incl. write_timeout amendment), ADR-031 status -> accepted, ADR-016 -> superseded
   (already reads so); ADR-015 rule 4 "extended by ADR-029" pointer; data_root() docstring;
   ADR-014 decision 4 "extended by ADR-030" pointer; annotate idea 000087; drop the ADR-016
   rule 3 qualifier; REQ-011 R09 ruling noted; mixing ruling (all text or all images) recorded
   in REQ-012 (idea 000647); regenerate the catalog. Quick checks only (governance, pytest
   governance/backlog/review_verdict tests, ruff); no builder phase.
10. Re-review: ACCEPT merged phases as they are; keep the rule "a gating reject gets another
    gating round".
11. Terminal sessions ending on panel/layout switches (D1; ideas 000651/000652): the owner wants
    PRESERVE SESSIONS ACROSS SWITCHES (detach/reattach). This reopens ADR-014 decision 4 and
    ADR-030 item 3 (no detach). Capture as an idea now (next Ideation), then plan a decision
    phase (ADR) before any fix phase; do not build warn-and-confirm.
12. Owner-machine checks: write ONE checklist document under docs/00-working/ (ungoverned, ADR-010)
    listing every check with source phase, what to do, what to look for, result column: Windows
    secondary-slot default, pre-migration browser profile (arch-02), ConPTY + token file mode
    (ADR-030), bookmark routes on Windows paths, CMD/PowerShell fit (REQ-037), R31 viewer-toggle
    click (wbf-18), audit O1..O11 (arch-16, copy from the audit's section 8).

## Next session, in order
1. Read this file, board.md, ideas-pending.md. `git status` clean; trunk = origin/ccr-b69b05b4-tdcrux.
2. (done) phase-wbf-02 merged. Set local dev to the trunk: `git branch -f dev ccr-b69b05b4-tdcrux`.
3. Ideation turn: record ideas-pending.md "PENDING (wave 7)" + the new asks from rulings 5, 7, 11, 12.
4. Housekeeping commit (ruling 9). Push.
5. Owner checklist document (ruling 12) in the same or a following commit. Push.
6. Claim arch-07 alone with ADR-031's widening (ruling 1); build; review; merge.
7. Then the serial plan (arch-08/09/10/17; arch-03/04; arch-14/15; wbf-17/12; the new websocket
   phase after the plan amendment; arch-18 last). arch-12/13 held.
8. Refresh the artifact after each merge batch (Run Reporter agent, or recreate it).
