---
schema_version: 1
id: doc-adr-terminal-interaction-api
code: ADR-030
title: The external terminal interaction API is a second-flag, token-authenticated, loopback HTTP surface over one shared output buffer
kind: adr
status: draft
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-api, sys-demo-stage, sys-contracts]
depends_on: [doc-workbench-terminal-decision, doc-workbench-api-decision, doc-demo-terminal-decision, doc-workbench-features-defects-requirements]
---

# The external terminal interaction API is a second-flag, token-authenticated, loopback HTTP surface over one shared output buffer

## Status

**Proposed; awaiting the owner's ratification (pre-approved run, 2026-10-08).** Written by
`phase-wbf-07` under the Session Manager's pre-approved run. The owner has not reviewed it. It
gates `phase-wbf-08` (build the flag-gated terminal inject and read API), which builds against the
recommendation below, so a different ruling changes that phase's scope. The ratification points are
collected in "Open items for the owner" at the end. Nothing is built by this record.

## Context

Idea `000087` (terminal interaction API for driving demo shell sessions from outside the stage
page) asks for HTTP endpoints that inject input into, and read output from, a running terminal
session, so that scripts and agents outside the stage page can drive it. Its original text lists
unresolved points: whether sessions outlive their websocket, how much output to buffer, and
whether the API generalises into workflow triggering. It also says the work "begins with a new ADR
covering gating (its own env flag or the existing one), loopback binding, session identity,
authentication if any, and output buffering."
[`REQ-012`](../06-requirements/REQ-012-workbench-features-defects.md) turns that list into `R15`
(a decision on each of six questions) and `R16` (state what `ADR-014` already owns).
[`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md) group `G51` and design decision 3
make the ADR its own phase, separate from the build.

### What `ADR-014` already owns (`R16`)

[`ADR-014`](ADR-014-workbench-terminal-capability.md) absorbed the session-registry half of
`000087` and parked the rest. This record does not reopen any of the following, and it proposes no
second registry:

| Settled by `ADR-014` | Where it lives now |
|---|---|
| A backend session registry maps session id to adapter and enforces the concurrent-session cap, now six | `SESSIONS` and `RESERVED` in `src/api/routes/demo_terminal.py`; `phase-wbf-09` (`R20`, `R21`) fixed the reservation race and the cap refusal |
| Loopback-only binding with fail-fast on a non-loopback host | `enforce_loopback_bind()`, run when the module is imported |
| Gating under `D_SYSTEM_DEMO_TERMINAL=1`; unset, the route is not registered | `src/api/__init__.py` |
| One PTY per websocket; a session ends when its websocket ends | the `finally` block in `terminal_websocket` |
| Per-session shell selection against a fixed allowlist (bash, cmd, powershell) | `SHELL_ALLOWLIST` |
| Session identity: a server-generated id, one per accepted connection | `uuid.uuid4().hex` in `terminal_websocket` |

`ADR-014` left exactly one item: "the outside-the-page inject/read HTTP API, detach/reattach, and
output buffering stay parked in that idea and would start from a further record." It also named the
reason: that surface "widens who can drive a shell from 'a person at the page' to 'any local
process', which deserves its own record with its own authentication question." This record is that
further record. [`ADR-013`](ADR-013-demo-terminal-capability.md) (now superseded) set the precedent
that a shell capability beyond its stated scope starts from its own decision record.

### Facts from the repository that bind the decision

1. **The websocket session id is generated on the server and the browser never sees it.**
   `terminal_websocket` creates `uuid.uuid4().hex`, uses it as the key in `SESSIONS`, and sends it
   nowhere. An external caller has no way to learn an id today.
2. **Adapter reads are destructive.** `TerminalAdapter.read()` (`src/demo/adapter.py`) consumes
   bytes from the PTY. `_pump_adapter_to_websocket` is the only reader today. A second reader would
   take bytes the browser then never receives.
3. **The idle bound counts websocket frames only.** `terminal_websocket` wraps
   `websocket.receive()` in a 300 second timeout (`D_SYSTEM_DEMO_TERMINAL_IDLE_TIMEOUT_SECONDS`
   overrides it). Input arriving over HTTP would not reset it, so a session driven only by HTTP
   under an idle browser tab would be reaped after 300 seconds.
4. **The session routes carry no authentication and no `Origin` check.** Read from the code:
   `terminal_websocket` accepts any connection to the route. A browser enforces CORS only on
   reading cross-origin responses; it does not stop a page on any origin from opening a websocket,
   or sending a cross-origin `POST` with a simple content type, to `127.0.0.1`. `src/main.py`
   allows one origin (`http://localhost:5173`) for CORS, which governs what a page may read back.
5. **The bind check is a launch-time heuristic.** The docstring of `resolve_configured_host()`
   says it covers "the launch paths in use today" and cannot see a programmatic
   `uvicorn.run(host=...)`, a config file or a proxy. The Vite dev proxy forwards requests to the
   backend from a loopback peer address whatever its own listen address is.
6. **The workbench routes and the terminal routes use different prefixes.** The terminal router is
   mounted at `/api/v1/demo/terminal`; the workbench routes at `/api/v1/workbench`. `ADR-015`
   scopes its read-only rule (rule 4) to the workbench routes.
7. **`data/` is gitignored** (`.gitignore`), so a file written there is never tracked.

Vocabulary follows `brain/concepts/terms-workbench-ui.md`: a slot is the container and a panel is
its content. This record names no slot by identifier. "The terminal panel" is the content the stage
page shows for a session, and "the browser" means the stage page attached to a session.

## Decision

The six questions of `R15`, each with its decision, then the contract `phase-wbf-08` builds.

### 1. Gating: a second flag, required in addition to the existing one

The inject/read routes mount only when **both** `D_SYSTEM_DEMO_TERMINAL=1` and
`D_SYSTEM_TERMINAL_API=1` are set in the server's environment (exact string `1`, as the existing
flag is read). With either unset, the routes are not registered: the module is not imported, no
handler exists, and a request returns the framework's default `404` (`R19`).

The second flag is additive. Every rehearsed launch command, the runbook, the Windows checklist
and `OPS-013` keep working unchanged, which is the cost `ADR-014` cited when it declined to rename
the first flag. In those launches the API is simply off.

Reason: the websocket lets a person at the page type into a shell. This surface lets a script do it
without a page, which `ADR-014` called a change in who can drive a shell. A launch decision that
exposes the first should not silently expose the second, and the rehearsed demo launch, which sets
the first flag every time, does not need the second at all. The cost is one extra environment
variable on the launches that want the API.

### 2. Binding: loopback only, checked at launch and again per request

1. **Launch.** The API module imports `src.api.routes.demo_terminal`, which runs
   `enforce_loopback_bind()` at import. No separate bind check is added, and the heuristic's stated
   coverage (fact 5) is inherited, not claimed to be complete.
2. **Per request.** Every API route also rejects a request whose peer address
   (`request.client.host`) is not `127.0.0.1` or `::1`, with `403` and error code `forbidden_peer`.
   This catches a bind the launch check missed. It does not catch a request forwarded by a local
   proxy such as the Vite dev server, whose peer address is loopback; the token (section 3) is the
   boundary for that case.
3. No setting widens this. Binding beyond loopback starts from a new decision record, as `ADR-014`
   and `ADR-015` state.

### 3. Authentication: a bearer token on every route, read from a file in `data/`

**What an unauthenticated loopback inject allows, stated plainly.** Loopback is reachable by every
process on the machine, not only the owner's. With no authentication, any such process, and any web
page the owner has open in a browser, can do the following to a session whose id it can obtain:

- write arbitrary bytes into a shell that runs with the owner's privileges, in the owner's working
  directory and environment. If that shell is running an agent such as `claude`, the bytes are
  prompts that agent will act on;
- read everything the shell has printed in the retained window, which can include environment
  values, file contents and credentials shown on screen;
- do both without any window being opened, from a browser tab the owner is not looking at.

Two facts reduce this and two limit the reduction.

- *Reduces:* the session id is a 128-bit random value that is not shown anywhere, so an attacker
  needs the list route to learn it. The list route would be unauthenticated too if there were no
  token, so this protects nothing by itself.
- *Reduces:* the injected input is echoed by the shell into the terminal panel, so a person looking
  at the panel sees it. This does not apply when the shell has echo off (a password prompt) or
  when nobody is looking.
- *Limits:* a process running as the owner can already start its own shell with the owner's
  privileges. For such a process the API adds access to the owner's existing session (its history,
  its running agent, its open credentials), not new privilege.
- *Limits:* the websocket route (fact 4) already lets any local process or any web page open a
  fresh shell with no authentication. A token on the new API does not close that. It keeps the new
  surface from being easier to reach than the existing one, and it covers the new surface's
  distinct exposures: other users' processes on a shared machine, cross-origin web pages, and
  reads of an existing session's output. The websocket gap is outside this record and is raised as
  an item for the owner (open item 7).

**Decision: every route requires `Authorization: Bearer <token>`.**

- The token is `secrets.token_urlsafe(32)`, generated when the API module is imported and written to
  `data/terminal-api-token` (the directory is gitignored; the module creates it if absent) with file
  mode `0600` on POSIX. The file is rewritten on each server start, so a token is valid for one
  server run. The path is logged at startup; the token never is.
- If the token cannot be generated or written, the module raises at import, the same way a
  non-loopback bind does, so the application does not start with the API mounted and unprotected.
- Comparison uses `hmac.compare_digest`. A missing, malformed or wrong token returns `401` with
  error code `unauthorized` and no other hint. Authentication is checked **before** the session
  lookup, so an unauthenticated caller cannot learn whether a session id exists.
- The token travels only in the header, never in a query string, so it does not reach server or
  proxy logs. A header named `Authorization` forces a browser to send a preflight request on any
  cross-origin call, and the CORS policy in `src/main.py` allows only `http://localhost:5173`, so a
  web page on another origin cannot send an authenticated request. The inject route additionally
  requires `Content-Type: application/json` (`415` otherwise), so even a request that skipped
  authentication could not be a browser "simple request".
- There is no environment-variable form of the token. A token in the server's environment would be
  inherited by every shell the terminal starts.

What the token does not do: it does not stop a process that can read `data/terminal-api-token`.
That is a process running as the owner, which can already run anything the owner can (see
"Limits"). On Windows, the file-mode restriction is best-effort and the check is
owner-machine, not run.

### 4. Session identity: the `ADR-014` id, discovered by a list route, never chosen by the caller

- A session is named by its existing registry id (`uuid.uuid4().hex`, 32 lowercase hex
  characters). This record adds no second identifier and no label.
- A caller learns ids from `GET /sessions`, which lists the sessions in `SESSIONS` with the shell
  and creation time so the caller can identify the one it wants (the newest, or by shell).
- **A caller cannot create a session by naming one.** An id not in `SESSIONS` is refused with
  `404` and error code `unknown_session`, and no state changes (`R17`). Sessions come into
  existence only through the websocket, as today. The API therefore drives sessions a browser has
  opened; it does not open shells (see "Not authorised by this record").
- The session id is not added to a websocket frame in this record. Doing so needs a change to the
  terminal panel code under `ts/`, which neither `phase-wbf-07` nor `phase-wbf-08` declares.

### 5. Output buffering: one bounded byte buffer per session, fed by the pump

**The pump becomes the only reader of the adapter and appends to a buffer; HTTP readers read the
buffer, never the adapter (`R18`).**

- `_pump_adapter_to_websocket` calls `adapter.read()` as it does today. For each chunk it first
  appends the bytes to the session's output buffer, then sends them to the websocket. Appending
  first means a failed send cannot drop bytes from the buffer.
- The buffer is a ring of the most recent **262144 bytes (256 KiB)** per session, with a
  monotonically increasing absolute byte offset: `total` is the count of bytes ever appended and
  `start = total - len(retained)` is the offset of the oldest retained byte. At six sessions the
  ceiling is 1.5 MiB of memory.
- It holds raw PTY output, escape sequences and shell echo included, not decoded text and not lines.
- All access is on the server's single event loop, as with `SESSIONS`, so it needs no lock.
- The buffer belongs to the session and is discarded with it. It is held in a record created and
  removed in the same two places as the `SESSIONS` entry (the successful start and the `finally`
  block in `terminal_websocket`). Membership and the cap remain `SESSIONS` and `RESERVED`; the
  record is not consulted for either. `phase-wbf-08` may realise this as a sibling mapping or as
  a richer value in `SESSIONS`, provided exactly one structure decides whether a session exists.
- The record also holds the shell name requested (or none), the creation time, and a
  last-activity time used by section 6.

### 6. Whether sessions outlive their websocket: no

`ADR-014`'s rule stands: one PTY per websocket, and the session ends with its websocket. There is
no detach, no reattach, and no grace period.

- When the websocket closes, the session leaves `SESSIONS`, its buffer is discarded, and its routes
  return `404 unknown_session`. An HTTP reader that needs the final output must read before the
  browser closes.
- When the shell exits while the websocket is still open, the session stays in `SESSIONS`.
  The read route returns the retained output with `"alive": false`, and the inject route returns
  `409` with error code `session_ended`.
- **HTTP activity keeps the idle bound honest.** An accepted inject and a read both update the
  session's last-activity time. When the websocket receive times out, the route checks the
  last-activity time and keeps waiting if HTTP activity occurred inside the idle window. Without
  this, a script driving a session under an idle tab would lose it after 300 seconds (fact 3). The
  websocket still has to be open; the bound only decides when a silent session is reaped.

### The contract `phase-wbf-08` builds

All routes are under the existing terminal prefix, `/api/v1/demo/terminal`, in a new module
`src/api/routes/demo_terminal_api.py` mounted from `src/api/__init__.py` inside the existing flag
block and behind the second flag. All routes check, in order: peer address, bearer token, then the
request. Errors share one shape:

```json
{ "error": { "code": "unknown_session", "message": "No live terminal session has that id" } }
```

Codes and statuses: `forbidden_peer` 403, `unauthorized` 401, `unknown_session` 404,
`session_ended` 409, `invalid_request` 422 (malformed body or query), `payload_too_large` 413,
`unsupported_media_type` 415. A route that does not exist (a flag unset) returns the framework
default `404` with a `detail` body, which is how a caller tells "flag off" from "unknown session".

**`GET /sessions`**

```json
{
  "sessions": [
    { "session_id": "3f9c...", "shell": "bash", "created_at": "2026-10-08T14:03:11Z",
      "alive": true, "output_start": 0, "output_total": 18234 }
  ]
}
```

`shell` is the allowlisted name the client requested, or `null` when it requested none (the
platform default or the `D_SYSTEM_DEMO_SHELL` override applied). Sessions are ordered by
`created_at`, oldest first. An empty list is `{"sessions": []}`, not an error.

**`POST /sessions/{session_id}/input`**

Request, `Content-Type: application/json`:

```json
{ "input": "ls -la", "submit": true }
```

- `input` is a string, encoded as UTF-8 and written unchanged with `adapter.write()`. The adapter
  contract does not change (`ADR-014`, idea `000087`).
- `submit` is an optional boolean, default `false`. When `true`, one carriage return (`\r`) is
  appended, which is what the browser terminal sends for Enter. The POSIX pty accepts it as end of
  line by default (`ICRNL`); `phase-wbf-08` confirms that on Linux, and the ConPTY (cmd,
  PowerShell) check is owner-machine, not run. The server translates nothing else, so control
  characters in
  `input` (for example `\u0003` for Ctrl-C) reach the shell.
- The encoded `input` plus the optional `\r` may not exceed **4096 bytes** (`413 payload_too_large`).
  A longer injection is several requests.
- The write runs off the event loop (`run_in_executor`), because `adapter.write()` is a blocking
  `os.write` on the PTY, and is serialised per session with an `asyncio.Lock` so two requests do not
  interleave their bytes.

Response `200`:

```json
{ "session_id": "3f9c...", "accepted_bytes": 7, "output_offset": 18234 }
```

`output_offset` is the session's `total` immediately before the write. A caller passes it as
`after` to the read route to read only what the injection produced. An unknown id is `404
unknown_session`; a session whose shell has exited is `409 session_ended`; neither writes anything.
Each accepted injection is logged at INFO with the session id, byte count and peer address, never
the content, which can carry secrets.

**`GET /sessions/{session_id}/output?after=<offset>&limit=<bytes>&wait=<seconds>`**

- `after` (integer, default: the oldest retained offset) is the absolute offset to read from.
  `after` greater than `total` is `422 invalid_request`.
- `limit` (integer, default 65536, maximum 262144) bounds the bytes returned.
- `wait` (number of seconds, default 0, maximum 10): when no bytes are available at `after`, the
  route holds the request until bytes arrive, the wait elapses, or the session ends, then returns.
  This lets a caller read an injection's result without a tight polling loop.

Response `200`:

```json
{
  "session_id": "3f9c...",
  "from": 18234,
  "next": 18291,
  "truncated": false,
  "alive": true,
  "text": "total 8\r\ndrwxr-xr-x ...",
  "data_base64": "dG90YWwgOA0K..."
}
```

- `from` is the offset of the first byte returned and `next` is the offset to pass as the next
  `after`. Reading never advances anything on the server: two readers, or one reader twice, get the
  same bytes. This is what makes the read non-destructive.
- `truncated` is `true` when `after` was older than the oldest retained byte, so output between
  `after` and `from` was dropped from the ring. The reader learns it missed output rather than
  receiving a silent gap.
- `data_base64` is the exact bytes. `text` is the same bytes decoded as UTF-8 with replacement for
  invalid sequences, escape sequences left in place. `next` never falls inside a multi-byte UTF-8
  sequence unless the session has ended, so successive `text` values concatenate cleanly.
- An unknown id is `404 unknown_session`. A session whose shell has exited still answers `200`
  with `"alive": false` until its websocket closes.

### Absence with the flag unset (`R19`)

With `D_SYSTEM_TERMINAL_API` unset, or `D_SYSTEM_DEMO_TERMINAL` unset, `demo_terminal_api` is never
imported and none of the three routes is registered, so each returns the framework `404`. No handler
runs, so no registry is read or written, no buffer is created, and the token file is not created.
The buffer and last-activity record on the websocket side are part of the terminal route, which
exists only under the first flag; with the second flag unset they exist but no route reads them.

### What `phase-wbf-08` must also do

- **Test client address.** The per-request peer check rejects Starlette's default `TestClient`
  peer (`testclient`). The tests construct it with a loopback `client=("127.0.0.1", 50000)` and
  add one case with a non-loopback peer that expects `403 forbidden_peer`.
- **Deliverables.** Its entry lists `src/api/routes/` and `test/`. Mounting the module needs a
  change to `src/api/__init__.py`, which is outside both, so the entry must also name that file
  before the phase is claimed. Documenting the second flag and the token path for operators (the
  demo runbook, `docs/00-working/demo-runbook.md`, is where the launch commands live) is a further
  file; the owner decides whether it belongs in that phase (open item 5).
- **Checks that map to the acceptance rows.** `R17`: inject over HTTP into a live test session and
  read the shell's output of it; an unknown id is `404 unknown_session` and `SESSIONS` is
  unchanged. `R18`: attach a websocket client, read over HTTP while output flows, and assert the
  websocket client received every byte the buffer holds. `R19`: with each flag unset, every route
  is `404` and `SESSIONS`, `RESERVED` and the buffer mapping are unchanged. Authentication: no
  header, wrong token and a right token on each route, and the `401` precedes the `404`.

## Alternatives considered

### Gating

**Use the existing flag alone.** This is the cheapest option and it needs no new variable. It is
rejected because it makes every demo launch, which already sets the flag, expose the strongest
capability this system has had: input into the owner's shell and the shell's output, to any process
that can reach the port. The demo does not use the API. One extra variable on the launches that do
want it is the whole cost of keeping that exposure a separate decision.

**A second flag alone, without requiring the first.** Rejected. The API acts only on sessions the
websocket creates, so it is useless without the first flag, and allowing it to mount alone would
create a state where the API is advertised but nothing can be listed. Requiring both also means the
`ADR-014` statement that one flag governs the terminal still holds as a lower bound.

**A level in the existing flag (`D_SYSTEM_DEMO_TERMINAL=2`).** Rejected. The code and every
document compare it to exactly `1`; a new value would be silently treated as off by anything that
does not know about it, and it overloads one variable with two decisions.

### Authentication

**None, loopback only.** The cheapest option, and the one `000087` hints at ("authentication if
any"). Rejected for the exposures listed in section 3: a shared machine, a web page in the owner's
browser, and reading an existing session's output. The saving is one header and one file; the risk
is a write path into a shell for anything that can reach the port. The token does not make the
whole terminal safe (the websocket gap remains) but it avoids adding a second unauthenticated way
in.

**Allow only requests from the stage page's origin (an `Origin` or `Host` allowlist).** Rejected as
the only control. It stops a browser page on another origin, but any local process can set any
header it likes, so it adds nothing against the local-process case. A token also stops the browser
case, so the allowlist would be redundant.

**A token supplied by the owner in an environment variable.** Rejected. The server's environment is
inherited by every shell it starts, so the token would be readable from inside the sessions it
protects. A generated token in a file that only the caller reads avoids that, and needs no setup.

**A per-session capability returned when the websocket opens.** Rejected for now. It would put a
secret in a websocket frame the terminal panel must read and show to a script, which needs changes
under `ts/` that no phase here declares. It is a candidate if the owner wants per-session
revocation.

**A Unix socket or Windows named pipe instead of TCP.** Rejected. It would give filesystem
permissions as authentication, but the server is a TCP application served by `uvicorn`, the owner's
machine is Windows, and a second transport doubles what `phase-wbf-08` builds and tests.

### Session identity

**Caller-chosen names or labels.** Rejected. Accepting a name from the caller means the first inject
to a new name either creates a session (refused above) or needs a name-to-id mapping, which is the
second registry `R16` forbids.

**Ordinal position ("session 1", "the newest").** Rejected. Positions shift when a session closes,
so an inject meant for one session could land in another, which in a shell is not a recoverable
mistake. A fixed id fails safe: it either names the session or it is unknown.

**Send the id to the browser in a websocket frame.** Rejected here because it needs `ts/` changes
(see section 4). The list route is enough for a script to find the session it wants.

### Output buffering

**Read the adapter directly from the HTTP route.** Rejected. `adapter.read()` consumes bytes, so a
read over HTTP would remove them from what the pump later sends to the browser. This is the defect
`R18` names.

**A queue or subscriber per reader.** Rejected. Each subscriber needs its own bound and its own
cleanup when it goes away without telling the server. One shared buffer with the reader holding its
own offset has no per-reader server state.

**An unbounded buffer, or a line-count limit.** Rejected. A shell can print without end, and a line
can be arbitrarily long, so neither bounds memory. A byte limit does.

**Writing the buffer to disk.** Rejected. It would persist whatever the shell printed, credentials
included, outside the process and past the session, which the memory-only buffer does not.

**A different depth.** 64 KiB was considered and rejected as too small to hold the output of one
build or test run, so a reader that polls every few seconds would see `truncated` often. 1 MiB was
rejected as larger than any reader needs; at six sessions it would hold 6 MiB for no gain. 256 KiB
is several thousand lines at 80 columns. The owner can change the constant; it is not a contract
the callers depend on beyond `truncated`.

**A second attach for reading (another websocket, or server-sent events).** Rejected. It is more to
build and test than a polled route with an optional wait, and a polled route is what a shell
script can call.

### Whether sessions outlive their websocket

**Detach and reattach.** This is the option `000087` raised, and it would let a script keep a shell
running after the browser closes. Rejected. A detached session needs a reaping policy that the idle
bound cannot provide (there is no peer to time out), it holds one of six cap slots with nobody
looking, and it makes a shell outlive every UI that could show it. That is a headless shell
capability, a larger decision than an inject/read API, and `ADR-013`'s precedent says it starts from
its own record.

**A grace period after disconnect.** Rejected for the same reasons at smaller scale, plus a state
("detached for N seconds") that the cap, the list route and the tests would each need to represent.

**Keep the buffer of an ended session for a short time.** Rejected. It would let a reader fetch the
tail after the browser closes, but it needs a second kind of entry that is not a live session, which
is a registry by another name. A reader that needs the tail reads before the browser closes, or
while the shell has exited and the websocket is still open (section 6).

## Not authorised by this record

Each of the following would be a new capability and starts from its own decision record, as
`ADR-013` and `ADR-014` require:

- creating a session over HTTP, or any headless shell;
- closing, killing or resizing a session over HTTP;
- detach and reattach (section 6);
- binding beyond loopback;
- generalising this API into workflow triggering. `000087` asks whether it should; this record
  answers only that it is not decided here. A caller of this API is a script that types into a
  shell the owner can watch, not a workflow engine.

## Consequences

- `phase-wbf-08` is bounded by "The contract `phase-wbf-08` builds": three routes, the second flag,
  the token file, the pump change, the idle-clock change, and tests for `R17`, `R18`, `R19` and
  authentication. It changes `demo_terminal.py` (the pump and the idle loop), adds one module, and
  needs `src/api/__init__.py` added to its deliverables.
- The websocket route's behaviour for a browser is unchanged. The one change on the browser's path
  is that the pump copies each chunk into the buffer before sending it. The browser's idle bound
  can now be extended by HTTP activity, never shortened.
- `ADR-014` is extended, not superseded: its decisions 1 to 5 stand. `ADR-015` is not extended: its
  rule 4 applies to the workbench routes, and this API lives under the terminal prefix. This record
  is nevertheless the "new decision record" that `ADR-014` and `ADR-015` require before a route that
  widens who can drive a shell.
- Nothing about the stage page changes. A script finds sessions by listing them, so a person
  running a demo sees no new control.
- An injected command is visible in the terminal panel as echo, but nothing in the panel marks it
  as coming from outside. A shell with echo off hides it.
- The first flag's exposure is unchanged by this record. The websocket still has no
  authentication, and the token on this API does not make the terminal safe against a local process
  (open item 7).
- Output retained for reading is held in server memory only, up to 256 KiB per session, and is gone
  when the session ends or the server stops.

## Open items for the owner

These are the points the owner is asked to ratify or change.

1. **A second flag, `D_SYSTEM_TERMINAL_API=1`, required in addition to the first.** The
   alternative is the existing flag alone, which needs no new variable and exposes the API on every
   demo launch.
2. **A bearer token from a generated file in `data/`, on every route.** The alternative is no
   authentication on loopback. The owner should say whether the token's inconvenience (a caller
   reads one file) is acceptable for the safety it buys.
3. **No detach or reattach; sessions end with their websocket.** This keeps `ADR-014` decision 4 as
   it is. A ruling for detach is a separate, larger decision.
4. **HTTP inject and read extend the idle bound; the session ends when the websocket does.** The
   alternative is to leave the bound on websocket frames only, which reaps a script-driven session
   under an idle tab after 300 seconds.
5. **Scope of `phase-wbf-08`'s documentation.** The record leaves open whether the second flag and
   the token path are documented in the demo runbook inside that phase or in a later one.
6. **Buffer depth of 256 KiB per session** and the 4096 byte input limit. Both are constants a
   later change can move.
7. **The websocket has no authentication or `Origin` check** (fact 4, from reading the code; not
   reproduced). It is outside this record's scope because `ADR-014` owns the route. The owner may
   want a separate decision on requiring the same token, or an `Origin` check, on the websocket;
   that would need a change to the terminal panel code to send it.
8. **Pointers on ratification.** Add a one-line "extended by ADR-030" pointer to `ADR-014`
   decision 4, which currently says the inject/read API "would start from a further record", and
   annotate idea `000087` so its remaining scope reads as delivered by this record and
   `phase-wbf-08`. The Session Manager's Ideation lane does the annotation; this phase records no
   ideas.

## Revisit trigger

Revisit if an agent or script needs to run a shell with no browser open, which is the case for
detach or headless creation. Revisit the token if the owner wants the stage page itself to call this
API (it would need the token delivered to the page), or if the websocket gains authentication
(item 7), at which point both should use one mechanism.
