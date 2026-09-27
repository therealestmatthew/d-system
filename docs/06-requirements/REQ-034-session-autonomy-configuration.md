---
schema_version: 1
id: doc-session-autonomy-configuration-requirements
code: REQ-034
title: Session autonomy configuration requirements — configurable axes, named presets, a mobile flag, and one referenced file that states what is in force
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-27'
updated: '2026-09-27'
systems: [sys-governance, sys-backlog]
depends_on: [doc-multi-session-coordination-protocol, doc-prompt-session-manager-starter-messages, doc-realization-role-contracts, doc-backlog-decisions]
---

# Session autonomy configuration requirements

Observable statements for ideas `000466` (make the sessions' level of autonomy configurable through
a referenced autonomy configuration file) and `000469` (a session configuration for when the owner
works from a mobile device with no terminal access, extending `000466`). The plan that delivers them
is [PLAN-051](../01-plans/PLAN-051-session-autonomy-configuration.md).

## Observed problem and scope

Each failure is recorded in the repository or in a working file the owner ruled on:

1. **The default mode is written in one place, and every other mode is written by hand for each
   run.** `GOV-017` states one mode: the owner approves each claim assignment (*Claim slots*) and
   each merge (*The merge gate*, step 4). The overnight mode of 2026-09-23 was a separate file
   written that night (`_working/overnight-sprint/01-authority.md`: pre-approved claims, delegated
   merges under five conditions, a PARK list, two fix cycles, and a lapse "when the owner next
   speaks to any session"). The conditional grant used on 2026-09-25 and 2026-09-26 ("merge once
   rebased and fully green on the SM's re-run; anything else comes back to the owner") exists only
   as a line in `_working/session-manager/restart-2026-09-26.md` §4 and in board entries. The owner
   described the cost when recording `000466`: "rather than having to explain that every time, we
   would need to make it configurable, and then reference that user-agent autonomy configuration
   file."
2. **The starters cannot state a mode other than the default.** `PROMPT-037`'s shared contract,
   item 4, says "The owner approves every merge". A run under any other mode has to amend the text
   before sending it, and the change leaves no record except in the messages themselves.
3. **Nothing tells a session what it may ask of an owner who is away from the terminal.** On
   2026-09-26 a session asked the owner to run `! git -C /code/d-system push origin d3e2bb1:dev`
   after the permission classifier blocked the push (`000469`). A `!` command cannot be run from
   the Remote Control mobile client, so the request held up the work until the owner returned. The
   limit on question previews is known only from a memory entry ("No Content in Question
   Previews").
4. **Nothing records a decision taken under a delegated mode in one agreed place.** The overnight
   authority wrote PARK reasons to `morning-report.md`. A conditional grant is recorded only where
   the Session Manager happened to note it on the board.

## Observable requirements and verification

| ID | Required observable behaviour | Verification |
|---|---|---|
| R01 | A tracked governance document defines every autonomy axis, every value each axis can take and what that value lets a session do without asking, the named presets, the mobile behaviours with the mobile mapping, the order in which settings are applied, and the list of owner decisions that no setting delegates | Read the document. A test fails if the registry (R02) has an axis, value, preset or behaviour the document does not name, or the other way round |
| R02 | A tracked registry file states the same axes, values, defaults, presets, behaviours and mobile mapping in machine-readable form and passes a JSON Schema | A schema test: the registry passes; a fixture preset naming an undeclared axis fails; a fixture value outside its axis's declared values fails |
| R03 | The registry ships three presets that reproduce the modes already used: `attended` (`GOV-017` as it stands), `conditional` (the 2026-09-25/26 conditional grant) and `overnight` (`01-authority.md` of 2026-09-23). `attended` sets every axis to its default | Read the registry beside `GOV-017`, `restart-2026-09-26.md` §4 and `01-authority.md`: each axis value in each preset matches a quoted line in its source. The test asserts `attended` equals the axis defaults |
| R04 | Mobile is one boolean setting. Each mobile behaviour is its own setting with its own default, and the registry's mobile mapping sets one value for each behaviour. Setting mobile to true applies the whole mapping, and an explicit setting of a single behaviour still takes precedence over the mapping | Resolver tests: mobile true with no overrides gives the mapped value for every behaviour; mobile true with one behaviour overridden gives the override for that one and the mapped value for the rest; mobile false gives the defaults |
| R05 | A gitignored in-force file at one fixed path in the primary checkout names the preset, the mobile flag, any single-axis or single-behaviour overrides, the items a delegated setting covers (such as pre-approved phases), an expiry, and the path of the decision log. Changing the setting is one edit to that file, with no commit | `git check-ignore` reports the path ignored. Read the governance document for the file's fields |
| R06 | A resolver tool reads the registry and the in-force file, applies preset, then mobile mapping, then overrides, and prints every effective axis and behaviour value together with where each value came from. It exits non-zero, and prints the `attended` defaults as the settings to use, when the in-force file is missing, fails validation, or names an undeclared axis, value, preset or behaviour | Resolver tests, one per case: a valid file; each precedence layer; a missing file; an undeclared axis; an out-of-range value; an expired setting |
| R07 | A new axis, value, preset or mobile behaviour can be added by editing the registry and the governance document only, without changing the resolver's code | A resolver test loads a fixture registry that adds one new axis and one new behaviour and resolves both correctly, with the resolver unchanged |
| R08 | No setting delegates an owner-reserved decision. The governance document reproduces `GOV-014`'s owner-reserved list, and the schema has no axis that could grant one of those decisions to an agent | The document test checks that the list matches `GOV-014` word for word. Read the schema's axis list against it |
| R09 | `GOV-017` cites the governance document as the source of the setting in force and states how a session learns it: at kickoff, from the contract line the Session Manager fills from the resolver's output; mid-run, from a new `MODE` message sent to every session; and on lapse, from an `OWNER-BACK` message that a session sends to the Session Manager when the owner speaks to it while an `on-owner-contact` expiry is in force. `GOV-017` also states what governs a step already under way when `MODE` arrives, and what the Session Manager withholds from a session that has not acknowledged it | Read `GOV-017`: the citation, the kickoff step, the three new rows in the message table, and both failure rules |
| R10 | `PROMPT-037`'s kickoff runs the resolver before composing the starters, and its shared contract carries one line stating the effective setting with a pointer to the governance document. No starter text restates what a mode permits | Read `PROMPT-037`. `grep` for "The owner approves every merge" in `PROMPT-037` returns no line; the merge item points to the setting instead |
| R11 | Every decision a session takes under a setting that is not `attended` (a claim taken from a pre-approved list, a delegated or conditional merge, a PARK, a terminal-only action queued for the owner) is appended to the decision log the in-force file names. Each entry names the session, the item, the axis and value that authorised it, and the outcome | Read the governance document for the entry fields. In the wiring phase's dry run, one sample entry is written to a gitignored log and read back |
| R12 | `GOV-003` records the owner's ruling that makes the configuration standing, including how a delegated merge relates to the owner-reserved "integration into `dev`" | Read the entry |

## What each requirement is not

- **R03 does not create a new mode.** The three presets are the modes used between 2026-09-23 and
  2026-09-26. Any further preset is added later under R07, by the owner.
- **R04 does not change what any session does when the owner is at the terminal.** Behaviour
  defaults keep today's practice. Whether previews carry content when the owner is at the terminal
  is an open question in the plan.
- **R05 does not keep a history of settings.** The in-force file is gitignored by the owner's
  choice. The decision log (R11) and the board keep what was decided under a setting.
- **R06 does not enforce anything.** The resolver reports the effective setting. Sessions act on
  it under `GOV-017`, and nothing blocks a tool call.
- **R08 does not change the owner-reserved list.** It stops a setting from reaching the list.
- **R09 and R10 do not edit `AGENTS.md` or `CLAUDE.md`.** The reference sits in `GOV-017`, which
  already governs how several sessions work together.
- **None of this ports the mechanism to the idea-realization plugin.** The owner ruled "not now"
  on 2026-09-27. Ideation recorded the port as `000496`.
- **None of this covers the orchestrator of `ADR-023`.** If the orchestrator takes over the Session
  Manager's work, it reads the same files. That design belongs to the orchestrator's plan.

## Accepted decisions

The owner's answers of 2026-09-27, given in Session 1 - Builder A to the questions that set this
scope:

- **Storage.** The owner chose the split: the level definitions in a tracked governance document,
  and the setting in force, with that run's specifics, in a gitignored file in the primary checkout
  (R01, R05).
- **Levels.** "We need the individual axes to be configurable either way. I'm good with the three
  recommended presets you proposed and an initial set of pre-configurations of those axes, but the
  system needs to be extensible based on how granular we make it in the future." (R02, R03, R07)
- **Mobile.** "Mobile mode should really just be a boolean config (yes or no) that comes with a
  pre-configured set of behaviors that need to change when agents act under mobile supervision.
  Maybe each behavior is individually configurable as a baseline then we can configure the mobile
  flag to behavior mapping to toggle them all at once with the mobile flag while still having the
  ability to switch each behavior based on our preferences." A terminal-only action is queued for
  the owner's return rather than stopping the work (R04).
- **Plugin.** Not now (scope note above).
