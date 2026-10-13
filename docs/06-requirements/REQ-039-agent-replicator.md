---
schema_version: 1
id: doc-agent-replicator-requirements
code: REQ-039
title: Agent Replicator requirements — fleet tracker files, a generalized orchestration model, one Python core with bash and PowerShell shells, and a double-click restart of every agent session
kind: requirement
status: draft
owner: repository-owner
created: '2026-10-12'
updated: '2026-10-12'
systems: [sys-fleet, sys-governance, sys-gov-docs, sys-backlog]
depends_on: [doc-multi-session-coordination-protocol, doc-prompt-session-manager-starter-messages, doc-realization-role-contracts, doc-live-demo, doc-adr-session-manager-into-orchestrator, doc-backlog-decisions]
---

# Agent Replicator requirements

Observable statements for idea `000693` (the Agent Replicator: a session that launches, kills
and restarts the other agent sessions, driven by tracked fleet files). The plan that delivers them
is [PLAN-054](../01-plans/PLAN-054-agent-replicator.md). Related ideas, read for context and not
promoted by this work: `000515` (a bash script that reopens every planning session after a
restart), `000514` (a catalog of repeatable automation commands), `000389` (session state and
resumability) and `000540` (the multi-session orchestration ships with the engine).

## Observed problem and scope

1. **Opening and restarting sessions depends on two gitignored scripts.**
   `_working/session-manager/relaunch-sessions.sh` and `open-advisor.sh` open each session in a
   terminal tab. They read a gitignored roster (`sessions.json`) whose own note says "The tracked
   version moves to bash/config/sessions.json and mirrors GOV-017's session table". Nothing checks
   that the roster agrees with `GOV-017`, and the Advisor's launch settings exist only inside
   `open-advisor.sh`.
2. **Session ids are recovered after the fact.** `relaunch-sessions.sh --record-ids` finds each
   session's id by searching transcripts for the newest title that matches the name. A resumed
   restart uses whatever that search found.
3. **Nothing kills a session safely.** `relaunch-sessions.sh` uses `pgrep` on the name only to
   refuse a duplicate. No tool stops a session, and the only way to stop one is to close its tab
   or match a process by name.
4. **The rules for who may start, stop or restart which session are written only for one
   arrangement.** `GOV-017` describes the Session Manager arrangement in prose. The live-demo
   build (`PLAN-021`, orchestrators that dispatch creators and validators) and the
   idea-realization roles (`GOV-014`) are arranged differently, and nothing describes any of the
   three as data a tool can read.
5. **There is no Windows path.** Both scripts need `gnome-terminal` and a Linux desktop.
6. **Restarting every agent session takes several steps at a terminal.** The owner asked for "a
   simple script I can double click to run and reboot the system", and clarified that it
   restarts all agent sessions while the computer stays up.

## Observable requirements and verification

| ID | Required observable behaviour | Verification |
|---|---|---|
| R01 | A tracked governance document defines the fleet model: agent definitions, roles, orchestration systems, agent instances, typed relationships (edges), lifecycle events, the authority rule, the fixed predicate vocabulary, and the definitions that only the owner starts or stops | Read the document. A test fails if a schema enum (edge type, lifecycle event, predicate, permission mode) names a value the document does not, or the other way round |
| R02 | Tracked fleet files under `docs/08-governance/fleet/` describe the fleet: `fleet.yaml` (host facts, enabled systems, defaults), `definitions.yaml` (agent definitions) and one `systems/<system-id>.yaml` per orchestration system. Each passes its JSON Schema in `schemas/` | Schema tests: every tracked file passes; one invalid fixture per schema fails |
| R03 | Three systems are described from the start: the multi-session arrangement of `GOV-017`, the live-demo build of `PLAN-021`, and the idea-realization roles of `GOV-014` | Read the three system files. The integrity test (R04) loads all three |
| R04 | Every reference in the fleet files resolves: each role names a declared definition, each edge names declared roles, each system named in `fleet.yaml` has a file, and a subagent definition names a `.claude/agents/` file that exists. A system file that names a roster table in its governing document matches that table row for row | The integrity test, with one fixture per broken reference. For the `GOV-017` system, a test compares its roles with the *The sessions* table |
| R05 | No definition can run with a permission mode wider than the tracked fleet allows. The schema's permission-mode values exclude any bypass mode, and an on-the-fly definition in the gitignored overlay must extend a tracked definition and may not widen its permission mode or its allowed tools | Schema test: a fixture with a bypass mode fails. Overlay tests: an overlay that widens the mode or adds a tool fails; one that narrows passes |
| R06 | The tool code names no particular session, role, system or governing document. Adding a fourth orchestration system means adding one system file and editing no code | A test loads a fixture fourth system with its own roles, edges and kill preconditions, and the core resolves authority and derives launch commands for it unchanged. A `grep` of `tools/fleet.py` and the shells for "Session Manager" and "GOV-017" returns nothing |
| R07 | One Python core, `tools/fleet.py`, folds the event log, decides authority, derives each launch command from the fleet files, prints a dry run, reports status, and writes a generated fleet map. The bash and PowerShell shells only open terminals, start and signal processes, and write pidfiles | Read the shells: each calls the core for every decision. Core tests cover each listed function |
| R08 | Runtime state is one append-only event log, `_working/agents/events.jsonl` (gitignored), holding instance events and relationship events. Current state (each instance's uuid, pid, status) is derived by folding it | `git check-ignore` reports the path ignored. A fold test builds state from a fixture log, including a kill and a respawn |
| R09 | Each launch pre-assigns a fresh session id (`--session-id <uuid>`) and records it in the event log before the process starts. No transcript search is used to find a session's id | Read the core's launch path. Dry-run output shows the uuid in the command and the matching `launched` event |
| R10 | A kill stops only the process that the event log recorded for that instance, after checking that the process's command line contains the instance's uuid. Nothing kills by process name. A second, forced kill needs its own owner approval | Shell tests against a dummy process: a matching uuid is stopped, a pid whose command line lacks the uuid is refused. `grep` for `pkill` and `killall` in the shells returns nothing |
| R11 | A lifecycle request (`FLEET <verb> <system> <target>`) is carried out only when the requester is the owner, or when the requester's role has an edge of that verb's type to the target's role with authority to request it, and every kill precondition the system file lists holds. Otherwise the core refuses, logs the refusal, and says why | Authority tests: one per edge type that grants, one where no edge exists, one per predicate that fails, one unknown requester |
| R12 | Kill preconditions are composed in each system file from a fixed vocabulary implemented in the core: `lock_free`, `target_safe`, `target_idle`, `coordinator_restart_ready`. A system file that names any other predicate fails validation | Schema test with an unknown predicate. One core test per predicate, true and false |
| R13 | The Owner Terminal and the Replicator are started and stopped only by the owner. No request from an agent can launch, kill or restart either | Authority tests: a request naming either target from any non-owner role is refused |
| R14 | The Linux shell opens each session in its own terminal tab, records the pid and process group, and refuses to open a second instance of a name that the folded state shows running | Live self-test (R19). A dry run against a fixture state with a running instance prints the refusal |
| R15 | A PowerShell shell provides the same operations on Windows (Windows Terminal tabs, process lookup by command line, tree kill), with every behaviour that cannot be checked without a Windows host listed in the operations document | `pwsh` parses every `.ps1` file. A `windows-latest` CI job runs the core's dry run through the PowerShell shell and passes. Read the operations document's unverified list |
| R16 | `.gitattributes` keeps shell scripts at LF line endings, and `.cmd` launchers at CRLF | `git check-attr eol` on one file of each kind |
| R17 | A double-click launcher restarts every agent session in the enabled systems and leaves the Owner Terminal alone. On Linux it is a `.desktop` file that runs a `.sh` script; on Windows a `.cmd` file or a shortcut that runs a `.ps1` script. Before stopping anything it shows which sessions it will restart and asks the owner to confirm, and it states whether a coordinator has reported ready to restart | Linux: run the `.sh` with its dry-run flag and read the list. Windows: the CI dry run (R15). The live run in R20 |
| R18 | A gitignored overlay (`_working/agents/overlay/`) lets the Replicator start an agent that is not yet tracked, under R05's limits. Promoting an overlay definition means copying it into `definitions.yaml` | Overlay tests (R05). Read the operations document's promotion steps |
| R19 | Before the fleet is wired into a live arrangement, a self-test system with one throwaway session is launched, listed, killed and relaunched on this machine. The run settles three open questions: whether `--name` sets the name `ListAgents` shows, whether `--session-id` accepts a fresh uuid for an interactive session, and whether a `claude` launch and a kill from `Bash` are blocked by the permission classifier | The session record of the shell phase quotes the output of each step and the answer to each question |
| R20 | `GOV-017` names the Replicator as a session and states its messages, and one live restart of every agent session at a wind-down the owner schedules goes through the Replicator | Read `GOV-017`'s session table and message table. The wiring phase's session record shows the restart: the coordinator's ready message, each kill and launch event, and the roster afterwards |
| R21 | The Replicator runs in the manual permission mode, so the owner approves each tool call it makes, and its approval prompt shows the requester and the edge that authorised the request | Read the Replicator's definition. The live restart's record quotes one approval prompt |

## What each requirement is not

- **R03 does not change how the demo build or idea-realization run.** Their roles are subagents
  whose lifecycle belongs to the parent that dispatched them. The files describe them; the
  Replicator starts and stops none of them.
- **R06 does not forbid the GOV-017 system file from naming GOV-017.** A system file names its
  governing document; the code does not.
- **R11 does not authenticate the requester.** Identity is the registered session name, which a
  `/rename` can change. The owner's approval of each Replicator tool call (R21) is the safeguard,
  as ruled on 2026-10-12.
- **R15 does not claim the Windows shell works.** It claims the shell parses, the dry run passes
  in CI, and every unchecked behaviour is listed.
- **R17 does not restart the computer.** It restarts the agent sessions only.
- **None of this edits `AGENTS.md` or `CLAUDE.md`.** The tracked data sits under
  `docs/08-governance/fleet/`, beside other governance data, which needs no orientation row.
- **None of this deletes the two gitignored scripts.** They live under `_working/`, which nothing
  deletes without the owner's approval. Once the shells work, the plan proposes their removal to
  the owner.
- **None of this moves the orchestration into the plugin** (`000540`) or the `ADR-023`
  orchestrator. Either would read the same files.

## Accepted decisions

The owner's rulings of 2026-10-12, given in the Session Manager's session on the Advisor's answers
A1 (the Replicator) and A2 (the fleet model):

- **Shape.** A meta session plus tracked fleet files and scripts; terminal tabs and Remote Control
  now, a `claude --bg` spike later; a new plan, requirement and `phase-rep-*` track; scripts under
  `tools/` with an `OPS` document.
- **Generalization.** "don't design it specific to this SM format. It should be generalizable to
  understanding orchestration systems in general so as the system evolves, it dynamically adapts
  based on its generalized understanding - not linked to one specific agent orchestration system
  design." (R06, R11, R12)
- **Tracker files.** "Be sure we design the system of tracker files needed for managing the growing
  agent fleets, including how we map relationships between individual agents to form orchestration
  systems." (R01 to R04, R08)
- **PowerShell now.** "We should draft windows Powershell now despite my earlier saying not to."
  With a `windows-latest` CI dry-run job (R15, R16).
- **Core and data.** One Python core with thin bash and `.ps1` shells; tracked data under
  `docs/08-governance/fleet/`; all three systems in the first phase; one event log (R02, R03, R07,
  R08).
- **Authority.** Requester identity by registered name with the owner's approval of each call;
  predicates fixed in code and composed by systems; the Replicator manages the Advisor; the Owner
  Terminal and the Replicator are owner-only; a coordinator session is killed only on its hand-off
  or the owner's instruction (R11 to R13).
- **On-the-fly agents.** A gitignored overlay, promoted when kept (R18).
- **Session ids.** Pre-assigned with `--session-id` (R09).
- **Replicator mode.** Manual (R21).
- **Restart launcher.** "I also will need a simple script I can double click to run and reboot the
  system", clarified as restarting all agent sessions while the computer stays up (R17).
- **Acceptance.** One live restart of all sessions at an owner-scheduled wind-down (R20).
