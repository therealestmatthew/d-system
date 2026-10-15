#!/usr/bin/env bash
# Apply the branch and tag rulesets in .github/rulesets/ to one GitHub repository, set its default
# branch to dev, and allow merge commits only. Guide: docs/guides/OPS-001-branching-and-ci.md.
#
# Usage:
#   tools/github/apply_rulesets.sh <owner/repo> <control|product>
#
#   control  applies control-dev.json, control-main.json, demo-tags.json
#   product  applies product-dev.json, product-main.json, demo-tags.json
#
# The repository owner runs this by hand, with `gh` signed in as an account that administers the
# repository. Nothing runs it automatically. It is idempotent: a ruleset whose name already exists
# on the repository is updated in place; otherwise it is created. Rulesets inherited from the
# organization are not touched.
#
# Both branches, dev and main, must already exist on the remote.
# Rulesets on a private repository need a paid GitHub plan for the organization.

set -euo pipefail

usage() {
  echo "usage: $0 <owner/repo> <control|product>" >&2
  exit 2
}

[ "$#" -eq 2 ] || usage
repo="$1"
kind="$2"

case "$repo" in
  */*) ;;
  *) echo "error: repository must be <owner/repo>, got '$repo'" >&2; usage ;;
esac

case "$kind" in
  control) files=(control-dev.json control-main.json demo-tags.json) ;;
  product) files=(product-dev.json product-main.json demo-tags.json) ;;
  *) echo "error: second argument must be control or product, got '$kind'" >&2; usage ;;
esac

command -v gh >/dev/null || { echo "error: gh is not installed" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "error: gh is not signed in (run gh auth login)" >&2; exit 1; }

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ruleset_dir="$(cd "$here/../../.github/rulesets" && pwd)"

echo "repository: $repo ($kind)"

# The default branch can only point at a branch that exists.
for branch in dev main; do
  if ! gh api "repos/$repo/branches/$branch" --silent 2>/dev/null; then
    echo "error: branch '$branch' does not exist on $repo; push it first" >&2
    exit 1
  fi
done

echo "setting default branch to dev and merge method to merge commit only"
gh api -X PATCH "repos/$repo" \
  -f default_branch=dev \
  -F allow_merge_commit=true \
  -F allow_squash_merge=false \
  -F allow_rebase_merge=false \
  --jq '"  default_branch=\(.default_branch) merge_commit=\(.allow_merge_commit) squash=\(.allow_squash_merge) rebase=\(.allow_rebase_merge)"'

for file in "${files[@]}"; do
  path="$ruleset_dir/$file"
  [ -f "$path" ] || { echo "error: missing $path" >&2; exit 1; }
  name="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["name"])' "$path")"
  id="$(gh api "repos/$repo/rulesets?includes_parents=false" --paginate \
        --jq ".[] | select(.name == \"$name\") | .id" | awk 'NR == 1')"
  if [ -n "$id" ]; then
    gh api -X PUT "repos/$repo/rulesets/$id" --input "$path" --silent
    echo "updated ruleset '$name' (id $id) from $file"
  else
    id="$(gh api -X POST "repos/$repo/rulesets" --input "$path" --jq .id)"
    echo "created ruleset '$name' (id $id) from $file"
  fi
done

echo "done. Review: gh api repos/$repo/rulesets --jq '.[] | \"\\(.id) \\(.name) \\(.enforcement)\"'"
