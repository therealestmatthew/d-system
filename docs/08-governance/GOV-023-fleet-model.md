---
schema_version: 1
id: doc-fleet-model
code: GOV-023
title: Fleet model — agent definitions, roles, orchestration systems, typed relationships, lifecycle events and the authority rule
kind: governance
status: active
owner: repository-owner
created: '2026-10-13'
updated: '2026-10-13'
systems: [sys-fleet, sys-gov-docs]
depends_on: [doc-agent-replicator, doc-agent-replicator-requirements, doc-multi-session-coordination-protocol, doc-realization-role-contracts]
---

# Fleet model

This document defines how the repository describes its agents as data: what each agent is, where it
sits in an orchestration system, how agents relate to each other, which events change their state,
and who may start, stop or restart which agent. It delivers `REQ-039` R01 for idea `000693` (the
Agent Replicator), under [PLAN-054](../01-plans/PLAN-054-agent-replicator.md).

The data lives in tracked files under `docs/08-governance/fleet/`, each checked by a JSON Schema in
`schemas/`. No code names a particular session, role, system or governing document; the files supply
all of it. A new orchestration system is a new system file. The arrangement in `GOV-017` is one such
file, not a special case.

## What the files are

| File | Schema | Holds |
|---|---|---|
| `fleet/fleet.yaml` | `schemas/fleet.schema.json` | Host facts, the enabled systems, launch defaults, this document's path, and the fleet-level roles that belong to no one system |
| `fleet/definitions.yaml` | `schemas/fleet-definition.schema.json` | Every agent definition |
| `fleet/systems/<system-id>.yaml` | `schemas/fleet-system.schema.json` | One orchestration system: its roles, edges, resources, messages, lifecycle hooks and kill preconditions |

Runtime state is not tracked. It is one append-only event log, `_working/agents/events.jsonl`
(gitignored), folded into current state the way the idea log is folded (`PLAN-054` D4). The value
lists below that only the log uses — lifecycle events and the `holds` edge — are defined here so the
schemas and the log agree from the start.

Every value list in the sections below is also an enum in `schemas/fleet.schema.json`. A test fails
when the two disagree in either direction. Adding a value means changing both, in one reviewed
change.

## Agent definitions

A definition says how to start an agent. One definition can serve several roles: the eight
interactive sessions of `GOV-017` start the same way and share one definition.

| Field | Meaning |
|---|---|
| `id` | Unique key, referenced by roles |
| `kind` | One of the definition kinds below |
| `status` | `available`, or `planned` when the agent file it will point at does not exist yet |
| `model`, `effort` | Optional for a session; omitted means the Claude Code default. Never set on a subagent |
| `permission_mode` | One of the permission modes below. Required for a session or an owner-manual agent |
| `allowed_tools`, `disallowed_tools` | Tool rules passed at launch. Never set on a subagent |
| `agent_file` | For a subagent, the `.claude/agents/` file whose front matter supplies model, effort and tools. Required unless `status` is `planned` |
| `prompt_file` | Optional: a prompt the launch passes as the first message |
| `cwd` | Working directory, relative to the host's `repo_root` in `fleet.yaml` (`.` is the repository) |
| `remote_control` | Whether the session starts with Remote Control |
| `launcher` | One of the launchers below |
| `notes` | Free text |

A subagent definition reads model, effort and tools from its agent file and never copies them, so
the two cannot drift (`PLAN-054` D1).

### Definition kinds

| Kind | Meaning |
|---|---|
| `session` | An interactive top-level Claude Code session |
| `subagent` | An agent another agent dispatches; its lifecycle belongs to the dispatcher |
| `owner-manual` | A session the owner starts and stops by hand, in the manual permission mode |

### Permission modes

There is no bypass value, and the schema refuses one (`REQ-039` R05).

| Mode | Meaning |
|---|---|
| `auto` | The permission classifier decides each tool call |
| `manual` | The owner approves each tool call |
| `dontAsk` | Anything the allowed rules do not cover is refused without a prompt |
| `plan` | Read-only planning mode |

### Launchers

| Launcher | Meaning |
|---|---|
| `tab` | Opened in its own terminal tab on the host's desktop |
| `background` | Started without a terminal, for example `claude --bg` (`phase-rep-06` decides whether it is used) |

## Roles

A role is a position in one system. It names the definition it uses, or, for a role that belongs to
the whole fleet, the fleet-level role it stands for.

| Field | Meaning |
|---|---|
| `id` | Unique within its system |
| `definition` or `fleet_role` | Exactly one: the definition this role starts, or the fleet-level role it references |
| `group` | One of the role groups below |
| `cardinality` | `min` and `max` instances |
| `lifecycle` | Who controls its lifecycle, one of the values below |
| `session_names` | For a session role, the registered names its instances use |
| `governing_row` | The row label of this role in the system's roster table, when the system has one |
| `not_in_governing_table` | True while the governing document does not yet list the role |

### Role groups

| Group | Meaning |
|---|---|
| `meta` | Coordinates, captures or plans; claims no backlog phase |
| `execution` | Builds or reviews backlog work |
| `owner` | Run by the owner, for commands reserved to the owner |
| `support` | Serves another role on request, such as an advisor |

### Lifecycle control

| Value | Meaning |
|---|---|
| `replicator` | The Replicator starts, stops and restarts it, on an authorised request |
| `owner-only` | Only the owner starts or stops it. The Replicator refuses every request that names it |
| `parent` | The agent that dispatched it controls it; the Replicator never acts on it |

## Fleet-level roles

`fleet.yaml` lists roles that serve every system: today the Replicator and the Owner Terminal, both
`owner-only` (`REQ-039` R13). A system whose governing roster lists one of them has a role with
`fleet_role` set, so the roster test can match the row without a second definition.

## Orchestration systems

A system file states:

- `roles` and `edges` between them;
- `resources` the system serialises, each with a kind and the role that grants it;
- `messages` the system's agents exchange;
- `hooks`: the role that winds the others down, the message that says it is ready to restart, the
  role that receives the kickoff and its template, and whether a restart resumes or starts new;
- `governing_documents`, and optionally a `roster` naming the document and section whose table lists
  the system's roles;
- `kill_preconditions`, chosen from the predicates below.

### Resource kinds

| Kind | Meaning |
|---|---|
| `lock` | One holder at a time, such as the primary-checkout lock |
| `slot-pool` | Up to a stated capacity of holders, such as claim slots |

## Relationships

An edge is typed and directed. A static edge links two roles in a system file. A runtime edge links
two instances, or an instance and a resource, in the event log.

### Edge types

| Type | Meaning |
|---|---|
| `coordinates` | The source directs the target's work |
| `delegates-to` | The source dispatches work to the target and receives the result |
| `reviews` | The source reviews the target's output |
| `hands-off-to` | The source's output is the target's input in a fixed sequence |
| `messages` | The source sends the target messages of the system's declared types |
| `shares-resource` | The two use one declared resource and must take turns |
| `holds` | Runtime only: an instance holds a declared resource. Opened by `FLEET hold`, closed by `FLEET release` |
| `approves` | The source approves the target's work before it proceeds |
| `launches` | The source may ask for, or carry out, the target's launch |
| `kills` | The source may ask for, or carry out, the target's stop |
| `restarts` | The source may ask for, or carry out, the target's restart |

`launches`, `kills` and `restarts` carry an authority: `request` (may ask the Replicator) or
`execute` (carries it out). Other attributes on any edge are `cardinality`, `max_cycles` and
`required`. A static edge may not be `holds`.

### Authority values

| Value | Meaning |
|---|---|
| `request` | The source may ask for the action; the Replicator decides under the authority rule |
| `execute` | The source carries out the action itself |

## Lifecycle events

Each event in the log names an instance and one of these values.

| Event | Meaning |
|---|---|
| `defined` | A definition was added to the fleet |
| `registered` | An instance was recorded in a role before launch |
| `launched` | The instance was started; the event carries its uuid and is written before the process starts |
| `acked` | The instance confirmed its role |
| `busy` | The instance reported work under way |
| `idle` | The instance reported no work under way |
| `safe` | The instance reported it can be stopped without loss |
| `wind-down-requested` | The wind-down role asked the instance to reach a safe point |
| `restart-ready` | The wind-down role reported the system ready to restart |
| `killed` | The instance was stopped; the event carries the reason |
| `respawned` | The instance was started again under the same role |
| `failed` | A launch or stop did not happen; the event carries the reason |
| `orphan-detected` | A recorded instance has no matching process, or a process has no record |
| `retired` | The instance or role was taken out of use |
| `deregistered` | The instance's record was closed |

## The authority rule

A lifecycle request is `FLEET <verb> <system> <target> [args]`. The verbs are `launch`, `kill`,
`restart`, `status`, `register`, `hold` and `release`. The core (`tools/fleet.py`, `phase-rep-02`)
decides each request this way (`PLAN-054` D6):

1. Identify the requester: sender's registered name, to its instance, to its role. An unknown sender
   is refused and logged.
2. The owner passes straight to step 4. Anyone else needs an edge from their role to the target's
   role whose type matches the verb, with authority `request`. The Replicator carries out a request
   only for a target whose role's lifecycle is `replicator`; an `owner-only` or `parent` target is
   refused.
3. For a kill, every kill precondition the system file lists must hold.
4. Execute. In the Replicator this is a tool call the owner approves, in the manual permission mode.
   The approval prompt shows the requester and the matched edge.
5. Log the outcome and reply `FLEET-DONE`, or `FLEET-REFUSED` with the reason.

`hold` and `release` start and stop nothing. They are accepted only from the role the system file
names as the resource's granter, or from the owner, and skip steps 3 and 4.

Identity is the registered name, which `/rename` can change. The owner's approval of each Replicator
tool call is the safeguard (owner ruling, 2026-10-12).

## Predicates

Kill preconditions are chosen from this fixed list. A system file composes them; it cannot define
new ones. A system file that names any other value fails validation (`REQ-039` R12).

| Predicate | Holds when |
|---|---|
| `lock_free` | No git operation is under way in the primary checkout or any worktree the system's roles use: no `index.lock`, no rebase or merge directory |
| `target_safe` | The target's last lifecycle event is `safe` and nothing later supersedes it |
| `target_idle` | The target's last lifecycle event is `idle` |
| `coordinator_restart_ready` | The system's wind-down role has logged its restart-ready message after the system's last launch |
| `resource_free` | No `holds` edge is open on any resource the system declares |

`resource_free` departs from the Advisor's four-predicate list in A2. `lock_free` sees only git's
own state, so it cannot see a lock that has been granted but not yet used; the `holds` edges can.

## On-the-fly agents

The Replicator may start an agent that is not tracked yet, from a gitignored overlay under
`_working/agents/overlay/` (`PLAN-054` D11). An overlay definition names the tracked definition it
extends. It may narrow that definition and may not widen it: no wider permission mode, no added
allowed tool, no removed denied tool. Permission modes order from narrowest to widest as `plan`,
`dontAsk`, `manual`, `auto`. Keeping an overlay agent means copying its definition into
`definitions.yaml` in a reviewed change. The checks are built in `phase-rep-02`.

## What this document is not

- It does not change how any system runs. `GOV-017`, `GOV-014` and `PLAN-021` still govern their
  systems; the system files describe them.
- It does not authenticate requesters. See *The authority rule*.
- It does not manage subagents. A `parent` role is described, never started or stopped by the
  Replicator.
