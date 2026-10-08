# Scout environment audit

Audit date: 2026-10-08. Read-only. No git write commands, no pytest, no tracked files edited. The only write is this file.

## 1. Git

- `git status --short`: clean (no output).
- Local branches: `ccr-b69b05b4-tdcrux` (checked out in the only worktree, `/home/user/d-system`), `dev`.
- Remote-tracking refs present locally: `origin/dev`, `origin/ccr-b69b05b4-tdcrux`.
- Worktrees: one, `/home/user/d-system` at `6951bb6` on `ccr-b69b05b4-tdcrux`.
- `dev` head: `6951bb6` (000599 record, Session 1). `origin/dev` head: `6951bb6`.
- `git rev-list --left-right --count dev...origin/dev`: `0 0`. dev equals origin/dev.
- Session branch `ccr-b69b05b4-tdcrux` head: `6951bb6`. It equals dev and origin/dev.
- `git merge-base --is-ancestor origin/dev ccr-b69b05b4-tdcrux`: exit 0 (origin/dev is an ancestor; they are identical).
- Remote heads (`git ls-remote --heads origin`): 20 lines.
  - `refs/heads/dev`, `refs/heads/main`.
  - 18 `agent/*` heads: fix-backlog-prefix-table, fix-ci-ruff-tools, fix-demo-terminal-ignore, fix-irs-11-hold, fix-promoted-to-codes, gemini-g1-three-axis-stress, gemini-g2-adr-023-parameters, gemini-g3-governance-analysis, gemini-run-summary, phase-asr-04, phase-asr-05, phase-grd-04, phase-lrr-03, phase-rel-03, phase-sch-03, plan-productivity-core, plan-productivity-core-v2, sys-content-entry.
  - No `ccr-b69b05b4-tdcrux` head on origin. The local `origin/ccr-b69b05b4-tdcrux` ref points at `6951bb6` and is a stale tracking ref; the remote branch is absent.

## 2. Config

- `git config core.hooksPath`: unset (exit 1).
- `tools/git-hooks/pre-commit`: exists, mode `-rwxr-xr-x`, 685 bytes.
- `tools/git-hooks/refuse_dirty_integration.py`: exists, 8286 bytes.
- `.git/hooks/pre-commit`: does not exist. `.git/hooks/` holds only `.sample` files. The tracked hook is not wired into git, because `core.hooksPath` is unset and nothing is installed under `.git/hooks`.
- `.gitignore` lines:
  - `4:.venv/`
  - `14:data/`
  - `42:_private/`, `43:_private/portfolio/`, `44:_private/portfolio/projects/`
  - `51:_working/`, `52:!_working/.gitkeep`

## 3. Stale claim: phase-idg-12

Backlog entry at `docs/09-backlog/backlog.yaml` line 10845.

- `status: active`
- `agent: agent-batch-runner`
- `owner: repository-owner`
- `priority: 3`, `session_budget: 1`
- `depends_on`: phase-idg-10, phase-idg-11, phase-dgov-01, phase-irs-03
- The entry has no `session`, `claimed` or `updated` key.
- `next_action` (line 10905): "Write the agent against the GOV-014/ARCH-006 shape - track in, one draft per accepted ..." The full text is on that line.

Claim date, from git history:

- `eeab5ee` on 2026-10-05 22:46:13 -0400, Matthew Mule: "Claim phase-idg-12 for batch-004 with the owner's approved claim-time edits". This is the commit that introduced `agent: agent-batch-runner` for phase-idg-12. It is an ancestor of dev.
- Earlier, `72e405b` (2026-10-05 17:59 -0400) claimed phase-dgov-01 for batch-004, and `d62dba3` (2026-10-05 08:24 -0400) was a phase-lrr-03 re-claim commit.
- The claim is about two days old as of 2026-10-08.

Branch check:

- `agent/phase-idg-12`: no local branch (`git branch -a --list '*idg-12*'` is empty) and no origin head (`git ls-remote --heads origin refs/heads/agent/phase-idg-12` is empty, exit 0).
- No branch carries the claim's work.

## 4. Batches (`docs/09-backlog/batches/`)

| File | id | status |
|---|---|---|
| batch-001-partition-portfolio-session-foundations.yaml | batch-001 | complete |
| batch-002-governance-guards-and-autonomous-operations.yaml | batch-002 | complete |
| batch-003-realization-graphs-and-idea-graph-foundations.yaml | batch-003 | complete |
| batch-004-requirement-ruling-planner-and-pipeline-head.yaml | batch-004 | in_progress |
| batch-005-gate-queue-execution-loop-and-anti-pattern-store.yaml | batch-005 | queued |
| batch-006-learning-loop-and-pipeline-close.yaml | batch-006 | queued |
| batch-007-run-budgets-and-batch-graph.yaml | batch-007 | queued |

Batch-004 phases, with status from backlog.yaml:

| Stage | Phase | Status | Agent |
|---|---|---|---|
| 1 | phase-dgov-01 | complete | agent-batch-runner |
| 2 | phase-idg-12 | active | agent-batch-runner |
| 3 | phase-irs-05 | queued | (none) |
| 4 | phase-irs-06 | complete | agent-builder-a |
| 5 | phase-irs-07 | queued | (none) |

The batch file itself says phase-irs-07 is "queued and unclaimed" and phase-irs-06 is complete (agent-builder-a).

## 5. Tooling

- `uv run python tools/check_dev_ci.py --help`: exit 0. It prints usage: `--commit`, `--wait` (default 0), `--interval` (default 30).
- `uv run python tools/check_dev_ci.py` (60 s timeout): exit 0. Output: `green: CI succeeded for 6951bb6: https://github.com/therealestmatthew/d-system/actions/runs/37468431228`
  - Independent check: `gh run list --workflow ci.yaml --commit <full dev sha> --limit 50` returns one run, 37468431228: push, dev, completed, success, created 2026-10-06T13:08:08Z.
  - A query with the 7-character SHA returns an empty list. The script expands the SHA to the full form, so only full SHAs work with `gh run list --commit`.
- `which`: gh `/usr/local/bin/gh`, node `/opt/node22/bin/node`, npm `/opt/node22/bin/npm`, uv `/root/.local/bin/uv`.
- `node --version`: v22.22.0. `npm --version`: 10.9.4.
- `ts/node_modules`: does not exist. Not installed (per instruction).
- `gh auth status`: prints "Failed to log in to github.com using token (GH_TOKEN) ... The token in GH_TOKEN is invalid." Yet `gh api user` returns `therealestmatthew`, and `gh run list` works. The auth status message conflicts with working API calls. Cause not investigated.
- `uv run python -m src.governance`: exit 0. Last line: `Governance OK: 45 systems, 455 documents, 37 memories, 347 backlog phases`.
- `uv run ruff check src/ test/ tools/`: exit 0. `All checks passed!`
- `uv run mypy src/`: exit 0. `Success: no issues found in 50 source files`.
- Runner files, all present:
  - `tools/run_review_checks.py` (11719 bytes)
  - `tools/check_test_baseline.py` (4232 bytes)
  - `tools/check_diff_patterns.py` (7397 bytes)
  - `tools/git-hooks/refuse_dirty_integration.py` (8286 bytes)
- OPS-029 (`docs/08-governance/OPS-029-run-review-checks.md`), first 40 lines. Command: `uv run python tools/run_review_checks.py <phase-id> <commit>`, with no other arguments accepted. Its steps:
  1. Reads the phase from `dev`'s `docs/09-backlog/backlog.yaml` via `git show dev:...`, not from the commit under review. The manifest records the dev commit used.
  2. Creates a detached worktree at the commit, under `../d-system-worktrees/review-<phase-id>-...`, outside the repo.
  3. Runs `uv sync --extra dev` and `cd ts && npm ci` in that worktree, listed as `setup` entries. These need network access to the uv and npm registries.
  - The doc says the runner never runs anything in the checkout it is started from.
  - The runner was not executed in this audit.

## 6. Disk

- `df -h /home/user | tail -1`: `/dev/vda 252G 9.3G 30G 24% /`
- `du -sh /home/user/d-system/.venv`: 227M

## 7. Agent definitions (`.claude/agents/`)

16 files: demo-adversary, demo-agent-evidence-checker, demo-agent-objection-panel, demo-creator-docs, demo-creator-py, demo-creator-web, demo-orch-content, demo-orch-data, demo-orch-stage, demo-validator-check, demo-validator-code, demo-validator-web, idea-triage, partition-adversary, partition-analyst, review-judge.

- `demo-adversary.md` frontmatter: `model: sonnet`, `effort: high`, `maxTurns: 50`, `tools: Read, Grep, Glob, Bash`. Read-and-run only, per its description.
- `review-judge.md` frontmatter: `model: sonnet`, `effort: high`, `maxTurns: 60`, `tools: Read, Grep, Glob`. No shell and no write tool. Runs in shadow until the owner promotes it under GOV-003.

## Anomalies

1. `gh auth status` reports the GH_TOKEN as invalid, but gh API calls succeed. Not investigated.
2. The session branch `ccr-b69b05b4-tdcrux` is not on origin. A stale local `origin/ccr-b69b05b4-tdcrux` ref remains.
3. The tracked `tools/git-hooks/pre-commit` is not wired: `core.hooksPath` is unset and `.git/hooks/pre-commit` does not exist.
4. phase-idg-12 is still `active` about two days after its claim commit, with no branch on origin or locally, and no session key in the record.
5. `ts/node_modules` is absent. `run_review_checks.py` runs `npm ci` in its own worktree, so it needs network access to the npm registry.
