---
schema_version: 1
id: doc-session-terminal-interaction-api-build
code: SESS-2026-10-08-11
title: Build the flag-gated terminal inject and read API (phase-wbf-08)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-api, sys-demo-stage]
depends_on: [doc-adr-terminal-interaction-api, doc-workbench-features-defects-requirements, doc-session-terminal-interaction-api-decision]
---

# Build the flag-gated terminal inject and read API (phase-wbf-08)

## Phase

`phase-wbf-08` (build the flag-gated terminal inject and read API), group of
[`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md). Builder A (`agent-builder-a`)
under the Session Manager's pre-approved run of 2026-10-08. Branch `agent/phase-wbf-08`, cut from
the run's integration branch `ccr-b69b05b4-tdcrux`.

## Awaiting ratification

The build follows [`ADR-030`](../04-decisions/ADR-030-terminal-interaction-api.md), which is
**proposed; awaiting the owner's ratification (pre-approved run, 2026-10-08)**. If the owner rules
differently on the second flag, the token, the buffer depth or the idle rule, this phase's code
changes with it. The runbook entry carries the same status note.

## Outcome

What was built, against the contract in the ADR:

- `src/api/routes/demo_terminal_api.py` (new): `GET /sessions`, `POST /sessions/{id}/input` and
  `GET /sessions/{id}/output` under `/api/v1/demo/terminal`. One dependency checks the peer
  (403 `forbidden_peer`) and the bearer token (401 `unauthorized`, `hmac.compare_digest`). The
  routes do not use framework validation: the inject route checks the content type (415), reads the
  raw body with `request.stream()` under the 16384-byte limit (413), then parses and validates by
  hand (413 for a decoded input over 4096 bytes, then 422); the output route validates its query
  by hand. A route class converts the one error exception into the shared
  `{"error": {"code", "message"}}` body. The order 403, 401, 404, 415, 413, 422, 409 holds.
- The token: `secrets.token_urlsafe(32)` generated at import; written to
  `~/.d-system/terminal-api/<key>.token` by `write_token_file()` (an existing file or symlink at the
  path is removed, the new file is created with `O_CREAT|O_EXCL|O_NOFOLLOW` at 0600, the directory
  is 0700, a symlinked or foreign-owned directory is refused). `token_file_path(repo_root, home)` is
  the overridable path function. Any failure raises `TokenFileError` at import, so a both-flags
  launch does not start unprotected. The path is logged at start-up, never the token.
- `src/api/routes/demo_terminal.py`: `SessionOutput` (the 256 KiB byte ring with absolute offsets, a
  per-session `asyncio.Condition`, the HTTP write lock, the last-inject and last-frame clocks) held
  in a sibling mapping `OUTPUT_RECORDS`; `SESSIONS` and `RESERVED` still alone decide whether a
  session exists. `OUTPUT_CAPTURE_ENABLED` is False until the API module is imported. With it on,
  the pump appends each chunk before sending it and drains the shell's tail after exit; the idle
  loop ignores a timeout when an inject was accepted inside the idle window and less than
  `TERMINAL_API_INJECT_CEILING_SECONDS` (3600) has passed since the last websocket frame. With it
  off the pump and the idle loop run the code they ran before.
- `src/api/__init__.py`: the second flag `D_SYSTEM_TERMINAL_API == "1"` nested inside the first
  flag's block.
- `docs/00-working/demo-runbook.md`: one entry at the end of the Launch Command Reference naming
  the second flag, the token path and its read rules.

Real-server check (uvicorn on port 8016, temporary HOME, a real websocket client): the token path
appears in the server log; an unauthenticated list answers 401; a listed session accepts
`echo smoke-$((6*7)); exit`, the read returns `smoke-42` and `alive: false`; the websocket client's
112 received bytes equal the buffer byte for byte; a later inject answers 409 `session_ended`.

## Evidence

- `uv run pytest test/test_demo_terminal.py`: 56 passed.
- `uv run pytest test/test_demo_terminal_api.py`: 111 passed at the first hand-off; 150 after the review round.
- `uv run pytest` (full): 1961 passed, 1 skipped, **1 failed**:
  `test/test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused`. It fails the same
  way with this phase's changes stashed (the sandbox runs as uid 0, which ignores `chmod 0500`), so
  it is not caused by this phase and was not touched.
- `uv run python -m src.governance`: `Governance OK: 45 systems, 464 documents, 37 memories, 354
  backlog phases` (before this record).
- `uv run ruff check src/ test/ tools/`: all checks passed. `uv run mypy src/`: no issues in 52
  source files. `cd ts && npm test`: 84 passed. `cd ts && npm run build`: built.
- Mutation checks on the new tests (each reverted): removing the post-exit drain fails the tail
  test; making the idle rule ignore injects fails the extension test; making a read set the inject
  clock fails the read-does-not-extend test; appending after the send, and only for long chunks,
  fails the tail and browser-completeness tests.

## Acceptance

- `R17`: an injected command executes in the named session (`$((6*7))` is `42` only if bash ran
  it), and an unknown or malformed id is `404 unknown_session` with `SESSIONS`, `RESERVED` and
  `OUTPUT_RECORDS` unchanged. Met.
- `R18`: with a websocket attached, an HTTP reader polling in 211-byte reads while `seq 1 3000`
  flows leaves the websocket client with exactly the bytes the buffer holds. Met.
- `R19`: with either flag unset, or set to anything but `1`, each route is the framework 404 with
  `{"detail": "Not Found"}`, `demo_terminal_api` is not imported, no token directory exists, capture
  is off and the registries are unchanged. Met.

## Not run

- Windows file-mode behaviour of the token file (profile-directory permissions; `0700` and `0600`
  have no effect there): owner-machine, not run.
- That ConPTY (cmd, PowerShell) accepts `\r` as end of line for `submit`: owner-machine, not run.
  On Linux the submit tests show the pty accepts it.

## Assumptions

Where the ADR is silent the safer option was chosen:

1. The record is a sibling mapping `OUTPUT_RECORDS`; a session in `SESSIONS` without a record is
   reported `404 unknown_session` rather than served without a buffer.
2. `alive` on the list and read routes is false once the websocket has closed, or once the shell
   has exited and the pump has drained its tail; until then a reader that sees `alive: false` has
   the whole tail. The inject check uses the shell's own state, since a dead shell cannot be written.
3. The pump's drain after exit is bounded at 2 seconds (`OUTPUT_DRAIN_SECONDS`), so a background
   process that inherited the pty cannot keep it reading.
4. The token file holds the token with no trailing newline, so the file content is exactly the
   header value. The module also refuses a created file whose mode has group or other bits (POSIX).
5. A token directory with a wider mode that the current user owns is tightened to 0700; one owned by
   another user, or a symlink, is refused. The parent `~/.d-system` is created 0700 if absent and is
   not otherwise checked, because a user may keep it as a symlink for dotfiles.
6. An inject whose write raises `RuntimeError` (the adapter was closed while the request waited) is
   `409 session_ended`, like `OSError`.
7. The start-up path line and the per-inject line use the `uvicorn.error` logger. An INFO line from
   a module's own logger is not printed under the documented launch command.
8. A `limit` smaller than the one multi-byte character at the start of a read wins over the
   character boundary; otherwise the read could never advance. In every other case a live read stops
   before an incomplete trailing sequence, and a read with only an incomplete sequence available
   returns empty (a long poll keeps waiting).
9. `wait` is accepted as plain decimal (`5`, `0.5`), not exponent form; `after` and `limit` are
   plain decimal digits. The `after` and `limit` digits are capped at 18 characters.
10. Responses carry `Cache-Control: no-store`.
11. (Superseded by the review round.) A blocked pty write now has a deadline and a dead pump now
    reads as not alive; see the Review section.

## Unresolved

- The full-suite failure above is pre-existing and environmental (running as root).
- The websocket route still has no authentication (ADR-030 open item 7); this phase does not change
  it.

## Review

Three reviews of `e39d74c` all passed. Verdict records, copied unchanged:
`docs/08-governance/reviews/verdicts/2026-10-08-phase-wbf-08-demo-adversary.json` (gating, four
minor), `.../2026-10-08-phase-wbf-08-security-review.json` (gating, one major and minors) and
`.../2026-10-08-phase-wbf-08-review-judge.json` (shadow, four minor). Dispositions:

- Security F01 (major, a blocked pty write has no deadline): fixed. `_write_bounded` makes the master
  descriptor non-blocking for the write and loops on `select` against a deadline
  (`INJECT_WRITE_DEADLINE_SECONDS`, 5 s), restoring blocking mode afterwards; the executor await is
  also wrapped in `asyncio.wait_for`. A partial write is returned with `accepted_bytes` set to the
  bytes actually written; a write that accepts nothing is `409` with a **new code `write_timeout`**
  (not in the ADR's table; the Session Manager or the owner must add it to ADR-030). The reviewer's
  reproduction is a test (a running `sleep`, six 4000-byte injects with CRs: each answers inside the
  deadline, one is `write_timeout`, and the shell is gone after the websocket closes). The websocket
  path drops a keystroke with a warning if it meets `BlockingIOError`, which can only happen while an
  inject holds the descriptor non-blocking; with the API off the descriptor is always blocking. An
  adapter with no descriptor (ConPTY) keeps its own `write()`, bounded only by the wait: owner-machine,
  not run.
- Security F02 (write racing `adapter.close()`): fixed. Teardown sets `ended`, takes the session's
  write lock (bounded by `WRITE_CLOSE_WAIT_SECONDS`, 7 s) and then closes the adapter. Tested by
  holding the lock and checking that `close()` waits.
- Security F03 (body read has no deadline; `ClientDisconnect`): fixed. The read is bounded by
  `BODY_READ_DEADLINE_SECONDS` (10 s) and a disconnect is caught; both answer `422 invalid_request`.
  Tested through the ASGI app with a stalled and a disconnecting body.
- Security F04 and judge F04 (parent directory unchecked): fixed. `~/.d-system` gets the same
  symlink, type and owner check; it is checked before the leaf is created, so a symlinked parent is
  refused without creating anything behind it. Its mode is left as it is. Tests: symlinked parent,
  foreign-owned parent (monkeypatched), parent mode kept.
- Security F05 (websocket accepts any Origin or Host): not mine. Pre-existing, outside this range;
  idea `000614`, ADR-030 open item 7.
- Security F06 and adversary F02 (missing tests): fixed. Added: chunked body without a length,
  concurrent injects, foreign Origin and Host with and without the token (and the CORS preflight),
  `X-Forwarded-For`, the token absent from the shell's and the server's environment, a websocket
  frame resetting the ceiling clock, the ring's content when the send raises, the post-exit drain
  while the pump is held in a send. Mutation checks on the frame reset, the drain, append-before-send,
  the teardown lock and the pump-alive rule each fail the new tests.
- Security F07 and judge F03 (dead pump reads alive): fixed. `_stream_alive` is `not ended and not
  pump_done`; an inject returns `409 session_ended` once the pump has stopped. Tested.
- Adversary F01 (collecting the tests with both flags exported rotates the token): fixed in
  `test/conftest.py`, which clears `D_SYSTEM_TERMINAL_API` before `src.main` is imported. The file
  already existed and is **not named in this phase's deliverables, which must be widened by
  `test/conftest.py`** (the Session Manager applies that on the trunk). HOME is not set there: it
  would change what git and other subprocess tests read, and the cleared flag already prevents any
  token write. A subprocess test collects both test files with both flags exported and a temporary
  HOME and asserts no `.d-system` appears.
- Adversary F03 (unused `type: ignore`): fixed; `uv run mypy test/test_demo_terminal_api.py` is clean.
- Adversary F04 (`wait` and `after` grammar narrower than the ADR): fixed. `wait` is parsed with
  `float()` plus a finite and range check (`.5`, `1e1`, `+1` accepted; non-ASCII and underscore forms
  still refused); `after` and `limit` stay ASCII digits only, per the ADR, with no 18-digit cap.
- Judge F01 (full pytest exits 1 on the root-sensitive test): not mine; unchanged and pre-existing.
- Judge F02 (verification entry omits `test/test_demo_terminal_api.py`): the Session Manager applies
  it on the trunk.
