"""Put the flat ``scripts/`` package on the import path; every test uses temporary fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = PLUGIN_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def as_developer(monkeypatch: object, handle: str, email: str | None = None) -> None:
    """Act as ``handle``: state it and set the git email that identifies it.

    The email goes through git's own ``GIT_CONFIG_*`` variables, so ``git config user.email``
    returns it in this process and in every subprocess a test starts.
    """
    setenv = monkeypatch.setenv  # type: ignore[attr-defined]
    setenv("IDEA_REALIZATION_HANDLE", handle)
    setenv("GIT_CONFIG_COUNT", "1")
    setenv("GIT_CONFIG_KEY_0", "user.email")
    setenv("GIT_CONFIG_VALUE_0", email if email is not None else f"{handle}@example.com")
