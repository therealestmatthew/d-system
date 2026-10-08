#!/bin/bash
# Merge turn for one READY phase: rebase, quick checks, verdict sha check, ff-merge, completion edit, push.
set -u; PH="$1"; WT=/home/user/d-system-worktrees/$PH; TRUNK=ccr-b69b05b4-tdcrux; P=/home/user/d-system
cd "$WT" || exit 9
if ! git rebase "$TRUNK" >/tmp/rebase-$$.log 2>&1; then
  for i in 1 2 3 4 5 6 7 8 9 10; do
    if git diff --name-only --diff-filter=U | grep -qv "docs/08-governance/catalog.md"; then echo "NON-CATALOG CONFLICT:"; git diff --name-only --diff-filter=U; git rebase --abort; exit 8; fi
    if git diff --name-only --diff-filter=U | grep -q "catalog.md"; then git checkout --ours docs/08-governance/catalog.md 2>/dev/null; uv run -q python -m src.governance --catalog >/dev/null 2>&1; git add docs/08-governance/catalog.md; fi
    if GIT_EDITOR=true git rebase --continue >/tmp/rebase-$$.log 2>&1; then break; fi
    git rev-parse -q --verify REBASE_HEAD >/dev/null 2>&1 || break
  done
fi
GD=$(git rev-parse --git-dir); { [ -d "$GD/rebase-merge" ] || [ -d "$GD/rebase-apply" ]; } && { echo "REBASE STILL IN PROGRESS"; exit 8; }
echo "rebased onto $TRUNK: $(git log --oneline -1)"
uv run -q python -m src.governance --catalog >/dev/null 2>&1
if ! git diff --quiet docs/08-governance/catalog.md; then git add docs/08-governance/catalog.md && git commit -q -m "Regenerate the catalog after rebasing $PH onto the trunk

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01RtMnXEnatV62SdHgZTaA6z" && echo "catalog regenerated and committed"; fi
TIP=$(git rev-parse HEAD); echo "tip $TIP"
uv run -q python -m src.governance 2>&1 | grep -v UV_NATIVE | tail -1
uv run -q ruff check src/ test/ tools/ 2>&1 | grep -v UV_NATIVE | tail -1
uv run -q mypy src/ 2>&1 | grep -v UV_NATIVE | tail -1
uv run -q pytest test/test_backlog*.py test/test_codes.py test/test_governance*.py test/test_review_verdict.py test/test_workbench_layout_schema.py -q 2>&1 | grep -v UV_NATIVE | tail -1
git diff --exit-code --quiet docs/08-governance/catalog.md && echo "catalog clean" || { echo "CATALOG DIRTY"; exit 7; }
echo "== verdict sha check"
cd "$P"; FAIL=0
grep " docs/08-governance/reviews/verdicts/.*$PH-" _working/session-manager/verdicts.sha256 | while read sha path; do
  got=$(git show "$TIP:$path" 2>/dev/null | sha256sum | cut -d' ' -f1)
  if [ "$got" = "$sha" ]; then echo "ok   $path"; else echo "MISMATCH $path (got ${got:-missing})"; exit 6; fi
done || exit 6
echo "== integrate"
if ! uv run -q python tools/git-hooks/refuse_dirty_integration.py >/tmp/refuse-$$.log 2>&1; then echo "INTEGRATION REFUSED"; tail -3 /tmp/refuse-$$.log; exit 5; fi; grep -v UV_NATIVE /tmp/refuse-$$.log | tail -1
if ! git merge --ff-only "agent/$PH" >/tmp/merge-$$.log 2>&1; then echo "FF-MERGE REFUSED"; tail -2 /tmp/merge-$$.log; exit 4; fi; tail -1 /tmp/merge-$$.log
python3 -I _working/session-manager/tools/complete_phase.py "$PH" || exit 3
uv run -q python -m src.governance --catalog >/dev/null 2>&1
uv run -q python -m src.governance 2>&1 | grep -v UV_NATIVE | tail -1
git add docs/09-backlog/backlog.yaml docs/08-governance/catalog.md
git commit -q -m "Complete $PH after its fast-forward integration

Gating verdict pass; every finding fixed or explicitly accepted on the branch. Catalog regenerated with --catalog.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01RtMnXEnatV62SdHgZTaA6z" 2>&1 | grep -v UV_NATIVE | tail -1
git branch -f dev "$TRUNK"; git push -q origin "$TRUNK" 2>&1 | tail -1
echo "TURN DONE $(git rev-parse --short HEAD) $PH"
