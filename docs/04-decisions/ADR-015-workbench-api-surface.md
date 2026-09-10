---
schema_version: 1
id: doc-workbench-api-decision
code: ADR-015
title: The workbench read/action API is repo-bounded, read-only, and gated with the terminal
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-api, sys-ui]
depends_on: [doc-workbench-requirements, doc-workbench-terminal-decision]
---

# The workbench read/action API is repo-bounded, read-only, and gated with the terminal

## Context

The workbench panels (REQ-007) need backend routes: injection-source enumeration for the
Skills/Prompts/Agents dropdowns (W04), directory listing and recursive file search for the HTML
Viewer and File Browser (W07, W09), idea and backlog reads for the explorers (W10, W11), and one
OS action — reveal-in-explorer (W09). Serving filesystem listings and spawning an OS opener from
a web route are new capabilities here whose boundaries need recording before they are built.

## Decision

1. **One gate, one binding.** Every workbench route mounts only when `D_SYSTEM_DEMO_TERMINAL=1`
   is set and under the loopback-only binding, exactly as [ADR-014](ADR-014-workbench-terminal-capability.md)
   states. Unset, none of these routes exist. The workbench is one launch decision, not several.
2. **Repository-bounded paths, always server-validated.** Every route taking a path resolves it
   against the repository root and rejects anything that escapes it — `..` traversal, absolute
   paths outside the root, and symlinks whose resolved target leaves the root. Validation happens
   on the resolved path, server-side, on every request; the in-app pickers (W07/W09/W01) are
   convenience, not the security boundary.
3. **Listings exclude private and derived content.** Directory listings and file search never
   return `_private/` or gitignored entries (`.venv/`, `data/`, `node_modules/`, …), using the
   repository's ignore rules rather than a hand-kept list — with `_public/` and the tracked tree
   included. What the UI can browse is what the repository tracks plus its shareable outputs.
4. **Read-only, except one named action.** Enumeration (skills from `.claude/skills/`, agents
   from `.claude/agents/`, prompts from `docs/02-prompts/`, plus the single curated-overrides
   file `_data/workbench/injection-overrides.json`), listing, search, idea and backlog routes
   respond to GET only and write nothing. Idea state is read exclusively through `fold()`
   (`src/db/ideas.py`); a route or component parsing `_data/ideas.jsonl` directly is a defect
   (W10). The backlog route reads `docs/09-backlog/backlog.yaml` and orders its queue view as
   the governance `--ready` rendering does (`next_up` first, then ready phases by priority).
5. **Reveal-in-explorer is the sole action route, allowlisted per platform.** POST only. It
   validates its path per rule 2, then spawns exactly one fixed opener: `explorer.exe /select,`
   on Windows, `xdg-open` on the entry's containing directory on Linux — argument lists built
   from the validated path, never through a shell string. No other OS command is reachable; new
   actions extend this record first.

## Rejected alternatives

- **Browser-native directory pickers.** The File System Access API yields OS-absolute paths the
  repo-bounded backend must refuse, and behaves differently per browser; the in-app dialog fed by
  the listing API keeps one path model everywhere (owner decision, 2026-09-10).
- **Mounting the read routes ungated.** Read-only listings look harmless, but they enumerate the
  owner's working tree; keeping them behind the same flag preserves ADR-013's property that the
  system's default state exposes nothing.
- **A generic "run command" action.** Rejected outright; the reveal action is a fixed opener with
  a validated argument, not a command surface.

## Consequences

- REQ-007 W14 is the verification contract for this record: absent-by-default routes, traversal
  and symlink rejection, no `_private/`/gitignored listings, GET-only reads, and the reveal
  route's path validation are all asserted by tests.
- The overrides file is versioned data (`_data/workbench/`), so curating labels, injected text
  and hidden entries is a reviewed diff, not UI state.
- Copy-absolute-path (W09) is served from the backend's knowledge of the repository root; it
  exposes the root's location, which is acceptable on a loopback-only surface.
- If the workbench ever needs a write route (editing data files from the UI), that starts from a
  new decision record; nothing here authorizes one.
