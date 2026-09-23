---
schema_version: 1
id: doc-multi-session-coordination-protocol
code: GOV-017
title: Multi-session coordination protocol — roles, the primary-checkout lock and the message contract
kind: governance
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-governance, sys-backlog]
depends_on: [doc-adr-multi-agent-concurrency, doc-coordinator-protocol, doc-build-coordinator, doc-backlog-decisions, doc-conversation-guidelines, doc-governance-operations]
---

# Multi-session coordination protocol

How the owner runs several interactive Claude Code sessions against this repository at once, with
one session coordinating the rest. It covers the session roles, how access to the primary checkout
is serialized, how claim slots are allocated, how merges reach the owner, and the exact messages
sessions exchange.

`AGENTS.md` governs what each agent may do; this document does not change any of it. It governs how
several sessions, each following `AGENTS.md`, take turns at the parts of the work that cannot run in
parallel. `GOV-013` and `PROMPT-036` govern a single coordinator that dispatches subagents; this
governs several top-level sessions, one of which may be running `PROMPT-036`.

The starter messages that put this protocol into effect are in
[PROMPT-037](../02-prompts/PROMPT-037-session-manager-starter-messages.md). This document says what
the rules are and why; that one carries the text sent to each session.

It was written on 2026-09-22, from the owner's rulings in the first session that ran this way.

## The sessions

There are two groups. **Meta sessions** coordinate, capture and plan; they never claim a backlog
phase. **Execution sessions** build backlog phases.

| Session | Group | Role | Claim slot |
|---|---|---|---|
| Session Manager | meta | Holds the primary-checkout lock, allocates claim slots, relays merges to the owner, keeps the board | never |
| Ideation | meta | Records ideas through the sanctioned writer; builds nothing | never |
| Prompt Planner | meta | Writes the prompts the owner runs in execution sessions; builds nothing | never |
| Session 5 - Batch Runner | execution | Runs `PROMPT-036` through the batch tables in order | one at a time |
| Session 1 - Builder A | execution | Builds one assigned conflict-free phase at a time through `/session-start` and `/session-close` | one |
| Session 2 - Builder B | execution | As Builder A | one |
| Session 3 - Standby Builder | execution | First in line for the next free slot; until then, reviews queued phases with `PROMPT-035` | none until assigned |
| Session 4 - Scout | execution | Read-only: candidate phases, batch reconnaissance, worktree and branch audits | never |

### Why these roles

- **The claim limit binds less than system overlap does.** `max_active` stays at 3. On 2026-09-22,
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
is set with `/rename <name>` inside the session, in the terminal. On 2026-09-22 a rename made from
the Remote Control mobile client changed only the name shown on that device; the registered name
stayed the auto-generated title, and the Session Manager could not tell which session was meant.

A session's `[ref]` in `ListAgents` does not change when it is renamed, and every received message
carries the sender's registered name. The first message to a session asks it to state its phase and
agent id, so a wrong link is found before it acts on role instructions.

## The primary-checkout lock

The primary checkout (`/code/d-system` on `dev`) is where claims, the catalog regeneration they
force, integrations and idea records are committed. Only one session writes there at a time.

- Any session may **read** there, including `uv run python -m src.governance` and `--ready`.
- To **write** — commit, merge, regenerate, or switch anything — a session asks for a turn, does
  only the purpose it stated, leaves `git status` clean, and reports the resulting commit.
- Before granting a turn, the Session Manager checks that the checkout is on `dev` and clean. After
  the holder reports, it checks that the commit landed and nothing else changed.
- **No tests, rebuilds or `pytest` in the primary checkout, by any session.**
  `test/test_codes.py` overwrites the tracked `docs/08-governance/catalog.md` while it runs and
  restores it afterwards. On 2026-09-22 two `/session-start` preflight runs overlapped there and
  left the catalog holding only `CORRUPTED` (ideas `000324`, `000325`). Tests run in the session's
  own worktree.

## Claim slots

The Session Manager allocates the three slots. Builders do not pick from `--ready` themselves; they
wait for an assignment. Before assigning, the Session Manager checks that the phase's Conflicts
column is empty against every active claim, and the owner approves each assignment. `/session-start`'s
own claim-approval question still goes to the owner as written.

The Conflicts column can miss real overlap: phases that edit the same directory under different
system ids are not flagged (ideas `000321`, `000322`). The Scout's candidate reports name such
hazards, and the Session Manager does not run two phases together that a report flags.

## The merge gate

A branch reaches `dev` only with the owner's approval, as `AGENTS.md` requires. Approval is relayed:

1. The session sends `READY` with the phase's own review verdict and the tail of its post-rebase
   `governance` and `pytest` runs.
2. The Session Manager re-runs `governance` and `pytest` on the branch in a separate temporary
   worktree, so it touches neither the primary checkout nor the session's worktree.
3. The Session Manager brings the merge to the owner with both results.
4. On the owner's yes, it sends `GRANTED merge` and gives the session the lock. If `dev` has moved
   since the run, the session rebases and re-runs both checks while holding the lock, so nothing can
   land between that run and the fast-forward. The completion edit is made in the same turn.
5. After the merge lands, the Session Manager sends `REBASE` to every session with an open branch.

**Owner ruling, 2026-09-22:** a `GRANTED merge` relayed by the Session Manager counts as the owner's
approval. A session whose own instructions require the owner's direct word may ask the owner once in
its own session to confirm this.

## Ideas

A session that meets an idea outside its work sends the bare idea to Ideation, one message per idea,
with its own session name, and does not record it. Ideation records ideas through
`tools/append_idea.py` in the primary checkout, which needs a turn, and batches waiting ideas into
one turn. It takes each id from the tool's output and sends it back to the originating session and
to the Session Manager.

## The message contract

The first line of every message is its type and subject. All messages to the Session Manager are
sent to the name `Session Manager`.

| Message | From | Meaning |
|---|---|---|
| `ACK <session> <state>` | any | Orientation received; states phase, branch and worktree, or none |
| `TURN? <claim\|catalog\|merge\|idea> <phase or branch>` | any | Asks for the primary-checkout lock for one stated purpose |
| `GRANTED <purpose>` | Session Manager | The recipient holds the lock; states the `dev` commit it was granted at |
| `QUEUED <n>` | Session Manager | The recipient is n-th in line |
| `TURN DONE <sha>` | lock holder | Lock released; the checkout is clean |
| `READY <branch>` | builder, batch runner | Ready to integrate, with review verdict and post-rebase output |
| `GRANTED merge` | Session Manager | The owner approved; the recipient holds the lock for the merge and completion edit |
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
holder and queue, pending merges, incidents and open items. Scout and standby reports go under
`_working/session-manager/scout/` and `_working/session-manager/reviews/`. All of it is gitignored
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
