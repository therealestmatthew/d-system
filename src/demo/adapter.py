"""The PTY adapter interface every shell implementation satisfies — ADR-013 section 4.

One shape, two backends: `src/demo/posix.py` (POSIX `pty` + bash, Linux/macOS) and
`src/demo/windows.py` (ConPTY via `pywinpty`, Windows). Nothing outside `src/demo/factory.py`
should import a backend directly — go through `create_adapter()` so platform detection and the
shell override stay in one place.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class TerminalAdapter(ABC):
    """A running shell reachable as a byte stream, independent of the host platform."""

    @abstractmethod
    def start(self) -> None:
        """Spawn the shell process. Must be called before write/read/resize."""

    @abstractmethod
    def write(self, data: bytes) -> None:
        """Send bytes to the shell's stdin, as if typed at the terminal."""

    @abstractmethod
    def read(self, size: int = 4096, timeout: float | None = None) -> bytes:
        """Read up to `size` bytes of shell output.

        With `timeout` set, returns `b""` if nothing arrives within it rather than
        blocking forever; with `timeout=None`, blocks until at least one byte arrives
        or the shell exits.
        """

    @abstractmethod
    def resize(self, cols: int, rows: int) -> None:
        """Tell the shell the terminal's new dimensions."""

    @abstractmethod
    def close(self) -> None:
        """Terminate the shell process and release any OS resources it holds."""

    @property
    @abstractmethod
    def alive(self) -> bool:
        """Whether the shell process is still running."""
