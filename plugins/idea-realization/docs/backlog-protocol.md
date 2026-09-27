# Backlog protocol

How work is broken into phases, claimed, run, handed off and completed. The backlog file lives at
`backlog_path`; its shape is `schemas/backlog.schema.json`. The core protocol (`protocol.md`)
covers worktrees and integration; this document covers everything that touches the backlog.

## 1. The backlog

- The backlog is the execution record of every open plan. Each phase is one independently
  verifiable outcome that fits one focused session, including its checks and hand-off. Parent
  plans keep the design.
- The backlog on the integration branch is the lock table, and the check is the lock check.
- The backlog YAML is the only editable state. Reports are generated from it, never copied into a
  second board.
- The `ready` command (the `backlog` skill) prints `next_up` first, then priority and id. For each
  phase it shows readiness, prerequisites and a Conflicts column naming the active phases it would
  collide with; for each active claim it shows a stale-claim signal. `--all` adds every phase's
  details and the source-plan coverage table. It changes nothing.

## 2. The phase schema

Top level: `schema_version` (1), `updated` (never in the future), `decision_record` (optional: a
governance or adr document), `max_active` (1 to 4, default 1), `next_up` and `items`.

| Field | Rule |
|---|---|
| `id` | `phase-<track>-<NN>`. Permanent and never renumbered. A new phase takes the next unused number in its track, chosen by hand. |
| `title` | One observable outcome. |
| `plan` | One primary plan document. |
| `sources` | Every other governed source the phase covers. |
| `systems` | One or more existing `sys-` ids. |
| `owner` | An existing owner key. |
| `priority` | 1 foundation, 2 capability, 3 composition, 4 conditional extension. |
| `session_budget` | Exactly 1: a review promise about scope, not a timing guarantee. |
| `depends_on` | Prerequisite phases, each complete before this phase is active or complete. No self-dependency and no cycle. |
| `scope` | At least one step. |
| `acceptance` | At least two observable conditions. |
| `verification` | At least one command or specific check, run and recorded during execution. |
| `deliverables` | Expected repository paths, which need not exist yet; refined during execution. |
| `next_action` | The first useful action, or an exact resume instruction. |
| `agent` | `agent-<name>`, naming the branch `agent/<phase-id>`. Required on every active phase while `max_active` exceeds 1. |
| `blocked_reason` | Required on blocked, deferred and cancelled phases. |
| `resume_when` | Required on blocked and deferred phases. |
| `session`, `completion_evidence`, `result` | Required together on a complete phase; may be recorded while a phase is active or blocked. A released phase (queued, deferred, cancelled) carries none of them. `session` names a session or walkthrough document. |

Session-record and decision-record file names given in a phase's initial deliverables are
illustrative. Source ids stay stable when a file moves.

## 3. Phase states

- A phase is `queued`, `active`, `blocked`, `deferred`, `complete` or `cancelled`. Readiness is
  derived: a queued phase is ready when every dependency is complete, and waiting otherwise.
- Transitions: queued to active once prerequisites are complete; active to complete; queued or
  active to blocked on an external impediment; blocked to queued once the resume condition is
  met; queued to deferred and back; active to queued with an exact hand-off; queued, blocked or
  deferred to cancelled when scope is withdrawn.
- Blocked and deferred are explicit decisions, not names for an unmet prerequisite.
- A cancelled dependency never satisfies its dependents. The dependency graph is revised
  deliberately.
- A deferred or blocked phase is released only by its recorded resume condition, never by elapsed
  time.
- `agent` stays on active, blocked and complete phases, and is dropped on queued, deferred and
  cancelled ones.

## 4. Queue order and `next_up`

- The queue order is the `next_up` entries as listed, then priority, then id. Position in the file
  means nothing.
- Every `next_up` entry names an existing phase that is neither complete nor cancelled.
- Ranking the `next_up` front of the queue belongs to the owner. An agent may propose an order but
  never writes one. The only agent edit is removing a phase in the change that completes it.
- `next_up` stays short: it says what happens now, and priority says when.
- "The next task" is the first ready phase in the rendered order.
- The phase's `scope`, `acceptance`, `verification` and `next_action` bound the work.

## 5. Capturing plans as phases

- Before implementing, the agent reads the open plans and the decision record, and finds existing
  phases before creating new ones.
- Each plan is split into one-outcome phases with acceptance and dependencies. A shared
  prerequisite is one phase referenced by every source it serves.
- Every draft, approved or active plan, overview or child, is covered by at least one non-cancelled
  phase through `plan` or `sources`. The phases are added in the same change as a new plan.
- Coverage is structural. A reference cannot prove every requirement was captured, so plan bodies
  are re-inspected whenever scope changes.
- The check runs and coverage (`ready --all`) is inspected before product work.
- A plan moves from approved to active when its implementation starts.
- A plan stays open until every phase mapped to it is complete, or cancelled with a reason.
  Deferred phases keep it open.
- At plan closure its acceptance criteria are reviewed, its completion evidence is recorded and
  its metadata is updated.

## 6. Claims and the active-claim limit

- `max_active` bounds the number of simultaneously active phases. Raising it authorizes nothing by
  itself.
- An agent holds at most one active phase and reuses the agent id it chose once.
- Orientation runs the check and the tests first. If either fails, nothing is claimed. While
  sessions run under `multi-session.md`, the tests run in the new worktree instead (section 4 there).
- The owner is asked before a claim is committed. An unanswered question is not a yes.
- A claim is one commit on the integration branch in the primary checkout. It holds this phase's
  `status: active` and `agent`, the backlog `updated` set to today, and the regenerated catalog,
  and nothing else. It is pushed before work begins.
- The primary checkout is brought up to date by a fast-forward pull and never switched. If it is
  not on the integration branch, the session stops and reports it.
- The check runs before the claim is committed. It rejects overlap with an active peer's systems,
  deliverables or dependency chain, and a full `max_active`. A rejection means choosing different
  work, never waiting.
- If the claim push is rejected as non-fast-forward: `git pull --rebase`, re-run the check, and
  confirm the claim is still safe.
- A peer's claim is never edited. A session touches only its own phase's backlog lines and
  `updated`.
- Owner-directed work with no phase claims nothing and uses `agent/<slug>`. Its first report says
  it is unclaimed. A phase is never invented to have something to claim.

The `session-start` skill carries these steps.

## 7. Concurrency

- No two active phases share a system. No declared deliverable path of one equals or contains one
  of the other's. Neither is a transitive prerequisite of the other.
- Work stays inside the declared systems and deliverables. The check cannot see edits outside
  them, so diff review confirms it.
- Widening a phase's declared systems or deliverables is committed on the integration branch, and
  the check re-run, before the work that needs it, so peers see the wider lock first.
- Work on a system that depends on a peer's active system treats the peer's contract as frozen at
  the branch point, and builds against the merged integration branch, never a peer's unmerged
  branch.

## 8. Stale claims

- Each active claim shows one of `no`, `STALE: <signal>`, `no evidence: no agent/<phase-id> branch
  found`, or `no signal evaluated`.
- There are two signals: no commit on `agent/<phase-id>` for more than 2 days, and no worktree
  checked out on that branch.
- A claim whose branch has no commits, including one whose branch does not follow
  `agent/<phase-id>`, reports no evidence and is never marked stale.
- The signal is evidence for the owner, never proof. A long read or an external wait looks the
  same as abandonment, and a missing worktree read on another machine is no evidence.
- No script releases a claim. The report is an input to the owner's decision.

## 9. The session record and checkpoints

- Each session has one session record. The `checkpoint` skill creates and updates it; the
  `session-close` skill finalises it.
- The session record is `kind: session` with status `active`. Its code comes from the session
  series, with a date equal to `created`, and the file is named `<code>-<topic>.md`. Its sections
  are Phase, Verification, Acceptance, Backlog and Unresolved, and each checkpoint regenerates
  them from observed state.
- Verification records the literal command and its literal output. A failure is never paraphrased
  into a pass.
- Acceptance is judged one condition at a time from recorded evidence, as Met or Not met.
- A checkpoint records progress, is safe to repeat, and never marks a phase complete. It never
  runs worktree, rebase or remote commands, and never touches another phase's lines.
- Once a session is closed, its record is only added to, never rewritten.

## 10. Completion

- An agent never completes a phase on its own judgement that the work looks finished.
- A phase is marked complete, by the owner or by a coordinator running the `session-close` skill,
  only when all three conditions hold:
  1. every verification command ran green, and its real output is in the session record;
  2. an independent adversarial review of the diff against the phase's acceptance ran, and every
     finding is fixed or explicitly accepted by the owner;
  3. the branch is integrated onto the integration branch with the owner's approval.
- The completion edit is one small commit on the integration branch right after integration,
  together with the regenerated catalog.
- The review runs in a fresh agent that does not share the session's context, never a fork. It
  receives the phase's scope, acceptance and verification, the diff range and the record. Its
  findings are recorded verbatim, each with its disposition.
- Completion writes `session`, `completion_evidence` (existing files) and `result` (the actual
  verification and review outcome), keeps `agent`, and removes the phase from `next_up` in the same
  change.
- While any condition is unmet, the phase stays active, or queued if handed off, with
  `next_action` naming what remains.
- An unclaimed session completes nothing.
- Close adds Review, Decisions, Corrections and Left undone sections to the record.
- Completion evidence lists files that existed when the phase closed. When a later phase's
  sanctioned scope deletes one, its evidence line is removed in the same change as an entry in the
  decision record, never silently.

## 11. Hand-off

- In the worktree, in this order: run verification, write the session record, rebase onto the
  integration branch and re-run the check and the tests, confirm the primary checkout is clean,
  ask the owner.
- Before every fast-forward onto the integration branch the primary checkout is confirmed clean.
  A peer's uncommitted work is never stashed or forced around; it is reported and waited on.
- An interrupted phase returns to queued with an exact `next_action`, clearing `agent`, `session`,
  `completion_evidence` and `result`, or goes to blocked with a reason. Its worktree is removed so
  no directory outlives the claim, and completion is never claimed.

## 12. Collisions

- A backlog conflict keeps both sides: the peer's phases verbatim, your own phase's edits, and
  `updated` set to today. It is never resolved with `--ours` or `--theirs`.
- A source-code conflict between phases declared disjoint means the declarations the concurrency
  check relies on are wrong. It is stopped, never forced, and always gets an entry in the decision
  record. The declarations are fixed before either phase completes.
- When resolving a collision needs a real choice (which phase yields, whether a boundary moves,
  whether a phase splits or widens its declarations, which implementation is kept), the decision
  and its reason go into the decision record in the same change. A commit message is not a record.
  A mechanical keep-both merge needs no entry.
- A duplicate document code is resolved by renumbering (`document-codes.md`, section 5).

The decision record is the document the backlog's `decision_record` names.

## 13. Leaving complete

- Phase ids and completed evidence are kept, never deleted.
- A phase that leaves complete, or stays complete but loses `session`, `completion_evidence` or
  `result`, is an error against HEAD unless the same change adds a decision-record entry naming it.
  Against the integration branch the same finding is a warning.
- Without a `decision_record` the regression check does not run, and the check says so.

## 14. Splitting and cancelling

- A phase that exceeds one session is split into new ids, keeping its rationale, and dependents
  are rewired before work continues. A phase is never left labelled as one session when it is not.
- A phase is cancelled only with a reason. A cancelled phase does not count toward plan coverage.
- The backlog `updated` is kept current on substantive edits and is never a future date.
