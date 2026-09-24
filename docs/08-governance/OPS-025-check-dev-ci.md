---
schema_version: 1
id: doc-ops-check-dev-ci
code: OPS-025
title: Check that dev's CI is green before a primary-checkout grant
kind: operation
status: active
owner: repository-owner
created: '2026-09-24'
updated: '2026-09-24'
systems: [sys-governance]
depends_on: [doc-deterministic-guards-requirements, doc-deterministic-guards, doc-multi-session-coordination-protocol]
---

# Check that dev's CI is green before a primary-checkout grant

## Trigger

The Session Manager runs it before every `GRANTED claim`, `GRANTED dryrun` and `GRANTED merge`
([GOV-017](GOV-017-multi-session-coordination-protocol.md)'s primary-checkout lock section and
`PROMPT-037` contract item 1). `idea` and `batch` turns are not gated (owner ruling, 2026-09-24).
It exists because `dev` stayed red for six days while grants continued: reading `gh run list` by
eye did not stop them (`REQ-028` R06, `PLAN-045` D6).

## Command

```bash
uv run python tools/check_dev_ci.py --wait 600
```

`--wait 600` re-checks every 30 seconds (`--interval`) while the result is unknown and stops at the
first green or red, or after 10 minutes. CI took about 2 m 45 s on 2026-09-24, so a grant made just
after a push usually waits that long. Without `--wait` the tool queries once.
`--commit <sha>` checks any commit pushed to `dev` instead of `dev`'s head.

## Expected result

| Exit | Meaning | What the Session Manager does |
|---|---|---|
| 0 | The latest completed `push` run of `ci.yaml` on `dev` for `dev`'s head succeeded | Grant |
| 1 | That run ended `failure`, `timed_out` or `startup_failure`; its URL is printed | No grant, except the turn or merge the owner names as the fix, with the owner's ruling and the run URL recorded |
| 2 | Not known: CI has not finished, the run was `cancelled`, `skipped` or `neutral`, `dev` is not pushed, or `git`/`gh` failed | No grant until the result is known, or the owner rules for that grant |

The tool asks `gh` for runs of one commit, never for "the latest run", and ignores `pull_request`
runs and runs on other branches. The commit is `git rev-parse dev`, so the answer is the same from
a worktree as from the primary checkout.

## Failure and recovery

- **`dev is not pushed`.** Local `dev` and `origin/dev` differ, so CI has not seen the head. The
  lock holder pushes `dev` before sending `TURN DONE` (GOV-017), so this means a turn ended
  without its push. Push `dev`, then run the check again with `--wait`.
- **`still unknown after waiting 600 s`.** CI is slow or queued. Ask the owner whether to wait
  longer or grant; do not grant on an older green commit, which would let an untested head through.
- **Red.** The run URL names the failing job. Only the fix is granted, on the owner's ruling. An
  `idea` turn to record the failure is not gated.
- **`gh failed`.** Usually authentication (`gh auth status`) or the network. The result is unknown,
  so exit 2 applies until `gh` answers.

<!-- generated:tool-reference:start -->

### Reference: `tools/check_dev_ci.py`

Report whether CI passed on `dev`'s head commit, so the Session Manager grants on a green `dev`.

The Session Manager runs this before it grants a `claim`, `dryrun` or `merge` turn in the primary
checkout (GOV-017's lock section, PROMPT-037 item 1):

    uv run python tools/check_dev_ci.py                 # dev's head, one query
    uv run python tools/check_dev_ci.py --wait 600      # poll until green or red, up to 10 minutes
    uv run python tools/check_dev_ci.py --commit <sha>  # any commit pushed to dev

It asks `gh run list --workflow ci.yaml --commit <sha>` for the runs of that commit and keeps
only `push` runs on the `dev` branch whose head is exactly that commit, so a `pull_request` run
or a second workflow cannot satisfy the check. It then reads the most recent completed run:

- exit 0: that run's conclusion is `success`;
- exit 1: it is `failure`, `timed_out` or `startup_failure`; the run's URL is printed;
- exit 2: the result is not known. No completed run exists for the commit (CI not started or
  still running), the latest completed run was `cancelled`, `skipped` or `neutral` or has a
  conclusion this script does not recognise, local `dev` differs from `origin/dev` (dev is not
  pushed), or `git` or `gh` failed.

Exit 2 fails closed: no grant while the result is unknown, unless the owner rules otherwise for
that grant. The conclusion mapping and the choice of gated turns are owner rulings of 2026-09-24.
With `--wait`, the script re-queries every `--interval` seconds while the answer is exit 2 and
stops at the first 0 or 1; a timeout exits 2.

The commit defaults to `git rev-parse dev`, not `HEAD`, so the answer is the same from a worktree
as from the primary checkout. With `--commit`, the pushed-dev comparison is skipped and the value
is expanded to a full SHA with `git rev-parse`.

See REQ-028 R06 and PLAN-045 D6 (docs/01-plans/PLAN-045-deterministic-guards.md), phase-grd-02.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--commit` | check this commit instead of dev's head (skips the pushed-dev check) |  |  |  |
| `--wait` | seconds to keep re-checking while the result is unknown (default 0) |  | 0.0 |  |
| `--interval` | seconds between checks when --wait is set (default 30) |  | 30.0 |  |

<!-- generated:tool-reference:end -->
