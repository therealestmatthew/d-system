"""Tests for the PTY adapter package, the demo terminal websocket route (ADR-013), and the
demo stage read routes.

Covers, for `src/demo/`: platform detection choosing the POSIX adapter, the shell override
(argument and env var), a real POSIX session echoing a real command's output, and — the one
that matters most for CI on Linux — that the package imports cleanly without `pywinpty`
installed, since it is a Windows-only optional dependency.

Covers, for `src/api/routes/demo_terminal.py`: that the route does not exist at all with
`D_SYSTEM_DEMO_TERMINAL` unset (not merely refuses); that a websocket client can send a
command and read its real output back with the flag set; and that the loopback-bind fail-fast
check actually refuses a non-loopback host, both as a direct unit check and through the
registration path `src/api/__init__.py` drives at import time.

Covers, for `src/api/routes/demo_stage.py`: that the talking-points route returns a configured
file's content unchanged and 404s with a clear message when the file is missing; that the
overview-location route reports the configured path without requiring the file to exist; and
that both routes are registered regardless of `D_SYSTEM_DEMO_TERMINAL`.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import src.api as api_module
import src.main as main_module
from src.api.routes.demo_stage import (
    DEMO_TERMINAL_FLAG_ENV_VAR,
    OVERVIEW_PAGE_PATH_ENV_VAR,
    TALKING_POINTS_PATH_ENV_VAR,
)
from src.api.routes.demo_terminal import (
    BIND_HOST_ENV_VAR,
    UVICORN_HOST_ENV_VAR,
    NonLoopbackBindError,
    enforce_loopback_bind,
    resolve_configured_host,
)
from src.demo.factory import SHELL_ENV_VAR, create_adapter, is_windows, resolve_shell
from src.demo.posix import DEFAULT_SHELL as DEFAULT_POSIX_SHELL
from src.demo.posix import PosixPtyAdapter

DEMO_TERMINAL_WS_PATH = "/api/v1/demo/terminal/ws"
DEMO_STAGE_TALKING_POINTS_PATH = "/api/v1/demo/stage/talking-points"
DEMO_STAGE_OVERVIEW_LOCATION_PATH = "/api/v1/demo/stage/overview-location"
DEMO_STAGE_TERMINAL_ENABLED_PATH = "/api/v1/demo/stage/terminal-enabled"


def test_platform_detection_is_not_windows_on_linux() -> None:
    assert is_windows() is False


def test_create_adapter_returns_posix_adapter_on_linux() -> None:
    adapter = create_adapter()
    assert isinstance(adapter, PosixPtyAdapter)


def test_resolve_shell_defaults_to_bash_on_posix() -> None:
    assert resolve_shell(windows=False) == DEFAULT_POSIX_SHELL


def test_resolve_shell_defaults_to_cmd_on_windows() -> None:
    assert resolve_shell(windows=True) == "cmd"


def test_shell_override_via_explicit_argument_is_honored() -> None:
    assert resolve_shell("/bin/zsh", windows=False) == "/bin/zsh"


def test_shell_override_via_env_var_is_honored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(SHELL_ENV_VAR, "/bin/sh")
    assert resolve_shell(windows=False) == "/bin/sh"


def test_shell_override_argument_wins_over_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(SHELL_ENV_VAR, "/bin/sh")
    assert resolve_shell("/bin/zsh", windows=False) == "/bin/zsh"


def test_create_adapter_honors_shell_override() -> None:
    adapter = create_adapter(shell="/bin/sh")
    assert isinstance(adapter, PosixPtyAdapter)
    assert adapter._shell == "/bin/sh"  # noqa: SLF001 — asserting the override landed


def test_posix_adapter_echoes_a_real_command() -> None:
    """A real `echo` round-trips through the actual PTY, not a mock."""
    adapter = PosixPtyAdapter(shell=DEFAULT_POSIX_SHELL)
    adapter.start()
    try:
        adapter.write(b"echo demo-terminal-marker\n")
        output = b""
        deadline = time.monotonic() + 5.0
        while b"demo-terminal-marker" not in output and time.monotonic() < deadline:
            output += adapter.read(size=4096, timeout=1.0)
        assert b"demo-terminal-marker" in output
    finally:
        adapter.close()


def test_posix_adapter_reports_alive_then_not_alive() -> None:
    adapter = PosixPtyAdapter(shell=DEFAULT_POSIX_SHELL)
    adapter.start()
    try:
        assert adapter.alive is True
        adapter.write(b"exit\n")
        deadline = time.monotonic() + 5.0
        while adapter.alive and time.monotonic() < deadline:
            adapter.read(size=4096, timeout=0.5)
        assert adapter.alive is False
    finally:
        adapter.close()


def test_posix_adapter_read_before_start_raises() -> None:
    adapter = PosixPtyAdapter(shell=DEFAULT_POSIX_SHELL)
    with pytest.raises(RuntimeError):
        adapter.read()


def test_module_imports_cleanly_without_pywinpty_installed() -> None:
    """`pywinpty` is a Windows-only optional dependency (ADR-013); this environment
    genuinely does not have it installed, so a clean subprocess import of the whole
    `src.demo` package — including `src.demo.windows` — is a real check, not a
    tautology.
    """
    with pytest.raises(ModuleNotFoundError):
        __import__("winpty")

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import src.demo; import src.demo.windows; import src.demo.posix; "
            "import src.demo.factory; import src.demo.adapter",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr


# --- src/api/routes/demo_terminal.py: flag gating, the websocket bridge, loopback bind ---


def _uncache_demo_terminal_module() -> None:
    """Force the next `from src.api.routes import demo_terminal` to genuinely re-execute it.

    Removing `sys.modules["src.api.routes.demo_terminal"]` alone is not enough: CPython's
    `from package import submodule` skips re-importing whenever `submodule` is already an
    attribute on the parent package object, which a prior import leaves behind. Clearing that
    attribute too is what makes the reload below actually re-run the module body (and, with
    it, the loopback-bind check that module runs at import time).
    """
    sys.modules.pop("src.api.routes.demo_terminal", None)
    routes_package = sys.modules.get("src.api.routes")
    if routes_package is not None and hasattr(routes_package, "demo_terminal"):
        delattr(routes_package, "demo_terminal")


@pytest.fixture
def rebuild_app(monkeypatch: pytest.MonkeyPatch) -> Callable[..., FastAPI]:
    """Rebuilds `src.api` and `src.main` under the given env, restoring flag-unset state after.

    `D_SYSTEM_DEMO_TERMINAL` gates a conditional import inside `src/api/__init__.py`, and
    `src.api.routes.demo_terminal` runs its loopback-bind check as a side effect of import —
    so proving the gating and the fail-fast for real means re-running those imports under a
    controlled environment, not just calling the pure functions in isolation.
    """

    def _build(*, flag: str | None, bind_host: str | None = None) -> FastAPI:
        if flag is None:
            monkeypatch.delenv("D_SYSTEM_DEMO_TERMINAL", raising=False)
        else:
            monkeypatch.setenv("D_SYSTEM_DEMO_TERMINAL", flag)
        if bind_host is None:
            monkeypatch.delenv(BIND_HOST_ENV_VAR, raising=False)
        else:
            monkeypatch.setenv(BIND_HOST_ENV_VAR, bind_host)
        _uncache_demo_terminal_module()
        importlib.reload(api_module)
        importlib.reload(main_module)
        return main_module.app

    yield _build

    monkeypatch.delenv("D_SYSTEM_DEMO_TERMINAL", raising=False)
    monkeypatch.delenv(BIND_HOST_ENV_VAR, raising=False)
    _uncache_demo_terminal_module()
    importlib.reload(api_module)
    importlib.reload(main_module)


def test_route_absent_with_flag_unset(rebuild_app: Callable[..., FastAPI]) -> None:
    """No `D_SYSTEM_DEMO_TERMINAL` means the route module is never imported — not present and
    refusing, genuinely absent from the running process, and unreachable over a websocket.
    """
    app = rebuild_app(flag=None)
    assert "src.api.routes.demo_terminal" not in sys.modules

    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(DEMO_TERMINAL_WS_PATH):
            pass  # pragma: no cover — unreachable when the route is absent


def test_websocket_command_round_trip_with_flag_set(rebuild_app: Callable[..., FastAPI]) -> None:
    """With the flag set, a websocket client can send a real command and read its real output
    back through the PTY adapter — a live shell round-trip, not a mocked one.
    """
    app = rebuild_app(flag="1")
    assert "src.api.routes.demo_terminal" in sys.modules

    client = TestClient(app)
    output = b""
    with client.websocket_connect(DEMO_TERMINAL_WS_PATH) as websocket:
        websocket.send_bytes(b"echo demo-terminal-ws-marker\n")
        deadline = time.monotonic() + 5.0
        while b"demo-terminal-ws-marker" not in output and time.monotonic() < deadline:
            output += websocket.receive_bytes()
    assert b"demo-terminal-ws-marker" in output


def test_registration_fails_fast_for_non_loopback_bind_with_flag_set(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    """With the flag set and a non-loopback bind host configured, importing the route module
    — which `src/api/__init__.py` does at app-construction time — raises before the app ever
    finishes building, rather than building an app that would refuse connections later.

    Caught as `RuntimeError` rather than `NonLoopbackBindError`: `rebuild_app` reloads
    `src.api.routes.demo_terminal`, which redefines `NonLoopbackBindError` as a new class
    object each time — the raised instance would not be an instance of the class this file
    imported once at collection time, even though it is the "same" exception by name.
    """
    with pytest.raises(RuntimeError, match="loopback"):
        rebuild_app(flag="1", bind_host="0.0.0.0")


def test_registration_fails_fast_for_uvicorn_host_env_var_non_loopback(
    monkeypatch: pytest.MonkeyPatch, rebuild_app: Callable[..., FastAPI]
) -> None:
    """The full bypass reproduced end to end: `D_SYSTEM_DEMO_TERMINAL=1
    UVICORN_HOST=0.0.0.0 uv run uvicorn src.main:app --port 8010` — no `--host` flag, no
    `D_SYSTEM_BIND_HOST`, just `UVICORN_HOST` the way `uvicorn`'s `click`-based CLI (built with
    `auto_envvar_prefix="UVICORN"`) actually reads it — must still refuse to build the app
    (D01-A finding 1).
    """
    monkeypatch.delenv(BIND_HOST_ENV_VAR, raising=False)
    monkeypatch.setenv(UVICORN_HOST_ENV_VAR, "0.0.0.0")
    monkeypatch.setattr(sys, "argv", ["uvicorn", "src.main:app", "--port", "8010"])
    with pytest.raises(RuntimeError, match="loopback"):
        rebuild_app(flag="1")
    monkeypatch.delenv(UVICORN_HOST_ENV_VAR, raising=False)


def test_enforce_loopback_bind_raises_for_non_loopback_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(BIND_HOST_ENV_VAR, "0.0.0.0")
    with pytest.raises(NonLoopbackBindError):
        enforce_loopback_bind()


@pytest.mark.parametrize("loopback_host", ["127.0.0.1", "::1", "localhost"])
def test_enforce_loopback_bind_passes_for_loopback_hosts(
    monkeypatch: pytest.MonkeyPatch, loopback_host: str
) -> None:
    monkeypatch.setenv(BIND_HOST_ENV_VAR, loopback_host)
    enforce_loopback_bind()  # must not raise


def test_resolve_configured_host_defaults_to_loopback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(BIND_HOST_ENV_VAR, raising=False)
    monkeypatch.setattr(sys, "argv", ["uvicorn", "src.main:app", "--port", "8010"])
    assert resolve_configured_host() == "127.0.0.1"


def test_resolve_configured_host_reads_host_flag_from_argv(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The real scenario ADR-013 names: `uvicorn src.main:app --host 0.0.0.0` runs the app in
    the same interpreter process as the `uvicorn` CLI, so `--host` is visible on `sys.argv`
    without any separate configuration the launch command could forget to set.
    """
    monkeypatch.delenv(BIND_HOST_ENV_VAR, raising=False)
    monkeypatch.setattr(
        sys, "argv", ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8010"]
    )
    assert resolve_configured_host() == "0.0.0.0"


def test_resolve_configured_host_env_var_overrides_argv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(BIND_HOST_ENV_VAR, "127.0.0.1")
    monkeypatch.setattr(
        sys, "argv", ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8010"]
    )
    assert resolve_configured_host() == "127.0.0.1"


def test_resolve_configured_host_reads_uvicorn_host_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`uvicorn`'s CLI is `click`-based with `auto_envvar_prefix="UVICORN"`, so
    `UVICORN_HOST=0.0.0.0 uvicorn src.main:app` sets the bind host exactly as `--host 0.0.0.0`
    would, without either the flag or `D_SYSTEM_BIND_HOST` appearing anywhere. Missing this
    check let `D_SYSTEM_DEMO_TERMINAL=1 UVICORN_HOST=0.0.0.0 uv run uvicorn src.main:app` start
    and bind non-loopback (D01-A finding 1) — this proves the pure function alone now catches
    it.
    """
    monkeypatch.delenv(BIND_HOST_ENV_VAR, raising=False)
    monkeypatch.setenv(UVICORN_HOST_ENV_VAR, "0.0.0.0")
    monkeypatch.setattr(sys, "argv", ["uvicorn", "src.main:app", "--port", "8010"])
    assert resolve_configured_host() == "0.0.0.0"


def test_resolve_configured_host_argv_host_flag_wins_over_uvicorn_host_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An explicit `--host` on the command line is what a real `uvicorn` launch honors over its
    own `UVICORN_HOST`-sourced default, so this function must agree.
    """
    monkeypatch.delenv(BIND_HOST_ENV_VAR, raising=False)
    monkeypatch.setenv(UVICORN_HOST_ENV_VAR, "0.0.0.0")
    monkeypatch.setattr(
        sys, "argv", ["uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8010"]
    )
    assert resolve_configured_host() == "127.0.0.1"


def test_enforce_loopback_bind_raises_for_non_loopback_uvicorn_host_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The exact bypass the adversarial review (D01-A finding 1) demonstrated: no
    `D_SYSTEM_BIND_HOST` set, no `--host` on argv, only `UVICORN_HOST=0.0.0.0` — the loopback
    fail-fast must still refuse.
    """
    monkeypatch.delenv(BIND_HOST_ENV_VAR, raising=False)
    monkeypatch.setenv(UVICORN_HOST_ENV_VAR, "0.0.0.0")
    monkeypatch.setattr(sys, "argv", ["uvicorn", "src.main:app", "--port", "8010"])
    with pytest.raises(NonLoopbackBindError):
        enforce_loopback_bind()


# --- src/api/routes/demo_stage.py: talking-points and overview-location read routes ---


def test_demo_stage_routes_registered_with_terminal_flag_unset() -> None:
    """The stage read routes carry no capability of their own (unlike the terminal route), so
    they exist regardless of `D_SYSTEM_DEMO_TERMINAL` — proven here against the module-level
    `main_module.app`, built with the flag unset in this process.
    """
    client = TestClient(main_module.app)
    response = client.get(DEMO_STAGE_OVERVIEW_LOCATION_PATH)
    assert response.status_code == 200


def test_get_talking_points_returns_404_with_clear_message_when_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing_path = tmp_path / "does-not-exist.json"
    monkeypatch.setenv(TALKING_POINTS_PATH_ENV_VAR, str(missing_path))
    client = TestClient(main_module.app)
    response = client.get(DEMO_STAGE_TALKING_POINTS_PATH)
    assert response.status_code == 404
    assert str(missing_path) in response.json()["detail"]


def test_get_talking_points_returns_file_content_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The route is a pass-through: the exact bytes on disk come back, byte for byte."""
    talking_points_file = tmp_path / "talking-points.json"
    raw_content = '{"points": ["first point", "second point"]}'
    talking_points_file.write_text(raw_content)
    monkeypatch.setenv(TALKING_POINTS_PATH_ENV_VAR, str(talking_points_file))

    client = TestClient(main_module.app)
    response = client.get(DEMO_STAGE_TALKING_POINTS_PATH)

    assert response.status_code == 200
    assert response.text == raw_content
    assert response.headers["content-type"].startswith("application/json")


def test_get_overview_location_reports_configured_path_without_requiring_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The overview page is generated by a later phase (`phase-demo-04`); this route reports
    the configured location whether or not the file exists yet.
    """
    overview_page = tmp_path / "d-system-overview.html"
    assert not overview_page.exists()
    monkeypatch.setenv(OVERVIEW_PAGE_PATH_ENV_VAR, str(overview_page))

    client = TestClient(main_module.app)
    response = client.get(DEMO_STAGE_OVERVIEW_LOCATION_PATH)

    assert response.status_code == 200
    assert response.json() == {"path": str(overview_page)}


def test_get_overview_location_defaults_to_a_path_under_public(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(OVERVIEW_PAGE_PATH_ENV_VAR, raising=False)
    client = TestClient(main_module.app)
    response = client.get(DEMO_STAGE_OVERVIEW_LOCATION_PATH)
    assert response.status_code == 200
    path = response.json()["path"]
    assert path.startswith("_public/")


def test_get_terminal_enabled_reports_false_with_flag_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(DEMO_TERMINAL_FLAG_ENV_VAR, raising=False)
    client = TestClient(main_module.app)
    response = client.get(DEMO_STAGE_TERMINAL_ENABLED_PATH)
    assert response.status_code == 200
    assert response.json() == {"terminal_enabled": False}


def test_get_terminal_enabled_reports_true_with_flag_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`demo_stage.py` reads the flag itself rather than importing `demo_terminal`, so this
    proves the read-back without needing the app to be rebuilt under the flag — the whole point
    of this route (D01-A finding 2) is that it works regardless of whether the terminal route
    module was ever imported in this process.
    """
    monkeypatch.setenv(DEMO_TERMINAL_FLAG_ENV_VAR, "1")
    client = TestClient(main_module.app)
    response = client.get(DEMO_STAGE_TERMINAL_ENABLED_PATH)
    assert response.status_code == 200
    assert response.json() == {"terminal_enabled": True}


def test_get_talking_points_defaults_to_ts_public_location(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With no override, the route serves `ts/public/talking-points.json` — this phase's own
    deliverable — unchanged, byte for byte, rather than a re-serialized or partial copy.
    """
    monkeypatch.delenv(TALKING_POINTS_PATH_ENV_VAR, raising=False)
    default_path = (
        Path(__file__).resolve().parents[1] / "ts" / "public" / "talking-points.json"
    )
    assert default_path.is_file()
    expected_content = default_path.read_bytes()

    client = TestClient(main_module.app)
    response = client.get(DEMO_STAGE_TALKING_POINTS_PATH)

    assert response.status_code == 200
    assert response.content == expected_content
