"""The capability and approval broker (`000031`, `phase-auto-02`, `ADR-022`).

This package is the tool-boundary enforcement mechanism ADR-022 ordered ahead of the trigger
gateway, run ledger and worker (`phase-auto-03` through `phase-auto-05`). It ships as an
enforcement point with a permissive default, not a full capability policy:

- `enforcement.check()` decides whether a named capability may proceed and writes an audit
  record for every call it sees, allowed or denied. With no denial configured, every capability
  is allowed (REQ-017 R01, R03). A capability named in the caller-supplied denial set is refused
  before it runs, independent of any prompt text.
- `approvals.py` is the approval-request surface scope bullets 3 and 4 ask for: a record
  carrying scope, reason, expiry and a decision, an append-only store making the decision
  immutable once recorded, and expiry enforced before a decision is honoured.
- `__main__.py` is the CLI surface (`python -m src.broker`): `check` for the tool-boundary call,
  and `request` / `list-pending` / `decide` for the approval surface.

REQ-017 R02 (every run carries a named capability set, not a role) and R04 (a full approval
schema and policy behind the four fields) are recorded open per ADR-022, not satisfied by this
package. `denied` in `enforcement.check()` is whatever the caller configures per call; this
package owns no built-in taxonomy of capabilities or roles.

Nothing in this repository invokes this package automatically yet. No hook, no CI step and no
other module calls `src.broker` today.

**The intended wiring — not built here, and explicitly out of this phase's deliverables — is one
`PreToolUse` hook entry per capability**, not one hook piping the raw tool-call payload straight
through. A real `PreToolUse` payload carries `tool_name` and `tool_input` and has no `capability`
field of its own, so the hook's command must name the capability explicitly with `--capability`,
and the hook's `matcher` selects which tools that capability covers. For example, denying network
access to `WebFetch` and `WebSearch` would be one `.claude/settings.json` hook entry with matcher
`WebFetch|WebSearch` and command:

    uv run python -m src.broker check --capability external_network --deny external_network

The raw `PreToolUse` payload (`tool_name`, `tool_input` and the rest) is still piped to this
command on stdin — `__main__.py`'s `check` subcommand carries it into the audit record as
context — but the capability name itself comes from `--capability`, never from the payload,
because the payload does not carry one. A hook wired this way blocks the call by treating this
CLI's exit code 2 as blocking; this CLI is fail-closed, so every error path, not only an evaluated
denial, exits 2 (see `__main__.py`). Deciding which tools map to which capabilities in general —
a taxonomy covering more than one hard-coded example — is REQ-017 R02, and stays recorded open;
what this package provides is the mechanism a per-capability hook entry would call, not the
taxonomy that decides how many hook entries a real deployment would need or what each one denies.
Wiring any of this into `.claude/settings.json` is outside `src/broker/` and `test/test_broker.py`,
this phase's only declared deliverables.
"""
