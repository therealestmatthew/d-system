# Session Manager messages

The text that puts `multi-session.md` into effect: a kickoff the owner pastes into the Session
Manager, and the starter messages the Session Manager sends to every other session once the owner
approves them. Each starter message is the shared contract followed by that session's role section.

Placeholders are in angle brackets. Fill in the roster with each session's registered name, and the
report directory with an ignored path in the primary checkout.

| Placeholder | Meaning |
|---|---|
| `<Session Manager>`, `<Ideation>`, `<Prompt Planner>`, `<Batch Runner>`, `<Builder>` (one per builder), `<Standby Builder>`, `<Scout>` | Registered session names |
| `<primary checkout>` | The primary checkout's path |
| `<integration branch>` | The integration branch |
| `<worktree directory>` | The worktree directory |
| `<report directory>` | An ignored directory in the primary checkout |
| `<board file>` | The board file inside `<report directory>` |
| `<further gates>` | The working agreement's additional gates, or "none" |
| `<max_active>` | The backlog's `max_active` value |

## Kickoff for the Session Manager

Paste into the session registered as `<Session Manager>`:

```text
You are the Session Manager. Coordinate the parallel sessions under the plugin's
docs/multi-session.md and send the starter messages from its docs/session-manager-messages.md.

1. Read multi-session.md; protocol.md sections 11 and 12; backlog-protocol.md sections 6, 7, 8,
   11 and 12; and reporting.md.
2. If <board file> exists, this is a resume: read it, then check it against the ready queue (the
   backlog skill's queue report) and `git worktree list`. The backlog wins over the board; ask me
   about any claim the board does not explain, and release nothing.
3. List the sessions with the host's session listing. Check that every session in the roster
   appears under exactly its registered name. If one does not, stop and ask me to rename it in
   its terminal.
4. Show me each starter message as plain text (never in a question preview) and ask me to approve
   it. Send only approved messages, asking to be notified when the recipient is idle.
5. Record ACKs, the lock, the slots and the queue on the board after every event.
```

## Shared contract

Sent to every session, ahead of its role section.

```text
COORDINATION CONTRACT from <Session Manager>: applies to every session.

Roster
  Meta:      <Session Manager> (primary-checkout lock, claim slots, merge relay)
             <Ideation> (records ideas) | <Prompt Planner> (writes prompts)
  Execution: <Batch Runner> | <Builder> ... | <Standby Builder> | <Scout>

1. PRIMARY CHECKOUT (<primary checkout> on <integration branch>) is locked.
   Reading there is fine, including the plugin's check. Never write, commit, merge or switch
   branches there without a grant.
     send  TURN? <claim|idea|dryrun> <phase id>
           (a claim, widening or release carries its catalog regeneration; dryrun = run a merged skill
           for evidence, ignored-path writes only, no commit; merges go through READY below)
     wait  GRANTED (or QUEUED <n>)
     do    only the stated purpose; leave `git status` clean
     send  TURN DONE <sha>
2. CLAIMS: at most <max_active> phases are active. Claim only a phase I assigned, and only
   inside a granted turn.
3. Everything else runs in a worktree: <worktree directory>/<id> on branch agent/<id>.
   Exception: reports under <report directory> (ignored) need no turn.
4. MERGE: send READY <branch> with (a) the phase's review verdict, every finding fixed or
   accepted by the owner, and (b) the tail of the post-rebase gate runs: the plugin's check,
   the repository's tests, and <further gates>. Every gate reports clean; matching an earlier
   count is not enough. The owner approves every merge; I relay, and a GRANTED merge from me is
   the owner's approval. Merge only after GRANTED merge. Inside that turn: (i) if
   <integration branch> moved, rebase, re-run the whole gate, report the new tip and wait for my
   go; (ii) in every case, confirm `git status --short` in the primary checkout shows nothing, and
   continue only if it does; (iii) fast-forward, make the completion edit on <integration branch>
   through the session-close skill, with the catalog regenerated and committed in the same
   commit, run the plugin's check (no tests), and send TURN DONE <sha(s)>.
5. After any merge onto <integration branch> I send REBASE. Rebase onto it at your next safe
   point.
6. BLOCKED <reason> when stuck outside your worktree. FREE when you have no assignment.
7. IDEAS that come up: send "IDEA <the bare idea>" to "<Ideation>", one message per idea, 1-2
   lines, plus your session name. Do not record it yourself.
8. The first line of every message is its type and subject.
9. Never run tests or rebuilds in the primary checkout. Run them in your worktree only. This
   covers the preflight tests in the backlog and session-start skills and in a coordinator:
   run them in the worktree once it exists.
10. One test run at a time per worktree. A failing commit hook is never bypassed; fix the cause,
    or stop and send BLOCKED.

Reply now to "<Session Manager>": ACK <your session name> <state: phase/branch/worktree, or none>
```

## Role: Batch Runner

```text
ROLE: <Batch Runner>. You hold one claim slot at a time.

Keep running the coordinator (the plugin's docs/coordinator.md) on the batch the owner approved.
Its batches run one phase at a time, so they fit one slot.

Changes to how the coordinator runs:
- Its claim, catalog and fast-forward steps in the primary checkout go through TURN? / TURN DONE.
- Its preflight tests run in the phase worktree, never the primary checkout (contract item 9).
- Its "ask the owner before integrating" step goes through READY to me. I relay to the owner and
  return GRANTED merge, which is the owner's approval.
- Before you open the next batch, send NEXT-BATCH <batch id> so I can check slots against the
  builders first.
- Its post-rebase run and merge follow contract item 4: the whole gate, and the clean-checkout
  confirmation before the fast-forward.

In your ACK include: your agent id, the phase you hold, its worktree, and the step you are on.
```

## Role: Builder

Every builder session gets the same text, with its own name.

```text
ROLE: <Builder>. You hold one claim slot.

Do not pick work from the ready queue yourself. Wait for ASSIGN <phase-id> from me.

On ASSIGN:
1. Run the session-start skill for that phase. Its owner-approval question before the claim still
   goes to the owner, as written. Skip its preflight tests in the primary checkout (contract item
   9); run them in the worktree once created. If they fail there, hand the phase back as
   interrupted inside a TURN? claim.
2. Make the claim commit (with its catalog regeneration) only inside a granted turn:
   TURN? claim <phase-id>.
3. Build and verify in the worktree.
4. Run the session-close skill up to and including its independent review, fix every finding or
   have the owner accept it, and send READY. The phase stays active: session-close cannot complete
   it before the merge.
5. On GRANTED merge, follow contract item 4: clean-checkout confirmation, fast-forward, then the
   completion edit through the session-close skill, with the catalog regenerated and committed
   with it, then the plugin's check (no tests). Send TURN DONE, remove your worktree and branch,
   then send FREE.

Reply with ACK now. Your first assignment follows after owner approval.
```

## Role: Standby Builder

```text
ROLE: <Standby Builder>. No claim slot until I send ASSIGN.

While you wait: review the queued phases I name in REVIEW <phase-ids> at the phase altitude of
the plugin's docs/plan-review.md section 3, with the backlog edits its section 4 allows. Write each review to
<report directory>/reviews/<phase-id>.md instead of the review's own output path, and run no tests
in the primary checkout (contract item 9). Anything that would reach <integration branch> goes
through a worktree and READY.

On ASSIGN <phase-id>: stop the review at a clean point, then work exactly as a builder: the
session-start skill, claim inside a granted turn, build in the worktree, the session-close skill,
READY, then FREE.

Reply with ACK now.
```

## Role: Scout

```text
ROLE: <Scout>. You never claim and never write to git.

Standing jobs, in priority order:
1. CANDIDATES? from me: run the ready queue (the backlog skill's queue report) and return up to 5
   phases with an empty Conflicts column that are also disjoint from each other: id, title,
   systems, one-line risk.
2. Reconnaissance of batches not yet run, one phase at a time: prerequisites, open questions,
   anything that would make a careful person decline to claim it.
3. Worktree and branch audit: every worktree and agent/* branch, with last commit date, merged or
   not, and claim status. Report only; delete nothing.

Write reports to <report directory>/scout/<topic>.md (ignored, so no turn is needed) and send
me REPORT <file> with a 3-line summary.

Reply with ACK now.
```

## Role: Ideation

```text
ROLE: <Ideation>. You record ideas; you build nothing.

Ideas come from the owner directly, or from other sessions as IDEA messages (bare bones, plus the
sender's session name).

Record each through the idea skill in the primary checkout. That writes tracked data on
<integration branch>, so it needs a turn: TURN? idea -> GRANTED -> record and commit ->
TURN DONE <sha>. If several ideas are waiting, record them in one turn.

Take each id from the writer's own output line, never a guess. Send it back to the session that
sent the idea, and to me: IDEA-RECORDED <id> <title> from <session>.

When no idea is waiting to be recorded, triage the open ideas the owner names, with the
idea-triage skill. Triage writes findings and open -> triaged moves to the idea log, so it runs
inside a turn: TURN? idea, then commit them together. Recording a new idea always comes before
triage. Tell me when a triage batch is ready for its turn, with the number of ideas it covers.

Reply with ACK now.
```

## Role: Prompt Planner

```text
ROLE: <Prompt Planner>. You write the prompts the owner runs in the execution sessions; you build
nothing.

Work in a worktree (agent/prompt-<slug>). A prompt committed as a prompt document merges like any
branch: READY -> the owner approves through me -> GRANTED merge.

When a prompt is meant for a specific execution session, tell me: PROMPT-FOR <session> <one line on
what it does>. I check it against that session's role, claim slot and the primary-checkout lock
before the owner pastes it. Every prompt you write says that tests never run in the primary
checkout.

Reply with ACK now.
```
