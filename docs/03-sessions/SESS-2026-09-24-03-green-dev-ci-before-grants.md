---
schema_version: 1
id: doc-session-green-dev-ci-before-grants
code: SESS-2026-09-24-03
title: Green dev CI before each primary-checkout grant
kind: session
status: active
owner: repository-owner
created: '2026-09-24'
updated: '2026-09-27'
systems: [sys-governance, sys-gov-docs]
depends_on: [doc-deterministic-guards]
---

# Green dev CI before each primary-checkout grant

## Phase

`phase-grd-02` — Green dev CI before each primary-checkout grant.

The work was built on 2026-09-24 under claim `2dd56d4`. The claim was released at `19f3e81` for the
plugin build and re-claimed on 2026-09-27 at `270e688` (owner approval in the builder's session).
The branch was then rebased onto `dev` at `270e688`, 153 plugin-build commits and three idea/doc
commits past the original base.

## Verification

Run in the worktree `../d-system-worktrees/phase-grd-02` on `agent/phase-grd-02`, after the review
fix and the last 2026-09-27 rebase, onto `dev` at `16b3331`.

```text
$ uv run pytest test/test_check_dev_ci.py
27 passed, 1 warning
```

```text
$ uv run python tools/check_dev_ci.py
unknown: dev is not pushed (dev is 270e688, origin/dev is 0131889); push dev, then wait for its CI run
exit 2
```

This is the live run against `dev`'s head. `dev` is deliberately unpushed today: the owner is on
mobile and holds the merge until they are at the terminal and `dev` is pushed. Exit 2 with the
not-pushed message is the tool's specified answer for this state. On 2026-09-24, with `dev`
pushed, the same command printed
`green: CI succeeded for 2dd56d4: https://github.com/therealestmatthew/d-system/actions/runs/35986703694`
and exited 0.

Exit 1 against the real `gh`, on a commit from the six-day red period (review finding 8 of the
pre-claim review), re-run on 2026-09-27:

```text
$ uv run python tools/check_dev_ci.py --commit 024443c
red: CI failure for 024443c: https://github.com/therealestmatthew/d-system/actions/runs/35876027675
exit 1
```

```text
$ uv run python -m src.governance --catalog
393 documents — adr: 21, architecture: 12, governance: 17, operation: 22, plan: 80, prompt: 40, requirement: 33, session: 168.
$ uv run python -m src.governance
Governance OK: 43 systems, 393 documents, 34 memories, 326 backlog phases
$ git diff --exit-code docs/08-governance/catalog.md
exit 0
$ uv run ruff check src/ test/ tools/check_dev_ci.py
All checks passed!
$ uv run mypy src/ tools/check_dev_ci.py
Success: no issues found in 47 source files
$ uv run ruff check src/ test/
All checks passed!
$ uv run mypy src/
Success: no issues found in 46 source files
```

Full suite, not in the verification list but run for the merge gate:

```text
$ uv run pytest
1147 passed, 1 warning
```

## Acceptance

- Unit tests over recorded `gh run list` JSON for the five cases — **Met.** `test_success_at_head_exits_0`,
  `test_failure_at_head_exits_1_naming_the_run`, `test_in_progress_exits_2`,
  `test_run_only_for_an_older_commit_exits_2` and `test_gh_error_exits_2` pass; every payload was
  recorded live on 2026-09-24 (the test module's docstring names the command).
- Run against the live repository, the tool's output is recorded in the session record — **Met.**
  `## Verification` above: exit 2 (dev not pushed) at `dev`'s head today, exit 0 at `dev`'s head on
  2026-09-24, and exit 1 with the run URL for `024443c`.
- The `GOV-017` and `PROMPT-037` diffs show the grant rule and the meaning of exit 2 — **Met.**
  `GOV-017`'s lock section gains the push-before-`TURN DONE` rule and the green-CI grant rule with
  exits 0, 1 and 2; `PROMPT-037` contract item 1 gains the push step and the same rule in short
  form. `REQ-028` R06 is amended to the rulings.

## Backlog

`status: active`. `next_action`: review done and its findings resolved; READY sent; the merge is
held by the owner until they are at the terminal and `dev` is pushed. `session`,
`completion_evidence` and `result` are recorded as interim evidence; `/session-close` does not
complete the phase before the merge.

## Unresolved

- Sessions already running hold the old `PROMPT-037` item 1 text. Whether the Session Manager
  re-sends the amended item or uses it only after a `/clear` is its operating choice.
- The merge is held (owner, 2026-09-27): this phase's own rule requires `dev` pushed before
  `TURN DONE` and a green CI before a merge grant, and neither can run while `dev` is unpushed.

## Review

Independent `/session-close` review, 2026-09-27, by a `demo-adversary` sub-agent over
`dev...agent/phase-grd-02` at `4f1cf42`. The 2026-09-24 review did not return before the reset and
was lost; this one replaces it. Its report, verbatim:

> ## Acceptance conditions
>
> 1. **"Unit tests over recorded gh run list JSON: success (0), failure (1), in progress (2), older-commit-only (2), gh error (2)."** — **Met.** Ran `uv run pytest test/test_check_dev_ci.py -q`: `27 passed`. The five named cases exist as `test_success_at_head_exits_0`, `test_failure_at_head_exits_1_naming_the_run`, `test_in_progress_exits_2`, `test_run_only_for_an_older_commit_exits_2`, `test_gh_error_exits_2` (`test/test_check_dev_ci.py:111-138`), plus 22 more covering filters, `--wait`, `--commit`, and `gh`/`git` failure modes. Fixtures are annotated as recorded live `gh` output on 2026-09-24 and I independently verified one against the live API (`gh run view 35876027675` returns exactly the `conclusion/headSha/headBranch/event/url` the `FAILURE_OLDER` fixture claims) — genuinely recorded, not invented.
>
> 2. **"Run against the live repository, the tool's output is recorded in the session record."** — **Met, but the record is stale for everything except the two commands it names.** I independently re-ran both:
>    - `uv run python tools/check_dev_ci.py` → `unknown: dev is not pushed (dev is 270e688, origin/dev is 0131889); push dev, then wait for its CI run`, exit 2 (dev intentionally unpushed today — matches the dispatch's stated context, not a defect).
>    - `uv run python tools/check_dev_ci.py --commit 024443c` → `red: CI failure for 024443c: https://github.com/therealestmatthew/d-system/actions/runs/35876027675`, exit 1 — confirmed live against a red-period commit as review fix 8 required.
>    These two match what's already written in `docs/03-sessions/SESS-2026-09-24-03-green-dev-ci-before-grants.md`. But that file's broader `## Verification` block is the **pre-rebase** capture (governance "347 documents", `pytest` "1096 passed, 1 skipped") — it was never refreshed even though the dispatch says "the builder will refresh it" and reports fresh post-rebase numbers (391 documents, 1142 passed) that never made it into the file. See Finding 1.
>
> 3. **"The GOV-017 and PROMPT-037 diffs show the grant rule and the meaning of exit 2."** — **Met.** `GOV-017`'s lock section (`docs/08-governance/GOV-017-multi-session-coordination-protocol.md:107-123`) states the push-before-`TURN DONE` rule, the exit 0/1/2 grant rule, and the idea/batch exemption. `PROMPT-037`'s contract item 1 (`docs/02-prompts/PROMPT-037-session-manager-starter-messages.md:63-75`) states the same in short form. `REQ-028` R06 and its "what R06 is not" note are amended to match (`docs/06-requirements/REQ-028-deterministic-guards.md:81,97-98`).
>
> ## Owner rulings / pre-claim review fixes
>
> - **Poll ~10 min via `--wait 600`, then ask owner** — Implemented. `check_with_wait` (`tools/check_dev_ci.py:151-165`) polls every `--interval` (default 30s) until 0/1 or the deadline; `OPS-025` names `--wait 600` as the Session Manager's command. Verified with `FakeClock`-based tests (`test_wait_polls_until_green`, `test_wait_stops_at_red`, `test_wait_times_out_with_2`) — timing arithmetic checked by hand and it's correct (loop only sleeps again if a full interval still fits before the deadline; a 0-wait call queries exactly once).
> - **Gate only claim/dryrun/merge, not idea/batch** — Implemented in `GOV-017`, `PROMPT-037`, `OPS-025`, and `REQ-028` R06's updated text, all consistently.
> - **Outcome mapping (success=0; failure/timed_out/startup_failure=1; cancelled/skipped/neutral=2)** — Implemented exactly (`tools/check_dev_ci.py:33-35` `GREEN`/`RED` sets), and unit-tested via `test_conclusion_mapping` including an unrecognised conclusion (`action_required` → 2, correctly fails closed).
> - **Push dev before TURN DONE, checked by Session Manager (origin/dev == dev)** — Implemented in `GOV-017:110-113` and `PROMPT-037` item 1 (`push` step added to the turn sequence), and the tool itself distinguishes "dev is not pushed" from "CI not finished" (`resolve_commit`, `tools/check_dev_ci.py:57-70`; `test_unpushed_dev_exits_2_without_asking_gh` confirms `gh` is never called in that case).
> - **Review fix 5 (query specifics: `--workflow ci.yaml`, `--commit $(git rev-parse dev)`, headBranch==dev, event==push)** — Implemented exactly (`tools/check_dev_ci.py:104-107,127-129`), confirmed against real `gh run list --help` (`-c/--commit`, `-w/--workflow` both exist, and `ci.yaml` is the actual workflow filename in `.github/workflows/`).
> - **Review fix 7 (OPS code via `--next-code`)** — `OPS-025` allocated cleanly; catalog count moved 389→391 documents (operation 21→22, session 167→168), no collision.
> - **Review fix 8 (live exit-1 run recorded)** — Confirmed live myself above; matches the session record's earlier capture.
> - **Review fix 1 (exit-1 grant path) and fix 2 (push-dev rule + distinct message + test)** — both implemented as described above.
>
> ## Verification commands (run in the worktree, not the primary checkout)
>
> - `uv run pytest test/test_check_dev_ci.py -q` → `27 passed` (matches claim).
> - `uv run python -m src.governance --catalog` → `391 documents...`; `git diff --exit-code docs/08-governance/catalog.md` → exit 0 (no diff, catalog already committed correctly).
> - `uv run python -m src.governance` → `Governance OK: 43 systems, 391 documents, 34 memories, 323 backlog phases`.
> - `uv run ruff check src/ test/ tools/check_dev_ci.py` → `All checks passed!`
> - `uv run mypy src/ tools/check_dev_ci.py` → `Success: no issues found in 47 source files`.
> - `uv run python tools/generate_tool_docs.py` → `21 tool document(s) current` — the OPS-025 generated tool-reference block is not stale, and `--help` output matches the doc's flag table exactly.
> - Did not run the full `uv run pytest` suite per instruction (only one run per worktree at a time, already run by the builder).
>
> ## Findings
>
> 1. **Fix — session record and backlog `result` field carry pre-rebase numbers, contradicting the claim that they were refreshed.** `docs/03-sessions/SESS-2026-09-24-03-green-dev-ci-before-grants.md` `## Verification` (governance "347 documents... 35 systems... 32 memories, 304 backlog phases", full `pytest` "1096 passed, 1 skipped") and `docs/09-backlog/backlog.yaml`'s `phase-grd-02.result` ("verification green in the worktree (1096 passed, 1 skipped)") both predate the rebase — the branch now sits on top of far more merged work (391 documents, 43 systems, 34 memories, 323 backlog phases per my own run above). The dispatch prompt states the builder obtained fresh post-rebase numbers today (test 27 passed; governance 391; full pytest 1142 passed) but those numbers are not in either file on disk. Anyone reading the session record or the backlog entry as merge evidence sees stale, now-wrong counts. Minimal fix: update both to the post-rebase figures before sending READY.
>
> 2. **Note — `check_with_wait`'s timeout message names the requested `--wait` value, not elapsed time.** `tools/check_dev_ci.py:161-163`: on timeout the message is `f"{verdict.message} (still unknown after waiting {wait:g} s)"` using the caller-supplied `wait` (e.g. 600), even though the loop's own guard (`clock() + interval <= deadline`) means actual elapsed time before the last check can be up to one `interval` short of `wait` (confirmed with `test_wait_times_out_with_2`: `wait=100, interval=30` → `clock.now == 90` but message says "waiting 100 s"). Cosmetic only — the exit code and grant behavior are unaffected — but the printed message is not literally true; the owner reading `check_dev_ci.py --wait 600`'s exit-2 message after ~590s of real waiting would see "waiting 600 s" printed early.
>
> 3. **No discrepancies found** in: the `gh` flag usage (`--commit`, `--workflow` both real, verified against `gh run list --help`), the workflow filename (`ci.yaml` matches `.github/workflows/ci.yaml` and `gh workflow list`), the conclusion→exit-code mapping, the `--commit` override's skip of the pushed-dev check, missing-binary handling (`FileNotFoundError` is caught via `OSError` for both `git` and `gh` calls), invalid-JSON/non-list `gh` output handling, the numbering and text integrity of `PROMPT-037`'s contract items (1-10, no gaps/duplication from the two-phase rebase against `phase-grd-01`'s edits to the same document), `REQ-028`'s R06 table row and "what R06 is not" note, and `backlog.yaml` (the diff touches only `phase-grd-02`'s own entry — no other phase's data was disturbed by the rebase).
>
> Net: no blocking findings. Finding 1 (fix-severity) should be closed — refresh the session record's Verification section and the backlog `result` field with the actual post-rebase numbers — before `READY` is sent, since that record is the acceptance evidence a merge reviewer relies on. Finding 2 is cosmetic and does not need to block.

Resolution:

1. **Fixed.** `## Verification` above and the backlog `result` now carry the post-rebase figures.
2. **Fixed.** `check_with_wait` records the start time and prints the time actually waited;
   `test_wait_times_out_with_2` now asserts `waiting 90 s`, and `OPS-025`'s troubleshooting entry
   describes the message as `still unknown after waiting <n> s`, at most `--wait`.

## Decisions

- **The grant gate covers `claim`, `dryrun` and `merge`, not `idea` or `batch`.** The pre-claim
  review argued that an idea or batch status commit cannot spread a red build, and that gating idea
  turns would stop a session from recording the failure. The owner ruled this on 2026-09-24, which
  amends `REQ-028` R06's "before any `GRANTED`"; R06 was edited in this phase and added to its
  deliverables.
- **Exit 2 while CI runs is polled, not escalated at once.** CI takes about three minutes, and
  asking the owner on every grant would move routine waiting onto them. The tool gained `--wait`
  and `--interval`; the Session Manager runs `--wait 600` and asks the owner only after that.
- **Push `dev` before `TURN DONE`, rather than falling back to the last green commit.** A fallback
  would let an untested head through, which is the failure R06 exists to stop. The tool reports an
  unpushed `dev` with its own exit-2 message and never calls `gh` in that case.
- **On red (exit 1), only the fix the owner names is granted**, with the ruling and the run URL
  recorded. Without this the gate had no way out of a red `dev`, because the fix itself needs a
  merge grant.
- **Conclusions other than success and failure**: `timed_out` and `startup_failure` are red;
  `cancelled`, `skipped`, `neutral` and anything unrecognised are unknown. A cancelled run says
  nothing about the code.

## Corrections

- The first checkpoint's `## Verification` block was not refreshed after the 2026-09-27 rebase,
  although the review dispatch described fresh numbers. The review caught it (finding 1) and the
  record now carries the post-rebase run.
- The timeout message printed the requested `--wait` instead of the time waited (review finding 2).
  Fixed in the tool, its test and `OPS-025`.

## Left undone

- **The merge.** The owner holds it until they are at the terminal and `dev` is pushed. Once `dev`
  is pushed, the Session Manager can run the tool this phase built before granting the merge, which
  is the first real use of the gate.
- **The completion edit** (`status: complete`, the completion evidence and `result`) is made on
  `dev` inside the merge turn, with the catalog regenerated by `--catalog` in the same commit, as
  `PROMPT-037` item 4(iii) requires.
- **CI optimisation** is not in this phase. The owner asked for an idea on it (000419).
