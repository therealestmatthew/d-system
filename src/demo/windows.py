"""Windows PTY adapter — ConPTY via `pywinpty`, cmd/PowerShell (ADR-013 section 4).

`pywinpty` is a Windows-only optional dependency (see `pyproject.toml`'s `sys_platform`
marker); a Linux or macOS install never needs it on disk. To keep that true even at
import time, `winpty` is imported inside `start()`, not at module scope — this module
can be imported on any platform, and only fails if a caller actually tries to start a
session without the package installed.
"""

from __future__ import annotations

from typing import Any

from src.demo.adapter import TerminalAdapter

DEFAULT_SHELL = "cmd"


class WindowsConPtyAdapter(TerminalAdapter):
    """A shell running behind Windows ConPTY, via the `pywinpty` package."""

    def __init__(
        self,
        shell: str = DEFAULT_SHELL,
        cwd: str | None = None,
        cols: int = 80,
        rows: int = 24,
    ) -> None:
        self._shell = shell
        self._cwd = cwd
        self._cols = cols
        self._rows = rows
        self._process: Any = None

    def start(self) -> None:
        import winpty  # type: ignore[import-not-found]  # Windows-only optional dependency
        # (ADR-013): not installed on this platform, so mypy has no stub for it here —
        # imported inside start() only, never at module scope.

        self._process = winpty.PtyProcess.spawn(
            self._shell,
            cwd=self._cwd,
            dimensions=(self._rows, self._cols),
        )

    def write(self, data: bytes) -> None:
        if self._process is None:
            raise RuntimeError("adapter not started")
        self._process.write(data.decode("utf-8", errors="replace"))

    def read(self, size: int = 4096, timeout: float | None = None) -> bytes:
        if self._process is None:
            raise RuntimeError("adapter not started")
        # pywinpty's PtyProcess.read() has no timeout parameter; it blocks until data
        # or EOF, which matches this method's own `timeout=None` contract. A caller
        # that needs a bounded wait on Windows polls `alive` alongside a short `size`.
        try:
            output = self._process.read(size)
        except EOFError:
            return b""
        return output.encode("utf-8") if isinstance(output, str) else output

    def resize(self, cols: int, rows: int) -> None:
        if self._process is None:
            raise RuntimeError("adapter not started")
        self._process.setwinsize(rows, cols)

    def close(self) -> None:
        if self._process is not None and self._process.isalive():
            self._process.terminate(force=True)

    @property
    def alive(self) -> bool:
        return self._process is not None and bool(self._process.isalive())
