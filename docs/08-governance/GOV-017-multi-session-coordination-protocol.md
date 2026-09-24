---
schema_version: 1
id: doc-multi-session-coordination-protocol
code: GOV-017
title: Multi-session coordination protocol — roles, the primary-checkout lock and the message contract
kind: governance
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-24'
systems: [sys-governance, sys-backlog]
depends_on: [doc-adr-multi-agent-concurrency, doc-coordinator-protocol, doc-build-coordinator, doc-backlog-decisions, doc-conversation-guidelines, doc-governance-operations]
---

# Multi-session coordination protocol

How the owner runs several interactive Claude Code sessions against this repository at once, with
one session coordinating the rest. It covers the session roles, how access to the primary checkout
is serialized, how claim slots are allocated, how merges reach the owner, and the exact messages
sessions exchange.

`AGENTS.md` governs what each agent may do. This document governs how several sessions take turns at
the parts of the work that cannot run in parallel. Where it departs from `AGENTS.md`, the departure is
an owner ruling, listed under *Departures from AGENTS.md* below and recorded in `GOV-003`. `GOV-013` and `PROMPT-036` govern a single coordinator that dispatches subagents; this
governs several top-level sessions, one of which may be running `PROMPT-036`.

The starter messages that put this protocol into effect are in
[PROMPT-037](../02-prompts/PROMPT-037-session-manager-starter-messages.md). This document says what
the rules are and why; that one carries the text sent to each session.

It was written on 2026-09-22, from the owner's rulings in the first session that ran this way.

## Departures from AGENTS.md

Each of these is an owner ruling of 2026-09-22, recorded in
[GOV-003](GOV-003-backlog-decisions.md). They apply only while sessions run under this protocol.

1. **Ideation commits ideas in the primary checkout**, inside a granted turn. `AGENTS.md` limits the
   primary checkout to claim commits and the catalog regeneration they force.
2. **Report files under `_working/session-manager/` are written in the primary checkout** by the
   Session Manager, the Scout and the Standby Builder, without a turn. The path is gitignored and
   never committed, so it cannot collide with a claim, a merge or an idea commit.
3. **Builders build the phase the Session Manager assigns**, not the first ready phase in the
   rendered order. The Session Manager assigns in rendered queue order among conflict-free phases.
4. **Merge approval is relayed.** `AGENTS.md` step 8 says to ask the owner before integrating. Under
   this protocol a `GRANTED merge` from the Session Manager is the owner's approval, for every
   session, including where `/session-start` or `PROMPT-036` says to ask the owner in the session.
5. **A batch table's `status` and `updated` lines are committed in the primary checkout** inside a `batch` turn, as
   `PROMPT-036` requires when it opens or closes a batch (owner ruling, 2026-09-22, later that night).
6. **Preflight tests run in the worktree.** `/session-start` step 1 (via `/backlog`) and `PROMPT-036`
   preflight step 2 run `uv run pytest` in the primary checkout. Under this protocol that run happens
   in the session's worktree, after it is created.

## The sessions

There are two groups. **Meta sessions** coordinate, capture and plan; they never claim a backlog
phase. **Execution sessions** build backlog phases.

| Session | Group | Role | Claim slot |
|---|---|---|---|
| Session Manager | meta | Holds the primary-checkout lock, allocates claim slots, relays merges to the owner, keeps the board | never |
| Ideation | meta | Records ideas through the sanctioned writer; triages open ideas when none are waiting; builds nothing | never |
| Prompt Planner | meta | Writes the prompts the owner runs in execution sessions; builds nothing | never |
| Session 5 - Batch Runner | execution | Runs `PROMPT-036` through the batch tables in order | one at a time |
| Session 1 - Builder A | execution | Builds one assigned conflict-free phase at a time through `/session-start` and `/session-close` | one |
| Session 2 - Builder B | execution | As Builder A | one |
| Session 3 - Standby Builder | execution | First in line for the next free slot; until then, reviews queued phases with `PROMPT-035` | none until assigned |
| Session 4 - Scout | execution | Read-only: candidate phases, batch reconnaissance, worktree and branch audits | never |

### Why these roles

- **System overlap blocks more phases than the claim limit does.** `max_active` stays at 3. On 2026-09-22,
  46 of 74 ready phases were blocked by a single active claim because they shared its system. More
  slots help only where that many mutually disjoint phases exist, and every extra claim adds rebases
  and merge approvals. The Batch Runner's batches run one phase at a time, so it needs one slot; the
  two Builders take the other two.
- **No dedicated reviewer session.** Both build paths already require an independent review before
  a phase completes: `PROMPT-036` step 6 dispatches an adversary, and `/session-close` step 3
  launches a review sub-agent. A reviewer session would repeat that work. The one check those reviews
  cannot make — whether a branch still passes after peers' merges — the Session Manager makes itself
  as part of the merge gate below.
- **A standby builder instead of a third builder.** A third builder would have no slot to claim.
  The standby builder is ready the moment a slot frees and does claim-free review work until then.
- **A scout.** Finding phases that are disjoint from each other and from active claims, and noticing
  where the Conflicts column is wrong, takes reading that would otherwise fill the Session Manager's
  context.

## Session names

Sessions address each other by their **registered name**, which is the name `ListAgents` shows. It
is set with `/rename <name>` inside the session, in the terminal. On 2026-09-22, as the owner
reported, a rename made from the Remote Control mobile client changed only the name shown on that
device; the registered name
stayed the auto-generated title, and the Session Manager could not tell which session was meant.

A session's `[ref]` in `ListAgents` does not change when it is renamed, and every received message
carries the sender's registered name. The first message to a session asks it to state its phase and
agent id, so a wrong link is found before it acts on role instructions.

## The primary-checkout lock

The primary checkout (`/code/d-system` on `dev`) is where claims, the catalog regeneration they
force, integrations, idea records and batch-table status changes are committed. Only one session writes there at a time.

- Any session may **read** there, including `uv run python -m src.governance` and `--ready`.
- To **write** — commit, merge, regenerate, or switch anything — a session asks for a turn
  (reports under `_working/session-manager/` excepted; see *Departures*), does
  only the purpose it stated, leaves `git status` clean, and reports the resulting commit.
- Before granting a turn, the Session Manager checks that the checkout is on `dev` and clean. After
  the holder reports, it checks that the commit landed and nothing else changed.
- **No tests, rebuilds or `pytest` in the primary checkout, by any session.**
  `test/test_codes.py` overwrites the tracked `docs/08-governance/catalog.md` while it runs and
  restores it afterwards. On 2026-09-22 two `/session-start` preflight runs overlapped there and
  left the catalog holding only `CORRUPTED` (ideas `000324`, `000325`). Tests run in the session's
  own worktree, including the preflight that `/session-start` and `PROMPT-036` would otherwise run
  in the primary checkout.
- **One `pytest` run at a time per worktree**, for the same reason: the tests resolve the catalog
  path to whichever checkout they run in, so two overlapping runs corrupt that worktree's catalog.
  Before a commit that is not meant to change the catalog, `git diff --exit-code
  docs/08-governance/catalog.md` confirms a test run did not leave it altered. A commit that does
  change it regenerates it with `--catalog` rather than keeping whatever is on disk.

## Claim slots

The Session Manager allocates the three slots. Builders do not pick from `--ready` themselves; they
wait for an assignment. Before assigning, the Session Manager checks that the phase's Conflicts
column is empty against every active claim, and takes the earliest such phase in the rendered queue
order (`next_up` first). **The owner approves each assignment** before it is sent. `/session-start`'s
own claim-approval question still goes to the owner as written.

The Conflicts column compares a phase only against phases already active, and only through their
declared systems and deliverable paths (`collisions()` in `src/governance/backlog.py`). It therefore
misses a phase assigned but not yet claimed, and files a phase will edit without declaring them. The
Scout's candidate reports check both against the assignments in flight and name such hazards, and **two phases a Scout report flags as overlapping never run at the same time**, even
when the Conflicts column is empty.

Two notices keep slot allocation ahead of new work: the Batch Runner sends `NEXT-BATCH` before it
opens another batch, and Prompt Planner sends `PROMPT-FOR` before the owner pastes a prompt into an
execution session, so the Session Manager can check it against that session's role, slot and the
lock. All three rules in this section are owner rulings of 2026-09-22.

## The merge gate

A branch reaches `dev` only with the owner's approval, as `AGENTS.md` requires. Approval is relayed:

1. The session sends `READY` with the phase's own review verdict — every finding either fixed or
   explicitly accepted — and the tail of its post-rebase runs of the four gate checks:
   `uv run python -m src.governance`, `uv run pytest`, `uv run ruff check src/ test/` and
   `uv run mypy src/`. `dev`'s baseline is 0 ruff findings and 0 mypy errors, so each check must report
   zero findings; matching the previous count is not enough.
2. The Session Manager re-runs the four gate checks on the branch tip in a detached temporary
   worktree (`git worktree add --detach ../d-system-worktrees/verify-<phase-id> <branch>`, removed
   afterwards), so it touches neither the primary checkout nor the session's worktree.
3. The Session Manager brings the merge to the owner with the session's and its own results for the
   four gate checks and `git diff --stat dev..<branch>`.
4. On the owner's yes, it sends `GRANTED merge` and gives the session the lock. If `dev` has moved
   since step 2, the session rebases and re-runs the four gate checks while holding the lock, and
   reports the new tip; the Session Manager re-runs step 2 on that tip before the session
   fast-forwards. Nothing else can land on `dev` while the session holds the lock.
5. Before the fast-forward, the session runs
   `uv run python tools/git-hooks/refuse_dirty_integration.py` in the primary checkout and continues
   only if it exits 0. This is `AGENTS.md` step 9's check (see `OPS-001`), restated here because the
   merge turn is where it runs under this protocol.
6. Inside the same turn the session fast-forwards `dev` and makes the completion edit — one small
   commit on `dev` immediately after the integration, as `GOV-003` sanctions (entry "Coordinator completion replaces
   owner-invoked /session-close, repository-wide"). The edit moves the phase's status, so the session
   regenerates the catalog with `uv run python -m src.governance --catalog` and commits it in the same
   commit, then runs `governance` on `dev`; no `pytest`. Then it sends `TURN DONE`. A completion edit
   that skipped the regeneration left `dev` red on 2026-09-23 (`f6216e9`, ideas `000405`, `000406`);
   since `phase-grd-01` the governance check and the pre-commit hook both refuse a stale catalog.
7. After the merge lands, the Session Manager sends `REBASE` to every session with an open branch.

**Owner ruling, 2026-09-22:** a `GRANTED merge` relayed by the Session Manager is the owner's
approval, as a standing rule for every session.

**Owner ruling, 2026-09-23:** the gate checks include `ruff` and `mypy` alongside `governance` and
`pytest` (steps 1, 2 and 4), and the dirty-integration check runs before every fast-forward
(step 5). Both are recorded in `GOV-003`.

**Owner ruling, 2026-09-23:** a failing pre-commit hook is never bypassed with `--no-verify`. The
session commits the fix; if the check itself is wrong, it stops and reports to the Session Manager
and the owner. The hook (`tools/git-hooks/pre-commit`, `OPS-009`) runs the private-content check
and the governance check, so a stale `catalog.md` or `ideas.md` refuses the commit (`REQ-028` R04,
R13). `core.hooksPath` is shared, so every worktree runs the primary checkout's copy of the hook.

## Ideas

A session that meets an idea outside its work sends the bare idea to Ideation, one message per idea,
with its own session name, and does not record it. Ideation records ideas through
`tools/append_idea.py` in the primary checkout, which needs a turn, and batches waiting ideas into
one turn. The message that carries an idea to Ideation is `IDEA`. When no idea is waiting, Ideation
triages open ideas with `/idea-triage` (owner ruling, 2026-09-22): the scouts are read-only, and the
findings and status moves are written in one idea turn. Recording a new idea comes before triage. It takes each id from the tool's output and sends it back to the originating session and
to the Session Manager.

## The message contract

The first line of every message is its type and subject. All messages to the Session Manager are
sent to the name `Session Manager`.

| Message | From | Meaning |
|---|---|---|
| `ACK <session> <state>` | any | Orientation received; states phase, branch and worktree, or none |
| `TURN? <claim\|idea\|batch\|dryrun> <phase or batch-id>` | any | Asks for the primary-checkout lock for one stated purpose. The catalog regeneration travels with the claim; `batch` covers only a batch table's `status` and `updated` lines, as `PROMPT-036` sets them when it opens or closes a batch; `dryrun` runs a merged skill or workflow in the primary checkout for a phase's acceptance evidence, writing only gitignored paths and committing nothing (owner ruling, 2026-09-22, first used by `phase-part-03`); merges go through `READY` |
| `GRANTED <purpose>` | Session Manager | The recipient holds the lock; states the `dev` commit it was granted at |
| `QUEUED <n>` | Session Manager | The recipient is n-th in line |
| `TURN DONE <sha>` | lock holder | Lock released; the checkout is clean |
| `READY <branch>` | builder, batch runner | Ready to integrate, with the review findings resolved and post-rebase output |
| `GRANTED merge` | Session Manager | The owner approved; the recipient holds the lock for the merge and completion edit, and ends the turn with `TURN DONE` |
| `REBASE` | Session Manager | `dev` moved; rebase at the next safe point |
| `ASSIGN <phase-id>` | Session Manager | An owner-approved phase to build |
| `REVIEW <phase-ids>` | Session Manager | Claim-free review work for the standby builder |
| `CANDIDATES?` | Session Manager | Asks the Scout for conflict-free candidate phases |
| `REPORT <file>` | scout, standby | A report written under `_working/session-manager/`, with a short summary |
| `NEXT-BATCH <batch-id>` | batch runner | About to open another batch; the Session Manager checks slots first |
| `PROMPT-FOR <session> <what>` | Prompt Planner | A prompt meant for that session, to be checked against its role before the owner pastes it |
| `IDEA` / `IDEA-RECORDED <id> <title> from <session>` | any / Ideation | An idea to record / the id it was recorded under |
| `BLOCKED <reason>` | any | Stuck on something outside the sender's worktree |
| `FREE` | execution | No assignment |

## State and resumption

The Session Manager keeps a board at `_working/session-manager/board.md`: roster, claim slots, lock
holder and queue, pending merges, incidents and open items. Scout reports go under
`_working/session-manager/scout/`, and Standby Builder reviews under
`_working/session-manager/reviews/<phase-id>.md` rather than where `PROMPT-035` would put them. All of it is gitignored
and ephemeral; the backlog on `dev` stays the lock table, and this document is the durable record of
the protocol.

To start or resume the arrangement:

1. Open the sessions and set each registered name with `/rename`, in the terminal, exactly as in the
   table above.
2. In the Session Manager, paste the kickoff from `PROMPT-037`. It reads the board if one exists,
   runs `ListAgents`, and checks every name.
3. The Session Manager shows the owner the starter messages from `PROMPT-037` and sends them once
   approved. Each session replies with `ACK`, which re-establishes who holds what.
4. Active claims in `backlog.yaml` are authoritative over the board. A claim the board does not
   explain is asked about, never released.
