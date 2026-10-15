#!/bin/sh
# Installs this repository's git hooks: points core.hooksPath at the tracked tools/git-hooks, so
# every worktree of this clone uses them and a pull that changes a hook updates it.
#
# Run once per clone, from anywhere inside it:
#   tools/install-hooks.sh
#
# Three hooks run tools/check_confidential.py: pre-commit on the staged files, commit-msg on the
# commit message, and pre-push on every commit a push sends (messages and added lines), which
# catches what a rebase, a cherry-pick or --no-verify let past the first two. Put the deny-list at
# .private/deny-list.txt in the main checkout (never committed; worktrees read it from there), or
# export PRIVATE_DENY_LIST=<path>; without one, only the private-directory path check runs.
#
# If the project adds a hook manager that also sets core.hooksPath (for example husky), call
# each of tools/git-hooks/pre-commit, commit-msg and pre-push from that manager's hook of the same
# name instead of running this script.

set -e
top=$(git rev-parse --show-toplevel)
cd "$top"

chmod +x tools/git-hooks/* tools/check_confidential.py
git config core.hooksPath tools/git-hooks

echo "core.hooksPath set to tools/git-hooks"
if [ -n "$PRIVATE_DENY_LIST" ]; then
    echo "deny-list: $PRIVATE_DENY_LIST (from PRIVATE_DENY_LIST)"
elif [ -f .private/deny-list.txt ]; then
    echo "deny-list: .private/deny-list.txt"
elif main_checkout=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)") &&
        [ -f "$main_checkout/.private/deny-list.txt" ]; then
    echo "deny-list: $main_checkout/.private/deny-list.txt (main checkout)"
else
    echo "WARNING: no deny-list found; the hook will only run the private-directory path check."
    echo "         Get the deny-list from the repository owner and save it as .private/deny-list.txt."
fi
