---
schema_version: 1
id: doc-workbench-terminal-decision
code: ADR-014
title: The workbench terminal is a gated product capability with a session registry and selectable shells
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-demo-stage, sys-api, sys-ui]
depends_on: [doc-workbench-requirements, doc-demo-terminal-decision]
supersedes: [doc-demo-terminal-decision]
---

# The workbench terminal is a gated product capability with a session registry and selectable shells

## Context

The demo terminal decision ([ADR-013](ADR-013-demo-terminal-capability.md)) authorized a shell
over a websocket for the presentation stage only: localhost-bound, mounted only under
`D_SYSTEM_DEMO_TERMINAL=1`, never deployed, and closed with the consequence that any future
feature wanting shell execution starts from its own decision record. On 2026-09-10 the owner
ratified that the stage becomes the chartered management UI ([PROMPT-020](../02-prompts/PROMPT-020-workbench-pre-plan-package.md)
decision 2), which makes the terminal a product capability. This is that decision record. Two
loose ends land here with it: the four-session cap is enforced only in the UI (recorded against
idea `000087` during `phase-demo-06`), and the workbench needs CMD and PowerShell as selectable
panels (REQ-007 W12).

## Decision

1. **ADR-013 is superseded and narrowed by this record.** Its demo-only intent ends: the terminal
   is a workbench capability other workbench features may build on. Its protective posture
   survives unchanged — the two rules below are carried forward, not relaxed.
2. **Loopback-only binding stays.** The server hosting the terminal and workbench routes binds to
   127.0.0.1/::1, with the existing fail-fast on any non-loopback host (including the
   `UVICORN_HOST` path). Remains the default posture until a decision record says otherwise
   (PROMPT-020 decision 2).
3. **Env-flag gating stays, under the existing flag.** `D_SYSTEM_DEMO_TERMINAL=1` continues to
   gate the terminal route: renaming it would break the runbook, the Windows checklist, OPS-013
   and the rehearsed launch commands during demo week for purely cosmetic gain. A rename to a
   product-named flag is deliberately deferred to a post-demo record. Unset, the route does not
   exist — not registered, not merely disabled.
4. **A backend session registry bounds and identifies sessions.** The websocket route keeps a
   registry mapping session id → adapter for the sessions it owns; the four-session cap is
   enforced there, not only in the UI, and a fifth connection is refused with a clear close
   reason. One PTY per websocket stays; sessions still die with their websocket. This adopts the
   registry half of idea `000087` only — the outside-the-page inject/read HTTP API, detach/
   reattach, and output buffering stay parked in that idea and would start from a further record.
5. **The shell is selected per session over the existing adapter override.** Terminal (bash), CMD
   and PowerShell are three panel options, all through the one adapter interface (POSIX pty;
   ConPTY via `pywinpty` on Windows). A shell unavailable on the host is reported as a clear
   in-panel message driven by a structured refusal from the route — never a raw error, never a
   route that pretends to connect. The client's shell request is validated against a fixed
   allowlist (bash, cmd, powershell); arbitrary executable paths are rejected.

## Rejected alternatives

- **A new flag now.** Cleaner naming, but it invalidates every rehearsed command and document in
  demo week; deferred rather than refused.
- **Adopting the full 000087 API.** The inject/read HTTP surface widens who can drive a shell
  from "a person at the page" to "any local process", which deserves its own record with its own
  authentication question — not a rider on a rename of intent.
- **Free-form shell selection.** Letting the client name any executable turns a terminal panel
  into a remote-exec primitive; the allowlist keeps the capability exactly the three shells the
  workbench offers.

## Consequences

- REQ-007 W12 and W14 verify the allowlist, the refusal shape and the registry cap; the R10/R11
  session semantics of REQ-006 remain binding on the reworked panel (W02/W03).
- The workbench read/action API ([ADR-015](ADR-015-workbench-api-surface.md)) mounts under the
  same gate and binding, so one launch decision governs the whole workbench surface.
- Idea `000087` stays open, narrowed: its registry half is delivered here; annotate it so the
  remaining scope is the inject/read API alone.
- Any deployment of the workbench beyond the owner's machines starts from a new decision record;
  nothing here authorizes one.
