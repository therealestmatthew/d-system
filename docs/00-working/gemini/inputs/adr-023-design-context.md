# Input for Gemini prompt G2: design context for ADR-023's open parameters (verbatim excerpts)

Copied on 2026-09-25 by the Prompt Planner session for `PROMPT-040` prompt G2. The sources are
gitignored design documents, so a worktree cannot see them. This file is an ungoverned staging copy
(ADR-010). Do not edit it; it is a snapshot.

**Status of this material.** Everything here is a **proposal**, not an owner ruling. The owner's
rulings are in `docs/04-decisions/ADR-023-session-manager-into-orchestrator.md`, which wins wherever
the two differ. Citations inside the excerpts (`P1 §n`, `P2 §n`, `finding n`, `board.md:n`, memory
names) refer to further gitignored files you cannot open; treat what the excerpt says about them as
given.

- **P3** = `_working/overnight-sprint/planning/session-manager-on-langgraph.md` (draft 4, 2026-09-23,
  Prompt Planner): sections 4.3, 5.5, 8.1 and 8.3.
- **D3** = `_working/session-manager/scout/d3-supervisor-vs-sm-session.md` (2026-09-24, Session 4 -
  Scout): sections 2, 3, 5 and 7. Its section 7 cites public documentation URLs; those were fetched
  on 2026-09-24.

---

# P3 excerpts

#### 4.3 The primary-checkout lease

This is the one genuinely new mechanism. Today it is a message protocol (TURN?, GRANTED, QUEUED,
TURN DONE). It must be shared by the daemon's runs and, during migration, by interactive sessions.

It is different from the daemon's own `flock` (`phase-irs-16`): that lock says "one tick at a
time"; the lease says "one writer to the primary checkout at a time", and its holder may be a
dispatched worker or an interactive session, not the daemon.

Options for where the lease lives:

| Option | How | For | Against |
|---|---|---|---|
| **(a) Lease file under `data/orchestrator/`, audited in the ledger** | A JSON file (holder, purpose, granted-at `dev` sha, heartbeat) created and removed under a short `flock`. Every grant and release also appends a ledger event. A CLI verb (`orchestrator lease acquire/release/status`) is the only way to take it | Disposable per `ADR-018`; interactive sessions can use the same verb | A second file next to the daemon lock. And because the lease spans several CLI calls (acquire, then git commands, then release), no process holds it throughout, so `flock`'s release-on-death does not apply: a dead holder is detected only by a stale heartbeat |
| (b) Ledger events only | Grant and release are events in `_data/runs.jsonl`; the holder is a fold | One source of state | The ledger is a tracked file with uncommitted appends in the primary checkout (`PLAN-039.01` §5); a lease written into the very checkout it guards cannot be committed while someone else holds the lease |
| (c) Keep it in messages | The Session Manager session stays the lock holder | No new code | Keeps findings 2 and 10 |

**Recommendation: (a).** Postconditions checked in code at release: `HEAD` is `dev`, exactly the
commits the purpose allows landed, and the checkout is clean.

"Clean" needs care. The orchestrator's own tracked logs (`_data/runs.jsonl`,
`_data/gate-decisions.jsonl`) and the idea log accumulate uncommitted appends in the primary
checkout by design (`PLAN-039.01` §5), and the lease's own grant event is one of them. The
existing dirty-checkout guard (`tools/git-hooks/refuse_dirty_integration.py`) refuses any staged,
unstaged or untracked path and any stash entry, so used unchanged it would refuse every release.
Two ways out:
- the lease's clean check ignores exactly those three append-only logs, and the ff-merge guard
  still sees them; or
- every release commits pending appends to the three logs, inside the lease, before its check.

The second keeps one definition of clean and keeps the logs committed often. It is the
recommendation, and the refusal logic stays in the existing guard rather than being re-implemented.

**The lease path must resolve to the primary checkout.** Every orchestrator path today hangs off
`Path(__file__).resolve().parents[2]`, which inside a worktree is that worktree. Interactive
sessions work in worktrees, so each would see its own lease. The lease resolves its path through
`git rev-parse --git-common-dir`, as `resolve_primary_checkout` in the dirty-checkout guard
already does.

**The lease holds no queue.** `lease acquire` either grants or refuses, naming the holder and the
purpose. Ordering among the daemon's own runs is the tick's business, since one tick runs at a
time. Interactive sessions during migration retry, or keep asking the Session Manager as today.
A real wait list is not needed until several independent writers compete, which is 000156's
territory. A stale lease (holder dead, heartbeat old) is recovered only if the
checkout is clean; a dirty checkout parks with a gate item and consumes the claim-recovery
procedure of `phase-conc-04` rather than inventing one (`PLAN-039` de-duplication boundary).

**The orchestrator's tracked writers need their own lock.** P2 §1.2–1.3 found that `ledger.start()`
checks for a duplicate key and then appends with no lock, and `decisions.decide()` computes its
sequence number the same way. `tick` never writes decisions; the races are two `gate` writers at
once (the Owner Desk and a manual command), and ledger writers that run outside the tick's lock
(`tools/append_run.py`, and the proposed lease verb). `phase-irs-16`'s `flock`, now on `dev`,
serialises `tick` and `start` only; `gate`, `tools/append_decision.py`, `tools/append_run.py` and
`tools/append_idea.py` take no lock (P2 §1.5). The append lock therefore covers all four writers,
including the idea log. Like the lease, it must resolve to the primary checkout: the daemon's own
lock path hangs off the module root, so a manual `tick` from a worktree takes that worktree's lock
and works on that worktree's copies of the logs (P2 §1.5). The simplest fix is
that every append to `_data/runs.jsonl` and `_data/gate-decisions.jsonl` takes a short append lock
(the same `flock` pattern, a separate file), independent of the long-held lease.

**Session liveness** (I1 gap 4). The lease body carries a heartbeat that the holder refreshes. For
an SDK dispatch the adapter refreshes it while the dispatch runs, so a dead worker is detected by a
stale heartbeat. For an interactive session during migration, the lease verb is the only liveness
signal there is; the design does not try to detect a dead interactive session that holds nothing.

**Against the other proposals for mediating `dev` writes** (I1 overlap 2):

| Idea | Shape | Relationship to the lease |
|---|---|---|
| 000156 | One agent owns the primary checkout and works a queue of version-control requests | The lease is the same serialisation without making an agent the owner, and without a queue; 000156 is the next step if a queue is ever needed |
| 000320 | An always-on broker orders conflicting action requests | The lease covers one resource (the primary checkout); a general broker is a superset. Build the lease; generalise only if a second contended resource appears |
| 000250 | A remote MCP server mediates orchestrator state and `dev` writes | A later home for the lease and ledger if work moves across machines. The lease's CLI verbs are the interface that would move |
| 000020 | An MCP Librarian service for docs, claims and checkouts | Crosses into the claim table, which `REQ-017` R16 forbids duplicating; the lease does not touch claims |

The lease does not replace `backlog.yaml` as the claim table. It only orders writes to the checkout
that holds it.


#### 5.5 How the owner approves from mobile

The owner uses Remote Control on mobile, where AskUserQuestion previews do not render (finding 8).

| Option | For | Against |
|---|---|---|
| **(a) Owner Desk: one interactive Claude Code session on Remote Control** that reads the gate queue, asks in batches of at most four with AskUserQuestion (content in the question text, never previews), and records answers with `orchestrator gate` | Works tonight with no new UI; the owner already uses this path; one session to watch instead of eight | Still an LLM session in the loop; its context grows over a day (but it holds no state — clearing it is always safe) |
| (b) Workbench page (`phase-irs-13`'s `ts/` deliverable) served from FastAPI and opened on the phone | No LLM in the approval path; structured and auditable | Needs the web UI built and reachable from the phone (network exposure is its own decision) |
| (c) Notifications plus a claude.ai artifact page per batch of decisions | Rich presentation | Answers would have to come back into the repository by hand or through a runtime capability; a second place where decisions live |

**Recommendation: (a) first, (b) when `phase-irs-13` builds the workbench surface.** Both write
through the same `gate` verb, so switching is a presentation change only.


#### 8.1 Where each kind of state lives

| Layer | Contents | Tracked? | Rule |
|---|---|---|---|
| Repository truth | `backlog.yaml`, `_data/ideas.jsonl`, governed docs, git history | yes | Wins every disagreement (`ADR-018`) |
| Run narrative | `_data/runs.jsonl` (ledger), `_data/gate-decisions.jsonl` (answers) | yes | Append-only, sanctioned writers; committed at sittings (`PLAN-039.01` §5) |
| Machinery | daemon lock, lease, checkpoints, watermark under `data/orchestrator/` | no | Disposable; deleting it loses nothing |
| Kill switch | `_working/orchestrator-halt` | no | Outside `data/` (`PLAN-039.01` §9) |
| Shared facts mid-run | `_tmpagent/` | yes | `phase-agx-07` extends it; no second lock table |
| Per-task context | Brief built by the dispatch adapter | no | Rebuilt every dispatch; its hash goes in the ledger |

000319 asked whether "the tracked half suffices". Under this design the answer is designed to be
yes: the one thing that lived only in gitignored files on the first night — owner decisions made
mid-run (`decisions.md`, `01-authority.md`, `owner-actions.md`) — moves into
`gate-decisions.jsonl` (tracked) and authority-grant records (tracked if D10 (a) is chosen).


#### 8.3 Memory: owner rulings and delegated authority

Tonight's `01-authority.md` is the prototype for unattended operation: a written, bounded, expiring
grant ("these claims; these merges if five conditions hold; lapses when the owner next speaks").
`src/broker/approvals.py` already records requests with scope, reason, expiry and an immutable
decision. The proposal is that a delegated-authority grant is an approval record in that store, and
G4 evaluates it: if a grant covers this phase and every condition holds (checked in code, not
judged), the G4 decision is written by the evaluator **citing the grant**; otherwise the item waits
for the owner. The approval store exists but nothing reads it: `check()` never consults it (P2
§1.4), so N7 builds the reader; it does not reuse one. This answers I1 gap 2 (a governed form of
delegated authority): the grant is a durable record rather than a hand-written file, and "lapses
when the owner next speaks" becomes an expiry plus an explicit revoke. One catch: the broker's store
is `_working/broker/approvals.jsonl`, which is gitignored (P2 §1.4). A grant that must survive a
lost machine, or be audited later, needs a tracked home; D10 asks where. This is also how `REQ-017` R02 and R04 (recorded open in `ADR-022`) get their first
real requests to be designed against.

Cross-model memory (`brain/procedures/`, the owner's memory files) stays as it is; the brief
includes the procedures that apply to a role.


---

# D3 excerpts

### 2. The two options side by side

| | A: long-lived SM session + daemon | B: supervisor node in the graph + daemon |
|---|---|---|
| Where routing judgement runs | In the SM session's conversation | In a graph node that calls the model once per routing event |
| Where coordination state lives | Records: ledger, gate queue, lease file, `backlog.yaml`. The session holds none (the rule it must follow) | The same records, plus LangGraph checkpoints (disposable, ADR-018) |
| How the owner is reached | AskUserQuestion in the SM session, over Remote Control, which keeps the question open and can push a notification (7.4) | Interrupt → gate queue → **an interactive session or a web page still needed** to put it to the owner |
| How the daemon reaches the LLM | It cannot message the session. P1 §2 (cited in P3 §11): a script can post only to its own session's inbox. The SM session must *pull* (`orchestrator status`, read the gate queue) or be woken by a watcher [C; the watcher is a spike] | Direct: the node is code in the daemon's process |
| Context over a day | Grows; needs clears. Safe to clear only if every pending item is a record (P3 §7.1) | None to manage if each call is fresh. A resumed SDK session per D4(c) brings context growth back into code |
| Testability | None beyond drills | The node's output can be replayed and checked against an allowed set; the LLM call itself is not deterministic |
| Cost | Every turn and every received message pays the whole context. A break longer than the cache lifetime reprocesses it (7.4). Not measured here [U] | One model call per routing event. Must not call on every tick [I] |
| Exists on `dev` today | The session, the protocol (GOV-017, PROMPT-037) and the relay practice | `gates.gate_node`, `resume_command`, the decisions log, `SqliteSaver`, the tick. No supervisor node, no `unit` graph (N12), no real dispatcher (`dispatch.py` raises `NotImplementedError`) [C] |
| Main risk | Relay errors (000404: an unsourced claim was relayed as a rule), context loss at clear, a pending AskUserQuestion stalling all coordination | A model routes on text that workers wrote (a prompt-injection path); non-deterministic routing; "loses detail in translation" (R2 E1, LangChain benchmark) |

**A drawback specific to A.** When the SM session asks the owner with AskUserQuestion,
its whole turn waits on the answer. Messages from other sessions queue up behind it. With the tick
as the coordinator, this matters less: the tick keeps advancing every run that is not interrupted,
and only the SM session's presenting work waits. [I]

### 3. The hybrid: where the line sits

The rule I propose: **code decides what is legal and does every write; the LLM chooses among legal
options and explains; the owner decides at every gate.**

| Decision | Code (deterministic) | LLM (A's session or B's node) | Owner |
|---|---|---|---|
| Which phases may be claimed now | `--ready`, the Conflicts column, `max_active`, rendered order, the lease | Flags hazards the Conflicts column misses (the Scout's job, N4). It may *remove* a candidate, never add one | Approves each assignment |
| Which phase is proposed next | The first legal phase in rendered order | Nothing, unless the owner allows deviations; if allowed, it must cite a reason and code records it | Approves |
| Which node a run goes to next | The graph's edges: every G4 before any merge, gate_verify before G4 (P3 §4.2) | At exception edges only: park or retry (fix cycle ≤ 2, then park), with a written reason | Rules on parks |
| Whether a worker's question needs the owner | — | Answers from records (rulings, GOV-003) *with a citation*, or forwards it. An answer without a citation is forwarded [I] | Answers forwarded questions |
| How a gate item is presented | The fields: diff stat, both check runs, verdict ref | The summary and the recommendation | Decides |
| Writes to `dev`, the lease, the gate queue, removals | All of them, as the only executor | Never | Approves (D5) |
| Permission policy | Broker `check()`, allow and deny rules, hooks | Never | Sets the policy (000333) |

**How code constrains B's node.** Its output is a structured value that names one member of a set
the code computed, plus a reason. Code rejects anything outside the set and parks the run with a
gate item. The node sits in its own node, away from any interrupt, because on resume LangGraph
re-runs the node that holds the interrupt from its start (R2 E1). Put in the same node, a paid,
non-deterministic model call would run again and could return a different answer. Each routing
proposal is written to the ledger with the reason and a hash of its input. [C for the re-run rule;
I for the design]

**How the same rule constrains A.** The session may only call sanctioned verbs (`orchestrator
gate`, the lease verb, the coordination-log writer from protocol Q3). Owner ruling Q12 already makes
the writer refuse a `GRANTED merge`, an `ASSIGN` or a branch deletion that cites no approving
`DECISION` event (board.md:167). That is the same rule in its message-era form. [C]


### 5. D5 (who commits to `dev`) under each option

| D5 option | Under A | Under B |
|---|---|---|
| **(a)** The owner triggers each write; one deterministic command runs per approved item | The SM session runs the command. Any classifier prompt appears in the session the owner is already using, so approval stays in one window. This is what happens today, moved from builders to the SM | Needs an interactive session (the Owner Desk) to run the command, so it becomes option A for this purpose. The node cannot do it |
| **(b)** After G4 approval, the daemon runs the deterministic merge and completion edit under the lease | Works; the SM session only presents | Natural fit. **But** git run by the daemon is outside the Claude Code permission layer, so the classifier no longer acts as a second check. The recorded G4 decision is the only authority. REQ-022 R03 must be amended or read as satisfied (P3 D5) |
| **(c)** An LLM worker runs the git commands under a narrow allow rule | The SM session itself; the classifier still applies | The supervisor node or a worker. Against section 3's line: an LLM would perform the write. I do not recommend it under either option |

**O-3 applies until P3 N2:** builders self-merge (board.md:168). So D5 governs only once N2 exists,
and nothing needs to change before then. [C]


### 7. External facts (LangGraph, Agent SDK, Claude Code)

A sub-agent fetched these pages on 2026-09-24; I checked each against its quoted text. Harness
note: the sub-agent's reply triggered the "bypass-permissions" pattern flag. The flagged text is
its citation of the permission-mode list (7.2), not an instruction, and nothing was acted on.

#### 7.1 LangGraph

- **An interrupt waits indefinitely.** "LangGraph saves the graph state using its persistence layer
  and waits indefinitely until you resume execution." Open-source LangGraph has no expiry. The hosted
  platform has an opt-in thread TTL whose `delete` strategy would also remove a waiting thread.
  https://docs.langchain.com/oss/python/langgraph/interrupts ;
  https://docs.langchain.com/langsmith/configure-ttl
- **The node with the interrupt re-runs from its start on resume.** "Side effects called before
  `interrupt` must be idempotent." The docs advise putting them after the interrupt or in a
  separate node. Same interrupts URL.
- **Several interrupts can be pending at once** (parallel branches). They are resumed together by
  mapping each interrupt id to its value. Same URL, "Handling multiple interrupts".
- **Static `interrupt_before` and `interrupt_after` are "not recommended for human-in-the-loop
  workflows. Use the `interrupt` function instead."** Same URL.
- **Checkpointers.** `SqliteSaver` is described as "Local file-based storage for development".
  `PostgresSaver` is the documented production option.
  https://docs.langchain.com/oss/python/langgraph/persistence . The orchestrator uses `SqliteSaver`
  (`tick.open_checkpoint_store`). This is acceptable because checkpoints are disposable under
  ADR-018, but it should be a recorded choice. [C; I for "acceptable"]
- **`langgraph-supervisor` is deprecated:** "no longer actively maintained. Instead use the
  subagents pattern". https://docs.langchain.com/oss/python/migrate/langgraph-supervisor . The
  docs separate a *supervisor* ("a full agent that maintains conversation context and dynamically
  decides which subagents to call across multiple turns") from a *router* ("typically a single
  classification step").
  https://docs.langchain.com/oss/python/langchain/multi-agent/subagents . **What section 3 proposes
  is a router, not a supervisor.** The documented way to constrain it is structured output
  restricted to a `Literal` of allowed routes (`llm.with_structured_output(Route)`).
  https://docs.langchain.com/oss/python/langgraph/workflows-agents
- **No human inbox in open-source LangGraph.** Agent Inbox is a separate UI, and its repository is
  archived (https://github.com/langchain-ai/agent-inbox). The application must build its own
  surface. This supports summary point 1.

#### 7.2 Agent SDK

- **A headless SDK run can ask the owner a question and wait.** AskUserQuestion "triggers your
  `canUseTool` callback"; the application returns the answers in `updated_input`. The callback
  "can stay pending indefinitely". The application cannot add its own questions to this flow.
  https://code.claude.com/docs/en/agent-sdk/user-input
- **A `PreToolUse` hook can `defer` a call.** The process exits with `stop_reason: "tool_deferred"`
  and the pending call is kept in the transcript, with "no timeout or retry limit"; the run is
  resumed later.
  - It works only in `-p`/SDK mode and only when the turn holds a single tool call.
  - On resume, the stored permission mode is not restored.
  - Session files are deleted after `cleanupPeriodDays`, 30 by default.
  - https://code.claude.com/docs/en/hooks
- **Evaluation order:** hooks → deny rules → ask rules → mode → allow rules → `canUseTool`.
  "Auto-approved tools never reach `canUseTool`." A hook's deny applies even in the bypass mode.
  https://code.claude.com/docs/en/agent-sdk/permissions
- **Sessions** are stored under `~/.claude/projects/<encoded-cwd>/*.jsonl`, on the same machine
  only, and "persist the conversation, not the filesystem".
  https://code.claude.com/docs/en/agent-sdk/sessions

#### 7.3 Auto mode (the classifier)

- `auto` is an SDK mode, but SDK runs and `claude -p` start in `default`.
- In a non-interactive run without a permission-prompt tool, repeated blocks mean "the action doesn't
  run and Claude keeps working… Claude Code doesn't stop the run".
- https://code.claude.com/docs/en/permission-modes
- **So a headless worker in auto mode drops a blocked action silently.** SDK workers must run in
  `default` with `can_use_tool`, as P3 §4.5 already requires. Their denials must be recorded, not
  lost. [C; I for "must"]

#### 7.4 Remote Control and cost of a long-lived session

- **Remote Control.** "Claude Code keeps permission prompts and `AskUserQuestion` questions open
  until you answer them". A "Push when actions required" setting covers both. The session goes
  offline if its terminal closes. https://code.claude.com/docs/en/remote-control
- **Cost of a long-lived session:**
  - "a one-line question in a session that has been open all day still draws usage for the whole
    conversation";
  - a break longer than the cache lifetime reprocesses the whole context;
  - "compacting a large context is itself a large request";
  - cross-session messages and idle scheduled tasks each send the full context.
  - https://code.claude.com/docs/en/costs . SDK auto-compaction may lose "specific instructions from
    early in the conversation" (https://code.claude.com/docs/en/agent-sdk/agent-loop).
  - **Impact on option A:** every SendMessage the SM session receives pays its whole context. A
    presenter-only SM that clears between sittings keeps this bounded. The Scout's decision-5
    polling must not run often. [I]

#### 7.5 What changed in this report because of 7.1-7.4

- **Worker questions (4.7) and permission prompts (4.9) now have a third mechanism.**
  - A worker's AskUserQuestion, or a tool call that needs approval, can be held in `can_use_tool`,
    or deferred with the transcript kept.
  - The application writes a gate item, and the run resumes with the owner's answer.
  - The worker then keeps its in-task context, which P3's deny-and-park loses.
- **The supervisor node should be built as a router node** with `Literal` structured output, not
  with the deprecated `langgraph-supervisor` package.

