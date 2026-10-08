"""Tests for the terminal interaction API (ADR-030, REQ-012 R17, R18, R19).

Covers `src/api/routes/demo_terminal_api.py` and the capture layer it switches on in
`src/api/routes/demo_terminal.py`: the flag combinations (absent unless both flags are `1`), the
token file creation rules (a temporary HOME, never a real token), the loopback peer check and the
bearer token, every error code and the precedence between them, the three routes against a real
bash session, the byte ring, the long poll, the idle-bound rules, and that the websocket path is
unchanged.

The POSIX file-mode assertions run on Linux. Windows file-mode behaviour (the profile directory's
default permissions; `0700` and `0600` have no effect there) is owner-machine, not run.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import importlib
import json
import os
import stat
import sys
import threading
import time
from collections.abc import Callable, Iterator, MutableMapping
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession

import src.api as api_module
import src.main as main_module

BASE = "/api/v1/demo/terminal"
WS_PATH = f"{BASE}/ws"
LIST_PATH = f"{BASE}/sessions"
LOOPBACK_PEER = ("127.0.0.1", 50000)
TERMINAL_FLAG = "D_SYSTEM_DEMO_TERMINAL"
API_FLAG = "D_SYSTEM_TERMINAL_API"
BIND_HOST_ENV_VAR = "D_SYSTEM_BIND_HOST"
IDLE_TIMEOUT_ENV_VAR = "D_SYSTEM_DEMO_TERMINAL_IDLE_TIMEOUT_SECONDS"
UNKNOWN_ID = "0" * 32

TERMINAL_MODULE = "src.api.routes.demo_terminal"
API_MODULE = "src.api.routes.demo_terminal_api"


# --- fixtures and helpers ------------------------------------------------------------------------


def _uncache_route_modules() -> None:
    """Make the next import of each terminal route module genuinely re-run it.

    Popping `sys.modules` alone is not enough: `from package import submodule` returns the
    attribute left on the parent package without importing again.
    """
    routes_package = sys.modules.get("src.api.routes")
    for dotted in (TERMINAL_MODULE, API_MODULE):
        sys.modules.pop(dotted, None)
        name = dotted.rsplit(".", 1)[1]
        if routes_package is not None and hasattr(routes_package, name):
            delattr(routes_package, name)


@pytest.fixture
def build(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[Callable[..., FastAPI]]:
    """Rebuild `src.api` and `src.main` under the given flags, with HOME in a temp directory."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))

    def _build(*, terminal: str | None = "1", api: str | None = "1") -> FastAPI:
        for name, value in ((TERMINAL_FLAG, terminal), (API_FLAG, api)):
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, value)
        monkeypatch.delenv(BIND_HOST_ENV_VAR, raising=False)
        _uncache_route_modules()
        importlib.reload(api_module)
        importlib.reload(main_module)
        return main_module.app

    yield _build

    monkeypatch.delenv(TERMINAL_FLAG, raising=False)
    monkeypatch.delenv(API_FLAG, raising=False)
    monkeypatch.delenv(BIND_HOST_ENV_VAR, raising=False)
    _uncache_route_modules()
    importlib.reload(api_module)
    importlib.reload(main_module)


@pytest.fixture
def client(build: Callable[..., FastAPI]) -> Iterator[TestClient]:
    """A client for an app with both flags set, peer address loopback, one shared event loop.

    The context manager keeps one event loop for every request and websocket, as the server has;
    without it each request would run in its own loop and the long poll's condition would be used
    from two loops.
    """
    app = build()
    with TestClient(app, client=LOOPBACK_PEER) as test_client:
        yield test_client


def terminal_module() -> Any:
    return sys.modules[TERMINAL_MODULE]


def api() -> Any:
    return sys.modules[API_MODULE]


def auth() -> dict[str, str]:
    return {"Authorization": f"Bearer {api().TOKEN}"}


def input_url(session_id: str) -> str:
    return f"{LIST_PATH}/{session_id}/input"


def output_url(session_id: str) -> str:
    return f"{LIST_PATH}/{session_id}/output"


def assert_error(response: Any, status: int, code: str) -> None:
    """The status, and the one shared body shape: {"error": {"code": ..., "message": ...}}."""
    assert response.status_code == status, response.text
    body = response.json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message"}
    assert body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]


def wait_until(condition: Callable[[], bool], timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return condition()


@contextlib.contextmanager
def open_session(
    test_client: TestClient, path: str = WS_PATH
) -> Iterator[tuple[WebSocketTestSession, str]]:
    """Open a websocket session and yield it with the id the list route reports for it."""
    known = {s["session_id"] for s in test_client.get(LIST_PATH, headers=auth()).json()["sessions"]}
    with test_client.websocket_connect(path) as websocket:
        found: list[str] = []

        def _appeared() -> bool:
            listing = test_client.get(LIST_PATH, headers=auth()).json()["sessions"]
            found[:] = [s["session_id"] for s in listing if s["session_id"] not in known]
            return bool(found)

        assert wait_until(_appeared), "the session never appeared in GET /sessions"
        yield websocket, found[0]


def inject(test_client: TestClient, session_id: str, text: str, *, submit: bool = True) -> Any:
    return test_client.post(
        input_url(session_id), json={"input": text, "submit": submit}, headers=auth()
    )


def read_until(
    test_client: TestClient, session_id: str, marker: str, *, after: int = 0, timeout: float = 8.0
) -> tuple[str, int]:
    """Read output over HTTP until `marker` appears; returns the text and the next offset."""
    text = ""
    deadline = time.monotonic() + timeout
    while marker not in text and time.monotonic() < deadline:
        response = test_client.get(
            output_url(session_id), params={"after": after, "wait": 1}, headers=auth()
        )
        assert response.status_code == 200, response.text
        body = response.json()
        text += body["text"]
        after = body["next"]
    assert marker in text, f"{marker!r} never appeared; got {text!r}"
    return text, after


def settle(test_client: TestClient, session_id: str, quiet: float = 0.4) -> int:
    """Wait until the session's `output_total` stops changing and return it."""

    def _total() -> int:
        listing = test_client.get(LIST_PATH, headers=auth()).json()["sessions"]
        return int(next(s for s in listing if s["session_id"] == session_id)["output_total"])

    last = _total()
    stable_since = time.monotonic()
    while time.monotonic() - stable_since < quiet:
        time.sleep(0.05)
        current = _total()
        if current != last:
            last, stable_since = current, time.monotonic()
    return last


def receive_exactly(websocket: WebSocketTestSession, count: int, timeout: float = 8.0) -> bytes:
    """Receive websocket bytes until `count` have arrived, without hanging the test on a bug."""
    received = bytearray()

    def _drain() -> None:
        while len(received) < count:
            received.extend(websocket.receive_bytes())

    worker = threading.Thread(target=_drain, daemon=True)
    worker.start()
    worker.join(timeout)
    assert not worker.is_alive(), f"websocket delivered {len(received)} of {count} bytes"
    return bytes(received)


# --- flag combinations (R19) --------------------------------------------------------------------


@pytest.mark.parametrize(
    ("terminal", "api_flag"),
    [("1", None), (None, "1"), (None, None), ("1", "true"), ("true", "1"), ("1", "0")],
)
def test_routes_absent_unless_both_flags_are_exactly_one(
    build: Callable[..., FastAPI], terminal: str | None, api_flag: str | None, tmp_path: Path
) -> None:
    """R19: with either flag unset (or not exactly `1`) every route is the framework 404, the
    API module is never imported, no token is written and capture stays off."""
    app = build(terminal=terminal, api=api_flag)
    assert API_MODULE not in sys.modules
    assert not (tmp_path / "home" / ".d-system").exists()
    if terminal == "1":
        assert terminal_module().OUTPUT_CAPTURE_ENABLED is False
    client = TestClient(app, client=LOOPBACK_PEER)
    for method, path in (
        ("get", LIST_PATH),
        ("post", input_url(UNKNOWN_ID)),
        ("get", output_url(UNKNOWN_ID)),
    ):
        response = getattr(client, method)(path, headers={"Authorization": "Bearer anything"})
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}


def test_flag_off_requests_have_no_side_effect(build: Callable[..., FastAPI]) -> None:
    """R19: requests to the absent routes leave the registry, the reservations and the output
    records unchanged, and write no token."""
    app = build(terminal="1", api=None)
    module = terminal_module()
    before = (dict(module.SESSIONS), set(module.RESERVED), dict(module.OUTPUT_RECORDS))
    client = TestClient(app, client=LOOPBACK_PEER)
    assert client.get(LIST_PATH).status_code == 404
    assert client.post(input_url(UNKNOWN_ID), json={"input": "ls"}).status_code == 404
    assert client.get(output_url(UNKNOWN_ID)).status_code == 404
    after = (dict(module.SESSIONS), set(module.RESERVED), dict(module.OUTPUT_RECORDS))
    assert after == before == ({}, set(), {})


def test_both_flags_mount_the_three_routes_and_turn_capture_on(
    build: Callable[..., FastAPI],
) -> None:
    app = build()
    assert API_MODULE in sys.modules
    assert terminal_module().OUTPUT_CAPTURE_ENABLED is True
    paths = set(app.openapi()["paths"])
    assert LIST_PATH in paths
    assert f"{LIST_PATH}/{{session_id}}/input" in paths
    assert f"{LIST_PATH}/{{session_id}}/output" in paths


def test_first_flag_only_keeps_no_buffer_and_session_still_works(
    build: Callable[..., FastAPI],
) -> None:
    """Under the first flag alone the websocket route creates no output record and the pump and
    idle loop run as before: a real round trip works and `OUTPUT_RECORDS` stays empty."""
    app = build(terminal="1", api=None)
    module = terminal_module()
    with TestClient(app) as client, client.websocket_connect(WS_PATH) as websocket:
        websocket.send_bytes(b"echo first-flag-only-marker\n")
        output = b""
        deadline = time.monotonic() + 5.0
        while b"first-flag-only-marker" not in output and time.monotonic() < deadline:
            output += websocket.receive_bytes()
        assert b"first-flag-only-marker" in output
        assert len(module.SESSIONS) == 1
        assert module.OUTPUT_RECORDS == {}
    assert module.OUTPUT_RECORDS == {}


# --- the token file -----------------------------------------------------------------------------


def test_token_file_is_written_at_import_with_mode_0600_in_a_0700_directory(
    build: Callable[..., FastAPI], tmp_path: Path
) -> None:
    build()
    module = api()
    path: Path = module.TOKEN_FILE
    home = tmp_path / "home"
    assert path.parent == home / ".d-system" / "terminal-api"
    assert path == module.token_file_path(module.REPO_ROOT, home)
    assert path.read_text() == module.TOKEN
    assert len(module.TOKEN) >= 43  # token_urlsafe(32)
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE((home / ".d-system").stat().st_mode) == 0o700


def test_token_file_key_is_the_sha256_prefix_of_the_repo_root(
    build: Callable[..., FastAPI], tmp_path: Path
) -> None:
    import hashlib

    build()
    module = api()
    root_a = tmp_path / "checkout-a"
    root_b = tmp_path / "checkout-b"
    root_a.mkdir()
    root_b.mkdir()
    path_a = module.token_file_path(root_a, tmp_path)
    path_b = module.token_file_path(root_b, tmp_path)
    assert path_a != path_b
    assert path_a.name == hashlib.sha256(str(root_a.resolve()).encode()).hexdigest()[:16] + ".token"


def test_startup_log_names_the_token_path_and_never_the_token(
    build: Callable[..., FastAPI], caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level("INFO", logger="uvicorn.error"):
        build()
    module = api()
    assert str(module.TOKEN_FILE) in caplog.text
    assert module.TOKEN not in caplog.text


def test_existing_file_with_mode_0644_is_replaced_by_a_0600_file(
    build: Callable[..., FastAPI], tmp_path: Path
) -> None:
    build()
    module = api()
    directory = tmp_path / "dir" / "terminal-api"
    directory.mkdir(parents=True)
    target = directory / "key.token"
    target.write_text("old")
    target.chmod(0o644)
    module.write_token_file(target, "fresh-token")
    assert target.read_text() == "fresh-token"
    assert stat.S_ISREG(os.lstat(target).st_mode)
    assert stat.S_IMODE(target.stat().st_mode) == 0o600


def test_symlink_at_the_token_path_is_replaced_and_its_target_untouched(
    build: Callable[..., FastAPI], tmp_path: Path
) -> None:
    build()
    module = api()
    victim = tmp_path / "victim.txt"
    victim.write_text("victim content")
    victim.chmod(0o644)
    directory = tmp_path / "dir" / "terminal-api"
    directory.mkdir(parents=True)
    target = directory / "key.token"
    target.symlink_to(victim)
    module.write_token_file(target, "fresh-token")
    assert not target.is_symlink()
    assert stat.S_ISREG(os.lstat(target).st_mode)
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    assert target.read_text() == "fresh-token"
    assert victim.read_text() == "victim content"
    assert stat.S_IMODE(victim.stat().st_mode) == 0o644


def test_directory_that_is_a_symlink_is_refused(
    build: Callable[..., FastAPI], tmp_path: Path
) -> None:
    build()
    module = api()
    real = tmp_path / "elsewhere"
    real.mkdir()
    parent = tmp_path / "parent"
    parent.mkdir()
    (parent / "terminal-api").symlink_to(real)
    with pytest.raises(module.TokenFileError, match="symlink"):
        module.write_token_file(parent / "terminal-api" / "key.token", "t")
    assert list(real.iterdir()) == []


def test_directory_owned_by_another_user_is_refused(
    build: Callable[..., FastAPI], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    build()
    module = api()
    directory = tmp_path / "foreign" / "terminal-api"
    directory.mkdir(parents=True)
    monkeypatch.setattr(os, "geteuid", lambda: os.stat(directory).st_uid + 1)
    with pytest.raises(module.TokenFileError, match="not owned"):
        module.write_token_file(directory / "key.token", "t")


def test_loose_directory_mode_is_tightened_to_0700(
    build: Callable[..., FastAPI], tmp_path: Path
) -> None:
    build()
    module = api()
    directory = tmp_path / "loose" / "terminal-api"
    directory.mkdir(parents=True)
    directory.chmod(0o755)
    module.write_token_file(directory / "key.token", "t")
    assert stat.S_IMODE(directory.stat().st_mode) == 0o700


def test_import_fails_closed_when_the_token_cannot_be_written(
    build: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """HOME names a regular file, so `<HOME>/.d-system` cannot be created. With both flags set the
    application must not start with the API mounted and unprotected."""
    not_a_directory = tmp_path / "not-a-directory"
    not_a_directory.write_text("x")
    build(terminal="1", api=None)  # fixture setup; the failing build follows
    monkeypatch.setenv("HOME", str(not_a_directory))
    with pytest.raises(RuntimeError, match="Cannot prepare"):
        build()
    assert terminal_module().OUTPUT_CAPTURE_ENABLED is False


def test_first_flag_only_launch_survives_an_unwritable_home(
    build: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Only a both-flags launch can be affected by a token write failure."""
    not_a_directory = tmp_path / "not-a-directory"
    not_a_directory.write_text("x")
    build(terminal="1", api=None)
    monkeypatch.setenv("HOME", str(not_a_directory))
    build(terminal="1", api=None)
    assert API_MODULE not in sys.modules


# --- peer check and authentication --------------------------------------------------------------


def test_peer_check_accepts_loopback_forms_and_refuses_everything_else(
    build: Callable[..., FastAPI],
) -> None:
    app = build()
    token = {"Authorization": f"Bearer {api().TOKEN}"}
    for peer in (("127.0.0.1", 1), ("::1", 1), ("::ffff:127.0.0.1", 1), ("127.0.0.2", 1)):
        with TestClient(app, client=peer) as peer_client:
            assert peer_client.get(LIST_PATH, headers=token).status_code == 200, peer
    for peer in (("10.1.2.3", 1), ("192.168.0.9", 1), ("localhost", 1), ("::ffff:10.1.2.3", 1)):
        with TestClient(app, client=peer) as peer_client:
            response = peer_client.get(LIST_PATH, headers=token)
            assert_error(response, 403, "forbidden_peer")


def test_default_testclient_peer_is_refused(build: Callable[..., FastAPI]) -> None:
    """Starlette's default `TestClient` peer is the string `testclient`, which is not an address."""
    app = build()
    with TestClient(app) as default_client:
        response = default_client.get(LIST_PATH, headers={"Authorization": f"Bearer {api().TOKEN}"})
    assert_error(response, 403, "forbidden_peer")


ROUTES: list[tuple[str, Callable[[str], str]]] = [
    ("get", lambda sid: LIST_PATH),
    ("post", input_url),
    ("get", output_url),
]


@pytest.mark.parametrize("index", [0, 1, 2])
def test_every_route_requires_the_bearer_token(client: TestClient, index: int) -> None:
    method, path_for = ROUTES[index]
    path = path_for(UNKNOWN_ID)
    kwargs: dict[str, Any] = {"json": {"input": "ls"}} if method == "post" else {}
    token = api().TOKEN
    bad_headers: list[dict[str, str]] = [
        {},
        {"Authorization": ""},
        {"Authorization": "Bearer"},
        {"Authorization": "Bearer "},
        {"Authorization": "Bearer wrong-token"},
        {"Authorization": f"Basic {token}"},
        {"Authorization": token},
        {"Authorization": f"Bearer {token}x"},
        {"Authorization": f"Bearer {token[:-1]}"},
    ]
    for headers in bad_headers:
        response = getattr(client, method)(path, headers=headers, **kwargs)
        assert_error(response, 401, "unauthorized")
    # A right token on an unknown id gets past authentication and reaches the lookup (or, for the
    # list route, succeeds). The scheme name is case-insensitive.
    ok = getattr(client, method)(
        path, headers={"Authorization": f"bearer {token}"}, **kwargs
    )
    if index == 0:
        assert ok.status_code == 200
    else:
        assert_error(ok, 404, "unknown_session")


def test_token_in_a_query_string_is_not_accepted(client: TestClient) -> None:
    response = client.get(LIST_PATH, params={"token": api().TOKEN})
    assert_error(response, 401, "unauthorized")


def test_unauthenticated_caller_learns_nothing_about_session_ids(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        live = client.get(output_url(session_id))
        unknown = client.get(output_url(UNKNOWN_ID))
    assert live.status_code == unknown.status_code == 401
    assert live.json() == unknown.json()


def test_wrong_method_on_a_mounted_route_is_the_framework_405(client: TestClient) -> None:
    assert client.delete(LIST_PATH, headers=auth()).status_code == 405
    assert client.get(input_url(UNKNOWN_ID), headers=auth()).status_code == 405
    assert client.post(output_url(UNKNOWN_ID), headers=auth()).status_code == 405


# --- GET /sessions ------------------------------------------------------------------------------


def test_empty_list_is_not_an_error(client: TestClient) -> None:
    response = client.get(LIST_PATH, headers=auth())
    assert response.status_code == 200
    assert response.json() == {"sessions": []}


def test_list_reports_each_session_oldest_first(client: TestClient) -> None:
    with open_session(client) as (_ws_one, first_id):
        with open_session(client, f"{WS_PATH}?shell=bash") as (_ws_two, second_id):
            body = client.get(LIST_PATH, headers=auth()).json()
    sessions = body["sessions"]
    assert [s["session_id"] for s in sessions] == [first_id, second_id]
    assert sessions[0]["shell"] is None
    assert sessions[1]["shell"] == "bash"
    for entry in sessions:
        assert set(entry) == {
            "session_id",
            "shell",
            "created_at",
            "alive",
            "output_start",
            "output_total",
        }
        assert len(entry["session_id"]) == 32
        assert entry["alive"] is True
        assert entry["output_start"] == 0
        assert entry["created_at"].endswith("Z") and "T" in entry["created_at"]


# --- R17: inject ---------------------------------------------------------------------------------


def test_injected_command_executes_in_the_named_session(client: TestClient) -> None:
    """R17: the shell executes the injected command (`$((6*7))` is only 42 if bash ran it) and the
    response names the bytes accepted and the offset the output starts at."""
    with open_session(client) as (_websocket, session_id):
        before = settle(client, session_id)
        response = inject(client, session_id, "echo r17-$((6*7))")
        assert response.status_code == 200
        assert response.json() == {
            "session_id": session_id,
            "accepted_bytes": len("echo r17-$((6*7))") + 1,
            "output_offset": before,
        }
        text, _ = read_until(client, session_id, "r17-42", after=response.json()["output_offset"])
        assert "r17-42" in text


def test_input_without_submit_does_not_run_until_a_carriage_return_arrives(
    client: TestClient,
) -> None:
    with open_session(client) as (_websocket, session_id):
        first = inject(client, session_id, "echo split-$((1+1", submit=False)
        assert first.json()["accepted_bytes"] == len("echo split-$((1+1")
        second = client.post(
            input_url(session_id), json={"input": "))", "submit": True}, headers=auth()
        )
        assert second.status_code == 200
        text, _ = read_until(client, session_id, "split-2", after=first.json()["output_offset"])
        assert "split-2" in text


def test_control_characters_reach_the_shell(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        inject(client, session_id, "sleep 30")
        time.sleep(0.3)
        response = inject(client, session_id, "\u0003", submit=False)
        assert response.status_code == 200
        inject(client, session_id, "echo after-ctrl-c-$((2*2))")
        read_until(client, session_id, "after-ctrl-c-4")


def test_multibyte_input_is_written_as_utf8(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        response = inject(client, session_id, "echo café-✓")
        assert response.json()["accepted_bytes"] == len("echo café-✓".encode()) + 1
        text, _ = read_until(client, session_id, "café-✓\r\n")
        assert "café-✓" in text


def test_accepted_inject_is_logged_without_its_content(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with open_session(client) as (_websocket, session_id):
        with caplog.at_level("INFO", logger="uvicorn.error"):
            response = inject(client, session_id, "echo secret-content-$((1+1))")
    assert response.status_code == 200
    lines = [r.getMessage() for r in caplog.records if "inject" in r.getMessage()]
    assert len(lines) == 1
    assert session_id in lines[0]
    assert f"bytes={response.json()['accepted_bytes']}" in lines[0]
    assert "127.0.0.1" in lines[0]
    assert "secret-content" not in caplog.text


def test_unknown_session_is_refused_and_changes_nothing(client: TestClient) -> None:
    """R17: an unknown id is `404 unknown_session`; no session is created and the registry,
    reservations and output records are untouched."""
    module = terminal_module()
    with open_session(client) as (_websocket, session_id):
        before = (dict(module.SESSIONS), set(module.RESERVED), dict(module.OUTPUT_RECORDS))
        for bad in (UNKNOWN_ID, "A" * 32, "not-an-id", "0" * 31, "0" * 33, "x" * 200):
            assert_error(inject(client, bad, "echo hi"), 404, "unknown_session")
            assert_error(client.get(output_url(bad), headers=auth()), 404, "unknown_session")
        after = (dict(module.SESSIONS), set(module.RESERVED), dict(module.OUTPUT_RECORDS))
        assert after == before
        assert list(module.SESSIONS) == [session_id]


def test_session_leaves_the_api_when_its_websocket_closes(client: TestClient) -> None:
    module = terminal_module()
    with open_session(client) as (_websocket, session_id):
        assert inject(client, session_id, "true").status_code == 200
    assert wait_until(lambda: not module.SESSIONS)
    assert module.OUTPUT_RECORDS == {}
    assert_error(inject(client, session_id, "true"), 404, "unknown_session")
    assert_error(client.get(output_url(session_id), headers=auth()), 404, "unknown_session")
    assert client.get(LIST_PATH, headers=auth()).json() == {"sessions": []}


def test_write_error_is_409_session_ended_not_500(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = terminal_module()
    with open_session(client) as (_websocket, session_id):
        adapter = module.SESSIONS[session_id]

        def _broken_write(data: bytes) -> None:
            raise OSError(5, "Input/output error")

        # Without a master descriptor the API falls back to the adapter's own write().
        monkeypatch.setattr(adapter, "_master_fd", None)
        monkeypatch.setattr(adapter, "write", _broken_write)
        assert_error(inject(client, session_id, "echo hi"), 409, "session_ended")


def test_write_on_a_descriptor_the_kernel_refuses_is_409_session_ended(
    client: TestClient,
) -> None:
    """A real descriptor error (here EBADF, as when the shell side has gone) reaches the bounded
    writer's select and write and is answered 409, not 500."""
    module = terminal_module()
    with open_session(client) as (_websocket, session_id):
        adapter = module.SESSIONS[session_id]
        real_fd = adapter._master_fd  # noqa: SLF001
        try:
            adapter._master_fd = 10_000  # noqa: SLF001 - a descriptor number that is not open
            assert_error(inject(client, session_id, "echo hi"), 409, "session_ended")
        finally:
            adapter._master_fd = real_fd  # noqa: SLF001


def test_exited_shell_answers_409_on_inject_and_alive_false_on_read(client: TestClient) -> None:
    module = terminal_module()
    with open_session(client) as (_websocket, session_id):
        assert inject(client, session_id, "exit").status_code == 200
        assert wait_until(lambda: not module.SESSIONS[session_id].alive)
        assert_error(inject(client, session_id, "echo nope"), 409, "session_ended")

        def _listed_dead() -> bool:
            listing = client.get(LIST_PATH, headers=auth()).json()["sessions"]
            return listing[0]["alive"] is False

        assert wait_until(_listed_dead)
        body = client.get(output_url(session_id), headers=auth()).json()
        assert body["alive"] is False
        assert "echo nope" not in body["text"]


def test_tail_written_just_before_exit_is_buffered_and_sent(client: TestClient) -> None:
    """With capture on, the pump drains the shell's last bytes after exit, so they reach the HTTP
    reader and the browser both."""
    with open_session(client) as (websocket, session_id):
        inject(client, session_id, "echo tail-marker-$((3*3)); exit")
        collected = ""
        after = 0
        deadline = time.monotonic() + 8.0
        alive = True
        while alive and time.monotonic() < deadline:
            body = client.get(
                output_url(session_id), params={"after": after, "wait": 2}, headers=auth()
            ).json()
            collected += body["text"]
            after = body["next"]
            alive = body["alive"]
        assert alive is False
        assert "tail-marker-9\r\n" in collected
        total = body["next"]
        assert settle(client, session_id) == total
        whole = client.get(output_url(session_id), params={"limit": 262144}, headers=auth()).json()
        buffered = base64.b64decode(whole["data_base64"])
        assert len(buffered) == total
        assert receive_exactly(websocket, total) == buffered


# --- validation table (input) --------------------------------------------------------------------


def test_input_content_type_must_be_json(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        wrong_types = ("text/plain", "application/x-www-form-urlencoded", "application/jsonx")
        for content_type in wrong_types:
            response = client.post(
                input_url(session_id),
                content=b'{"input": "ls"}',
                headers={**auth(), "Content-Type": content_type},
            )
            assert_error(response, 415, "unsupported_media_type")
        response = client.post(input_url(session_id), content=b'{"input": "ls"}', headers=auth())
        assert_error(response, 415, "unsupported_media_type")
        ok = client.post(
            input_url(session_id),
            content=b'{"input": "true", "submit": true}',
            headers={**auth(), "Content-Type": "Application/JSON; charset=utf-8"},
        )
        assert ok.status_code == 200


def test_input_body_size_limits(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        headers = {**auth(), "Content-Type": "application/json"}
        too_big = b'{"input": "' + b"a" * 16384 + b'"}'
        assert_error(
            client.post(input_url(session_id), content=too_big, headers=headers),
            413,
            "payload_too_large",
        )
        # Over the limit and not JSON: the size is decided before the JSON is parsed.
        assert_error(
            client.post(input_url(session_id), content=b"{" * 16385, headers=headers),
            413,
            "payload_too_large",
        )
        # No Content-Length: a streamed body past the limit is refused as it is read.
        def _chunks() -> Iterator[bytes]:
            for _ in range(20):
                yield b" " * 1024

        assert_error(
            client.post(input_url(session_id), content=_chunks(), headers=headers),
            413,
            "payload_too_large",
        )
        # 4096 bytes is accepted without the carriage return, 4097 is not, and 4096 plus a
        # carriage return is not.
        assert inject(client, session_id, "#" + "a" * 4095, submit=False).status_code == 200
        assert_error(
            inject(client, session_id, "#" + "a" * 4096, submit=False), 413, "payload_too_large"
        )
        assert_error(
            inject(client, session_id, "#" + "a" * 4095, submit=True), 413, "payload_too_large"
        )
        # The limit is on encoded bytes: 2049 two-byte characters is 4098 bytes.
        assert_error(
            inject(client, session_id, "é" * 2049, submit=False), 413, "payload_too_large"
        )


@pytest.mark.parametrize(
    "body",
    [
        b"",
        b"not json",
        b"[]",
        b'"input"',
        b"42",
        b"null",
        b"{}",
        b'{"submit": true}',
        b'{"input": 5}',
        b'{"input": null}',
        b'{"input": ["ls"]}',
        b'{"input": ""}',
        b'{"input": "", "submit": false}',
        b'{"input": "ls", "submit": "yes"}',
        b'{"input": "ls", "submit": 1}',
        b'{"input": "ls", "submit": null}',
        b'{"input": "ls", "extra": 1}',
        b'{"input": "\\ud800"}',
        b"\xef\xbb\xbf" + b'{"input": "ls"}',
        b'{"input": "\xff"}',
    ],
)
def test_input_body_shape_is_422(client: TestClient, body: bytes) -> None:
    with open_session(client) as (_websocket, session_id):
        response = client.post(
            input_url(session_id),
            content=body,
            headers={**auth(), "Content-Type": "application/json"},
        )
        assert_error(response, 422, "invalid_request")


def test_empty_input_with_submit_true_sends_just_a_carriage_return(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        response = inject(client, session_id, "", submit=True)
        assert response.status_code == 200
        assert response.json()["accepted_bytes"] == 1


def test_submit_defaults_to_false(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        response = client.post(
            input_url(session_id), json={"input": "# no newline"}, headers=auth()
        )
        assert response.json()["accepted_bytes"] == len("# no newline")


# --- precedence: 403, 401, 404, 415, 413, 422, 409 ----------------------------------------------


def test_precedence_one_request_per_adjacent_pair(client: TestClient) -> None:
    app = main_module.app
    module = terminal_module()
    malformed = b"{not json"
    huge = b" " * 20000
    with open_session(client) as (_websocket, session_id):
        json_headers = {**auth(), "Content-Type": "application/json"}

        # 403 before 401: a non-loopback peer with no token.
        with TestClient(app, client=("10.1.2.3", 1)) as remote:
            assert_error(remote.get(output_url(session_id)), 403, "forbidden_peer")
            assert_error(
                remote.post(input_url(UNKNOWN_ID), content=malformed), 403, "forbidden_peer"
            )

        # 401 before 404, 415, 413 and 422: no token, whatever else is wrong.
        unauthenticated: list[tuple[str, dict[str, Any]]] = [
            (input_url(UNKNOWN_ID), {"content": huge}),
            (input_url(session_id), {"content": huge, "headers": {"Content-Type": "text/plain"}}),
            (input_url(session_id), {"content": malformed}),
        ]
        for path, kwargs in unauthenticated:
            assert_error(client.post(path, **kwargs), 401, "unauthorized")

        # 404 before 415, 413 and 422: right token, unknown session, everything else wrong.
        assert_error(
            client.post(
                input_url(UNKNOWN_ID),
                content=huge,
                headers={**auth(), "Content-Type": "text/plain"},
            ),
            404,
            "unknown_session",
        )
        assert_error(
            client.get(output_url(UNKNOWN_ID), params={"after": "x", "limit": "0"}, headers=auth()),
            404,
            "unknown_session",
        )

        # 415 before 413 and 422.
        assert_error(
            client.post(
                input_url(session_id),
                content=huge,
                headers={**auth(), "Content-Type": "text/plain"},
            ),
            415,
            "unsupported_media_type",
        )

        # 413 before 422: an oversized body that is also not JSON, and a decoded input over the
        # limit whose `submit` is the wrong type.
        assert_error(
            client.post(input_url(session_id), content=huge, headers=json_headers),
            413,
            "payload_too_large",
        )
        assert_error(
            client.post(
                input_url(session_id),
                content=json.dumps({"input": "a" * 5000, "submit": "yes"}).encode(),
                headers=json_headers,
            ),
            413,
            "payload_too_large",
        )

        # 422 before 409: a malformed body for a session whose shell has exited.
        assert inject(client, session_id, "exit").status_code == 200
        assert wait_until(lambda: not module.SESSIONS[session_id].alive)
        assert_error(
            client.post(input_url(session_id), content=malformed, headers=json_headers),
            422,
            "invalid_request",
        )
        assert_error(inject(client, session_id, "echo hi"), 409, "session_ended")


# --- GET /output: validation ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "query",
    [
        "after=-1",
        "after=abc",
        "after=1.5",
        "after=",
        "after=%2B1",
        "after=99999999999",
        "after=1&after=2",
        "limit=0",
        "limit=-5",
        "limit=262145",
        "limit=abc",
        "limit=1.5",
        "limit=1&limit=2",
        "wait=-1",
        "wait=10.5",
        "wait=11",
        "wait=nan",
        "wait=inf",
        "wait=abc",
        "wait=",
        "wait=1&wait=2",
    ],
)
def test_output_query_validation_is_422(client: TestClient, query: str) -> None:
    with open_session(client) as (_websocket, session_id):
        response = client.get(f"{output_url(session_id)}?{query}", headers=auth())
        assert_error(response, 422, "invalid_request")


def test_output_query_boundaries_and_unknown_parameters(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        total = settle(client, session_id)
        base = output_url(session_id)
        assert client.get(f"{base}?limit=1", headers=auth()).status_code == 200
        assert client.get(f"{base}?limit=262144", headers=auth()).status_code == 200
        assert client.get(f"{base}?wait=0", headers=auth()).status_code == 200
        assert client.get(f"{base}?wait=0.1", headers=auth()).status_code == 200
        assert client.get(f"{base}?unknown=anything&other=1", headers=auth()).status_code == 200
        assert client.get(f"{base}?after={total}", headers=auth()).status_code == 200
        beyond = client.get(f"{base}?after={total + 1}", headers=auth())
        assert_error(beyond, 422, "invalid_request")


# --- GET /output: reading ------------------------------------------------------------------------


def test_reading_is_non_destructive_and_idempotent(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        inject(client, session_id, "echo idem-$((8*8))")
        read_until(client, session_id, "idem-64")
        total = settle(client, session_id)
        first = client.get(output_url(session_id), params={"after": 0}, headers=auth()).json()
        second = client.get(output_url(session_id), params={"after": 0}, headers=auth()).json()
        assert first == second
        assert first["from"] == 0
        assert first["next"] == total
        assert first["truncated"] is False
        assert first["alive"] is True
        assert base64.b64decode(first["data_base64"]).decode() == first["text"]
        assert "idem-64" in first["text"]
        assert set(first) == {
            "session_id",
            "from",
            "next",
            "truncated",
            "alive",
            "text",
            "data_base64",
        }


def test_default_after_is_the_oldest_retained_offset_and_limit_bounds_the_bytes(
    client: TestClient,
) -> None:
    with open_session(client) as (_websocket, session_id):
        inject(client, session_id, "echo limit-$((9*9))")
        read_until(client, session_id, "limit-81")
        everything = client.get(output_url(session_id), headers=auth()).json()
        assert everything["from"] == 0
        first = client.get(output_url(session_id), params={"limit": 5}, headers=auth()).json()
        assert len(base64.b64decode(first["data_base64"])) == 5
        assert first["next"] == first["from"] + 5


def test_reader_resumes_from_next_and_sees_each_byte_once(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        inject(client, session_id, "seq 1 400")
        read_until(client, session_id, "400\r\n")
        total = settle(client, session_id)
        gathered = bytearray()
        after = 0
        while after < total:
            body = client.get(
                output_url(session_id), params={"after": after, "limit": 97}, headers=auth()
            ).json()
            assert body["from"] == after
            gathered.extend(base64.b64decode(body["data_base64"]))
            assert body["next"] > after
            after = body["next"]
        whole = client.get(output_url(session_id), params={"limit": 262144}, headers=auth()).json()
        assert bytes(gathered) == base64.b64decode(whole["data_base64"])


def test_after_older_than_the_ring_reports_truncated_from_the_oldest_byte(
    client: TestClient,
) -> None:
    """Fill the ring past 256 KiB and read from offset 0: `from` is the oldest retained offset and
    `truncated` is true."""
    ring = terminal_module().OUTPUT_RING_BYTES
    with open_session(client) as (_websocket, session_id):
        inject(client, session_id, "head -c 400000 /dev/zero | tr '\\0' 'x'; echo; echo ring-done")
        read_until(client, session_id, "ring-done", after=0, timeout=20.0)
        total = settle(client, session_id)
        assert total > ring
        body = client.get(output_url(session_id), params={"after": 0}, headers=auth()).json()
        assert body["truncated"] is True
        assert body["from"] == total - ring
        listing = client.get(LIST_PATH, headers=auth()).json()["sessions"][0]
        assert listing["output_start"] == total - ring
        assert listing["output_total"] == total
        recent = client.get(
            output_url(session_id), params={"after": total - ring}, headers=auth()
        ).json()
        assert recent["truncated"] is False


# --- the byte ring ------------------------------------------------------------------------------


def make_output() -> Any:
    return terminal_module().SessionOutput(shell=None)


def test_ring_tracks_absolute_offsets(build: Callable[..., FastAPI]) -> None:
    build()
    output = make_output()
    assert (output.start, output.total) == (0, 0)
    output.append(b"abc")
    output.append(b"def")
    assert (output.start, output.total, bytes(output.buffer)) == (0, 6, b"abcdef")


def test_ring_drops_the_oldest_bytes_beyond_256_kib(build: Callable[..., FastAPI]) -> None:
    build()
    module = terminal_module()
    assert module.OUTPUT_RING_BYTES == 262144
    output = make_output()
    output.append(b"a" * 200000)
    output.append(b"b" * 100000)
    assert output.total == 300000
    assert len(output.buffer) == 262144
    assert output.start == 300000 - 262144
    assert bytes(output.buffer[-100000:]) == b"b" * 100000
    assert bytes(output.buffer[: 200000 - output.start]) == b"a" * (200000 - output.start)
    output.append(b"c" * 300000)
    assert output.start == output.total - 262144
    assert set(output.buffer) == {ord("c")}


def test_select_chunk_clamps_to_the_ring(build: Callable[..., FastAPI]) -> None:
    build()
    output = make_output()
    output.append(b"x" * 300000)
    first, chunk = api()._select_chunk(output, 0, 65536, finished=False)  # noqa: SLF001
    assert first == output.start
    assert len(chunk) == 65536
    first, chunk = api()._select_chunk(output, 299990, 65536, finished=False)  # noqa: SLF001
    assert (first, len(chunk)) == (299990, 10)
    first, chunk = api()._select_chunk(output, 300000, 65536, finished=False)  # noqa: SLF001
    assert (first, chunk) == (300000, b"")


def test_next_never_falls_inside_a_multibyte_sequence_while_the_session_is_live(
    build: Callable[..., FastAPI],
) -> None:
    build()
    select = api()._select_chunk  # noqa: SLF001
    output = make_output()
    snowman = "☃".encode()  # three bytes
    output.append(b"ab" + snowman + snowman[:2])  # a complete character then a partial one
    first, chunk = select(output, 0, 100, finished=False)
    assert (first, chunk) == (0, b"ab" + snowman)
    # The limit lands inside the first character: the chunk stops before it.
    first, chunk = select(output, 0, 4, finished=False)
    assert chunk == b"ab"
    # Only a partial character is available: nothing is returned until the rest arrives.
    first, chunk = select(output, 5, 100, finished=False)
    assert (first, chunk) == (5, b"")
    output.append(snowman[2:])
    first, chunk = select(output, 5, 100, finished=False)
    assert chunk == snowman
    # Once the session has ended the partial tail is returned as it is.
    partial = make_output()
    partial.append(b"z" + snowman[:2])
    assert select(partial, 0, 100, finished=True)[1] == b"z" + snowman[:2]
    # A limit smaller than the sequence cannot be honoured without cutting it; the limit wins so
    # that a reader can still advance.
    only = make_output()
    only.append(snowman + b"tail")
    assert select(only, 0, 2, finished=False)[1] == snowman[:2]


def test_successive_text_values_concatenate_cleanly_across_a_split(
    build: Callable[..., FastAPI],
) -> None:
    build()
    select = api()._select_chunk  # noqa: SLF001
    decode = api()._decode_text  # noqa: SLF001
    output = make_output()
    payload = ("héllo ✓ wörld " * 40).encode()
    output.append(payload)
    text = ""
    after = 0
    while after < output.total:
        first, chunk = select(output, after, 7, finished=False)
        assert chunk
        text += decode(chunk)
        after = first + len(chunk)
    assert text == payload.decode()
    assert "�" not in text


def test_text_drops_leading_continuation_bytes_but_base64_is_exact(
    build: Callable[..., FastAPI],
) -> None:
    build()
    decode = api()._decode_text  # noqa: SLF001
    snowman = "☃".encode()
    assert decode(snowman[1:] + b"ok") == "ok"
    assert decode(snowman[2:] + b"ok") == "ok"
    assert decode(b"\x80\x80\x80\x80ok") == "�ok"  # only three are dropped
    assert decode(b"plain") == "plain"
    assert decode(b"a\xffb") == "a�b"
    assert decode(b"\x1b[31mred\x1b[0m") == "\x1b[31mred\x1b[0m"  # escape sequences stay


def test_after_in_the_middle_of_a_character_gives_exact_bytes_and_clean_text(
    client: TestClient,
) -> None:
    with open_session(client) as (_websocket, session_id):
        inject(client, session_id, "printf 'mid-\\xe2\\x9c\\x93-end\\n'")
        read_until(client, session_id, "mid-✓-end")
        everything = client.get(output_url(session_id), params={"after": 0}, headers=auth()).json()
        data = base64.b64decode(everything["data_base64"])
        position = data.rindex("✓".encode())
        body = client.get(
            output_url(session_id), params={"after": position + 1}, headers=auth()
        ).json()
        assert body["from"] == position + 1
        assert base64.b64decode(body["data_base64"]) == data[position + 1 :]
        assert body["text"].startswith("-end")


# --- long poll ----------------------------------------------------------------------------------


def test_wait_returns_immediately_when_bytes_are_available(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        inject(client, session_id, "echo ready-$((5*5))")
        read_until(client, session_id, "ready-25")
        started = time.monotonic()
        body = client.get(
            output_url(session_id), params={"after": 0, "wait": 10}, headers=auth()
        ).json()
        assert time.monotonic() - started < 2.0
        assert body["text"]


def test_wait_times_out_with_an_empty_read_when_nothing_arrives(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        total = settle(client, session_id)
        started = time.monotonic()
        response = client.get(
            output_url(session_id), params={"after": total, "wait": 0.6}, headers=auth()
        )
        elapsed = time.monotonic() - started
        body = response.json()
        assert response.status_code == 200
        assert 0.5 <= elapsed < 5.0
        assert body["text"] == "" and body["data_base64"] == ""
        assert body["from"] == body["next"] == total
        assert body["alive"] is True


def test_waiting_read_wakes_when_the_injection_produces_output(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        total = settle(client, session_id)

        def _long_poll() -> tuple[float, dict[str, Any]]:
            started = time.monotonic()
            reply = client.get(
                output_url(session_id), params={"after": total, "wait": 10}, headers=auth()
            )
            return time.monotonic() - started, reply.json()

        with ThreadPoolExecutor(max_workers=1) as pool:
            pending = pool.submit(_long_poll)
            time.sleep(0.5)
            assert not pending.done(), "the long poll returned before anything was injected"
            inject(client, session_id, "echo wake-$((4*4))")
            elapsed, body = pending.result(timeout=15)
        assert elapsed < 8.0, "the long poll waited out its full wait instead of waking"
        assert body["from"] == total
        assert body["next"] > total
        assert body["text"]


def test_waiting_read_wakes_when_the_session_ends(client: TestClient) -> None:
    with open_session(client) as (websocket, session_id):
        total = settle(client, session_id)
        # Only the exit itself produces output; read until the stream reports it has ended.
        results: list[dict[str, Any]] = []

        def _poll_until_ended() -> None:
            after = total
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                body = client.get(
                    output_url(session_id), params={"after": after, "wait": 10}, headers=auth()
                ).json()
                results.append(body)
                after = body["next"]
                if not body["alive"]:
                    return

        worker = threading.Thread(target=_poll_until_ended, daemon=True)
        worker.start()
        time.sleep(0.3)
        inject(client, session_id, "exit")
        worker.join(15)
        assert not worker.is_alive()
        assert results[-1]["alive"] is False
        del websocket


def test_waiting_read_wakes_when_the_websocket_closes(client: TestClient) -> None:
    holder: dict[str, Any] = {}

    def _long_poll(session_id: str, total: int) -> None:
        started = time.monotonic()
        reply = client.get(
            output_url(session_id), params={"after": total, "wait": 10}, headers=auth()
        )
        holder["elapsed"] = time.monotonic() - started
        holder["response"] = reply

    with ThreadPoolExecutor(max_workers=1) as pool:
        with open_session(client) as (_websocket, session_id):
            total = settle(client, session_id)
            pending = pool.submit(_long_poll, session_id, total)
            time.sleep(0.4)
        pending.result(timeout=15)
    assert holder["elapsed"] < 8.0
    response = holder["response"]
    assert response.status_code == 200
    assert response.json()["alive"] is False
    assert_error(client.get(output_url(session_id), headers=auth()), 404, "unknown_session")


# --- R18: the browser loses nothing --------------------------------------------------------------


def test_browser_receives_every_byte_the_buffer_holds_while_http_reads(client: TestClient) -> None:
    """R18: adapter reads are destructive, so only the pump may read the adapter. An HTTP reader
    polling in small chunks while output flows must leave the websocket client with exactly the
    bytes the buffer holds."""
    with open_session(client) as (websocket, session_id):
        inject(client, session_id, "seq 1 3000")
        gathered = bytearray()
        after = 0
        deadline = time.monotonic() + 15.0
        while b"3000\r\n" not in gathered and time.monotonic() < deadline:
            body = client.get(
                output_url(session_id),
                params={"after": after, "limit": 211, "wait": 1},
                headers=auth(),
            ).json()
            gathered.extend(base64.b64decode(body["data_base64"]))
            after = body["next"]
        assert b"3000\r\n" in gathered
        total = settle(client, session_id)
        whole = client.get(
            output_url(session_id), params={"after": 0, "limit": 262144}, headers=auth()
        ).json()
        buffered = base64.b64decode(whole["data_base64"])
        assert len(buffered) == total
        assert buffered.startswith(bytes(gathered))
        received = receive_exactly(websocket, total)
        assert received == buffered
        # Every number the shell printed reached the browser.
        for number in (1, 1500, 3000):
            assert f"\r\n{number}\r\n".encode() in received or number == 1


def test_two_http_readers_see_the_same_bytes(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        inject(client, session_id, "echo twin-$((7*7))")
        read_until(client, session_id, "twin-49")
        total = settle(client, session_id)
        a = client.get(output_url(session_id), params={"after": 0}, headers=auth()).json()
        b = client.get(output_url(session_id), params={"after": 0}, headers=auth()).json()
        assert a == b and a["next"] == total


# --- the websocket path is unchanged -------------------------------------------------------------


def test_websocket_round_trip_and_resize_are_unchanged_with_both_flags(client: TestClient) -> None:
    with client.websocket_connect(WS_PATH) as websocket:
        websocket.send_text(json.dumps({"type": "resize", "cols": 132, "rows": 51}))
        websocket.send_text("not json")
        websocket.send_bytes(b"stty size; echo ws-$((6*7))-both-flags\n")
        output = b""
        deadline = time.monotonic() + 5.0
        while b"ws-42-both-flags" not in output and time.monotonic() < deadline:
            output += websocket.receive_bytes()
    assert b"51 132" in output
    assert b"ws-42-both-flags" in output
    assert b"not json" not in output


def test_session_cap_and_refusals_are_unchanged_with_both_flags(client: TestClient) -> None:
    module = terminal_module()
    with contextlib.ExitStack() as stack:
        for _ in range(module.MAX_CONCURRENT_SESSIONS):
            stack.enter_context(client.websocket_connect(WS_PATH))
        assert wait_until(lambda: len(module.OUTPUT_RECORDS) == module.MAX_CONCURRENT_SESSIONS)
        with client.websocket_connect(WS_PATH) as refused:
            from starlette.websockets import WebSocketDisconnect

            with pytest.raises(WebSocketDisconnect) as exc_info:
                refused.receive_bytes()
        assert exc_info.value.code == module.SESSION_LIMIT_CLOSE_CODE
        assert exc_info.value.reason == module.SESSION_LIMIT_CLOSE_REASON
        assert len(client.get(LIST_PATH, headers=auth()).json()["sessions"]) == 6
    assert wait_until(lambda: not module.SESSIONS and not module.OUTPUT_RECORDS)


def test_refused_shell_request_leaves_no_output_record(client: TestClient) -> None:
    module = terminal_module()
    from starlette.websockets import WebSocketDisconnect

    with client.websocket_connect(f"{WS_PATH}?shell=/bin/zsh") as websocket:
        websocket.receive_text()
        with pytest.raises(WebSocketDisconnect):
            websocket.receive_text()
    assert wait_until(lambda: not module.RESERVED)
    assert module.SESSIONS == {}
    assert module.OUTPUT_RECORDS == {}


# --- the idle bound ------------------------------------------------------------------------------


def test_ceiling_rule_is_exact(
    build: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The rule the idle loop applies at a timeout, decided without a clock."""
    build()
    module = terminal_module()
    rule = module._inject_extends_idle_bound  # noqa: SLF001
    output = module.SessionOutput(shell=None, last_frame=1000.0)
    idle = 300.0
    # No inject was ever accepted: the timeout reaps.
    assert rule(output, idle, 1300.0) is False
    # An inject inside the idle window extends.
    output.last_inject = 1200.0
    assert rule(output, idle, 1300.0) is True
    # An inject older than the idle window does not.
    output.last_inject = 900.0
    assert rule(output, idle, 1300.0) is False
    # An inject inside the window extends only while the last frame is under the ceiling.
    output.last_inject = 4500.0
    assert module.TERMINAL_API_INJECT_CEILING_SECONDS == 3600
    assert rule(output, idle, 4599.0) is True  # 3599 s since the last frame
    assert rule(output, idle, 4600.0) is False  # 3600 s since the last frame
    output.last_frame = 4400.0  # a websocket frame resets the ceiling's clock
    assert rule(output, idle, 4600.0) is True
    monkeypatch.setattr(module, "TERMINAL_API_INJECT_CEILING_SECONDS", 100.0)
    assert rule(output, idle, 4600.0) is False


def test_a_read_does_not_extend_the_idle_bound(
    build: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A poller of the output route must not keep a dead-peer shell and its cap slot alive: with
    reads arriving continuously the session is still reaped at the idle bound."""
    monkeypatch.setenv(IDLE_TIMEOUT_ENV_VAR, "0.6")
    app = build()
    module = terminal_module()
    with TestClient(app, client=LOOPBACK_PEER) as client:
        websocket_cm = client.websocket_connect(WS_PATH)
        websocket_cm.__enter__()
        try:
            assert wait_until(lambda: len(module.SESSIONS) == 1)
            session_id = next(iter(module.SESSIONS))
            started = time.monotonic()
            gone_after: float | None = None
            while time.monotonic() - started < 6.0:
                response = client.get(
                    output_url(session_id), params={"wait": 0.2}, headers=auth()
                )
                if response.status_code == 404:
                    gone_after = time.monotonic() - started
                    break
                assert response.status_code == 200
            assert gone_after is not None, "continuous reads kept the session alive"
            assert gone_after < 4.0
        finally:
            with contextlib.suppress(Exception):
                websocket_cm.__exit__(None, None, None)


def test_an_accepted_inject_extends_the_idle_bound_once_per_window(
    build: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    """With a 1.0 s bound, an inject at ~0.3 s keeps the session past 1.0 s (the first timeout is
    ignored), and with no further inject the next timeout reaps it."""
    monkeypatch.setenv(IDLE_TIMEOUT_ENV_VAR, "1.0")
    app = build()
    module = terminal_module()
    with TestClient(app, client=LOOPBACK_PEER) as client:
        websocket_cm = client.websocket_connect(WS_PATH)
        websocket_cm.__enter__()
        try:
            assert wait_until(lambda: len(module.SESSIONS) == 1)
            session_id = next(iter(module.SESSIONS))
            started = time.monotonic()
            time.sleep(0.3)
            assert inject(client, session_id, "true").status_code == 200
            time.sleep(max(0.0, 1.5 - (time.monotonic() - started)))
            assert session_id in module.SESSIONS, "the accepted inject did not extend the bound"
            assert wait_until(lambda: session_id not in module.SESSIONS, timeout=6.0)
            assert module.OUTPUT_RECORDS == {}
        finally:
            with contextlib.suppress(Exception):
                websocket_cm.__exit__(None, None, None)


def test_idle_loop_ignores_the_api_when_capture_is_off(
    build: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Under the first flag alone the idle loop is the one it always was: a timeout reaps."""
    monkeypatch.setenv(IDLE_TIMEOUT_ENV_VAR, "0.5")
    app = build(terminal="1", api=None)
    module = terminal_module()
    with TestClient(app) as client:
        websocket_cm = client.websocket_connect(WS_PATH)
        websocket_cm.__enter__()
        try:
            assert wait_until(lambda: len(module.SESSIONS) == 1)
            assert wait_until(lambda: not module.SESSIONS, timeout=6.0)
        finally:
            with contextlib.suppress(Exception):
                websocket_cm.__exit__(None, None, None)


# --- review round: bounded writes, teardown, bodies, directories, dead pump ---------------------


class FakeAdapter:
    """A stand-in for a shell with no PTY descriptor, so the API uses the adapter's own write()."""

    def __init__(self, write: Callable[[bytes], object] | None = None) -> None:
        self.alive = True
        self.writes: list[bytes] = []
        self._write = write

    def write(self, data: bytes) -> None:
        if self._write is not None:
            self._write(data)
        self.writes.append(data)

    def read(self, size: int = 4096, timeout: float | None = None) -> bytes:
        return b""

    def close(self) -> None:
        self.alive = False


def register_fake_session(
    monkeypatch: pytest.MonkeyPatch, adapter: FakeAdapter, session_id: str = "ab" * 16
) -> tuple[str, Any]:
    module = terminal_module()
    output = module.SessionOutput(shell=None)
    monkeypatch.setitem(module.SESSIONS, session_id, adapter)
    monkeypatch.setitem(module.OUTPUT_RECORDS, session_id, output)
    return session_id, output


def test_inject_into_a_shell_that_is_not_reading_is_bounded(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Security review F01. A foreground command that is not reading input stops the pty accepting
    bytes once the line discipline's buffer is full. Every inject must still answer within the
    deadline (a partial write is reported as such, a write that accepts nothing is 409
    `write_timeout`), and the shell must be gone once the websocket closes."""
    monkeypatch.setattr(api(), "INJECT_WRITE_DEADLINE_SECONDS", 1.0)
    module = terminal_module()
    results: list[tuple[int, Any]] = []
    with open_session(client) as (_websocket, session_id):
        adapter = module.SESSIONS[session_id]
        assert inject(client, session_id, "sleep 60").status_code == 200
        time.sleep(0.5)
        for _ in range(6):
            started = time.monotonic()
            response = client.post(
                input_url(session_id),
                json={"input": ("x" * 79 + "\r") * 50, "submit": False},
                headers=auth(),
            )
            assert time.monotonic() - started < 4.0, "an inject outlived its deadline"
            results.append((response.status_code, response.json()))
    assert any(
        status == 409 and body["error"]["code"] == "write_timeout" for status, body in results
    ), results
    assert any(
        (status == 200 and body["accepted_bytes"] < 4000)
        or (status == 409 and body["error"]["code"] == "write_timeout")
        for status, body in results
    )
    for status, body in results:
        if status == 409:
            assert_error_body(body, "write_timeout")
    assert wait_until(lambda: not adapter.alive, timeout=8.0), "the shell outlived its session"
    assert wait_until(lambda: not module.SESSIONS)


def assert_error_body(body: dict[str, Any], code: str) -> None:
    assert set(body) == {"error"}
    assert body["error"]["code"] == code


def test_descriptor_is_blocking_again_after_a_bounded_write(client: TestClient) -> None:
    module = terminal_module()
    with open_session(client) as (_websocket, session_id):
        adapter = module.SESSIONS[session_id]
        assert inject(client, session_id, "true").status_code == 200
        assert os.get_blocking(adapter._master_fd) is True  # noqa: SLF001


def test_adapter_without_a_descriptor_is_bounded_by_the_wait(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An adapter the API cannot write non-blockingly (ConPTY) is still answered at the deadline:
    409 `write_timeout`, the inject lock is released, and the next request is not queued behind it.
    The stuck thread itself cannot be freed; that is the documented limit of the fallback."""
    release = threading.Event()
    adapter = FakeAdapter(write=lambda data: release.wait(10))
    session_id, _output = register_fake_session(monkeypatch, adapter)
    monkeypatch.setattr(api(), "INJECT_WRITE_DEADLINE_SECONDS", 0.3)
    monkeypatch.setattr(api(), "INJECT_WRITE_THREAD_GRACE_SECONDS", 0.3)
    try:
        started = time.monotonic()
        assert_error(inject(client, session_id, "x", submit=False), 409, "write_timeout")
        assert time.monotonic() - started < 3.0
        started = time.monotonic()
        assert_error(inject(client, session_id, "y", submit=False), 409, "write_timeout")
        assert time.monotonic() - started < 3.0
    finally:
        release.set()


def test_partial_write_reports_the_bytes_actually_accepted(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = terminal_module()
    with open_session(client) as (_websocket, session_id):
        adapter = module.SESSIONS[session_id]
        monkeypatch.setattr(api(), "INJECT_WRITE_DEADLINE_SECONDS", 0.5)
        real_write = os.write
        calls: list[int] = []

        def _short_write(fd: int, data: Any) -> int:
            # Accept 3 bytes on the first call, then report the pty as full.
            if fd == adapter._master_fd and not calls:  # noqa: SLF001
                calls.append(1)
                return real_write(fd, bytes(data[:3]))
            if fd == adapter._master_fd:  # noqa: SLF001
                raise BlockingIOError
            return real_write(fd, data)

        monkeypatch.setattr(api().os, "write", _short_write)
        response = inject(client, session_id, "# abcdefgh", submit=False)
        monkeypatch.setattr(api().os, "write", real_write)
        assert response.status_code == 200
        assert response.json()["accepted_bytes"] == 3


def test_teardown_waits_for_an_inflight_inject_before_closing_the_adapter(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Security review F02. While an inject holds the session's write lock the adapter must not be
    closed (its descriptor number could be reused under the write thread); it closes as soon as the
    lock is released."""
    module = terminal_module()
    with open_session(client) as (websocket, session_id):
        output = module.OUTPUT_RECORDS[session_id]
        adapter = module.SESSIONS[session_id]
        closed = threading.Event()
        original_close = adapter.close

        def _recording_close() -> None:
            closed.set()
            original_close()

        monkeypatch.setattr(adapter, "close", _recording_close)
        portal = client.portal
        assert portal is not None
        portal.call(output.write_lock.acquire)
        websocket.close()
        time.sleep(0.8)
        assert not closed.is_set(), "the adapter was closed while a write was in flight"
        portal.call(output.write_lock.release)
        assert closed.wait(5.0)
    assert wait_until(lambda: not module.SESSIONS)


def test_queued_inject_refuses_once_the_session_is_ending(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = FakeAdapter()
    session_id, output = register_fake_session(monkeypatch, adapter)
    output.ended = True
    assert_error(inject(client, session_id, "x"), 409, "session_ended")
    assert adapter.writes == []


# --- request bodies that stall or vanish ---------------------------------------------------------


async def drive_asgi(
    path: str,
    headers: dict[str, str],
    script: list[dict[str, Any]],
    *,
    timeout: float = 8.0,
) -> tuple[int, dict[str, Any]]:
    """Call the ASGI app directly with a scripted `receive`; after the script it stalls forever."""
    sent: list[dict[str, Any]] = []
    pending = iter(script)

    async def receive() -> MutableMapping[str, Any]:
        try:
            return next(pending)
        except StopIteration:
            await asyncio.sleep(3600)
            raise AssertionError("unreachable") from None

    async def send(message: MutableMapping[str, Any]) -> None:
        sent.append(dict(message))

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        "client": ("127.0.0.1", 50000),
        "server": ("testserver", 80),
        "scheme": "http",
        "root_path": "",
    }
    await asyncio.wait_for(main_module.app(scope, receive, send), timeout)
    status = next(m["status"] for m in sent if m["type"] == "http.response.start")
    body = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
    return status, json.loads(body)


def _body_headers() -> dict[str, str]:
    return {**auth(), "Content-Type": "application/json", "Content-Length": "100"}


def test_stalled_request_body_is_answered_at_the_deadline(
    build: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Security review F03: a body that never completes is 422, not an open connection."""
    build()
    monkeypatch.setattr(api(), "BODY_READ_DEADLINE_SECONDS", 0.3)
    adapter = FakeAdapter()
    session_id, _output = register_fake_session(monkeypatch, adapter)
    started = time.monotonic()
    status, body = asyncio.run(
        drive_asgi(
            input_url(session_id),
            _body_headers(),
            [{"type": "http.request", "body": b'{"input"', "more_body": True}],
        )
    )
    assert time.monotonic() - started < 3.0
    assert status == 422
    assert_error_body(body, "invalid_request")
    assert adapter.writes == []


def test_disconnecting_client_during_the_body_is_not_a_server_error(
    build: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    build()
    adapter = FakeAdapter()
    session_id, _output = register_fake_session(monkeypatch, adapter)
    with caplog.at_level("ERROR"):
        status, body = asyncio.run(
            drive_asgi(
                input_url(session_id),
                _body_headers(),
                [
                    {"type": "http.request", "body": b'{"input"', "more_body": True},
                    {"type": "http.disconnect"},
                ],
            )
        )
    assert status == 422
    assert_error_body(body, "invalid_request")
    assert "ClientDisconnect" not in caplog.text
    assert adapter.writes == []


def test_chunked_body_without_content_length_is_read_and_accepted(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = FakeAdapter()
    session_id, _output = register_fake_session(monkeypatch, adapter)

    def _chunks() -> Iterator[bytes]:
        yield b'{"input": "chun'
        yield b'ked", "submit": true}'

    response = client.post(
        input_url(session_id),
        content=_chunks(),
        headers={**auth(), "Content-Type": "application/json"},
    )
    assert response.status_code == 200, response.text
    assert adapter.writes == [b"chunked\r"]


def test_concurrent_injects_are_written_one_at_a_time(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The per-session lock: two simultaneous requests never overlap inside `write()`."""
    spans: list[tuple[float, float]] = []

    def _slow_write(data: bytes) -> None:
        start = time.monotonic()
        time.sleep(0.3)
        spans.append((start, time.monotonic()))

    adapter = FakeAdapter(write=_slow_write)
    session_id, _output = register_fake_session(monkeypatch, adapter)
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(inject, client, session_id, f"msg-{n}") for n in range(3)]
        responses = [future.result(timeout=15) for future in futures]
    assert [r.status_code for r in responses] == [200, 200, 200]
    assert len(spans) == 3
    spans.sort()
    for earlier, later in zip(spans, spans[1:], strict=False):
        assert earlier[1] <= later[0], "two writes overlapped"
    assert sorted(adapter.writes) == [b"msg-0\r", b"msg-1\r", b"msg-2\r"]


# --- the token directory's parent ---------------------------------------------------------------


def test_parent_directory_that_is_a_symlink_is_refused(
    build: Callable[..., FastAPI], tmp_path: Path
) -> None:
    build()
    module = api()
    real = tmp_path / "elsewhere"
    real.mkdir()
    home = tmp_path / "linked-home"
    home.mkdir()
    (home / ".d-system").symlink_to(real)
    with pytest.raises(module.TokenFileError, match="symlink"):
        module.write_token_file(module.token_file_path(tmp_path / "repo", home), "t")
    assert list(real.iterdir()) == []


def test_parent_directory_owned_by_another_user_is_refused(
    build: Callable[..., FastAPI], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    build()
    module = api()
    home = tmp_path / "foreign-home"
    (home / ".d-system").mkdir(parents=True)
    monkeypatch.setattr(os, "geteuid", lambda: os.stat(home).st_uid + 1)
    with pytest.raises(module.TokenFileError, match=r"\.d-system is not owned"):
        module.write_token_file(module.token_file_path(tmp_path / "repo", home), "t")


def test_parent_directory_keeps_its_mode(build: Callable[..., FastAPI], tmp_path: Path) -> None:
    """Only the leaf is forced to 0700; a parent the user already keeps is left as it is."""
    build()
    module = api()
    home = tmp_path / "shared-home"
    (home / ".d-system").mkdir(parents=True)
    (home / ".d-system").chmod(0o755)
    path = module.token_file_path(tmp_path / "repo", home)
    module.write_token_file(path, "t")
    assert stat.S_IMODE((home / ".d-system").stat().st_mode) == 0o755
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


# --- a pump that stops for a reason other than the shell exiting ----------------------------------


class ScriptedAdapter:
    """Reads come from a script; `alive` turns false once `exit_after` reads have been made."""

    def __init__(self, reads: list[bytes], exit_after: int | None) -> None:
        self._reads = list(reads)
        self._count = 0
        self._exit_after = exit_after

    @property
    def alive(self) -> bool:
        return self._exit_after is None or self._count < self._exit_after

    def read(self, size: int = 4096, timeout: float | None = None) -> bytes:
        self._count += 1
        return self._reads.pop(0) if self._reads else b""


class RecordingWebSocket:
    def __init__(self, *, fail: bool = False, delay: float = 0.0) -> None:
        self.sent: list[bytes] = []
        self._fail = fail
        self._delay = delay

    async def send_bytes(self, data: bytes) -> None:
        if self._fail:
            raise ConnectionError("peer gone")
        if self._delay:
            await asyncio.sleep(self._delay)
        self.sent.append(data)


def test_ring_holds_the_chunk_when_the_send_raises(build: Callable[..., FastAPI]) -> None:
    """ADR-030 section 5: append first, so a failed send cannot drop bytes from the ring."""
    build()
    module = terminal_module()
    output = module.SessionOutput(shell=None)
    adapter = ScriptedAdapter([b"kept-in-the-ring"], exit_after=None)
    websocket = RecordingWebSocket(fail=True)
    with pytest.raises(ConnectionError):
        asyncio.run(module._pump_adapter_to_websocket(adapter, websocket, output))  # noqa: SLF001
    assert bytes(output.buffer) == b"kept-in-the-ring"
    assert output.total == len(b"kept-in-the-ring")
    assert output.pump_done is True


def test_pump_that_failed_makes_the_session_read_dead(build: Callable[..., FastAPI]) -> None:
    build()
    module = terminal_module()
    output = module.SessionOutput(shell=None)
    adapter = ScriptedAdapter([b"x"], exit_after=None)  # the shell itself is still running
    with pytest.raises(ConnectionError):
        asyncio.run(
            module._pump_adapter_to_websocket(  # noqa: SLF001
                adapter, RecordingWebSocket(fail=True), output
            )
        )
    assert adapter.alive is True
    assert api()._stream_alive(adapter, output) is False  # noqa: SLF001


def test_inject_and_read_after_the_pump_died(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Security review F07 and judge F03: no output will be captured, so the session reads
    `alive: false`, an inject is 409 and nothing is written."""
    adapter = FakeAdapter()
    session_id, output = register_fake_session(monkeypatch, adapter)
    assert inject(client, session_id, "before").status_code == 200
    output.pump_done = True
    assert_error(inject(client, session_id, "after"), 409, "session_ended")
    assert adapter.writes == [b"before\r"]
    body = client.get(output_url(session_id), headers=auth()).json()
    assert body["alive"] is False
    listing = client.get(LIST_PATH, headers=auth()).json()["sessions"]
    assert listing[0]["alive"] is False


def test_drain_collects_the_tail_while_the_pump_is_held_in_a_send(
    build: Callable[..., FastAPI],
) -> None:
    """The shell exits while the pump is still awaiting the send of its last chunk; the loop then
    ends, and only the drain still reads (and sends) what the shell wrote just before it exited."""
    build()
    module = terminal_module()
    output = module.SessionOutput(shell=None)
    adapter = ScriptedAdapter([b"first|", b"tail-one|", b"tail-two"], exit_after=1)
    websocket = RecordingWebSocket(delay=0.2)
    asyncio.run(module._pump_adapter_to_websocket(adapter, websocket, output))  # noqa: SLF001
    assert bytes(output.buffer) == b"first|tail-one|tail-two"
    assert b"".join(websocket.sent) == b"first|tail-one|tail-two"
    assert output.pump_done is True


# --- foreign origins, forwarded headers, the token's reach ----------------------------------------


def test_foreign_origin_and_host_need_the_token_and_get_no_cors_grant(
    client: TestClient,
) -> None:
    evil = {"Origin": "http://evil.example", "Host": "evil.example:8019"}
    assert_error(client.get(LIST_PATH, headers=evil), 401, "unauthorized")
    # With the token the request is served: the token is the boundary, not the Origin or Host.
    assert client.get(LIST_PATH, headers={**evil, **auth()}).status_code == 200
    preflight = client.options(
        LIST_PATH,
        headers={
            "Origin": "http://evil.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert "access-control-allow-origin" not in preflight.headers
    stage = client.options(
        LIST_PATH,
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert stage.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_forwarded_for_header_is_never_trusted(build: Callable[..., FastAPI]) -> None:
    app = build()
    token = auth()
    with TestClient(app, client=("127.0.0.1", 1)) as local:
        response = local.get(LIST_PATH, headers={**token, "X-Forwarded-For": "8.8.8.8"})
        assert response.status_code == 200
    with TestClient(app, client=("10.1.2.3", 1)) as remote:
        response = remote.get(LIST_PATH, headers={**token, "X-Forwarded-For": "127.0.0.1"})
        assert_error(response, 403, "forbidden_peer")


def test_token_is_not_in_the_environment_of_the_server_or_a_shell(client: TestClient) -> None:
    token = api().TOKEN.encode()
    module = terminal_module()
    with open_session(client) as (_websocket, session_id):
        pid = module.SESSIONS[session_id]._process.pid  # noqa: SLF001
        shell_environment = Path(f"/proc/{pid}/environ").read_bytes()
    assert token not in shell_environment
    assert token not in Path("/proc/self/environ").read_bytes()
    assert token not in " ".join(os.environ.values()).encode()


# --- the idle bound: a websocket frame resets the ceiling's clock -------------------------------


def test_websocket_frame_resets_the_ceiling_clock(
    build: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Idle bound 1.0 s, ceiling 1.9 s. An inject at ~0.3 s extends past the first timeout; a frame
    at ~1.4 s restarts both clocks; an inject at ~2.0 s then extends the timeout at ~2.4 s, which is
    past 1.9 s since the session started but only ~1.0 s since the frame. Without the frame's reset
    the session would be reaped at ~2.4 s."""
    monkeypatch.setenv(IDLE_TIMEOUT_ENV_VAR, "1.0")
    app = build()
    module = terminal_module()
    monkeypatch.setattr(module, "TERMINAL_API_INJECT_CEILING_SECONDS", 1.9)
    with TestClient(app, client=LOOPBACK_PEER) as client:
        websocket_cm = client.websocket_connect(WS_PATH)
        websocket = websocket_cm.__enter__()
        try:
            assert wait_until(lambda: len(module.SESSIONS) == 1)
            session_id = next(iter(module.SESSIONS))
            started = time.monotonic()

            def _sleep_until(offset: float) -> None:
                time.sleep(max(0.0, offset - (time.monotonic() - started)))

            _sleep_until(0.3)
            assert inject(client, session_id, "true").status_code == 200
            _sleep_until(1.4)
            websocket.send_text(json.dumps({"type": "resize", "cols": 100, "rows": 30}))
            _sleep_until(2.0)
            assert inject(client, session_id, "true").status_code == 200
            _sleep_until(2.9)
            assert session_id in module.SESSIONS, "the frame did not reset the ceiling clock"
            assert wait_until(lambda: session_id not in module.SESSIONS, timeout=8.0)
        finally:
            with contextlib.suppress(Exception):
                websocket_cm.__exit__(None, None, None)


# --- query forms and import safety ----------------------------------------------------------------


@pytest.mark.parametrize("wait", [".5", "1e1", "+1", "0", "10", "10.0", "0.25", "00.5"])
def test_wait_accepts_the_forms_float_reads(client: TestClient, wait: str) -> None:
    with open_session(client) as (_websocket, session_id):
        response = client.get(f"{output_url(session_id)}?after=0&wait={wait}", headers=auth())
        assert response.status_code == 200, (wait, response.text)


@pytest.mark.parametrize("wait", ["1_0", "١", "1e2", "1e-400x", "infinity", "-0.1", "0x1"])
def test_wait_still_refuses_non_finite_out_of_range_and_non_ascii(
    client: TestClient, wait: str
) -> None:
    with open_session(client) as (_websocket, session_id):
        response = client.get(output_url(session_id), params={"wait": wait}, headers=auth())
        assert_error(response, 422, "invalid_request")


def test_long_run_of_leading_zeros_in_after_is_accepted(client: TestClient) -> None:
    with open_session(client) as (_websocket, session_id):
        response = client.get(f"{output_url(session_id)}?after={'0' * 40}", headers=auth())
        assert response.status_code == 200
        assert response.json()["from"] == 0


def test_collecting_the_tests_with_both_flags_exported_writes_no_token(tmp_path: Path) -> None:
    """Review of ADR-030 tests (adversary F01): importing the app with both flags exported rotates
    the token of a running server. `test/conftest.py` clears the second flag before the test
    modules import `src.main`, so a collection run under exported flags writes nothing."""
    import subprocess

    repo_root = Path(__file__).resolve().parents[1]
    environment = {
        **os.environ,
        "HOME": str(tmp_path),
        "USERPROFILE": str(tmp_path),
        TERMINAL_FLAG: "1",
        API_FLAG: "1",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
            "test/test_demo_terminal_api.py",
            "test/test_demo_terminal.py",
        ],
        cwd=repo_root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (tmp_path / ".d-system").exists()
