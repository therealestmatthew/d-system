"""Platform detection and shell override — ADR-013 section 4.

`create_adapter()` is the one place that picks a `TerminalAdapter` implementation: the
platform is auto-detected via `platform.system()`, and either the `shell` argument or
the `D_SYSTEM_DEMO_SHELL` environment variable overrides the default shell for that
platform. `src.demo.windows` itself is imported unconditionally, at module load, by
this file below — that module only defines `WindowsConPtyAdapter` and a default shell
constant, it does not import `pywinpty` at module scope. The actual safety mechanism is
inside `WindowsConPtyAdapter.start()`, which defers `import winpty` to the moment a
Windows adapter is actually started — so a Linux or macOS caller loads
`src/demo/windows.py` but never touches its `pywinpty` import, because that import
never happens on this platform.
"""

from __future__ import annotations

import os
import platform

from src.demo.adapter import TerminalAdapter
from src.demo.posix import DEFAULT_SHELL as DEFAULT_POSIX_SHELL
from src.demo.windows import DEFAULT_SHELL as DEFAULT_WINDOWS_SHELL

SHELL_ENV_VAR = "D_SYSTEM_DEMO_SHELL"


def is_windows() -> bool:
    """True on Windows, false on every other platform (Linux, macOS)."""
    return platform.system() == "Windows"


def resolve_shell(shell: str | None = None, *, windows: bool | None = None) -> str:
    """The shell to launch: explicit argument, then env var, then the platform default.

    `windows` overrides platform detection for tests; callers outside this module leave
    it unset.
    """
    if shell is not None:
        return shell
    env_shell = os.environ.get(SHELL_ENV_VAR)
    if env_shell:
        return env_shell
    on_windows = is_windows() if windows is None else windows
    return DEFAULT_WINDOWS_SHELL if on_windows else DEFAULT_POSIX_SHELL


def create_adapter(shell: str | None = None, *, cwd: str | None = None) -> TerminalAdapter:
    """Build the adapter for the running platform, honoring the shell override."""
    resolved_shell = resolve_shell(shell)
    if is_windows():
        from src.demo.windows import WindowsConPtyAdapter

        return WindowsConPtyAdapter(shell=resolved_shell, cwd=cwd)

    from src.demo.posix import PosixPtyAdapter

    return PosixPtyAdapter(shell=resolved_shell, cwd=cwd)
