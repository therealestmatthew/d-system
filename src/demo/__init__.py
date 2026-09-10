"""The demo terminal's PTY adapter package — ADR-013.

`create_adapter()` is the intended entry point: it auto-detects the platform and
returns the matching `TerminalAdapter` implementation (`PosixPtyAdapter` or
`WindowsConPtyAdapter`), honoring a shell override from either an explicit argument or
the `D_SYSTEM_DEMO_SHELL` environment variable. Importing this package never requires
`pywinpty` — that import happens only inside `WindowsConPtyAdapter.start()`.
"""

from __future__ import annotations

from src.demo.adapter import TerminalAdapter
from src.demo.factory import SHELL_ENV_VAR, create_adapter, is_windows, resolve_shell

__all__ = [
    "SHELL_ENV_VAR",
    "TerminalAdapter",
    "create_adapter",
    "is_windows",
    "resolve_shell",
]
