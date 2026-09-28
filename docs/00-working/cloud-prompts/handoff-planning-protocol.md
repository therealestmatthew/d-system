# Handoff: planning protocol document (idea 000500)

*Ran unclaimed: owner-directed work with no backlog phase; no peer holds a lock against it.*

## 1. Branch and tip

- Branch: `agent/cloud-planning-protocol`
- Tip when the gates ran: `4d83a82`. This handoff commit sits directly on top of it; it changes
  only this file and `status.md`, both ungoverned.
- Rebased onto `origin/dev` at `a34e8f3` (`git rebase origin/dev` reported "Current branch
  agent/cloud-planning-protocol is up to date").

## 2. What changed

- `docs/08-governance/GOV-021-planning-protocol.md`: added. The planning protocol, `status:
  draft`, 19 steps in three groups (before planning, planning, execution and after), each
  pointing to where it is defined; an Out of scope section; five open questions.
- `docs/08-governance/catalog.md`: regenerated for the new document (one row, and the governance
  count 17 → 18).
- `docs/00-working/cloud-prompts/status.md`: row 1 set to `in progress`, then `ready`.
- `docs/00-working/cloud-prompts/handoff-planning-protocol.md`: this file.

Commits: `95970b4` (tracker start), `935bf2f` (the document and catalog), `4d83a82` (a pointer
fix in step 14: `AGENTS.md` has four "Concurrent agents" sections, not three; the step now names
the two it relies on).

## 3. Codes allocated with `--next-code`

- `GOV-021` (`uv run python -m src.governance --next-code governance`, run once). The local
  Session Manager should check it is still free on current `dev`.

## 4. Review verdict

**Not run. This is an open item.** The prompt names `partition-adversary`. The Agent tool
rejected it: `Agent type 'partition-adversary' not found. Available agents: claude,
claude-code-guide, demo-adversary, demo-creator-docs, demo-creator-py, demo-creator-web,
demo-orch-content, demo-orch-data, demo-orch-stage, demo-validator-check, demo-validator-code,
demo-validator-web, Explore, general-purpose, idea-triage, Plan, statusline-setup`.

Cause: the session loaded its agent types from the branch the clone opened on,
`claude/master-prompt-execution-udywbn`. That branch was cut from `main` at `6a9ab96`
(2026-09-12), and its `.claude/agents/` has 11 files and no `partition-adversary.md`. The file is
on `origin/dev` and on this branch.

The prompt forbids substituting `general-purpose`. The owner was asked whether to substitute
`demo-adversary` and chose to leave the review open. The Session Manager should dispatch
`partition-adversary` locally with the prompt's brief (`planning-protocol.md`, "Adversarial
review"), `{ABS}` set to the local checkout, `<file>` = `GOV-021-planning-protocol.md`. Add this
to the brief: the owner's four answers of 2026-09-28 (section 7 below) count as owner rulings
for the fidelity check.

As a partial check, which does not replace the review, the session opened every document and
section the draft points to. It found one wrong pointer (step 14, fixed in `4d83a82`) and none
elsewhere.

## 5. Gate runs (last ten lines each, verbatim)

`uv run python -m src.governance`:

```
WARNING status-regression: dev is unreadable, skipping the dev-relative comparison
Governance OK: 43 systems, 398 documents, 34 memories, 332 backlog phases
EXIT=0
```

`uv run pytest`:

```
test/test_workbench_layout_schema.py .....................               [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/starlette/testclient.py:53
  /home/user/d-system/.venv/lib/python3.12/site-packages/starlette/testclient.py:53: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = Callable[[], AbstractContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============ 1151 passed, 1 skipped, 1 warning in 146.99s (0:02:26) ============
EXIT=0
```

`uv run ruff check src/ test/`:

```
All checks passed!
EXIT=0
```

`uv run mypy src/`:

```
Success: no issues found in 46 source files
EXIT=0
```

The `status-regression` warning appears because this clone has no local `dev` branch, only
`origin/dev`. It showed on the baseline run before any change as well.

## 6. Documents that need amending (not amended here)

- **`GOV-008`, "The pipeline", stage 1.** It reads: "A governed prompt document (precedent: the
  workbench pre-plan package, `PROMPT-020`), planned **interactively with the owner**". It has no
  optional or ungoverned case. The owner's ruling of 2026-09-27 says the pre-plan package is
  optional and lives in `docs/00-working/` unless it will be re-run, has owner gates, or needs its
  own review. `GOV-021` step 4 carries the ruling (its Open question 1).
- **`GOV-014` against `GOV-018`, an existing inconsistency between them.** `GOV-014`, "Phase-fit",
  never-do: "never register a phase directly to the backlog — that is the mapper's output". So
  phases are registered at stage 7. But `GOV-018`, "Step 2", defines the phase altitude as "Every
  phase in `docs/09-backlog/backlog.yaml` whose `plan` is this plan's `id`", which is stage 5,
  before the mapper runs. `GOV-021` Open question 4 records it. Which one should change is the
  owner's decision.

## 7. Ideas for local Ideation

- The cloud master prompt's sessions open on whatever branch the cloud session was created with,
  and load `.claude/agents/` from it. Any agent type added since that branch was cut cannot be
  dispatched, as happened with `partition-adversary` here. Cloud sessions for these prompts
  should start from `dev`, or the prompts should expect this.

The owner named no new wants during the session.

## 8. Open owner questions and stated assumptions

Owner answers given in this session (2026-09-28), all recorded in `GOV-021`:

1. The plan is audited before it is decomposed into phases, as the owner stated it. The conflict
   with `GOV-018`'s plan altitude, `GOV-002` and `ARCH-006` stage 4 is flagged (Open question 3).
2. `systems` and `depends_on` are assigned after the decompose-and-audit loop, as in `ARCH-006`
   stage 7. The conflict with the backlog schema, `GOV-018` and `GOV-014` is flagged (Open
   question 4).
3. Order: systems and dependencies, then G3, then batching (Open question 5 records that the
   owner's wording read "batch phases and order dependencies").
4. The optional pre-plan investigation comes before the requirement (step 4).
5. The adversarial review is left open rather than substituted (section 4).

Still open for the owner (`GOV-021`, "Open questions"):

- Whether and when to amend `GOV-008` for the optional pre-plan package (Open question 1).
- Whether the decompose-and-audit loop needs an interim stop rule until the heuristic (`000445`,
  `phase-irs-05`) exists (Open question 2).
- Whether `GOV-018`, `GOV-014`, `GOV-002` or the backlog schema change to match the owner's step
  order, or the order changes to match them (Open questions 3 and 4).

Assumptions:

- G2 needed no question. `ARCH-006`'s G2 ("Track acceptance": the partition's tracks and
  new-plan-vs-amendment rulings stand) is the gate the owner calls "partition acceptance".
  `ARCH-006`'s own authority model uses the words "partition acceptance". The document uses
  `ARCH-006`'s name with the owner's wording in brackets after it.
- `systems: [sys-gov-docs]` (governance-document authoring, as on `GOV-010`).
- Per the prompt, `GOV-021` states near its top that it was written in an unclaimed session. The
  owner may want that line removed when approving the document.
