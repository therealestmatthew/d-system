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


def _is_positive_int(value: object) -> TypeGuard[int]:
    """True for a JSON integer greater than zero — excludes bool, which is an int subclass."""
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _apply_control_message(adapter: TerminalAdapter, text: str) -> None:
    """Parse a text frame as a control message and apply it, or drop it silently.

    The only recognized control message is `{"type": "resize", "cols": N, "rows": N}` with
    positive integer `cols`/`rows`. Invalid JSON, a non-object payload, an unrecognized
    `"type"`, or a missing/non-positive-integer `cols`/`rows` is dropped without raising —
    a malformed text frame must never crash the session and must never reach the shell as
    input, so there is no fallback path here that writes `text` to the adapter.
    """
    try:
        message = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return
    if not isinstance(message, dict) or message.get("type") != "resize":
        return
    cols = message.get("cols")
    rows = message.get("rows")
    if not _is_positive_int(cols):
        return
    if not _is_positive_int(rows):
        return
    adapter.resize(cols, rows)


@router.websocket("/ws")
async def terminal_websocket(websocket: WebSocket) -> None:
    """Bridge a websocket connection to a real shell session via the `src.demo` adapter.

    Two ASGI frame kinds share this one socket: binary frames are raw shell input, written
    to the adapter unchanged; text frames are control messages (today, only a terminal
    resize) parsed and applied by `_apply_control_message` — never written to the shell.
    """
    await websocket.accept()
    adapter = create_adapter()
    adapter.start()
    pump_task = asyncio.create_task(_pump_adapter_to_websocket(adapter, websocket))
    try:
        while True:
            message = await websocket.receive()
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
