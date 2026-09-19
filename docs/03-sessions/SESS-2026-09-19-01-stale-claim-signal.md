---
schema_version: 1
id: doc-session-stale-claim-signal
code: SESS-2026-09-19-01
title: Define the stale-claim signal and report it in --ready
kind: session
status: active
owner: repository-owner
created: '2026-09-19'
updated: '2026-09-19'
systems: [sys-governance, sys-backlog]
depends_on: [doc-concurrency-git-safety]
---

# Define the stale-claim signal and report it in --ready

## Phase

`phase-conc-01` — Define the stale-claim signal and report it in `--ready`.

## Verification

`uv run python -m src.governance`

```
Governance OK: 31 systems, 282 documents, 26 memories, 278 backlog phases
```

`uv run pytest test/test_backlog.py`

```
45 passed, 2 warnings
```

Additionally run (not in the phase's `verification` list, but relevant evidence): `uv run pytest`
— 1 failed, 635 passed. The one failure is `test_ideas.py::test_the_committed_markdown_matches_regenerated_output`,
confirmed pre-existing on `dev` before this session's changes (reproduced against `f08b086` with
this session's diff stashed) — unrelated to `sys-governance`/`sys-backlog` backlog rendering and not
touched by this phase's deliverables.

`uv run python tools/check_no_private_content.py`, run with these changes staged:

```
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (712 tracked files, 0 identifiers checked)
```

Real `--ready` output against this repository's live claims, confirming the signal fires on real
data rather than only on synthetic test fixtures:

```
| Claimed phase | Agent | Locked systems | Stale? |
|---|---|---|---|
| phase-conc-01 | agent-conc | sys-governance, sys-backlog | no |
| phase-lit-07 | agent-lit | sys-research | no evidence: no agent/<phase-id> branch found |
```

## Acceptance

- REQ-013 R01 (a stale claim is reported as a distinct state naming the signal; a live claim in the
  same run is not flagged): **Met**. `test_ready_report_names_the_stale_signal_beside_a_live_claim`
  constructs one live and one stale synthetic claim in the same `render_backlog` call and asserts the
  live row ends `no` while the stale row contains `STALE:` and names the day count. The real `--ready`
  output above shows the same distinction on live repository state, though `phase-lit-07` lands in the
  third ("no evidence") state rather than "STALE" — see Unresolved.
- REQ-013 R02 (the definition uses only evaluable inputs and states explicitly that staleness is
  evidence for the owner, not proof the agent is dead): **Met**. `stale_claim_signal`'s two inputs
  (`days_since_commit`, `worktree_exists`) are both git/filesystem facts with no judgement step
  between measurement and signal name. Its docstring states four separate non-proofs (not proof of
  death, not proof work is missing, not evidence across machines, not authorization to release), and
  `GOV-002-backlog-protocol.md`'s new "The stale-claim signal" section restates this for a human
  reader.
- REQ-013 R03's negative half (grep over `src/governance/` finds no code writing `status: queued`
  over a peer's claim): **Met**. `test_no_governance_code_writes_a_claim_release` greps every `.py`
  file under `src/governance/` for five literal assignment shapes of `status` to `"queued"` and
  asserts none appear; it currently passes because no such code exists anywhere in this phase's diff
  or the pre-existing module.

## Backlog

`phase-conc-01` stays `status: active`, `agent: agent-conc`. `deliverables` gained
`src/governance/__main__.py` (the git-evidence gathering the report needed was not achievable from
`backlog.py` alone, which stays a pure function of its inputs; `GOV-002` already permits updating
proposed deliverable filenames at execution). `next_action` is unchanged from the claim commit — the
threshold-from-history step it named is done — pending the owner's or a peer's review before
integration onto `dev`.

## Unresolved

- **`phase-lit-07` is not flagged `STALE` by this signal**, despite having had no commit on any
  `agent/*` branch matching the `agent/<phase-id>` convention since 2026-09-14 (5 days as of this
  session, against a 2-day threshold). Its real branch is `agent/lit-campaign` and its real worktree
  is `/code/d-system-worktrees/lit-campaign` — neither name follows the `agent/<phase-id>` /
  `../d-system-worktrees/<phase-id>` convention `AGENTS.md` states as a rule. Both of
  `stale_claim_signal`'s inputs are computed by looking up `agent/phase-lit-07` specifically, so
  neither can be evaluated, and the report says so explicitly (`no evidence: no agent/<phase-id>
  branch found`) rather than misreporting `no` (confirmed live) or guessing `STALE`. This is a
  genuine gap in what the signal can see for any claim whose branch was not created per convention;
  closing it would mean correlating a phase to its real branch some other way (recorded in
  `backlog.yaml`, or discovered by content rather than name), which is out of this phase's declared
  scope and deliverables. Left for the owner or the recovery-procedure phase (`phase-conc-04`) to
  weigh — this session did not investigate, and was instructed not to duplicate, whatever a separate
  parallel investigation of `phase-lit-07` itself is doing.
- `test/test_ideas.py::test_the_committed_markdown_matches_regenerated_output` fails on a clean
  checkout of this branch's parent commit, before this session's changes; not investigated further
  since it is outside `sys-governance`/`sys-backlog` and this phase's deliverables.
- This branch has not been rebased onto current `dev` or reviewed for integration; that remains the
  owner's or a peer's call per `AGENTS.md`.
