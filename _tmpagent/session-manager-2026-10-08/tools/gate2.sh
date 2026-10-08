#!/bin/bash
# Merge-gate checks for one phase worktree (Session Manager helper). usage: gate.sh <worktree> [phase-id]
# Rebases onto the trunk, runs the five gate checks, the test baseline, diff patterns and containment.
set -u
WT="$1"; PH="${2:-}"; TRUNK=ccr-b69b05b4-tdcrux; PRIMARY=/home/user/d-system
cd "$WT" || exit 9
echo "== rebase onto $TRUNK"; if ! git rebase "$TRUNK" >/tmp/gate-rebase-$$.log 2>&1; then echo "REBASE CONFLICT"; git diff --name-only --diff-filter=U; git rebase --abort; echo "== GATE DONE (rebase failed)"; exit 8; fi; tail -1 /tmp/gate-rebase-$$.log
echo "== tip $(git rev-parse HEAD)"
echo "== governance"; uv run -q python -m src.governance 2>&1 | grep -v UV_NATIVE | tail -2
echo "== pytest"; uv run -q pytest -q --junitxml=/tmp/branch-$$.xml 2>&1 | grep -v UV_NATIVE | tail -3
echo "== ruff"; uv run -q ruff check src/ test/ tools/ 2>&1 | grep -v UV_NATIVE | tail -2
echo "== mypy"; uv run -q mypy src/ 2>&1 | grep -v UV_NATIVE | tail -2
if [ -d ts/node_modules ]; then echo "== npm test"; (cd ts && npm test 2>&1 | sed "s/\x1b\[[0-9;]*m//g" | grep -a -E "Test Files|Tests |FAIL|failed" | head -12); else echo "== npm test: skipped (no node_modules)"; fi
echo "== catalog clean"; git diff --exit-code --stat docs/08-governance/catalog.md && echo "catalog unchanged by tests"
echo "== baseline (base = trunk tip in a temp clone)"
BASE=$(mktemp -d /tmp/base-XXXX); git clone -q --shared "$PRIMARY" "$BASE" && (cd "$BASE" && git checkout -q "$TRUNK" && ln -s "$WT/.venv" .venv && uv run -q pytest -q --junitxml=/tmp/base-$$.xml 2>&1 | grep -v UV_NATIVE | tail -1); 
uv run -q python tools/check_test_baseline.py /tmp/base-$$.xml /tmp/branch-$$.xml 2>&1 | grep -v UV_NATIVE | tail -3; echo "baseline exit: ${PIPESTATUS[0]}"
rm -rf "$BASE"
echo "== diff patterns"; uv run -q python tools/check_diff_patterns.py "$TRUNK..HEAD" 2>&1 | grep -v UV_NATIVE | tail -3; echo "diff-patterns exit: ${PIPESTATUS[0]}"
if [ -n "$PH" ]; then echo "== containment"; uv run -q python -m src.governance --containment "$PH" 2>&1 | grep -v UV_NATIVE | tail -8; fi
echo "== status"; git status --short | head -5; echo "== GATE DONE"
