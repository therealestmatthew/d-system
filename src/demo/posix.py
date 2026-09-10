"""POSIX PTY adapter — `pty` + bash, for Linux/macOS (ADR-013 section 4).

Uses the standard library's `pty.openpty()` to allocate a master/slave file descriptor
pair, then spawns the shell with its stdio wired to the slave end so it believes it is
attached to a real terminal (job control, prompts, and `$PS1` all behave normally). The
parent process only ever touches the master end.
"""

from __future__ import annotations

import fcntl
import os
import pty
import select
import struct
import subprocess
import termios

from src.demo.adapter import TerminalAdapter

DEFAULT_SHELL = "/bin/bash"


class PosixPtyAdapter(TerminalAdapter):
    """A shell running behind a POSIX pseudo-terminal."""

    def __init__(self, shell: str = DEFAULT_SHELL, cwd: str | None = None) -> None:
        self._shell = shell
        self._cwd = cwd
        self._master_fd: int | None = None
        self._process: subprocess.Popen[bytes] | None = None

    def start(self) -> None:
        master_fd, slave_fd = pty.openpty()
        self._master_fd = master_fd
        try:
            self._process = subprocess.Popen(
                [self._shell],
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                cwd=self._cwd,
                start_new_session=True,
                close_fds=True,
            )
        finally:
            # The child has its own copy of the slave fd; the parent never reads or
            # writes it directly, so it is closed here rather than held open.
            os.close(slave_fd)

    def write(self, data: bytes) -> None:
        if self._master_fd is None:
            raise RuntimeError("adapter not started")
        os.write(self._master_fd, data)

    def read(self, size: int = 4096, timeout: float | None = None) -> bytes:
        if self._master_fd is None:
            raise RuntimeError("adapter not started")
        if timeout is not None:
            ready, _, _ = select.select([self._master_fd], [], [], timeout)
            if not ready:
                return b""
        try:
            return os.read(self._master_fd, size)
        except OSError:
            # EIO: the child exited and the kernel reclaimed the slave side — that is
            # the normal way a PTY read reports end-of-stream, not an error to raise.
            return b""

    def resize(self, cols: int, rows: int) -> None:
        if self._master_fd is None:
            raise RuntimeError("adapter not started")
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(self._master_fd, termios.TIOCSWINSZ, winsize)

    def close(self) -> None:
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()
        if self._master_fd is not None:
            try:
                os.close(self._master_fd)
            except OSError:
                pass
            self._master_fd = None

    @property
    def alive(self) -> bool:
        return self._process is not None and self._process.poll() is None
