---
schema_version: 1
id: doc-session-refuse-dirty-integration
code: SESS-2026-09-22-06
title: Refuse integration over a dirty primary checkout
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems:
- sys-governance
- sys-delivery
depends_on:
- doc-concurrency-git-safety-requirements
- doc-concurrency-git-safety
---

# Refuse integration over a dirty primary checkout

## Phase

`phase-conc-02` — Refuse integration over a dirty primary checkout. Claimed as `agent-coord`,
worked on `agent/phase-conc-02` in `/code/d-system-worktrees/phase-conc-02`, per `PLAN-026` and
`REQ-013` (`R04`).

## What was built

`tools/git-hooks/refuse_dirty_integration.py` (new): a pre-merge script, run by hand in the
primary checkout immediately before `git merge --ff-only agent/<phase-id>`. It refuses on two
independent conditions, either sufficient alone:

1. **A dirty working tree** — every path `git status --porcelain` reports (staged, unstaged,
   untracked) is named in the refusal.
2. **A non-empty stash** — `git stash list` in the primary checkout. This is what makes the
   refusal survive `git stash`: a peer's uncommitted work stashed away still shows a clean working
   tree to check 1 alone, but the stash entry is evidence work is in flight, and stashing to clear
   the refusal is the exact `000041` incident mechanism.

`resolve_primary_checkout()` resolves `--repo` (default: cwd) to the primary checkout via
`git rev-parse --git-common-dir` before either check runs, so the guard always inspects the real
primary checkout regardless of which worktree or subdirectory it is invoked from or pointed at.

The integration branch is configuration (`--integration-branch` / `$D_SYSTEM_INTEGRATION_BRANCH`,
default `dev`), used only to name the branch in the refusal message.

`docs/08-governance/OPS-001-operations.md` gained a new "Refuse integration over a dirty primary
checkout" section: the invocation, the placement decision and its reason, what is and is not
wired up today, the primary-checkout resolution behavior, and the deliberate stash-is-uncommitted-
work definition of "clean."

`test/test_refuse_dirty_integration.py` (new): four tests, each running the guard as a real
subprocess against a disposable git repository built fresh under `tmp_path` — never against
`/code/d-system` or this worktree.

## Owner rulings

Three rulings were given and followed, none re-opened:

1. **Form and placement: a pre-merge script under `tools/`, invoked at the merge step.** Git has
   no stash event to hook, so a `pre-commit`/`pre-push` hook cannot catch this; the merge is the
   one hookable moment. The script was placed at `tools/git-hooks/refuse_dirty_integration.py`
   rather than top-level `tools/` — `tools/git-hooks/` is itself a declared deliverable, and every
   top-level `tools/*.py` file is required by `test/test_tool_docs.py` (an unrelated, pre-existing
   convention) to pair with its own new `OPS-*` governed document, which minting was out of this
   phase's scope. The coordinator confirmed this placement is accepted as-is; it will not move.
2. **`test/` was widened into the phase's declared deliverables mid-session** (committed on `dev`
   as `178ae3a`, this branch rebased onto it), after the initial build stopped short of adding a
   test file per the original instruction that `test/` was undeclared. The four-test file above
   was added once the ruling landed.
3. **`OPS-001` is branch-agnostic but configurable.** The guard names "the integration branch" as
   configuration (`--integration-branch` / `$D_SYSTEM_INTEGRATION_BRANCH`, default `dev`) rather
   than hard-coding `dev` or `main`.

## Placement decision and reason

`phase-conc-08` (the general enforcement-placement rule) has not landed — it is still `queued` in
`docs/09-backlog/backlog.yaml`. This phase therefore states its own placement and reason rather
than deferring to it, per its own scope bullet 3: a pre-merge script, invoked by hand in the
primary checkout at the integration step, documented in `OPS-001-operations.md`'s new section and
in `PLAN-026`'s "decision 2." `phase-conc-08`, once it lands, generalises the placement question
this phase answers narrowly.

## Verification

```
$ uv run python -m src.governance
Governance OK: 35 systems, 314 documents, 30 memories, 293 backlog phases
```

```
$ uv run pytest
767 passed, 2 warnings in 63.52s (0:01:03)
```

## Acceptance

- **"REQ-013 R04 holds: with an unrelated modified file in the primary checkout, the integration
  is refused and the dirty paths are named." — Met.** Confirmed by
  `test_unrelated_modified_file_is_refused_and_named` and by the validator's independent
  disposable-repo run (exit 1, "Refused" and `unrelated.txt` named).
- **"The refusal survives a `git stash` — stashing the peer's work does not let the integration
  proceed." — Met.** After `git stash -u`, `git status --porcelain` is empty but the guard still
  refuses on the non-empty stash list, naming the stash entry and stating it counts as uncommitted
  work. Confirmed by `test_stashing_the_dirty_file_still_refuses` and the validator's run.
- **"A clean primary checkout is not refused, so the guard does not block ordinary work." — Met.**
  A fresh repository with only its initial commit exits 0 with "not refused." Confirmed by
  `test_clean_checkout_is_not_refused` and the validator's run. (The adversary noted, and this
  session's fix cycle made explicit, that "clean" here is the guard's own stricter sense — no
  stash entries either — documented as deliberate rather than left implicit; see Finding 2 below.)

## Validator

`/code/d-system/_working/build-batch-002/phase-conc-02-validation.md` — **PASS**. All three
acceptance conditions independently re-verified against disposable repositories, both verification
commands green, deliverables matched exactly what was declared.

## Adversarial review

Two rounds, both recorded in `/code/d-system/_working/build-batch-002/phase-conc-02-adversary.md`
(commit range `178ae3a..260fbe0`, then the fix-cycle range `260fbe0..8c6c0b3`). First round: three
confirmed findings. Second round (re-attack after the fix): **SOUND, no new findings.**

**Finding 1 — MEDIUM, confirmed.** `OPS-001` claimed the script ran "in step 9 above" of
`AGENTS.md`'s hand-off procedure, but `AGENTS.md` (owner-only, correctly unmodified) still reads
exactly its prior prose-only `git status` check, with no mention of the new script anywhere.
*Fix:* `OPS-001` now states plainly, under "What is, and is not, wired up," that nothing today
calls the script automatically — not step 9, a git hook, or CI — and that an agent following
`AGENTS.md`'s literal steps would not encounter it. The script's own docstring was corrected to
match. A proposed one-line `AGENTS.md` addition is recorded below, for the owner to decide;
`AGENTS.md` was not touched. *Re-attack: FIXED, confirmed* — grepped both files directly, no
remaining claim that the script is part of the followed procedure.

**Finding 2 — MEDIUM, confirmed, accepted as deliberate behaviour.** A single pre-existing,
unrelated stash in the primary checkout blocks every future integration, with no way to
distinguish "a peer's work stashed to defeat this guard" from "an unrelated stash nobody has
cleaned up." The adversary flagged this as very likely intended but noted acceptance 3's plain
wording ("a clean primary checkout is not refused") doesn't obviously cover the guard's stricter
sense of "clean." Per the coordinator's explicit instruction, the *behaviour was not weakened* —
this is the correct stash-proofing, not a bug. *Fix:* the refusal now names each stash entry and
states outright that a stash counts as uncommitted work that must be restored and committed, or
dropped by its owner, before integrating. `OPS-001` now states explicitly: **"clean" for this
guard means no working-tree changes *and* no stash entries**, and names the accepted consequence
as intentional. *Re-attack: FIXED, confirmed* — the new wording and stash-list echo were both
verified present in the real refusal.

**Finding 3 — MEDIUM, confirmed.** `--repo` (or cwd) pointed at a linked worktree instead of the
primary checkout silently reported "not refused" while the real primary checkout was dirty —
`refs/stash` is shared across worktrees so a stash was still caught, but an ordinary dirty
working-tree file in the true primary was invisible from any other worktree. *Fix:*
`resolve_primary_checkout()` resolves `--repo`/cwd to the primary checkout via
`git rev-parse --git-common-dir` before either check runs, so the result no longer depends on
which worktree or subdirectory the script is invoked from or pointed at. A new test builds a
primary + linked worktree under `tmp_path`, dirties only the primary, and confirms the guard
invoked against the linked worktree still refuses and names the dirty path. *Re-attack: FIXED,
confirmed* — including a mutation test where `resolve_primary_checkout` was stubbed to an identity
function, which the new test correctly caught as a regression.

**Held under both rounds (no finding):** mutation tests neutering the dirty-path and stash checks
were both caught by the existing suite; a gitignored file is invisible to the guard (ordinary git
behavior, not a finding since a gitignored file cannot land on `dev` via a merge); running from a
subdirectory of the primary checkout with no `--repo` still finds dirt correctly; staged-only,
untracked-only and rename-entry porcelain states all parsed correctly; deliverables touched
exactly matched what was declared (`tools/git-hooks/`, `tools/`, `test/`,
`docs/08-governance/OPS-001-operations.md`, no overreach).

## Unresolved

**Nothing invokes the guard automatically.** It is a pre-merge script an agent must choose to run
by hand; `AGENTS.md`'s literal hand-off steps do not call it, and no git hook or CI wiring exists.
This is by design for the git-stash half of the problem (there is no stash event to hook), but the
merge step itself *could* be wired to run it automatically and currently is not. A proposed
one-line `AGENTS.md` addition — inserted immediately before step 9's merge command block in
*Concurrent agents: complete and hand off* — awaits the owner's decision, since no agent may edit
`AGENTS.md` without explicit approval:

> Before merging, run `uv run python tools/git-hooks/refuse_dirty_integration.py` in the primary
> checkout and confirm it exits 0 — see `OPS-001-operations.md` for what it checks.

## Backlog

`phase-conc-02` stays as the coordinator finds it; this session does not edit
`docs/09-backlog/backlog.yaml`. The completion edit, and the integration decision, are the
coordinator's to make on `dev`.
