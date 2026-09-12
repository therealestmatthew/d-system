---
schema_version: 1
id: doc-demo-terminal-decision
code: ADR-013
title: Demo terminal is a localhost-only, flag-gated capability that is never deployed
kind: adr
status: superseded
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-demo-stage, sys-api]
depends_on: [doc-live-demo-requirements]
---

# Demo terminal is a localhost-only, flag-gated capability that is never deployed

> **Superseded and narrowed 2026-09-10 by the workbench terminal capability decision
> ([ADR-014](ADR-014-workbench-terminal-capability.md))**: the demo-only intent below ends — the
> terminal is a workbench product capability — while the loopback-only binding and the
> `D_SYSTEM_DEMO_TERMINAL=1` gating carry forward unchanged.

## Context

The live demo ([REQ-006](../06-requirements/REQ-006-live-demo.md)) needs a working terminal embedded
in the stage page: xterm.js in the browser, connected over a websocket to a real shell. Nothing in
this repository shells out to an interactive process today, so exposing a shell over a network
route — even locally — is a new class of capability here, and its boundaries need recording before
any of it is built.

## Decision

1. **Localhost-only binding.** The server hosting the terminal route binds to 127.0.0.1. The route
   is never reachable from another machine.
2. **Env-flag gating.** The websocket route mounts only when `D_SYSTEM_DEMO_TERMINAL=1` is set. In
   every other configuration — the default — the route does not exist: it is not registered, not
   merely disabled.
3. **Demo-only intent, never deployed.** The capability exists for the presentation stage on the
   owner's own machine. It ships in no deployment configuration, no CI job starts it, and no other
   feature may depend on it.
4. **Cross-platform PTY adapter.** One adapter interface with two implementations: POSIX `pty` +
   bash on Linux/macOS, and ConPTY via `pywinpty` + cmd or PowerShell on Windows. The platform is
   auto-detected; a config override selects the shell. `pywinpty` is declared as a Windows-only
   optional dependency so Linux/macOS installs never pull it.

## Rejected: exposing the capability by default

Mounting the route unconditionally and relying on the localhost binding alone was rejected. A
terminal route that always exists invites reuse by later features and widens the consequence of any
future binding or proxy mistake to arbitrary shell access. The env flag keeps the capability's
existence an explicit, per-launch decision, and the default state of the system is that no shell is
reachable over any socket.

## Consequences

- The stage page must handle the route's absence (flag unset) with a clear message rather than an
  opaque connection error, since that is the system's default state.
- Verification of the gating and binding is part of `phase-demo-01`'s acceptance
  (R05 in REQ-006), and the Windows smoke check (R06) is part of demo readiness, not an
  afterthought.
- If a future feature wants shell execution, it starts from its own decision record, not from this
  one; this ADR authorizes the demo stage only.
