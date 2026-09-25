---
schema_version: 1
id: doc-session-plugin-backlog-sessions
code: SESS-2026-09-25-05
title: Idea-realization plugin backlog check, ready report and session skills
kind: session
status: active
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-backlog]
depends_on: [doc-idea-realization-plugin-backlog-sessions]
---

# Idea-realization plugin backlog check, ready report and session skills

## Phase

`phase-plug-04` — Backlog check and ready report, plus the session-start, checkpoint and
session-close skills (and, by the owner's amendment, the backlog skill).

## Verification

Run in `../d-system-worktrees/phase-plug-04` on `agent/phase-plug-04`, Claude Code 2.1.280.

```text
$ cd plugins/idea-realization && uv run pytest
FAILED test/test_scripts_portable.py::test_scripts_run_against_a_temporary_root
1 failed, 285 passed

$ claude plugin validate plugins/idea-realization --strict
✔ Validation passed

$ uv run python tools/check_no_private_content.py   # changes staged
check_no_private_content: OK (972 tracked files, 0 identifiers checked)

$ uv run python -m src.governance
Governance OK: 43 systems, 363 documents, 32 memories, 318 backlog phases
```

The one failure is outside this phase's files: `test_scripts_portable.py` (from `phase-plug-01`)
copies `scripts/` and `.claude-plugin/` but not `schemas/`, and the backlog check reads
`schemas/backlog.schema.json`, so `check.py` exits 1 in the copy with "No such file or directory".
The Session Manager reported that the fix, copying `schemas/`, lands with `phase-plug-02`; raised
with the Session Manager this session.

Loading check: `claude -p … --plugin-dir …/plugins/idea-realization` from a scratch repository
listed `idea-realization:backlog`, `catalog`, `checkpoint`, `doctor`, `next-code`, `plan-check`,
`prerequisites`, `scaffold`, `session-close`, `session-start`.

Unchanged-logic port (owner ruling this session: shown by diff, not by a cross-tree test, which
would break `REQ-031` R21). `diff src/governance/backlog.py plugins/idea-realization/scripts/backlog.py`
changes 30 lines: the PEP 723 header and module docstring; three comments and docstrings that
named phase ids, a date or the working agreement's filename, rewritten generically; and one logic
change, the guard `if "decision_record" in catalog:` around the existing decision-record rule,
required by the owner's ruling that `decision_record` is optional. `regression.py`'s logic is
unchanged except that the backlog path, the decisions path and the second base are parameters
(`check`, `audit`, `bases(integration_branch)`) instead of the constants `BACKLOG_PATH`,
`DECISIONS_PATH` and `BASES`.

## Acceptance

- Two active phases sharing a system fail check naming both; the ported tests pass — Met
  (`test_two_active_phases_sharing_a_system_fail_naming_both` runs `check.py` and reads
  `<first>/<second>: concurrent phases share system sys-core`; the 26 ported backlog tests and the
  ported regression tests pass).
- A differently named decisions document is found through `decision_record`; no `decision_record`
  passes check and the regression check reports it did not run; an unresolved `decision_record`
  fails — Met (`test_the_real_check_reports_a_regression_and_honours_the_named_decisions_document`,
  `test_no_decision_record_passes_and_says_regression_did_not_run`,
  `test_a_decision_record_resolving_to_no_document_fails`).
- `checkpoint` names the complete status only in a prohibition; `session-close` states the three
  conditions; no skill names the integration branch — Met (`test_checkpoint_names_the_complete_
  status_only_to_forbid_it`, `test_session_close_states_the_three_completion_conditions`,
  `test_no_skill_names_an_integration_branch`).
- The backlog skill has no claim command; the active-status line appears only in a prohibition —
  Met (`test_the_backlog_skill_never_claims`).
- The R02 check passes — Met (`test_plugin_names_no_source_instance` passes).

The verification list is not all green: the plugin suite has the one failure above.

## Backlog

`status: active`, `agent: agent-builder-b`. `next_action`: rebase onto the integration branch once
`phase-plug-02` lands the portable-test fix, re-run the plugin suite and send READY; the review is
done and dispositioned. `session: doc-session-plugin-backlog-sessions`; `completion_evidence` cites
the backlog script, check module, regression script, schema, the two test files and this record;
`result` records the suite's one outside failure and the review outcome.

## Unresolved

- The portable-test dependency above.
- **Schema: `items` may be empty** (`minItems: 0`, the source requires 1) — owner ruling this
  session, after the review raised it. The scaffold's backlog seed is `items: []`; with the source's
  rule a freshly scaffolded repository fails its own check. `test_the_scaffolded_seed_passes_the_check`
  covers it.
- **`REQ-031` R24's verification says each thin skill "names exactly one script"; the `backlog`
  skill names two** (`check.py` and `cli.py`), because R24 itself says it "runs `check` and
  `ready`". Owner ruling this session: amend R24's verification to "Each skill file names exactly one
  script, except `backlog`, which runs `check` and `ready`; …". The amendment is outside this
  phase's files; handed to the Session Manager in READY.
- **PLAN-048.04's compare test** was not written (owner ruling this session), because a plugin test
  reading this repository's `src/governance/backlog.py` breaks R21. The plan's decision text still
  describes it.
- **The confidential-directory refusal is not ported.** The source's `public_path` refuses
  declared paths through the confidential directory; the plugin cannot name it (R02), so
  `repository_path` refuses only absolute paths, `..`, symlinks, `.git`, `.venv` and
  `node_modules`. The ported test for it now checks `.git/config` and `../elsewhere`.
- **Planner call (PLAN-048.04's open question):** `ready` prints the stale-claim signal, as the
  source's report does; it is one column of the same table.

## Review

Independent adversarial review by a `demo-adversary` agent, given the scope, acceptance,
verification and deliverables, the range `dev...HEAD` (d43f47c, 3c7e51e), this record, the sources
ported and the owner's rulings. It reached its turn limit once and was asked to finish and report.
It re-ran the plugin suite, `validate --strict`, the private-content check and governance, diffed
both ported scripts and the schema against their sources, and grepped the skills. Its report,
condition by condition:

1. Two active phases sharing a system; ported tests — **Met.** "285 passed, 1 failed … the
   pre-known peer-owned failure … the port is unchanged in logic except: PEP 723 header, doc
   rewording that strips phase ids/`AGENTS.md`/dates for R02, and the one `if "decision_record" in
   catalog:` guard around the existing rule — matching the session record's own diff claim, which I
   verified rather than trusted."
2. `decision_record` resolution — **Met.** "resolves the decisions path from
   `scanned.documents[record]["path"]`, never a literal filename … all exist and passed."
3. Checkpoint, session-close, branch literals — **Met.** "`status: complete` … appears once, at line
   16, inside 'Writing `status: complete` here is forbidden in every case…' … no 'owner-only'
   framing anywhere in `skills/` … Grepped all four skills for `\bdev\b|\bmain\b` — no hits."
4. Backlog skill never claims — **Met.** "only one hit, line 9, 'Setting `status: active` or an
   `agent` on any phase is forbidden in this skill'."
5. R02 — **Met**, "with the one pre-declared, non-blocking exception": `test_scripts_portable.py`
   "never [copies] `schemas/` … This is the only failure; nothing else fails. Confirmed."

It confirmed no file outside the deliverables was touched. It stated what it did not check: no
adversarial probe of `repository_path`'s symlink and escape handling beyond reading it, and no probe
of a `decision_record` that resolves to a document of the wrong kind ("inspect_backlog flags it, but
regression.py still runs against it; I judged this immaterial").

Findings, as reported, and their disposition:

1. **minor** — `items.minItems` loosened from 1 to 0 "without an explicit owner ruling on record for
   that specific change". **Accepted by the owner** this session (Unresolved).
2. **minor** — R24's "names exactly one script" is "technically violated by the `backlog` skill …
   required by R24's own prose … the requirement text is internally inconsistent, not the
   implementation". **Accepted by the owner, with R24's wording to be amended** (Unresolved).

"No blocking or major findings survived the attack."

## Decisions

The owner approved the claim and ruled at the claim question that the child plan's cross-tree
compare test is dropped, because a plugin test reading this repository's source breaks R21; the
diff in Verification stands in for it and the reviewer re-derived it. `decision_record` is optional
by the owner's earlier ruling; after the review the owner also ruled `items` may be empty, and that
R24's verification is amended rather than the `backlog` skill cut to one script.

The builder's calls: `backlog.py` keeps the source's logic line for line apart from the
`decision_record` guard; `checks/backlog.py` holds the file reading, the schema check and the
document-scan wiring, and refuses to check the backlog while the document tree has errors rather
than reporting every phase's plan and owner as unknown; regression warnings and the "did not run"
note go to standard error so they never change the exit code; the skills read the integration
branch and worktree directory by running `paths.py` with the option assignments, so no skill holds
a branch name; the ported tests build phase ids and dates at run time so the plugin's R02 check
stays green over its own tests.

## Corrections

- The first attempt to port `regression.py` by scripted text replacement failed on a docstring
  mismatch; it was rewritten directly from the source.
- The first test-porting script's function-removal pattern deleted 25 of 29 tests; replaced with a
  line-based removal and the count checked (26 kept, the three that read this repository dropped).
- A docstring naming a phase id was turned into an f-string by the porting script, so it was no
  longer a docstring; fixed by hand.
- `session-start` first told the agent to `git switch` the primary checkout while also saying it is
  never switched; it now confirms the branch and stops if it is wrong.
- A `SESS-` literal in a test fixture tripped the R02 check; now built at run time.

## Left undone

- The plugin suite's one failure waits on `phase-plug-02`'s fix to `test_scripts_portable.py`; the
  Session Manager ruled this phase rebases after that merge.
- R24's verification wording is the Session Manager's to amend.
- The phase stays `active` until the owner approves the merge; completion follows on the
  integration branch.
