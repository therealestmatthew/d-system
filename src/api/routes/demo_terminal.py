"""Demo terminal websocket route — ADR-013 section 1 and 2.

`src/api/__init__.py` imports this module only when `D_SYSTEM_DEMO_TERMINAL=1`; with the flag
unset, this module is never imported and the route is never registered — the websocket path
does not exist, it does not exist-but-refuse. Importing this module is also what triggers
`enforce_loopback_bind()` below, so a launch with the flag set on a non-loopback bind host
fails fast at import time, before the app finishes constructing.
"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Final

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from src.demo.adapter import TerminalAdapter
from src.demo.factory import create_adapter

DEMO_TERMINAL_FLAG: Final[str] = "D_SYSTEM_DEMO_TERMINAL"
BIND_HOST_ENV_VAR: Final[str] = "D_SYSTEM_BIND_HOST"
LOOPBACK_HOSTS: Final[frozenset[str]] = frozenset({"127.0.0.1", "::1", "localhost"})
DEFAULT_UVICORN_HOST: Final[str] = "127.0.0.1"

READ_CHUNK_SIZE: Final[int] = 4096
READ_TIMEOUT_SECONDS: Final[float] = 0.1


class NonLoopbackBindError(RuntimeError):
    """Raised when D_SYSTEM_DEMO_TERMINAL=1 but the configured bind host is not loopback."""


def resolve_configured_host() -> str:
    """The host this process is bound (or about to bind) to.

    Checked in order: the `D_SYSTEM_BIND_HOST` env var (an explicit override — used by tests,
    and by any launch method that does not go through the `uvicorn` CLI), then `--host` on the
    process's own `sys.argv` (the `uvicorn` CLI and the app it imports run in the same
    interpreter process, so `--host 0.0.0.0` on the launch command line is visible here), then
    uvicorn's own default of 127.0.0.1.
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


@router.websocket("/ws")
async def terminal_websocket(websocket: WebSocket) -> None:
    """Bridge a websocket connection to a real shell session via the `src.demo` adapter."""
    await websocket.accept()
    adapter = create_adapter()
    adapter.start()
    pump_task = asyncio.create_task(_pump_adapter_to_websocket(adapter, websocket))
    try:
        while True:
            data = await websocket.receive_bytes()
            adapter.write(data)
    except WebSocketDisconnect:
        pass
    finally:
        pump_task.cancel()
        adapter.close()


# This module is imported only when D_SYSTEM_DEMO_TERMINAL=1 (see src/api/__init__.py), so
# enforcing the loopback bind here — as a side effect of import, not merely a comment — ties
# the check to the same condition that gates the route's existence.
enforce_loopback_bind()
