"""Demo terminal websocket route — ADR-013 section 1 and 2.

`src/api/__init__.py` imports this module only when `D_SYSTEM_DEMO_TERMINAL=1`; with the flag
unset, this module is never imported and the route is never registered — the websocket path
does not exist, it does not exist-but-refuse. Importing this module is also what triggers
`enforce_loopback_bind()` below, so a launch with the flag set on a non-loopback bind host
fails fast at import time, before the app finishes constructing.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import Final, TypeGuard

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from src.demo.adapter import TerminalAdapter
from src.demo.factory import create_adapter

DEMO_TERMINAL_FLAG: Final[str] = "D_SYSTEM_DEMO_TERMINAL"
BIND_HOST_ENV_VAR: Final[str] = "D_SYSTEM_BIND_HOST"
UVICORN_HOST_ENV_VAR: Final[str] = "UVICORN_HOST"
LOOPBACK_HOSTS: Final[frozenset[str]] = frozenset({"127.0.0.1", "::1", "localhost"})
DEFAULT_UVICORN_HOST: Final[str] = "127.0.0.1"

READ_CHUNK_SIZE: Final[int] = 4096
READ_TIMEOUT_SECONDS: Final[float] = 0.1

# `struct.pack("HHHH", ...)` in `src/demo/posix.py` packs each field as an unsigned short
# (0..65535); a resize frame outside that range reaches `fcntl.ioctl` and raises
# `struct.error`, which is not a `WebSocketDisconnect` and so tears the whole session down
# (D06-A finding 1, proven with `{"type":"resize","cols":100000,...}`). Rejecting it here,
# before `adapter.resize()` is ever called, keeps it a dropped frame like any other malformed
# one.
MIN_TERMINAL_DIMENSION: Final[int] = 1
MAX_TERMINAL_DIMENSION: Final[int] = 65535

# A peer that vanishes without sending a close frame — SIGKILL'd, or a dropped network path —
# never sends `websocket.disconnect`, so an unbounded `await websocket.receive()` blocks
# forever and `finally: adapter.close()` never runs, orphaning the shell (D06-A finding 2,
# proven with a hard-killed client leaving `sleep 6666` running). Wrapping each receive in a
# timeout bounds how long a session can go silent before its shell is reaped; any real frame —
# including a future client-side keepalive ping — resets the clock simply by making the next
# receive() resolve. Generous by default so a presenter reading slides mid-demo, with no
# keystrokes and no shell output, is never mistaken for a dead peer; overridable for tests.
IDLE_TIMEOUT_ENV_VAR: Final[str] = "D_SYSTEM_DEMO_TERMINAL_IDLE_TIMEOUT_SECONDS"
DEFAULT_IDLE_TIMEOUT_SECONDS: Final[float] = 300.0


def _resolve_idle_timeout_seconds() -> float:
    """The idle bound for `websocket.receive()`, read fresh on each connection.

    Read at connection time rather than cached at import time so tests can set
    `D_SYSTEM_DEMO_TERMINAL_IDLE_TIMEOUT_SECONDS` to a small value with `monkeypatch` without
    reloading this module.
    """
    raw = os.environ.get(IDLE_TIMEOUT_ENV_VAR)
    if raw is None:
        return DEFAULT_IDLE_TIMEOUT_SECONDS
    try:
        return float(raw)
    except ValueError:
        return DEFAULT_IDLE_TIMEOUT_SECONDS


class NonLoopbackBindError(RuntimeError):
    """Raised when D_SYSTEM_DEMO_TERMINAL=1 but the configured bind host is not loopback."""


def resolve_configured_host() -> str:
    """The host this process is bound (or about to bind) to.

    This is a heuristic, not a certainty: it inspects the same process's env vars and argv
    for the ways `uvicorn` conventionally learns its bind host, but it cannot see every path
    a caller could take to change that host (a programmatic `uvicorn.run(host=...)` call, a
    config file, a reverse proxy remapping the bind after the fact, or an env var name this
    function does not yet know to check). Adding a new launch method to the fleet without
    adding it here would let that method start on a non-loopback host unrefused — so treat
    this function's coverage as "the launch paths in use today", not "every launch path".

    Checked in order:
    1. `D_SYSTEM_BIND_HOST` — an explicit override used by tests, and by any launch method
       that does not go through the `uvicorn` CLI at all.
    2. `--host` on the process's own `sys.argv` — the `uvicorn` CLI and the app it imports run
       in the same interpreter process, so `--host 0.0.0.0` on the launch command line is
       visible here. An explicit CLI flag is what a real `uvicorn` invocation honors over its
       own env-var default, so it is checked before `UVICORN_HOST` here too.
    3. `UVICORN_HOST` — uvicorn's CLI is built on `click` with `auto_envvar_prefix="UVICORN"`,
       so `UVICORN_HOST=0.0.0.0` sets `--host` for a `uvicorn` launch exactly as if it had been
       passed on the command line, and this function must check it or a launch of the form
       `UVICORN_HOST=0.0.0.0 uvicorn src.main:app` would bind non-loopback while this function
       still reported the loopback default.
    4. Uvicorn's own default of 127.0.0.1, when none of the above says otherwise.
    """
    env_host = os.environ.get(BIND_HOST_ENV_VAR)
    if env_host:
        return env_host
    argv = sys.argv
    for index, arg in enumerate(argv):
        if arg == "--host" and index + 1 < len(argv):
            return argv[index + 1]
        if arg.startswith("--host="):
            return arg.split("=", 1)[1]
    uvicorn_host_env = os.environ.get(UVICORN_HOST_ENV_VAR)
    if uvicorn_host_env:
        return uvicorn_host_env
    return DEFAULT_UVICORN_HOST


def enforce_loopback_bind() -> None:
    """Fail fast unless the configured bind host is loopback — ADR-013 section 1."""
    host = resolve_configured_host()
    if host not in LOOPBACK_HOSTS:
        raise NonLoopbackBindError(
            f"{DEMO_TERMINAL_FLAG}=1 requires a loopback bind host (127.0.0.1 or ::1); "
            f"got {host!r}. Refusing to start per ADR-013."
        )


router = APIRouter()


async def _pump_adapter_to_websocket(adapter: TerminalAdapter, websocket: WebSocket) -> None:
    """Forward shell output to the client until the shell exits or the pump is cancelled."""
    loop = asyncio.get_event_loop()
    while adapter.alive:
        data = await loop.run_in_executor(
            None, adapter.read, READ_CHUNK_SIZE, READ_TIMEOUT_SECONDS
        )
        if data:
            await websocket.send_bytes(data)


def _is_valid_dimension(value: object) -> TypeGuard[int]:
    """True for a JSON integer in `1..MAX_TERMINAL_DIMENSION` — excludes bool, which is an
    int subclass, and excludes anything `struct.pack("HHHH", ...)` (an unsigned short per
    field, in `src/demo/posix.py`) cannot hold.
    """
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and MIN_TERMINAL_DIMENSION <= value <= MAX_TERMINAL_DIMENSION
    )


def _apply_control_message(adapter: TerminalAdapter, text: str) -> None:
    """Parse a text frame as a control message and apply it, or drop it silently.

    The only recognized control message is `{"type": "resize", "cols": N, "rows": N}` with
    `cols`/`rows` integers in `1..MAX_TERMINAL_DIMENSION`. Invalid JSON, a non-object payload,
    an unrecognized `"type"`, or a missing/out-of-range `cols`/`rows` is dropped without
    raising — a malformed text frame must never crash the session and must never reach the
    shell as input, so there is no fallback path here that writes `text` to the adapter.
    """
    try:
        message = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return
    if not isinstance(message, dict) or message.get("type") != "resize":
        return
    cols = message.get("cols")
    rows = message.get("rows")
    if not _is_valid_dimension(cols):
        return
    if not _is_valid_dimension(rows):
        return
    adapter.resize(cols, rows)


@router.websocket("/ws")
async def terminal_websocket(websocket: WebSocket) -> None:
    """Bridge a websocket connection to a real shell session via the `src.demo` adapter.

    Two ASGI frame kinds share this one socket: binary frames are raw shell input, written
    to the adapter unchanged; text frames are control messages (today, only a terminal
    resize) parsed and applied by `_apply_control_message` — never written to the shell.

    Each `receive()` is bounded by an idle timeout (`_resolve_idle_timeout_seconds`): a peer
    that vanishes without a close frame — SIGKILL'd, or a dropped network path — would
    otherwise block this loop forever and leave the shell orphaned, since `finally:` never
    runs until the `await` resolves (D06-A finding 2).
    """
    await websocket.accept()
    adapter = create_adapter()
    adapter.start()
    pump_task = asyncio.create_task(_pump_adapter_to_websocket(adapter, websocket))
    idle_timeout_seconds = _resolve_idle_timeout_seconds()
    try:
        while True:
            try:
                message = await asyncio.wait_for(
                    websocket.receive(), timeout=idle_timeout_seconds
                )
            except TimeoutError:
                break
            if message["type"] == "websocket.disconnect":
                raise WebSocketDisconnect(message["code"], message.get("reason"))
            data = message.get("bytes")
            if data is not None:
                adapter.write(data)
                continue
            text = message.get("text")
            if text is not None:
                _apply_control_message(adapter, text)
    except WebSocketDisconnect:
        pass
    finally:
        pump_task.cancel()
        adapter.close()


# This module is imported only when D_SYSTEM_DEMO_TERMINAL=1 (see src/api/__init__.py), so
# enforcing the loopback bind here — as a side effect of import, not merely a comment — ties
# the check to the same condition that gates the route's existence.
enforce_loopback_bind()
