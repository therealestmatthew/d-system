---
schema_version: 1
id: doc-session-build-batch-1
code: SESS-2026-09-16-12
title: Build batch 1 completed under the coordinator pack
kind: session
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-realization, sys-backlog, sys-governance]
depends_on: [doc-build-coordinator, doc-coordinator-protocol, doc-backlog-decisions, doc-session-corpus-status-flag, doc-session-portable-workflows-ported, doc-session-session-type-taxonomy, doc-session-realization-role-contracts, doc-session-stopgap-triage-dispatch]
---

# Build batch 1 completed under the coordinator pack

First run of the build coordinator pack ([PROMPT-036](../02-prompts/PROMPT-036-build-coordinator.md)),
coordinator `agent-build`, dispatching Sonnet agents per the cost protocol (`GOV-008`). This is the
batch record; each phase has its own session record.

## Outcome

All five batch-1 phases completed, integrated and marked complete, each under `GOV-003`'s three
conditions (green verification with captured output, adversarial review resolved, owner-approved
integration): the corpus status filter (`phase-part-02`, `SESS-2026-09-16-07`), workflow
portability (`phase-port-02`, `SESS-2026-09-16-08`), the session type taxonomy (`phase-ses-01`,
`SESS-2026-09-16-09`), the pipeline role contracts (`phase-irs-03`, `SESS-2026-09-16-10`) and the
stopgap triage dispatch (`phase-irs-01`, `SESS-2026-09-16-11`). None skipped, none blocked.
Close-out state of `dev`: governance OK (31 systems, 272 documents, 278 phases), pytest 629
passed, no batch worktree or branch left behind.

## Spend posture (per GOV-008)

- Fix cycles: `phase-part-02` 0, `phase-port-02` 0, `phase-ses-01` 1, `phase-irs-03` 1,
  `phase-irs-01` 2 (cap reached, all findings resolved within it).
- No Opus escalation. All dispatches Sonnet; roughly 22 agent dispatches total (5 recon,
  1 blocker resolver, 5 creators, 4 fix cycles, 4 validators, 4 adversaries... one validator run
  per phase plus one FAIL re-covered by a fix and adversary re-attack).
- Wall clock about 3.5 hours; the coordinator finished with the large majority of its context
  budget unused. Five phases per batch is realistic evidence-backed sizing.

## Evidence the first run was asked to produce

**Batch size:** five phases fit one coordinator session with ample margin; the binding variable is
fix cycles, not phase count. Six is plausible for documentation-heavy batches.

**Where the unit run met reality (pack defects to fold into PROMPT-036, decided by the owner):**

1. The hard boundary "No `next_up` edits" collides with the governance validator, which requires a
   completed phase to be removed from `next_up`; `session-close.md` sanctions that removal as part
   of the completion edit. The pack's step 9 should say so explicitly.
2. A verification list can contain a judgment item ("read the taxonomy and confirm...") that the
   coordinator's context discipline forbids it to perform; this run delegated such items to the
   validator and adversary and recorded that interpretation.
3. Phase declarations can be invalidated by an earlier phase in the same batch: `phase-irs-03`
   declared `.claude/agents/` but `phase-port-02` had just made one of those files generated, so
   the real edit landed in `agent-workflows/` — a ripple the declarations could not have named in
   advance. The adversary flagged it; it was accepted as forced.
4. `--next-code` kind names are exact (`requirement`, not `req`); one creator lost a turn to this.
5. An untracked, `info/exclude`-hidden local file at a newly tracked path (`.codex/agents/
   idea-triage.toml`) let the merge overwrite it silently where a plain clone hard-fails; the
   obsolete exclude line was removed after the merge.

## Decisions filed

All owner decisions were answered in-run (batch-open scoping and placement rulings; GOV-014's two
unsourced defaults accepted; per-phase merge approvals, with a conditional pre-approval covering
the last two phases). `_working/build-b1/decisions.md` holds the log; nothing remains open.
