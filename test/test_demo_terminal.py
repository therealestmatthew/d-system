"""Tests for the PTY adapter package — ADR-013 section 4, `src/demo/`.

Covers platform detection choosing the POSIX adapter, the shell override (argument and
env var), a real POSIX session echoing a real command's output, and — the one that
matters most for CI on Linux — that the package imports cleanly without `pywinpty`
installed, since it is a Windows-only optional dependency.
"""

from __future__ import annotations

import subprocess
import sys
import time

import pytest

from src.demo.factory import SHELL_ENV_VAR, create_adapter, is_windows, resolve_shell
from src.demo.posix import DEFAULT_SHELL as DEFAULT_POSIX_SHELL
from src.demo.posix import PosixPtyAdapter


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
