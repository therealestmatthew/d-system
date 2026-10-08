"""Terminal interaction API: list sessions, inject input, read output (ADR-030).

`src/api/__init__.py` imports this module only when both `D_SYSTEM_DEMO_TERMINAL=1` and
`D_SYSTEM_TERMINAL_API=1` are set. With either unset the module is never imported: no route is
registered (a request gets the framework's default 404), no handler runs, no token file is
written and `demo_terminal.OUTPUT_CAPTURE_ENABLED` stays False, so the websocket route keeps no
output record.

What importing this module does, in order:

1. Imports `src.api.routes.demo_terminal`, which runs `enforce_loopback_bind()` (ADR-030 section 2).
2. Generates the bearer token and writes it to `~/.d-system/terminal-api/<key>.token`, created
   atomically at mode 0600 in a 0700 directory (ADR-030 section 3). A failure raises
   `TokenFileError` and the application does not start with the API mounted and unprotected.
3. Switches output capture on in `demo_terminal` (ADR-030 section 5).

The routes sit under the terminal prefix, `/api/v1/demo/terminal`. They do not use framework
request validation, because that answers a malformed body with its own 422 before authentication
runs. One dependency checks the peer and the token, and each handler validates by hand, so the
precedence is 403, 401, 404, 415, 413, 422, 409 and every error carries the one shared body.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import hashlib
import hmac
import ipaddress
import json
import logging
import math
import os
import re
import secrets
import select
import stat
import time
from collections.abc import Callable, Coroutine
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.requests import ClientDisconnect

from src.api.routes import demo_terminal
from src.api.routes.demo_stage import REPO_ROOT

TERMINAL_API_FLAG: Final[str] = "D_SYSTEM_TERMINAL_API"

MAX_INPUT_BYTES: Final[int] = 4096
MAX_BODY_BYTES: Final[int] = 16384
DEFAULT_OUTPUT_LIMIT: Final[int] = 65536
MAX_OUTPUT_LIMIT: Final[int] = 262144
MAX_WAIT_SECONDS: Final[float] = 10.0

# Deadlines, read at the point of use so tests can lower them. An inject's PTY write is bounded
# because a shell whose foreground process is not reading input (a long build) stops accepting
# bytes once the line discipline's buffer is full; an unbounded write would hold the request, the
# session's inject lock and an executor thread, and keep the shell alive after its session ends.
INJECT_WRITE_DEADLINE_SECONDS: float = 5.0
# Extra time the event loop gives the write thread past its own deadline before giving up on it.
INJECT_WRITE_THREAD_GRACE_SECONDS: Final[float] = 2.0
BODY_READ_DEADLINE_SECONDS: float = 10.0

TOKEN_DIRECTORY_PARTS: Final[tuple[str, str]] = (".d-system", "terminal-api")
SESSION_ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{32}")
_DIGITS_PATTERN: Final[re.Pattern[str]] = re.compile(r"[0-9]+")

# The token path and the inject audit line must be visible to the person running the server.
# Uvicorn configures its own loggers, not the root logger, so an INFO line from this module's own
# logger would not be printed under the documented launch command.
logger = logging.getLogger("uvicorn.error")


# --- the shared error shape ---------------------------------------------------------------------


class TerminalApiError(Exception):
    """An API refusal that `_ApiRoute` turns into the shared `{"error": {...}}` body."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


def _error_response(exc: TerminalApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
        headers={"Cache-Control": "no-store"},
    )


def _json_response(content: dict[str, Any]) -> JSONResponse:
    return JSONResponse(content=content, headers={"Cache-Control": "no-store"})


def _unauthorized() -> TerminalApiError:
    return TerminalApiError(401, "unauthorized", "A valid bearer token is required")


def _unknown_session() -> TerminalApiError:
    return TerminalApiError(404, "unknown_session", "No live terminal session has that id")


def _invalid_request(message: str) -> TerminalApiError:
    return TerminalApiError(422, "invalid_request", message)


def _session_ended() -> TerminalApiError:
    return TerminalApiError(409, "session_ended", "The terminal session's shell has ended")


class _ApiRoute(APIRoute):
    """Route class that answers a `TerminalApiError` with the shared error body.

    An `APIRouter` cannot carry exception handlers (only the application can, and `src/main.py` is
    outside this phase), so the conversion happens around each route's own handler instead.
    """

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original = super().get_route_handler()

        async def handler(request: Request) -> Response:
            try:
                return await original(request)
            except TerminalApiError as exc:
                return _error_response(exc)

        return handler


# --- the token file ------------------------------------------------------------------------------


class TokenFileError(RuntimeError):
    """Raised at import when the token file cannot be created safely (ADR-030, fail closed)."""


def token_file_path(repo_root: Path, home: Path | None = None) -> Path:
    """The token file for the checkout at `repo_root`: `<home>/.d-system/terminal-api/<key>.token`.

    `<key>` is the first 16 hex characters of the SHA-256 of the absolute repository root path, so
    two checkouts or worktrees never overwrite each other's token. `home` defaults to the user's
    home directory (the profile directory on Windows); tests pass a temporary directory.
    """
    base = Path.home() if home is None else home
    key = hashlib.sha256(str(repo_root.resolve()).encode("utf-8")).hexdigest()[:16]
    return base.joinpath(*TOKEN_DIRECTORY_PARTS, f"{key}.token")


def _check_token_directory(level: Path, *, tighten: bool) -> None:
    """Refuse a symlink, a non-directory or a foreign owner at `level` (POSIX owner check).

    The leaf is also tightened to 0700. The parent (`~/.d-system`) keeps its mode: a user may keep
    other files there, and the leaf's own 0700 is what protects the token.
    """
    info = os.lstat(level)
    if stat.S_ISLNK(info.st_mode):
        raise TokenFileError(f"{level} is a symlink; refusing to write the API token under it")
    if not stat.S_ISDIR(info.st_mode):
        raise TokenFileError(f"{level} is not a directory")
    if os.name == "posix":
        if info.st_uid != os.geteuid():
            raise TokenFileError(f"{level} is not owned by the current user")
        if tighten and info.st_mode & 0o077:
            os.chmod(level, 0o700)


def _prepare_token_directory(directory: Path) -> None:
    """Create the token directory at mode 0700; check it and its parent (ADR-030 section 3).

    The parent is created and checked before the leaf is created, so a symlinked parent is refused
    without creating anything behind it.
    """
    try:
        for level, tighten in ((directory.parent, False), (directory, True)):
            try:
                os.mkdir(level, 0o700)
            except FileExistsError:
                pass
            _check_token_directory(level, tighten=tighten)
    except OSError as exc:
        raise TokenFileError(f"Cannot prepare {directory} for the API token: {exc}") from exc


def write_token_file(path: Path, token: str) -> None:
    """Write `token` to `path`, created atomically at mode 0600 (ADR-030 section 3).

    Any existing file is removed first, then the new one is created with
    `O_CREAT | O_EXCL | O_NOFOLLOW` and mode 0600. Opening an existing file for writing would keep
    its old mode, and a chmod after creation leaves a window at the umask mode. A symlink planted at
    the path cannot redirect the write. The token is written without a trailing newline so that the
    file's content is exactly the token. Raises `TokenFileError` on any failure.
    """
    _prepare_token_directory(path.parent)
    try:
        try:
            existing = os.lstat(path)
        except FileNotFoundError:
            pass
        else:
            if stat.S_ISDIR(existing.st_mode):
                raise TokenFileError(f"{path} is a directory")
            os.unlink(path)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, 0o600)
        try:
            if os.name == "posix" and os.fstat(fd).st_mode & 0o077:
                raise TokenFileError(f"{path} was created with a mode that other users can read")
            data = token.encode("ascii")
            written = 0
            while written < len(data):
                written += os.write(fd, data[written:])
        finally:
            os.close(fd)
    except TokenFileError:
        with contextlib.suppress(OSError):
            os.unlink(path)
        raise
    except OSError as exc:
        with contextlib.suppress(OSError):
            os.unlink(path)
        raise TokenFileError(f"Cannot write the API token to {path}: {exc}") from exc


# Generated once per process, when both flags are set and this module is imported. A launch with
# either flag unset never reaches this line, so it never generates or writes a token.
TOKEN: Final[str] = secrets.token_urlsafe(32)
TOKEN_FILE: Final[Path] = token_file_path(REPO_ROOT)
write_token_file(TOKEN_FILE, TOKEN)
logger.info("Terminal API token file: %s", TOKEN_FILE)


# --- authentication ------------------------------------------------------------------------------


def _is_loopback_peer(request: Request) -> bool:
    """True only when the peer address is loopback; the string `localhost` is not a peer address."""
    client = request.client
    if client is None:
        return False
    try:
        address = ipaddress.ip_address(client.host)
    except ValueError:
        return False
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
        address = address.ipv4_mapped
    return address.is_loopback


def _token_is_valid(header: str | None) -> bool:
    if header is None:
        return False
    scheme, _, presented = header.partition(" ")
    if scheme.lower() != "bearer":
        return False
    return hmac.compare_digest(presented.strip().encode("utf-8"), TOKEN.encode("ascii"))


async def authenticate(request: Request) -> None:
    """Peer check (403) then bearer token (401), before anything else about the request is read."""
    if not _is_loopback_peer(request):
        raise TerminalApiError(403, "forbidden_peer", "Requests must come from a loopback address")
    if not _token_is_valid(request.headers.get("authorization")):
        raise _unauthorized()


router = APIRouter(route_class=_ApiRoute, dependencies=[Depends(authenticate)])


# --- session lookup ------------------------------------------------------------------------------


def _lookup(session_id: str) -> tuple[Any, demo_terminal.SessionOutput]:
    """The live adapter and output record for `session_id`, or 404 `unknown_session`.

    Anything that is not 32 lowercase hex characters, or is not in `SESSIONS`, gets the same
    answer. `SESSIONS` decides whether a session exists; a session without an output record cannot
    be served and is reported the same way.
    """
    if SESSION_ID_PATTERN.fullmatch(session_id) is None:
        raise _unknown_session()
    adapter = demo_terminal.SESSIONS.get(session_id)
    output = demo_terminal.OUTPUT_RECORDS.get(session_id)
    if adapter is None or output is None:
        raise _unknown_session()
    return adapter, output


def _stream_alive(adapter: Any, output: demo_terminal.SessionOutput) -> bool:
    """False once the websocket has closed or the pump has stopped for any reason.

    The pump ends when the shell has exited and its tail is drained, and also when it fails (for
    example a send to a vanished browser), in which case nothing more would be captured, so the
    session no longer reads as alive and no longer accepts input.
    """
    del adapter  # the pump, not the shell alone, decides: it drains the tail after the shell exits
    return not output.ended and not output.pump_done


# --- GET /sessions -------------------------------------------------------------------------------


@router.get("/sessions")
async def list_sessions() -> JSONResponse:
    entries = []
    for session_id, adapter in list(demo_terminal.SESSIONS.items()):
        output = demo_terminal.OUTPUT_RECORDS.get(session_id)
        if output is None:
            continue
        entries.append((output.created_at, session_id, adapter, output))
    entries.sort(key=lambda entry: entry[0])
    return _json_response(
        {
            "sessions": [
                {
                    "session_id": session_id,
                    "shell": output.shell,
                    "created_at": datetime.fromtimestamp(created_at, tz=UTC).strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "alive": _stream_alive(adapter, output),
                    "output_start": output.start,
                    "output_total": output.total,
                }
                for created_at, session_id, adapter, output in entries
            ]
        }
    )


# --- POST /sessions/{session_id}/input -----------------------------------------------------------

_write_executor: ThreadPoolExecutor | None = None


def _get_write_executor() -> ThreadPoolExecutor:
    """The executor for `adapter.write()`, kept apart from the default executor the pump reads on.

    `adapter.write()` is a blocking `os.write` on the PTY; a write that blocks must not starve the
    pump's reads. Created on first use so an import that never injects starts no threads.
    """
    global _write_executor
    if _write_executor is None:
        _write_executor = ThreadPoolExecutor(
            max_workers=demo_terminal.MAX_CONCURRENT_SESSIONS,
            thread_name_prefix="terminal-api-write",
        )
    return _write_executor


def _is_json_content_type(header: str | None) -> bool:
    if header is None:
        return False
    return header.split(";", 1)[0].strip().lower() == "application/json"


def _too_large(message: str) -> TerminalApiError:
    return TerminalApiError(413, "payload_too_large", message)


async def _collect_body(request: Request) -> bytes:
    chunks: list[bytes] = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > MAX_BODY_BYTES:
            raise _too_large(f"The request body may not exceed {MAX_BODY_BYTES} bytes")
        chunks.append(chunk)
    return b"".join(chunks)


async def _read_limited_body(request: Request) -> bytes:
    """Read the raw body, refusing it as soon as it passes `MAX_BODY_BYTES` (before any parsing).

    The read has a deadline, and a client that disconnects part-way is answered like a body that
    never completed: both are `422 invalid_request`, an existing code.
    """
    declared = request.headers.get("content-length")
    if declared is not None and declared.isascii() and declared.isdigit():
        if len(declared) > 18 or int(declared) > MAX_BODY_BYTES:
            raise _too_large(f"The request body may not exceed {MAX_BODY_BYTES} bytes")
    try:
        return await asyncio.wait_for(_collect_body(request), timeout=BODY_READ_DEADLINE_SECONDS)
    except TimeoutError:
        raise _invalid_request("The request body was not received in time") from None
    except ClientDisconnect:
        raise _invalid_request("The client disconnected before the body was complete") from None


def _parse_inject_body(body: bytes) -> bytes:
    """Validate the inject body by hand and return the bytes to write to the shell.

    The decoded-size check (413) runs before the remaining shape checks (422), matching the
    precedence in ADR-030.
    """
    try:
        parsed = json.loads(body.decode("utf-8"))
    except (ValueError, RecursionError):
        raise _invalid_request("The body must be valid UTF-8 JSON") from None
    if not isinstance(parsed, dict):
        raise _invalid_request("The body must be a JSON object")
    text = parsed.get("input")
    submit = parsed.get("submit", False)
    encoded: bytes | None = None
    if isinstance(text, str):
        with contextlib.suppress(UnicodeEncodeError):
            encoded = text.encode("utf-8")
        if encoded is not None and len(encoded) + (1 if submit is True else 0) > MAX_INPUT_BYTES:
            raise _too_large(
                f"input plus the optional carriage return may not exceed {MAX_INPUT_BYTES} bytes"
            )
    unknown = set(parsed) - {"input", "submit"}
    if unknown:
        raise _invalid_request(f"Unknown key: {sorted(unknown)[0]}")
    if not isinstance(text, str) or encoded is None:
        raise _invalid_request("input is required and must be a UTF-8 string")
    if not isinstance(submit, bool):
        raise _invalid_request("submit must be a boolean")
    if not encoded and not submit:
        raise _invalid_request("input may not be empty unless submit is true")
    return encoded + (b"\r" if submit else b"")


def _write_bounded(adapter: Any, payload: bytes, deadline_seconds: float) -> int:
    """Write `payload` to the shell without blocking past `deadline_seconds`; returns bytes written.

    Runs on the write executor. For an adapter that exposes a PTY master descriptor
    (`PosixPtyAdapter._master_fd`) the descriptor is made non-blocking for the duration and the
    write is a loop of `select` for writability and `os.write`, so a shell that is not reading
    cannot hold the thread. Zero bytes written by the deadline raises `TimeoutError`; a partial
    write is returned as such and the caller reports it. An adapter without such a descriptor
    (ConPTY) falls back to its own `write()`, which the caller still bounds with a timeout on the
    wait, but whose thread this module cannot free. That fallback is owner-machine, not run.
    """
    fd = getattr(adapter, "_master_fd", None)
    if not isinstance(fd, int):
        adapter.write(payload)
        return len(payload)
    deadline = time.monotonic() + deadline_seconds
    written = 0
    os.set_blocking(fd, False)
    try:
        while written < len(payload):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            _, writable, _ = select.select([], [fd], [], remaining)
            if not writable:
                break
            try:
                written += os.write(fd, payload[written:])
            except BlockingIOError:
                continue
    finally:
        with contextlib.suppress(OSError):
            os.set_blocking(fd, True)
    if written == 0:
        raise TimeoutError("the terminal did not accept input before the deadline")
    return written


@router.post("/sessions/{session_id}/input")
async def inject_input(session_id: str, request: Request) -> JSONResponse:
    adapter, output = _lookup(session_id)
    if not _is_json_content_type(request.headers.get("content-type")):
        raise TerminalApiError(
            415, "unsupported_media_type", "Content-Type must be application/json"
        )
    payload = _parse_inject_body(await _read_limited_body(request))
    if output.pump_done or not adapter.alive:
        raise _session_ended()
    async with output.write_lock:
        if output.ended or output.pump_done or not adapter.alive:
            raise _session_ended()
        offset = output.total
        loop = asyncio.get_running_loop()
        deadline = INJECT_WRITE_DEADLINE_SECONDS
        try:
            written = await asyncio.wait_for(
                loop.run_in_executor(
                    _get_write_executor(), _write_bounded, adapter, payload, deadline
                ),
                timeout=deadline + INJECT_WRITE_THREAD_GRACE_SECONDS,
            )
        except TimeoutError:
            # TimeoutError is an OSError, so it is handled first. Nothing was written.
            raise TerminalApiError(
                409,
                "write_timeout",
                "The terminal did not accept input in time; its foreground process may be busy",
            ) from None
        except (OSError, RuntimeError):
            # OSError: the shell exited between the `alive` check and the write. RuntimeError:
            # the adapter was closed (its websocket ended) while this request waited.
            raise _session_ended() from None
        output.last_inject = time.monotonic()
    peer = request.client.host if request.client is not None else "unknown"
    logger.info(
        "terminal API inject: session=%s bytes=%d peer=%s", session_id, written, peer
    )
    return _json_response(
        {"session_id": session_id, "accepted_bytes": written, "output_offset": offset}
    )


# --- GET /sessions/{session_id}/output -----------------------------------------------------------


def _single_param(request: Request, name: str) -> str | None:
    values = request.query_params.getlist(name)
    if len(values) > 1:
        raise _invalid_request(f"{name} may be given once")
    return values[0] if values else None


def _parse_integer_param(request: Request, name: str) -> int | None:
    """A non-negative decimal integer: ASCII digits only, so no sign, space or underscore."""
    raw = _single_param(request, name)
    if raw is None:
        return None
    if _DIGITS_PATTERN.fullmatch(raw) is None or len(raw) > 4000:
        raise _invalid_request(f"{name} must be a non-negative integer")
    return int(raw)


def _parse_wait_param(request: Request) -> float:
    """A finite number of seconds from 0 to 10, in any form `float()` reads (`.5`, `1e1`)."""
    raw = _single_param(request, "wait")
    if raw is None:
        return 0.0
    try:
        value = float(raw) if raw.isascii() and "_" not in raw else math.nan
    except ValueError:
        value = math.nan
    if not math.isfinite(value) or not 0.0 <= value <= MAX_WAIT_SECONDS:
        raise _invalid_request("wait must be a number of seconds from 0 to 10")
    return value


def _utf8_complete_length(data: bytes) -> int:
    """The length of `data` without a trailing, incomplete UTF-8 sequence."""
    size = len(data)
    for back in range(1, min(3, size) + 1):
        byte = data[size - back]
        if byte & 0xC0 == 0x80:
            continue
        if byte >= 0xF8 or byte < 0xC0:
            return size
        needed = 4 if byte >= 0xF0 else 3 if byte >= 0xE0 else 2
        return size if back >= needed else size - back
    return size


def _select_chunk(
    output: demo_terminal.SessionOutput, after: int, limit: int, *, finished: bool
) -> tuple[int, bytes]:
    """The offset and bytes a read at `after` returns, without changing anything.

    While the session is live the chunk never ends inside a UTF-8 sequence, so successive `text`
    values concatenate. If `limit` is below the length of the one sequence at the start, `limit`
    wins and the chunk is cut inside it: the only alternative is a read that can never advance.
    """
    start = output.start
    first = max(after, start)
    end = min(output.total, first + limit)
    chunk = bytes(output.buffer[first - start : end - start])
    if chunk and not finished:
        keep = _utf8_complete_length(chunk)
        if keep > 0:
            chunk = chunk[:keep]
        elif end == output.total:
            chunk = b""
    return first, chunk


def _decode_text(chunk: bytes) -> str:
    """Decode as UTF-8 with replacement, dropping up to three leading continuation bytes."""
    skip = 0
    while skip < 3 and skip < len(chunk) and chunk[skip] & 0xC0 == 0x80:
        skip += 1
    return chunk[skip:].decode("utf-8", errors="replace")


@router.get("/sessions/{session_id}/output")
async def read_output(session_id: str, request: Request) -> JSONResponse:
    adapter, output = _lookup(session_id)
    after_param = _parse_integer_param(request, "after")
    limit_param = _parse_integer_param(request, "limit")
    wait = _parse_wait_param(request)
    if after_param is not None and after_param > output.total:
        raise _invalid_request("after is beyond the end of the session's output")
    if limit_param is not None and not 1 <= limit_param <= MAX_OUTPUT_LIMIT:
        raise _invalid_request(f"limit must be an integer from 1 to {MAX_OUTPUT_LIMIT}")
    limit = DEFAULT_OUTPUT_LIMIT if limit_param is None else limit_param
    after = output.start if after_param is None else after_param

    def _ready() -> bool:
        finished = not _stream_alive(adapter, output)
        return finished or bool(_select_chunk(output, after, limit, finished=False)[1])

    if wait > 0 and not _ready():
        async with output.condition:
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(output.condition.wait_for(_ready), timeout=wait)

    alive = _stream_alive(adapter, output)
    first, chunk = _select_chunk(output, after, limit, finished=not alive)
    return _json_response(
        {
            "session_id": session_id,
            "from": first,
            "next": first + len(chunk),
            "truncated": after < output.start,
            "alive": alive,
            "text": _decode_text(chunk),
            "data_base64": base64.b64encode(chunk).decode("ascii"),
        }
    )


# Capture is switched on last: if anything above raised, the application does not start, and
# `OUTPUT_CAPTURE_ENABLED` was never turned on.
demo_terminal.OUTPUT_CAPTURE_ENABLED = True
