# Handoff: planning protocol document (idea 000500)

*Ran unclaimed: owner-directed work with no backlog phase; no peer holds a lock against it.*

## 1. Branch and tip

- Branch: `agent/cloud-planning-protocol`
- Tip when the final gates ran: `62c7444`. This handoff commit sits directly on top of it; it changes
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
the two it relies on), `a04ec06` (first handoff, review open), `62c7444` (fixes for review findings
F1 to F5).

## 3. Codes allocated with `--next-code`

- `GOV-021` (`uv run python -m src.governance --next-code governance`, run once). The local
  Session Manager should check it is still free on current `dev`.

## 4. Review verdict

**Agent type:** `partition-adversary`, dispatched with model Sonnet (owner direction: `GOV-008`
cost protocols and agent hygiene). **Brief:** the prompt's brief verbatim ("Adversarial review"
in `planning-protocol.md`), `{ABS}` = `/home/user/d-system`, `<file>` =
`GOV-021-planning-protocol.md`, plus the owner's four 2026-09-28 answers stated as rulings for the
fidelity check. It received no account of the drafting session's reasoning. The work was
committed and pushed before dispatch.

The first attempt, before the session restarted, failed: `Agent type 'partition-adversary' not
found`. The session had loaded its agent types from `claude/master-prompt-execution-udywbn`, cut
from `main` at `6a9ab96` (2026-09-12), which has no `partition-adversary.md`. After the restart
the type was available, and the owner directed the run.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| F1 | blocker | Step 17 said the owner runs `/session-close`. `GOV-003` ("Coordinator completion replaces owner-invoked /session-close, repository-wide", owner, 2026-09-16) and `.claude/commands/session-close.md` let a coordinator complete a phase once three conditions hold; `ARCH-006`'s G5 row is stale | `fixed` in `62c7444`. The session confirmed the quotes. Step 17 now says `/session-close` is the only path and does not name who runs it; new Open question 6 records `GOV-003` against `ARCH-006` and `AGENTS.md`. Not settled here, because `AGENTS.md` also disagrees with `GOV-003` (section 6) |
| F2 | major | Step 10 cited `ARCH-006` stage 6 for the later-added-phase review; that altitude is stage 5 | `fixed` in `62c7444`: stage 6 cited for splits, stage 5 (third altitude) for later-added phases |
| F3 | minor | The 2026-09-28 owner rulings were not marked **Owner ruling** like the 2026-09-27 ones | `fixed` in `62c7444`: the intro names both sets; step 4 and Open questions 3 to 5 carry **Owner ruling, 2026-09-28** |
| F4 | minor | Step 11's `GOV-002` citations cover how `systems` and `depends_on` are used, not the validator that checks them | `fixed` in `62c7444`: step 11 names the `src.governance` validator and `ARCH-006` stage 7's "Rides on" column; the `GOV-002` citations stay for the field semantics |
| F5 | minor | "The gate model" shortened a heading every other citation quotes in full | `fixed` in `62c7444`: full heading quoted |

The adversary reported these checks as holding: fidelity to idea `000500`'s findings and the
2026-09-28 rulings; coverage of all nine `ARCH-006` stages and gates G1 to G5; every "queued"
phase is queued on the backlog; no invented rules; nothing decided for `000501`, `000502` or
`000505`. The fixes did not change step order, so the review was not re-dispatched.

## 5. Gate runs (last ten lines each, verbatim)

Two full runs. The first ran at `4d83a82`, before the review, and all four gates passed with
the same output as below except pytest's time (146.99s). The second, below, ran at `62c7444`
after the review fixes, following `git rebase origin/dev` (up to date at `a34e8f3`).

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
============ 1151 passed, 1 skipped, 1 warning in 148.16s (0:02:28) ============
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
- **`ARCH-006`, the G5 row.** It reads: "the owner runs `/session-close` over a queue of finished
  phases in one sitting. No standing owner-only rule is delegated". `GOV-003` superseded that on
  2026-09-16 ("Coordinator completion replaces owner-invoked /session-close,
  repository-wide"). Found by review finding F1; `GOV-021` Open question 6.
- **`AGENTS.md`, "Session backlog", line 180: needs the owner's approval, not edited.** It reads:
  "It is safe to record progress any number of times, but do not mark a phase complete; only the
  owner-invoked review (e.g., `/session-close`) does that. An agent must never invoke final
  closure itself." That contradicts `GOV-003`'s 2026-09-16 decision. Proposed wording, if the
  owner confirms `GOV-003` stands: "It is safe to record progress any number of times, but do not
  mark a phase complete; only `/session-close` does that, invoked by the owner or by a coordinator
  once the three conditions in `GOV-003` ('Coordinator completion replaces owner-invoked
  /session-close') hold. No other agent invokes final closure." If the owner meant `AGENTS.md` to
  stand, `GOV-003` and `session-close.md` need amending instead.

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
5. The adversarial review was first left open rather than substituted; after the session
   restarted, the owner directed the run with Sonnet under `GOV-008`'s cost and agent-hygiene
   rules (section 4).

Still open for the owner (`GOV-021`, "Open questions"):

- Whether and when to amend `GOV-008` for the optional pre-plan package (Open question 1).
- Whether the decompose-and-audit loop needs an interim stop rule until the heuristic (`000445`,
  `phase-irs-05`) exists (Open question 2).
- Who may run `/session-close`: `GOV-003` against `ARCH-006` and `AGENTS.md` (Open question 6,
  and section 6).
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
