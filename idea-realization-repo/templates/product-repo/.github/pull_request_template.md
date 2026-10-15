<!-- A pull request to dev carries one phase's branch, agent/<phase-id>. It is merged with a merge
commit, by the session that closes the phase, after the gating review passed and `verify` is green.
Fill every field; "n/a" needs a reason. -->

## Phase

- Phase id: `REPLACE-WITH-PHASE-ID`
- Phase title: REPLACE-WITH-TITLE
- Control repository branch: `agent/REPLACE-WITH-PHASE-ID`

## Gating review

- Verdict record (control repository): `docs/reviews/REPLACE-WITH-DATE-PHASE-ID-REVIEWER.json`
- Verdict: pass / reject
- Reviewed commit (full hash; must equal this pull request's head when it is merged):
  `REPLACE-WITH-REVIEWED-COMMIT`

## Verification

The phase's verification commands, run in the product worktree on the reviewed commit. Paste the
result line of each (counts, failures); paste a failure in full.

```text
REPLACE-WITH-VERIFICATION-OUTPUT
```

## Checklist

- [ ] The branch is `agent/<phase-id>`, rebased onto `origin/dev`, and its head is the reviewed commit.
- [ ] The gating review passed on that commit, and every finding has a recorded disposition.
- [ ] `verify` is green on this pull request.
- [ ] The diff stays inside the phase's declared deliverables.
- [ ] No credential, secret value or deny-listed identifier in the diff; the pre-commit hook ran
      (no `--no-verify`).
- [ ] No AWS resource is created by CI; any infrastructure change was deployed, if at all, by
      `aws-deploy` from a developer machine.
- [ ] Merge with **Create a merge commit** (`gh pr merge <n> --merge --match-head-commit <reviewed commit>`).
