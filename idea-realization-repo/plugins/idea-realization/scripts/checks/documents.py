"""The document-governance feature: its check and its commands.

``check`` scans the document root (``documents.scan``) and compares the committed catalog with a
fresh render. The commands are ``next-code`` (``codes.py``), ``release-code``
(``reservations.py``) and ``catalog`` (``documents.py``).
"""

from __future__ import annotations

from collections.abc import Callable

import codes
import documents
import paths
import reservations


def check(config: paths.Config) -> list[str]:
    return documents.check(config)


COMMANDS: dict[str, tuple[str, Callable[[list[str]], int]]] = {
    "next-code": ("allocate and reserve the next document code for a kind", codes.main),
    "release-code": ("list code reservations, or release one never written",
                     reservations.main),
    "catalog": ("regenerate the document catalog", documents.main),
}
