---
name: "Phase Completion"
description: "Pull request template for completing a phase and integrating to dev"
---

## Phase
<!-- Which phase does this PR complete? Link to backlog.yaml -->
Completes: [phase-xxx-nn](../../docs/09-backlog/backlog.yaml)

## Summary
<!-- One paragraph: what was built, why, key changes -->

## Acceptance Criteria Verification

All acceptance criteria from the phase are met:

- [x] Criterion 1: Brief description
- [x] Criterion 2: Brief description
- [x] Criterion 3: Brief description

## Verification Results

Tests pass:
```bash
$ uv run pytest [test_path] -v
# [paste actual output]
```

Type checking:
```bash
$ uv run mypy [src_path]
# [paste actual output or "All good"]
```

Linting:
```bash
$ uv run ruff check [paths]
# [paste actual output or "No issues"]
```

## Scope Confirmation

Did NOT deviate from phase scope:
- [x] Only touched files in `deliverables` list
- [x] No out-of-scope refactoring or features
- [x] Changes stay within declared `systems`

## Completion Evidence

Files that now exist and are ready:
- `src/path/file.py` — Implementation
- `test/path/test_file.py` — Tests
- `docs/path/documentation.md` — Documentation (if applicable)

## Session Record
<!-- Link to the session record that documents this work -->
Session: [SESS-YYYY-MM-DD-agent-NN](../../docs/03-sessions/SESS-yyyy-mm-dd-agent-nn.md)

## Notes
<!-- Anything the reviewer should know: trade-offs, future improvements, known limitations, etc. -->

---

## For Reviewers (Team Lead)

**Before merging, check:**
- [ ] All acceptance criteria verified above
- [ ] Tests pass in the verification results
- [ ] No scope creep (only changed what phase declared)
- [ ] Session record exists and is clear
- [ ] No conflicts with other active phases
- [ ] Rebased onto latest `dev` (no stale merges)

**If approving:** Merge with `git merge --ff-only` from primary checkout after verifying `dev` is clean.

**If requesting changes:** Comment on the specific concerns; agent will fix, rebase, and re-push.
