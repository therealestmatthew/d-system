#!/usr/bin/env bash
# Apply the branch and tag rulesets in .github/rulesets/ to one GitHub repository, set its default
# branch to dev, and allow merge commits only. Guide: docs/guides/OPS-001-branching-and-ci.md.
#
# Usage:
#   tools/github/apply_rulesets.sh <owner/repo> <control|product> <main-merger>
#
#   control  applies control-dev.json, control-main.json, demo-tags.json
#   product  applies product-dev.json, product-main.json, demo-tags.json
#
#   <main-merger> is the only actor allowed to merge into main:
#     user:<login>             one GitHub account (the repository owner)
#     team:<org>/<team-slug>   a team whose only member is the repository owner
#   The *-main.json rulesets contain an `update` rule (restrict updates) and an empty bypass list,
#   so as committed nobody can update main. This script looks up the actor's numeric id and adds
#   it as the ruleset's single bypass actor with bypass_mode `pull_request`: that actor can merge a
#   pull request into main and cannot push to it directly; everyone else is refused. The id is
#   read from GitHub at run time and never written into a tracked file.
#
# Before anything reaches GitHub the script checks the target: <owner/repo> must be the repository
# this machine's configuration names for <kind>, so control rulesets cannot land on the product
# repository or the reverse. It reads `control_github` or `product_github` (as <org>/<repo>), or,
# when that is unset, the GitHub repository in `control_remote` or `product_remote`, through the
# plugin's scripts/paths.py: .idea-realization/local.yaml or IDEA_REALIZATION_<KEY>. The
# comparison ignores case, as GitHub does. It refuses when the value is unset or differs.
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
  echo "usage: $0 <owner/repo> <control|product> <user:<login>|team:<org>/<team-slug>>" >&2
  exit 2
}

[ "$#" -eq 3 ] || usage
repo="$1"
kind="$2"
merger="$3"

case "$repo" in
  */*) ;;
  *) echo "error: repository must be <owner/repo>, got '$repo'" >&2; usage ;;
esac

case "$kind" in
  control) files=(control-dev.json control-main.json demo-tags.json) ;;
  product) files=(product-dev.json product-main.json demo-tags.json) ;;
  *) echo "error: second argument must be control or product, got '$kind'" >&2; usage ;;
esac

case "$merger" in
  user:?*) actor_type=User; actor_ref="${merger#user:}" ;;
  team:?*/?*) actor_type=Team; actor_ref="${merger#team:}" ;;
  *) echo "error: third argument must be user:<login> or team:<org>/<team-slug>, got '$merger'" >&2; usage ;;
esac

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
control_root="$(cd "$here/../.." && pwd)"
ruleset_dir="$control_root/.github/rulesets"

# The GitHub <org>/<repo> in a remote URL on github.com, or nothing.
github_slug() {
  printf '%s\n' "$1" | sed -n -E \
    -e 's#^(git@|ssh://git@)github\.com[:/]([^/]+/[^/]+)$#\2#p' \
    -e 's#^https://github\.com/([^/]+/[^/]+)$#\1#p' | sed -e 's#\.git$##' -e 's#/$##'
}

# Verify the target before anything reaches GitHub.
command -v uv >/dev/null || { echo "error: uv is not installed; it reads the configured repositories" >&2; exit 1; }
config="$(uv run --quiet "$control_root/plugins/idea-realization/scripts/paths.py" \
            --root "${IDEA_REALIZATION_ROOT:-$control_root}")" \
  || { echo "error: could not read the configuration (scripts/paths.py failed)" >&2; exit 1; }
expected="$(printf '%s\n' "$config" | sed -n "s/^${kind}_github: //p")"
source_key="${kind}_github"
if [ -z "$expected" ]; then
  expected="$(github_slug "$(printf '%s\n' "$config" | sed -n "s/^${kind}_remote: //p")")"
  source_key="${kind}_remote"
fi
if [ -z "$expected" ]; then
  echo "error: ${kind}_github is not set (nor a github.com ${kind}_remote), so the $kind repository cannot be verified." >&2
  echo "       Set it in .idea-realization/local.yaml (template: local.example.yaml) and run again." >&2
  exit 1
fi
if [ "$(printf '%s' "$repo" | tr '[:upper:]' '[:lower:]')" != "$(printf '%s' "$expected" | tr '[:upper:]' '[:lower:]')" ]; then
  echo "error: '$repo' does not match the $kind repository this machine is configured for ($source_key: $expected)." >&2
  echo "       Refusing: $kind rulesets go only to the $kind repository." >&2
  exit 1
fi

command -v gh >/dev/null || { echo "error: gh is not installed" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "error: gh is not signed in (run gh auth login)" >&2; exit 1; }

echo "repository: $repo ($kind, matches $source_key)"

if [ "$actor_type" = User ]; then
  actor_id="$(gh api "users/$actor_ref" --jq .id)" \
    || { echo "error: GitHub user '$actor_ref' not found" >&2; exit 1; }
else
  actor_id="$(gh api "orgs/${actor_ref%%/*}/teams/${actor_ref#*/}" --jq .id)" \
    || { echo "error: team '$actor_ref' not found (it must belong to the organization)" >&2; exit 1; }
fi
echo "main merger: $actor_type $actor_ref (id $actor_id), bypass mode pull_request"

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
  case "$file" in
    *-main.json)
      # Add the main merger as the only bypass actor, in a temporary copy of the ruleset.
      body="$(mktemp)"
      python3 - "$path" "$actor_type" "$actor_id" > "$body" <<'PY'
import json
import sys

path, actor_type, actor_id = sys.argv[1], sys.argv[2], int(sys.argv[3])
ruleset = json.load(open(path))
ruleset["bypass_actors"] = [
    {"actor_id": actor_id, "actor_type": actor_type, "bypass_mode": "pull_request"}
]
json.dump(ruleset, sys.stdout, indent=2)
PY
      path="$body"
      ;;
  esac
  id="$(gh api "repos/$repo/rulesets?includes_parents=false" --paginate \
        --jq ".[] | select(.name == \"$name\") | .id" | awk 'NR == 1')"
  if [ -n "$id" ]; then
    gh api -X PUT "repos/$repo/rulesets/$id" --input "$path" --silent
    echo "updated ruleset '$name' (id $id) from $file"
  else
    id="$(gh api -X POST "repos/$repo/rulesets" --input "$path" --jq .id)"
    echo "created ruleset '$name' (id $id) from $file"
  fi
  case "$file" in *-main.json) rm -f "$body" ;; esac
done

echo "done. Review: gh api repos/$repo/rulesets --jq '.[] | \"\\(.id) \\(.name) \\(.enforcement)\"'"
