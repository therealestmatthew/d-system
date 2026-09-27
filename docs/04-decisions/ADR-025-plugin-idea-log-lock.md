---
schema_version: 1
id: doc-adr-plugin-idea-log-lock
code: ADR-025
title: The plugin's idea writer serializes on a filelock lock in the git common directory
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-27'
updated: '2026-09-27'
systems: [sys-plugin-ideas]
depends_on: [doc-plugin-audit-remediation-requirements]
---

# The plugin's idea writer serializes on a filelock lock in the git common directory

## Status

Accepted. The owner ruled on 2026-09-27, in the Session Manager session, after the Session Manager
set out three mechanisms (ruling D2 in
[REQ-035](../06-requirements/REQ-035-plugin-audit-remediation.md)). This record states the ruling
and what follows from it before `phase-plfx-01` builds it.

## Context

The idea-realization plugin's writer, `plugins/idea-realization/scripts/idea.py`, performs every
mutation as fold, decide, append (`add` at `:315-319`), with no lock. An independent validation of
an external audit ran twelve `idea.py add` calls at once on a fresh repository: two `created`
events for `000008` were written, three writers reported errors, and every later read of the log
failed. The plugin's own multi-session procedure runs several sessions against one repository at
once, and `docs/multi-session.md:7` says the plugin supplies no lock, so this happens in normal use.

Any fix must hold across the worktrees of one repository, because the sessions work in separate
worktrees of one checkout. It must also survive a writer that crashes while holding the lock, and it
must work on Windows, which `scripts/prerequisites.py:31-43` lists as supported.

## Decision

The writer takes an exclusive lock with the `filelock` library around the whole read, validate and
append of every mutating operation.

- **Library.** `filelock`, pinned to one exact version (`==`) in the PEP 723 header of every
  plugin script that imports it and in this repository's `dev` extra, because the plugin's tests
  import the scripts from this repository's environment. On Linux and macOS `filelock` uses
  `fcntl.flock`, and on Windows `msvcrt.locking`. Checked on 2026-09-27: version 4.0.4 is current,
  `FileLock` resolves to `UnixFileLock` on Linux, and the lock file remains on disk after release.
- **Location.** `<git common directory>/idea-realization/ideas.lock`, found with
  `git rev-parse --path-format=absolute --git-common-dir`, the same way the code reservations find
  theirs (`scripts/reservations.py:65-70`). Every worktree of a repository resolves the same file,
  and nothing under `.git` is tracked, so no ignore rule is needed.
- **Scope.** One lock per repository, not one per log file. A repository has one idea log; a lock
  keyed on the log path would let two worktrees configured with different spellings of that path
  write at once.
- **Timeout.** A writer that cannot take the lock within its timeout exits non-zero, names the lock
  file, and appends nothing. It never writes without the lock.
- **Crash.** The operating system releases an `flock` or `msvcrt` lock when its process ends, so a
  crashed writer leaves a lock file that no longer holds a lock. There is no stale-lock detection
  to write.

## Alternatives rejected

- **The plugin's own `fcntl` and `msvcrt` code (standard library only).** It keeps the dependency
  list at `jsonschema` and `pyyaml`. The cost is two platform branches written and maintained in
  the plugin, and the Windows branch would have no CI (idea `000484`). `filelock` already contains
  both branches, with their own test coverage.
- **An `O_CREAT|O_EXCL` lock file with stale-lock detection**, following the reservation pattern.
  The cost is deciding when a lock is stale. A crashed writer leaves a file that blocks every writer
  until a timeout or a person clears it. An age-based rule can also expire a lock that a slow but
  live writer still holds.
- **Procedural serialization only (the previous state).** The multi-session procedure serializes
  idea writes through a turn request. That did not prevent the failure, because a session writing
  outside the procedure, or two coordinators, reproduce it.

## Consequences

- The plugin's scripts gain a third runtime dependency. `REQ-031` R03 named only `jsonschema` and
  `pyyaml`, and REQ-035 R02 widens it. The plugin's portability test (`test/test_scripts_portable.py`,
  `ALLOWED`) changes with it.
- The lock serializes writers on one machine only. Two worktrees on two machines, or two branches
  each adding `00000N` and then merging, can still collide. REQ-035 R03 (owner ruling D3) makes
  that a procedural rule with a warning: ideas are recorded only on the integration branch in the
  primary checkout.
- The rendered view (`render_ideas.py`) is written without the lock. It is regenerated from the
  log, so a lost write there is repaired by the next render.
- The Windows path is not exercised by any CI run.
