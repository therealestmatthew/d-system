---
schema_version: 1
id: doc-agent-replicator
code: PLAN-054
title: Agent Replicator — fleet tracker files and a generalized orchestration model, one Python core with bash and PowerShell shells, a double-click restart of every agent session, and the GOV-017 wiring
kind: plan
status: approved
owner: repository-owner
created: '2026-10-12'
updated: '2026-10-13'
systems: [sys-fleet, sys-governance, sys-gov-docs, sys-backlog]
depends_on: [doc-agent-replicator-requirements, doc-multi-session-coordination-protocol, doc-prompt-session-manager-starter-messages, doc-realization-role-contracts, doc-live-demo, doc-adr-session-manager-into-orchestrator, doc-backlog-decisions]
---

# Agent Replicator

Delivers [REQ-039](../06-requirements/REQ-039-agent-replicator.md), for idea `000693` (the
Agent Replicator). Related ideas read for context: `000515` (reopen every planning session after a
restart), `000514` (a catalog of repeatable automation commands), `000389` (session state and
resumability) and `000540` (the multi-session orchestration ships with the engine). This plan
covers the launcher `000515` asks for, but promotes none of the four.

**Status: approved at G3 on 2026-10-13.** Written 2026-10-12 by Session 3 - Standby Builder on an owner-approved
assignment relayed by the Session Manager, running unclaimed (no backlog phase). The inputs were
the Advisor's answers A1 (the Replicator) and A2 (the fleet model) and the owner's rulings on each,
under `_working/session-manager/advisor/` (gitignored). `REQ-039`, *Accepted decisions*, quotes
the rulings. It was reviewed under `GOV-018` at the plan and phase altitudes. The review record is
`2026-10-12-plan-054`, with ten findings, dispositioned on 2026-10-13 by the same session as planner
stand-in. The same revision applied the Advisor's check of the drafts against the rulings. A
later-added review of `phase-rep-07`, `2026-10-13-plan-054-later-added`, had one finding, also
fixed. The owner approved the plan and `REQ-039` at G3 on 2026-10-13, relayed by the Session
Manager, including the departure that moves the system files from the first phase to
`phase-rep-07`.

## Context and scope

`REQ-039` lists six problems. In short: sessions are opened by two gitignored scripts from a
roster nothing checks; session ids are found afterwards by searching transcripts; nothing stops a
session safely; the authority to start, stop and restart sessions is written as prose for one
arrangement only; there is no Windows path; and restarting every session takes several terminal
steps.

The owner ruled that the design must not be specific to the Session Manager arrangement: "It
should be generalizable to understanding orchestration systems in general". So the plan models
orchestration as data. The Session Manager arrangement of `GOV-017` becomes one system file among
three, and the code reads every authority decision from those files.

## Decisions

**D1. Five kinds of thing make up the model.**

| Kind | What it is | Where it lives |
|---|---|---|
| Agent definition | How to start an agent: model, effort, permission mode, allowed and denied tools, prompt source (a `.claude/agents/` file or a prompt file), working directory (`cwd`), whether Remote Control is on (`remote_control`), how it is started (`launcher`: `tab` or `background`), and kind (`session`, `subagent` or `owner-manual`) | `definitions.yaml` (tracked); overlay (gitignored) |
| Role | A position in one system: the definition it uses, its group (`meta`, `execution`, `owner`, `support`), how many instances it may have, and who controls its lifecycle (`replicator`, `owner-only` or `parent`) | the system file |
| Orchestration system | Roles, edges between roles, shared resources (locks, slot pools), message types, lifecycle hooks (which role winds down the others, the message that says it is ready to restart, which role gets the kickoff, the kickoff template, new or resume by default), governing documents, and kill preconditions | `systems/<system-id>.yaml` (tracked) |
| Agent instance | One running agent in a role. A session has a name, uuid, pid, working directory, host and launcher; a subagent has a parent and a dispatch time, recorded only when observed | the event log (gitignored) |
| Relationship (edge) | A typed, directed link between two roles (static, in the system file) or two instances (runtime, in the event log) | system file; event log |

A subagent definition points at its `.claude/agents/` file and reads model and tools from that
file's front matter rather than copying them, so the two cannot drift.

The rejected alternative was a flat roster, one row per session as `sessions.json` has today.
That cannot say which session may stop which, or describe a subagent arrangement at all, so the
authority rule would have to live in code for each arrangement, which the owner ruled out.

**D2. A fixed set of edge types and lifecycle events.** Edge types: `coordinates`, `delegates-to`,
`reviews`, `hands-off-to`, `messages`, `shares-resource`, `holds`, `approves`, `launches`,
`kills`, `restarts`. `holds` is runtime only: it links an instance to a resource the system file
declares (a lock or a slot), opened by one event and closed by another. `launches`, `kills` and
`restarts` carry an authority attribute, `request` or `execute`; other attributes
are cardinality, `max_cycles` and `required`. Lifecycle events: `defined`, `registered`,
`launched`, `acked`, `busy`, `idle`, `safe`, `wind-down-requested`, `restart-ready`, `killed`,
`respawned`, `failed`, `orphan-detected`, `retired`, `deregistered`. The schemas enumerate both
lists and the governance document defines each value; a test keeps the two in agreement (R01). A
new type is a change to both, reviewed like any governance change. The rejected alternative,
free-text types chosen per system file, would let two systems name the same relationship
differently, and the authority rule (D6) could not match an edge to a verb.

**D3. The tracked files sit under `docs/08-governance/fleet/`.** The owner ruled this location.
`docs/08-governance/` already holds governance data (`systems.yaml`, `codes.yaml`), so the files
need no orientation row in `CLAUDE.md`. The schemas are `schemas/fleet.schema.json`,
`schemas/fleet-definition.schema.json` and `schemas/fleet-system.schema.json`. The governance
document is `docs/08-governance/GOV-023-fleet-model.md` and the operations document for
`tools/fleet.py` is `docs/08-governance/OPS-034-fleet.md`; both codes were allocated at planning
time so each phase declares exact paths.

| File | Holds |
|---|---|
| `fleet.yaml` | Host facts (operating system, terminal launcher, Claude Code projects directory), the enabled systems, defaults, and the fleet-level roles that belong to no one system: the Replicator and the Owner Terminal, both `owner-only`. A system that lists either of them in its governing roster (as `GOV-017` lists the Owner Terminal) has a role that references the fleet-level role rather than redefining it |
| `definitions.yaml` | Every agent definition. The permission-mode enum is `auto`, `manual`, `dontAsk`, `plan`; there is no bypass value (R05) |
| `systems/gov017-multi-session.yaml` | The `GOV-017` arrangement: one role per row of *The sessions*, including the Owner Terminal as an `owner-only` role that references the fleet-level role, plus the Advisor (lifecycle `replicator`) and the Replicator, both marked as not yet in the governing table until `phase-rep-05` |
| `systems/demo-build.yaml` | The `PLAN-021` live-demo build: orchestrators and the creators and validators they dispatch, all lifecycle `parent` |
| `systems/idea-realization.yaml` | The `GOV-014` roles, with the `hands-off-to` chain and the owner's `approves` edges at each gate |

The rejected alternative, a new top-level directory, needs a `CLAUDE.md` row and the owner's
approval of that edit.

**D4. Runtime state is one append-only log, folded like the idea log.** The owner ruled for one
log. `_working/agents/events.jsonl` holds instance events and edge events; the core folds it into
current state the same way `src/db/ideas.py` folds `_data/ideas.jsonl`. Other gitignored paths
under `_working/agents/`: `pids/<instance-id>`, `overlay/definitions.local.yaml` and
`overlay/systems.local.yaml`, `restart/<system-id>` (the restart pointer), and `map/` (the
generated fleet map). The log replaces `session-ids.json` and `current-restart`. The rejected
alternative, separate instance and edge logs, would need two folds kept in step.

**D5. One Python core, thin shells.** The owner ruled this shape. `tools/fleet.py` does everything
that is a decision: fold, authority, command derivation from the fleet files, dry run, status,
the fleet map. `tools/fleet/fleet.sh` and `tools/fleet/fleet.ps1` only open a terminal tab, start
a process, capture its pid, write the pidfile and send a signal, and they call the core for
everything else. The rejected alternative, two full script sets, would give two places for the
authority rule to differ.

**D6. Every lifecycle request goes through one authority rule.** A request is
`FLEET <verb> <system> <target> [args]`, with verbs `launch`, `kill`, `restart`, `status`,
`register`, `hold` and `release`. The core:

1. identifies the requester from the sender's registered name, through the folded instances, to
   a role; an unknown sender is refused and logged;
2. passes the owner straight to step 4; for anyone else, looks for an edge from the requester's
   role to the target's role whose type matches the verb, with authority `request`; executes only
   for a target whose role has lifecycle `replicator`;
3. checks every kill precondition the system file lists;
4. executes, which in the Replicator means a tool call the owner approves (D10);
5. logs the outcome and replies `FLEET-DONE` or `FLEET-REFUSED` with the reason.

`hold` and `release` start and stop no process. `FLEET hold <system> <resource> <holder>` opens a
`holds` edge from the holder's instance to a resource the system file declares, and `release`
closes it. Each declared resource names the role that grants it; only that role or the owner may
send `hold` or `release` for it, and steps 3 and 4 do not apply. The `resource_free` predicate
(D7) reads these edges.

Nothing in the code names a role, system or document; the system files supply all of it (R06). A
fourth system, such as an `ADR-023` orchestrator, is a fourth file.

Identity is the registered name, which `/rename` can change. The owner ruled that the per-call
approval is the safeguard, so the approval prompt shows the requester and the matched edge. The
rejected alternative, refusing agent-requested kills until a uuid can be verified, would block
the restart hand-off this plan exists for.

**D7. The predicate vocabulary is fixed in code and composed in system files.** The owner ruled
this. Each predicate is checked from something a program can observe:

| Predicate | Holds when |
|---|---|
| `lock_free` | No git operation is under way in the primary checkout or any worktree the system's roles use: no `index.lock`, no rebase or merge directory |
| `target_safe` | The target's last lifecycle event is `safe` and nothing later supersedes it |
| `target_idle` | The target's last lifecycle event is `idle` |
| `coordinator_restart_ready` | The system's wind-down role has logged its restart-ready message after the system's last launch |
| `resource_free` | No `holds` edge is open on any resource the system file declares (D2): no instance holds a lock or a slot |

The rejected alternative, expressions in YAML, would need an evaluator and lets a system file
state a condition no code checks.

`resource_free` departs from the Advisor's A2 list, which had four predicates. `lock_free` sees
only git's own state, so it cannot tell that a session has been granted the primary-checkout
lock and has not yet started a git command. A system that declares a lock records each grant and
release as a `holds` edge through `FLEET hold` and `FLEET release` (D6), and `resource_free` reads
them. Its result is only as current as those messages. For `GOV-017` the granting role is the
Session Manager, which grants the primary-checkout lock: it sends `hold` with each `GRANTED` and
`release` when it receives each `TURN DONE`. `phase-rep-05` writes that into `GOV-017` and the system file.

**D8. Launch pre-assigns the session id; kill checks it.** Each launch writes a `launched` event
with a fresh uuid, then starts `claude --session-id <uuid> --name <name> ...`. On Linux the shell
starts the process with `setsid` so it heads its own process group, and writes the pidfile. A
kill reads the pid from the folded state, checks that `/proc/<pid>/cmdline` contains the uuid,
and sends `SIGTERM` to the process group. When the command line does not contain the uuid (the
process has exited and the pid was reused, or the pidfile is stale), the kill is refused, a
`failed` event records the reason, and the instance is reported as `orphan-detected` for the owner
to look at. `SIGKILL` needs a second owner approval. On Windows the
shell opens a `wt.exe` tab, finds the process with `Get-CimInstance Win32_Process` by the uuid in
its command line, and stops the tree with `Stop-Process` or `taskkill /T`, with the same refusal
on a mismatch. Nothing kills by process name (R10). The rejected alternative is today's method:
start the session unnamed by id, then find the id by searching transcripts for the newest title
that matches the name (`relaunch-sessions.sh --record-ids`). A rename or two sessions with one
name gives the wrong id, and a kill by name can stop a session that was not meant.

**D9. A system restart follows the system file's hooks.** The Replicator waits for the
wind-down role's restart-ready message (for `GOV-017` today, `RESTART-READY <file> <new|resume>`,
written in the system file, not in code). It then kills the system's `replicator`-lifecycle
instances in reverse dependency order, relaunches them in forward order with the kickoff for the
kickoff role, checks each name with `ListAgents`, and reports the roster: name, uuid and pid
for each. It never touches `owner-only` roles. The rejected alternative, a restart sequence
written into the tool, is the Session Manager-specific design the owner ruled out; a second
system with a different wind-down would need a code change.

**D10. The Replicator is a session in the manual permission mode, listed in the fleet.** The
owner ruled the manual mode, so the owner approves every launch and kill it makes. It and the
Advisor are definitions in `definitions.yaml`. The Replicator is a fleet-level `owner-only` role
in `fleet.yaml`, because it serves every system; the Advisor is a role in the `GOV-017` system with
lifecycle `replicator`. The owner starts the Replicator from the desktop, because tab launching
needs a display (`relaunch-sessions.sh` refuses without one). The owner ruled for manual over
auto. The rejected alternative, auto mode, would let the permission classifier be the only check
on a kill, and a session that is stopped wrongly cannot be resumed mid-step.

**D11. On-the-fly agents go in a gitignored overlay.** An overlay definition names a tracked
definition it extends. The core refuses an overlay that widens the permission mode or adds an
allowed tool or removes a denied one. To keep an overlay agent, its definition is copied into
`definitions.yaml` in an ordinary reviewed change. The owner ruled for the overlay. The rejected
alternative, committing every new definition before its first launch, would put a primary-checkout
turn and a merge in front of every one-off agent.

**D12. The double-click launcher restarts every agent session.** The owner asked for "a simple
script I can double click to run and reboot the system", meaning every agent session, with the
computer staying up. The launcher is `tools/fleet/restart-agents.sh` with a `.desktop` file on
Linux, and `tools/fleet/restart-agents.ps1` with a `.cmd` wrapper on Windows; a
`fleet.py install-launcher` command writes the `.desktop` file or Windows shortcut to the owner's
desktop when the owner runs it. The launcher runs as the owner, so the authority rule passes it
(D6, step 2). It:

1. runs the core's restart dry run over every enabled system and shows the list of sessions it
   will restart, and for each system whether its wind-down role has logged restart-ready;
2. refuses while `lock_free` fails, and says which repository has an operation under way;
3. asks the owner to confirm, with a stronger warning when a system has not logged
   restart-ready or when `resource_free` fails (a session holds a declared lock or slot);
4. restarts each system as D9 describes, resuming each session by its recorded uuid unless the
   system file's default is `new`. When a system has not logged restart-ready and the owner
   confirms anyway, it resumes each session by its recorded uuid and logs each kill with the
   reason `owner-forced-no-restart-ready`;
5. leaves the Owner Terminal alone and restarts the Replicator last (OQ1).

The Linux `.desktop` file sets `Terminal=true`, so the confirmation and any refusal are shown in
a terminal window. The Windows `.cmd` wrapper pauses on a non-zero exit, so a failure stays on
screen until the owner closes it.

The rejected alternative, a launcher that only sends a request to the Replicator, would fail
whenever the Replicator is the session that has stopped working.

**D13. A self-test system settles the unknowns before anything live.** `rep-03` adds a fixture
system, `fleet-selftest`, with one throwaway session. Launching, listing, killing and relaunching
it answers A1's three open questions (R19) without disturbing a working session. The live
restart of every session waits for `rep-05`. The rejected alternative, settling the three
questions in the first live restart, would test unknown launch behaviour on every working session
at once, and a wrong answer would leave the whole arrangement down.

**D14. PowerShell is written now and checked in CI.** The owner reversed the earlier deferral.
`rep-04` writes the `.ps1` shell and launcher, adds `.gitattributes` (LF for `.sh` and `.ps1`, CRLF
for `.cmd`) and a `windows-latest` job in `.github/workflows/ci.yaml` that runs the dry run through
`fleet.ps1`. The workflow edit sends the change through a security review. Behaviours that need a
Windows host are listed in the operations document as unverified: `wt.exe` tab titles, pid capture
when `wt.exe` re-parents the process, whether the command line is visible through CIM, tree-kill
behaviour, `--remote-control` and `--session-id` on Windows, the projects-directory name encoding,
execution policy, Git Bash presence, and `uv` and Python on `PATH`. The owner ruled for writing it
now. The rejected alternative, deferring it until a Windows host exists, was the Advisor's first
recommendation; its cost is that nothing about the Windows path is known until that host appears,
and the core's interface could settle in a shape the PowerShell shell cannot use.

**D15. A new system id, `sys-fleet`, is registered now as planned.** It names the fleet core,
shells, schemas and data, so `rep-*` phases lock it rather than all of `sys-governance`. This
follows `sys-auto-gateway`, registered as planned with only its plan as a path. `rep-01` adds the
real paths when they exist. The rejected alternative, tagging the phases `sys-governance`, would
make every `rep-*` phase collide with every phase that touches the governance engine, though none
of them changes `src/governance`.

## Implementation phases

| Phase | What | Requirements | Depends on |
|---|---|---|---|
| `phase-rep-01` | `GOV-023` (model, edge types, lifecycle events, authority rule, predicates, owner-only kinds, overlay limits); three schemas; `fleet.yaml` and `definitions.yaml` (including the Replicator and the Advisor); the schema, integrity and enum-agreement tests; `sys-fleet` paths | R01, R02, R04 (references), R05 (schema), R13 (data) | none |
| `phase-rep-07` | The three system files (`gov017-multi-session`, `demo-build`, `idea-realization`) and the roster test that compares a system file with its governing table. The demo build's roster is `PROMPT-012`'s ten agents plus the coordinator session of `PROMPT-014`, which itself dispatches `demo-adversary` and `demo-validator-web` (`PROMPT-018`) | R03, R04 (roster) | `phase-rep-01` |
| `phase-rep-02` | `tools/fleet.py`: fold, authority, command derivation, dry run, status, fleet map, overlay checks; `OPS-034`; fixtures for each edge type, each predicate, each refusal, a fourth system and an overlay | R05 (overlay), R06–R09, R11–R13, R18 | `phase-rep-07` |
| `phase-rep-03` | `tools/fleet/fleet.sh`: tabs, `setsid`, pidfiles, uuid-checked kill; `restart-agents.sh`, its `.desktop` file and `install-launcher`; the `fleet-selftest` system and its live run; the proposal to the owner to retire the two interim scripts | R10, R14, R17 (Linux), R19 | `phase-rep-02` |
| `phase-rep-04` | `tools/fleet/fleet.ps1`, `restart-agents.ps1` and its `.cmd` wrapper; `.gitattributes`; the `windows-latest` dry-run job; the unverified list in the `OPS` document | R15, R16, R17 (Windows) | `phase-rep-02`, `phase-rep-03` |
| `phase-rep-05` | The wiring: `GOV-017` (Replicator row, `FLEET` and restart messages, restart procedure, `hold` and `release` on each lock grant and release), `PROMPT-037` (Replicator starter), the `GOV-003` entry recording the owner's rulings; one live restart of every agent session through the Replicator at an owner-scheduled wind-down | R20, R21 | `phase-rep-03` |
| `phase-rep-06` | Optional spike: `claude --bg` with Remote Control, written up as a recommendation | none (spike) | `phase-rep-03` |

## Requirement coverage

| Requirement | Phase | Acceptance evidence |
|---|---|---|
| R01 | `phase-rep-01` | The document; the enum-agreement test |
| R02 | `phase-rep-01` | The schema tests and their invalid fixtures |
| R03 | `phase-rep-07` | The three system files |
| R04 | `phase-rep-01` (references), `phase-rep-07` (roster) | The integrity test; the `GOV-017` roster test |
| R05 | `phase-rep-01` (schema), `phase-rep-02` (overlay) | The bypass fixture; the overlay fixtures |
| R06 | `phase-rep-02` | The fourth-system fixture; the `grep` returning nothing |
| R07 | `phase-rep-02` | The core tests |
| R08 | `phase-rep-02` | The fold test; `git check-ignore` |
| R09 | `phase-rep-02` | The dry run showing the uuid and the `launched` event |
| R10 | `phase-rep-03` | The dummy-process kill tests; the `grep` for `pkill` and `killall` |
| R11 | `phase-rep-02` | The authority tests |
| R12 | `phase-rep-02` | The predicate tests; the unknown-predicate fixture |
| R13 | `phase-rep-01` (roles), `phase-rep-02` (refusals) | The owner-only refusal tests |
| R14 | `phase-rep-03` | The self-test run; the duplicate-refusal dry run |
| R15 | `phase-rep-04` | The `pwsh` parse; the CI job's run |
| R16 | `phase-rep-04` | `git check-attr eol` |
| R17 | `phase-rep-03`, `phase-rep-04`, `phase-rep-05` | The Linux dry run; the CI dry run; the live restart |
| R18 | `phase-rep-02` | The overlay tests; the `OPS` promotion steps |
| R19 | `phase-rep-03` | The session record's three answers |
| R20 | `phase-rep-05` | The `GOV-017` rows; the live restart's record |
| R21 | `phase-rep-01` (definition), `phase-rep-05` (prompt quoted) | The Replicator definition; the quoted approval prompt |

Every requirement maps to a phase, and every phase except the optional spike has a row.

`phase-rep-07` was split out of `phase-rep-01` after the plan review (finding F03). The new
governance document, three schemas and the integrity tests fill one session; the three system
files model 9, 10 and the demo build's roles from three documents, and the roster test needs
them. The phase id is `rep-07` rather than a renumbering, so the review record's references to
`phase-rep-01` to `phase-rep-06` stay correct.

## Execution order and real concurrency

- Every `rep-*` phase declares `sys-fleet`, so no two of them are ever active together. They run
  one at a time: `rep-01` → `rep-07` → `rep-02` → `rep-03`, each reading what the previous one
  wrote, then `rep-04`, `rep-05` and `rep-06` in whatever order the owner places them. `rep-04`
  is ordered after `rep-03` so the PowerShell shell follows a Linux shell that has run live.
- **`phase-mode-03` collision.** `phase-rep-05` and `phase-mode-03` (the autonomy setting's
  `GOV-017` and `PROMPT-037` wiring) are the only queued phases that edit those two files. They do
  not depend on each other; declaring the same deliverables keeps them from being active at once,
  and whichever runs second rebases onto the other's text.
- `rep-01` adds files in `docs/08-governance/` and `schemas/`, as `phase-mode-01` and
  `phase-mode-02` do. Those two declare the whole `docs/08-governance/` directory and share
  `sys-gov-docs` with every `rep-*` phase, so the validator keeps any `rep-*` phase and either of
  them from being active together; whichever merges second rebases.
- `rep-04` edits `.github/workflows/ci.yaml`, which any CI phase also edits.
- The owner placed the chain at the front of `next_up` at G3 (OQ5).

## Out of scope

- **Moving the orchestration into the plugin or the engine** (`000540`), and the `ADR-023`
  orchestrator. Both would read these files.
- **Generating restart files from recorded state** (`000389`). The restart pointer moves to
  `_working/agents/restart/`; what the restart file says is unchanged.
- **Managing subagent lifecycles.** Subagents' roles have lifecycle `parent`; the files describe
  them and the Replicator starts or stops none.
- **Any edit to `AGENTS.md` or `CLAUDE.md`** (D3).
- **Deleting the interim scripts.** They are under `_working/`; `rep-03` proposes their removal
  and the owner decides.

## Open questions

All five were ruled by the owner at G3 on 2026-10-13, relayed by the Session Manager.

- **OQ1. Does the double-click launcher restart the Replicator?** Yes, last. It never restarts
  the Owner Terminal (D12, step 5).
- **OQ2. What the launcher does when no coordinator has reported ready to restart.** As D12
  states: warn, ask again, then resume each session by its recorded uuid and log each kill as
  `owner-forced-no-restart-ready`; refuse only while `lock_free` fails.
- **OQ3. Where the launcher's desktop file is installed.** Only by `install-launcher`, when the
  owner runs it: `~/.local/share/applications` and `~/Desktop` on Linux, the desktop on Windows.
- **OQ4. Registering `sys-fleet` in this planning change** (D15). Yes.
- **OQ5. Queue position.** The whole chain goes to the front of `next_up`, ahead of
  `phase-cap-08`, in dependency order: `phase-rep-01`, `phase-rep-07`, `phase-rep-02`,
  `phase-rep-03`, `phase-rep-04`, `phase-rep-05`, `phase-rep-06`.
