# Multi-session coordination

How the owner runs several interactive sessions against one repository at once. One of them, the
Session Manager, coordinates the rest: session roles, serialized access to the primary checkout,
claim slots, merge relay and the message contract.

This is a procedure the owner and the sessions follow. The plugin supplies no lock, no relay and no
messaging: the backlog on the integration branch stays the only lock table (`backlog-protocol.md`,
section 6), and sessions message each other through the host's cross-session messaging, addressed
by registered name. The protocol runs only where the host provides that messaging.

`protocol.md` and `backlog-protocol.md` govern each session. This document governs how sessions take
turns at the work that cannot run in parallel, and a rule here applies only while sessions run
under it. `coordinator.md` governs one coordinator dispatching subagents; here, several top-level
sessions run, one of which may run a coordinator. The kickoff and starter messages are in
`session-manager-messages.md`.

## 1. Sessions and roles

Meta sessions coordinate, capture and plan, and never claim a phase. Execution sessions build
phases.

| Role | Kind | Claim slots | Does |
|---|---|---|---|
| Session Manager | meta | none | Holds the primary-checkout lock, allocates claim slots, relays merges to the owner, keeps the board |
| Ideation | meta | none | Records ideas; triages open ideas the owner names when none are waiting |
| Prompt Planner | meta | none | Writes the prompts the owner runs in execution sessions |
| Batch Runner | execution | one at a time | Runs the coordinator through its batches one phase at a time (`coordinator.md`, `batches.md`) |
| Builder | execution | one | Builds the phase the Session Manager assigns |
| Standby Builder | execution | none until assigned | First in line for the next free slot; until then, reviews queued phases against the phase-altitude checks (`plan-review.md`, section 3) and reports findings, writing no dispositions; section 4 bounds any backlog edit |
| Scout | execution | none | Read-only: finds conflict-free candidate phases, reconnoitres batches, audits worktrees and branches |

There is no reviewer session. Each build path's own independent review is the phase review
(`backlog-protocol.md`, section 10); the Session Manager's re-run at the merge gate covers whether a
branch still passes after peers' merges.

## 2. Session names

- Sessions address each other by registered name, the name the host's session listing shows. It is
  set in the session's own terminal.
- Renaming a session leaves its listing reference unchanged. Every received message carries the
  sender's registered name.
- The first message to a session asks it to state its phase and agent id, so a wrong link is found
  before the session acts on role instructions.

## 3. The primary-checkout lock

- One session writes in the primary checkout at a time. Any session may read there, including
  running the check and the ready queue.
- To write (commit, merge, regenerate or switch anything), a session sends `TURN?` with one stated
  purpose, does only that, leaves `git status` clean and reports the commit.
- Before granting a turn, the Session Manager confirms the checkout is on the integration branch
  and clean. After the holder reports, it confirms the commit landed and nothing else changed.
- The turn purposes are the complete list of primary-checkout work while this protocol runs:
  - `claim`: a claim, a widening of a phase's declarations, or the release of a claim when a phase
    is handed back as interrupted, with the catalog regeneration each forces;
  - `idea`: Ideation records waiting ideas, or the triage findings and moves for ideas the owner
    named, through the `idea` and `idea-triage` skills;
  - `dryrun`: a merged skill runs to gather a phase's acceptance evidence, writing only ignored
    paths and committing nothing;
  - a merge, which does not use `TURN?`: it goes through `READY` and the merge gate (section 6).
- The Session Manager, the Scout and the Standby Builder write reports in the primary checkout's
  ignored report directory without a turn. Reports are never committed.

## 4. Tests

- While sessions run under this protocol, no session runs tests or rebuilds in the primary
  checkout. The preflight tests of the `backlog` and `session-start` skills, and a coordinator's,
  run in the session's worktree once it exists; a red preflight there hands the phase back as an
  interrupted phase (`backlog-protocol.md`, section 11), inside a `claim` turn. The `backlog`
  skill run on its own, with no worktree, skips the tests and says so.
- One test run at a time per worktree.
- The check is not a test run. It renders the catalog in memory and runs in the primary checkout,
  including after a completion edit.

## 5. Claim slots

- The Session Manager allocates the claim slots. There are `max_active` of them, and claim-holding
  sessions never exceed `max_active`.
- Builders build the phase the Session Manager assigns and never pick from the ready queue
  themselves.
- The Session Manager assigns the earliest phase in ready-queue order (`next_up` first) whose
  Conflicts column is empty against every active claim.
- The owner approves each assignment before it is sent. The `session-start` skill's claim question
  still goes to the owner as written.
- The Conflicts column compares a phase only with active phases, through declared systems,
  deliverables and dependencies. It misses phases assigned but not yet claimed, and files edited
  without being declared. The Scout's candidate reports check both gaps against the assignments in
  flight; two phases a Scout report flags as overlapping never run at the same time, even when the
  Conflicts column is empty.
- The Batch Runner sends `NEXT-BATCH` before opening another batch.
- The Prompt Planner sends `PROMPT-FOR` before the owner pastes a prompt into an execution session.
  The Session Manager checks the prompt against that session's role, slot and the lock.

## 6. The merge gate

- A branch reaches the integration branch only with the owner's approval, relayed as below.
- `READY` carries the phase's review verdict, with every finding fixed or accepted by the owner, and
  the tail of the session's post-rebase gate runs.
- The gate is the check, the repository's tests, and every further gate the repository's working
  agreement names. Each must report clean; matching an earlier count is not enough.
- The Session Manager re-runs the gate on the branch tip in a detached temporary worktree,
  `<worktree directory>/verify-<phase-id>`, and removes it afterwards. It touches neither the
  primary checkout nor the session's worktree.
- The Session Manager brings the owner both sets of gate results and
  `git diff --stat <integration branch>..<branch>`.
- On the owner's yes, the Session Manager sends `GRANTED merge`. It is the owner's approval for
  every session, and it hands the session the lock.
- If the integration branch moved since the re-run, the session rebases, re-runs the gate while
  holding the lock and reports the new tip. The Session Manager re-runs the gate again before the
  fast-forward. Nothing else lands while the lock is held.
- Before the fast-forward, the primary checkout is confirmed clean (`backlog-protocol.md`, section
  11).
- In the same turn the session fast-forwards, makes the completion edit through the `session-close`
  skill with the catalog regenerated in the same commit, runs the check on the integration branch
  (no tests), and sends `TURN DONE`.
- After a merge lands, the Session Manager sends `REBASE` to every session with an open branch.
- A failing commit hook is never bypassed. The session commits the fix. If the hook itself is wrong,
  the session stops and reports to the Session Manager and the owner.

## 7. Ideas

- A session that meets an idea outside its work does not record it. It sends the bare idea to
  Ideation in an `IDEA` message, one idea per message, with its own name.
- Ideation batches the waiting ideas into one `idea` turn. Recording new ideas comes before triage.
- When no idea is waiting, Ideation triages the open ideas the owner names, inside an `idea` turn.
- Ideation takes each id from the writer's output and returns `IDEA-RECORDED` to the originating
  session and to the Session Manager.

## 8. The message contract

The first line of every message is its type and subject. Every message to the Session Manager goes
to its registered name.

| Message | From | Meaning |
|---|---|---|
| `ACK <session> <state>` | any | Orientation received; states phase, branch and worktree, or none |
| `TURN? <claim\|idea\|dryrun> <phase id>` | any | Asks for the lock for one stated purpose |
| `GRANTED <purpose>` | Session Manager | The recipient holds the lock; states the integration-branch commit it was granted at |
| `QUEUED <n>` | Session Manager | The recipient is n-th in line |
| `TURN DONE <sha>` | lock holder | Lock released; the checkout is clean |
| `READY <branch>` | builder, batch runner | Ready to integrate, with review findings resolved and the post-rebase output |
| `GRANTED merge` | Session Manager | The owner approved; the recipient holds the lock for the merge and the completion edit, and ends with `TURN DONE` |
| `REBASE` | Session Manager | The integration branch moved; rebase at the next safe point |
| `ASSIGN <phase-id>` | Session Manager | An owner-approved phase to build |
| `REVIEW <phase-ids>` | Session Manager | Claim-free review work for the Standby Builder |
| `CANDIDATES?` | Session Manager | Asks the Scout for conflict-free candidate phases |
| `REPORT <file>` | Scout, Standby Builder | A report in the report directory, with a short summary |
| `NEXT-BATCH <batch id>` | Batch Runner | About to open another batch |
| `PROMPT-FOR <session> <what>` | Prompt Planner | A prompt meant for that session |
| `IDEA` / `IDEA-RECORDED <id> <title> from <session>` | any / Ideation | An idea to record / the id it was recorded under |
| `BLOCKED <reason>` | any | Stuck on something outside the sender's worktree |
| `FREE` | execution | No assignment |

## 9. State and resumption

- The Session Manager keeps a board in the ignored report directory: roster, claim slots, lock
  holder and queue, pending merges, problems and open items.
- Scout reports go under `<report directory>/scout/`. Standby reviews go to
  `<report directory>/reviews/<phase-id>.md`, not to the review pack's own output path.
- The board and the reports are ephemeral. The backlog on the integration branch is the lock table.
- To start or resume: open the sessions and set each registered name in its terminal; paste the
  kickoff into the Session Manager, which reads the board if one exists, lists the sessions and
  checks every name; the Session Manager shows the owner the starter messages and sends each once
  approved; each session replies `ACK`.
- Active claims in the backlog are authoritative over the board. A claim the board does not explain
  is asked about and never released.
