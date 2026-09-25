"""One module per feature. ``check.py`` and ``cli.py`` find them here; neither is edited to add one.

A feature module may define either or both of:

``check(config: paths.Config) -> list[str]``
    Every problem found in the target repository, one line each. An empty list means clean.

``COMMANDS: dict[str, tuple[str, Callable[[list[str]], int]]]``
    Subcommands for ``cli.py``: name to (one-line help, function taking the remaining arguments
    and returning an exit code).

A module whose name starts with an underscore is ignored.
"""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent


def features() -> dict[str, ModuleType]:
    """Import every feature module present, keyed by feature name, in name order."""
    found = {}
    for info in sorted(pkgutil.iter_modules([str(HERE)]), key=lambda item: item.name):
        if not info.name.startswith("_"):
            found[info.name] = importlib.import_module(f"{__name__}.{info.name}")
    return found
