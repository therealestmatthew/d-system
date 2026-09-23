---
schema_version: 1
id: doc-session-capability-and-approval-broker
code: SESS-2026-09-22-11
title: Build the capability and approval broker, enforced at the tool boundary
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems:
- sys-api
- sys-governance
depends_on:
- doc-broker-first-autonomous-operations
- doc-autonomous-operations-architecture
- doc-autonomous-agent-operations-requirements
- doc-autonomous-agent-operations
---

# Build the capability and approval broker, enforced at the tool boundary

## Phase

`phase-auto-02` — build the capability and approval broker, ahead of the trigger gateway, run
ledger and worker (`phase-auto-03` through `phase-auto-05`), per `ADR-022`'s ordering ruling.
Worked on `agent/phase-auto-02` in `/code/d-system-worktrees/phase-auto-02`, base `6339ba0`.

## What was built

`src/broker/` — four modules, no other file touched:

- **`enforcement.py`** — `check(capability, *, denied=(), state_dir, context=None) -> Decision`,
  the tool-boundary function. Permissive default: a capability not present in the caller-supplied
  `denied` set is allowed. `denied` is per-call, not a stored policy — this module owns no
  built-in capability taxonomy. Both the requested capability and every `denied` entry are
  normalised (`.strip().casefold()`) before comparison, and the normalised name is what the
  `Decision` and the audit record carry. Every call, allowed or denied, is appended to
  `<state_dir>/audit.jsonl` before `check()` returns. `record_refusal()` is the fallback used when
  `check()` itself cannot be run or trusted — it always returns `allowed=False` and writes
  best-effort (swallowing a write failure rather than raising).
- **`approvals.py`** — the approval-request surface: `request(scope, reason, expires_at)`,
  `pending()`, `get(id)`, `decide(id, decision, decided_by)`. Storage is an append-only JSONL log
  (`<state_dir>/approvals.jsonl`); current state is the last record per id. `decide()` is the only
  function that can add a decision, and it refuses a second one — that is what makes a decision
  immutable. `is_expired()` gates both `pending()` (an expired, undecided approval is not listed)
  and `decide()` (raises rather than honouring a decision against an expired approval).
- **`__main__.py`** — `python -m src.broker`: `check` for the tool-boundary call (see below), and
  `request` / `list-pending` / `decide` for the approval surface. A CLI was chosen over an API
  route specifically to avoid editing `src/api/__init__.py` or `src/main.py`, both shared
  registration files another phase could be mid-edit on.
- **`__init__.py`** — package docstring stating the shape, what stays open, and the intended
  (unbuilt) wiring.

## The owner's narrowing ruling

Deliverables are exactly `src/broker/` and `test/test_broker.py` — no other file, and no
`schemas/approval.schema.json`. The four required approval fields (`scope`, `reason`,
`expires_at`, `decision`) are validated in code inside `approvals.py`, the same way
`src/governance/reservations.py` validates its own small append-only record without a paired
JSON Schema file. This was an explicit ruling, not a default: every other entity type in this
repository (`commitment`, `project`, `idea`, …) does get a schema, and R04 (the full approval
policy/taxonomy) staying open per `ADR-022` was the stated reason a schema was not warranted yet.

## R02 / R04 — recorded open, not claimed

`ADR-022` ("The broker ships as an enforcement point with a permissive default") rules the broker
built here satisfies `REQ-017` R01 and R03 but explicitly leaves R02 (every run carries a named,
specific capability set, not a role) and R04 (a full approval schema/policy) open, because there
is no second source of real capability requests yet to design a taxonomy against — the gateway and
ledger are both deferred to later phases. Nothing in `src/broker/` declares a capability taxonomy:
`denied` in `enforcement.check()` and `scope` in an approval request are free-form strings the
caller supplies, not values drawn from an enumerated list this package owns. This is stated in
`src/broker/__init__.py`, `enforcement.py` and `approvals.py`'s own docstrings, not only here.

## R03's mechanism and how it is tested

R03: "an agent prompted to use a denied capability is stopped at the boundary, not trusted to
decline." `enforcement.check()` computes `allowed` purely from whether the normalised capability
name is in the caller-supplied `denied` set — never from any text describing intent — and
`__main__.py`'s `check` subcommand turns that into a process exit code before the underlying tool
call would run: **exit 0 = allowed, exit 2 = blocked**, and after fix cycles 1 and 2 (below),
every error path also exits 2, never anything else. A wrapper (a `PreToolUse` hook, not built in
this phase) that blocks on a nonzero — or specifically non-zero-and-not-0 — exit stops the call
mechanically; the agent's prompt plays no part.

Tested at a real subprocess boundary in `test/test_broker.py`, not just at the Python API:
`test_cli_check_blocks_a_denied_capability_with_exit_code_two` feeds a tool-call JSON payload
naming a denied capability to `python -m src.broker check` and asserts exit code 2, the printed
`allowed: false`, and the recorded audit entry. `test_cli_check_allows_by_default_with_exit_code_zero`
covers the permissive default the same way. 32 tests total in `test/test_broker.py` after both fix
cycles, all against real subprocesses for the CLI surface.

## Verification

```
$ uv run pytest
799 passed, 2 warnings in 68.49s
```

```
$ uv run python -m src.governance
Governance OK: 35 systems, 321 documents, 30 memories, 293 backlog phases
```

Both exit 0.

## Validator

The dispatched validator ran the declared verification commands against the initial build
(`f0e3d58`) and reported **PASS** before the adversary's independent review began.

## Adversarial review — two rounds, six findings, all resolved

### Round 1 (against `f0e3d58`) — five HIGH findings, all fixed in `4894ee9`

- **F1 — missing `capability` field failed open (exit 1) with no audit record.** A real
  `PreToolUse` payload never carries `capability`; the CLI exited 1 (non-blocking under the hook
  contract) and returned before any audit write. *Fixed:* `check` now fails closed — exit 2 — on
  every error path via a single fail-closed handler in `_cmd_check`, and records the refusal via
  the new `enforcement.record_refusal()` before returning.
- **F2 — malformed JSON on stdin also failed open (exit 1), no audit record.** Same class as F1,
  same fix.
- **F3 — an unwritable/uncreatable `--state-dir` crashed with an uncaught `PermissionError`, exit
  1.** *Fixed:* the call to `enforcement.check()` is wrapped in its own `try`/`except OSError`,
  reclassified as a refusal (`audit-write-failed`), and `record_refusal()` attempts its own
  best-effort write via the new `enforcement._try_append_audit()`, which swallows a further
  `OSError` rather than raising — a refusal is still returned even when the very reason the
  ordinary path failed also breaks the refusal's own attempt to log itself.
- **F4 — capability-name matching was exact-string, so `External_Network` or `"
  external_network "` bypassed a denial on `external_network`.** *Fixed:* `enforcement.check()`
  now normalises (`.strip().casefold()`) both the requested capability and every `denied` entry
  before comparing, and records the normalised name.
- **F5 — the documented wiring (pipe the raw `PreToolUse` payload straight to `check`) does not
  work**, because a real `PreToolUse` payload has no `capability` field and the mechanism had no
  way to derive one from it. *Fixed* by correcting `src/broker/__init__.py` and `__main__.py`'s
  docstrings to describe the supported wiring — one hook entry per capability, the hook's matcher
  selecting the tools, `--capability` naming the capability on the command line — and by flipping
  argument precedence so `--capability` overrides a `capability` field in the payload rather than
  being overridden by its absence.

### Round 2 (re-attack after fix cycle 1, against `4894ee9`) — F1–F5 confirmed fixed; one new finding

- **F6 — MEDIUM — if stdout is closed or broken, `check` exited 120, not 2, even for a denied
  capability**, because the final `print()` and `return` sat outside the fail-closed
  `try`/`except`: a `BrokenPipeError` (or any `OSError`) writing the decision propagated
  uncaught, and Python's own interpreter-shutdown flush of the broken stream can override the
  process's exit code to 120. *Fixed in `7990559` (this cycle):* the exit code is now decided
  entirely before any output is attempted — `_cmd_check` computes `exit_code` and either a
  decision or a refusal first, then calls a new `_write_best_effort()` helper that swallows any
  `OSError` while writing, and on `BrokenPipeError` specifically redirects the stream's underlying
  file descriptor to `os.devnull` so a later shutdown-time flush of the same stream cannot fail
  again and override the code. `KeyboardInterrupt` during `check` is now also caught and treated
  as a refusal (exit 2, reason `interrupted`). `SIGTERM` is handled from the moment `check` starts
  (`_install_sigterm_fail_closed`) and exits the process immediately via `os._exit(2)`, bypassing
  any further Python-level flushing that could change the code. `SIGKILL` cannot be handled by any
  process, this one included — the docstring says so plainly, and a caller must not treat an
  unexplained process death as equivalent to a recorded refusal.

  Three new tests: `test_cli_check_exits_two_when_stdout_is_broken_before_any_write` (a denied
  capability, stdout broken before the child ever writes, deterministic via a pre-closed pipe read
  end — asserts exit 2 and that the refusal was still audited);
  `test_cli_check_exits_two_when_stdout_is_broken_for_an_allowed_capability` (same broken-pipe
  setup with nothing denied — asserts the exit code is never Python's own broken-pipe/shutdown
  code 120); and `test_cli_check_exits_two_on_sigterm` (sends `SIGTERM` to a subprocess blocked
  reading stdin and asserts exit 2 — noted in the test's own docstring as a real
  subprocess/signal interaction rather than a pure unit test, deterministic in practice because
  the signal handler installs in microseconds before the process blocks on `stdin.read()`, with a
  generous 300ms margin before the signal is sent).

- **F4 variants (hyphen/underscore/homoglyph spellings of a capability name) — accepted as LOW,
  not fixed.** Per the coordinator's explicit ruling: both the denied name and the requested
  capability name in the supported wiring are owner-authored in the same hook command (see the
  wiring example below), so a spelling mismatch between them is a self-inflicted, immediately
  visible configuration error, not an attacker-controlled bypass the way case/whitespace variants
  from an agent-supplied payload were (F4, fixed in round 1). Only `.strip().casefold()`
  normalisation was built; hyphen/underscore folding and homoglyph detection were explicitly ruled
  out of scope for this finding.

`test/test_broker.py`: 32 tests after both fix cycles, all passing.

## Unresolved

**Nothing in this repository invokes `src.broker` automatically.** No hook, no CI step and no
other module calls it today. This is stated plainly in `src/broker/__init__.py` and
`__main__.py`'s own docstrings, and is expected — wiring it in is explicitly outside this phase's
declared deliverables (`src/broker/`, `test/test_broker.py`), which are the only files this
session or either fix cycle touched.

**The wiring the owner would add** — a `PreToolUse` hook entry per capability, matcher selecting
the tools, `--capability` naming the capability explicitly (a real `PreToolUse` payload never
carries one):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "WebFetch|WebSearch",
        "hooks": [
          {
            "type": "command",
            "command": "uv run python -m src.broker check --capability external_network --deny external_network --state-dir _working/broker"
          }
        ]
      }
    ]
  }
}
```

**Environment caveats for that wiring, none of them built or verified here:**

- `uv` must be on the hook process's `PATH`, or the command must name an absolute path to it —
  a hook runs outside an interactive shell's environment and cannot be assumed to inherit it.
- `--state-dir` should be an absolute path in real use. The default (`_working/broker`, relative)
  is resolved against the hook's working directory, which a hook runner is not guaranteed to set
  to the repository root.
- A hook timeout that kills the broker process, or a `SIGKILL` from any other source, is not a
  refusal — it is the process simply ceasing to exist before it could decide or record anything.
  A caller must not treat an unexplained process death the same as this CLI's own exit-2 refusal;
  doing so would be trusting the absence of a signal rather than a recorded decision, which is the
  same class of gap `000031` exists to close.

Mapping a general set of tools to capabilities — more than the one hard-coded example above — is
`REQ-017` R02, and stays recorded open per `ADR-022`; this phase built the mechanism a
per-capability hook entry would call, not the taxonomy deciding how many such entries a real
deployment needs or what each one should deny.

## Backlog

This session does not edit `docs/09-backlog/backlog.yaml`. The completion edit, and the
integration decision, are the coordinator's to make on `dev`.
