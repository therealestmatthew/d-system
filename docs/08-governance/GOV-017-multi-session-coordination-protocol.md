---
schema_version: 1
id: doc-multi-session-coordination-protocol
code: GOV-017
title: Multi-session coordination protocol — roles, the primary-checkout lock and the message contract
kind: governance
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-10-05'
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
   Session Manager, the Scout, the Standby Builder and the Owner Terminal (its command queue), without a
   turn. The path is gitignored and
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

There are three groups. **Meta sessions** coordinate, capture and plan; they never claim a backlog
phase. **Execution sessions** build backlog phases. The optional **owner** session, the Owner Terminal,
runs commands reserved to the owner; it takes no turns and builds nothing.

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
| Owner Terminal | owner | Runs the owner-only commands the Session Manager queues, each approved by the owner in that session (optional; see *The Owner Terminal*) | never |

### Why these roles

- **System overlap blocks more phases than the claim limit does.** `max_active` stays at 3. On 2026-09-22,
  46 of 74 ready phases were blocked by a single active claim because they shared its system. More
  slots help only where that many mutually disjoint phases exist, and every extra claim adds rebases
  and merge approvals. The Batch Runner's batches run one phase at a time, so it needs one slot; the
  two Builders take the other two.
- **No dedicated reviewer session.** Build reviews are subagents the Session Manager dispatches, as
  *Build reviews* below requires: the session that built a phase asks for its review and never
  dispatches it. A reviewer session would add a second coordinator for the same dispatches. The one
  check a review cannot make — whether a branch still passes after peers' merges — the Session
  Manager makes itself as part of the merge gate below.
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
  the holder reports, it checks that the commit landed, that `origin/dev` equals `dev`, and that
  nothing else changed.
- **The lock holder pushes `dev` to `origin` before sending `TURN DONE`.** CI runs on a push, so an
  unpushed commit has no CI result and the next grant cannot be checked. If the push is refused or
  blocked, the holder sends `BLOCKED`, keeps the turn, and asks the owner.
- **`dev` must be green before a `claim`, `dryrun` or `merge` grant.** Before sending any of these
  `GRANTED` messages, the Session Manager runs `uv run python tools/check_dev_ci.py --wait 600`
  ([OPS-025](OPS-025-check-dev-ci.md)) and grants only on exit 0. Exit 1 means the latest CI run for
  `dev`'s head failed: the only grant allowed is the turn or merge the owner names as the fix, and
  the owner's ruling and the run URL the tool prints are recorded on the board. Exit 2 means the
  result is still not known after the wait (CI still running, a cancelled run, `dev` not pushed, or
  `gh` failed): no grant until the result is known, or until the owner rules for that grant. `idea`
  and `batch` turns are not gated. They cannot spread a red build, and an `idea` turn is how a red
  build gets recorded. These are owner rulings of 2026-09-24 (`REQ-028` R06, `PLAN-045` D6).
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

## Build reviews

**The assurance dispatch rule.** Every build review is dispatched and briefed by the coordinator,
never by the session that built the phase (`REQ-030` R03, `PLAN-047` D3). Under this protocol the
coordinator is the Session Manager. A building session sends `REVIEW-REQUEST` and waits for
`VERDICT`. When the owner runs `/session-close` in their own session, that session did not build the
phase and may dispatch directly, under the same brief rule. A `PROMPT-036` run outside this protocol
is the coordinator for the phases its creators built, and dispatches under the same rule. Run as the
Batch Runner under this protocol, it sends `REVIEW-REQUEST` like a Builder.

**The brief.** The brief is the reviewer's whole input. It holds:

- the phase id and its `scope`, `acceptance` and `verification` entries, copied from `dev`'s
  `backlog.yaml`;
- the commit range under review and the output of `git diff <range>`. The judge has no shell, so
  the diff text itself goes in the brief;
- the path to the runner's `manifest.json` under `_working/review-checks/<phase-id>/<commit12>/`.
  Each entry's `file` is relative to the root of the checkout that ran the runner, and every
  evidence file sits beside the manifest;
- for the gating reviewer only, the path of a checkout of the branch at the reviewed commit, so it
  can run commands. The coordinator makes it, as a scratch clone (`git clone --shared` of the
  primary checkout, then a checkout of that commit), and removes it after the review. It is never
  the builder's worktree, which may hold uncommitted state. The shadow judge has no shell and
  gets no checkout.

A checkout of the branch contains the builder's session record and its commit history. The brief
tells the gating reviewer not to read either: not the phase's record under `docs/03-sessions/`, and
not `git log` or commit messages.

The brief may not contain anything the builder wrote: not the session record, not commit messages or
`git log` output, not the text of `REVIEW-REQUEST` or `READY` beyond the branch and its tip, not a
summary of what the builder says it did or why, and not the builder's own review. A reviewer that
reads the builder's account judges the account instead of the work (owner ruling, 2026-09-23).

**The review.** On `REVIEW-REQUEST`, the Session Manager:

1. runs `uv run python tools/run_review_checks.py <phase-id> <tip>`
   ([OPS-029](OPS-029-run-review-checks.md)), which runs the phase's `verification` list and the
   four gate checks at the tip in a detached worktree and writes the manifest;
2. dispatches the **gating reviewer** — a dedicated reviewer type, `demo-adversary` or
   `demo-validator-code`, never a `general-purpose` agent — and, during shadow, the **shadow
   judge**, `review-judge`. Both get the same brief, except that only the gating reviewer gets the
   checkout. Before the first dispatch of a run, check that
   `review-judge` is among the available agent types;
3. writes one verdict record per reviewer, named `<verdict_id>.json` and valid against
   `schemas/review-verdict.schema.json` (`REQ-030` R05, `PLAN-047` D4), into the staging directory
   `_working/session-manager/verdicts-pending/<phase-id>/` in the primary checkout. That path is
   gitignored, so writing there needs no turn (*Departures*, item 2); the runner's worktree is
   already gone, and a record written onto `dev` would put an unmerged phase's record there. It
   copies each finding without changing it, keeps the reviewer's raw reply as an evidence file under
   `_working/session-manager/review-replies/`, and puts that reply's sha256 in the record. The
   gating reviewer's record carries `gating: true`; the judge's carries `gating: false`;
4. records each verdict record's sha256 in `_working/session-manager/verdicts.sha256`, one
   `sha256sum` line per file, giving the path the record will have on the branch,
   `docs/08-governance/reviews/verdicts/<verdict_id>.json`. It sends `VERDICT` with the staged paths
   and their sha256.

The building session copies each staged record unchanged into its worktree at
`docs/08-governance/reviews/verdicts/<verdict_id>.json` and commits it on its branch; the directory
is created by the first record copied. It fixes or explicitly accepts
each finding; a `reject` verdict means a fix and a new `REVIEW-REQUEST`, which produces new records
beside the old ones. Every build review is recorded this way, gating and shadow alike (`REQ-030`
R05, R06), from `phase-asr-04` on. A sampled re-review (`PLAN-047` D6,
[OPS-030](OPS-030-draw-rereview-sample.md)) is recorded the same way with `gating: false`, because
the merge it would have decided has already happened.

**Leaving shadow.** The judge's verdicts decide nothing while it runs in shadow. It leaves shadow
when the owner decides so on a comparison table built from the verdict records, after at least ten
reviewed phases, and that decision is recorded in `GOV-003` (owner ruling at G3, 2026-09-24).
Until then every build review runs both reviewers, and only the gating verdict decides.

## The merge gate

A branch reaches `dev` only with the owner's approval, as `AGENTS.md` requires. Approval is relayed:

1. The session sends `READY` with the paths of the verdict records the Session Manager handed it,
   committed unchanged on the branch, and every finding either fixed or explicitly accepted. The
   records come from the review in *Build reviews*: the runner, then the gating reviewer and, during
   shadow, the shadow judge `review-judge`, on the same brief. It also sends the tail of its
   post-rebase runs of the four gate checks:
   `uv run python -m src.governance`, `uv run pytest`, `uv run ruff check src/ test/ tools/` and
   `uv run mypy src/`. `dev`'s baseline is 0 ruff findings and 0 mypy errors, so each check must report
   zero findings; matching the previous count is not enough.

   `READY` also carries the output of two branch checks run after the rebase (`REQ-028` R07, R08,
   R10; `PLAN-045` D7, D9):

   - the test baseline, `uv run python tools/check_test_baseline.py <base.xml> <branch.xml>`, where
     the session produces both JUnit reports itself: the base from `uv run pytest --junitxml` on
     `dev`'s tip in a temporary `git clone --shared`, deleted afterwards, the branch from the
     rebased branch
     ([OPS-031](OPS-031-check-test-baseline.md));
   - the diff patterns, `uv run python tools/check_diff_patterns.py dev..HEAD`
     ([OPS-032](OPS-032-check-diff-patterns.md)).

   A nonzero result from either blocks the merge unless the owner signs off, and the sign-off names
   the tests or lines it accepts. The session records that sign-off in its session record before the
   merge; the Session Manager relays no `GRANTED merge` for a branch with an unsigned nonzero result.
   For a claimed phase, `READY` also carries the report of
   `uv run python -m src.governance --containment <phase-id>`, which diffs the active branch against
   the phase's declared paths (`phase-dgov-06`, `REQ-015` R12-R13). That report never blocks.
2. The Session Manager re-runs the checks on the branch tip with the review runner,
   `uv run python tools/run_review_checks.py <phase-id> <tip>`. Its manifest is this step's re-run:
   it runs the phase's `verification` list and the four gate checks in a detached worktree it
   removes afterwards, so it touches neither the primary checkout nor the session's worktree
   (`PLAN-047` D2). A branch with no phase has nothing for the runner to read, so for unclaimed work
   the Session Manager re-runs the four gate checks in a detached temporary worktree
   (`git worktree add --detach ../d-system-worktrees/verify-<slug> <branch>`, removed afterwards).

   In the same step it checks the verdict records against the commit itself, so no checkout is
   needed after the runner removes its worktree. For each of this phase's lines in
   `_working/session-manager/verdicts.sha256`, it runs `git show <tip>:<path> | sha256sum` in the
   primary checkout, which reads the branch's committed blob without switching anything. Each must
   print the recorded sha256. A different sha256, or a recorded path missing at the tip, refuses the
   branch. The Session Manager names the file and reports the difference to the owner as a finding
   (`REQ-030` R10, `PLAN-047` D4).
3. The Session Manager brings the merge to the owner with the session's results, its own runner
   manifest, the gating reviewer's verdict and the shadow judge's verdict, the verdict-record check,
   and `git diff --stat dev..<branch>`. Only the gating verdict decides.
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

**Owner ruling, 2026-10-04:** the session produces both JUnit reports for the test baseline (step
1): the base on `dev`'s tip in a temporary shared clone and the branch after the rebase. It
replaces `PLAN-045` D7's "the Session Manager's own merge-gate re-run on `dev`", which cannot be the
base because that re-run tests the branch tip and comes after `READY`. Recorded in `GOV-003`.

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

## The Owner Terminal

Some commands only the owner may run: pushing `dev`, deleting `origin` branches, and writing paths a
deny rule closes to agents (`.agents/`, `.codex/`). An agent session in auto mode is refused these,
and the owner cannot type them while working from the Remote Control mobile client. The Owner
Terminal is the way to run them. It is a Claude Code session in the manual permission mode,
connected through Remote Control, so the owner approves every tool call it makes from wherever they
are. It is optional: the arrangement runs without it when the owner is at the terminal.

The owner's approval in the Owner Terminal is the authorization for each command. The Session Manager
queues only commands reserved to the owner, such as a push of `dev`, which agent sessions are refused
by design. It never queues a command the owner declined, and never uses the queue to run work that
belongs to an agent session.

**Starting it.** The owner starts it in a terminal on this machine:
`claude --permission-mode manual --remote-control "Owner Terminal"`. When the owner is away from the
terminal, the Session Manager may start or resume it on the owner's explicit request, detached under a
pseudo-terminal, for example
`setsid script -qfc "claude --resume <session-id> --permission-mode manual --remote-control 'Owner Terminal'" /dev/null`
(this machine has no tmux). The 2026-09-30 relaunch used `--permission-mode default`, which the CLI accepts
but does not list; `manual` is the documented value. The first Owner Terminal, launched from a Codex
session, ended when that process exited; the relaunch under `setsid` kept running. Check `ListAgents`
after any start.

**The queue.** The Owner Terminal keeps a running list at
`_working/session-manager/owner-terminal-queue.md` (gitignored). Each entry has an id (`C1`, `C2`, ...),
a purpose, the exact command, a precondition, a status and the result. It records each entry the
Session Manager sends as `queued` and runs one only when the owner tells it to in its own session.

**Commands that touch `dev`** (a push) carry the precondition *SM GO*. The Owner Terminal asks
`GO? <id>`, and the Session Manager answers `GO <id>` only when the primary checkout is clean and no
session holds the lock, then grants nothing else until the result is reported. Other commands run in
the order the owner chooses.

**Reporting.** After each command the Owner Terminal updates the queue file and sends the Session
Manager `DONE <id>` or `FAILED <id>` with the real output. A failed or refused command is not retried
and not worked around. The Owner Terminal never commits, merges, rebases or edits tracked files, and
runs no tests in the primary checkout.

**Limits seen on 2026-09-30.** Messages to it travel over Remote Control: delivery is not confirmed
and `notify_when_idle` is not supported, so the Session Manager checks results against the repository
(`git ls-remote`, the worktree) rather than waiting for a reply. It once ran two commands and reported
neither until asked; the Session Manager found the push by checking `origin`.

## The message contract

The first line of every message is its type and subject. All messages to the Session Manager are
sent to the name `Session Manager`.

| Message | From | Meaning |
|---|---|---|
| `ACK <session> <state>` | any | Orientation received; states phase, branch and worktree, or none |
| `TURN? <claim\|idea\|batch\|dryrun> <phase or batch-id>` | any | Asks for the primary-checkout lock for one stated purpose. The catalog regeneration travels with the claim; `batch` covers only a batch table's `status` and `updated` lines, as `PROMPT-036` sets them when it opens or closes a batch; `dryrun` runs a merged skill or workflow in the primary checkout for a phase's acceptance evidence, writing only gitignored paths and committing nothing (owner ruling, 2026-09-22, first used by `phase-part-03`); merges go through `READY` |
| `GRANTED <purpose>` | Session Manager | The recipient holds the lock; states the `dev` commit it was granted at |
| `QUEUED <n>` | Session Manager | The recipient is n-th in line |
| `TURN DONE <sha>` | lock holder | Lock released; the checkout is clean and `dev` is pushed to `origin` |
| `REVIEW-REQUEST <branch> <tip>` | builder, batch runner | Asks the Session Manager for the phase's build review at that commit. Not `REVIEW`, which assigns standby work |
| `VERDICT <phase-id>` | Session Manager | The build review is done: each verdict record's path, its sha256 and its verdict, gating and shadow. The session commits the records unchanged |
| `READY <branch>` | builder, batch runner | Ready to integrate, with the verdict records committed unchanged, their findings resolved, and post-rebase output |
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
| `QUEUE <id>` | Session Manager | An owner-only command for the Owner Terminal to record: purpose, command, precondition |
| `GO? <id>` / `GO <id>` | Owner Terminal / Session Manager | The precondition check before a command that touches `dev`, and its answer |
| `DONE <id>` / `FAILED <id>` | Owner Terminal | The command ran, with its output, or failed or was refused, with the message |

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
