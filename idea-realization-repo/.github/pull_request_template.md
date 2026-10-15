<!--
Control repository pull request. Feature branches reach `dev` only through a pull request merged
with a merge commit. Claim, completion, idea and workstream commits, and a developer's own entry in
`docs/systems.yaml`, go directly to `dev` and need no pull request. Planning pull requests (plans,
requirements, new phases) are merged by the owner. Release pull requests (`dev` to `main`) list the phases they carry instead of the
phase section below.
-->

## Phase

- Phase id and title:
- Plan (code and title):
- Idea ids (`<handle>-NNNNNN`), if any:
- Unclaimed work (no phase): yes / no. If yes, say what was asked and by whom.

## What changed

<!-- One line per change. Name the files or areas; say why, not only what. -->

-

## Verification

<!-- Paste the real output tails, not a summary. A failure is a result: paste it. -->

```text
check.py:
pytest:
check_confidential.py (run with the changes staged):
```

## Gating review

- Verdict record: `docs/reviews/<date>-<phase-id>-<reviewer type>.json`
- Verdict: pass / reject
- Product `reviewed_commit`:
- Product pull request:
- Findings not fixed, each with who accepted it:

## Checklist

- [ ] Branch rebased onto `origin/dev`; nothing merged in from `dev`.
- [ ] `check.py` passes; the catalog was regenerated, not edited by hand.
- [ ] No confidential identifier in any file, commit message or this description (no organization
      name, customer, account id or key). An email address appears only as a developer's own work
      email in `docs/systems.yaml`.
- [ ] `CLAUDE.md` is unchanged, or the owner approved the exact change (say where).
- [ ] No commit used `--no-verify`.
- [ ] AWS changes, if any, were made by the `aws-deploy` agent through `tools/aws-sandbox`.
