#!/bin/bash
# Build the reviewer brief for one phase at one commit. usage: make_brief.sh <phase-id> <tip-sha> [branch]
# Writes _working/session-manager/briefs/review-<phase>.md and a scratch checkout for the gating reviewer.
set -u
PH="$1"; TIP="$2"; BR="${3:-agent/$PH}"; PRIMARY=/home/user/d-system; SM=$PRIMARY/_working/session-manager
TRUNK=ccr-b69b05b4-tdcrux; OUT=$SM/briefs/review-$PH.md
cd $PRIMARY
BASE=$(git merge-base $TRUNK $TIP)
SHORT=$(git rev-parse --short=12 $TIP)
MAN=$(ls -d $PRIMARY/_working/review-checks/$PH/$SHORT* 2>/dev/null | head -1)
SCRATCH=/home/user/d-system-worktrees/scratch-$PH
rm -rf $SCRATCH; git clone -q --shared $PRIMARY $SCRATCH && git -C $SCRATCH checkout -q $TIP
{
echo "# Review brief: $PH at $TIP"
echo
echo "Range under review: $BASE..$TIP (branch $BR, base = trunk $TRUNK, which stands in for dev in this run)."
echo "Runner manifest: ${MAN:-NOT FOUND}/manifest.json (evidence files beside it; file paths inside are relative to the runner's checkout root)."
echo "Scratch checkout of the branch at the reviewed commit (gating reviewer only): $SCRATCH"
echo
echo "Do not read docs/03-sessions/, git log or commit messages, or any builder account. Judge the work, not the account."
echo
echo "## Phase entry (from dev's backlog.yaml)"
echo '```yaml'
git show dev:docs/09-backlog/backlog.yaml | awk -v id="$PH" '$0=="- id: "id{p=1;print;next} p&&/^- id: /{exit} p{print}' | grep -v "^  result:\|^  session:\|^  completion_evidence:" 
echo '```'
echo
echo "## Diff (session record and backlog bookkeeping excluded)"
echo '```diff'
git diff $BASE $TIP -- . ':!docs/03-sessions' ':!docs/09-backlog/backlog.yaml' ':!docs/08-governance/catalog.md' ':!docs/00-working/ideas.md'
echo '```'
} > $OUT
echo "brief: $OUT ($(wc -c < $OUT) bytes); manifest: ${MAN:-NONE}; scratch: $SCRATCH"
