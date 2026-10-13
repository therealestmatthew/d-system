---
schema_version: 1
id: doc-agent-replicator
code: PLAN-054
title: Agent Replicator — fleet tracker files and a generalized orchestration model, one Python core with bash and PowerShell shells, a double-click restart of every agent session, and the GOV-017 wiring
kind: plan
status: draft
owner: repository-owner
created: '2026-10-12'
updated: '2026-10-12'
systems: [sys-fleet, sys-governance, sys-gov-docs, sys-backlog]
depends_on: [doc-agent-replicator-requirements, doc-multi-session-coordination-protocol, doc-prompt-session-manager-starter-messages, doc-realization-role-contracts, doc-live-demo, doc-adr-session-manager-into-orchestrator, doc-backlog-decisions]
---

# Agent Replicator

Delivers [REQ-039](../06-requirements/REQ-039-agent-replicator.md), for idea `000693` (the
Agent Replicator). Related ideas read for context: `000515` (reopen every planning session after a
restart), `000514` (a catalog of repeatable automation commands), `000389` (session state and
resumability) and `000540` (the multi-session orchestration ships with the engine). This plan
covers the launcher `000515` asks for, but promotes none of the four.

**Status: draft.** Written 2026-10-12 by Session 3 - Standby Builder on an owner-approved
assignment relayed by the Session Manager, running unclaimed (no backlog phase). The inputs were
the Advisor's answers A1 (the Replicator) and A2 (the fleet model) and the owner's rulings on each,
under `_working/session-manager/advisor/` (gitignored). `REQ-039`, *Accepted decisions*, quotes
the rulings. It awaits the plan review and G3.

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
| Agent definition | How to start an agent: model, effort, permission mode, allowed and denied tools, prompt source (a `.claude/agents/` file or a prompt file), and kind (`session`, `subagent` or `owner-manual`) | `definitions.yaml` (tracked); overlay (gitignored) |
| Role | A position in one system: the definition it uses, its group (`meta`, `execution`, `owner`, `support`), how many instances it may have, and who controls its lifecycle (`replicator`, `owner-only` or `parent`) | the system file |
| Orchestration system | Roles, edges between roles, shared resources (locks, slot pools), message types, lifecycle hooks (which role winds down the others, the message that says it is ready to restart, which role gets the kickoff, the kickoff template, new or resume by default), governing documents, and kill preconditions | `systems/<system-id>.yaml` (tracked) |
| Agent instance | One running agent in a role. A session has a name, uuid, pid, working directory, host and launcher; a subagent has a parent and a dispatch time, recorded only when observed | the event log (gitignored) |
| Relationship (edge) | A typed, directed link between two roles (static, in the system file) or two instances (runtime, in the event log) | system file; event log |

A subagent definition points at its `.claude/agents/` file and reads model and tools from that
file's front matter rather than copying them, so the two cannot drift.

**D2. A fixed set of edge types and lifecycle events.** Edge types: `coordinates`, `delegates-to`,
`reviews`, `hands-off-to`, `messages`, `shares-resource`, `approves`, `launches`, `kills`,
`restarts`. The last three carry an authority attribute, `request` or `execute`; other attributes
are cardinality, `max_cycles` and `required`. Lifecycle events: `defined`, `registered`,
`launched`, `acked`, `busy`, `idle`, `safe`, `wind-down-requested`, `restart-ready`, `killed`,
`respawned`, `failed`, `orphan-detected`, `retired`, `deregistered`. The schemas enumerate both
lists and the governance document defines each value; a test keeps the two in agreement (R01). A
new type is a change to both, reviewed like any governance change.

**D3. The tracked files sit under `docs/08-governance/fleet/`.** The owner ruled this location.
`docs/08-governance/` already holds governance data (`systems.yaml`, `codes.yaml`), so the files
need no orientation row in `CLAUDE.md`. The schemas are `schemas/fleet.schema.json`,
`schemas/fleet-definition.schema.json` and `schemas/fleet-system.schema.json`.

| File | Holds |
|---|---|
| `fleet.yaml` | Host facts (operating system, terminal launcher, Claude Code projects directory), the enabled systems, defaults, and the fleet-level roles that belong to no one system: the Replicator and the Owner Terminal, both `owner-only` |
| `definitions.yaml` | Every agent definition. The permission-mode enum is `auto`, `manual`, `dontAsk`, `plan`; there is no bypass value (R05) |
| `systems/gov017-multi-session.yaml` | The `GOV-017` arrangement, including the Advisor (lifecycle `replicator`) |
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
`register`. The core:

1. identifies the requester from the sender's registered name, through the folded instances, to
   a role; an unknown sender is refused and logged;
2. passes the owner straight to step 4; for anyone else, looks for an edge from the requester's
   role to the target's role whose type matches the verb, with authority `request`; executes only
   for a target whose role has lifecycle `replicator`;
3. checks every kill precondition the system file lists;
4. executes, which in the Replicator means a tool call the owner approves (D10);
5. logs the outcome and replies `FLEET-DONE` or `FLEET-REFUSED` with the reason.

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

The rejected alternative, expressions in YAML, would need an evaluator and lets a system file
state a condition no code checks.

**D8. Launch pre-assigns the session id; kill checks it.** Each launch writes a `launched` event
with a fresh uuid, then starts `claude --session-id <uuid> --name <name> ...`. On Linux the shell
starts the process with `setsid` so it heads its own process group, and writes the pidfile. A
kill reads the pid from the folded state, checks that `/proc/<pid>/cmdline` contains the uuid,
and sends `SIGTERM` to the process group. `SIGKILL` needs a second owner approval. On Windows the
shell opens a `wt.exe` tab, finds the process with `Get-CimInstance Win32_Process` by the uuid in
its command line, and stops the tree with `Stop-Process` or `taskkill /T`. Nothing kills by
process name (R10).

**D9. A system restart follows the system file's hooks.** The Replicator waits for the
wind-down role's restart-ready message (for `GOV-017` today, `RESTART-READY <file> <new|resume>`,
written in the system file, not in code). It then kills the system's `replicator`-lifecycle
instances in reverse dependency order, relaunches them in forward order with the kickoff for the
kickoff role, checks each name with `ListAgents`, and reports the roster: name, uuid and pid
for each. It never touches `owner-only` roles.

**D10. The Replicator is a session in the manual permission mode, listed in the fleet.** The
owner ruled the manual mode, so the owner approves every launch and kill it makes. It and the
Advisor are definitions in `definitions.yaml`. The Replicator is a fleet-level `owner-only` role
in `fleet.yaml`, because it serves every system; the Advisor is a role in the `GOV-017` system with
lifecycle `replicator`. The owner starts the Replicator from the desktop, because tab launching
needs a display (`relaunch-sessions.sh` refuses without one).

**D11. On-the-fly agents go in a gitignored overlay.** An overlay definition names a tracked
definition it extends. The core refuses an overlay that widens the permission mode or adds an
allowed tool or removes a denied one. To keep an overlay agent, its definition is copied into
`definitions.yaml` in an ordinary reviewed change.

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
   restart-ready;
4. restarts each system as D9 describes, resuming each session by its recorded uuid unless the
   system file's default is `new`;
5. leaves the Owner Terminal alone and restarts the Replicator last (OQ1).

The rejected alternative, a launcher that only sends a request to the Replicator, would fail
whenever the Replicator is the session that has stopped working.

**D13. A self-test system settles the unknowns before anything live.** `rep-03` adds a fixture
system, `fleet-selftest`, with one throwaway session. Launching, listing, killing and relaunching
it answers A1's three open questions (R19) without disturbing a working session. The live
restart of every session waits for `rep-05`.

**D14. PowerShell is written now and checked in CI.** The owner reversed the earlier deferral.
`rep-04` writes the `.ps1` shell and launcher, adds `.gitattributes` (LF for `.sh` and `.ps1`, CRLF
for `.cmd`) and a `windows-latest` job in `.github/workflows/ci.yaml` that runs the dry run through
`fleet.ps1`. The workflow edit sends the change through a security review. Behaviours that need a
Windows host are listed in the operations document as unverified: `wt.exe` tab titles, pid capture
when `wt.exe` re-parents the process, whether the command line is visible through CIM, tree-kill
behaviour, `--remote-control` and `--session-id` on Windows, the projects-directory name encoding,
execution policy, Git Bash presence, and `uv` and Python on `PATH`.

**D15. A new system id, `sys-fleet`, is registered now as planned.** It names the fleet core,
shells, schemas and data, so `rep-*` phases lock it rather than all of `sys-governance`. This
follows `sys-auto-gateway`, registered as planned with only its plan as a path. `rep-01` adds the
real paths when they exist.

## Implementation phases

| Phase | What | Requirements | Depends on |
|---|---|---|---|
| `phase-rep-01` | The governance document (model, edge types, lifecycle events, authority rule, predicates, owner-only kinds, overlay limits); three schemas; `fleet.yaml`, `definitions.yaml` (including the Replicator and the Advisor) and the three system files; the integrity, enum-agreement and `GOV-017` roster tests; `sys-fleet` paths | R01–R05, R13 (data) | none |
| `phase-rep-02` | `tools/fleet.py`: fold, authority, command derivation, dry run, status, fleet map, overlay checks; its `OPS` document; fixtures for each edge type, each predicate, each refusal, a fourth system and an overlay | R05 (overlay), R06–R09, R11–R13, R18 | `phase-rep-01` |
| `phase-rep-03` | `tools/fleet/fleet.sh`: tabs, `setsid`, pidfiles, uuid-checked kill; `restart-agents.sh`, its `.desktop` file and `install-launcher`; the `fleet-selftest` system and its live run; the proposal to the owner to retire the two interim scripts | R10, R14, R17 (Linux), R19 | `phase-rep-02` |
| `phase-rep-04` | `tools/fleet/fleet.ps1`, `restart-agents.ps1` and its `.cmd` wrapper; `.gitattributes`; the `windows-latest` dry-run job; the unverified list in the `OPS` document | R15, R16, R17 (Windows) | `phase-rep-02`, `phase-rep-03` |
| `phase-rep-05` | The wiring: `GOV-017` (Replicator row, `FLEET` and restart messages, restart procedure), `PROMPT-037` (Replicator starter), the `GOV-003` entry recording the owner's rulings; one live restart of every agent session through the Replicator at an owner-scheduled wind-down | R20, R21 | `phase-rep-03` |
| `phase-rep-06` | Optional spike: `claude --bg` with Remote Control, written up as a recommendation | none (spike) | `phase-rep-03` |

## Requirement coverage

| Requirement | Phase | Acceptance evidence |
|---|---|---|
| R01 | `phase-rep-01` | The document; the enum-agreement test |
| R02 | `phase-rep-01` | The schema tests and their invalid fixtures |
| R03 | `phase-rep-01` | The three system files |
| R04 | `phase-rep-01` | The integrity test and the `GOV-017` roster test |
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

## Execution order and real concurrency

- `rep-01` → `rep-02` → `rep-03`, in order: each reads what the previous one wrote.
- `rep-04` depends on `rep-02` and is ordered after `rep-03` so the PowerShell shell copies a
  Linux shell that has run live. `rep-05` and `rep-06` need only `rep-03`, so `rep-04`, `rep-05`
  and `rep-06` can run in parallel once `rep-03` is complete, subject to the collisions below.
- **`phase-mode-03` collision.** `phase-rep-05` and `phase-mode-03` (the autonomy setting's
  `GOV-017` and `PROMPT-037` wiring) edit the same two files. They do not depend on each other;
  declaring the same deliverables keeps them from being active at once, and whichever runs second
  rebases onto the other's text. `phase-grd-03` and `phase-asr-04` also edit those files.
- `rep-01` writes new files in `docs/08-governance/` and `schemas/`, as `phase-mode-01` and
  `phase-mode-02` do. Their deliverables are different files, so the validator does not block
  them; both register a schema, so whichever merges second rebases.
- `rep-04` edits `.github/workflows/ci.yaml`, which any CI phase also edits.
- No phase goes into `next_up` without the owner's word (OQ5).

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

- **OQ1. Does the double-click launcher restart the Replicator?** The owner said "all agent
  sessions". Proposed: yes, last, because the owner is the requester; the Owner Terminal is never
  restarted.
- **OQ2. What does the launcher do when no coordinator has reported ready to restart?** Proposed:
  warn and ask again, then restart by resuming each session by its recorded uuid, and refuse only
  while a git operation is under way (D12). The alternative is to refuse until a restart-ready
  event exists, which would make the launcher useless when the coordinator itself has hung.
- **OQ3. Where the launcher's desktop file is installed.** Proposed: `~/.local/share/applications`
  and `~/Desktop` on Linux, the Windows desktop on Windows, written only by `install-launcher` when
  the owner runs it.
- **OQ4. Registering `sys-fleet` in this planning change** (D15). Proposed: yes, as planned, with
  `PLAN-054` as its only path until `rep-01`.
- **OQ5. Queue position.** The six phases stay out of `next_up` until the owner places them.
