---
schema_version: 1
id: doc-session-autonomy-configuration
code: PLAN-051
title: Session autonomy configuration — a governance document and registry of axes and presets, a mobile flag, a resolver, and the GOV-017 wiring
kind: plan
status: draft
owner: repository-owner
created: '2026-09-27'
updated: '2026-09-27'
systems: [sys-governance, sys-backlog]
depends_on: [doc-session-autonomy-configuration-requirements, doc-multi-session-coordination-protocol, doc-prompt-session-manager-starter-messages, doc-realization-role-contracts, doc-backlog-decisions]
---

# Session autonomy configuration

Delivers [REQ-034](../06-requirements/REQ-034-session-autonomy-configuration.md), for ideas `000466`
(make the sessions' level of autonomy configurable through a referenced autonomy configuration file)
and `000469` (a session configuration for when the owner works from a mobile device with no terminal
access).

**Status: draft.** Written 2026-09-27 by Session 1 - Builder A on an owner-directed assignment
relayed by the Session Manager, running unclaimed (no backlog phase). It was reviewed under
`GOV-018` at the plan and phase altitudes. The review record is `2026-09-27-plan-051`, with eight
findings, all `fixed` and none escalated. It awaits G3.

## Context and scope

`REQ-034`'s problem section lists four failures. In short: `GOV-017` states only the owner-in-the-loop
mode, so the overnight mode and the conditional grant were written out by hand for each run; the
starters cannot state any other mode without being edited; nothing tells a session what it may ask
of an owner who is on the mobile client; and decisions taken under a delegated mode have no agreed
record.

The modes this plan turns into configuration are the ones already used:

| Mode | Source | What it let sessions do without asking |
|---|---|---|
| Owner in the loop | `GOV-017`, *Claim slots* and *The merge gate* | Nothing beyond `GOV-017`: the owner approves each assignment and each merge |
| Conditional grant | `_working/session-manager/restart-2026-09-26.md` §4 | The Session Manager grants a merge "once rebased and fully green on the SM's re-run; anything else comes back to the owner". A code change made after the review counts as "anything else" |
| Overnight | `_working/overnight-sprint/01-authority.md` (2026-09-23) | Claims from a listed set count as owner-approved; the Session Manager grants merges for those items under five conditions; an item that needs the owner is parked; at most two fix cycles; everything lapses when the owner next speaks to any session |

Both `_working/` files are gitignored. This plan is the first tracked record of what they permitted.

The owner's answers of 2026-09-27 set the design. They are quoted in `REQ-034`, *Accepted
decisions*: the split between a tracked definition and a gitignored setting; configurable axes with
three presets and room to add more; mobile as one boolean with per-behaviour settings and a mapping;
and no port to the plugin for now.

## Decisions

**D1. Definitions are tracked; the setting in force is a gitignored file in the primary checkout.**
The owner chose this split. The definitions are the rule, so they belong in a governed document with
history. The setting in force changes from one night to the next and carries run-specific lists,
such as the phases pre-approved for a night, which is how `01-authority.md` was used. Its path is
`_working/session-manager/autonomy.yaml`. Every session can read it at that path, as sessions
already read `_working/session-manager/` files there, and the Session Manager may write under that
directory without a turn (`GOV-017`, *Departures*, item 2). Two alternatives were rejected. A
tracked in-force file would need a primary-checkout turn for each change of level, and the owner
would have to wait for one before going to sleep. A section in `GOV-017` alone would leave the mode
to be stated for each run, which is the problem `000466` records.

**D2. The configuration is a set of axes. A preset is a named set of axis values, and settings are
applied in three layers.** The owner asked for "the individual axes to be configurable either way"
together with presets. The resolver applies the chosen preset first, then the mobile mapping when
mobile is true, then any single-axis or single-behaviour override in the in-force file. The last
layer wins, which gives the owner's "ability to switch each behavior based on our preferences". Two
alternatives were rejected. Presets alone would make every variation a new preset. Axes alone would
mean filling in every axis each time, and the owner accepted presets.

**D3. The initial axes and values are the ones the three modes used, and no others.**

| Axis | Values (default first) | Source of each non-default value |
|---|---|---|
| `claim_approval` | `owner-each`, `pre-approved-list` | `01-authority.md` §1 |
| `merge_approval` | `owner-each`, `conditional-green`, `delegated` | `restart-2026-09-26.md` §4; `01-authority.md` §2 |
| `decision_points` | `ask`, `park` | `01-authority.md` §3 |
| `fix_cycles` | none, or a whole number | `01-authority.md` §2 ("at most 2 per phase") |
| `expiry` | `none`, `on-owner-contact` | `01-authority.md` header |

The presets are `attended` (every default), `conditional` (`merge_approval: conditional-green`) and
`overnight` (`pre-approved-list`, `delegated`, `park`, `fix_cycles: 2`, `on-owner-contact`). The
governance document defines each value exactly as its source does. For example, `delegated` carries
`01-authority.md`'s five merge conditions, and `conditional-green` carries the rule that a change made
after the review goes back to the owner. `pre-approved-list` and `delegated` apply only to the items
the in-force file lists (D5). An axis for "decide and log" was proposed in `000466` but was never
used, so it is not in the initial set. The owner can add it later under D4.

**D4. The registry is YAML with a JSON Schema, kept in agreement with the governance document by a
test.** The registry is `docs/08-governance/autonomy.yaml`, and its schema is
`schemas/autonomy.schema.json`. The schema describes axes, values, presets, behaviours and the mobile
mapping in general terms, so the owner can add any of them by editing the registry and the document,
with no change to code (`REQ-034` R07). A test fails when the document and the registry name
different axes, values, presets or behaviours. Two alternatives were rejected. With the prose
document alone, the resolver would have to parse Markdown. With the YAML alone, nothing would
explain what a value lets a session do, and rules in this repository live in governed documents.

**D5. The in-force file names a preset, the mobile flag, overrides, the covered items, what is
excluded, an expiry, and a decision-log path.** The covered items are, for example, the phases
pre-approved for a night and the fixes branches `01-authority.md` §1 listed. The exclusions are
free-text items that a delegated setting never covers, such as `01-authority.md` §4's run-specific
"Wire the broker hook". The Session Manager repeats them in the contract line. The rejected
alternative was a preset with no run-specific fields, where a delegated setting would cover every
phase and branch. That would widen `01-authority.md`'s practice: it named six phases and two branches
and said "Nothing else may be claimed", and the owner would lose that limit.

**D6. A resolver tool computes the effective setting and falls back to `attended`.** The tool is
`tools/autonomy.py`. It prints each axis and behaviour value with its source layer, and one contract
line for the Session Manager to paste. When the file is missing, fails validation, names anything the
registry does not declare, or has expired, the tool exits non-zero and prints the `attended`
defaults. The Session Manager then works under `attended` and tells the owner why. Two alternatives
were rejected. Sessions applying the three layers themselves would each be one more place where the
wrong layer could win. Falling back to the last good setting, or to the most permissive one, would
let an unreadable file grant authority. The tool ships with its own `OPS-*` document, as `AGENTS.md`
requires.

**D7. Mobile is one boolean. Each behaviour has its own default, and the mapping sets them all
at once.** The owner ruled this. The initial behaviours come from `000469` and the memory entry on
question previews:

| Behaviour | Values (default first) | Mobile mapping |
|---|---|---|
| `bang_commands` | `allowed`, `never` | `never` |
| `question_previews` | `content`, `text-only` (default is open question OQ1) | `text-only` |
| `terminal_only_actions` | `ask-now`, `queue-for-return` | `queue-for-return` |

A queued terminal-only action is written to the decision log and to the board, and the work carries
on, as the owner chose. A push blocked by the permission classifier, which is the case in `000469`,
is a terminal-only action, so the "pushes deferred" example is covered without a separate behaviour.
Two alternatives were rejected. A fixed mobile preset, with no behaviour settable on its own,
would stop the owner switching "each behavior based on our preferences". A mobile variant of
each preset would double the presets and duplicate the mapping in each one.

**D8. No setting delegates an owner-reserved decision. A delegated merge is the owner's approval,
given in advance.** `GOV-014` reserves "integration into `dev`" to the owner permanently. Under
`delegated` or `conditional-green`, the owner has approved in advance each merge that meets the
stated conditions, for the items listed. The Session Manager checks the conditions; it does not
decide the merge. `GOV-017` already treats a relayed `GRANTED merge` as the owner's approval
(*Departures*, item 4). This extends that approval to one given before the `READY` arrives. The
reading is not the same as the one `GOV-014` states, so `GOV-003` records it only as the owner's
ruling at G3 (OQ2). The document reproduces the owner-reserved list, and the schema has no axis
that reaches it. Two alternatives were rejected. Leaving out delegated merges would drop the mode
that `01-authority.md` ran on 2026-09-23 and that the owner asked to configure. Treating a
delegated merge as the Session Manager's own decision would move an owner-reserved item to an
agent.

**D9. Sessions learn the setting at kickoff, through `MODE` when it changes mid-run, and
`OWNER-BACK` ends an `on-owner-contact` expiry.** At kickoff the Session Manager runs the resolver
and puts its contract line in the shared contract as a new item. When the owner changes the
setting, the Session Manager sends `MODE <contract line>` to every session. Each session replies
`ACK <session> MODE`, and the ACKs go on the board. When the owner speaks to a session while an
`on-owner-contact` expiry is in force, that session sends `OWNER-BACK` to the Session Manager. The
Session Manager then sets the in-force file to `attended`, keeps the mobile flag as it was, and
sends `MODE`.

Failure paths. A step already under way when `MODE` arrives finishes under the setting it started
under, and the session's next step uses the new one. A merge turn counts as one step from
`GRANTED merge` to `TURN DONE`. Until a session has sent `ACK <session> MODE`, the Session Manager
grants it no turn, assignment or merge, and when a grant is waiting on that session it tells the
owner. If the owner speaks to the Session Manager itself under an `on-owner-contact` expiry, that
counts as `OWNER-BACK`. If the owner speaks to a session that does not send `OWNER-BACK`, the
setting stays in force until the owner's next message to the Session Manager. `GOV-017` records
that gap.

The rejected alternative was for each session to re-read the file before every
decision. A change would then arrive with no acknowledgement, and a session partway through a step
could act on either version.

**D10. The reference goes in `GOV-017`, not in `AGENTS.md`.** `000466` offered both. `GOV-017`
governs how several sessions work together, and every mode above applies only while sessions run
under it. `AGENTS.md` cannot change without the owner's approval of that specific edit, and this plan
does not need it.

**D11. Every decision taken under a setting other than `attended` goes to one decision log.** The
in-force file names the log's path. It defaults to `_working/session-manager/decisions.md`, beside
the board, which the owner reads on return. `01-authority.md`'s `morning-report.md` shows the need.
An entry names the time, the session, the item, the axis and value that authorised it, and the
outcome. Two alternatives were rejected. Keeping decisions on the board would mix them with lock
and slot events, so the owner would have to read the whole board on return. Writing them to each
session's own record would split one night's decisions across several files, and a parked item
has no session record yet.

## Implementation phases

| Phase | What | Requirements | Depends on |
|---|---|---|---|
| `phase-mode-01` | The governance document (axes, values, presets, behaviours, mobile mapping, precedence, in-force file fields, decision log, owner-reserved list), the registry `docs/08-governance/autonomy.yaml`, `schemas/autonomy.schema.json`, and a test that checks the registry against the schema and the document against the registry | R01, R02, R03, R04 (definition), R05 (fields), R08, R11 (fields) | none |
| `phase-mode-02` | `tools/autonomy.py`, its `OPS-*` document, and resolver tests, with fixtures for each precedence layer, each failure case and a registry extended by one axis and one behaviour | R04 (resolution), R06, R07 | `phase-mode-01` |
| `phase-mode-03` | The wiring: `GOV-017` (citation, kickoff step, a departure entry, `MODE`, `ACK … MODE` and `OWNER-BACK`); `PROMPT-037` (the kickoff runs the resolver; a contract item carries the line; item 4 stops restating the merge mode); the `GOV-003` entry recording the owner's G3 ruling; a dry run that resolves a sample in-force file into the contract line and writes one decision-log entry | R09, R10, R11 (dry run), R12 | `phase-mode-02` |

## Requirement coverage

| Requirement | Phase | Acceptance evidence |
|---|---|---|
| R01 | `phase-mode-01` | The document, and the agreement test failing on a fixture registry with an extra axis |
| R02 | `phase-mode-01` | Schema test: the registry passes; the undeclared-axis and out-of-range fixtures fail |
| R03 | `phase-mode-01` | Each preset value quoted beside its source line in the document; the test that `attended` equals the defaults |
| R04 | `phase-mode-01` (definition), `phase-mode-02` (resolution) | The document's mobile section; the three mobile resolver tests |
| R05 | `phase-mode-01` | The document's in-force section; `git check-ignore _working/session-manager/autonomy.yaml` |
| R06 | `phase-mode-02` | The six resolver fixtures |
| R07 | `phase-mode-02` | The extended-registry fixture resolves with the resolver unchanged |
| R08 | `phase-mode-01` | The document test comparing the list with `GOV-014` |
| R09 | `phase-mode-03` | The `GOV-017` passages and message-table rows |
| R10 | `phase-mode-03` | The `PROMPT-037` kickoff and contract text; the `grep` returning nothing |
| R11 | `phase-mode-01` (fields), `phase-mode-03` (dry run) | The document's decision-log section; the sample entry read back |
| R12 | `phase-mode-03` | The `GOV-003` entry |

Every requirement maps to a phase, and every phase has a row.

## Execution order and real concurrency

- The phases run in order: `phase-mode-02` reads the registry and schema from `phase-mode-01`, and
  `phase-mode-03` cites the resolver and its contract line.
- `phase-mode-01` and `phase-mode-02` each declare `docs/08-governance/` for a new document, so each
  collides with any active phase that declares that directory: today `phase-asr-02`, `phase-asr-03`,
  `phase-asr-04` and the `phase-grd-*` and `phase-dam-01` phases that edit documents there.
- `phase-mode-03` edits `GOV-017` and `PROMPT-037`, which `phase-grd-02`, `phase-grd-03` and
  `phase-asr-04` also edit. `phase-grd-02` has been active since 2026-09-27 (claimed for
  `agent-builder-b` at `270e688`) and changes `GOV-017`'s primary-checkout lock section and
  `PROMPT-037`'s contract item 1. The phases do not depend on each other. Declaring the same files means they cannot be
  active at the same time, and whichever runs second rebases onto the other's text.
- No phase goes into `next_up` without the owner's word (OQ4).

## Out of scope

- **Porting the mechanism to the idea-realization plugin** (`plugins/idea-realization/docs/multi-session.md`
  and `session-manager-messages.md`). The owner ruled "not now" on 2026-09-27. Ideation recorded
  it as `000496` (port the session autonomy configuration to the plugin), which extends `000466`.
- **Enforcing the setting at the tool boundary.** The resolver reports; sessions comply under
  `GOV-017`. Enforcement at the tool boundary is the broker's job (`phase-auto-*`, `PLAN-032`).
- **The orchestrator of `ADR-023`.** It would read the same files if it takes over the Session
  Manager's work.
- **Any edit to `AGENTS.md` or `CLAUDE.md`** (D10).
- **New modes.** Only the three used ones ship (D3). Further presets and axes are added later
  under D4.

## Open questions

- **OQ1. The default for `question_previews` at the terminal.** The memory entry "No Content in
  Question Previews" puts drafts in message text in every session today, not only on mobile. A
  default of `text-only` keeps that. A default of `content` restores previews when the owner is at
  the terminal, with the mobile mapping switching them off. Proposed: `text-only`, which keeps
  today's practice.
- **OQ2. The `GOV-003` wording for a delegated merge** (D8). Proposed: "A merge the Session
  Manager grants under `conditional-green` or `delegated`, for an item the in-force file lists and
  with every stated condition met, is the owner's approval given in advance. The owner-reserved list
  in `GOV-014` is unchanged."
- **OQ3. Whether the setting applies to a session outside `GOV-017`**, for example a lone session
  or the owner's own `/session-close`. Proposed: no. The setting applies only while sessions run
  under `GOV-017` (D10).
- **OQ4. Queue position.** The three phases stay out of `next_up` until the owner places them.
